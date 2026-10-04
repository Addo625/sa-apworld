from BaseClasses import Item, ItemClassification, Location, Region
from worlds.AutoWorld import World

DISPLAY_NAME = "Touhou Chireiden ~ Subterranean Animism"
STARTING_ID = 110000


class TItem(Item):
	game = DISPLAY_NAME


class TLocation(Location):
	game = DISPLAY_NAME


class TWorld(World):
	game = DISPLAY_NAME

	item_name_to_id = {"Reimu A - Yukari": STARTING_ID}
	location_name_to_id = {"[Reimu] Stage 1 Clear": STARTING_ID}

	def create_regions(self):
		menu = Region("Menu", self.player, self.multiworld)
		menu.add_locations(self.location_name_to_id, TLocation)
		self.multiworld.regions.append(menu)

	def create_item(self, name: str) -> TItem:
		return TItem(name, ItemClassification.progression, self.item_name_to_id[name], self.player)

	def create_items(self):
		self.multiworld.itempool.append(self.create_item("Reimu A - Yukari"))

	def set_rules(self):
		self.multiworld.completion_condition[self.player] = lambda state: state.has("Reimu A - Yukari", self.player)
