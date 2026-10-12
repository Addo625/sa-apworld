"""
DeathLink (EoSD death_link_loop): lives read each poll -> deaths to send. Pure, no memory access.
"""
import logging

from .Options import DeathLinkAmnesty, DeathLinkTrigger

logger = logging.getLogger("Client")


class LinkState:
	def __init__(self, trigger=DeathLinkTrigger.default, amnesty=DeathLinkAmnesty.default):
		self.trigger = trigger  # DeathLinkTrigger value; /deathlink_trigger changes it
		self.amnesty = amnesty  # deaths forgiven before one is sent; /deathlink_amnesty changes it
		self.deaths = 0  # forgiven so far
		self.incoming = False  # a received death that hasn't killed the player yet


def on_state(prev, state, link):
	"""prev: last poll's state after the client's own writes (items, traps), so only the game lowers lives here.
	-> True when this poll's death should be sent."""
	# A game over counts even if the stage is already torn down by the poll that reads -1 (probe 32 R5 K5).
	if not (prev and prev.in_game and (state.in_game or state.lives == -1)) or None in (prev.lives, state.lives):
		return False  # a menu exit or a new run: lives are leftovers, not deaths
	# A pause-menu Restart that resets lives lower isn't a death: probe 32 R5 K4b saw none sent (Practice and full run).
	if prev.lives < 0 or state.lives >= prev.lives:
		return False
	if link.incoming:
		link.incoming = False  # the death the link asked for (or one that beat it to it) is never echoed
		return False
	if link.trigger == DeathLinkTrigger.option_game_over and state.lives >= 0:
		return False
	if link.deaths < link.amnesty:
		link.deaths += 1
		logger.info(f"DeathLink: {link.deaths}/{link.amnesty} deaths forgiven")
		return False
	link.deaths = 0
	return True
