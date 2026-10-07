"""
Variables (names, lists, IDs). Ported from Nepley's EoSD world (MIT).
"""

DISPLAY_NAME = "Touhou Chireiden ~ Subterranean Animism"
SHORT_NAME = "Touhou SA"
STARTING_ID = 110000

CHARACTERS_LIST = ["Reimu", "Marisa"]
SHOT_TYPE_LIST = ["Reimu A", "Reimu B", "Reimu C", "Marisa A", "Marisa B", "Marisa C"]
ALL_CHARACTERS_LIST = CHARACTERS_LIST + SHOT_TYPE_LIST
CHARACTER_TO_ITEM = {
	"Reimu": ["Reimu A - Yukari", "Reimu B - Suika", "Reimu C - Aya"],
	"Marisa": ["Marisa A - Alice", "Marisa B - Patchouli", "Marisa C - Nitori"],
}
DIFFICULTY_LIST = ["Easy", "Normal", "Hard", "Lunatic"]
EXTRA_CHECKS = ["Sanae - Midboss", "Koishi Defeated"]
# Stage 4's midboss has no spell card and leaves on a timer: no location.
STAGES_LIST = [
	["Kisume - Midboss", "Yamame Defeated"],
	["Parsee - Midboss", "Parsee Defeated"],
	["Yuugi - Midboss", "Yuugi Defeated"],
	["Satori Defeated"],
	["Cat Orin - Midboss", "Orin Defeated"],
	["Orin - Midboss", "Utsuho Defeated"],
	EXTRA_CHECKS,
]
ENDING_NORMAL_ITEM = "Ending - Utsuho"
ENDING_EXTRA_ITEM = "Ending - Koishi"

"""
Addresses for th11.exe v1.00a, relative to the image base 0x400000 (MoF style).
A list is a pointer chain [base, off, ...]; None is not sourced yet (ticket 06 probes, 07 fixes).
thprac = touhouworldcup/thprac thprac_th11.cpp; Globals struct at 0x4A56E0.
"""

GAME_NAME = "th11.exe"

# General
ADDR_GAME_MODE = 0x000A8ECC  # source: thprac menu/replay-select object ptr (0x4A8ECC), MoF-analogue of ADDR_GAME_MODE 0x7784C; "0 = in game" is MoF's meaning, TODO(06)
ADDR_MENU = [0x000A8ECC, 0xB0]  # source: MoF-analogue offset, likely wrong (SA menu struct differs: thprac reads shot at +0x38) TODO(06)
ADDR_MENU_CURSOR = [0x000A8ECC, 0x24]  # source: MoF-analogue offset, likely wrong TODO(06)
ADDR_GAME_FLAGS = 0x000A5758  # source: thprac, bit 0 = practice
ADDR_STAGE = 0x000A5728  # source: thprac STAGE_NUM / Globals.stage
ADDR_DIFFICULTY = 0x000A5720  # source: thprac Globals.difficulty
ADDR_CHARACTER = 0x000A5710  # source: thprac Globals.chara
ADDR_SHOT_TYPE = 0x000A5714  # source: thprac Globals.subshot
ADDR_IS_BOSS_PRESENT = None  # source: none yet; enemy manager ptr is 0x4A8D7C (thprac), boss field offset TODO(06)

# Resources
ADDR_LIVES = 0x000A5718  # source: thprac Globals.lives
ADDR_LIFE_PIECES = 0x000A571C  # source: thprac Globals.life_pieces
ADDR_POWER = 0x000A56E8  # source: thprac Globals.power (0-80 in practice)
ADDR_SCORE = 0x000A56E4  # source: thprac Globals.score
ADDR_CONTINUES = 0x000A573C  # source: thprac Globals.continues (offset 0x5C)

# Save data (score.dat); MoF reads these through ptr 0x7783C, SA's pointer is unknown.
ADDR_PRACTICE_UNLOCK = None  # source: none yet, MoF-analogue table (character x shot x difficulty x stage) TODO(06)
ADDR_EXTRA_UNLOCK = None  # source: none yet, MoF-analogue per-shot bytes TODO(06); thcrap fix_extra_stage_relocking patches Rxede8

# Code patch sites; each carries its original bytes in EXPECTED_BYTES.
ADDR_PRACTICE_STARTING_LIVES = None  # source: none yet, MoF-analogue of 0x1796A TODO(06)
ADDR_NORMAL_CONTINUE_LIVES = None  # source: none yet, MoF-analogue of 0x17955 TODO(06)
EXPECTED_BYTES = {
	"ADDR_PRACTICE_STARTING_LIVES": None,
	"ADDR_NORMAL_CONTINUE_LIVES": None,
}

PROBE_TABLE = {name: value for name, value in globals().items() if name.startswith("ADDR_")}
