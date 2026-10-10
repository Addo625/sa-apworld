from .. import test as bases
from ..Rules import stage_rooms
from .test_generate import ALL_SHOTS, DEFAULT_ROOMS

# Per owner: 3 checks per stage, 4 in stage 4 (two cat Orins), counting the clears.
PER_OWNER = 19
# Difficulty checks per owner and difficulty: midbosses and bosses, without the clears.
PER_DIFFICULTY = 13


def location_count(test):
	return len(test.multiworld.get_locations(test.player))


def item_count(test):
	pool = [item for item in test.multiworld.itempool if item.player == test.player]
	locked = [loc for loc in test.multiworld.get_locations(test.player) if loc.locked]
	return len(pool) + len(locked)


class TestShotType(bases.TH11TestBase):
	options = {"shot_type": True}

	def test_count_shot_type(self):
		self.assertEqual(location_count(self), 6 * PER_OWNER)
		self.assertEqual(item_count(self), 6 * PER_OWNER)
		self.assertEqual(len([loc for loc in self.multiworld.get_locations(self.player) if loc.locked]), 6)

	def test_shot_needs_its_item(self):
		self.collect_by_name(["Next Stage"])
		owned = self.multiworld.precollected_items[self.player][0].name.split(" - ")[0]
		other = "Marisa C" if owned != "Marisa C" else "Reimu A"
		self.assertTrue(self.can_reach_location(f"[{owned}] Yuugi Defeated"))
		self.assertFalse(self.can_reach_location(f"[{other}] Yuugi Defeated"))


class TestDifficulty(bases.TH11TestBase):
	options = {"difficulty_check": True}

	def test_count_difficulty(self):
		self.assertEqual(location_count(self), 2 * 6 + 4 * 2 * PER_DIFFICULTY)
		self.assertEqual(item_count(self), location_count(self))

	def test_plain_stage_keeps_only_clear(self):
		names = {loc.name for loc in self.multiworld.get_region("[Reimu] Stage 1", self.player).locations}
		self.assertEqual(names, {"[Reimu] Stage 1 Clear"})

	def test_difficulty_needs_lower_difficulty(self):
		self.collect_by_name(ALL_SHOTS)
		lower = self.get_items_by_name("Lower Difficulty")
		self.assertTrue(self.can_reach_location("[Lunatic][Reimu] Yamame Defeated"))
		self.assertFalse(self.can_reach_location("[Hard][Reimu] Yamame Defeated"))
		self.collect(lower[0])
		self.assertTrue(self.can_reach_location("[Hard][Reimu] Yamame Defeated"))
		self.assertFalse(self.can_reach_location("[Easy][Reimu] Yamame Defeated"))
		self.collect(lower[1:])
		self.assertTrue(self.can_reach_location("[Easy][Reimu] Yamame Defeated"))

	def test_room_skips_difficulty_locations(self):
		# Each stage keeps 2 clears + the Lunatic checks (the only ungated ones): the defaults' counts.
		self.assertEqual(stage_rooms(self.world), DEFAULT_ROOMS)


class TestDifficultyExcludeLunatic(bases.TH11TestBase):
	options = {"difficulty_check": True, "exclude_lunatic": True}

	def test_count_difficulty_no_lunatic(self):
		self.assertEqual(location_count(self), 2 * 6 + 3 * 2 * PER_DIFFICULTY)
		self.assertNotIn("[Lunatic][Reimu] Yamame Defeated", {loc.name for loc in self.multiworld.get_locations(self.player)})

	def test_hard_is_free_easy_needs_two(self):
		self.collect_by_name(ALL_SHOTS)
		lower = self.get_items_by_name("Lower Difficulty")
		self.assertTrue(self.can_reach_location("[Hard][Marisa] Yamame Defeated"))
		self.collect(lower[0])
		self.assertFalse(self.can_reach_location("[Easy][Marisa] Yamame Defeated"))
		self.collect(lower[1])
		self.assertTrue(self.can_reach_location("[Easy][Marisa] Yamame Defeated"))


class TestBoth(bases.TH11TestBase):
	options = {"shot_type": True, "difficulty_check": True, "stage_unlock": "by_shot_type"}

	def test_count_both(self):
		self.assertEqual(location_count(self), 6 * 6 + 4 * 6 * PER_DIFFICULTY)
		self.assertEqual(item_count(self), location_count(self))
		self.assertEqual(len(self.get_items_by_name("[Reimu A] Next Stage")), 5)

	def test_by_shot_type_rule(self):
		self.collect_by_name(ALL_SHOTS)
		self.collect(self.get_items_by_name("[Reimu A] Next Stage")[:2])
		self.assertTrue(self.can_reach_location("[Lunatic][Reimu A] Yuugi Defeated"))
		self.assertFalse(self.can_reach_location("[Lunatic][Reimu B] Yuugi Defeated"))
		self.assertFalse(self.can_reach_location("[Lunatic][Reimu A] Satori Defeated"))


class TestByCharacter(bases.TH11TestBase):
	options = {"stage_unlock": "by_character"}

	def test_by_character_rule(self):
		self.collect_by_name(ALL_SHOTS)
		self.assertEqual(self.get_items_by_name("Next Stage"), [])
		self.collect(self.get_items_by_name("[Reimu] Next Stage")[:2])
		self.assertTrue(self.can_reach_location("[Reimu] Yuugi Defeated"))
		self.assertFalse(self.can_reach_location("[Reimu] Satori Defeated"))
		self.assertFalse(self.can_reach_location("[Marisa] Parsee Defeated"))

	def test_by_character_needs_character_shot(self):
		start = self.multiworld.precollected_items[self.player][0].name
		other = "Marisa" if start.startswith("Reimu") else "Reimu"
		self.collect_by_name(f"[{other}] Next Stage")
		self.assertFalse(self.can_reach_location(f"[{other}] Parsee Defeated"))

	def test_room_by_character(self):
		# Locations before stage k (0, 6, 12, 18, 26, 32) - (k-1) per character - other shot - GATE_SLACK.
		self.assertEqual(stage_rooms(self.world), [-4, 0, 4, 8, 14, 18])


class TestByShotTypeFallback(bases.TH11TestBase):
	options = {"stage_unlock": "by_shot_type"}

	def test_falls_back_to_by_character(self):
		self.assertEqual(self.world.fill_slot_data()["stage_unlock"], 1)
		self.assertEqual(len(self.get_items_by_name("[Reimu] Next Stage")), 5)
		self.assertEqual(self.get_items_by_name("[Reimu A] Next Stage"), [])


class TestByShotTypeCharacterChecks(bases.TH11TestBase):
	options = {"stage_unlock": "by_shot_type", "difficulty_check": True}

	def test_any_shot_of_the_character_opens(self):
		self.collect_by_name(ALL_SHOTS)
		self.collect(self.get_items_by_name("[Reimu B] Next Stage")[:2])
		self.assertTrue(self.can_reach_location("[Lunatic][Reimu] Yuugi Defeated"))
		self.assertFalse(self.can_reach_location("[Lunatic][Marisa] Parsee Defeated"))


class TestNotProgressive(bases.TH11TestBase):
	options = {"progressive_stage": False}

	def test_stage_items(self):
		self.assertEqual(self.get_items_by_name("Next Stage"), [])
		self.assertEqual(len(self.get_items_by_name(["Stage 2", "Stage 3", "Stage 4", "Stage 5", "Stage 6"])), 5)

	def test_stage_needs_its_item_and_earlier_ones(self):
		self.collect_by_name(ALL_SHOTS + ["Stage 3"])
		self.assertTrue(self.can_reach_location("[Reimu] Kisume - Midboss"))
		self.assertFalse(self.can_reach_location("[Reimu] Yuugi Defeated"))
		self.collect_by_name("Stage 2")
		self.assertTrue(self.can_reach_location("[Reimu] Yuugi Defeated"))
		self.assertFalse(self.can_reach_location("[Reimu] Satori Defeated"))


class TestNotProgressiveByCharacter(bases.TH11TestBase):
	options = {"progressive_stage": False, "stage_unlock": "by_character"}

	def test_character_stage_item(self):
		self.collect_by_name(ALL_SHOTS + [f"[Marisa] Stage {level}" for level in range(2, 6)])
		self.assertTrue(self.can_reach_location("[Marisa] Orin Defeated"))
		self.assertFalse(self.can_reach_location("[Reimu] Orin Defeated"))
