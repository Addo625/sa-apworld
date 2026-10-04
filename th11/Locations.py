from BaseClasses import Location

from .Variables import *


class TLocation(Location):
	game: str = DISPLAY_NAME


# Every location gets an ID, created or not, so IDs never shift when
# shot type, Extra or difficulty checks are added later (EoSD layout).
location_table = {}
location_id_offset = 0

for character in ALL_CHARACTERS_LIST:
	for level, stage in enumerate(STAGES_LIST, 1):
		for check in stage:
			location_table[f"[{character}] {check}"] = STARTING_ID + location_id_offset
			location_id_offset += 1
		level_name = "Extra" if level == 7 else level
		location_table[f"[{character}] Stage {level_name} Clear"] = STARTING_ID + location_id_offset
		location_id_offset += 1

for difficulty in DIFFICULTY_LIST:
	for character in ALL_CHARACTERS_LIST:
		for stage in STAGES_LIST[:6]:
			for check in stage:
				location_table[f"[{difficulty}][{character}] {check}"] = STARTING_ID + location_id_offset
				location_id_offset += 1
