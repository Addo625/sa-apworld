"""
Item application: received item names -> memory writes. Pure, no memory access.
(Not items.py: it would collide with Items.py on case-insensitive filesystems.)
"""
import logging

from . import Variables
from .Items import item_table
from .Options import Mode
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


def apply(item_name, state, limit_lives=MAX_LIVES):
	"""-> writes [(entry, value)] for one item. limit_lives caps what +1 Life gives; it never takes lives away."""
	if not in_run(state):
		return []
	if item_name == "+1 Life":
		return [(Variables.ADDR_LIVES, max(state.lives, min(state.lives + 1, limit_lives, MAX_LIVES)))]
	if item_name in POWER and state.power is not None:
		return [(Variables.ADDR_POWER, min(state.power + POWER[item_name], MAX_POWER))]
	return []


def with_writes(state, writes):
	"""state as it reads once lives/power writes land."""
	return state._replace(**{"lives" if entry == Variables.ADDR_LIVES else "power": value for entry, value in writes})


def apply_new(item_names, applied, state, limit_lives=MAX_LIVES):
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
		new = apply(name, state, limit_lives)
		writes += new
		state = with_writes(state, new)
	return writes, len(item_names)


def difficulty_for(lower, slot_data):
	"""normal_dynamic: the lowest difficulty `lower` Lower Difficulty items open, never Easy (EoSD). Else None: the player picks."""
	if slot_data.get("mode") != Mode.option_normal_dynamic:
		return None
	return max(1, Variables.lowest_unlocked(lower, slot_data.get("exclude_lunatic")))


def difficulty_writes(state, lower, slot_data):
	"""-> writes forcing normal_dynamic's difficulty during a run of stages 1-6 (EoSD also forces it mid-run)."""
	target = difficulty_for(lower, slot_data)
	if target is None or not in_run(state) or state.stage not in range(1, 7) or state.difficulty not in range(4) or state.difficulty == target:
		return []
	return [(Variables.ADDR_DIFFICULTY, target)]


def continue_lives(item_names, limit_lives=MAX_LIVES):
	"""Lives a normal-mode continue restores: one per +1 Life received (MoF caps it at 8), at most limit_lives."""
	return min(list(item_names).count("+1 Life"), 8, limit_lives)


def goal_reached(item_names, slot_data):
	"""Ending items received meet slot_data's goal and ending_required (missing: Utsuho once)."""
	item_names = list(item_names)
	return goal_met(item_names.count, slot_data.get("goal", 0), slot_data.get("ending_required", 0))
