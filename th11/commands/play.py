"""
Everyday commands: the tracker, item messages and sounds, launching the game.
"""
import os
import subprocess

from CommonClient import ClientCommandProcessor, logger
from settings import get_settings


class PlayCommands(ClientCommandProcessor):
	def _cmd_tracker(self):
		"""Show each stage's gate, what you have toward it, and the checks left (also in the Tracker tab)"""
		for line in self.ctx.tracker_lines():
			logger.info(line)
		return True

	def _cmd_messages(self, which: str = ""):
		"""Item messages: mine (only items you send or receive, the default) or all (everyone's finds)"""
		if which not in ("mine", "all"):
			logger.info(f"Showing {'all item messages' if self.ctx.all_messages else 'only your items'}. Usage: /messages mine|all")
			return False
		self.ctx.all_messages = which == "all"
		logger.info(f"Item messages: {which}")
		return True

	def _cmd_itemsound(self, state: str = ""):
		"""Item sounds on/off (on by default)"""
		if state not in ("on", "off"):
			logger.info(f"Item sounds are {'on' if self.ctx.item_sound else 'off'}. Usage: /itemsound on|off")
			return False
		self.ctx.item_sound = state == "on"
		logger.info(f"Item sounds {state}")
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
