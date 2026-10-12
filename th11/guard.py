"""
Menu guard rail: keeps the menu cursor off locked difficulties, characters and shot types. Pure, no memory access.
"""
from .Variables import CHARACTER_TO_ITEM, CHARACTERS_LIST, MENU_CHARACTER, MENU_DIFFICULTY, MENU_SHOT, SHOT_TYPE_LIST, lowest_unlocked


def unlocked_shots(item_names):
	return {shot for shot in SHOT_TYPE_LIST if CHARACTER_TO_ITEM[shot][0] in item_names}


def unlocked_difficulties(lower, slot_data):
	return range(lowest_unlocked(lower, slot_data.get("exclude_lunatic")), 4)


def nearest(cursor, allowed):
	return min(allowed, key=lambda i: (abs(i - cursor), i), default=None)


def correct(state, difficulties, shots):
	"""-> the cursor to write, or None to leave it. A cursor with nothing unlocked to move to is left too.
	shots None (items not in yet): shot and character cursors are left."""
	cursor = state.menu_cursor
	if state.in_game or cursor is None:
		return None
	if state.menu == MENU_DIFFICULTY and cursor in range(4) and cursor not in difficulties:
		return nearest(cursor, difficulties)
	if shots is None:
		return None
	if state.menu == MENU_CHARACTER and cursor in range(2):
		allowed = [i for i in range(2) if any(SHOT_TYPE_LIST.index(shot) // 3 == i for shot in shots)]
	elif state.menu == MENU_SHOT and state.character is not None and cursor in range(3):
		character_shots = SHOT_TYPE_LIST[CHARACTERS_LIST.index(state.character) * 3:][:3]
		allowed = [i for i, shot in enumerate(character_shots) if shot in shots]
	else:
		return None
	return None if cursor in allowed else nearest(cursor, allowed)
