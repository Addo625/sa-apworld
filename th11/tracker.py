"""
Text tracker: what each stage's gate expects, what's received, and the checks left. Pure, no memory access.
"""
from collections import Counter

from . import captures
from .Options import ExtraStage, ProgressiveStage, StageUnlock
from .receive import SHOT_GROUP, goal_reached, practice_lives, stage_open
from .Rules import goal_key_lock, key_locks
from .Variables import (
	CAPTURE_CAPS, CHARACTER_TO_ITEM, CHARACTERS_LIST, DIFFICULTY_LIST, ENDING_EXTRA_ITEM, ENDING_NORMAL_ITEM, SHOT_TO_CHARACTER,
	SHOT_TYPE_LIST, STAGE4_APPEARANCES, STAGES_LIST, lower_difficulty_needed, lowest_unlocked,
)

STAGE_OF_CHECK = {check: level for level, checks in enumerate(STAGES_LIST, 1) for check in checks}
STAGE_OF_CHECK.update({check: 4 for check in STAGE4_APPEARANCES})
UTSUHO_GOAL = ["Utsuho once", "Utsuho with both characters", "Utsuho with {} shot types"]
KOISHI_GOAL = ["", "Koishi once", "Koishi with both characters"]


def stage_name(level):
	return "Extra" if level == 7 else f"Stage {level}"


def location_stage(name):
	"""Location name -> (owner or None for a shared capture slot, level 1-7, is a capture), or None if it isn't a stage check."""
	if name.startswith("[") and name.split("]")[0][1:] in DIFFICULTY_LIST:
		name = name.split("]", 1)[1]
	owner = None
	if name.startswith("["):
		owner, name = name[1:].split("] ", 1)
	if name in STAGE_OF_CHECK:
		return owner, STAGE_OF_CHECK[name], False
	if name.startswith("Stage "):
		level = name.split()[1]
		return owner, 7 if level == "Extra" else int(level), " - Capture " in name
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
	"""What the received items lack for a stage's gate (lives, power, Lower Difficulty), as text parts."""
	lives, power, lower = requirement[:3]  # seeds from before 75 carried keys as a 4th
	parts = []
	if count["+1 Life"] < lives:
		parts.append(f"+1 Life {count['+1 Life']}/{lives}")
	if count["+0.50 Power"] < power:
		parts.append(f"+0.50 Power {count['+0.50 Power']}/{power}")
	if count["Lower Difficulty"] < lower:
		difficulty = next(d for i, d in enumerate(DIFFICULTY_LIST) if lower_difficulty_needed(i, exclude_lunatic) <= lower)
		parts.append(f"{difficulty}: Lower Difficulty {count['Lower Difficulty']}/{lower}")
	return parts


def key_row(held, slot_data):
	"""The key locks (75) in one line, or None when the seed has none: what each lock opens at, and how many more."""
	locks = []
	if key_locks(slot_data)[slot_data.get("key_lock_toll_stage", 5)]:
		locks.append((f"Stage {slot_data['key_lock_toll_stage']} opens at", slot_data["key_lock_toll"]))
	final = slot_data.get("key_lock_final", 0)
	if goal_key_lock(slot_data):
		locks.append(("Goal needs", final))
	elif any(key_locks(slot_data)[6:]) and final:
		locks.append((f"{'Stage 6' if slot_data.get('key_lock_final_target', 0) == 0 else 'Extra'} opens at", final))
	if not locks:
		return None
	if all(held >= keys for _, keys in locks):
		return f"Keys {held} held (all locks open)"
	return f"Keys {held} held  ·  " + "  ·  ".join(
		f"{name} {keys} ({'open' if held >= keys else f'{keys - held} more'})" for name, keys in locks)


def report(item_names, missing_names, slot_data, captured=()):
	"""-> tracker lines. missing_names: location names not checked yet. captured: the "<owner>:<spell slot>" entries this
	seed recorded (68), "" as owner when capture slots are shared."""
	item_names = [name for name in item_names if name]
	count = Counter(item_names)
	requirements = [tuple(r)[:3] for r in slot_data.get("stage_requirements") or [(0, 0, 0)] * 6]
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
	] + [row for row in [key_row(count["Spell Card Key"], slot_data)] if row] + [
		"",
		f"+1 Life {count['+1 Life']} (Practice starts with {practice_lives(item_names, slot_data, slot_data.get('limit_lives', 9))})"
		f"  ·  +0.50 Power {count['+0.50 Power']} (Practice starts at {min(count['+0.50 Power'] * 0.5, 4):.2f})  ·  Lower Difficulty {count['Lower Difficulty']}"
		f" (easiest: {DIFFICULTY_LIST[lowest_unlocked(count['Lower Difficulty'], exclude_lunatic)]})",
		"",
		"OPEN = in logic · PLAYABLE = the game opens it, logic expects more · LOCKED = needs its stage item or keys",
	]
	shots = [shot for shot in SHOT_TYPE_LIST if CHARACTER_TO_ITEM[shot][0] in count]
	if not shots:
		lines.append("No shot type received yet.")
	# A character's shots share checks and stage unlocks unless shot_type or by_shot_type splits them: one block each.
	per_shot = slot_data.get("shot_type") or slot_data.get("stage_unlock") == StageUnlock.option_by_shot_type
	blocks = [(shot, shot) for shot in shots] if per_shot else [
		(f"{character} ({', '.join(shot.split()[1] for shot in group)})", group[0])
		for character in CHARACTERS_LIST if (group := [shot for shot in shots if SHOT_TO_CHARACTER[shot] == character])]
	for title, shot in blocks:
		owner = shot if slot_data.get("shot_type") else SHOT_TO_CHARACTER[shot]
		lines += ["", title + ("" if not per_shot or owner == shot else f" (checks shared with {owner})")]
		if slot_data.get("spell_card_keys"):
			spell_owner = captures.owner(shot, slot_data)
			done = sum(1 for entry in captured if entry.rsplit(":", 1)[0] == spell_owner)
			who = f"{spell_owner} hasn't captured" if spell_owner else "not captured"
			lines.append(f"  Spells captured this seed: {done}. A capture check needs a spell {who} yet in this seed (any difficulty)")
		for level, requirement in enumerate(requirements, 1):
			bosses, spells = left[(owner, level, False)], left[(owner, level, True)] + left[(None, level, True)]
			slots = min(slot_data.get("captures_per_stage", 0), CAPTURE_CAPS[level - 1]) if slot_data.get("spell_card_keys") and level < 7 else 0
			parts = [f"{bosses} boss check{'s' * (bosses != 1)} left"] * bool(bosses)
			parts += [f"captures {slots - spells}/{slots}" if spells else "captures done"] * bool(slots)
			suffix = f" -- {', '.join(parts)}" if bosses or spells else " -- all checked"
			if not stage_open(item_names, slot_data, shot, level):
				# Name only what blocks: the stage item, the keys, or both (open ignoring keys = only keys block).
				needs = [] if stage_open(item_names, {**slot_data, "spell_card_keys": 0}, shot, level) else [
					missing_stage_item(count, group_of(shot), level, progressive, apart)]
				keys = key_locks(slot_data)[level]
				needs += [f"Spell Card Key {count['Spell Card Key']}/{keys}"] * (count["Spell Card Key"] < keys)
				lines.append(f"  {stage_name(level)}: LOCKED, needs {', '.join(needs)}{suffix}")
				continue
			missing = gate_missing(count, requirement, exclude_lunatic)
			lines.append(f"  {stage_name(level)}: " + (f"PLAYABLE, logic expects {', '.join(missing)}" if missing else "OPEN") + suffix)
	return lines
