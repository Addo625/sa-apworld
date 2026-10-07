import logging

from .Variables import *

RESOURCES = ["lives", "power", "difficulty", "keys"]
# ponytail: fixed slack for fill randomness; raise it if a fixed seed in test_extremes_fill_fixed_seeds fails.
GATE_SLACK = 2


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


def stage_rooms(world):
	"""Locations open before each stage that can hold its gate items."""
	excluded = world.options.exclude_locations.value
	open_before, rooms = 0, []
	for stage in range(1, 7):
		rooms.append(open_before - (stage - 1) - 1 - GATE_SLACK)
		for character in CHARACTERS_LIST:
			region = world.multiworld.get_region(f"[{character}] Stage {stage}", world.player)
			open_before += sum(location.name not in excluded for location in region.locations)
	return rooms


def set_rules(world):
	player, options = world.player, world.options
	get = lambda name: world.multiworld.get_region(name, player)

	def difficulty(gate):
		# Without Lunatic the game starts one step lower.
		return max(0, gate.value - 1) if options.exclude_lunatic else gate.value

	mid = (options.number_life_mid.value, options.power_mid.value, difficulty(options.difficulty_mid))
	end = (options.number_life_end.value, options.power_end.value, difficulty(options.difficulty_end))
	world.stage_requirements, notes = stage_requirements(mid, end, 0, stage_rooms(world))
	for note in notes:
		logging.warning(f"{SHORT_NAME} ({world.player_name}): gate doesn't fit, {note}")

	for character in CHARACTERS_LIST:
		shots = CHARACTER_TO_ITEM[character]
		get("Menu").connect(get(character), rule=lambda state, shots=shots: state.has_any(shots, player))
		# Keys are always 0 until ticket 21 adds the Spell Card Key item and its rule.
		for level, (lives, power, lower, _keys) in enumerate(world.stage_requirements, 1):
			get(character).connect(get(f"[{character}] Stage {level}"), rule=lambda state, stages=level - 1, lives=lives, power=power, lower=lower: (
				state.has("Next Stage", player, stages)
				and state.has("+1 Life", player, lives)
				and state.has("+0.50 Power", player, power)
				and state.has("Lower Difficulty", player, lower)
			))

	endings = [f"[{character}] {ENDING_NORMAL_ITEM}" for character in CHARACTERS_LIST]
	world.multiworld.completion_condition[player] = lambda state: state.has_any(endings, player)
