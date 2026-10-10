import unittest

from ..Locations import location_table
from ..detect import step
from ..state import decode_state
from .test_state import PRACTICE_S1, S0

BOSS = 0x3100000


def play(stage=1, boss=False, **values):
	return decode_state({**PRACTICE_S1, "ADDR_STAGE": stage, "ADDR_IS_BOSS_PRESENT": BOSS if boss else 0, **values})


def ids(*names):
	return [location_table[name] for name in names]


def run_stage(stage, runs, **values):
	"""Plays `runs` boss-field on/off pairs from the stage start; returns every location sent."""
	sent, count = [], 0
	states = [decode_state(S0), play(stage, **values)] + [play(stage, boss, **values) for _ in range(runs) for boss in (True, False)]
	for prev, state in zip(states, states[1:]):
		locations, count = step(prev, state, count)
		sent += locations
	return sent


class TestDetect(unittest.TestCase):
	def test_detect_midboss(self):
		self.assertEqual(run_stage(1, 1), ids("[Reimu] Kisume - Midboss"))

	def test_detect_boss(self):
		self.assertEqual(step(play(boss=True), play(), 1), (ids("[Reimu] Yamame Defeated", "[Reimu] Stage 1 Clear"), 2))

	def test_detect_clear(self):
		"""The stage boss leaving (1.7 s before the tally, 06 bossrec) is the clear."""
		self.assertEqual(run_stage(1, 2)[-1:], ids("[Reimu] Stage 1 Clear"))
		self.assertEqual(run_stage(7, 2)[-1:], ids("[Reimu] Stage Extra Clear"))

	def test_detect_negative_menu_exit(self):
		quit_to_menu = decode_state({**S0, "ADDR_STAGE": 1, "ADDR_LIVES": 6})  # S9: enemy manager gone, menu up
		self.assertEqual(step(play(boss=True), quit_to_menu, 1), ([], 1))
		# The field drops on the same poll the menu pointer comes back.
		self.assertEqual(step(play(boss=True), play(boss=False, ADDR_MENU=0), 1), ([], 1))

	def test_detect_negative_game_over(self):
		self.assertEqual(step(play(boss=True), play(ADDR_LIVES=-1), 1), ([], 1))

	def test_detect_stage3_single_run(self):
		self.assertEqual(run_stage(3, 1), ids("[Reimu] Yuugi - Midboss", "[Reimu] Yuugi Defeated", "[Reimu] Stage 3 Clear"))

	def test_detect_stage4_first_appearance(self):
		self.assertEqual(run_stage(4, 1), ids("[Reimu] Cat Orin - First Appearance"))

	def test_detect_stage4_second_appearance(self):
		self.assertEqual(step(play(4, boss=True), play(4), 1), (ids("[Reimu] Cat Orin - Second Appearance"), 2))

	def test_detect_stage4_satori_after_two_runs(self):
		self.assertEqual(run_stage(4, 3), ids(
			"[Reimu] Cat Orin - First Appearance", "[Reimu] Cat Orin - Second Appearance",
			"[Reimu] Satori Defeated", "[Reimu] Stage 4 Clear",
		))

	def test_detect_stage4_quit_mid_encounter_sends_nothing(self):
		quit_to_menu = decode_state({**S0, "ADDR_STAGE": 4, "ADDR_LIVES": 6})  # S9
		self.assertEqual(step(play(4, boss=True), quit_to_menu, 0), ([], 0))
		self.assertEqual(step(play(4, boss=True), play(4, ADDR_MENU=0), 1), ([], 1))

	def test_detect_full_stage(self):
		self.assertEqual(run_stage(6, 2), ids("[Reimu] Orin - Midboss", "[Reimu] Utsuho Defeated", "[Reimu] Stage 6 Clear"))

	def test_detect_extra_runs_send_nothing(self):
		self.assertEqual(run_stage(1, 3), run_stage(1, 2))

	def test_detect_restart_resets_runs(self):
		"""Back to the menu and into the stage again: the next run is the midboss again."""
		self.assertEqual(step(decode_state(S0), play(), 1), ([], 0))
		self.assertEqual(step(play(stage=1), play(stage=2), 1), ([], 0))

	def test_detect_marisa(self):
		self.assertEqual(run_stage(2, 1, ADDR_CHARACTER=1), ids("[Marisa] Parsee - Midboss"))


SHOT = {"shot_type": True}
DIFFICULTY = {"difficulty_check": True}
MULTIPLE = {"difficulty_check": True, "check_multiple_difficulty": True}


def boss_kill(slot_data, lower=0, **values):
	"""Stage 1 boss leaves (the second run): Normal, Reimu A unless overridden."""
	return step(play(boss=True, **values), play(**values), 1, slot_data, lower)[0]


class TestDetectGranularity(unittest.TestCase):
	def test_detect_shot_type(self):
		self.assertEqual(boss_kill(SHOT, ADDR_CHARACTER=1, ADDR_SHOT_TYPE=2), ids("[Marisa C] Yamame Defeated", "[Marisa C] Stage 1 Clear"))

	def test_detect_difficulty(self):
		self.assertEqual(boss_kill(DIFFICULTY), ids("[Normal][Reimu] Yamame Defeated", "[Reimu] Stage 1 Clear"))

	def test_detect_shot_type_and_difficulty(self):
		self.assertEqual(boss_kill({**SHOT, **DIFFICULTY}, ADDR_DIFFICULTY=3, ADDR_SHOT_TYPE=1), ids(
			"[Lunatic][Reimu B] Yamame Defeated", "[Reimu B] Stage 1 Clear",
		))

	def test_detect_difficulty_without_multiple_sends_one(self):
		self.assertEqual(boss_kill(DIFFICULTY, lower=3, ADDR_DIFFICULTY=2), ids("[Hard][Reimu] Yamame Defeated", "[Reimu] Stage 1 Clear"))

	def test_detect_multiple_difficulty_sends_unlocked_lower(self):
		# Hard with 2 Lower Difficulty: Normal is unlocked, Easy isn't.
		self.assertEqual(boss_kill(MULTIPLE, lower=2, ADDR_DIFFICULTY=2), ids(
			"[Normal][Reimu] Yamame Defeated", "[Hard][Reimu] Yamame Defeated", "[Reimu] Stage 1 Clear",
		))
		self.assertEqual(boss_kill(MULTIPLE, lower=3, ADDR_DIFFICULTY=3)[:4], ids(
			"[Easy][Reimu] Yamame Defeated", "[Normal][Reimu] Yamame Defeated",
			"[Hard][Reimu] Yamame Defeated", "[Lunatic][Reimu] Yamame Defeated",
		))

	def test_detect_multiple_difficulty_exclude_lunatic(self):
		# Without Lunatic the game starts on Hard: 1 Lower Difficulty opens Normal.
		self.assertEqual(boss_kill({**MULTIPLE, "exclude_lunatic": True}, lower=1, ADDR_DIFFICULTY=2)[:2], ids(
			"[Normal][Reimu] Yamame Defeated", "[Hard][Reimu] Yamame Defeated",
		))

	def test_detect_unreadable_difficulty_still_clears(self):
		self.assertEqual(boss_kill(DIFFICULTY, ADDR_DIFFICULTY=None), ids("[Reimu] Stage 1 Clear"))

	def test_detect_extra_has_no_difficulty_checks(self):
		self.assertEqual(
			step(play(7, boss=True, ADDR_DIFFICULTY=4), play(7, ADDR_DIFFICULTY=4), 1, DIFFICULTY)[0],
			ids("[Reimu] Koishi Defeated", "[Reimu] Stage Extra Clear"),
		)

	def test_detect_ignores_locked_shot(self):
		"""Practice S3 is Reimu A on Normal: without Reimu A's item the run counts but sends nothing."""
		self.assertEqual(step(play(boss=True), play(), 0, shots={"Reimu B"}, lower=3), ([], 1))
		self.assertEqual(step(play(boss=True), play(), 0, shots={"Reimu A"}, lower=3)[0], ids("[Reimu] Kisume - Midboss"))

	def test_detect_ignores_locked_difficulty(self):
		self.assertEqual(step(play(boss=True), play(), 0, shots={"Reimu A"}, lower=1), ([], 1))  # Normal needs 2
		self.assertEqual(step(play(boss=True), play(), 0, shots={"Reimu A"}, lower=2)[0], ids("[Reimu] Kisume - Midboss"))
		extra = step(play(7, boss=True, ADDR_DIFFICULTY=4), play(7, ADDR_DIFFICULTY=4), 1, shots={"Reimu A"})[0]
		self.assertEqual(extra, ids("[Reimu] Koishi Defeated", "[Reimu] Stage Extra Clear"))  # Extra has no difficulty lock
