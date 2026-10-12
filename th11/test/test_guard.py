import unittest

from ..Variables import MENU_CHARACTER as CHARACTER_MENU, MENU_DIFFICULTY as DIFFICULTY_MENU, MENU_SHOT as SHOT_MENU
from ..guard import correct, unlocked_difficulties, unlocked_shots
from ..state import decode_state
from .test_state import PRACTICE_S1, S1


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

	def test_shot_menu_from_probe(self):
		self.assertEqual((CHARACTER_MENU, SHOT_MENU), (2, 3))  # probe 32 R6 M1
		self.assertEqual(correct(menu(3, 0), range(4), {"Reimu B"}), 1)

	def test_shot_menu_moves_to_nearest_unlocked(self):
		self.assertEqual(correct(menu(SHOT_MENU, 0), range(4), {"Reimu B", "Reimu C"}), 1)
		self.assertEqual(correct(menu(SHOT_MENU, 1), range(4), {"Reimu A", "Reimu C"}), 0)  # tie: first
		self.assertEqual(correct(menu(SHOT_MENU, 0, character=1), range(4), {"Reimu A", "Marisa C"}), 2)

	def test_shot_menu_leaves_unlocked_or_hopeless(self):
		self.assertIsNone(correct(menu(SHOT_MENU, 1), range(4), {"Reimu B"}))
		self.assertIsNone(correct(menu(SHOT_MENU, 1), range(4), {"Marisa A"}))  # no Reimu shot to move to

	def test_character_menu_moves_off_character_without_shots(self):
		self.assertEqual(correct(menu(CHARACTER_MENU, 0), range(4), {"Marisa B"}), 1)
		self.assertEqual(correct(menu(CHARACTER_MENU, 1), range(4), {"Reimu C"}), 0)
		self.assertIsNone(correct(menu(CHARACTER_MENU, 1), range(4), {"Reimu C", "Marisa A"}))

	def test_shot_and_character_menus_wait_for_items(self):
		self.assertIsNone(correct(menu(SHOT_MENU, 0), range(4), None))
		self.assertIsNone(correct(menu(CHARACTER_MENU, 0), range(4), None))

	def test_other_menus_and_play_untouched(self):
		self.assertIsNone(correct(menu(0, 0), range(3, 4), set()))  # title
		self.assertIsNone(correct(decode_state(PRACTICE_S1), range(3, 4), set()))
