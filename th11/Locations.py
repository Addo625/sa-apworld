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

# Capture slots, appended after the table above ("" = shared slots).
for prefix in [f"[{character}] " for character in ALL_CHARACTERS_LIST] + [""]:
	for level in range(1, 8):
		level_name, count = ("Extra", CAPTURE_IDS_EXTRA) if level == 7 else (level, CAPTURE_IDS_PER_STAGE)
		for k in range(1, count + 1):
			location_table[f"{prefix}Stage {level_name} - Capture {k}"] = STARTING_ID + location_id_offset
			location_id_offset += 1

# Stage 4 cat-Orin appearances (ticket 25), appended after the captures.
for prefix in [f"[{character}] " for character in ALL_CHARACTERS_LIST] + [
	f"[{difficulty}][{character}] " for difficulty in DIFFICULTY_LIST for character in ALL_CHARACTERS_LIST
]:
	for check in STAGE4_APPEARANCES:
		location_table[f"{prefix}{check}"] = STARTING_ID + location_id_offset
		location_id_offset += 1
