import unittest

from .. import Variables, receive, test as bases
from ..Options import Mode
from ..detect import step
from ..patching import PatchMismatch, patch_immediate
from ..state import decode_state
from .test_detect import ids, play
from .test_state import BASE, S0, FakeMemory
from .test_extra import EXTRA
from .test_generate import ALL_SHOTS, STAGE6
from .test_granularity import PER_OWNER, item_count, location_count

STAGE_ITEMS = ["Next Stage", "[Reimu] Next Stage", "[Marisa] Next Stage"] + [f"Stage {level}" for level in range(2, 7)]


class TestNormalStatic(bases.TH11TestBase):
	options = {"mode": "normal_static", "stage_unlock": "by_character", "extra_stage": "linear"}

	def test_normal_no_next_stage_items(self):
		self.assertFalse(self.get_items_by_name(STAGE_ITEMS + ["Extra Stage", "[Reimu] Extra Stage"]))
		self.collect_by_name(ALL_SHOTS)
		self.assertTrue(self.can_reach_location(STAGE6))
		self.assertTrue(self.can_reach_location(EXTRA))

	def test_filler_covers_missing_stage_items(self):
		self.assertEqual(item_count(self), location_count(self))
		self.assertEqual(location_count(self), 2 * (PER_OWNER + 3))


class TestNormalApartExtra(bases.TH11TestBase):
	options = {"mode": "normal_dynamic", "extra_stage": "apart"}

	def test_apart_extra_keeps_its_item(self):
		self.assertEqual(len(self.get_items_by_name("Extra Stage")), 1)
		self.assertFalse(self.get_items_by_name("Next Stage"))
		self.collect_by_name(ALL_SHOTS)
		self.assertFalse(self.can_reach_location(EXTRA))
		self.collect_by_name("Extra Stage")
		self.assertTrue(self.can_reach_location(EXTRA))


class TestNormalDynamicNoEasy(bases.TH11TestBase):
	options = {"mode": "normal_dynamic", "difficulty_end": "easy"}

	def test_easy_gate_lowered_to_normal(self):
		self.assertEqual(self.world.fill_slot_data()["stage_requirements"][5][2], 2)


class TestNormalDynamicDifficultyCheck(bases.TH11TestBase):
	options = {"mode": "normal_dynamic", "difficulty_check": True, "difficulty_end": "easy"}

	def test_difficulty_check_makes_it_static(self):
		slot_data = self.world.fill_slot_data()
		self.assertEqual(slot_data["mode"], 2)
		self.assertEqual(slot_data["stage_requirements"][5][2], 3)


class TestNormalClient(unittest.TestCase):
	def test_dynamic_difficulty_lowest_unlocked(self):
		dynamic = {"mode": Mode.option_normal_dynamic}
		self.assertEqual(receive.difficulty_for(0, dynamic), 3)  # no Lower Difficulty: Lunatic
		self.assertEqual(receive.difficulty_for(2, dynamic), 1)  # Normal
		self.assertEqual(receive.difficulty_for(3, dynamic), 1)  # Easy unlocked, but dynamic never forces Easy (EoSD)
		self.assertEqual(receive.difficulty_for(1, {**dynamic, "exclude_lunatic": True}), 1)
		self.assertIsNone(receive.difficulty_for(2, {"mode": Mode.option_normal_static}))
		in_stage = play(1, ADDR_DIFFICULTY=3)
		self.assertEqual(receive.difficulty_writes(in_stage, 2, dynamic), [(Variables.ADDR_DIFFICULTY, 1)])
		self.assertEqual(receive.difficulty_writes(play(1, ADDR_DIFFICULTY=1), 2, dynamic), [])
		self.assertEqual(receive.difficulty_writes(decode_state(S0), 2, dynamic), [])  # not in a run

	def test_continue_lives_patch_uses_guard(self):
		memory = FakeMemory()
		site, prefix = BASE + 0x17955, b"\xc7\x40\x5c"
		memory.set(site - len(prefix), prefix + b"\x02")
		patch_immediate(memory, site, prefix, 5)
		self.assertEqual(memory.writes, [(site - len(prefix), prefix + b"\x05")])
		memory.writes.clear()
		with self.assertRaises(PatchMismatch):
			patch_immediate(memory, site, b"\x90\x90\x90", 6)
		self.assertEqual(memory.writes, [])
		self.assertEqual(receive.continue_lives(["+1 Life"] * 3 + ["Next Stage"]), 3)
		self.assertEqual(receive.continue_lives(["+1 Life"] * 12), 8)
		self.assertEqual(receive.continue_lives(["+1 Life"] * 5, limit_lives=2), 2)

	def test_normal_run_stage_transitions(self):
		states = [decode_state(S0), play(1), play(1, True), play(1), play(1, True), play(1), play(2), play(2, True), play(2)]
		sent, runs = [], 0
		for prev, state in zip(states, states[1:]):
			locations, runs = step(prev, state, runs)
			sent += locations
		self.assertEqual(sent, ids("[Reimu] Kisume - Midboss", "[Reimu] Yamame Defeated", "[Reimu] Stage 1 Clear", "[Reimu] Parsee - Midboss"))
