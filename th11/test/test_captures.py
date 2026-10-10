from BaseClasses import CollectionState, ItemClassification

from .. import test as bases
from ..Rules import stage_rooms
from ..Variables import CHARACTER_TO_ITEM

ALL_SHOTS = CHARACTER_TO_ITEM["Reimu"] + CHARACTER_TO_ITEM["Marisa"]
STAGE3 = "[Reimu] Yuugi Defeated"
STAGE4 = "[Reimu] Satori Defeated"


def capture_locations(test):
	return [loc for loc in test.multiworld.get_locations(test.player) if " - Capture " in loc.name]


def assert_pool_fills(test, captures, keys):
	"""38 core locations plus captures, all filled: pool + 2 locked endings."""
	pool = [item for item in test.multiworld.itempool if item.player == test.player]
	test.assertEqual(len(test.multiworld.get_locations(test.player)), 38 + captures)
	test.assertEqual(len(pool) + 2, 38 + captures)
	test.assertEqual(len(test.get_items_by_name("Spell Card Key")), keys)


class TestDefaultOff(bases.TH11TestBase):
	def test_spell_card_keys_default_off(self):
		self.assertEqual(self.world.options.spell_card_keys.value, 0)
		self.assertEqual(capture_locations(self), [])
		self.assertEqual(self.get_items_by_name("Spell Card Key"), [])


class TestOffCreatesNone(bases.TH11TestBase):
	options = {"spell_card_keys": "off", "captures_per_stage": 6, "capture_slots": "shared"}

	def test_off_creates_none(self):
		self.assertEqual(capture_locations(self), [])
		self.assertEqual(len(self.multiworld.get_locations(self.player)), 38)


class TestAlongside(bases.TH11TestBase):
	options = {"spell_card_keys": "alongside"}

	def test_capture_count_default_alongside(self):
		self.assertEqual(len(capture_locations(self)), 24)
		region = self.multiworld.get_location("[Marisa] Stage 6 - Capture 2", self.player).parent_region
		self.assertEqual(region.name, "[Marisa] Stage 6")

	def test_item_count_matches_locations(self):
		assert_pool_fills(self, 24, 12)

	def test_rooms_count_captures_and_key_slack(self):
		# Stages hold 10, 10, 10, 12, 10 locations with 2 captures per character.
		self.assertEqual(stage_rooms(self.world), [-4, 5, 14, 23, 34, 43])
		self.assertEqual(stage_rooms(self.world, keys_required=20), [-6, 3, 12, 21, 32, 41])

	def test_key_gate_stage3(self):
		# 12 keys at 75 % -> 9 required by stage 6, floor(9/4) = 2 at stage 3.
		self.assertEqual([req[3] for req in self.world.stage_requirements], [0, 0, 2, 4, 6, 9])
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		keys = self.get_items_by_name("Spell Card Key")
		self.collect(keys[0])
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect(keys[1])
		self.assertTrue(self.can_reach_location(STAGE3))
		self.assertFalse(self.can_reach_location(STAGE4))


class TestStage1Cap(bases.TH11TestBase):
	options = {"spell_card_keys": "alongside", "captures_per_stage": 6}

	def test_stage1_capped_at_2(self):
		names = {loc.name for loc in capture_locations(self)}
		self.assertIn("[Reimu] Stage 1 - Capture 2", names)
		self.assertNotIn("[Reimu] Stage 1 - Capture 3", names)
		self.assertEqual(len(names), 2 * (2 + 4 + 4 + 4 + 5 + 6))
		assert_pool_fills(self, 50, 25)


class TestKeyCountRounding(bases.TH11TestBase):
	# Shared, 1 per stage = 6 slots; 25 % = 1.5 keys rounds up to 2.
	options = {"spell_card_keys": "alongside", "capture_slots": "shared", "captures_per_stage": 1, "spell_card_keys_in_pool": 25}

	def test_key_count_rounding(self):
		self.assertEqual(len(capture_locations(self)), 6)
		self.assertEqual(len(self.get_items_by_name("Spell Card Key")), 2)
		# Required: floor(75 % of 2) = 1, reached only at stage 6.
		self.assertEqual([req[3] for req in self.world.stage_requirements], [0, 0, 0, 0, 0, 1])


class TestShared(bases.TH11TestBase):
	options = {"spell_card_keys": "alongside", "capture_slots": "shared"}

	def test_capture_count_shared(self):
		assert_pool_fills(self, 12, 6)
		self.assertEqual(self.multiworld.get_location("Stage 2 - Capture 1", self.player).parent_region.name, "Stage 2 Captures")

	def test_shared_slot_opens_from_either_character(self):
		start = self.multiworld.precollected_items[self.player][0]
		for character in CHARACTER_TO_ITEM:
			state = CollectionState(self.multiworld)
			state.remove(start)
			self.assertFalse(self.multiworld.get_location("Stage 1 - Capture 1", self.player).can_reach(state))
			state.collect(self.world.create_item(CHARACTER_TO_ITEM[character][0]), prevent_sweep=True)
			self.assertTrue(self.multiworld.get_location("Stage 1 - Capture 1", self.player).can_reach(state), character)


class TestKeysOnly(bases.TH11TestBase):
	options = {"spell_card_keys": "keys_only", "number_life_mid": 8, "power_end": 8}

	def test_keys_only_ignores_lives(self):
		assert_pool_fills(self, 24, 12)
		self.assertEqual(self.get_items_by_name("+1 Life")[0].classification, ItemClassification.useful)
		self.assertEqual([req[:3] for req in self.world.stage_requirements], [(0, 0, 0)] * 6)
		self.collect_by_name(ALL_SHOTS + ["Next Stage", "Spell Card Key"])
		self.assertTrue(self.can_reach_location("[Reimu] Utsuho Defeated"))


class TestKeysOnlyZeroKeys(bases.TH11TestBase):
	options = {"spell_card_keys": "keys_only", "spell_card_keys_in_pool": 0, "number_life_mid": 8}

	def test_keys_only_zero_keys_falls_back(self):
		with self.assertLogs(level="WARNING") as logs:
			self.world_setup()
		self.assertTrue(any("keys_only" in line for line in logs.output))
		self.assertEqual(self.world.fill_slot_data()["spell_card_keys"], 1)
		self.assertEqual(self.get_items_by_name("+1 Life")[0].classification, ItemClassification.progression)
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect_by_name("+1 Life")
		self.assertTrue(self.can_reach_location(STAGE3))
