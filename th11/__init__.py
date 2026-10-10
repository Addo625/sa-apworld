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
from .Rules import goal_endings, set_rules
from .Variables import *

# Pooled at max_quantity (one fewer Lower Difficulty without Lunatic). Shot types and stages are added separately.
CORE_ITEMS = ["+1 Life", "+0.50 Power", "Lower Difficulty"]
# With spell_card_keys: keys_only these gate nothing.
KEYS_ONLY_USEFUL = CORE_ITEMS


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
		# Checks belong to characters, or shot types with shot_type; difficulty checks exist per playable difficulty.
		self.owners = SHOT_TYPE_LIST if options.shot_type else CHARACTERS_LIST
		self.difficulties = [d for d in DIFFICULTY_LIST if d != "Lunatic" or not options.exclude_lunatic] if options.difficulty_check else []
		# Too few locations for 30 stage items without extra checks (EoSD).
		if options.stage_unlock == options.stage_unlock.option_by_shot_type and not (options.shot_type or options.difficulty_check):
			options.stage_unlock.value = options.stage_unlock.option_by_character
		# Koishi needs the Extra stage, and all shot types needs shot-type checks (EoSD).
		if not options.extra_stage:
			options.goal.value = options.goal.option_utsuho
		if options.ending_required == options.ending_required.option_all_shot_types and not options.shot_type:
			options.ending_required.value = options.ending_required.option_both_characters
		self.unlock_groups = {
			options.stage_unlock.option_global: [""],
			options.stage_unlock.option_by_character: CHARACTERS_LIST,
			options.stage_unlock.option_by_shot_type: SHOT_TYPE_LIST,
		}[options.stage_unlock.value]
		# Capture slots per stage 1-6, and the keys they put in the pool (rounded half up).
		self.captures = [min(options.captures_per_stage.value, cap) if options.spell_card_keys else 0 for cap in CAPTURE_CAPS]
		slots = sum(self.captures) * (1 if options.capture_slots == options.capture_slots.option_shared else len(self.owners))
		self.key_count = (slots * options.spell_card_keys_in_pool.value + 50) // 100
		if options.spell_card_keys == options.spell_card_keys.option_keys_only and not self.key_count:
			logging.warning(f"{SHORT_NAME} ({self.player_name}): keys_only with no Spell Card Keys in the pool, using alongside")
			options.spell_card_keys.value = options.spell_card_keys.option_alongside

	def create_regions(self):
		create_regions(self)

	def set_rules(self):
		set_rules(self)

	def create_item(self, name: str) -> TItem:
		data = item_table[name]
		classification = data.classification
		if name in KEYS_ONLY_USEFUL and self.options.spell_card_keys == self.options.spell_card_keys.option_keys_only:
			classification = ItemClassification.useful
		return TItem(name, classification, data.code, self.player)

	def create_items(self):
		total_locations = len(self.multiworld.get_unfilled_locations(self.player))

		endings = goal_endings(self.options.goal.value)
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
			names = [f"{prefix}Next Stage"] * 5 if self.options.progressive_stage else [f"{prefix}Stage {level}" for level in range(2, 7)]
			if self.options.extra_stage:  # linear and progressive: one more Next Stage; else an Extra Stage item
				linear = self.options.extra_stage == self.options.extra_stage.option_linear
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
			early[f"{prefix}Next Stage" if self.options.progressive_stage else f"{prefix}Stage 2"] = 1
		pool += [self.create_item("Spell Card Key") for _ in range(self.key_count)]

		pool += [self.create_item(self.get_filler_item_name()) for _ in range(total_locations - len(self.owners) * len(endings) - len(pool))]
		self.multiworld.itempool += pool

	def get_filler_item_name(self) -> str:
		return "+0.05 Power"

	def fill_slot_data(self) -> dict:
		return {
			**self.options.as_dict(
				# stage_unlock is the mode in effect (by_shot_type without extra checks reads by_character).
				"stage_unlock", "progressive_stage", "shot_type", "difficulty_check", "check_multiple_difficulty",
				"exclude_lunatic",
				"number_life_mid", "power_mid", "difficulty_mid",
				"number_life_end", "power_end", "difficulty_end",
				"extra_stage", "number_life_extra", "power_extra",
				# goal and ending_required are in effect (koishi/both without Extra read utsuho,
				# all_shot_types without shot_type reads both_characters).
				"goal", "ending_required",
				"death_link",
				# spell_card_keys is the mode in effect (keys_only without keys reads alongside).
				"spell_card_keys", "captures_per_stage", "capture_slots",
			),
			# Per stage 1-6 and Extra: (lives, power, lower difficulty, keys), after any fit cuts.
			"stage_requirements": self.stage_requirements,
		}
