"""
Menu guard rail: keeps the menu cursor off locked difficulties and shot types. Pure, no memory access.
"""
from .Variables import CHARACTER_TO_ITEM, CHARACTERS_LIST, MENU_DIFFICULTY, MENU_SHOT, SHOT_TYPE_LIST, lowest_unlocked


def unlocked_shots(item_names):
	return {shot for shot in SHOT_TYPE_LIST if CHARACTER_TO_ITEM[shot][0] in item_names}


def unlocked_difficulties(lower, slot_data):
	return range(lowest_unlocked(lower, slot_data.get("exclude_lunatic")), 4)


def nearest(cursor, allowed):
	return min(allowed, key=lambda i: (abs(i - cursor), i), default=None)


def correct(state, difficulties, shots, shot_menu=MENU_SHOT):
	"""-> the cursor to write, or None to leave it. A cursor with nothing unlocked to move to is left too."""
	cursor = state.menu_cursor
	if state.in_game or cursor is None:
		return None
	if state.menu == MENU_DIFFICULTY and cursor in range(4) and cursor not in difficulties:
		return nearest(cursor, difficulties)
	if shot_menu is not None and state.menu == shot_menu and state.character is not None and cursor in range(3):
		character_shots = SHOT_TYPE_LIST[CHARACTERS_LIST.index(state.character) * 3:][:3]
		allowed = [i for i, shot in enumerate(character_shots) if shot in shots]
		if cursor not in allowed:
			return nearest(cursor, allowed)
	return None
