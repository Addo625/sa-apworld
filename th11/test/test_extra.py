import unittest

from BaseClasses import CollectionState

from .. import test as bases
from ..Rules import goal_met
from .test_generate import ALL_SHOTS
from .test_granularity import PER_OWNER, item_count, location_count

EXTRA = "[Reimu] Koishi Defeated"
EXTRA_PER_OWNER = 3  # Sanae, Koishi, the clear


def locked(test):
	return {loc.name: loc.item.name for loc in test.multiworld.get_locations(test.player) if loc.locked}


def beaten_with(test, locations):
	"""Whether the whole pool plus the locked items at `locations` beats the game (no sweep of locked items)."""
	state = CollectionState(test.multiworld)
	for item in test.multiworld.itempool:
		state.collect(item, prevent_sweep=True)
	for name in locations:
		state.collect(test.multiworld.get_location(name, test.player).item, prevent_sweep=True)
	return test.multiworld.has_beaten_game(state, test.player)


class TestExtraExcluded(bases.TH11TestBase):
	options = {"goal": "koishi", "ending_required": "all_shot_types"}

	def test_no_extra_locations(self):
		self.assertEqual(location_count(self), 2 * PER_OWNER)
		self.assertFalse(self.get_items_by_name("Extra Stage"))

	def test_goal_falls_back_to_utsuho(self):
		slot_data = self.world.fill_slot_data()
		self.assertEqual(slot_data["goal"], 0)
		self.assertEqual(len(slot_data["stage_requirements"]), 6)


class TestGoalKoishiOnce(bases.TH11TestBase):
	options = {"extra_stage": "apart", "goal": "koishi"}

	def test_goal_koishi_once(self):
		self.assertEqual(locked(self), {
			"[Reimu] Stage Extra Clear": "[Reimu] Ending - Koishi", "[Marisa] Stage Extra Clear": "[Marisa] Ending - Koishi",
		})
		self.assertFalse(beaten_with(self, []))
		self.assertTrue(beaten_with(self, ["[Marisa] Stage Extra Clear"]))

	def test_counts(self):
		self.assertEqual(location_count(self), 2 * (PER_OWNER + EXTRA_PER_OWNER))
		self.assertEqual(item_count(self), location_count(self))
		self.assertEqual(len(self.get_items_by_name("Extra Stage")), 1)
		self.assertEqual(len(self.get_items_by_name("Next Stage")), 5)

	def test_apart_needs_extra_stage_after_stage_6(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		self.assertFalse(self.can_reach_location(EXTRA))
		self.collect_by_name("Extra Stage")
		self.assertTrue(self.can_reach_location(EXTRA))
		self.assertTrue(self.can_reach_location("[Reimu] Sanae - Midboss"))
		self.remove(self.get_items_by_name("Next Stage")[:1])
		self.assertFalse(self.can_reach_location(EXTRA))


class TestGoalBothAllCharacters(bases.TH11TestBase):
	options = {"extra_stage": "linear", "goal": "both", "ending_required": "both_characters"}

	def test_goal_both_all_characters(self):
		self.assertEqual(len(locked(self)), 4)
		self.assertFalse(beaten_with(self, ["[Reimu] Stage 6 Clear", "[Marisa] Stage 6 Clear", "[Reimu] Stage Extra Clear"]))
		self.assertFalse(beaten_with(self, ["[Reimu] Stage Extra Clear", "[Marisa] Stage Extra Clear", "[Reimu] Stage 6 Clear"]))
		self.assertTrue(beaten_with(self, [f"[{c}] Stage {s} Clear" for c in ("Reimu", "Marisa") for s in (6, "Extra")]))

	def test_linear_needs_sixth_next_stage(self):
		stages = self.get_items_by_name("Next Stage")
		self.assertEqual(len(stages), 6)
		self.collect_by_name(ALL_SHOTS)
		self.collect(stages[:5])
		self.assertTrue(self.can_reach_location("[Reimu] Utsuho Defeated"))
		self.assertFalse(self.can_reach_location(EXTRA))
		self.collect(stages[5])
		self.assertTrue(self.can_reach_location(EXTRA))


class TestAllShotTypesFallsBack(bases.TH11TestBase):
	options = {"extra_stage": "apart", "goal": "both", "ending_required": "all_shot_types"}

	def test_all_shot_types_falls_back(self):
		self.assertEqual(self.world.fill_slot_data()["ending_required"], 1)


class TestAllShotTypes(bases.TH11TestBase):
	options = {"extra_stage": "apart", "goal": "koishi", "ending_required": "all_shot_types", "shot_type": True,
		"stage_unlock": "by_shot_type"}

	def test_needs_every_shot(self):
		self.assertEqual(self.world.fill_slot_data()["ending_required"], 2)
		self.assertEqual(len(self.get_items_by_name("[Reimu A] Extra Stage")), 1)
		clears = [f"[{shot}] Stage Extra Clear" for shot in ("Reimu A", "Reimu B", "Reimu C", "Marisa A", "Marisa B", "Marisa C")]
		self.assertFalse(beaten_with(self, clears[:5]))
		self.assertTrue(beaten_with(self, clears))


class TestLinearNotProgressive(bases.TH11TestBase):
	options = {"extra_stage": "linear", "progressive_stage": False, "stage_unlock": "by_character"}

	def test_extra_stage_after_stage_6(self):
		self.collect_by_name(ALL_SHOTS + ["[Reimu] Extra Stage"])
		self.assertFalse(self.can_reach_location(EXTRA))
		self.collect_by_name([f"[Reimu] Stage {level}" for level in range(2, 7)])
		self.assertTrue(self.can_reach_location(EXTRA))
		self.assertFalse(self.can_reach_location("[Marisa] Koishi Defeated"))


class TestExtraLifeGate(bases.TH11TestBase):
	options = {"extra_stage": "apart", "number_life_extra": 8}

	def test_extra_life_gate(self):
		self.assertEqual(self.world.fill_slot_data()["stage_requirements"][6], (8, 0, 0, 0))
		self.collect_by_name(ALL_SHOTS + ["Next Stage", "Extra Stage"])
		lives = self.get_items_by_name("+1 Life")
		self.collect(lives[:7])
		self.assertFalse(self.can_reach_location(EXTRA))
		self.collect(lives[7])
		self.assertTrue(self.can_reach_location(EXTRA))


class TestGoalMet(unittest.TestCase):
	def test_goal_met(self):
		def met(items, goal, required):
			return goal_met(items.count, goal, required)
		self.assertTrue(met(["[Reimu] Ending - Utsuho"], 0, 0))
		self.assertFalse(met(["[Reimu] Ending - Koishi"], 0, 0))
		self.assertFalse(met(["[Reimu] Ending - Utsuho"], 2, 0))
		self.assertTrue(met(["[Reimu] Ending - Utsuho", "[Marisa] Ending - Koishi"], 2, 0))
		self.assertFalse(met(["[Reimu] Ending - Koishi"] * 3, 1, 1))
		self.assertFalse(met(["[Reimu] Ending - Koishi"] * 3 + ["[Marisa] Ending - Koishi"] * 2, 1, 2))
		self.assertTrue(met(["[Reimu] Ending - Koishi"] * 3 + ["[Marisa] Ending - Koishi"] * 3, 1, 2))
