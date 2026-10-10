import logging

from .Variables import *

RESOURCES = ["lives", "power", "difficulty", "keys"]
# ponytail: fixed slack for fill randomness; raise it if a fixed seed in test_extremes_fill_fixed_seeds fails.
GATE_SLACK = 3
# ponytail: +1 slack per this many required keys; measured, 50 required keys failed 3-11 of 50
# fixed seeds at slack 2-5 and 0 at 6-8. Scale with total gate size if non-key gates ever grow.
KEYS_PER_SLACK = 10
# ponytail: non-progressive stage items per character/shot are each needed in one exact sphere, so fill
# clogs early spheres more. Measured at max gates over 100 fixed seeds, per group: by_character failed 3-6 at +1,
# 0 at +2; shot types (6 groups) 5 at +1, 0-1 at +2, 0 at +3.
SLACK_PER_UNLOCK_GROUP = 3


def stage_requirements(mid, end, keys_required, rooms):
	"""Per-stage (lives, power, difficulty, keys) for stages 1-6, cut to fit each stage's room.

	Each resource ramps 0, 0, mid/2, mid, (mid+end)/2, end. Over room, the largest of
	lives/power/keys loses one (ties: lives, power, keys); difficulty goes only once they're 0.
	"""
	requirements, notes = [], []
	for stage, room in enumerate(rooms, 1):
		req = [[0, 0, m // 2, m, (m + e) // 2, e][stage - 1] for m, e in zip(mid, end)]
		req.append(0 if stage < 3 else keys_required * (stage - 2) // 4)
		while sum(req) > room:
			index = max((0, 1, 3), key=lambda i: req[i])  # max() keeps the first of a tie
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


def stage_rooms(world, keys_required=0):
	"""Locations open before each stage that can hold its gate items.

	Opening every owner's stages < k takes (k-1) stage items per unlock group used and every owner's shot.
	Difficulty locations that need Lower Difficulty are gated, so only the hardest difficulty's count."""
	excluded = world.options.exclude_locations.value
	groups = min(len(world.unlock_groups), len(world.owners))
	slack = GATE_SLACK + keys_required // KEYS_PER_SLACK
	if not world.options.progressive_stage:
		slack += SLACK_PER_UNLOCK_GROUP * groups
	open_before, rooms = 0, []
	for stage in range(1, 7):
		rooms.append(open_before - (stage - 1) * groups - (len(world.owners) - 1) - slack)
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


def stage_unlocked(state, player, group, level, progressive):
	prefix = f"[{group}] " if group else ""
	if progressive:
		unlocked = state.has(f"{prefix}Next Stage", player, level - 1)
	else:
		# The game opens stage k with just its item; logic also wants the earlier ones, so stages < k
		# open before k and stage_rooms holds (without this, max gates failed 18 of 50 fixed seeds).
		unlocked = state.has_all([f"{prefix}Stage {stage}" for stage in range(2, level + 1)], player)
	return unlocked and (not group or state.has_any(CHARACTER_TO_ITEM[group], player))


def set_rules(world):
	player, options = world.player, world.options
	get = lambda name: world.multiworld.get_region(name, player)

	def difficulty(gate):
		# Without Lunatic the game starts one step lower.
		return max(0, gate.value - 1) if options.exclude_lunatic else gate.value

	mid = (options.number_life_mid.value, options.power_mid.value, difficulty(options.difficulty_mid))
	end = (options.number_life_end.value, options.power_end.value, difficulty(options.difficulty_end))
	if options.spell_card_keys == options.spell_card_keys.option_keys_only:
		mid = end = (0, 0, 0)
	keys_required = world.key_count * options.spell_card_keys_required.value // 100
	world.stage_requirements, notes = stage_requirements(mid, end, keys_required, stage_rooms(world, keys_required))
	for note in notes:
		logging.warning(f"{SHORT_NAME} ({world.player_name}): gate doesn't fit, {note}")

	progressive = bool(options.progressive_stage)
	for owner in world.owners:
		shots = CHARACTER_TO_ITEM[owner]
		groups = owner_groups(world, owner)
		get("Menu").connect(get(owner), rule=lambda state, shots=shots: state.has_any(shots, player))
		for level, (lives, power, lower, keys) in enumerate(world.stage_requirements, 1):
			get(owner).connect(get(f"[{owner}] Stage {level}"), rule=lambda state, groups=groups, level=level, lives=lives, power=power, lower=lower, keys=keys: (
				any(stage_unlocked(state, player, group, level, progressive) for group in groups)
				and state.has("+1 Life", player, lives)
				and state.has("+0.50 Power", player, power)
				and state.has("Lower Difficulty", player, lower)
				and state.has("Spell Card Key", player, keys)
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

	endings = [f"[{character}] {ENDING_NORMAL_ITEM}" for character in CHARACTERS_LIST]
	world.multiworld.completion_condition[player] = lambda state: state.has_any(endings, player)
