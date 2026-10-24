import logging
from typing import ClassVar

import settings
from BaseClasses import ItemClassification
from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, Type, components, launch_subprocess

from .Items import TItem, item_table
from .Locations import location_table
from .Options import TH11Options
from .Regions import create_regions
from .Rules import goal_endings, plan_gates, set_rules
from .Variables import *

# Pooled at max_quantity (one fewer Lower Difficulty without Lunatic). Shot types and stages are added separately.
CORE_ITEMS = ["+1 Life", "+0.50 Power", "Lower Difficulty"]
# Trap item -> its weight option; `traps` % of filler is drawn from these.
TRAP_OPTIONS = {
	"-50% Power": "power_trap",
	"-1 Life": "life_trap",
	"No Focus": "no_focus_trap",
	"Reverse Movement": "reverse_movement_trap",
	"Aya Speed": "aya_speed_trap",
	"Freeze": "freeze_trap",
	"Power Drain": "power_drain_trap",
}


def launch_client(*args: str):
	from .Client import launch
	launch_subprocess(launch, name="GameClient", args=args)


components.append(Component(SHORT_NAME + " Client", func=launch_client, component_type=Type.CLIENT))


class TSettings(settings.Group):
	class TGameExe(settings.UserFilePath):
		"""File path to the Touhou SA executable (v1.00a th11.exe)"""
		description = "Touhou SA Executable"

	game_exe: TGameExe = TGameExe("th11.exe")


class TWorld(World):
	game = DISPLAY_NAME
	options: TH11Options
	options_dataclass = TH11Options

	settings_key = "touhou_sa_settings"
	settings: ClassVar[TSettings]

	item_name_to_id = {name: data.code for name, data in item_table.items()}
	location_name_to_id = location_table

	def generate_early(self):
		options = self.options
		# The goal's needs first: they change who owns checks and whether Extra exists.
		if options.utsuho_endings == options.utsuho_endings.option_shot_types and not options.shot_type:
			logging.warning(f"{self.player_name}: utsuho_endings: shot_types needs shot_type; turning it on")
			options.shot_type.value = True
		if options.koishi_endings and not options.extra_stage:
			logging.warning(f"{self.player_name}: koishi_endings needs the Extra stage; extra_stage set to linear")
			options.extra_stage.value = options.extra_stage.option_linear
		# Checks belong to characters, or shot types with shot_type; difficulty checks exist per playable difficulty.
		self.owners = SHOT_TYPE_LIST if options.shot_type else CHARACTERS_LIST
		self.difficulties = [d for d in DIFFICULTY_LIST if d != "Lunatic" or not options.exclude_lunatic] if options.difficulty_check else []
		# Difficulty checks need the difficulty you pick (EoSD).
		if options.mode == options.mode.option_normal_dynamic and options.difficulty_check:
			options.mode.value = options.mode.option_normal_static
		self.normal = options.mode != options.mode.option_practice
		# Too few locations for 30 stage items without extra checks (EoSD).
		if options.stage_unlock == options.stage_unlock.option_by_shot_type and not (options.shot_type or options.difficulty_check):
			options.stage_unlock.value = options.stage_unlock.option_by_character
		self.unlock_groups = {
			options.stage_unlock.option_global: [""],
			options.stage_unlock.option_by_character: CHARACTERS_LIST,
			options.stage_unlock.option_by_shot_type: SHOT_TYPE_LIST,
		}[options.stage_unlock.value]
		# Capture slots per stage 1-6, and the Spell Card Keys in the pool (at most one per capture check).
		self.captures = [min(options.captures_per_stage.value, cap) if options.spell_card_keys else 0 for cap in CAPTURE_CAPS]
		slots = sum(self.captures) * (1 if options.capture_slots == options.capture_slots.option_shared else len(self.owners))
		self.key_count = min(options.spell_card_keys_in_pool.value, slots)
		if self.key_count < options.spell_card_keys_in_pool.value:
			self.warn(f"spell_card_keys_in_pool lowered to {self.key_count}, the number of capture checks")
		self.clamp_key_locks()
		if options.spell_card_keys_local and self.key_count:
			options.local_items.value.add("Spell Card Key")

	def warn(self, message):
		logging.warning(f"{SHORT_NAME} ({self.player_name}): {message}")

	def clamp_key_locks(self):
		"""Key locks (75) the pool can satisfy: each at most the keys in the pool with the slack, the final at least the
		toll; inert (with a warning) in normal modes and for an Extra target without Extra. Kept in self.key_lock."""
		options = self.options
		toll, final = options.key_lock_toll, options.key_lock_final
		if options.key_lock_final_target == options.key_lock_final_target.option_extra and not options.extra_stage and final:
			self.warn("key_lock_final targets the Extra stage, which is excluded; no final lock")
			final.value = 0
		for lock, name in [(toll, "key_lock_toll"), (final, "key_lock_final")]:
			most = max(self.key_count - options.key_lock_slack.value, 0)
			if lock.value > most:
				self.warn(f"{name} lowered to {most}: {self.key_count} keys in the pool, {options.key_lock_slack.value} kept as slack")
				lock.value = most
		if final.value and final.value < toll.value:
			self.warn(f"key_lock_final raised to the toll, {toll.value}")
			final.value = toll.value
		if self.normal and (toll.value or final.value):
			self.warn("key locks work in Practice mode only; this seed has none")
		self.key_lock = options.as_dict("spell_card_keys", "mode", "key_lock_toll", "key_lock_toll_stage", "key_lock_final",
			"key_lock_final_target")

	def create_regions(self):
		create_regions(self)

	def set_rules(self):
		set_rules(self)

	def create_item(self, name: str) -> TItem:
		data = item_table[name]
		classification = data.classification
		if name == "Spell Card Key" and not self.keys_needed():
			classification = ItemClassification.filler  # no lock asks for keys
		return TItem(name, classification, data.code, self.player)

	def keys_needed(self):
		"""Spell Card Keys logic counts on: the largest lock with its slack (75)."""
		return max(self.logic_keys + [self.goal_keys])

	def create_items(self):
		plan_gates(self)
		total_locations = len(self.multiworld.get_unfilled_locations(self.player))

		endings = goal_endings(self.options.koishi_endings.value)
		for owner in self.owners:
			for ending, level in zip([ENDING_NORMAL_ITEM, ENDING_EXTRA_ITEM], [6, "Extra"]):
				if ending in endings:
					location = self.multiworld.get_location(f"[{owner}] Stage {level} Clear", self.player)
					location.place_locked_item(self.create_item(f"[{SHOT_TO_CHARACTER.get(owner, owner)}] {ending}"))

		pool = []
		for name in CORE_ITEMS:
			quantity = item_table[name].max_quantity
			if name == "Lower Difficulty" and self.options.exclude_lunatic:
				quantity -= 1
			pool += [self.create_item(name) for _ in range(quantity)]
		for group in self.unlock_groups:
			prefix = f"[{group}] " if group else ""
			linear = self.options.extra_stage == self.options.extra_stage.option_linear
			if self.normal:  # a run plays every stage: only an apart Extra needs an item
				names = [f"{prefix}Extra Stage"] if self.options.extra_stage and not linear else []
			else:
				names = [f"{prefix}Next Stage"] * 5 if self.options.progressive_stage else [f"{prefix}Stage {level}" for level in range(2, 7)]
				if self.options.extra_stage:  # linear and progressive: one more Next Stage; else an Extra Stage item
					names.append(f"{prefix}Next Stage" if linear and self.options.progressive_stage else f"{prefix}Extra Stage")
			pool += [self.create_item(name) for name in names]

		shots = [shot for character in CHARACTERS_LIST for shot in CHARACTER_TO_ITEM[character]]
		start = self.random.choice(shots)
		self.multiworld.push_precollected(self.create_item(start))
		pool += [self.create_item(shot) for shot in shots if shot != start]
		if self.options.shot_type:
			# The starting shot opens only 3 locations and fill could clog them with gate items (1-7 of 50
			# fixed seeds failed): place another shot and the start's first stage unlock there first.
			owner = SHOT_TYPE_LIST[shots.index(start)]
			prefix = next(f"[{group}] " if group else "" for group in self.unlock_groups if group in ("", owner, SHOT_TO_CHARACTER[owner]))
			early = self.multiworld.local_early_items[self.player]
			early[self.random.choice([shot for shot in shots if shot != start])] = 1
			if not self.normal:
				early[f"{prefix}Next Stage" if self.options.progressive_stage else f"{prefix}Stage 2"] = 1
		# Only the keys logic counts on are progression (all 50 as progression with max gates failed 15 of 20 fixed seeds).
		# The rest still open the game's locks, so they're useful, not filler: they show as worth having in the client
		# and hints, and fill treats useful like filler. Without locks every key is filler (create_item).
		keys = [self.create_item("Spell Card Key") for _ in range(self.key_count)]
		if self.keys_needed():
			for key in keys[self.keys_needed():]:
				key.classification = ItemClassification.useful
		pool += keys

		filler = total_locations - len(self.owners) * len(endings) - len(pool)
		weights = [getattr(self.options, option).value for option in TRAP_OPTIONS.values()]
		traps = filler * self.options.traps.value // 100 if any(weights) else 0
		if traps:
			pool += [self.create_item(name) for name in self.random.choices(list(TRAP_OPTIONS), weights, k=traps)]
		pool += [self.create_item(self.get_filler_item_name()) for _ in range(filler - traps)]
		self.multiworld.itempool += pool

	def get_filler_item_name(self) -> str:
		return "+0.05 Power"

	def fill_slot_data(self) -> dict:
		return {
			**self.options.as_dict(
				# mode and stage_unlock are in effect (normal_dynamic with difficulty_check reads normal_static,
				# by_shot_type without extra checks reads by_character).
				"mode", "stage_unlock", "progressive_stage", "shot_type", "difficulty_check", "check_multiple_difficulty",
				"exclude_lunatic",
				"number_life_mid", "power_mid", "difficulty_mid",
				"number_life_end", "power_end", "difficulty_end",
				"extra_stage", "number_life_extra", "power_extra",
				# The goal (both parts must hold); shot_type/extra_stage above already include what it turned on.
				"utsuho_endings", "utsuho_shots", "koishi_endings",
				"death_link", "death_link_trigger", "death_link_amnesty", "ring_link", "limit_lives", "min_lives",
				"spell_card_keys", "captures_per_stage", "capture_slots",
				# Key locks as the game applies them (after clamping), without the logic slack.
				"key_lock_toll", "key_lock_toll_stage", "key_lock_final", "key_lock_final_target",
			),
			# Per stage 1-6 and Extra: (lives, power, lower difficulty), after any fit cuts.
			"stage_requirements": self.stage_requirements,
		}
