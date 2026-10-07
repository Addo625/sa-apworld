from worlds.AutoWorld import World

from .Items import TItem, item_table
from .Locations import location_table
from .Options import TH11Options
from .Regions import create_regions
from .Rules import set_rules
from .Variables import *

# Pooled at max_quantity (one fewer Lower Difficulty without Lunatic). Shot types are added separately.
CORE_ITEMS = ["+1 Life", "+0.50 Power", "Lower Difficulty", "Next Stage"]


class TWorld(World):
	game = DISPLAY_NAME
	options: TH11Options
	options_dataclass = TH11Options

	item_name_to_id = {name: data.code for name, data in item_table.items()}
	location_name_to_id = location_table

	def create_regions(self):
		create_regions(self)

	def set_rules(self):
		set_rules(self)

	def create_item(self, name: str) -> TItem:
		data = item_table[name]
		return TItem(name, data.classification, data.code, self.player)

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
			),
			# Per stage 1-6: (lives, power, lower difficulty, keys), after any fit cuts.
			"stage_requirements": self.stage_requirements,
		}
