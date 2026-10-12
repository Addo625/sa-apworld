import unittest

from .. import Variables
from ..receive import apply, apply_new, extra_shots, extra_unlock, goal_reached, sound
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

	def test_apply_life_respects_limit(self):
		self.assertEqual(apply("+1 Life", play(lives=2), limit_lives=3), [(LIVES, 3)])
		self.assertEqual(apply("+1 Life", play(lives=3), limit_lives=3), [(LIVES, 3)])
		self.assertEqual(apply("+1 Life", play(lives=9), limit_lives=3), [(LIVES, 9)])  # never takes lives away
		self.assertEqual(apply_new(["+1 Life"] * 3, 0, play(lives=2), 3)[0], [(LIVES, 3), (LIVES, 3), (LIVES, 3)])

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
		for name in ("Next Stage", "Lower Difficulty", "Reimu A - Yukari", "[Marisa] Next Stage", "[Reimu C] Stage 4", "Stage 2"):
			with self.assertLogs("Client", "INFO"):
				self.assertEqual(apply_new([name], 0, play()), ([], 1))
		with self.assertNoLogs("Client", "INFO"):  # written by extra_shots, not pending
			self.assertEqual(apply_new(["Extra Stage", "[Marisa B] Extra Stage"], 0, play()), ([], 2))

	def test_apply_batch_stacks(self):
		self.assertEqual(apply_new(["+1 Life", "+1 Life", "+0.50 Power"], 0, play(lives=2))[0],
			[(LIVES, 3), (LIVES, 4), (POWER, 10)])

	def test_apply_replay_is_idempotent(self):
		"""A reconnect resends the full list from index 0: applying it twice gives the writes of applying it once."""
		received = ["+1 Life", "+0.50 Power", "+0.05 Power"]
		writes, applied = apply_new(received, 0, play())
		self.assertEqual(apply_new(received, applied, play(lives=3, power=11)), ([], 3))
		self.assertEqual(apply_new(received + ["+1 Life"], applied, play(lives=3))[0], [(LIVES, 4)])


REIMU, MARISA_B = ["Reimu A - Yukari", "Reimu B - Suika", "Reimu C - Aya"], "Marisa B - Patchouli"
APART = {"extra_stage": 2}


class TestExtra(unittest.TestCase):
	def test_apply_extra_stage_global(self):
		self.assertEqual(extra_shots(REIMU + [MARISA_B], APART), set())
		self.assertEqual(extra_shots(REIMU + [MARISA_B, "Extra Stage"], APART), {0, 1, 2, 4})  # received shots only
		self.assertEqual(extra_shots(REIMU + ["Extra Stage"], {}), set())  # extra_stage exclude

	def test_apply_extra_stage_per_character(self):
		slot_data = {**APART, "stage_unlock": 1}
		self.assertEqual(extra_shots(REIMU + [MARISA_B, "[Marisa] Extra Stage"], slot_data), {4})

	def test_apply_extra_stage_per_shot(self):
		slot_data = {**APART, "stage_unlock": 2}
		self.assertEqual(extra_shots(REIMU + [MARISA_B, "[Reimu B] Extra Stage"], slot_data), {1})
		self.assertEqual(extra_shots(["Reimu A - Yukari", "[Reimu B] Extra Stage"], slot_data), set())  # Reimu B not received

	def test_linear_extra_follows_stage_items(self):
		progressive = {"extra_stage": 1}
		self.assertEqual(extra_shots([MARISA_B] + ["Next Stage"] * 5, progressive), set())
		self.assertEqual(extra_shots([MARISA_B] + ["Next Stage"] * 6, progressive), {4})
		self.assertEqual(extra_shots([MARISA_B, "Extra Stage"], {**progressive, "progressive_stage": False}), {4})

	def test_normal_mode_leaves_linear_extra_to_the_game(self):
		self.assertEqual(extra_shots([MARISA_B] + ["Next Stage"] * 6, {"extra_stage": 1, "mode": 1}), set())
		self.assertEqual(extra_shots([MARISA_B, "Extra Stage"], {**APART, "mode": 1}), {4})

	def test_extra_unlock_keeps_other_bits(self):
		self.assertEqual(extra_unlock(bytes([0, 1, 0x11, 0, 0, 0]), {0, 1, 2}), bytes([0x10, 0x11, 0x11, 0, 0, 0]))

	def test_extra_unlock_replay_is_idempotent(self):
		"""The bytes are a function of the full received list: a reconnect's replay writes the same bytes."""
		once = extra_unlock(bytes(6), extra_shots(REIMU + ["Extra Stage"], APART))
		self.assertEqual(extra_unlock(once, extra_shots(REIMU + ["Extra Stage"] * 2, APART)), once)


class TestGoal(unittest.TestCase):
	def test_goal_reached(self):
		self.assertFalse(goal_reached(["+1 Life", "[Reimu] Ending - Koishi"], {}))
		self.assertTrue(goal_reached(["+1 Life", "[Marisa] Ending - Utsuho"], {}))

	def test_goal_koishi_both_characters(self):
		slot_data = {"goal": 1, "ending_required": 1}
		self.assertFalse(goal_reached(["[Reimu] Ending - Koishi", "[Marisa] Ending - Utsuho"], slot_data))
		self.assertTrue(goal_reached(iter(["[Reimu] Ending - Koishi", "[Marisa] Ending - Koishi"]), slot_data))


class TestSound(unittest.TestCase):
	def test_sound_requested_per_item(self):
		self.assertEqual(sound(["+1 Life"]), "extend")
		self.assertEqual(sound(["+0.05 Power"]), "power")
		self.assertEqual(sound(["Reimu A - Yukari"]), "ok")
		self.assertEqual(sound(["[Reimu] Extra Stage"]), "ok")
		self.assertEqual(sound(["Lower Difficulty", "+0.50 Power", "+1 Life"]), "extend")  # one per tick, most important
		self.assertIsNone(sound([]))
		self.assertIsNone(sound(["-1 Life"]))  # traps make their own noise

	def test_sound_patch_sites_guarded(self):
		"""The cave sites go through safe_patch: listed in EXPECTED_BYTES, so the guard and thcrap overlap tests cover them."""
		for name in ("ADDR_SOUND_HACK_1", "ADDR_SOUND_HACK_2"):
			self.assertIn(name, Variables.EXPECTED_BYTES)
