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
from .Rules import set_rules
from .Variables import *

# Pooled at max_quantity (one fewer Lower Difficulty without Lunatic). Shot types are added separately.
CORE_ITEMS = ["+1 Life", "+0.50 Power", "Lower Difficulty", "Next Stage"]
# With spell_card_keys: keys_only these gate nothing.
KEYS_ONLY_USEFUL = CORE_ITEMS[:3]


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
		# Capture slots per stage 1-6, and the keys they put in the pool (rounded half up).
		self.captures = [min(options.captures_per_stage.value, cap) if options.spell_card_keys else 0 for cap in CAPTURE_CAPS]
		slots = sum(self.captures) * (1 if options.capture_slots == options.capture_slots.option_shared else len(CHARACTERS_LIST))
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

		for character in CHARACTERS_LIST:
			location = self.multiworld.get_location(f"[{character}] Stage 6 Clear", self.player)
			location.place_locked_item(self.create_item(f"[{character}] {ENDING_NORMAL_ITEM}"))

		pool = []
		for name in CORE_ITEMS:
			quantity = item_table[name].max_quantity
			if name == "Lower Difficulty" and self.options.exclude_lunatic:
				quantity -= 1
			pool += [self.create_item(name) for _ in range(quantity)]

		shots = [shot for character in CHARACTERS_LIST for shot in CHARACTER_TO_ITEM[character]]
		start = self.random.choice(shots)
		self.multiworld.push_precollected(self.create_item(start))
		pool += [self.create_item(shot) for shot in shots if shot != start]
		pool += [self.create_item("Spell Card Key") for _ in range(self.key_count)]

		pool += [self.create_item(self.get_filler_item_name()) for _ in range(total_locations - len(CHARACTERS_LIST) - len(pool))]
		self.multiworld.itempool += pool

	def get_filler_item_name(self) -> str:
		return "+0.05 Power"

	def fill_slot_data(self) -> dict:
		return {
			**self.options.as_dict(
				"exclude_lunatic",
				"number_life_mid", "power_mid", "difficulty_mid",
				"number_life_end", "power_end", "difficulty_end",
				"death_link",
				# spell_card_keys is the mode in effect (keys_only without keys reads alongside).
				"spell_card_keys", "captures_per_stage", "capture_slots",
			),
			# Per stage 1-6: (lives, power, lower difficulty, keys), after any fit cuts.
			"stage_requirements": self.stage_requirements,
		}
