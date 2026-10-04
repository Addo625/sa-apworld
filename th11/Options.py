from dataclasses import dataclass

from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle


class ExcludeLunatic(Toggle):
	"""Exclude Lunatic difficulty. Start on Hard instead."""
	display_name = "Exclude Lunatic difficulty"


class NumberLifeMid(Range):
	"""Number of lives the randomizer expects you to have before facing Yuugi and Satori"""
	display_name = "Lives expected for stages 3/4"
	range_start = 0
	range_end = 8
	default = 0


class PowerMid(Range):
	"""Number of +0.50 Power packs the randomizer expects you to have before facing Yuugi and Satori"""
	display_name = "Power packs expected for stages 3/4"
	range_start = 0
	range_end = 8
	default = 0


class DifficultyMid(Choice):
	"""The difficulty expected in order to face Yuugi and Satori (starting from Lunatic down to Easy)"""
	display_name = "Difficulty for stages 3/4"
	option_lunatic = 0
	option_hard = 1
	option_normal = 2
	option_easy = 3
	default = 0


class NumberLifeEnd(Range):
	"""Number of lives the randomizer expects you to have before facing Orin and Utsuho"""
	display_name = "Lives expected for stages 5/6"
	range_start = 0
	range_end = 8
	default = 0


class PowerEnd(Range):
	"""Number of +0.50 Power packs the randomizer expects you to have before facing Orin and Utsuho"""
	display_name = "Power packs expected for stages 5/6"
	range_start = 0
	range_end = 8
	default = 0


class DifficultyEnd(Choice):
	"""The difficulty expected in order to face Orin and Utsuho (starting from Lunatic down to Easy)"""
	display_name = "Difficulty for stages 5/6"
	option_lunatic = 0
	option_hard = 1
	option_normal = 2
	option_easy = 3
	default = 0


@dataclass
class TH11Options(PerGameCommonOptions):
	exclude_lunatic: ExcludeLunatic
	number_life_mid: NumberLifeMid
	power_mid: PowerMid
	difficulty_mid: DifficultyMid
	number_life_end: NumberLifeEnd
	power_end: PowerEnd
	difficulty_end: DifficultyEnd
	# Does nothing until ticket 14.
	death_link: DeathLink
