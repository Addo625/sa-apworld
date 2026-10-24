import struct
import unittest

from BaseClasses import CollectionState, ItemClassification

from .. import test as bases
from ..Rules import key_locks, stage_rooms
from ..Variables import CHARACTER_TO_ITEM, SPELL_CARD_COUNT, SPELL_CARD_SIZE, SPELL_CLEAR_OFFSET
from ..captures import capture_location, count_address, owner, spell_slot

ALL_SHOTS = CHARACTER_TO_ITEM["Reimu"] + CHARACTER_TO_ITEM["Marisa"]
STAGE3 = "[Reimu] Yuugi Defeated"
STAGE6 = "[Reimu] Utsuho Defeated"
EXTRA = "[Reimu] Koishi Defeated"


def capture_locations(test):
	return [loc for loc in test.multiworld.get_locations(test.player) if " - Capture " in loc.name]


def assert_pool_fills(test, captures, keys):
	"""38 core locations plus captures, all filled: pool + 2 locked endings."""
	pool = [item for item in test.multiworld.itempool if item.player == test.player]
	test.assertEqual(len(test.multiworld.get_locations(test.player)), 38 + captures)
	test.assertEqual(len(pool) + 2, 38 + captures)
	test.assertEqual(len(test.get_items_by_name("Spell Card Key")), keys)


class TestDefaultOn(unittest.TestCase):
	def test_spell_card_keys_default_on(self):
		from ..Options import KeyLockFinal, KeyLockSlack, SpellCardKeys, SpellCardKeysInPool
		self.assertTrue(SpellCardKeys.default)
		self.assertEqual((SpellCardKeysInPool.default, KeyLockFinal.default, KeyLockSlack.default), (12, 6, 2))


class TestOff(bases.TH11TestBase):
	def test_spell_card_keys_off(self):
		self.assertEqual(self.world.options.spell_card_keys.value, 0)
		self.assertEqual(capture_locations(self), [])
		self.assertEqual(self.get_items_by_name("Spell Card Key"), [])


class TestOffCreatesNone(bases.TH11TestBase):
	options = {"spell_card_keys": False, "captures_per_stage": 6, "capture_slots": "shared"}

	def test_off_creates_none(self):
		self.assertEqual(capture_locations(self), [])
		self.assertEqual(len(self.multiworld.get_locations(self.player)), 38)


class TestDefaults(bases.TH11TestBase):
	"""Captures on with the default locks (75): 12 keys, the final lock at 6 on Stage 6, slack 2."""
	options = {"spell_card_keys": True}

	def test_capture_count(self):
		self.assertEqual(len(capture_locations(self)), 24)
		region = self.multiworld.get_location("[Marisa] Stage 6 - Capture 2", self.player).parent_region
		self.assertEqual(region.name, "[Marisa] Stage 6")

	def test_item_count_matches_locations(self):
		assert_pool_fills(self, 24, 12)
		self.assertEqual(self.get_items_by_name("Spell Card Key")[0].classification, ItemClassification.progression)

	def test_rooms_count_captures_and_key_slack(self):
		# Stages hold 10, 10, 10, 12, 10 locations with 2 captures per character.
		self.assertEqual(stage_rooms(self.world), [-4, 5, 14, 23, 34, 43])
		self.assertEqual(stage_rooms(self.world, keys=20), [-6, 3, 12, 21, 32, 41])

	def test_final_lock_needs_lock_plus_slack_in_logic(self):
		"""The game opens Stage 6 at 6 keys; logic counts on it at 8, so 2 missed captures never strand a player."""
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		keys = self.get_items_by_name("Spell Card Key")
		self.assertTrue(self.can_reach_location("[Reimu] Orin Defeated"))  # Stage 5: no lock
		self.collect(keys[:7])
		self.assertFalse(self.can_reach_location(STAGE6))
		self.collect(keys[7])
		self.assertTrue(self.can_reach_location(STAGE6))


class TestTollStage3(bases.TH11TestBase):
	options = {"spell_card_keys": True, "key_lock_toll": 4, "key_lock_toll_stage": "stage_3", "key_lock_final": 12}

	def test_toll_and_clamped_final(self):
		slot = self.world.fill_slot_data()
		self.assertEqual((slot["key_lock_toll"], slot["key_lock_final"]), (4, 10))  # 12 keys, 2 kept as slack
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		keys = self.get_items_by_name("Spell Card Key")
		self.collect(keys[:5])
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect(keys[5])
		self.assertTrue(self.can_reach_location(STAGE3))
		self.assertFalse(self.can_reach_location(STAGE6))  # 10 + 2


class TestGoalLock(bases.TH11TestBase):
	options = {"spell_card_keys": True, "key_lock_final_target": "goal"}

	def test_goal_needs_keys_not_stage_6(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		self.assertTrue(self.can_reach_location(STAGE6))
		state = self.multiworld.state
		state.collect(self.multiworld.get_location("[Reimu] Stage 6 Clear", self.player).item, prevent_sweep=True)
		self.assertFalse(self.multiworld.has_beaten_game(state, self.player))
		self.collect(self.get_items_by_name("Spell Card Key")[:8])
		self.assertTrue(self.multiworld.has_beaten_game(self.multiworld.state, self.player))


class TestExtraLock(bases.TH11TestBase):
	options = {"spell_card_keys": True, "extra_stage": "apart", "key_lock_final_target": "extra", "key_lock_final": 10}

	def test_extra_needs_keys_stage_6_doesnt(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage", "Extra Stage"])
		self.assertTrue(self.can_reach_location(STAGE6))
		self.assertFalse(self.can_reach_location(EXTRA))
		self.collect_by_name("Spell Card Key")
		self.assertTrue(self.can_reach_location(EXTRA))


class TestNoLocks(bases.TH11TestBase):
	options = {"spell_card_keys": True, "key_lock_final": 0}

	def test_keys_are_filler(self):
		self.assertEqual(self.get_items_by_name("Spell Card Key")[0].classification, ItemClassification.filler)
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		self.assertTrue(self.can_reach_location(STAGE6))


class TestNormalModeIgnoresLocks(bases.TH11TestBase):
	options = {"spell_card_keys": True, "mode": "normal_static", "key_lock_toll": 3}

	def test_warns_and_keys_are_filler(self):
		with self.assertLogs(level="WARNING") as logs:
			self.world_setup()
		self.assertTrue(any("Practice mode only" in line for line in logs.output))
		self.assertEqual(self.get_items_by_name("Spell Card Key")[0].classification, ItemClassification.filler)


class TestPoolCapped(bases.TH11TestBase):
	# Shared, 1 per stage = 6 capture checks: the 12-key pool drops to 6, the final lock to 6 - 2 slack.
	options = {"spell_card_keys": True, "capture_slots": "shared", "captures_per_stage": 1, "spell_card_keys_local": True}

	def test_pool_and_lock_lowered(self):
		with self.assertLogs(level="WARNING") as logs:
			self.world_setup()
		self.assertTrue(any("spell_card_keys_in_pool lowered to 6" in line for line in logs.output))
		self.assertEqual(len(self.get_items_by_name("Spell Card Key")), 6)
		self.assertEqual(self.world.fill_slot_data()["key_lock_final"], 4)
		self.assertIn("Spell Card Key", self.world.options.local_items.value)


class TestStage1Cap(bases.TH11TestBase):
	options = {"spell_card_keys": True, "captures_per_stage": 6}

	def test_stage1_capped_at_2(self):
		names = {loc.name for loc in capture_locations(self)}
		self.assertIn("[Reimu] Stage 1 - Capture 2", names)
		self.assertNotIn("[Reimu] Stage 1 - Capture 3", names)
		self.assertEqual(len(names), 2 * (2 + 4 + 4 + 4 + 5 + 6))
		assert_pool_fills(self, 50, 12)


class TestShared(bases.TH11TestBase):
	options = {"spell_card_keys": True, "capture_slots": "shared"}

	def test_capture_count_shared(self):
		assert_pool_fills(self, 12, 12)
		self.assertEqual(self.multiworld.get_location("Stage 2 - Capture 1", self.player).parent_region.name, "Stage 2 Captures")

	def test_shared_slot_opens_from_either_character(self):
		start = self.multiworld.precollected_items[self.player][0]
		for character in CHARACTER_TO_ITEM:
			state = CollectionState(self.multiworld)
			state.remove(start)
			self.assertFalse(self.multiworld.get_location("Stage 1 - Capture 1", self.player).can_reach(state))
			state.collect(self.world.create_item(CHARACTER_TO_ITEM[character][0]), prevent_sweep=True)
			self.assertTrue(self.multiworld.get_location("Stage 1 - Capture 1", self.player).can_reach(state), character)


class TestCaptureDetection(unittest.TestCase):
	"""24: a card new to the owner sends its stage's next capture check, up to the stage's slots."""
	SLOT = {"spell_card_keys": 1, "captures_per_stage": 2}

	def test_capture_first_sends_slot1(self):
		self.assertEqual(capture_location("Reimu A", 1, False, self.SLOT, set()), "[Reimu] Stage 1 - Capture 1")
		self.assertEqual(capture_location("Reimu A", 1, False, self.SLOT, {"[Reimu] Stage 1 - Capture 1"}), "[Reimu] Stage 1 - Capture 2")

	def test_capture_fills_the_lowest_unchecked_after_a_collect(self):
		"""A collect checked Capture 2 out of order: the next spell sends Capture 1, not a checked Capture 2 again."""
		self.assertEqual(capture_location("Reimu A", 5, False, self.SLOT, {"[Reimu] Stage 5 - Capture 2"}), "[Reimu] Stage 5 - Capture 1")
		both = {"[Reimu] Stage 5 - Capture 1", "[Reimu] Stage 5 - Capture 2"}
		self.assertIsNone(capture_location("Reimu A", 5, False, self.SLOT, both))

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
