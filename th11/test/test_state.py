import ast
import unittest
from pathlib import Path

from .. import Variables
from ..probe import resolve, write_int
from ..state import decode_state, read_state
from .test_client import BASE, FakeMemory

# Ticket 06 /probe captures (state -> {entry: value}); None = <unreadable>.
# ADDR_ENEMY_MANAGER was only probed in S8b (0). Elsewhere it is inferred from the 06 boss notes:
# non-zero during a stage (bossrec found the boss field behind it), 0 on menus (S8b).
IN_STAGE = 0x02000000
OUT_OF_STAGE = {"ADDR_ENEMY_MANAGER": 0}
PRACTICE_S1 = {
	"ADDR_ENEMY_MANAGER": IN_STAGE, "ADDR_MENU_PTR": 0, "ADDR_MENU": None, "ADDR_MENU_CURSOR": None, "ADDR_STAGE": 1,
	"ADDR_DIFFICULTY": 1, "ADDR_CHARACTER": 0, "ADDR_SHOT_TYPE": 0, "ADDR_LIVES": 9, "ADDR_POWER": 0,
}
S0 = {**OUT_OF_STAGE, "ADDR_MENU_PTR": 52159048, "ADDR_MENU": 0, "ADDR_MENU_CURSOR": 0, "ADDR_STAGE": 0,
	"ADDR_DIFFICULTY": 1, "ADDR_CHARACTER": 0, "ADDR_SHOT_TYPE": 0, "ADDR_LIVES": 0, "ADDR_POWER": 0}
S1 = {**S0, "ADDR_MENU_PTR": 62416248, "ADDR_MENU": 1, "ADDR_MENU_CURSOR": 1, "ADDR_STAGE": 3, "ADDR_SHOT_TYPE": 1,
	"ADDR_LIVES": 9, "ADDR_POWER": 80}
FIXTURES = {
	"S0_title": (S0, dict(in_game=False, menu=0, character="Reimu", shot="Reimu A")),
	"S1_difficulty_select": (S1, dict(in_game=False, menu=1, menu_cursor=1, stage=3, lives=9, power=80, shot="Reimu B")),
	"S1b_difficulty_lunatic": ({**S1, "ADDR_MENU_CURSOR": 3}, dict(in_game=False, menu=1, menu_cursor=3, difficulty=1)),
	"S2_character_select": (
		{**S1, "ADDR_MENU_PTR": 58160792, "ADDR_MENU": 3, "ADDR_CHARACTER": 1, "ADDR_POWER": 62},
		dict(in_game=False, menu=3, menu_cursor=1, character="Marisa", shot="Marisa B", power=62),
	),
	"S3_practice_stage1": (PRACTICE_S1, dict(
		in_game=True, menu=None, stage=1, difficulty=1, character="Reimu", shot="Reimu A", lives=9, power=0)),
	"S4_midboss": ({**PRACTICE_S1, "ADDR_POWER": 33}, dict(in_game=True, stage=1, power=33)),
	"S5_after_midboss": ({**PRACTICE_S1, "ADDR_POWER": 44}, dict(in_game=True, power=44)),
	"S6_boss": ({**PRACTICE_S1, "ADDR_LIVES": 6, "ADDR_POWER": 0}, dict(in_game=True, lives=6, power=0)),
	"S7_stage_clear": ({**PRACTICE_S1, "ADDR_LIVES": 6, "ADDR_POWER": 14}, dict(in_game=True, lives=6, power=14)),
	"S8a_practice_menu_fresh": (S0, dict(in_game=False, menu=0)),
	"S8b_practice_menu_unlocked": (
		{**S0, "ADDR_MENU_PTR": 0, "ADDR_MENU": None, "ADDR_IS_BOSS_PRESENT": None},
		dict(in_game=False, boss_present=False, menu=None, stage=0),
	),
	"S9_quit_during_boss": (
		{**OUT_OF_STAGE, "ADDR_MENU_PTR": 60379904, "ADDR_MENU": 0, "ADDR_MENU_CURSOR": 2, "ADDR_STAGE": 1,
			"ADDR_DIFFICULTY": 0, "ADDR_CHARACTER": 0, "ADDR_SHOT_TYPE": 0, "ADDR_LIVES": 6, "ADDR_POWER": 50},
		dict(in_game=False, menu=0, menu_cursor=2, stage=1, difficulty=0, lives=6, power=50),
	),
	# The enemy manager wasn't probed at game over, so in_game is unknown there; lives == -1 is the signal.
	"S10_game_over_extra": (
		{key: value for key, value in PRACTICE_S1.items() if key != "ADDR_ENEMY_MANAGER"}
		| {"ADDR_STAGE": 7, "ADDR_DIFFICULTY": 4, "ADDR_LIVES": -1},
		dict(stage=7, difficulty=4, lives=-1, power=0),
	),
	"S11a_life_lost": ({**PRACTICE_S1, "ADDR_DIFFICULTY": 0, "ADDR_LIVES": 8}, dict(difficulty=0, lives=8)),
	"S11b_life_piece": (
		{**PRACTICE_S1, "ADDR_DIFFICULTY": 0, "ADDR_LIVES": 6, "ADDR_POWER": 50},
		dict(difficulty=0, lives=6, power=50),
	),
}


class TestProbeFixtures(unittest.TestCase):
	def test_fixture_entries_are_in_table(self):
		for name, (values, _) in FIXTURES.items():
			self.assertLessEqual(set(values), set(Variables.PROBE_TABLE), name)


def fixture_test(values, expected):
	def test(self):
		state = decode_state(values)
		self.assertEqual({field: getattr(state, field) for field in expected}, expected)
	return test


for _name, (_values, _expected) in FIXTURES.items():
	setattr(TestProbeFixtures, f"test_probe_fixtures_{_name}", fixture_test(_values, _expected))


class TestBossPresent(unittest.TestCase):
	MANAGER = BASE + Variables.ADDR_ENEMY_MANAGER

	def memory(self, manager, boss=None):
		memory = FakeMemory()
		memory.set(self.MANAGER, manager.to_bytes(4, "little"))
		if boss is not None:
			memory.set(manager + Variables.ADDR_IS_BOSS_PRESENT[1], boss.to_bytes(4, "little"))
		return memory

	def test_boss_present_stage_loading(self):
		self.assertFalse(read_state(self.memory(0)).boss_present)

	def test_boss_present_boss_up(self):
		self.assertTrue(read_state(self.memory(0x3000000, boss=0x3100000)).boss_present)

	def test_boss_present_no_boss(self):
		state = read_state(self.memory(0x3000000, boss=0))
		self.assertTrue(state.in_game)
		self.assertFalse(state.boss_present)


# The writers themselves: write_entry checks its entry at run time, safe_patch guards with EXPECTED_BYTES.
WRITERS = {"write_bytes", "write_entry", "safe_patch", "patch_value", "_cmd_poke"}  # _cmd_poke: human-typed debug write for probe requests (28)


def call_name(node):
	return isinstance(node, ast.Call) and getattr(node.func, "attr", getattr(node.func, "id", None))


class TestWriteAddresses(unittest.TestCase):
	def test_every_write_address_in_table(self):
		"""Client code writes only through write_int (entry checked at run time) or safe_patch on a table entry."""
		package = Path(__file__).resolve().parents[1]
		for path in package.glob("*.py"):
			tree = ast.parse(path.read_text())
			inside_writers = {
				id(node) for function in ast.walk(tree)
				if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)) and function.name in WRITERS
				for node in ast.walk(function)
			}
			for call in ast.walk(tree):
				if id(call) in inside_writers:
					continue
				where = f"{path.name}:{getattr(call, 'lineno', '?')}"
				self.assertNotEqual(call_name(call), "write_bytes", f"{where}: raw write_bytes, use write_int")
				if call_name(call) in ("safe_patch", "patch_value"):
					names = {getattr(n, "attr", getattr(n, "id", None)) for n in ast.walk(call.args[1])}
					self.assertTrue(names & set(Variables.EXPECTED_BYTES), f"{where}: patch site is not a Variables entry")

	def test_every_write_address_in_table_recorded(self):
		"""Recording fake: each sourced entry writes at its resolved address; a raw address writes nothing."""
		memory = FakeMemory()
		memory.set(BASE + Variables.ADDR_MENU_PTR, (0x3100000).to_bytes(4, "little"))
		memory.set(BASE + Variables.ADDR_ENEMY_MANAGER, (0x3000000).to_bytes(4, "little"))
		memory.set(BASE + Variables.ADDR_EXTRA_UNLOCK[0], (0x3300000).to_bytes(4, "little"))
		memory.set(BASE + Variables.ADDR_SPELL_ID[0], (0x3400000).to_bytes(4, "little"))
		memory.set(BASE + Variables.ADDR_PLAYER_PTR, (0x3000000).to_bytes(4, "little"))  # the loop writes it back unchanged
		entries = [entry for entry in Variables.PROBE_TABLE.values() if entry is not None]
		expected = [resolve(memory, entry) for entry in entries]
		for entry in entries:
			write_int(memory, entry, 0x3100000 if entry == Variables.ADDR_MENU_PTR else 0x3000000)  # keep pointers valid
		self.assertEqual([address for address, _ in memory.writes], expected)
		memory.writes.clear()
		for raw in (BASE + Variables.ADDR_LIVES, None, [Variables.ADDR_ENEMY_MANAGER, 0x20]):
			with self.assertRaises(ValueError):
				write_int(memory, raw, 1)
		self.assertEqual(memory.writes, [])

	def test_write_int_writes_signed_little_endian(self):
		memory = FakeMemory()
		write_int(memory, Variables.ADDR_LIVES, -1)
		self.assertEqual(memory.writes, [(BASE + Variables.ADDR_LIVES, b"\xff\xff\xff\xff")])


class TestDemoFlag(unittest.TestCase):
	def test_title_demo_is_not_play(self):
		"""Batch 32 R8: GAME_FLAGS 32 in both title demos; 0 in a normal run, 16 in Practice, 20 at a Practice Game Over."""
		self.assertFalse(decode_state({**PRACTICE_S1, "ADDR_GAME_FLAGS": 32}).in_game)
		self.assertTrue(decode_state({**PRACTICE_S1, "ADDR_GAME_FLAGS": 16}).in_game)
		self.assertTrue(decode_state({**PRACTICE_S1, "ADDR_GAME_FLAGS": 0}).in_game)
		self.assertTrue(decode_state({**PRACTICE_S1, "ADDR_GAME_FLAGS": 20}).in_game)
		self.assertFalse(decode_state({**PRACTICE_S1, "ADDR_GAME_FLAGS": 32}).boss_present)
