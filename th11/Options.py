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


class SpellCardKeys(Choice):
	"""Capturing spell cards becomes checks, and Spell Card Keys in the pool gate stages 3-6.
	off: no capture checks or keys.
	alongside: keys gate stages together with lives, power and difficulty.
	keys_only: keys are the only gate; lives, power and difficulty are just useful.
	keys_only with no keys in the pool acts as alongside."""
	display_name = "Spell Card Keys"
	option_off = 0
	option_alongside = 1
	option_keys_only = 2
	# Off until the client detects captures; ticket 24 flips it to alongside.
	default = 0


class CapturesPerStage(Range):
	"""Capture checks per stage: the k-th different spell card you capture in a stage with a character
	sends that stage's k-th check. Captures count across runs and on any difficulty.
	Capped per stage at the fewest cards any difficulty has (stage 1: 2, stages 2-4: 4, stage 5: 5, stage 6: 6)."""
	display_name = "Captures per stage"
	range_start = 0
	range_end = 6
	default = 2


class CaptureSlots(Choice):
	"""per_character: Reimu and Marisa each have their own capture checks.
	shared: one set of capture checks per stage, sent by either character."""
	display_name = "Capture slots"
	option_per_character = 0
	option_shared = 1
	default = 0


class SpellCardKeysInPool(Range):
	"""Percentage of capture checks that add a Spell Card Key to the pool; the rest add filler."""
	display_name = "Spell Card Keys in pool (%)"
	range_start = 0
	range_end = 100
	default = 50


class SpellCardKeysRequired(Range):
	"""Percentage of the pool's Spell Card Keys needed for stage 6. Earlier stages need 0, 0, 1/4, 1/2, 3/4 of that.
	Gates that don't fit in the checks before a stage are lowered, with a warning."""
	display_name = "Spell Card Keys required (%)"
	range_start = 0
	range_end = 100
	default = 75


@dataclass
class TH11Options(PerGameCommonOptions):
	exclude_lunatic: ExcludeLunatic
	number_life_mid: NumberLifeMid
	power_mid: PowerMid
	difficulty_mid: DifficultyMid
	number_life_end: NumberLifeEnd
	power_end: PowerEnd
	difficulty_end: DifficultyEnd
	spell_card_keys: SpellCardKeys
	captures_per_stage: CapturesPerStage
	capture_slots: CaptureSlots
	spell_card_keys_in_pool: SpellCardKeysInPool
	spell_card_keys_required: SpellCardKeysRequired
	# Does nothing until ticket 14.
	death_link: DeathLink
