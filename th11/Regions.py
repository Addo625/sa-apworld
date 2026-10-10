from BaseClasses import Region

from .Locations import TLocation, location_table
from .Variables import *


def create_regions(world):
	"""Menu -> owner (character, or shot type with shot_type) -> Stage N, one gate per stage.
	Difficulty checks live in "[<Difficulty>][<owner>] Stage N", entered from the owner's Stage N.
	Shared capture slots get a "Stage N Captures" region entered from any owner's Stage N.
	With extra_stage, "[<owner>] Stage Extra" is stage 7.
	Connections live in Rules. world.stage_regions[N-1] lists stage N's owner and shared capture regions,
	world.difficulty_regions[N-1] its difficulty regions as (difficulty, owner, region)."""
	player, multiworld = world.player, world.multiworld
	shared = world.options.capture_slots == world.options.capture_slots.option_shared
	for name in ["Menu"] + world.owners:
		multiworld.regions.append(Region(name, player, multiworld))

	def region(name, checks):
		new = Region(name, player, multiworld)
		new.add_locations({check: location_table[check] for check in checks}, TLocation)
		multiworld.regions.append(new)
		return new

	world.stage_regions = [[] for _ in range(6)]
	world.difficulty_regions = [[] for _ in range(6)]
	for level, captures in enumerate(world.captures, 1):
		capture_names = [f"Stage {level} - Capture {k}" for k in range(1, captures + 1)]
		stage_checks = STAGES_LIST[level - 1] + (STAGE4_APPEARANCES if level == 4 else [])
		for owner in world.owners:
			checks = [f"[{owner}] Stage {level} Clear"]
			if not world.difficulties:
				checks += [f"[{owner}] {check}" for check in stage_checks]
			if not shared:
				checks += [f"[{owner}] {name}" for name in capture_names]
			world.stage_regions[level - 1].append(region(f"[{owner}] Stage {level}", checks))
			for difficulty in world.difficulties:
				checks = [f"[{difficulty}][{owner}] {check}" for check in stage_checks]
				world.difficulty_regions[level - 1].append((difficulty, owner, region(f"[{difficulty}][{owner}] Stage {level}", checks)))
		if shared and capture_names:
			world.stage_regions[level - 1].append(region(f"Stage {level} Captures", capture_names))
	if world.options.extra_stage:  # stage 7: no difficulty or capture checks
		world.stage_regions.append([
			region(f"[{owner}] Stage Extra", [f"[{owner}] {check}" for check in EXTRA_CHECKS + ["Stage Extra Clear"]])
			for owner in world.owners
		])
		world.difficulty_regions.append([])
