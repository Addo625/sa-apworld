from BaseClasses import CollectionState
from Fill import distribute_items_restrictive

from .. import test as bases
from ..Rules import stage_rooms
from ..Locations import location_table
from ..Variables import CHARACTER_TO_ITEM, STAGE4_APPEARANCES, STARTING_ID

ALL_SHOTS = CHARACTER_TO_ITEM["Reimu"] + CHARACTER_TO_ITEM["Marisa"]
STAGE3 = "[Reimu] Yuugi Defeated"
STAGE4 = "[Reimu] Satori Defeated"
STAGE5 = "[Reimu] Orin Defeated"
STAGE6 = "[Reimu] Utsuho Defeated"
# Stage k: locations in stages < k (6, 6, 6, 8, 6 per stage) - (k-1) Next Stage - other shot - GATE_SLACK.
DEFAULT_ROOMS = [-4, 1, 6, 11, 18, 23]


class TestGenerate(bases.TH11TestBase):
	def test_location_count(self):
		self.assertEqual(len(self.multiworld.get_locations(self.player)), 38)

	def test_item_count_matches_locations(self):
		pool = [item for item in self.multiworld.itempool if item.player == self.player]
		locked = [loc for loc in self.multiworld.get_locations(self.player) if loc.locked]
		self.assertEqual(len(pool) + len(locked), 38)
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

	def test_cat_orin_gated_like_satori(self):
		for check in STAGE4_APPEARANCES:
			location = self.multiworld.get_location(f"[Marisa] {check}", self.player)
			self.assertEqual(location.parent_region.name, "[Marisa] Stage 4")

	def test_cat_orin_ids_appended(self):
		appearances = [id for name, id in location_table.items() if " Appearance" in name]
		self.assertEqual(len(appearances), 2 * 8 * 5)  # base + 4 difficulties, 8 characters/shots
		self.assertEqual(sorted(appearances), sorted(location_table.values())[-len(appearances):])
		self.assertEqual(location_table["[Reimu] Satori Defeated"], STARTING_ID + 9)

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
		slot_data = self.multiworld.worlds[self.player].fill_slot_data()
		self.assertEqual(set(slot_data), {
			"exclude_lunatic",
			"number_life_mid", "power_mid", "difficulty_mid",
			"number_life_end", "power_end", "difficulty_end",
			"death_link",
			"spell_card_keys", "captures_per_stage", "capture_slots",
			"stage_requirements",
		})
		self.assertEqual(slot_data["stage_requirements"], [(0, 0, 0, 0)] * 6)

	def test_rooms(self):
		self.assertEqual(stage_rooms(self.world), DEFAULT_ROOMS)


class TestLifeGate(bases.TH11TestBase):
	options = {"number_life_mid": 8}

	def collect_lives(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		return self.get_items_by_name("+1 Life")

	def test_stage3_half_life_gate(self):
		lives = self.collect_lives()
		self.collect(lives[:3])
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect(lives[3])
		self.assertTrue(self.can_reach_location(STAGE3))

	def test_stage4_full_life_gate(self):
		lives = self.collect_lives()
		self.collect(lives[:7])
		self.assertFalse(self.can_reach_location(STAGE4))
		self.collect(lives[7])
		self.assertTrue(self.can_reach_location(STAGE4))


class TestPowerGate(bases.TH11TestBase):
	options = {"power_end": 8}

	def test_power_gate(self):
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		packs = self.get_items_by_name("+0.50 Power")
		self.assertTrue(self.can_reach_location(STAGE4))
		self.collect(packs[:3])
		self.assertFalse(self.can_reach_location(STAGE5))
		self.collect(packs[3])
		self.assertTrue(self.can_reach_location(STAGE5))
		self.collect(packs[4:7])
		self.assertFalse(self.can_reach_location(STAGE6))
		self.collect(packs[7])
		self.assertTrue(self.can_reach_location(STAGE6))


class TestDifficultyGateExcludeLunatic(bases.TH11TestBase):
	options = {"exclude_lunatic": True, "difficulty_mid": "easy"}

	def test_one_fewer_lower_difficulty(self):
		# Easy minus the missing Lunatic step = 2: stage 3 needs 1, stage 4 needs 2.
		self.collect_by_name(ALL_SHOTS + ["Next Stage"])
		lower = self.get_items_by_name("Lower Difficulty")
		self.assertEqual(len(lower), 2)
		self.assertFalse(self.can_reach_location(STAGE3))
		self.collect(lower[0])
		self.assertTrue(self.can_reach_location(STAGE3))
		self.assertFalse(self.can_reach_location(STAGE4))
		self.collect(lower[1])
		self.assertTrue(self.can_reach_location(STAGE4))


class TestExcludedRoom(bases.TH11TestBase):
	options = {"exclude_locations": ["[Reimu] Kisume - Midboss", "[Marisa] Yamame Defeated"]}

	def test_room_ignores_excluded(self):
		self.assertEqual(stage_rooms(self.world), DEFAULT_ROOMS[:1] + [room - 2 for room in DEFAULT_ROOMS[1:]])


MAX_GATES = {
	"number_life_mid": 8, "power_mid": 8, "difficulty_mid": "easy",
	"number_life_end": 8, "power_end": 8, "difficulty_end": "easy",
}
EXTREMES = {
	"max": MAX_GATES,
	"max exclude_lunatic": {**MAX_GATES, "exclude_lunatic": True},
	"max exclude stage 1-2": {**MAX_GATES, "exclude_locations": [
		"[Reimu] Kisume - Midboss", "[Reimu] Parsee Defeated", "[Marisa] Yamame Defeated", "[Marisa] Stage 2 Clear",
	]},
	"defaults": {},
	# The clamp trims keys too, and that must still fill.
	"keys max": {
		**MAX_GATES, "spell_card_keys": "alongside", "captures_per_stage": 6,
		"spell_card_keys_in_pool": 100, "spell_card_keys_required": 100,
	},
	"keys no captures": {"spell_card_keys": "alongside", "captures_per_stage": 0},
	"keys shared keys_only": {"spell_card_keys": "keys_only", "capture_slots": "shared"},
}


class TestMaxGates(bases.TH11TestBase):
	options = MAX_GATES

	def test_extremes_fill_fixed_seeds(self):
		for name, options in EXTREMES.items():
			self.options = options
			for seed in range(1, 51):
				with self.subTest(name, seed=seed):
					self.world_setup(seed)
					distribute_items_restrictive(self.multiworld)
					self.assertTrue(self.multiworld.can_beat_game())

	def test_clamp_warns(self):
		with self.assertLogs(level="WARNING") as logs:
			self.world_setup()
		self.assertTrue(any("Stage 3" in line for line in logs.output))
		# (4, 4, 1) needs 9 slots; stage 3 has room for 6.
		self.assertEqual(self.world.fill_slot_data()["stage_requirements"][2], (2, 3, 1, 0))
