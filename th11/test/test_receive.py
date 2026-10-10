import unittest

from .. import Variables
from ..receive import apply, apply_new, goal_reached
from ..state import decode_state
from .test_state import PRACTICE_S1, S0

LIVES, POWER = Variables.ADDR_LIVES, Variables.ADDR_POWER


def play(lives=2, power=0):
	return decode_state({**PRACTICE_S1, "ADDR_LIVES": lives, "ADDR_POWER": power})


class TestApply(unittest.TestCase):
	def test_apply_life(self):
		self.assertEqual(apply("+1 Life", play(lives=2)), [(LIVES, 3)])

	def test_apply_life_cap(self):
		self.assertEqual(apply("+1 Life", play(lives=9)), [(LIVES, 9)])

	def test_apply_power(self):
		self.assertEqual(apply("+0.50 Power", play(power=33)), [(POWER, 43)])
		self.assertEqual(apply("+0.05 Power", play(power=33)), [(POWER, 34)])

	def test_apply_power_cap(self):
		self.assertEqual(apply("+0.50 Power", play(power=75)), [(POWER, 80)])

	def test_apply_outside_a_run_writes_nothing(self):
		self.assertEqual(apply("+1 Life", decode_state(S0)), [])  # menu: lives are leftovers
		self.assertEqual(apply("+1 Life", play(lives=-1)), [])  # game over

	def test_apply_waits_for_a_run(self):
		"""An item received on a menu is applied when the next run starts, not dropped."""
		self.assertEqual(apply_new(["+1 Life"], 0, decode_state(S0)), ([], 0))
		self.assertEqual(apply_new(["+1 Life"], 0, play(lives=2)), ([(LIVES, 3)], 1))

	def test_apply_pending_unlock_items_write_nothing(self):
		for name in ("Next Stage", "Lower Difficulty", "Reimu A - Yukari", "[Marisa] Next Stage", "[Reimu C] Stage 4", "Stage 2", "Extra Stage", "[Marisa B] Extra Stage"):
			with self.assertLogs("Client", "INFO"):
				self.assertEqual(apply_new([name], 0, play()), ([], 1))

	def test_apply_batch_stacks(self):
		self.assertEqual(apply_new(["+1 Life", "+1 Life", "+0.50 Power"], 0, play(lives=2))[0],
			[(LIVES, 3), (LIVES, 4), (POWER, 10)])

	def test_apply_replay_is_idempotent(self):
		"""A reconnect resends the full list from index 0: applying it twice gives the writes of applying it once."""
		received = ["+1 Life", "+0.50 Power", "+0.05 Power"]
		writes, applied = apply_new(received, 0, play())
		self.assertEqual(apply_new(received, applied, play(lives=3, power=11)), ([], 3))
		self.assertEqual(apply_new(received + ["+1 Life"], applied, play(lives=3))[0], [(LIVES, 4)])


class TestGoal(unittest.TestCase):
	def test_goal_reached(self):
		self.assertFalse(goal_reached(["+1 Life", "[Reimu] Ending - Koishi"], {}))
		self.assertTrue(goal_reached(["+1 Life", "[Marisa] Ending - Utsuho"], {}))

	def test_goal_koishi_both_characters(self):
		slot_data = {"goal": 1, "ending_required": 1}
		self.assertFalse(goal_reached(["[Reimu] Ending - Koishi", "[Marisa] Ending - Utsuho"], slot_data))
		self.assertTrue(goal_reached(iter(["[Reimu] Ending - Koishi", "[Marisa] Ending - Koishi"]), slot_data))
