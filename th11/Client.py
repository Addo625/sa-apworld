import asyncio
import os
import subprocess

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

from . import detect, receive
from .Items import item_table
from .Variables import DISPLAY_NAME, GAME_NAME, PROBE_TABLE, SHORT_NAME
from .probe import format_probe, write_int
from .state import read_state

ITEM_NAMES = {data.code: name for name, data in item_table.items()}
POLL_SECONDS = 0.5


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

	async def server_auth(self, password_requested: bool = False):
		if password_requested and not self.password:
			await super().server_auth(password_requested)
		await self.get_username()
		await self.send_connect()

	def received_names(self):
		return [ITEM_NAMES.get(item.item) for item in self.items_received]

	async def check_goal(self):
		if not self.finished_game and receive.goal_reached(filter(None, self.received_names())):
			self.finished_game = True
			await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

	def on_package(self, cmd: str, args: dict):
		if cmd == "Connected" and self.applied_for != (self.seed_name, self.slot):
			self.applied_for, self.items_applied = (self.seed_name, self.slot), 0
		if cmd == "ReceivedItems":
			asyncio.create_task(self.check_goal())

	async def poll(self, controller, prev, runs):
		"""One loop tick: send checks for prev -> now, write new items. -> (state, runs)."""
		state = read_state(controller)
		locations, runs = detect.step(prev, state, runs) if prev else ([], 0)
		self.locations_found.update(locations)
		if self.slot is None:
			return state, runs  # not connected: checks wait in locations_found
		if self.locations_found:
			await self.check_locations(self.locations_found)
			self.locations_found.clear()
		writes, self.items_applied = receive.apply_new(self.received_names(), self.items_applied, state)
		for entry, value in writes:
			write_int(controller, entry, value)
		return state, runs


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
