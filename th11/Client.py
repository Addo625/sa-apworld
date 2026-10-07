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
from settings import get_settings

from .Variables import DISPLAY_NAME, GAME_NAME, PROBE_TABLE, SHORT_NAME
from .probe import format_probe


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
	"""Touhou SA context: connection and commands only, no game loop yet (ticket 08)."""
	game = DISPLAY_NAME
	items_handling = 0b111  # Item from starting inventory, own world and other world
	command_processor = TouhouClientProcessor

	async def server_auth(self, password_requested: bool = False):
		if password_requested and not self.password:
			await super().server_auth(password_requested)
		await self.get_username()
		await self.send_connect()


def launch(*args: str):
	async def main(args):
		ctx = TouhouContext(args.connect, args.password)
		ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
		if gui_enabled:
			ctx.run_gui()
		ctx.run_cli()
		await ctx.exit_event.wait()
		await ctx.shutdown()

	parser = get_base_parser(description=SHORT_NAME + " Client")
	args, _ = parser.parse_known_args(args)

	import colorama
	colorama.just_fix_windows_console()
	asyncio.run(main(args))
