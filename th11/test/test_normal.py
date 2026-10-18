import unittest
from pathlib import Path

from .. import Variables, receive, test as bases
from ..Options import Mode
from ..detect import step
from ..patching import PatchMismatch, patch_value
from ..state import decode_state
from .test_detect import ids, play
from .test_state import BASE, S0, FakeMemory
from .test_extra import EXTRA
from .test_generate import ALL_SHOTS, STAGE6
from .test_granularity import PER_OWNER, item_count, location_count

GAME = Path(__file__).resolve().parents[2] / ".games/sa/th11.exe"
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
		site, original, code = BASE + Variables.ADDR_NORMAL_CONTINUE_LIVES, Variables.EXPECTED_BYTES["ADDR_NORMAL_CONTINUE_LIVES"], Variables.NORMAL_CONTINUE_LIVES_CODE
		memory.set(site, original)
		patch_value(memory, site, original, code, 5)
		self.assertEqual(memory.writes, [(site, bytes.fromhex("b8 05 00 00 00 eb 17 90"))])
		patch_value(memory, site, original, code, 3)  # repeats over its own earlier patch
		self.assertEqual(memory.read_bytes(site, len(original)), code(3))
		memory.writes.clear()
		memory.set(site, b"\x90" * len(original))
		with self.assertRaises(PatchMismatch):
			patch_value(memory, site, original, code, 6)
		self.assertEqual(memory.writes, [])
		self.assertEqual(receive.continue_lives(["+1 Life"] * 3 + ["Next Stage"]), 3)
		self.assertEqual(receive.continue_lives(["+1 Life"] * 12), 8)
		self.assertEqual(receive.continue_lives(["+1 Life"] * 5, limit_lives=2), 2)

	@unittest.skipUnless(GAME.exists(), ".games/ is gitignored")
	def test_continue_lives_site_bytes(self):
		"""th11.exe v1.00a: the original bytes sit at the site, and the patch's jump lands on the Practice branch's
		mov [lives], eax (A3 18 57 4A 00) right before the shared continuation at 0x41FA5B."""
		exe = GAME.read_bytes()
		offset = Variables.ADDR_NORMAL_CONTINUE_LIVES - 0x1000 + 0x400  # .text: RVA 0x1000 at file offset 0x400
		original = Variables.EXPECTED_BYTES["ADDR_NORMAL_CONTINUE_LIVES"]
		self.assertEqual(exe[offset:offset + len(original)], original)
		self.assertEqual(exe[offset - 0xF1:offset - 0xEC], bytes.fromhex("be 02 00 00 00"))  # 0x41F947 mov esi, 2: vanilla lives
		code = Variables.NORMAL_CONTINUE_LIVES_CODE(2)
		target = offset + 7 + code[6]  # jmp rel8 ends at site + 7
		self.assertEqual(exe[target:target + 5], bytes.fromhex("a3 18 57 4a 00"))
		self.assertEqual(target + 5, offset + 8 + original[7])  # the original jmp's target, 0x41FA5B

	def test_normal_run_stage_transitions(self):
		states = [decode_state(S0), play(1), play(1, True), play(1), play(1, True), play(1), play(2), play(2, True), play(2)]
		sent, runs = [], 0
		for prev, state in zip(states, states[1:]):
			locations, runs = step(prev, state, runs)
			sent += locations
		self.assertEqual(sent, ids("[Reimu] Kisume - Midboss", "[Reimu] Yamame Defeated", "[Reimu] Stage 1 Clear", "[Reimu] Parsee - Midboss"))


class TestPracticeStartingLives(unittest.TestCase):
	def test_min_lives_adds_to_received(self):
		"""59: min_lives + the +1 Life items, capped by limit_lives and the game's 9."""
		from ..receive import practice_lives
		self.assertEqual(practice_lives(["+1 Life"], {}), 1)
		self.assertEqual(practice_lives(["+1 Life"], {"min_lives": 2}), 3)
		self.assertEqual(practice_lives(["+1 Life"] * 8, {"min_lives": 8}), 9)
		self.assertEqual(practice_lives(["+1 Life"], {"min_lives": 2}, limit_lives=2), 2)

	@unittest.skipUnless(GAME.exists(), "no th11.exe (.games is gitignored)")
	def test_practice_starting_lives_site_bytes(self):
		"""49: th11.exe v1.00a's Practice init sets lives with this exact instruction, and the patch keeps its shape."""
		exe = GAME.read_bytes()
		offset = Variables.ADDR_PRACTICE_STARTING_LIVES - 0x1000 + 0x400
		original = Variables.EXPECTED_BYTES["ADDR_PRACTICE_STARTING_LIVES"]
		self.assertEqual(exe[offset:offset + len(original)], original)
		self.assertEqual(Variables.PRACTICE_STARTING_LIVES_CODE(9), original)  # 9 restores vanilla
		self.assertEqual(len(Variables.PRACTICE_STARTING_LIVES_CODE(3)), len(original))
