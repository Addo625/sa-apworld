import unittest

from .. import Variables
from ..receive import PRACTICE_TABLE_SIZE, apply, apply_new, extra_shots, extra_unlock, goal_reached, practice_open, practice_unlock, sound
from ..state import decode_state
from .test_state import PRACTICE_S1, S0

LIVES, POWER = Variables.ADDR_LIVES, Variables.ADDR_POWER


def play(lives=2, power=0):
	return decode_state({**PRACTICE_S1, "ADDR_LIVES": lives, "ADDR_POWER": power})


class TestApply(unittest.TestCase):
	def test_apply_life(self):
		self.assertEqual(apply("+1 Life", play(lives=2)), [(LIVES, 3)])

	def test_apply_life_cap(self):
		self.assertEqual(apply("+1 Life", play(lives=9)), [(LIVES, 9)])

	def test_apply_life_respects_limit(self):
		self.assertEqual(apply("+1 Life", play(lives=2), limit_lives=3), [(LIVES, 3)])
		self.assertEqual(apply("+1 Life", play(lives=3), limit_lives=3), [(LIVES, 3)])
		self.assertEqual(apply("+1 Life", play(lives=9), limit_lives=3), [(LIVES, 9)])  # never takes lives away
		self.assertEqual(apply_new(["+1 Life"] * 3, 0, play(lives=2), 3)[0], [(LIVES, 3), (LIVES, 3), (LIVES, 3)])

	def test_practice_start_holds_lives_and_packs(self):
		"""80: the game's run init gives a Practice run the item lives (49) and power (80); waiting ones aren't added
		again, and the client writes no power of its own. Other waiting items still apply."""
		names = ["+1 Life", "+0.50 Power", "+0.50 Power", "+0.05 Power"]
		self.assertEqual(apply_new(names, 0, play(lives=1, power=20), started=True), ([(POWER, 21)], 4))
		self.assertEqual(apply_new(["+1 Life"], 0, play(lives=1))[0], [(LIVES, 2)])  # mid-run: applied as before

	def test_practice_power(self):
		from ..receive import practice_power
		self.assertEqual(practice_power([]), 0)
		self.assertEqual(practice_power(["+0.50 Power", "+0.50 Power", "+0.05 Power"]), 20)
		self.assertEqual(practice_power(["+0.50 Power"] * 9), 80)  # 4.00 at most

	def test_apply_power(self):
		self.assertEqual(apply("+0.50 Power", play(power=33)), [(POWER, 43)])
		self.assertEqual(apply("+0.05 Power", play(power=33)), [(POWER, 34)])

	def test_apply_power_cap(self):
		self.assertEqual(apply("+0.50 Power", play(power=75)), [(POWER, 80)])

	def test_apply_outside_a_run_writes_nothing(self):
		self.assertEqual(apply("+1 Life", decode_state(S0)), [])  # menu: lives are leftovers
		self.assertEqual(apply("+1 Life", play(lives=-1)), [])  # game over

	def test_apply_waits_for_a_run(self):
		"""An item received on a menu is applied when the next run starts, not dropped."""
		self.assertEqual(apply_new(["+1 Life"], 0, decode_state(S0)), ([], 0))
		self.assertEqual(apply_new(["+1 Life"], 0, play(lives=2)), ([(LIVES, 3)], 1))

	def test_apply_unlock_items_write_no_resources(self):
		"""Unlock items go through practice_open and extra_shots, which need no run; apply_new leaves them, silently."""
		names = ["Next Stage", "Lower Difficulty", "Reimu A - Yukari", "[Marisa] Next Stage", "[Reimu C] Stage 4", "Stage 2",
			"Extra Stage", "[Marisa B] Extra Stage"]
		with self.assertNoLogs("Client", "INFO"):
			self.assertEqual(apply_new(names, 0, play()), ([], len(names)))

	def test_apply_batch_stacks(self):
		self.assertEqual(apply_new(["+1 Life", "+1 Life", "+0.50 Power"], 0, play(lives=2))[0],
			[(LIVES, 3), (LIVES, 4), (POWER, 10)])

	def test_apply_replay_is_idempotent(self):
		"""A reconnect resends the full list from index 0: applying it twice gives the writes of applying it once."""
		received = ["+1 Life", "+0.50 Power", "+0.05 Power"]
		writes, applied = apply_new(received, 0, play())
		self.assertEqual(apply_new(received, applied, play(lives=3, power=11)), ([], 3))
		self.assertEqual(apply_new(received + ["+1 Life"], applied, play(lives=3))[0], [(LIVES, 4)])


REIMU, MARISA_B = ["Reimu A - Yukari", "Reimu B - Suika", "Reimu C - Aya"], "Marisa B - Patchouli"
APART = {"extra_stage": 2}


class TestExtra(unittest.TestCase):
	def test_apply_extra_stage_global(self):
		self.assertEqual(extra_shots(REIMU + [MARISA_B], APART), set())
		self.assertEqual(extra_shots(REIMU + [MARISA_B, "Extra Stage"], APART), {0, 1, 2, 4})  # received shots only
		self.assertEqual(extra_shots(REIMU + ["Extra Stage"], {}), set())  # extra_stage exclude

	def test_apply_extra_stage_per_character(self):
		slot_data = {**APART, "stage_unlock": 1}
		self.assertEqual(extra_shots(REIMU + [MARISA_B, "[Marisa] Extra Stage"], slot_data), {4})

	def test_apply_extra_stage_per_shot(self):
		slot_data = {**APART, "stage_unlock": 2}
		self.assertEqual(extra_shots(REIMU + [MARISA_B, "[Reimu B] Extra Stage"], slot_data), {1})
		self.assertEqual(extra_shots(["Reimu A - Yukari", "[Reimu B] Extra Stage"], slot_data), set())  # Reimu B not received

	def test_linear_extra_follows_stage_items(self):
		progressive = {"extra_stage": 1}
		self.assertEqual(extra_shots([MARISA_B] + ["Next Stage"] * 5, progressive), set())
		self.assertEqual(extra_shots([MARISA_B] + ["Next Stage"] * 6, progressive), {4})
		self.assertEqual(extra_shots([MARISA_B, "Extra Stage"], {**progressive, "progressive_stage": False}), {4})

	def test_normal_mode_leaves_linear_extra_to_the_game(self):
		self.assertEqual(extra_shots([MARISA_B] + ["Next Stage"] * 6, {"extra_stage": 1, "mode": 1}), set())
		self.assertEqual(extra_shots([MARISA_B, "Extra Stage"], {**APART, "mode": 1}), {4})

	def test_extra_unlock_keeps_other_bits(self):
		self.assertEqual(extra_unlock(bytes([0, 1, 0x11, 0, 0, 0]), {0, 1, 2}), bytes([0x10, 0x11, 0x11, 0, 0, 0]))

	def test_extra_unlock_replay_is_idempotent(self):
		"""The bytes are a function of the full received list: a reconnect's replay writes the same bytes."""
		once = extra_unlock(bytes(6), extra_shots(REIMU + ["Extra Stage"], APART))
		self.assertEqual(extra_unlock(once, extra_shots(REIMU + ["Extra Stage"] * 2, APART)), once)


LUNATIC, HARD, NORMAL, EASY = 3, 2, 1, 0


def rows(shots, levels, stages):
	return {(shot, level, stage) for shot in shots for level in levels for stage in stages}


class TestPractice(unittest.TestCase):
	def test_apply_next_stage_writes_unlock_rows(self):
		self.assertEqual(practice_open(["Reimu A - Yukari"], {}), rows([0], [LUNATIC], [1]))
		self.assertEqual(practice_open(["Reimu A - Yukari"] + ["Next Stage"] * 2, {}), rows([0], [LUNATIC], [1, 2, 3]))
		self.assertEqual(practice_open(["Reimu A - Yukari"] + ["Next Stage"] * 9, {}), rows([0], [LUNATIC], range(1, 7)))

	def test_apply_lower_difficulty(self):
		self.assertEqual(practice_open([MARISA_B, "Lower Difficulty"], {}), rows([4], [HARD, LUNATIC], [1]))
		self.assertEqual(practice_open([MARISA_B] + ["Lower Difficulty"] * 3, {}), rows([4], range(4), [1]))
		self.assertEqual(practice_open([MARISA_B, "Lower Difficulty"], {"exclude_lunatic": True}), rows([4], [NORMAL, HARD, LUNATIC], [1]))

	def test_apply_shot_type(self):
		self.assertEqual(practice_open(["Next Stage"], {}), set())
		self.assertEqual(practice_open([MARISA_B, "Reimu C - Aya", "Next Stage"], {}), rows([2, 4], [LUNATIC], [1, 2]))

	def test_apply_group_stage_items(self):
		by_character, by_shot = {"stage_unlock": 1}, {"stage_unlock": 2}
		self.assertEqual(practice_open(REIMU + [MARISA_B, "[Marisa] Next Stage"], by_character),
			rows([0, 1, 2], [LUNATIC], [1]) | rows([4], [LUNATIC], [1, 2]))
		self.assertEqual(practice_open(REIMU + ["[Reimu B] Next Stage"], by_shot), rows([0, 1, 2], [LUNATIC], [1]) | {(1, LUNATIC, 2)})
		stages = {"progressive_stage": False}
		self.assertEqual(practice_open([MARISA_B, "Stage 2", "Stage 4"], stages), rows([4], [LUNATIC], [1, 2]))  # 4 needs 3 too
		self.assertEqual(practice_open([MARISA_B, "[Marisa B] Stage 2"], {**stages, **by_shot}), rows([4], [LUNATIC], [1, 2]))

	def test_normal_mode_opens_every_stage(self):
		self.assertEqual(practice_open([MARISA_B], {"mode": 1}), rows([4], [LUNATIC], range(1, 7)))

	def test_practice_unlock_sets_only_unlocked_bytes(self):
		current = bytes([0x11, 0x22, 0x33, 0x44, 0, 0, 0x55, 0x66] * (PRACTICE_TABLE_SIZE // 8))  # scores, padding survive
		new, ours = practice_unlock(current, 4, {(4, NORMAL, 3), (0, EASY, 1)})
		self.assertEqual(len(new), PRACTICE_TABLE_SIZE)
		self.assertEqual(new[0x45], 1)  # Normal Stage 3, the byte probe 32 R7 poked
		self.assertEqual([i for i in range(5, PRACTICE_TABLE_SIZE, 8) if new[i]], [0x45])
		self.assertEqual([i for i in range(PRACTICE_TABLE_SIZE) if new[i] != current[i]], [0x45])
		self.assertEqual(ours, {(4, NORMAL, 3)})

	def test_practice_replay_is_idempotent(self):
		"""A reconnect's replay of the same received list rewrites nothing."""
		received = ["Reimu A - Yukari", "Next Stage"]
		once, ours = practice_unlock(bytes(PRACTICE_TABLE_SIZE), 0, practice_open(received, {}))
		self.assertEqual(practice_unlock(once, 0, practice_open(list(received), {}), ours), (once, ours))
		self.assertEqual([i for i in range(5, PRACTICE_TABLE_SIZE, 8) if once[i]], [0x95, 0x9D])  # Lunatic 1, 2

	def test_lock_never_clears_unlocked_cleared_entry(self):
		"""47: 'cleared but locked' entries (39's writes) froze every boss dialog. Cleared entries stay or become unlocked."""
		cleared = bytes([0, 0, 0, 0, 1, 1, 0, 0] * (PRACTICE_TABLE_SIZE // 8))
		damaged = bytes([0, 0, 0, 0, 1, 0, 0, 0] * (PRACTICE_TABLE_SIZE // 8))
		every = rows([0], range(4), range(1, 7))
		self.assertEqual(practice_unlock(cleared, 0, set(), every), (cleared, set()))  # even entries it unlocked itself
		self.assertEqual(practice_unlock(damaged, 0, set())[0], cleared)  # a damaged save is repaired

	def test_lock_keeps_entries_unlocked_before_attach(self):
		"""Only entries this client unlocked in this game process are locked again; the save's own unlocks stay."""
		saved = bytearray(PRACTICE_TABLE_SIZE)
		saved[0x05] = 1  # Easy 1, unlocked by the game, not cleared
		new, ours = practice_unlock(bytes(saved), 0, set())
		self.assertEqual(new, bytes(saved))
		opened, ours = practice_unlock(bytes(saved), 0, rows([0], [EASY], [1, 2]))  # Easy 2 is ours
		self.assertEqual((opened[0x05], opened[0x0D], ours), (1, 1, {(0, EASY, 2)}))
		relocked, ours = practice_unlock(opened, 0, set(), ours)  # another seed, same game: only ours goes
		self.assertEqual((relocked, ours), (bytes(saved), set()))


class TestGoal(unittest.TestCase):
	def test_goal_reached(self):
		self.assertFalse(goal_reached(["+1 Life", "[Reimu] Ending - Koishi"], {}))
		self.assertTrue(goal_reached(["+1 Life", "[Marisa] Ending - Utsuho"], {}))

	def test_goal_koishi_both_characters(self):
		slot_data = {"koishi_endings": 2}
		self.assertFalse(goal_reached(["[Reimu] Ending - Koishi", "[Marisa] Ending - Utsuho"], slot_data))
		self.assertFalse(goal_reached(["[Reimu] Ending - Koishi", "[Marisa] Ending - Koishi"], slot_data))  # Utsuho too
		self.assertTrue(goal_reached(iter(["[Reimu] Ending - Koishi", "[Marisa] Ending - Koishi", "[Reimu] Ending - Utsuho"]), slot_data))


class TestSound(unittest.TestCase):
	def test_sound_requested_per_item(self):
		self.assertEqual(sound(["+1 Life"]), "extend")
		self.assertEqual(sound(["+0.05 Power"]), "power")
		self.assertEqual(sound(["Reimu A - Yukari"]), "ok")
		self.assertEqual(sound(["[Reimu] Extra Stage"]), "ok")
		self.assertEqual(sound(["Lower Difficulty", "+0.50 Power", "+1 Life"]), "extend")  # one per tick, most important
		self.assertIsNone(sound([]))
		self.assertIsNone(sound(["-1 Life"]))  # traps make their own noise

	def test_sound_patch_sites_guarded(self):
		"""The cave sites go through safe_patch: listed in EXPECTED_BYTES, so the guard and thcrap overlap tests cover them."""
		for name in ("ADDR_SOUND_HACK_1", "ADDR_SOUND_HACK_2"):
			self.assertIn(name, Variables.EXPECTED_BYTES)


class TestLinearExtraInNormalMode(unittest.TestCase):
	"""Q3: a normal-mode linear Extra opens when that owner's Stage 6 Clear is checked, not after a no-continue clear."""
	def test_opens_for_cleared_owner_only(self):
		from ..receive import extra_shots
		slot = {"mode": 2, "extra_stage": 1}  # normal_static, linear
		received = ["Reimu A - Yukari", "Reimu C - Aya", "Marisa B - Patchouli"]
		self.assertEqual(extra_shots(received, slot), set())
		self.assertEqual(extra_shots(received, slot, {"Reimu"}), {0, 2})  # Reimu's received shots
		self.assertEqual(extra_shots(received, slot, {"Marisa B"}), {4})  # shot_type owner


class TestKeyLocks(unittest.TestCase):
	"""75: the game's key locks, with the counts the YAML set (the logic slack never reaches the client)."""
	SLOT = {"spell_card_keys": 1, "mode": 0, "key_lock_toll": 3, "key_lock_toll_stage": 5, "key_lock_final": 6,
		"key_lock_final_target": 0}

	def test_key_locks_per_target(self):
		from ..Rules import key_locks
		self.assertEqual(key_locks(self.SLOT), [0, 0, 0, 0, 0, 3, 6, 6])
		self.assertEqual(key_locks({**self.SLOT, "key_lock_final_target": 2}), [0, 0, 0, 0, 0, 3, 3, 6])
		self.assertEqual(key_locks({**self.SLOT, "key_lock_final_target": 1}), [0, 0, 0, 0, 0, 3, 3, 3])
		self.assertEqual(key_locks({**self.SLOT, "mode": 2}), [0] * 8)  # normal mode: no locks
		self.assertEqual(key_locks({**self.SLOT, "spell_card_keys": 0}), [0] * 8)

	def test_practice_hides_key_locked_stages(self):
		shots = ["Reimu A - Yukari"] + ["Next Stage"] * 5
		stages = lambda keys: {stage for _, _, stage in practice_open(shots + ["Spell Card Key"] * keys, self.SLOT)}
		self.assertEqual(stages(2), {1, 2, 3, 4})
		self.assertEqual(stages(3), {1, 2, 3, 4, 5})  # the toll's 3, not 3 + slack
		self.assertEqual(stages(6), set(range(1, 7)))

	def test_goal_needs_keys_when_targeted(self):
		slot = {**self.SLOT, "key_lock_final_target": 1}
		self.assertFalse(goal_reached(["[Reimu] Ending - Utsuho"] + ["Spell Card Key"] * 5, slot))
		self.assertTrue(goal_reached(["[Reimu] Ending - Utsuho"] + ["Spell Card Key"] * 6, slot))
		self.assertTrue(goal_reached(["[Reimu] Ending - Utsuho"], self.SLOT))  # stage_6 target: the goal itself is free
