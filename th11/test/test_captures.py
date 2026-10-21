import struct
import unittest

from BaseClasses import CollectionState, ItemClassification

from .. import test as bases
from ..Rules import stage_rooms
from ..Variables import CHARACTER_TO_ITEM, SPELL_CARD_COUNT, SPELL_CARD_SIZE, SPELL_CLEAR_OFFSET
from ..captures import capture_location, count_address, owner, spell_slot

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


class TestDefaultAlongside(unittest.TestCase):
	def test_spell_card_keys_default_alongside(self):
		from ..Options import SpellCardKeys
		self.assertEqual(SpellCardKeys.default, SpellCardKeys.option_alongside)


class TestOff(bases.TH11TestBase):
	def test_spell_card_keys_off(self):
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


class TestCaptureDetection(unittest.TestCase):
	"""24: a card new to the owner sends its stage's next capture check, up to the stage's slots."""
	SLOT = {"spell_card_keys": 1, "captures_per_stage": 2}

	def test_capture_first_sends_slot1(self):
		self.assertEqual(capture_location("Reimu A", 1, False, self.SLOT, set()), "[Reimu] Stage 1 - Capture 1")
		self.assertEqual(capture_location("Reimu A", 1, False, self.SLOT, {"[Reimu] Stage 1 - Capture 1"}), "[Reimu] Stage 1 - Capture 2")

	def test_capture_same_card_twice_sends_nothing(self):
		self.assertIsNone(capture_location("Reimu A", 1, True, self.SLOT, set()))

	def test_capture_beyond_slot_count_sends_nothing(self):
		sent = {"[Reimu] Stage 1 - Capture 1", "[Reimu] Stage 1 - Capture 2"}
		self.assertIsNone(capture_location("Reimu A", 1, False, self.SLOT, sent))
		self.assertIsNone(capture_location("Reimu A", 7, False, self.SLOT, set()))  # Extra has no capture checks
		self.assertIsNone(capture_location("Reimu A", 1, False, {"spell_card_keys": 0, "captures_per_stage": 2}, set()))

	def test_capture_owners(self):
		self.assertEqual(capture_location("Marisa C", 2, False, {**self.SLOT, "capture_slots": 1}, set()), "Stage 2 - Capture 1")
		self.assertEqual(capture_location("Marisa C", 2, False, {**self.SLOT, "shot_type": 1}, set()), "[Marisa C] Stage 2 - Capture 1")
		self.assertEqual(owner("Marisa C", self.SLOT), "Marisa")  # per_character: Marisa's 3 shots share one set
		self.assertEqual(owner("Marisa C", {"capture_slots": 1}), "")
		self.assertEqual(owner("Marisa C", {"shot_type": 1}), "Marisa C")

	def test_spell_slots_ignore_difficulty(self):
		"""63: Kisume's Hard and Lunatic cards are one spell; each 4 IDs from 2 are one attack on E/N/H/L."""
		self.assertEqual({spell_slot(card) for card in (0, 1)}, {0})
		self.assertEqual({spell_slot(card) for card in range(2, 6)}, {1})
		self.assertEqual(spell_slot(6), 2)
		self.assertEqual(spell_slot(161), 40)
		self.assertEqual(spell_slot(162), 41)

	def test_count_address(self):
		"""Each shot's records are a save chunk apart; a card's capture count is at + id * 0x90 + 0x80 (0x40CE4C)."""
		self.assertEqual(count_address(0x1000, "Reimu A", 0), 0x1000 + SPELL_CLEAR_OFFSET)
		self.assertEqual(count_address(0x1000, "Reimu B", 2), 0x1000 + 0x68D4 + 2 * SPELL_CARD_SIZE + SPELL_CLEAR_OFFSET)

	def test_capture_cards_are_in_the_save(self):
		"""The decoded save layout the live entry relies on: Marisa C's records, IDs in order, with a Kisume attempt."""
		from pathlib import Path
		path = Path(__file__).resolve().parents[2] / ".games/sa/scoreth11.dat"
		if not path.exists():
			self.skipTest("no save (.games is gitignored)")
		from .. import scoredat
		chunk = [body for signature, _, _, body in scoredat.chunks(scoredat.decode(path.read_bytes())) if signature == "CR"][5]
		records = chunk[scoredat.PRACTICE_OFFSET + 4 * 6 * scoredat.PRACTICE_SIZE:]
		self.assertEqual(len(records), SPELL_CARD_COUNT * SPELL_CARD_SIZE)
		self.assertEqual([struct.unpack_from("<i", records, card * SPELL_CARD_SIZE + 0x88)[0] for card in range(3)], [0, 1, 2])
