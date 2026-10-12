"""
Item application: received item names -> memory writes. Pure, no memory access.
(Not items.py: it would collide with Items.py on case-insensitive filesystems.)
"""
import logging
from collections import Counter

from . import Variables
from .Items import item_table
from .Options import ExtraStage, Mode, ProgressiveStage, StageUnlock
from .Rules import goal_met, stage_unlocked

logger = logging.getLogger("Client")

MAX_LIVES = 9  # probe 06 S3: Practice starts at 9
MAX_POWER = 80  # 4.00 in units of 0.05 (probe 06)
POWER = {"+0.50 Power": 10, "+0.05 Power": 1}
# These write the practice-unlock bytes (ticket 39); their counts stay in the received list for it.
PENDING_UNLOCK = {"Lower Difficulty"} | {
	name for name, data in item_table.items() if data.category == "Characters" or data.category.endswith("Stages")
}
UNLOCK_ITEMS = PENDING_UNLOCK | {name for name, data in item_table.items() if data.category.endswith("Extra Stage")}
SHOT_GROUP = {  # a shot's unlock group, as Rules.owner_groups names it
	StageUnlock.option_global: lambda shot: "",
	StageUnlock.option_by_character: Variables.SHOT_TO_CHARACTER.get,
	StageUnlock.option_by_shot_type: lambda shot: shot,
}


class Received:
	"""Rules' CollectionState calls over a received-name list, so the client opens what logic expects."""
	def __init__(self, item_names):
		self.count = Counter(item_names)

	def has(self, name, player, count=1):
		return self.count[name] >= count

	def has_all(self, names, player):
		return all(self.count[name] for name in names)

	def has_any(self, names, player):
		return any(self.count[name] for name in names)


def extra_shots(item_names, slot_data):
	"""-> indexes (SHOT_TYPE_LIST order, the game's char * 3 + shot) of received shots whose Extra the items open.
	A normal-mode linear Extra is left to the game (its own clear unlocks it)."""
	extra = slot_data.get("extra_stage", ExtraStage.default)
	apart = extra == ExtraStage.option_apart
	normal = slot_data.get("mode", Mode.option_practice) != Mode.option_practice
	if not extra or (normal and not apart):
		return set()
	state, group = Received(item_names), SHOT_GROUP[slot_data.get("stage_unlock", StageUnlock.default)]
	progressive = slot_data.get("progressive_stage", ProgressiveStage.default)
	return {i for i, shot in enumerate(Variables.SHOT_TYPE_LIST) if state.has(Variables.CHARACTER_TO_ITEM[shot][0], None)
		and stage_unlocked(state, None, group(shot), 7, progressive, apart, normal)}


def extra_unlock(current: bytes, shots):
	"""The per-shot ending bytes with Extra's bit set for `shots`; other bits (endings seen) are kept, nothing is locked."""
	return bytes(byte | Variables.EXTRA_UNLOCK_BIT if i in shots else byte for i, byte in enumerate(current))


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
			logger.info(f"{name}: pending unlock address (ticket 39)")
		new = apply(name, state, limit_lives)
		writes += new
		state = with_writes(state, new)
	return writes, len(item_names)


def sound(item_names):
	"""-> the one sound for items applied in a tick (the cave plays one ID at a time): extend > power > ok, or None."""
	kinds = {"extend" if name == "+1 Life" else "power" if name in POWER else "ok" if name in UNLOCK_ITEMS else None for name in item_names}
	return next((kind for kind in ("extend", "power", "ok") if kind in kinds), None)


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
