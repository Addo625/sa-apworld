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
CHARACTER_TO_ITEM.update({shot: [item] for shot, item in zip(SHOT_TYPE_LIST, CHARACTER_TO_ITEM["Reimu"] + CHARACTER_TO_ITEM["Marisa"])})
SHOT_TO_CHARACTER = {shot: shot.split()[0] for shot in SHOT_TYPE_LIST}
DIFFICULTY_LIST = ["Easy", "Normal", "Hard", "Lunatic"]


def lower_difficulty_needed(index, exclude_lunatic):
	"""Lower Difficulty items that unlock DIFFICULTY_LIST[index]; without Lunatic the game starts on Hard."""
	return max(0, 3 - index - (1 if exclude_lunatic else 0))


def lowest_unlocked(lower, exclude_lunatic):
	"""Easiest DIFFICULTY_LIST index that `lower` Lower Difficulty items open."""
	return next(i for i in range(4) if lower_difficulty_needed(i, exclude_lunatic) <= lower)


EXTRA_CHECKS = ["Sanae - Midboss", "Koishi Defeated"]
# Stage 4's cat Orin leaves on a timer, twice; her checks are STAGE4_APPEARANCES, appended
# after the captures in the ID table so these IDs don't shift.
STAGES_LIST = [
	["Kisume - Midboss", "Yamame Defeated"],
	["Parsee - Midboss", "Parsee Defeated"],
	["Yuugi - Midboss", "Yuugi Defeated"],
	["Satori Defeated"],
	["Cat Orin - Midboss", "Orin Defeated"],
	["Orin - Midboss", "Utsuho Defeated"],
	EXTRA_CHECKS,
]
STAGE4_APPEARANCES = ["Cat Orin - First Appearance", "Cat Orin - Second Appearance"]
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
MENU_DIFFICULTY = 1  # source: probe 06 S1/S1b: difficulty select, cursor Easy 0 .. Lunatic 3
# Probe 06 S2: character select is menu 3 (cursor 1 on Marisa B), but whether its cursor picks the shot or the
# character is unknown; guard.correct takes it as the shot (A 0, B 1, C 2) of ADDR_CHARACTER. TODO(32 R6, 38)
MENU_SHOT = None
ADDR_GAME_FLAGS = 0x000A5758  # source: probe 06: 0x10 in Practice play (S3-S7, S11), 4 on character select (S2), 0 in Extra (S10)
ADDR_STAGE = 0x000A5728  # source: probe 06 S3-S10: 1-6, Extra = 7
ADDR_DIFFICULTY = 0x000A5720  # source: probe 06 S3-S11: Easy 0 .. Lunatic 3, Extra 4; set on confirm, not on cursor move
ADDR_CHARACTER = 0x000A5710  # source: probe 06 S2-S7: Reimu 0, Marisa 1
ADDR_SHOT_TYPE = 0x000A5714  # source: probe 06 S2-S7: A 0, B 1, C 2
ADDR_IS_BOSS_PRESENT = [ADDR_ENEMY_MANAGER, 0x1C]  # source: 06 /bossrec + /bosswatch stages 1, 2, 5, 6: boss object ptr, non-zero while a midboss or boss is up
ADDR_REPLAY_MGR_PTR = 0x000A8EB8  # source: thprac REPLAY_MGR_PTR; not probed, candidate for ADDR_IN_DEMO
ADDR_IN_DEMO = None  # source: none yet, EoSD-analogue (th06 ADDR_IN_DEMO): non-zero while a replay plays, so the run is not play TODO(32 R8, 41)

# Resources; outside a run these hold leftovers from the last run or the title demo (probe 06 S1, S9).
ADDR_LIVES = 0x000A5718  # source: probe 06 S3-S11; -1 = game over (S10)
ADDR_LIFE_PIECES = 0x000A571C  # source: probe 06 S6, S11b
ADDR_POWER = 0x000A56E8  # source: probe 06 S4-S12: units of 0.05, max 80 (4.00), a bomb costs 20
ADDR_SCORE = 0x000A56E4  # source: probe 06 S4-S11: stored /10
ADDR_CONTINUES = 0x000A573C  # source: thprac Globals.continues (offset 0x5C); 0 in every 06 probe, no continue used

# Player movement speeds, D = diagonal. Unlike MoF's floats (player + 0x3D4..0x3E0), SA keeps int32 = speed x 128:
# the player init (0x42F8A0) scales the shot's .sht floats (+0x10..+0x1C, sht ptr at player + 0x92C) by 128.0
# into player + 0x890..0x89C, and the movement code (0x4303AD) reads the focus pair while player + 0x8D20 is set.
ADDR_PLAYER_PTR = 0x000A8EB4  # source: thprac `#define player (*(Player**)0x4a8eb4)`; static (35): the 0x8D24-byte player's constructor stores it here (0x42F852)
ADDR_SPEED_NORMAL = [ADDR_PLAYER_PTR, 0x890]  # source: static disassembly (35), as above; P3-style poke in probe batch 44 R4
ADDR_SPEED_FOCUS = [ADDR_PLAYER_PTR, 0x894]  # source: static disassembly (35)
ADDR_SPEED_NORMAL_D = [ADDR_PLAYER_PTR, 0x898]  # source: static disassembly (35)
ADDR_SPEED_FOCUS_D = [ADDR_PLAYER_PTR, 0x89C]  # source: static disassembly (35)

# Spell captures. thprac_th11.cpp has no spell ID, bonus or history code (its spell practice
# patches ECL), and FearLess and disassembly weren't reachable in 22: each entry has one source at most.
ADDR_SPELL_ID = None  # source: none yet, current spell card ID (spells.js 0-174) or -1 TODO(23)
ADDR_SPELL_BONUS = None  # source: none yet, spell bonus flag/value on capture TODO(23)
ADDR_SPELL_HISTORY = [0x000C343C, 0x6E8]  # source: 06 dumps only: paired u32 counters (attempts/captures?) at a 0x20 stride that rose in play TODO(23)

# Save data (score.dat); MoF reads these through ptr 0x7783C, SA's pointer is unknown.
ADDR_PRACTICE_UNLOCK = None  # source: none yet, MoF-analogue table (character x shot x difficulty x stage) TODO(06)
# Save struct + 0x2DDEA: one ending byte per shot (char * 3 + shot), bad endings 0-5 then good endings 6-11. A good ending
# on Normal+ sets bit 0x10, which is Extra unlocked for that shot (thcrap fix_extra_stage_relocking at 0x40EDE8 keeps it).
ADDR_EXTRA_UNLOCK = [0x000A8EBC, 0x2DDF0]  # source: probe 32 R1 failed (ST bytes), so static disassembly (33): every Extra menu tests bit 0x10 here (0x43CC17, 0x43D0EF, any-shot 0x439350)
EXTRA_UNLOCK_BIT = 0x10  # source: 33, as above

# Code patch sites; each carries its original bytes in EXPECTED_BYTES.
ADDR_PRACTICE_STARTING_LIVES = None  # source: none yet, MoF-analogue of 0x1796A TODO(06)
ADDR_NORMAL_CONTINUE_LIVES = 0x0001FA38  # source: static disassembly (34): a continue re-runs the game init, whose non-Practice branch stores esi (mov esi, 2 at 0x41F947, shared with an ANM interrupt) into lives; rewritten by NORMAL_CONTINUE_LIVES_CODE TODO(32 R2)
NORMAL_CONTINUE_LIVES_CODE = lambda lives: bytes([0xB8, lives, 0, 0, 0, 0xEB, 0x17, 0x90])  # source: 34; mov eax, lives; jmp 0x41FA56 (the Practice branch's mov [lives], eax); nop

ADDR_KILL_CONDITION = None  # source: none yet, MoF-analogue of 0x25A91 (jmp E9 DC 02 00 00 past the hit, NOP'd to kill); EXPECTED_BYTES are the jump TODO(32 R5, 36)
# Item sounds (MoF initSoundHack): a code cave plays the sound ID the client writes to a spare dword, then zeroes it.
# Static disassembly (40); relocations are stripped, so the absolute addresses in the cave are fixed. TODO(32 R9)
ADDR_CUSTOM_SOUND_ID = 0x000CAF00  # source: 40: .data slack past its virtual end 0x4CAE40, mapped (page) and zero, never referenced
ADDR_SOUND_HACK_1 = 0x00029058  # source: 40: call 0x44A340 (sound queue update) in the supervisor's per-frame calc 0x429030; becomes call cave
ADDR_SOUND_HACK_2 = 0x0008AF00  # source: 40: zero slack past .text's end 0x48AE15, executable; holds SOUND_CAVE
SOUND_IDS = {"extend": 0x2C, "power": 0x1D, "ok": 0x0A}  # source: 40: sound table 0x4A34F0 -> se_extend, se_powerup, se_ok00; extend 0x420950 and item pickup 0x423ABA play the first two
_SOUND_ID = (0x400000 + ADDR_CUSTOM_SOUND_ID).to_bytes(4, "little")
SOUND_HOOK = bytes.fromhex("e8 a3 1e 06 00")  # source: 40; call 0x48AF00 (the cave), which tail-jumps to the replaced call's 0x44A340
SOUND_CAVE = (  # source: 40
	bytes.fromhex("60 8b 35") + _SOUND_ID  # pushad; mov esi, [sound id]
	+ bytes.fromhex("85 f6 74 1d c7 05") + _SOUND_ID + bytes(4)  # test esi, esi; jz done; mov [sound id], 0
	+ bytes.fromhex("e8 c6 f2 fb ff")  # call 0x44A1E0: queue sound esi (what extend does)
	+ bytes.fromhex("83 3d 84 8d 4a 00 00 74 05 e8 62 5a f9 ff")  # if the HUD [0x4A8D84] is up, call 0x42098A: extend's tail redraws lives/pieces
	+ bytes.fromhex("61 e9 12 f4 fb ff")  # done: popad; jmp 0x44A340
)
EXPECTED_BYTES = {
	"ADDR_PRACTICE_STARTING_LIVES": None,
	"ADDR_NORMAL_CONTINUE_LIVES": bytes.fromhex("89 35 18 57 4a 00 eb 1b"),  # mov [lives], esi; jmp 0x41FA5B
	"ADDR_KILL_CONDITION": None,
	"ADDR_SOUND_HACK_1": bytes.fromhex("e8 e3 12 02 00"),  # call 0x44A340
	"ADDR_SOUND_HACK_2": bytes(len(SOUND_CAVE)),
}

PROBE_TABLE = {name: value for name, value in globals().items() if name.startswith("ADDR_")}
