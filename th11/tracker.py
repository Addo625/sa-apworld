"""
Text tracker: what each stage's gate expects, what's received, and the checks left. Pure, no memory access.
"""
from collections import Counter

from .Options import ExtraStage, ProgressiveStage, StageUnlock
from .receive import SHOT_GROUP, goal_reached, practice_lives, stage_open
from .Variables import (
	CHARACTER_TO_ITEM, CHARACTERS_LIST, DIFFICULTY_LIST, ENDING_EXTRA_ITEM, ENDING_NORMAL_ITEM, SHOT_TO_CHARACTER,
	SHOT_TYPE_LIST, STAGE4_APPEARANCES, STAGES_LIST, lower_difficulty_needed, lowest_unlocked,
)

STAGE_OF_CHECK = {check: level for level, checks in enumerate(STAGES_LIST, 1) for check in checks}
STAGE_OF_CHECK.update({check: 4 for check in STAGE4_APPEARANCES})
UTSUHO_GOAL = ["Utsuho once", "Utsuho with both characters", "Utsuho with {} shot types"]
KOISHI_GOAL = ["", "Koishi once", "Koishi with both characters"]


def stage_name(level):
	return "Extra" if level == 7 else f"Stage {level}"


def location_stage(name):
	"""Location name -> (owner or None for a shared capture slot, level 1-7), or None if it isn't a stage check."""
	if name.startswith("[") and name.split("]")[0][1:] in DIFFICULTY_LIST:
		name = name.split("]", 1)[1]
	owner = None
	if name.startswith("["):
		owner, name = name[1:].split("] ", 1)
	if name in STAGE_OF_CHECK:
		return owner, STAGE_OF_CHECK[name]
	if name.startswith("Stage "):
		level = name.split()[1]
		return owner, 7 if level == "Extra" else int(level)
	return None


def missing_stage_item(count, group, level, progressive, apart):
	"""The stage item a locked stage still needs, as text."""
	prefix = f"[{group}] " if group else ""
	if level == 7 and (apart or not progressive):
		return f"{prefix}Extra Stage"
	if progressive:
		return f"{prefix}Next Stage {count[prefix + 'Next Stage']}/{level - 1}"
	return ", ".join(f"{prefix}Stage {stage}" for stage in range(2, level + 1) if not count[f"{prefix}Stage {stage}"])


def gate_missing(count, requirement, exclude_lunatic):
	"""What the received items lack for a stage's gate (lives, power, Lower Difficulty, keys), as text parts."""
	lives, power, lower, keys = requirement
	parts = []
	if count["+1 Life"] < lives:
		parts.append(f"+1 Life {count['+1 Life']}/{lives}")
	if count["+0.50 Power"] < power:
		parts.append(f"+0.50 Power {count['+0.50 Power']}/{power}")
	if count["Lower Difficulty"] < lower:
		difficulty = next(d for i, d in enumerate(DIFFICULTY_LIST) if lower_difficulty_needed(i, exclude_lunatic) <= lower)
		parts.append(f"{difficulty}: Lower Difficulty {count['Lower Difficulty']}/{lower}")
	if count["Spell Card Key"] < keys:
		parts.append(f"Spell Card Key {count['Spell Card Key']}/{keys}")
	return parts


def report(item_names, missing_names, slot_data):
	"""-> tracker lines. missing_names: location names not checked yet."""
	item_names = [name for name in item_names if name]
	count = Counter(item_names)
	requirements = [tuple(r) for r in slot_data.get("stage_requirements") or [(0, 0, 0, 0)] * 6]
	exclude_lunatic = slot_data.get("exclude_lunatic")
	group_of = SHOT_GROUP[slot_data.get("stage_unlock", StageUnlock.default)]
	progressive = slot_data.get("progressive_stage", ProgressiveStage.default)
	apart = slot_data.get("extra_stage", ExtraStage.default) == ExtraStage.option_apart
	left = Counter(filter(None, map(location_stage, missing_names)))

	utsuho, koishi = slot_data.get("utsuho_endings", 0), slot_data.get("koishi_endings", 0)
	goal = UTSUHO_GOAL[utsuho].format(slot_data.get("utsuho_shots", 6)) + (f" + {KOISHI_GOAL[koishi]}" if koishi else "")
	endings = [ENDING_NORMAL_ITEM] + ([ENDING_EXTRA_ITEM] if koishi else [])
	lines = [
		f"Goal: {goal} -- {'DONE' if goal_reached(item_names, slot_data) else 'not yet'}",
		"  " + ", ".join(f"{ending}: " + " / ".join(f"{c} {count[f'[{c}] {ending}']}" for c in CHARACTERS_LIST) for ending in endings),
		"",
		f"+1 Life {count['+1 Life']} (Practice starts with {practice_lives(item_names, slot_data, slot_data.get('limit_lives', 9))})"
		f"  ·  +0.50 Power {count['+0.50 Power']} (Practice starts at {min(count['+0.50 Power'] * 0.5, 4):.2f})  ·  Lower Difficulty {count['Lower Difficulty']}"
		f" (easiest: {DIFFICULTY_LIST[lowest_unlocked(count['Lower Difficulty'], exclude_lunatic)]})"
		+ (f"  ·  Spell Card Key {count['Spell Card Key']}" if slot_data.get("spell_card_keys") else ""),
		"",
		"OPEN = in logic · PLAYABLE = the game opens it, logic expects more · LOCKED = needs its stage item",
	]
	shots = [shot for shot in SHOT_TYPE_LIST if CHARACTER_TO_ITEM[shot][0] in count]
	if not shots:
		lines.append("No shot type received yet.")
	for shot in shots:
		owner = shot if slot_data.get("shot_type") else SHOT_TO_CHARACTER[shot]
		lines += ["", f"{shot}" + ("" if owner == shot else f" (checks shared with {owner})")]
		for level, requirement in enumerate(requirements, 1):
			checks = left[(owner, level)] + left[(None, level)]
			suffix = f" -- {checks} check{'s' * (checks != 1)} left" if checks else " -- all checked"
			if not stage_open(item_names, slot_data, shot, level):
				lines.append(f"  {stage_name(level)}: LOCKED, needs {missing_stage_item(count, group_of(shot), level, progressive, apart)}{suffix}")
				continue
			missing = gate_missing(count, requirement, exclude_lunatic)
			lines.append(f"  {stage_name(level)}: " + (f"PLAYABLE, logic expects {', '.join(missing)}" if missing else "OPEN") + suffix)
	return lines
