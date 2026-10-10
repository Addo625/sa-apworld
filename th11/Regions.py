from BaseClasses import Region

from .Locations import TLocation, location_table
from .Variables import *


def create_regions(world):
	"""Menu -> character -> Stage N, one gate per stage. Shared capture slots get a
	"Stage N Captures" region entered from either character's Stage N. Connections live in Rules.
	world.stage_regions[N-1] lists every region of stage N."""
	player, multiworld = world.player, world.multiworld
	shared = world.options.capture_slots == world.options.capture_slots.option_shared
	for name in ["Menu"] + CHARACTERS_LIST:
		multiworld.regions.append(Region(name, player, multiworld))

	world.stage_regions = [[] for _ in range(6)]
	for level, captures in enumerate(world.captures, 1):
		capture_names = [f"Stage {level} - Capture {k}" for k in range(1, captures + 1)]
		for character in CHARACTERS_LIST:
			region = Region(f"[{character}] Stage {level}", player, multiworld)
			stage_checks = STAGES_LIST[level - 1] + (STAGE4_APPEARANCES if level == 4 else [])
			checks = [f"[{character}] {check}" for check in stage_checks] + [f"[{character}] Stage {level} Clear"]
			if not shared:
				checks += [f"[{character}] {name}" for name in capture_names]
			region.add_locations({name: location_table[name] for name in checks}, TLocation)
			world.stage_regions[level - 1].append(region)
		if shared and capture_names:
			region = Region(f"Stage {level} Captures", player, multiworld)
			region.add_locations({name: location_table[name] for name in capture_names}, TLocation)
			world.stage_regions[level - 1].append(region)
		multiworld.regions += world.stage_regions[level - 1]
