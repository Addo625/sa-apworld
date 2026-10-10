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
# Capture slots per stage 1-6: the fewest spell cards any difficulty offers (stage 1:
# Kisume's card is Hard/Lunatic only). From memory and spells.js's ID grouping; 23 verifies it.
CAPTURE_CAPS = [2, 4, 4, 4, 5, 6]
# IDs are reserved up to these counts (Extra has 13 cards); only stages 1-6 are created.
CAPTURE_IDS_PER_STAGE = 6
CAPTURE_IDS_EXTRA = 13
ENDING_NORMAL_ITEM = "Ending - Utsuho"
ENDING_EXTRA_ITEM = "Ending - Koishi"

"""
Addresses for th11.exe v1.00a, relative to the image base 0x400000 (MoF style).
A list is a pointer chain [base, off, ...]; None is not sourced yet (its TODO marks it not reached in 06).
"probe 06 Sx" = verified against ticket 06's /probe capture of state Sx (fixtures in test/test_state.py).
thprac = touhouworldcup/thprac thprac_th11.cpp; Globals struct at 0x4A56E0.
"""

GAME_NAME = "th11.exe"

# General
ADDR_MENU_PTR = 0x000A8ECC  # source: probe 06 S0-S2, S9: menu object ptr, 0 in play but also 0 on some menus (S8b); not a game mode
ADDR_ENEMY_MANAGER = 0x000A8D7C  # source: thprac enemy manager ptr; probe 06 S8b: 0 outside a stage, so non-zero = in a stage
ADDR_MENU = [ADDR_MENU_PTR, 0xB0]  # source: probe 06 S0-S2, S9 (menu ptr + 0xB0)
ADDR_MENU_CURSOR = [ADDR_MENU_PTR, 0x24]  # source: probe 06 S1/S1b (Normal 1, Lunatic 3)
ADDR_GAME_FLAGS = 0x000A5758  # source: probe 06: 0x10 in Practice play (S3-S7, S11), 4 on character select (S2), 0 in Extra (S10)
ADDR_STAGE = 0x000A5728  # source: probe 06 S3-S10: 1-6, Extra = 7
ADDR_DIFFICULTY = 0x000A5720  # source: probe 06 S3-S11: Easy 0 .. Lunatic 3, Extra 4; set on confirm, not on cursor move
ADDR_CHARACTER = 0x000A5710  # source: probe 06 S2-S7: Reimu 0, Marisa 1
ADDR_SHOT_TYPE = 0x000A5714  # source: probe 06 S2-S7: A 0, B 1, C 2
ADDR_IS_BOSS_PRESENT = [ADDR_ENEMY_MANAGER, 0x1C]  # source: 06 /bossrec + /bosswatch stages 1, 2, 5, 6: boss object ptr, non-zero while a midboss or boss is up

# Resources; outside a run these hold leftovers from the last run or the title demo (probe 06 S1, S9).
ADDR_LIVES = 0x000A5718  # source: probe 06 S3-S11; -1 = game over (S10)
ADDR_LIFE_PIECES = 0x000A571C  # source: probe 06 S6, S11b
ADDR_POWER = 0x000A56E8  # source: probe 06 S4-S12: units of 0.05, max 80 (4.00), a bomb costs 20
ADDR_SCORE = 0x000A56E4  # source: probe 06 S4-S11: stored /10
ADDR_CONTINUES = 0x000A573C  # source: thprac Globals.continues (offset 0x5C); 0 in every 06 probe, no continue used

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
