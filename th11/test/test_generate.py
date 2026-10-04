from BaseClasses import CollectionState

from .. import test as bases
from ..Variables import CHARACTER_TO_ITEM

ALL_SHOTS = CHARACTER_TO_ITEM["Reimu"] + CHARACTER_TO_ITEM["Marisa"]
STAGE3 = "[Reimu] Yuugi Defeated"


class TestGenerate(bases.TH11TestBase):
	def test_location_count(self):
		self.assertEqual(len(self.multiworld.get_locations(self.player)), 34)

	def test_item_count_matches_locations(self):
		pool = [item for item in self.multiworld.itempool if item.player == self.player]
		locked = [loc for loc in self.multiworld.get_locations(self.player) if loc.locked]
		self.assertEqual(len(pool) + len(locked), 34)
		self.assertEqual(len(locked), 2)
		self.assertEqual(len(self.get_items_by_name(ALL_SHOTS)), 5)
		self.assertEqual(len(self.multiworld.precollected_items[self.player]), 1)
		self.assertEqual(len(self.get_items_by_name("Next Stage")), 5)
		self.assertEqual(len(self.get_items_by_name("+1 Life")), 8)
		self.assertEqual(len(self.get_items_by_name("+0.50 Power")), 8)
		self.assertEqual(len(self.get_items_by_name("Lower Difficulty")), 3)

	def test_stage3_blocked_without_next_stage(self):
		self.collect_by_name(ALL_SHOTS)
		self.collect_by_name("Next Stage")
		self.assertTrue(self.can_reach_location(STAGE3))
		self.remove(self.get_items_by_name("Next Stage")[:4])
		self.assertFalse(self.can_reach_location(STAGE3))
		self.assertTrue(self.can_reach_location("[Reimu] Parsee Defeated"))

	def test_stage_needs_character_shot(self):
		start = self.multiworld.precollected_items[self.player][0].name
		own, other = ("Reimu", "Marisa") if start in CHARACTER_TO_ITEM["Reimu"] else ("Marisa", "Reimu")
		self.assertTrue(self.can_reach_location(f"[{own}] Yamame Defeated"))
		self.assertFalse(self.can_reach_location(f"[{other}] Yamame Defeated"))
		self.collect_by_name(CHARACTER_TO_ITEM[other][2])
		self.assertTrue(self.can_reach_location(f"[{other}] Yamame Defeated"))

	def test_goal_requires_ending(self):
		# prevent_sweep: a sweep would pick up the locked ending as soon as Stage 6 is reachable.
		state = CollectionState(self.multiworld)
		for item in self.multiworld.itempool:
			state.collect(item, prevent_sweep=True)
		self.assertFalse(self.multiworld.has_beaten_game(state, self.player))
		state.collect(self.multiworld.get_location("[Marisa] Stage 6 Clear", self.player).item, prevent_sweep=True)
		self.assertTrue(self.multiworld.has_beaten_game(state, self.player))

	def test_slot_data_keys(self):
		self.assertEqual(set(self.multiworld.worlds[self.player].fill_slot_data()), {
			"exclude_lunatic",
			"number_life_mid", "power_mid", "difficulty_mid",
			"number_life_end", "power_end", "difficulty_end",
			"death_link",
		})


class TestLifeGate(bases.TH11TestBase):
	options = {"number_life_mid": 8}

	def test_stage3_blocked_by_life_gate(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		lives = self.get_items_by_name("+1 Life")
		self.collect(lives[:7])
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect(lives[7])
		self.assertTrue(self.can_reach_location(STAGE3))


class TestPowerGate(bases.TH11TestBase):
	options = {"power_end": 8}

	def test_power_gate(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		packs = self.get_items_by_name("+0.50 Power")
		self.assertTrue(self.can_reach_location(STAGE3))
		self.collect(packs[:7])
		self.assertFalse(self.can_reach_location("[Reimu] Utsuho Defeated"))
		self.collect(packs[7])
		self.assertTrue(self.can_reach_location("[Reimu] Utsuho Defeated"))


class TestDifficultyGateExcludeLunatic(bases.TH11TestBase):
	options = {"exclude_lunatic": True, "difficulty_mid": "easy"}

	def test_one_fewer_lower_difficulty(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		self.assertEqual(len(self.get_items_by_name("Lower Difficulty")), 2)
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect_by_name("Lower Difficulty")
		self.assertTrue(self.can_reach_location(STAGE3))
