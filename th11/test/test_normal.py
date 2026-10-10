from .. import test as bases
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
