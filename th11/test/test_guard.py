import unittest

from ..Variables import MENU_DIFFICULTY as DIFFICULTY_MENU
from ..guard import correct, unlocked_difficulties, unlocked_shots
from ..state import decode_state
from .test_state import PRACTICE_S1, S1

SHOT_MENU = 3  # probe 06 S2; Variables keeps it off until 32 R6


def menu(menu, cursor, character=0):
	return decode_state({**S1, "ADDR_MENU": menu, "ADDR_MENU_CURSOR": cursor, "ADDR_CHARACTER": character})


class TestGuard(unittest.TestCase):
	def test_unlocked(self):
		self.assertEqual(unlocked_shots(["Reimu B - Suika", "+1 Life", "Marisa C - Nitori"]), {"Reimu B", "Marisa C"})
		self.assertEqual(list(unlocked_difficulties(0, {})), [3])
		self.assertEqual(list(unlocked_difficulties(1, {"exclude_lunatic": True})), [1, 2, 3])

	def test_difficulty_menu_moves_off_locked(self):
		self.assertEqual(correct(menu(DIFFICULTY_MENU, 0), range(2, 4), set()), 2)
		self.assertEqual(correct(menu(DIFFICULTY_MENU, 1), range(3, 4), set()), 3)

	def test_difficulty_menu_leaves_unlocked(self):
		self.assertIsNone(correct(menu(DIFFICULTY_MENU, 3), range(2, 4), set()))
		self.assertIsNone(correct(menu(DIFFICULTY_MENU, 0), range(4), set()))

	def test_shot_menu_moves_to_nearest_unlocked(self):
		self.assertEqual(correct(menu(SHOT_MENU, 0), range(4), {"Reimu B", "Reimu C"}, SHOT_MENU), 1)
		self.assertEqual(correct(menu(SHOT_MENU, 1), range(4), {"Reimu A", "Reimu C"}, SHOT_MENU), 0)  # tie: first
		self.assertEqual(correct(menu(SHOT_MENU, 0, character=1), range(4), {"Reimu A", "Marisa C"}, SHOT_MENU), 2)

	def test_shot_menu_leaves_unlocked_or_hopeless(self):
		self.assertIsNone(correct(menu(SHOT_MENU, 1), range(4), {"Reimu B"}, SHOT_MENU))
		self.assertIsNone(correct(menu(SHOT_MENU, 1), range(4), {"Marisa A"}, SHOT_MENU))  # no Reimu shot to move to

	def test_shot_menu_off_until_probed(self):
		self.assertIsNone(correct(menu(SHOT_MENU, 0), range(4), {"Reimu B"}))

	def test_other_menus_and_play_untouched(self):
		self.assertIsNone(correct(menu(0, 0), range(3, 4), set()))  # title
		self.assertIsNone(correct(decode_state(PRACTICE_S1), range(3, 4), set(), SHOT_MENU))
