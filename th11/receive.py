"""
Item application: received item names -> memory writes. Pure, no memory access.
(Not items.py: it would collide with Items.py on case-insensitive filesystems.)
"""
import logging

from . import Variables
from .Variables import CHARACTER_TO_ITEM, ENDING_NORMAL_ITEM

logger = logging.getLogger("Client")

MAX_LIVES = 9  # probe 06 S3: Practice starts at 9
MAX_POWER = 80  # 4.00 in units of 0.05 (probe 06)
POWER = {"+0.50 Power": 10, "+0.05 Power": 1}
# These write the practice-unlock bytes, not found yet (26-27). Their counts stay in the received list for 28.
PENDING_UNLOCK = {"Next Stage", "Lower Difficulty"} | {shot for shots in CHARACTER_TO_ITEM.values() for shot in shots}


def in_run(state):
	"""Lives and power only exist during a run; outside one they are leftovers."""
	return state.in_game and state.lives is not None and state.lives >= 0


def apply(item_name, state):
	"""-> writes [(entry, value)] for one item."""
	if not in_run(state):
		return []
	if item_name == "+1 Life":
		return [(Variables.ADDR_LIVES, min(state.lives + 1, MAX_LIVES))]
	if item_name in POWER and state.power is not None:
		return [(Variables.ADDR_POWER, min(state.power + POWER[item_name], MAX_POWER))]
	return []


def apply_new(item_names, applied, state):
	"""-> (writes, items applied). Only items after `applied` take effect, so a reconnect's full replay writes nothing.
	Outside a run nothing is applied: items wait for the next run."""
	# ponytail: `applied` lives in the client only, so restarting the client replays every life and power once;
	# store it in server data storage if that's abused.
	if not in_run(state):
		return [], applied
	writes = []
	for name in item_names[applied:]:
		if name in PENDING_UNLOCK:
			logger.info(f"{name}: pending unlock table (ticket 28)")
		for entry, value in apply(name, state):
			writes.append((entry, value))
			state = state._replace(**{"lives" if entry == Variables.ADDR_LIVES else "power": value})
	return writes, len(item_names)


def goal_reached(item_names):
	return any(name.endswith(ENDING_NORMAL_ITEM) for name in item_names)
