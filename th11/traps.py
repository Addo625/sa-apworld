"""
Traps (EoSD/MoF trap_loop): received trap names -> memory writes over time. Pure, no memory access.
"""
import logging

from . import Variables
from .Items import item_table
from .receive import in_run

logger = logging.getLogger("Client")

TRAPS = {name for name, data in item_table.items() if data.category == "Traps"}
# Speed traps change the four speed floats, one at a time, and restore them after these seconds.
TIMED = {"No Focus": 20, "Reverse Movement": 20, "Aya Speed": 20, "Freeze": 3}
DRAIN_SECONDS = 20  # Power Drain: -1 power unit (0.05) per second for this long
ENTER_DELAY = 2  # seconds in a run before traps fire, so stage setup doesn't overwrite them (EoSD)
SPEED_ENTRIES = ["ADDR_SPEED_NORMAL", "ADDR_SPEED_FOCUS", "ADDR_SPEED_NORMAL_D", "ADDR_SPEED_FOCUS_D"]


def trapped_speeds(name, saved):
	"""(normal, focus, normal diagonal, focus diagonal) while `name` is active."""
	normal, focus, normal_d, focus_d = saved
	return {
		"No Focus": (normal, normal, normal_d, normal_d),
		"Reverse Movement": (-normal, -focus, -normal_d, -focus_d),
		"Aya Speed": (normal * 2, focus / 2, normal_d * 2, focus_d / 2),
		"Freeze": (0.0, 0.0, 0.0, 0.0),
	}[name]


class TrapState:
	def __init__(self):
		self.queue = []  # received, not fired yet; waits outside a run
		self.entered = None  # time the current run was first seen
		self.speed = None  # (name, ends at, saved speeds) of the active speed trap
		self.drain_until = 0
		self.drained_at = 0


def speeds_sourced():
	return None not in [getattr(Variables, name) for name in SPEED_ENTRIES]


def tick(traps, now, state, speeds):
	"""One poll: fire the first queued trap that can fire, run timers. speeds: the 4 speed floats, None if unreadable.
	-> (int writes [(entry, value)], speed writes (4 floats) or None)."""
	if not in_run(state):
		# ponytail: like EoSD, nothing is written outside a run (the player object may be gone) and an active
		# speed trap is forgotten; this assumes each stage rebuilds the player's speeds (35 checks it in game).
		traps.entered, traps.speed, traps.drain_until = None, None, 0
		return [], None
	if traps.entered is None:
		traps.entered = now
	if now - traps.entered < ENTER_DELAY:
		return [], None
	lives, power = state.lives, state.power
	new_speeds = None
	if traps.speed and now >= traps.speed[1] and speeds is not None:
		new_speeds, traps.speed = traps.speed[2], None
	for name in traps.queue:
		if name in TIMED and speeds_sourced() and (traps.speed or speeds is None):
			continue  # one speed trap at a time, and only with the speeds readable
		traps.queue.remove(name)  # one trap per tick, so a backlog doesn't land at once (EoSD)
		logger.info(f"Trap: {name}")
		if name == "-50% Power" and power is not None:
			power //= 2
		elif name == "-1 Life":
			lives = max(lives - 1, 0)  # takes the last spare life, never a game over
		elif name == "Power Drain":
			traps.drain_until = max(traps.drain_until, now) + DRAIN_SECONDS
		elif not speeds_sourced():
			logger.info(f"{name}: pending the speed addresses (probe batch 32 R3, ticket 35)")
		else:
			saved = new_speeds or speeds  # a trap that just expired restores first
			traps.speed = (name, now + TIMED[name], saved)
			new_speeds = trapped_speeds(name, saved)
		break
	if now < traps.drain_until and now - traps.drained_at >= 1 and power:
		power, traps.drained_at = power - 1, now
	writes = []
	if lives != state.lives:
		writes.append((Variables.ADDR_LIVES, lives))
	if power != state.power:
		writes.append((Variables.ADDR_POWER, power))
	return writes, new_speeds
