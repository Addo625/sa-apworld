import logging

from .Variables import *

RESOURCES = ["lives", "power", "difficulty"]
# ponytail: fixed slack for fill randomness; raise it if a fixed seed in test_extremes_fill_fixed_seeds fails.
GATE_SLACK = 3
# ponytail: +1 slack per this many required keys; measured, 50 required keys failed 3-11 of 50
# fixed seeds at slack 2-5 and 0 at 6-8. Scale with total gate size if non-key gates ever grow.
KEYS_PER_SLACK = 10
# ponytail: a key lock leaves a third of its stage's room free. Measured at max gates, 6 captures and 50 keys over 20-30
# fixed seeds: a 20-key final lock filled every seed, 26 failed 3 of 20. Re-measure if the pool or the caps grow.
KEY_LOCK_MARGIN = 3
# ponytail: non-progressive stage items per character/shot are each needed in one exact sphere, so fill
# clogs early spheres more. Measured at max gates over 100 fixed seeds, per group: by_character failed 3-6 at +1,
# 0 at +2; shot types (6 groups) 5 at +1, 0-1 at +2, 0 at +3.
SLACK_PER_UNLOCK_GROUP = 3
# ponytail: the Extra stage adds a late stage item per group. Measured at max gates (Extra 8/8) over 100 fixed
# seeds, per group: linear 3-5 failed at +0-1 (global, by_character not progressive), apart shot types 4 at +1; 0 at +2.
EXTRA_SLACK = 2


def stage_requirements(mid, end, rooms, extra=(0, 0, 0), round_up=False):
	"""Per-stage (lives, power, difficulty) for stages 1-6, and Extra as stage 7 when rooms has 7 entries,
	cut to fit each stage's room.

	Each resource ramps 0, 0, mid/2, mid, (mid+end)/2, end, rounded down; round_up (a_little_bit_of_luck) rounds the
	difficulty's halves up. Extra needs `extra`. Over room, the larger of lives/power loses one (ties: lives);
	difficulty goes only once they're 0.
	"""
	requirements, notes = [], []
	for stage, room in enumerate(rooms, 1):
		up = [0, 0, round_up]  # lives, power, difficulty: +1 before halving rounds up
		req = [[0, 0, (m + u) // 2, m, (m + e + u) // 2, e, x][stage - 1] for m, e, x, u in zip(mid, end, extra, up)]
		while sum(req) > room:
			index = max((0, 1), key=lambda i: req[i])  # max() keeps the first of a tie
			if req[index] == 0:
				index = 2
				if req[index] == 0:
					break
			req[index] -= 1
			notes.append(f"Stage {stage}: lowered {RESOURCES[index]} to {req[index]} (room {room})")
		requirements.append(tuple(req))
	return requirements, notes


def difficulty_lower(world, difficulty):
	"""Lower Difficulty items needed to play `difficulty`."""
	return lower_difficulty_needed(DIFFICULTY_LIST.index(difficulty), world.options.exclude_lunatic)


def stage_rooms(world, keys=0):
	"""Locations open before each stage that can hold its gate items.

	Opening every owner's stages < k takes (k-1) stage items per unlock group used and every owner's shot.
	Difficulty locations that need Lower Difficulty are gated, so only the hardest difficulty's count.
	keys: the most keys a lock asks of logic (lock + slack), which widens the slack as the old key gate did."""
	excluded = world.options.exclude_locations.value
	groups = min(len(world.unlock_groups), len(world.owners))
	slack = GATE_SLACK + keys // KEYS_PER_SLACK
	if not world.options.progressive_stage and not world.normal:
		slack += SLACK_PER_UNLOCK_GROUP * groups
	if world.options.extra_stage:
		slack += EXTRA_SLACK * groups
	open_before, rooms = 0, []
	for stage in range(1, len(world.stage_regions) + 1):
		# Normal mode has no stage items, only an apart Extra's.
		stage_items = int(stage == 7 and world.options.extra_stage == world.options.extra_stage.option_apart) if world.normal else stage - 1
		rooms.append(open_before - stage_items * groups - (len(world.owners) - 1) - slack)
		regions = world.stage_regions[stage - 1] + [
			region for difficulty, _, region in world.difficulty_regions[stage - 1] if not difficulty_lower(world, difficulty)
		]
		for region in regions:
			open_before += sum(location.name not in excluded for location in region.locations)
	return rooms


def owner_groups(world, owner):
	"""Unlock groups whose stage items open `owner`'s stages ("" = global)."""
	if world.unlock_groups == [""]:
		return [""]
	if owner in world.unlock_groups:
		return [owner]
	if owner in SHOT_TO_CHARACTER:  # by_character with shot-type checks
		return [SHOT_TO_CHARACTER[owner]]
	return [shot for shot in SHOT_TYPE_LIST if SHOT_TO_CHARACTER[shot] == owner]  # by_shot_type with character checks


def key_locks(slot):
	"""Spell Card Keys held to open each level (index 1-6, Extra 7; index 0 unused), from slot data or option values (75).
	The toll closes key_lock_toll_stage and later; the final lock closes Stage 6 and Extra (target stage_6) or Extra
	only (extra); target goal closes no stage. Practice mode only: a normal run can't skip stages."""
	locks = [0] * 8
	if not slot.get("spell_card_keys") or slot.get("mode", 0) != 0:
		return locks
	toll, final, target = slot.get("key_lock_toll", 0), slot.get("key_lock_final", 0), slot.get("key_lock_final_target", 0)
	for level in range(slot.get("key_lock_toll_stage", 5), 8):
		locks[level] = toll
	for level in {0: (6, 7), 2: (7,)}.get(target, ()):
		locks[level] = max(locks[level], final)
	return locks


def stage_unlocked(state, player, group, level, progressive, apart=False, normal=False, keys=0):
	"""Level 7 is Extra: one more Next Stage (linear, progressive), else the Extra Stage item.
	Normal mode needs no stage item but an apart Extra's (EoSD constructStageRule). keys: Spell Card Keys held (75)."""
	prefix = f"[{group}] " if group else ""
	if normal and not (level == 7 and apart):
		unlocked = True
	elif level == 7 and (apart or not progressive):
		unlocked = state.has(f"{prefix}Extra Stage", player)
	elif progressive:
		unlocked = state.has(f"{prefix}Next Stage", player, level - 1)
	else:
		# The game opens stage k with just its item; logic also wants the earlier ones, so stages < k
		# open before k and stage_rooms holds (without this, max gates failed 18 of 50 fixed seeds).
		unlocked = state.has_all([f"{prefix}Stage {stage}" for stage in range(2, level + 1)], player)
	return unlocked and (not group or state.has_any(CHARACTER_TO_ITEM[group], player)) and state.has("Spell Card Key", player, keys)


def fit_key_locks(world, rooms, slack):
	"""Lower a key lock (with the slack) to the locations open before the first stage it closes, as gates are (75)."""
	options, lock = world.options, world.key_lock
	final_level = {0: 6, 2: 7}.get(lock["key_lock_final_target"])
	for option, level in [(options.key_lock_toll, lock["key_lock_toll_stage"]), (options.key_lock_final, final_level)]:
		if not option.value or not key_locks(lock)[level or 0] or level > len(rooms):
			continue
		room = max(rooms[level - 1], 0)
		if option.value + slack > room:
			option.value = max(room - slack, 0)
			logging.warning(f"{SHORT_NAME} ({world.player_name}): {option.__class__.__name__} lowered to {option.value}: "
				f"Stage {'Extra' if level == 7 else level} has room for {room} keys with the slack")
	options.key_lock_final.value = max(options.key_lock_final.value, options.key_lock_toll.value) if options.key_lock_final.value else 0
	lock.update(key_lock_toll=options.key_lock_toll.value, key_lock_final=options.key_lock_final.value)


def plan_gates(world):
	"""Gates and key locks, fitted to the locations before each stage. Runs before create_items, which needs
	world.logic_keys to know how many keys are progression; set_rules then applies them."""
	options = world.options

	def difficulty(gate):
		# Dynamic mode never plays Easy (EoSD); without Lunatic the game starts one step lower.
		value = min(gate.value, gate.option_normal) if options.mode == options.mode.option_normal_dynamic else gate.value
		return max(0, value - 1) if options.exclude_lunatic else value

	mid = (options.number_life_mid.value, options.power_mid.value, difficulty(options.difficulty_mid))
	end = (options.number_life_end.value, options.power_end.value, difficulty(options.difficulty_end))
	extra = (options.number_life_extra.value, options.power_extra.value, 0)
	# Logic counts on a key lock only once the slack is reachable too, so a few missed captures never leave a player stuck.
	slack = options.key_lock_slack.value
	rooms = stage_rooms(world, max(key_locks(world.key_lock)) + slack)
	fit_key_locks(world, rooms, slack)
	logic_keys = [keys + slack if keys else 0 for keys in key_locks(world.key_lock)]
	# The keys take their room first; lives, power and difficulty are cut to fit around them.
	gate_rooms = [room - logic_keys[level] for level, room in enumerate(rooms, 1)]
	world.stage_requirements, notes = stage_requirements(mid, end, gate_rooms, extra, bool(options.a_little_bit_of_luck))
	# A stage's gate items must also sit before every later stage, so a lock shares its room with the largest gate of
	# each resource so far (an all-max seed with a 48-key final lock failed every fill without this).
	held = [sum(max(req[r] for req in world.stage_requirements[:level]) for r in range(3)) for level in range(1, len(rooms) + 1)]
	fit_key_locks(world, [room - gates - max(room, 0) // KEY_LOCK_MARGIN for room, gates in zip(rooms, held)], slack)
	world.logic_keys = [keys + slack if keys else 0 for keys in key_locks(world.key_lock)]
	goal_keys = goal_key_lock(world.key_lock)
	world.goal_keys = goal_keys + slack if goal_keys else 0
	for note in notes:
		logging.warning(f"{SHORT_NAME} ({world.player_name}): gate doesn't fit, {note}")


def set_rules(world):
	player, options = world.player, world.options
	get = lambda name: world.multiworld.get_region(name, player)
	logic_keys = world.logic_keys

	progressive = bool(options.progressive_stage)
	apart = options.extra_stage == options.extra_stage.option_apart
	normal = world.normal
	for owner in world.owners:
		shots = CHARACTER_TO_ITEM[owner]
		groups = owner_groups(world, owner)
		get("Menu").connect(get(owner), rule=lambda state, shots=shots: state.has_any(shots, player))
		for level, (lives, power, lower) in enumerate(world.stage_requirements, 1):
			# ponytail: logic puts Extra after Stage 6 even when apart (the game opens it with the item alone): an apart
			# Extra gated by every life and power pack failed fill 9 of 100 fixed seeds, 0 once chained. To let apart
			# Extra into logic early, connect it from the owner and cap its gate below stage 6's, then re-measure.
			source = get(f"[{owner}] Stage 6") if level == 7 else get(owner)
			source.connect(get(f"[{owner}] Stage {'Extra' if level == 7 else level}"), rule=lambda state, groups=groups, level=level, lives=lives, power=power, lower=lower, keys=logic_keys[level]: (
				any(stage_unlocked(state, player, group, level, progressive, apart, normal, keys) for group in groups)
				and state.has("+1 Life", player, lives)
				and state.has("+0.50 Power", player, power)
				and state.has("Lower Difficulty", player, lower)
			))

	# Shared capture slots open from any owner's stage region.
	for regions in world.stage_regions:
		stages, shared = regions[:len(world.owners)], regions[len(world.owners):]
		for captures in shared:
			for stage in stages:
				stage.connect(captures)

	# A difficulty's checks need its Lower Difficulty count on top of the stage gate.
	for level, regions in enumerate(world.difficulty_regions, 1):
		for difficulty, owner, region in regions:
			get(f"[{owner}] Stage {level}").connect(region, rule=lambda state, lower=difficulty_lower(world, difficulty): (
				state.has("Lower Difficulty", player, lower)
			))

	utsuho, shots, koishi = options.utsuho_endings.value, options.utsuho_shots.value, options.koishi_endings.value
	goal_keys = world.goal_keys
	world.multiworld.completion_condition[player] = lambda state: goal_met(lambda name: state.count(name, player), utsuho, shots, koishi, goal_keys)


def goal_endings(koishi):
	"""Ending items the goal needs: Utsuho always, Koishi unless koishi_endings is none."""
	return [ENDING_NORMAL_ITEM] + ([ENDING_EXTRA_ITEM] if koishi else [])


def ending_count_met(count, ending, mode, shots=6):
	"""mode 0: either character; 1: both characters; 2: at least `shots` endings in total (shot_types: each shot's
	clear holds one "[<character>] Ending", so the endings of both characters add up to the shots that cleared)."""
	per_character = [count(f"[{character}] {ending}") for character in CHARACTERS_LIST]
	if mode == 0:
		return any(per_character)
	if mode == 1:
		return all(per_character)
	return sum(per_character) >= shots


def goal_key_lock(slot):
	"""Spell Card Keys the goal needs: the final lock when its target is the goal (75), else 0."""
	locked = slot.get("spell_card_keys") and slot.get("mode", 0) == 0 and slot.get("key_lock_final_target", 0) == 1
	return slot.get("key_lock_final", 0) if locked else 0


def goal_met(count, utsuho, utsuho_shots, koishi, keys=0):
	"""count(item name) -> int. Both parts must hold: Utsuho's (utsuho_endings, utsuho_shots) and Koishi's
	(koishi_endings: 0 none, 1 once, 2 both characters); keys: Spell Card Keys held, for a goal key lock (75)."""
	return ending_count_met(count, ENDING_NORMAL_ITEM, utsuho, utsuho_shots) and (
		not koishi or ending_count_met(count, ENDING_EXTRA_ITEM, koishi - 1)) and count("Spell Card Key") >= keys
