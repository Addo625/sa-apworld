import asyncio
import os
import random
import subprocess
import time

from CommonClient import (
	CommonContext,
	ClientCommandProcessor,
	get_base_parser,
	logger,
	server_loop,
	gui_enabled,
)
from NetUtils import ClientStatus
from settings import get_settings

from . import Variables, deathlink, detect, receive, ringlink, traps
from .Items import item_table
from .Options import DeathLinkAmnesty, DeathLinkTrigger
from .Variables import DISPLAY_NAME, GAME_NAME, PROBE_TABLE, SHORT_NAME
from .patching import PatchMismatch, patch_immediate, safe_patch
from .probe import float_candidates, format_probe, memsearch, read_entry, read_float, write_float, write_int
from .state import read_state

ITEM_NAMES = {data.code: name for name, data in item_table.items()}
POLL_SECONDS = 0.5
MEMSEARCH_CAP = 50
KILL_SECONDS = 0.1  # how long the kill site stays patched (EoSD killPlayer)
KILL_RETRY_SECONDS = 2  # a kill that took no life (bomb, respawn invincibility) is retried after this


class TouhouClientProcessor(ClientCommandProcessor):
	def _cmd_probe(self):
		"""Attach to th11.exe and print every address table entry"""
		from .gameController import gameController
		try:
			controller = gameController()
		except Exception as e:
			logger.error(f"Cannot attach to {GAME_NAME}: {e}")
			return False
		logger.info(format_probe(controller, PROBE_TABLE))
		return True

	def _cmd_memsearch(self, hex_pattern: str = ""):
		"""Search th11.exe's readable memory for a hex byte pattern (e.g. from tools/scoredat.py)"""
		from .gameController import gameController
		try:
			pattern = bytes.fromhex(hex_pattern)
		except ValueError:
			pattern = b""
		if not pattern:
			logger.error("Usage: /memsearch <hex bytes>")
			return False
		try:
			controller = gameController()
			regions = controller.readable_regions()
		except Exception as e:
			logger.error(f"Cannot attach to {GAME_NAME}: {e}")
			return False
		found = memsearch(controller, regions, pattern, MEMSEARCH_CAP)
		logger.info(f"{len(found)} match(es) in {len(regions)} regions" + (f" (capped at {MEMSEARCH_CAP})" if len(found) >= MEMSEARCH_CAP else ""))
		for address in found:
			logger.info(f"  0x{address:08X} (base + 0x{address - controller.base_address:X})")
		return True

	def _cmd_peek(self, hex_address: str = "", count: str = "16"):
		"""Print count bytes at an absolute hex address (e.g. a /memsearch match)"""
		from .gameController import gameController
		try:
			address, count = int(hex_address, 16), int(count)
		except ValueError:
			logger.error("Usage: /peek <hex address> [count]")
			return False
		try:
			data = gameController().read_bytes(address, count)
		except Exception as e:
			logger.error(f"Cannot read {GAME_NAME} at 0x{address:08X}: {e}")
			return False
		logger.info(f"0x{address:08X}: {data.hex(' ')}")
		return True

	def _cmd_poke(self, hex_address: str = "", hex_bytes: str = ""):
		"""Debug: write hex bytes at an absolute hex address, only as a probe request says"""
		from .gameController import gameController
		try:
			address, data = int(hex_address, 16), bytes.fromhex(hex_bytes)
		except ValueError:
			data = b""
		if not data:
			logger.error("Usage: /poke <hex address> <hex bytes>")
			return False
		try:
			controller = gameController()
			before = controller.read_bytes(address, len(data))
			controller.write_bytes(address, data)
		except Exception as e:
			logger.error(f"Cannot write {GAME_NAME} at 0x{address:08X}: {e}")
			return False
		logger.info(f"0x{address:08X}: {before.hex(' ')} -> {data.hex(' ')}")
		return True

	def _cmd_playerfloats(self, count: str = "1000"):
		"""Print speed-like floats in the first count (hex) bytes of the player object, to find its speed fields"""
		from .gameController import gameController
		try:
			controller = gameController()
			player = read_entry(controller, Variables.ADDR_PLAYER_PTR)
			data = controller.read_bytes(player, int(count, 16))  # player None or 0 raises
		except Exception as e:
			logger.error(f"Cannot read the player object (in a stage?): {e}")
			return False
		logger.info(f"Player object at 0x{player:08X}")
		for offset, value in float_candidates(data):
			logger.info(f"  +0x{offset:X} = {value:g} (addr 0x{player + offset:08X})")
		return True

	def _cmd_deathlink(self, active: str = ""):
		"""Turn DeathLink on or off, or show it"""
		active = active.lower()
		if active not in ("", "on", "off"):
			logger.error("Usage: /deathlink [on|off]")
			return False
		if active:
			asyncio.create_task(self.ctx.update_death_link(active == "on"))
			self.ctx.link.incoming = False  # a death received before turning it off doesn't wait
		logger.info(f"DeathLink: {active or ('on' if 'DeathLink' in self.ctx.tags else 'off')}")
		return True

	def _cmd_ringlink(self, active: str = ""):
		"""Turn RingLink on or off, or show it"""
		active = active.lower()
		if active not in ("", "on", "off"):
			logger.error("Usage: /ringlink [on|off]")
			return False
		if active:
			asyncio.create_task(self.ctx.update_ring_link(active == "on"))
		logger.info(f"RingLink: {active or ('on' if 'RingLink' in self.ctx.tags else 'off')}")
		return True

	def _cmd_deathlink_trigger(self, value: str = ""):
		"""Send a death on every life lost (life) or only on a game over (game_over), or show the setting"""
		if value:
			if value.lower() not in DeathLinkTrigger.options:  # from_text would also take "random"
				logger.error("Usage: /deathlink_trigger [life|game_over]")
				return False
			self.ctx.link.trigger = DeathLinkTrigger.options[value.lower()]
		logger.info(f"DeathLink trigger: {DeathLinkTrigger.get_option_name(self.ctx.link.trigger)}")
		return True

	def _cmd_deathlink_amnesty(self, value: str = ""):
		"""Set how many deaths are forgiven before one is sent (0-10), or show it"""
		if value:
			if not value.isdigit() or not DeathLinkAmnesty.range_start <= int(value) <= DeathLinkAmnesty.range_end:
				logger.error("Usage: /deathlink_amnesty [0-10]")
				return False
			self.ctx.link.amnesty, self.ctx.link.deaths = int(value), 0
		logger.info(f"DeathLink amnesty: {self.ctx.link.amnesty}")
		return True

	def _cmd_launch(self):
		"""Launch Touhou SA"""
		game_exe = get_settings().touhou_sa_settings.game_exe
		try:
			# The game finds th11.dat relative to its working directory.
			subprocess.Popen([game_exe], cwd=os.path.dirname(os.path.abspath(game_exe)), close_fds=True)
		except OSError as e:
			logger.error(f"Failed to launch Touhou: {e.strerror}")
			return False
		return True


class TouhouContext(CommonContext):
	"""Touhou SA context: polls the game, sends checks, applies received items."""
	game = DISPLAY_NAME
	items_handling = 0b111  # Item from starting inventory, own world and other world
	command_processor = TouhouClientProcessor

	def __init__(self, server_address=None, password=None):
		super().__init__(server_address, password)
		self.items_applied = 0  # kept across server reconnects, which replay the list from index 0
		self.applied_for = None  # (seed, slot) items_applied counts for
		self.locations_found = set()
		self.slot_data = {}  # options detect needs (shot_type, difficulty_check, ...); empty until connected
		self.continue_lives = None  # (controller, lives) last patched; a restarted game needs it again
		self.traps = traps.TrapState()
		self.traps_seen = 0  # received items scanned for traps, kept across reconnects like items_applied
		self.link = deathlink.LinkState()
		self.link_prev = None  # last poll's state after the client's writes, for deathlink.on_state
		self.killed_at = -KILL_RETRY_SECONDS  # time.monotonic() of the last kill attempt
		self.ring_link_id = random.randint(0, 999999)  # RingLink "source": our own bounces come back and are skipped
		self.rings = 0  # received, applied at the next poll

	async def update_ring_link(self, active: bool):
		"""CommonContext.update_death_link for the RingLink tag."""
		old_tags = self.tags.copy()
		if active:
			self.tags.add("RingLink")
		else:
			self.tags -= {"RingLink"}
		if old_tags != self.tags and self.server and not self.server.socket.closed:
			await self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}])

	async def server_auth(self, password_requested: bool = False):
		if password_requested and not self.password:
			await super().server_auth(password_requested)
		await self.get_username()
		await self.send_connect()

	def received_names(self):
		return [ITEM_NAMES.get(item.item) for item in self.items_received]

	async def check_goal(self):
		if not self.finished_game and receive.goal_reached(filter(None, self.received_names()), self.slot_data):
			self.finished_game = True
			await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

	def on_package(self, cmd: str, args: dict):
		if cmd == "Connected":
			self.slot_data = args.get("slot_data") or {}
			if self.applied_for != (self.seed_name, self.slot):
				self.applied_for, self.items_applied, self.traps_seen = (self.seed_name, self.slot), 0, 0
				self.traps = traps.TrapState()
				# A new seed starts from its options; a reconnect keeps what the commands changed.
				self.link = deathlink.LinkState(
					self.slot_data.get("death_link_trigger", DeathLinkTrigger.default),
					self.slot_data.get("death_link_amnesty", DeathLinkAmnesty.default))
				asyncio.create_task(self.update_death_link(bool(self.slot_data.get("death_link"))))
				asyncio.create_task(self.update_ring_link(bool(self.slot_data.get("ring_link"))))
		if cmd == "Bounced" and "RingLink" in args.get("tags", []) and "RingLink" in self.tags:
			data = args.get("data") or {}
			amount = data.get("amount")
			if data.get("source") != self.ring_link_id and isinstance(amount, int) and not isinstance(amount, bool):
				self.rings += amount
		if cmd == "ReceivedItems":
			asyncio.create_task(self.check_goal())

	def on_deathlink(self, data: dict):
		super().on_deathlink(data)
		if Variables.ADDR_KILL_CONDITION is None:
			logger.info("DeathLink: can't kill the player yet, pending the kill code site (probe batch 32 R5, ticket 36)")
		else:
			self.link.incoming = True  # kills at the next poll in a run; waits outside one

	async def kill(self, controller):
		"""Patch the kill site for KILL_SECONDS so the player dies (EoSD/MoF setKill), then restore it."""
		expected = Variables.EXPECTED_BYTES["ADDR_KILL_CONDITION"]
		nops = b"\x90" * len(expected)
		try:
			safe_patch(controller, controller.base_address + Variables.ADDR_KILL_CONDITION, expected, nops)
		except PatchMismatch as e:
			logger.error(f"DeathLink: not killed, unexpected game code: {e}")
			self.link.incoming = False
			return
		try:
			await asyncio.sleep(KILL_SECONDS)
		finally:
			safe_patch(controller, controller.base_address + Variables.ADDR_KILL_CONDITION, nops, expected)

	async def poll(self, controller, prev, runs):
		"""One loop tick: send checks for prev -> now, write new items. -> (state, runs)."""
		state = read_state(controller)
		# ponytail: checks found before the first connect use empty slot_data (per character, no difficulty);
		# queue the raw runs instead if playing before connecting with shot_type/difficulty_check matters.
		lower = self.received_names().count("Lower Difficulty")
		locations, runs = detect.step(prev, state, runs, self.slot_data, lower) if prev else ([], 0)
		self.locations_found.update(locations)
		if self.slot is None or prev is None:
			self.link_prev = None  # lives seen before a (re)attach or connect aren't this run's
		if self.slot is None:
			return state, runs  # not connected: checks wait in locations_found
		if self.locations_found:
			await self.check_locations(self.locations_found)
			self.locations_found.clear()
		names = self.received_names()
		writes, self.items_applied = receive.apply_new(names, self.items_applied, state)
		for entry, value in writes + receive.difficulty_writes(state, lower, self.slot_data):
			write_int(controller, entry, value)
		self.traps.queue += [name for name in names[self.traps_seen:] if name in traps.TRAPS]
		self.traps_seen = len(names)
		speeds = [read_float(controller, getattr(Variables, name)) for name in traps.SPEED_ENTRIES]
		written = receive.with_writes(state, writes)
		trap_writes, new_speeds = traps.tick(self.traps, time.monotonic(), written, None if None in speeds else speeds)
		for entry, value in trap_writes:
			write_int(controller, entry, value)
		for name, value in zip(traps.SPEED_ENTRIES, new_speeds or []):
			write_float(controller, getattr(Variables, name), value)
		if "DeathLink" in self.tags:
			if deathlink.on_state(self.link_prev, state, self.link):
				await self.send_death()
			if self.link.incoming and receive.in_run(state) and time.monotonic() - self.killed_at >= KILL_RETRY_SECONDS:
				self.killed_at = time.monotonic()
				await self.kill(controller)
		written = receive.with_writes(written, trap_writes)
		ring_writes = []
		if "RingLink" in self.tags:
			rings = ringlink.delta(self.link_prev, state)
			if rings:
				await self.send_msgs([{"cmd": "Bounce", "tags": ["RingLink"],
					"data": {"time": time.time(), "source": self.ring_link_id, "amount": rings}}])
			ring_writes = ringlink.receive(written, self.rings)
		self.rings = 0
		for entry, value in ring_writes:
			write_int(controller, entry, value)
		self.link_prev = receive.with_writes(written, ring_writes)
		if self.slot_data.get("mode"):
			self.patch_continue_lives(controller, receive.continue_lives(names))
		return state, runs

	def patch_continue_lives(self, controller, lives):
		"""Normal mode: a continue restores the lives from items (MoF setNormalContinueLives). Once per value and game process."""
		if self.continue_lives == (controller, lives):
			return
		self.continue_lives = (controller, lives)
		site = Variables.ADDR_NORMAL_CONTINUE_LIVES
		if site is None:
			logger.info(f"Continue lives ({lives}): pending the continue-lives code site (probe batch 32, R2)")
			return
		try:
			patch_immediate(controller, controller.base_address + Variables.ADDR_NORMAL_CONTINUE_LIVES, Variables.EXPECTED_BYTES["ADDR_NORMAL_CONTINUE_LIVES"], lives)
		except PatchMismatch as e:
			logger.error(f"Continue lives not patched, unexpected game code: {e}")


async def game_loop(ctx: TouhouContext):
	"""Attach to th11.exe, poll it every POLL_SECONDS, reattach when the process restarts."""
	from .gameController import gameController
	controller, prev, runs = None, None, 0
	while not ctx.exit_event.is_set():
		await asyncio.sleep(POLL_SECONDS)
		if controller is None:
			try:
				controller = gameController()
			except Exception:
				continue
			logger.info(f"Attached to {GAME_NAME}")
		try:
			controller.read_bytes(controller.base_address, 1)  # read_state hides read errors; this one means the process is gone
		except Exception as e:
			logger.info(f"Lost {GAME_NAME} ({e}), waiting for it to restart")
			controller, prev, runs = None, None, 0
			continue
		try:
			prev, runs = await ctx.poll(controller, prev, runs)
		except Exception:
			logger.exception("Game loop tick failed")  # keep prev and runs: the stage's run count must survive


def launch(*args: str):
	async def main(args):
		ctx = TouhouContext(args.connect, args.password)
		ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
		if gui_enabled:
			ctx.run_gui()
		ctx.run_cli()
		watcher = asyncio.create_task(game_loop(ctx), name="game loop")
		await ctx.exit_event.wait()
		await watcher
		await ctx.shutdown()

	parser = get_base_parser(description=SHORT_NAME + " Client")
	args, _ = parser.parse_known_args(args)

	import colorama
	colorama.just_fix_windows_console()
	asyncio.run(main(args))
