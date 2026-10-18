from dataclasses import dataclass

from Options import Choice, DeathLink, PerGameCommonOptions, Range, Toggle


class Mode(Choice):
	"""Which mode you play.
	practice: stages unlock with Next Stage items, played from Practice.
	normal_dynamic: full runs from stage 1; gates are lives, power, difficulty and character. The difficulty is
	always the lowest unlocked one, never Easy. With difficulty_check this acts as normal_static.
	normal_static: same, but the difficulty is the one you pick.
	In normal modes continues are unlimited and a continue restores the lives you got from items."""
	display_name = "Mode"
	option_practice = 0
	option_normal_dynamic = 1
	option_normal_static = 2
	default = 0


class StageUnlock(Choice):
	"""How stage unlocks are grouped in Practice mode, and for Extra Stage items.
	global: one set of stage unlocks for everyone.
	by_character: each character has its own stage unlocks.
	by_shot_type: each shot type has its own stage unlocks.
	Without shot_type or difficulty_check, by_shot_type acts as by_character, since there aren't enough locations otherwise."""
	display_name = "Stage unlock mode"
	option_global = 0
	option_by_character = 1
	option_by_shot_type = 2
	default = 0


class ProgressiveStage(Toggle):
	"""Stages unlock progressively (Next Stage items); off, each stage has its own unlock item (Stage 2 .. Stage 6)."""
	display_name = "Progressive Stage Unlock"
	default = True


class ShotTypeCheck(Toggle):
	"""If each shot type has its own checks and they are not just separated by character"""
	display_name = "Shot Type Check"


class DifficultyCheck(Toggle):
	"""If midboss and boss checks are separated by difficulty."""
	display_name = "Difficulty Check"


class CheckMultipleDifficulty(Toggle):
	"""For difficulty checks, beating a boss also sends its checks of the lower difficulties you have unlocked."""
	display_name = "Multiple Difficulty Check"


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


class ExtraStage(Choice):
	"""Whether the Extra stage (Sanae, Koishi) is included.
	exclude: no Extra stage.
	linear: Extra is a 7th stage, opened by one more Next Stage (progressive) or an Extra Stage item after Stage 6.
	apart: Extra has its own Extra Stage item; the game opens it right away, logic still expects it after Stage 6.
	Extra Stage items follow stage_unlock (global, per character or per shot type)."""
	display_name = "Extra Stage"
	option_exclude = 0
	option_linear = 1
	option_apart = 2
	default = 0


class NumberLifeExtra(Range):
	"""Number of lives the randomizer expects you to have before facing Koishi"""
	display_name = "Lives expected for the Extra stage"
	range_start = 0
	range_end = 8
	default = 0


class PowerExtra(Range):
	"""Number of +0.50 Power packs the randomizer expects you to have before facing Koishi"""
	display_name = "Power packs expected for the Extra stage"
	range_start = 0
	range_end = 8
	default = 0


class UtsuhoEndings(Choice):
	"""How many Utsuho endings (Stage 6 clears) the goal needs.
	once: with either character.
	both_characters: with Reimu and with Marisa.
	shot_types: with utsuho_shots different shot types; turns shot_type on (endings sit on each shot's Stage 6 Clear)."""
	display_name = "Utsuho endings required"
	option_once = 0
	option_both_characters = 1
	option_shot_types = 2
	default = 0


class UtsuhoShots(Range):
	"""With utsuho_endings: shot_types, how many shot types must clear Stage 6."""
	display_name = "Utsuho shot types required"
	range_start = 1
	range_end = 6
	default = 6


class KoishiEndings(Choice):
	"""How many Koishi endings (Extra clears) the goal needs, on top of Utsuho's.
	none: Koishi isn't part of the goal.
	once: with either character.
	both_characters: with Reimu and with Marisa.
	Anything but none turns the Extra stage on (linear) if it's excluded."""
	display_name = "Koishi endings required"
	option_none = 0
	option_once = 1
	option_both_characters = 2
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
	# Off until batch 58 R6 confirms capture detection in game; then alongside (24).
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


class Traps(Range):
	"""Percentage of fillers that are traps"""
	display_name = "Percentage of fillers that are traps"
	range_start = 0
	range_end = 100
	default = 0


class PowerTrap(Range):
	"""Weight of the -50% Power trap: halves your power."""
	display_name = "-50% Power trap"
	range_start = 0
	range_end = 100
	default = 20


class LifeTrap(Range):
	"""Weight of the -1 Life trap: removes a life, but never causes a game over."""
	display_name = "-1 Life trap"
	range_start = 0
	range_end = 100
	default = 0


class NoFocusTrap(Range):
	"""Weight of the No Focus trap: focusing doesn't slow you down for a while."""
	display_name = "No Focus trap"
	range_start = 0
	range_end = 100
	default = 20


class ReverseMovementTrap(Range):
	"""Weight of the Reverse Movement trap: your movement is reversed for a while."""
	display_name = "Reverse Movement trap"
	range_start = 0
	range_end = 100
	default = 20


class AyaSpeedTrap(Range):
	"""Weight of the Aya Speed trap: faster unfocused, slower focused for a while."""
	display_name = "Aya Speed trap"
	range_start = 0
	range_end = 100
	default = 20


class FreezeTrap(Range):
	"""Weight of the Freeze trap: you can't move for a few seconds."""
	display_name = "Freeze trap"
	range_start = 0
	range_end = 100
	default = 5


class PowerDrainTrap(Range):
	"""Weight of the Power Drain trap: you lose 0.05 power per second for a while."""
	display_name = "Power Drain trap"
	range_start = 0
	range_end = 100
	default = 15


class DeathLinkTrigger(Choice):
	"""When your death is sent to the others with DeathLink. Can be changed in the client with /deathlink_trigger.
	life: every life lost.
	game_over: only a game over."""
	display_name = "DeathLink trigger"
	option_life = 0
	option_game_over = 1
	default = 0


class DeathLinkAmnesty(Range):
	"""Deaths forgiven before one is sent: with 2, every third death is sent. Can be changed in the client with /deathlink_amnesty."""
	display_name = "DeathLink amnesty"
	range_start = 0
	range_end = 10
	default = 0


class RingLink(Toggle):
	"""Whether power gained or lost in a stage is shared with other RingLink players (0.05 power is one ring, as in
	MoF). Can be changed in the client with /ringlink."""
	display_name = "RingLink"


class LimitLives(Range):
	"""Most lives a +1 Life (or a normal-mode continue) can give you. Only the client applies it, not the item pool
	or logic. Can be changed in the client with /limits."""
	display_name = "Lives limit"
	range_start = 0
	range_end = 9
	default = 9


class MinLives(Range):
	"""Spare lives a Practice run starts with before any +1 Life: it starts with min_lives + your +1 Life items (at most
	limit_lives). Only the client applies it; logic still counts the +1 Life items for the gates."""
	display_name = "Minimum Practice lives"
	range_start = 0
	range_end = 8
	default = 0


@dataclass
class TH11Options(PerGameCommonOptions):
	mode: Mode
	stage_unlock: StageUnlock
	progressive_stage: ProgressiveStage
	shot_type: ShotTypeCheck
	difficulty_check: DifficultyCheck
	check_multiple_difficulty: CheckMultipleDifficulty
	exclude_lunatic: ExcludeLunatic
	number_life_mid: NumberLifeMid
	power_mid: PowerMid
	difficulty_mid: DifficultyMid
	number_life_end: NumberLifeEnd
	power_end: PowerEnd
	difficulty_end: DifficultyEnd
	extra_stage: ExtraStage
	number_life_extra: NumberLifeExtra
	power_extra: PowerExtra
	utsuho_endings: UtsuhoEndings
	utsuho_shots: UtsuhoShots
	koishi_endings: KoishiEndings
	spell_card_keys: SpellCardKeys
	captures_per_stage: CapturesPerStage
	capture_slots: CaptureSlots
	spell_card_keys_in_pool: SpellCardKeysInPool
	spell_card_keys_required: SpellCardKeysRequired
	traps: Traps
	power_trap: PowerTrap
	life_trap: LifeTrap
	no_focus_trap: NoFocusTrap
	reverse_movement_trap: ReverseMovementTrap
	aya_speed_trap: AyaSpeedTrap
	freeze_trap: FreezeTrap
	power_drain_trap: PowerDrainTrap
	death_link: DeathLink
	death_link_trigger: DeathLinkTrigger
	death_link_amnesty: DeathLinkAmnesty
	ring_link: RingLink
	limit_lives: LimitLives
	min_lives: MinLives
