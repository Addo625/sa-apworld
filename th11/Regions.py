from BaseClasses import Region

from .Locations import TLocation, location_table
from .Variables import *


def create_regions(world):
	"""Menu -> character -> Stage N, one gate per stage. Connections live in Rules."""
	player, multiworld = world.player, world.multiworld
	for name in ["Menu"] + CHARACTERS_LIST:
		multiworld.regions.append(Region(name, player, multiworld))

	for character in CHARACTERS_LIST:
		for level, stage in enumerate(STAGES_LIST[:6], 1):
			region = Region(f"[{character}] Stage {level}", player, multiworld)
			checks = [f"[{character}] {check}" for check in stage] + [f"[{character}] Stage {level} Clear"]
			region.add_locations({name: location_table[name] for name in checks}, TLocation)
			multiworld.regions.append(region)
