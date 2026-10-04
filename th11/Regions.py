from BaseClasses import Region

from .Locations import TLocation, location_table
from .Variables import *

GROUPS = {"Early": (1, 2), "Mid": (3, 4), "Late": (5, 6)}


def create_regions(world):
	"""Menu -> character -> Early/Mid/Late -> Stage N (EoSD shape). Connections live in Rules."""
	player, multiworld = world.player, world.multiworld
	names = ["Menu"]
	for character in CHARACTERS_LIST:
		names += [character] + [f"[{character}] {group}" for group in GROUPS]
	for name in names:
		multiworld.regions.append(Region(name, player, multiworld))

	for character in CHARACTERS_LIST:
		for level, stage in enumerate(STAGES_LIST[:6], 1):
			region = Region(f"[{character}] Stage {level}", player, multiworld)
			checks = [f"[{character}] {check}" for check in stage] + [f"[{character}] Stage {level} Clear"]
			region.add_locations({name: location_table[name] for name in checks}, TLocation)
			multiworld.regions.append(region)
