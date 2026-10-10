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
