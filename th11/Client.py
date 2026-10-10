import asyncio
import os
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

from . import Variables, detect, receive, traps
from .Items import item_table
from .Variables import DISPLAY_NAME, GAME_NAME, PROBE_TABLE, SHORT_NAME
from .patching import PatchMismatch, patch_immediate
from .probe import float_candidates, format_probe, memsearch, read_entry, read_float, write_float, write_int
from .state import read_state

ITEM_NAMES = {data.code: name for name, data in item_table.items()}
POLL_SECONDS = 0.5
MEMSEARCH_CAP = 50


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
		if cmd == "ReceivedItems":
			asyncio.create_task(self.check_goal())

	async def poll(self, controller, prev, runs):
		"""One loop tick: send checks for prev -> now, write new items. -> (state, runs)."""
		state = read_state(controller)
		# ponytail: checks found before the first connect use empty slot_data (per character, no difficulty);
		# queue the raw runs instead if playing before connecting with shot_type/difficulty_check matters.
		lower = self.received_names().count("Lower Difficulty")
		locations, runs = detect.step(prev, state, runs, self.slot_data, lower) if prev else ([], 0)
		self.locations_found.update(locations)
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
		written = state._replace(**{"lives" if entry == Variables.ADDR_LIVES else "power": value for entry, value in writes})
		trap_writes, new_speeds = traps.tick(self.traps, time.monotonic(), written, None if None in speeds else speeds)
		for entry, value in trap_writes:
			write_int(controller, entry, value)
		for name, value in zip(traps.SPEED_ENTRIES, new_speeds or []):
			write_float(controller, getattr(Variables, name), value)
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
