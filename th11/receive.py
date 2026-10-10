"""
Item application: received item names -> memory writes. Pure, no memory access.
(Not items.py: it would collide with Items.py on case-insensitive filesystems.)
"""
import logging

from . import Variables
from .Items import item_table
from .Rules import goal_met

logger = logging.getLogger("Client")

MAX_LIVES = 9  # probe 06 S3: Practice starts at 9
MAX_POWER = 80  # 4.00 in units of 0.05 (probe 06)
POWER = {"+0.50 Power": 10, "+0.05 Power": 1}
# These write the practice-unlock bytes, not found yet (26-27), or the Extra unlock (ADDR_EXTRA_UNLOCK, 32).
# Their counts stay in the received list for 28 and 32.
PENDING_UNLOCK = {"Lower Difficulty"} | {
	name for name, data in item_table.items()
	if data.category == "Characters" or data.category.endswith(("Stages", "Extra Stage"))
}


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
			logger.info(f"{name}: pending unlock address (tickets 28, 32)")
		for entry, value in apply(name, state):
			writes.append((entry, value))
			state = state._replace(**{"lives" if entry == Variables.ADDR_LIVES else "power": value})
	return writes, len(item_names)


def goal_reached(item_names, slot_data):
	"""Ending items received meet slot_data's goal and ending_required (missing: Utsuho once)."""
	item_names = list(item_names)
	return goal_met(item_names.count, slot_data.get("goal", 0), slot_data.get("ending_required", 0))
