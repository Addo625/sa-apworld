from .Regions import GROUPS
from .Variables import *


def resources_rule(player, lives, power, difficulty):
	return lambda state: (
		state.count("+1 Life", player) >= lives
		and state.count("+0.50 Power", player) >= power
		and state.count("Lower Difficulty", player) >= difficulty
	)


def set_rules(world):
	player, options = world.player, world.options
	get = lambda name: world.multiworld.get_region(name, player)

	def difficulty(gate):
		# Without Lunatic the game starts one step lower.
		return max(0, gate.value - 1) if options.exclude_lunatic else gate.value

	group_rules = {
		"Early": None,
		"Mid": resources_rule(player, options.number_life_mid.value, options.power_mid.value, difficulty(options.difficulty_mid)),
		"Late": resources_rule(player, options.number_life_end.value, options.power_end.value, difficulty(options.difficulty_end)),
	}

	for character in CHARACTERS_LIST:
		shots = CHARACTER_TO_ITEM[character]
		get("Menu").connect(get(character), rule=lambda state, shots=shots: state.has_any(shots, player))
		for group, levels in GROUPS.items():
			get(character).connect(get(f"[{character}] {group}"), rule=group_rules[group])
			for level in levels:
				get(f"[{character}] {group}").connect(
					get(f"[{character}] Stage {level}"),
					rule=lambda state, n=level - 1: state.has("Next Stage", player, n),
				)

	endings = [f"[{character}] {ENDING_NORMAL_ITEM}" for character in CHARACTERS_LIST]
	world.multiworld.completion_condition[player] = lambda state: state.has_any(endings, player)
