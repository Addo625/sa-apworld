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
