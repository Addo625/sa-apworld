"""
Game state decoding from the address table. Pure: works on {entry name: value} or any reader.
"""
from typing import NamedTuple, Optional

from . import Variables
from .probe import read_entry

STATE_ENTRIES = [
	"ADDR_ENEMY_MANAGER", "ADDR_IS_BOSS_PRESENT", "ADDR_MENU", "ADDR_MENU_CURSOR", "ADDR_STAGE",
	"ADDR_DIFFICULTY", "ADDR_CHARACTER", "ADDR_SHOT_TYPE", "ADDR_LIVES", "ADDR_POWER", "ADDR_IN_DEMO",
]


class GameState(NamedTuple):
	"""None = unreadable."""
	in_game: bool  # a stage is being played (enemy manager exists, not a replay)
	boss_present: bool  # a midboss or boss is up
	menu: Optional[int]  # menu id, None in play
	menu_cursor: Optional[int]
	stage: Optional[int]  # 1-6, Extra 7
	difficulty: Optional[int]  # Easy 0 .. Lunatic 3, Extra 4
	character: Optional[str]
	shot: Optional[str]
	lives: Optional[int]  # -1 = game over
	power: Optional[int]  # units of 0.05, max 80


def decode_state(values) -> GameState:
	"""values: {entry name: int, or None when unreadable}; missing entries count as unreadable."""
	# A replay (title Demo Play) isn't play: no checks, deaths, rings, traps or items in it (ticket 30).
	in_game = bool(values.get("ADDR_ENEMY_MANAGER")) and not values.get("ADDR_IN_DEMO")
	character, shot = values.get("ADDR_CHARACTER"), values.get("ADDR_SHOT_TYPE")
	valid = character in (0, 1) and shot in (0, 1, 2)
	return GameState(
		in_game=in_game,
		boss_present=in_game and bool(values.get("ADDR_IS_BOSS_PRESENT")),
		menu=values.get("ADDR_MENU"),
		menu_cursor=values.get("ADDR_MENU_CURSOR"),
		stage=values.get("ADDR_STAGE"),
		difficulty=values.get("ADDR_DIFFICULTY"),
		character=Variables.CHARACTERS_LIST[character] if valid else None,
		shot=Variables.SHOT_TYPE_LIST[character * 3 + shot] if valid else None,
		lives=values.get("ADDR_LIVES"),
		power=values.get("ADDR_POWER"),
	)


def read_state(reader) -> GameState:
	return decode_state({name: read_entry(reader, getattr(Variables, name)) for name in STATE_ENTRIES})
