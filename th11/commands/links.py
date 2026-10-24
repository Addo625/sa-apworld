"""
DeathLink, RingLink and lives-limit commands.
"""
import asyncio

from CommonClient import ClientCommandProcessor, logger

from ..Options import DeathLinkAmnesty, DeathLinkTrigger, LimitLives


class LinkCommands(ClientCommandProcessor):
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

	def _cmd_receivedeath(self):
		"""Kill the player as a received DeathLink would, without another player's death"""
		if "DeathLink" not in self.ctx.tags:
			logger.error("DeathLink is off: /deathlink on first")
			return False
		self.ctx.link.incoming = True
		logger.info("DeathLink: test death received")
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

	def _cmd_limits(self, lives: str = ""):
		"""Set the most lives a +1 Life can give (0-9), or show it"""
		if lives:
			if not lives.isdigit() or not LimitLives.range_start <= int(lives) <= LimitLives.range_end:
				logger.error("Usage: /limits [0-9]")
				return False
			self.ctx.limit_lives = int(lives)
		logger.info(f"Lives limit: {self.ctx.limit_lives}")
		return True
