import importlib
import json
import re
import sys
import unittest
from pathlib import Path

from .. import Variables
from ..patching import PatchMismatch, safe_patch
from ..probe import format_probe, memsearch, parse_address, parse_pattern, ptrscan

BASE = 0x400000
CAPTURE_ENTRIES = ["ADDR_SPELL_ID", "ADDR_SPELL_BONUS", "ADDR_SPELL_HISTORY"]
THCRAP =Path(__file__).resolve().parents[2] / ".games/sa/thcrap/repos/nmlgc/base_tsa"
GAME = Path(__file__).resolve().parents[2] / ".games/sa/th11.exe"


class FakeMemory:
	"""Sparse byte memory; reading an unset byte raises like pymem does."""
	base_address = BASE

	def __init__(self):
		self.bytes = {}
		self.writes = []

	def set(self, address, data: bytes):
		for i, byte in enumerate(data):
			self.bytes[address + i] = byte

	def read_bytes(self, address, size):
		return bytes(self.bytes[address + i] for i in range(size))

	def write_bytes(self, address, data):
		self.writes.append((address, data))
		self.set(address, data)


class TestProbe(unittest.TestCase):
	def test_probe_formats_all_entries(self):
		memory = FakeMemory()
		memory.set(BASE + 0x10, (3).to_bytes(4, "little"))
		memory.set(BASE + 0x20, (0x500000).to_bytes(4, "little"))
		memory.set(0x500008, (-1).to_bytes(4, "little", signed=True))
		table = {"ADDR_LIVES": 0x10, "ADDR_MENU": [0x20, 0x8], "ADDR_TODO": None}
		self.assertEqual(format_probe(memory, table).splitlines(), [
			"ADDR_LIVES = 3 (addr 0x00400010)",
			"ADDR_MENU = -1 (addr 0x00500008)",
			"ADDR_TODO = <unsourced>",
		])

	def test_probe_survives_read_error(self):
		memory = FakeMemory()
		memory.set(BASE + 0x10, (7).to_bytes(4, "little"))
		table = {"ADDR_BAD_PTR": [0x30, 0x4], "ADDR_BAD": 0x40, "ADDR_LIVES": 0x10}
		self.assertEqual(format_probe(memory, table).splitlines(), [
			"ADDR_BAD_PTR = <unreadable>",
			"ADDR_BAD = <unreadable>",
			"ADDR_LIVES = 7 (addr 0x00400010)",
		])

	def test_probe_table_covers_every_address(self):
		self.assertIn("ADDR_LIVES", Variables.PROBE_TABLE)
		self.assertEqual(set(Variables.PROBE_TABLE), {name for name in vars(Variables) if name.startswith("ADDR_")})

	def test_capture_entries_present(self):
		for name in CAPTURE_ENTRIES:
			self.assertIn(name, Variables.PROBE_TABLE)

	def test_probe_lists_capture_entries(self):
		memory = FakeMemory()
		memory.set(BASE + 0xC343C, (0x14AF998).to_bytes(4, "little"))
		memory.set(0x14AF998 + 0x6E8, (5).to_bytes(4, "little"))
		lines = format_probe(memory, Variables.PROBE_TABLE).splitlines()
		self.assertIn("ADDR_SPELL_HISTORY = 5 (addr 0x014B0080)", lines)
		self.assertIn("ADDR_SPELL_ID = <unsourced>", lines)
		self.assertIn("ADDR_SPELL_BONUS = <unsourced>", lines)


class TestMemsearch(unittest.TestCase):
	def test_memsearch_finds_pattern(self):
		memory = FakeMemory()
		memory.set(0x0F00, bytes(0x2100))
		memory.set(0x0FFE, b"CRxy")  # spans the 0x1000 page boundary
		memory.set(0x1FFE, b"CRzw")  # spans the boundary between the two regions
		memory.set(0x2800, b"CRCR")
		regions = [(0x2000, 0x1000), (0x1000, 0x1000), (0x0F00, 0x100)]
		self.assertEqual(memsearch(memory, regions, b"CR", block=0x1000), [0x0FFE, 0x1FFE, 0x2800, 0x2802])
		self.assertEqual(memsearch(memory, regions, b"Rxy", block=0x10), [0x0FFF])

	def test_memsearch_skips_unreadable(self):
		memory = FakeMemory()
		memory.set(0x3000, b"..CR..")
		self.assertEqual(memsearch(memory, [(0x1000, 0x100), (0x3000, 6)], b"CR"), [0x3002])

	def test_memsearch_caps_results(self):
		memory = FakeMemory()
		memory.set(0x1000, b"\xAA" * 200)
		self.assertEqual(memsearch(memory, [(0x1000, 200)], b"\xAA\xAA", cap=50), list(range(0x1000, 0x1000 + 50)))

	def test_ptrscan_finds_static_pointer(self):
		memory = FakeMemory()
		memory.set(0x4A2000, bytes(0x40))
		memory.set(0x4A2010, (0x03821BB8).to_bytes(4, "little"))  # save struct, table at + 0x5A4
		memory.set(0x4A2020, (0x0382215C).to_bytes(4, "little"))  # the target itself
		memory.set(0x4A2030, (0x0382315C).to_bytes(4, "little"))  # past the target
		memory.set(0x4A2008, (0x03820000).to_bytes(4, "little"))  # before the window
		self.assertEqual(ptrscan(memory, 0x4A2000, 0x4A2040, 0x0382215C),
			[(0x4A2010, 0x03821BB8), (0x4A2020, 0x0382215C)])
		with self.assertRaises(KeyError):  # unreadable tail: an error, not "no pointers"
			ptrscan(memory, 0x4A2000, 0x4A2080, 0x0382215C)


class TestPatchSites(unittest.TestCase):
	def test_patch_sites_refuse_on_mismatch(self):
		memory = FakeMemory()
		memory.set(0x1000, b"\x6a\x02")
		with self.assertRaises(PatchMismatch):
			safe_patch(memory, 0x1000, b"\x6a\x03", b"\x6a\x09")
		self.assertEqual(memory.writes, [])
		self.assertEqual(memory.read_bytes(0x1000, 2), b"\x6a\x02")

	def test_patch_sites_write_on_match(self):
		memory = FakeMemory()
		memory.set(0x1000, b"\x6a\x02")
		safe_patch(memory, 0x1000, b"\x6a\x02", b"\x6a\x09")
		self.assertEqual(memory.writes, [(0x1000, b"\x6a\x09")])

	@unittest.skipUnless(GAME.exists(), ".games/ is gitignored")
	def test_sound_cave_sites_bytes(self):
		"""th11.exe v1.00a: vanilla bytes at both sites, and each rel32 in the hook and cave lands on the function
		the notes name (40). .text maps RVA 0x1000 to file offset 0x400 and holds 0x8A000 bytes, slack included."""
		exe = GAME.read_bytes()

		def code(rva, size):
			return exe[rva - 0x1000 + 0x400:rva - 0x1000 + 0x400 + size]

		def target(rva, code_bytes, at):  # the E8/E9 at code_bytes[at], placed at rva
			return rva + at + 5 + int.from_bytes(code_bytes[at + 1:at + 5], "little", signed=True)

		hook, cave, cave_code = Variables.ADDR_SOUND_HACK_1, Variables.ADDR_SOUND_HACK_2, Variables.SOUND_CAVE
		self.assertLessEqual(cave + len(cave_code), 0x1000 + 0x8A000)
		for name in ("ADDR_SOUND_HACK_1", "ADDR_SOUND_HACK_2"):
			expected = Variables.EXPECTED_BYTES[name]
			self.assertEqual(code(getattr(Variables, name), len(expected)), expected)
		self.assertEqual(target(hook, Variables.EXPECTED_BYTES["ADDR_SOUND_HACK_1"], 0), 0x4A340)  # sound queue update
		self.assertEqual(target(hook, Variables.SOUND_HOOK, 0), cave)
		self.assertEqual(code(0x4A340, 3), bytes.fromhex("83 ec 08"))  # sub esp, 8: its entry
		self.assertEqual(target(cave, cave_code, 0x15), 0x4A1E0)  # play sound esi
		self.assertEqual(code(0x4A1E0, 9), bytes.fromhex("57 0f bf 3c f5 f6 34 4a 00"))  # push edi; movsx edi, [0x4A34F6 + esi*8]
		self.assertEqual(target(cave, cave_code, 0x23), 0x2098A)  # extend's HUD tail
		self.assertEqual(code(0x2098A, 0x1A), bytes.fromhex("a1 1c 57 4a 00 8b 15 18 57 4a 00 57 8b 3d 84 8d 4a 00 50 e8 be 96 ff ff 5f c3"))  # ... call 0x41A060 (HUD lives/pieces, ret 4); pop edi; ret
		self.assertEqual(target(cave, cave_code, 0x29), 0x4A340)
		self.assertEqual(cave_code[0x28], 0x61)  # popad, where both jz land
		self.assertEqual(cave + 0x0B + cave_code[0x0A], cave + 0x28)
		self.assertEqual(cave + 0x23 + cave_code[0x22], cave + 0x28)
		sound_id = (BASE + Variables.ADDR_CUSTOM_SOUND_ID).to_bytes(4, "little")
		self.assertEqual((cave_code[3:7], cave_code[0x0D:0x11]), (sound_id, sound_id))

	@unittest.skipUnless(GAME.exists(), ".games/ is gitignored")
	def test_extra_unlock_is_what_the_menus_read(self):
		"""33: the any-shot Extra check and the shot select's Extra row test bit 0x10 at [0x4A8EBC] + 0x2DDF0 (+ char * 3)."""
		exe = GAME.read_bytes()
		code = lambda rva, size: exe[rva - 0x1000 + 0x400:][:size]
		save, offset = Variables.ADDR_EXTRA_UNLOCK
		pointer, field = (BASE + save).to_bytes(4, "little"), offset.to_bytes(4, "little")
		bit = bytes([Variables.EXTRA_UNLOCK_BIT])
		# mov eax, [save]; mov cl, 0x10; test [eax + field], cl
		self.assertEqual(code(0x39350, 13), b"\xa1" + pointer + b"\xb1" + bit + b"\x84\x88" + field)
		# mov eax, [character]; mov edx, [save]; lea ecx, [edx + eax * 2]; add ecx, eax; test byte [ecx + field], 0x10
		self.assertEqual(code(0x3D0DF, 23), bytes.fromhex("a1 10 57 4a 00 8b 15") + pointer + bytes.fromhex("8d 0c 42 03 c8 f6 81") + field + bit)

	def test_patch_sites_have_expected_bytes(self):
		for name, expected in Variables.EXPECTED_BYTES.items():
			self.assertIn(name, Variables.PROBE_TABLE)
			if getattr(Variables, name) is not None:
				self.assertTrue(expected, f"{name} has an address but no EXPECTED_BYTES")

	@unittest.skipUnless(THCRAP.exists(), ".games/ is gitignored")
	def test_patch_sites_dont_overlap_thcrap(self):
		ranges = thcrap_ranges()
		self.assertGreater(len(ranges), 20)  # the parse found the binhacks and breakpoints
		for name, expected in Variables.EXPECTED_BYTES.items():
			offset = getattr(Variables, name)
			if offset is None:
				continue
			start, end = BASE + offset, BASE + offset + len(expected)
			for hack, hack_start, hack_end in ranges:
				self.assertFalse(start < hack_end and hack_start < end, f"{name} overlaps thcrap {hack}")


def thcrap_address(text):
	return BASE + int(text[2:], 16) if text.startswith("Rx") else int(text, 16)


# [symbol] and <option> references assemble to 4 bytes.
# ponytail: other thcrap code syntax (expressions) is counted as hex, extend if a v1.00a hack uses it.
REFERENCE = re.compile(r"\[[^\]]*\]|<[^>]*>")


def code_length(code):
	return len(REFERENCE.sub("", code).replace(" ", "")) // 2 + 4 * len(REFERENCE.findall(code))


def thcrap_ranges():
	"""(name, start, end) for every v1.00a binhack and breakpoint, merging th11.js into the version file."""
	base, version = (json.loads((THCRAP / f).read_text()) for f in ("th11.js", "th11.v1.00a.js"))
	ranges = []
	for kind in ("binhacks", "breakpoints"):
		for name, hack in version[kind].items():
			hack = {**base.get(kind, {}).get(name, {}), **hack}
			addresses = hack["addr"] if isinstance(hack["addr"], list) else [hack["addr"]]
			if "code" in hack:
				length = max(code_length(hack["code"]), code_length(hack.get("expected", "")))
			else:
				length = int(hack.get("cavesize", 1))
			ranges += [(name, thcrap_address(a), thcrap_address(a) + length) for a in addresses]
	return ranges


def game_memory(lives=2, boss=0, **fields):
	"""FakeMemory holding a Practice Stage 1 run (probe 06 S3) with the given lives, boss field and other entries."""
	from .test_state import PRACTICE_S1
	memory, manager = FakeMemory(), 0x3000000
	for name, value in {**PRACTICE_S1, "ADDR_ENEMY_MANAGER": manager, "ADDR_LIVES": lives, **fields}.items():
		entry = getattr(Variables, name)
		if isinstance(entry, int) and value is not None:
			memory.set(BASE + entry, value.to_bytes(4, "little", signed=True))
	memory.set(manager + Variables.ADDR_IS_BOSS_PRESENT[1], boss.to_bytes(4, "little"))
	for site in ("ADDR_SOUND_HACK_1", "ADDR_SOUND_HACK_2"):  # vanilla code, so the sound cave installs
		memory.set(BASE + getattr(Variables, site), Variables.EXPECTED_BYTES[site])
	return memory


# Practice S3's Reimu A on Normal; checks need both unlocked (ticket 16).
UNLOCKED = ("Reimu A - Yukari", "Lower Difficulty", "Lower Difficulty")


def menu_memory(menu, cursor):
	"""FakeMemory on a menu (probe 06 S1): menu object with its id and cursor, no stage."""
	memory, menu_object = FakeMemory(), 0x3100000
	memory.set(BASE + Variables.ADDR_MENU_PTR, menu_object.to_bytes(4, "little"))
	memory.set(BASE + Variables.ADDR_ENEMY_MANAGER, bytes(4))
	memory.set(menu_object + Variables.ADDR_MENU[1], menu.to_bytes(4, "little"))
	memory.set(menu_object + Variables.ADDR_MENU_CURSOR[1], cursor.to_bytes(4, "little"))
	return memory


def received(*names):
	from NetUtils import NetworkItem
	from ..Items import item_table
	return [NetworkItem(item_table[name].code, 0, 1) for name in names]


class TestClientLoop(unittest.IsolatedAsyncioTestCase):
	def context(self, *items, sound=False):
		from ..Client import TouhouContext
		ctx = TouhouContext()  # needs the running loop
		ctx.item_sound = sound
		ctx.slot = 1
		ctx.missing_locations = set(range(Variables.STARTING_ID, Variables.STARTING_ID + 1000))
		ctx.items_received = received(*items)
		ctx.sent = []

		async def send_msgs(msgs):
			ctx.sent += msgs
		ctx.send_msgs = send_msgs
		return ctx

	async def test_goal_sent_on_ending_item(self):
		from NetUtils import ClientStatus
		ctx = self.context("+1 Life")
		await ctx.check_goal()
		self.assertEqual(ctx.sent, [])
		ctx.items_received = received("+1 Life", "[Reimu] Ending - Utsuho")
		await ctx.check_goal()
		await ctx.check_goal()
		self.assertEqual(ctx.sent, [{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

	async def test_poll_sends_check_and_writes_items(self):
		from ..Locations import location_table
		ctx = self.context(*UNLOCKED, "+1 Life")
		midboss_up = game_memory(lives=2, boss=0x3100000)
		prev, runs = await ctx.poll(midboss_up, None, 0)
		self.assertEqual(ctx.sent, [])
		self.assertEqual(midboss_up.writes[0], (BASE + Variables.ADDR_LIVES, (3).to_bytes(4, "little")))  # then its sound
		midboss_gone = game_memory(lives=3)
		state, runs = await ctx.poll(midboss_gone, prev, runs)
		self.assertEqual(ctx.sent, [{"cmd": "LocationChecks", "locations": (location_table["[Reimu] Kisume - Midboss"],)}])
		await ctx.poll(midboss_gone, state, runs)  # the next tick: nothing new
		self.assertEqual(len(ctx.sent), 1)
		self.assertEqual(midboss_gone.writes, [])

	async def test_poll_plays_item_sound_once(self):
		from unittest import mock
		lives = (BASE + Variables.ADDR_LIVES, (3).to_bytes(4, "little"))
		extend = (BASE + Variables.ADDR_CUSTOM_SOUND_ID, (0x2C).to_bytes(4, "little"))
		cave = [(BASE + Variables.ADDR_SOUND_HACK_2, Variables.SOUND_CAVE), (BASE + Variables.ADDR_SOUND_HACK_1, Variables.SOUND_HOOK)]
		ctx, memory = self.context("+1 Life", sound=True), game_memory(lives=2)
		await ctx.poll(memory, None, 0)
		self.assertEqual(memory.writes, [lives] + cave + [extend])  # lives first: the cave redraws them with the sound
		memory.writes.clear()
		await ctx.poll(memory, None, 0)  # applied already: no second sound
		self.assertEqual(memory.writes, [])
		memory.set(BASE + Variables.ADDR_LIVES, (2).to_bytes(4, "little"))
		await self.context("+1 Life", sound=True).poll(memory, None, 0)  # a restarted client, same game: the cave stays
		self.assertEqual(memory.writes, [lives, extend])
		with mock.patch.multiple(Variables, ADDR_CUSTOM_SOUND_ID=None), mock.patch.dict(Variables.PROBE_TABLE, {"ADDR_CUSTOM_SOUND_ID": None}):
			memory = game_memory(lives=2)
			with self.assertLogs("Client", "INFO") as logs:
				await self.context("+1 Life", sound=True).poll(memory, None, 0)
			self.assertIn("pending the sound cave", "\n".join(logs.output))
			self.assertEqual(memory.writes, [lives])

	async def test_item_sound_off_by_default_writes_no_cave(self):
		memory = game_memory(lives=2)
		await self.context("+1 Life").poll(memory, None, 0)
		self.assertEqual(memory.writes, [(BASE + Variables.ADDR_LIVES, (3).to_bytes(4, "little"))])  # no cave, hook or sound id

	async def test_sound_cave_refuses_unexpected_code(self):
		memory = game_memory(lives=2)
		memory.set(BASE + Variables.ADDR_SOUND_HACK_2, b"\xcc" * len(Variables.SOUND_CAVE))  # slack used by something else
		with self.assertLogs("Client", "ERROR") as logs:
			await self.context("+1 Life", sound=True).poll(memory, None, 0)
		self.assertIn("not played, unexpected game code", "\n".join(logs.output))
		self.assertEqual(memory.writes, [(BASE + Variables.ADDR_LIVES, (3).to_bytes(4, "little"))])  # no cave, no sound id

	async def test_poll_fires_trap_once(self):
		from unittest import mock
		from .. import traps
		ctx = self.context("-1 Life")
		with mock.patch.object(traps, "ENTER_DELAY", 0):
			memory = game_memory(lives=2)
			await ctx.poll(memory, None, 0)
			self.assertEqual(memory.writes, [(BASE + Variables.ADDR_LIVES, (1).to_bytes(4, "little"))])
			memory = game_memory(lives=1)
			await ctx.poll(memory, None, 0)  # not replayed
			self.assertEqual(memory.writes, [])

	async def test_poll_trap_sees_item_written_same_tick(self):
		from unittest import mock
		from .. import traps
		ctx = self.context("+1 Life", "-1 Life")
		with mock.patch.object(traps, "ENTER_DELAY", 0):
			memory = game_memory(lives=2)
			await ctx.poll(memory, None, 0)
		lives = [int.from_bytes(data, "little") for address, data in memory.writes if address == BASE + Variables.ADDR_LIVES]
		self.assertEqual(lives, [3, 2])

	async def test_poll_maps_checks_with_slot_data(self):
		from ..Locations import location_table
		ctx = self.context(*UNLOCKED)
		ctx.on_package("Connected", {"slot_data": {"difficulty_check": True, "check_multiple_difficulty": True}})
		prev, runs = await ctx.poll(game_memory(boss=0x3100000), None, 0)
		await ctx.poll(game_memory(), prev, runs)  # Practice S3 is Normal; 2 Lower Difficulty open Normal, not Easy
		self.assertEqual(ctx.sent, [{"cmd": "LocationChecks", "locations": (location_table["[Normal][Reimu] Kisume - Midboss"],)}])

	async def test_checks_before_connect_use_slot_data(self):
		from ..Locations import location_table
		ctx = self.context()
		ctx.slot = None
		hard_reimu_b = {"ADDR_DIFFICULTY": 2, "ADDR_SHOT_TYPE": 1}
		prev, runs = await ctx.poll(game_memory(boss=0x3100000, **hard_reimu_b), None, 0)
		state, runs = await ctx.poll(game_memory(**hard_reimu_b), prev, runs)
		self.assertEqual(ctx.sent, [])
		ctx.slot = 1
		ctx.on_package("Connected", {"slot_data": {"shot_type": True, "difficulty_check": True}})
		state, runs = await ctx.poll(game_memory(**hard_reimu_b), state, runs)
		self.assertEqual(ctx.sent, [])  # waits for ReceivedItems: the lock filter needs them
		ctx.items_received = received("Reimu B - Suika", "Lower Difficulty")  # Hard open
		await ctx.poll(game_memory(**hard_reimu_b), state, runs)
		self.assertEqual(ctx.sent, [{"cmd": "LocationChecks", "locations": (location_table["[Hard][Reimu B] Kisume - Midboss"],)}])

	async def test_checks_before_connect_skip_locked_shot(self):
		ctx = self.context()
		ctx.slot = None
		prev, runs = await ctx.poll(game_memory(boss=0x3100000, ADDR_DIFFICULTY=2, ADDR_SHOT_TYPE=1), None, 0)
		state, runs = await ctx.poll(game_memory(ADDR_DIFFICULTY=2, ADDR_SHOT_TYPE=1), prev, runs)
		ctx.slot = 1
		ctx.items_received = received("Reimu A - Yukari", "Lower Difficulty")  # Reimu B locked
		await ctx.poll(game_memory(ADDR_DIFFICULTY=2, ADDR_SHOT_TYPE=1), state, runs)
		self.assertEqual(ctx.sent, [])

	async def test_poll_ignores_locked_shot(self):
		ctx = self.context("Reimu B - Suika", "Lower Difficulty", "Lower Difficulty")
		prev, runs = await ctx.poll(game_memory(boss=0x3100000), None, 0)
		await ctx.poll(game_memory(), prev, runs)
		self.assertEqual(ctx.sent, [])

	async def test_locked_run_logs_once(self):
		ctx = self.context("Reimu B - Suika", "Lower Difficulty", "Lower Difficulty")
		prev, runs = await ctx.poll(menu_memory(menu=3, cursor=1), None, 0)
		with self.assertLogs("Client", "INFO") as logs:
			state, runs = await ctx.poll(game_memory(), prev, runs)  # Practice S3: Reimu A
			await ctx.poll(game_memory(), state, runs)
		self.assertEqual([line for line in logs.output if "isn't unlocked" in line],
			["INFO:Client:Reimu A isn't unlocked: this run sends no checks"])
		ctx = self.context("Reimu A - Yukari")  # Normal locked
		with self.assertLogs("Client", "INFO") as logs:
			await ctx.poll(game_memory(), prev, 0)
		self.assertIn("Normal isn't unlocked: this run sends no checks", "\n".join(logs.output))

	async def test_poll_moves_cursor_off_locked_difficulty(self):
		ctx = self.context("Reimu A - Yukari", "Lower Difficulty")  # Hard and Lunatic open
		memory = menu_memory(menu=1, cursor=0)
		await ctx.poll(memory, None, 0)
		self.assertEqual(memory.writes, [(0x3100000 + Variables.ADDR_MENU_CURSOR[1], (2).to_bytes(4, "little"))])
		memory = menu_memory(menu=1, cursor=3)
		await ctx.poll(memory, None, 0)
		self.assertEqual(memory.writes, [])

	async def test_poll_before_received_items_keeps_checks(self):
		ctx = self.context()  # connected, ReceivedItems not in yet
		prev, runs = await ctx.poll(game_memory(boss=0x3100000), None, 0)
		await ctx.poll(game_memory(), prev, runs)
		self.assertEqual(len(ctx.sent), 1)

	async def test_poll_unlocks_extra_on_a_menu(self):
		save = 0x3200000
		memory = menu_memory(menu=0, cursor=0)
		ctx = self.context("Marisa B - Patchouli", "[Marisa B] Extra Stage")
		ctx.slot_data = {"extra_stage": 2, "stage_unlock": 2}
		await ctx.poll(memory, None, 0)
		self.assertEqual(memory.writes, [])  # save struct not loaded: skipped
		memory.set(BASE + Variables.ADDR_EXTRA_UNLOCK[0], save.to_bytes(4, "little"))
		memory.set(save + Variables.ADDR_EXTRA_UNLOCK[1], bytes([1, 0, 0, 0, 1, 0]))
		await ctx.poll(memory, None, 0)
		self.assertEqual(memory.writes, [(save + Variables.ADDR_EXTRA_UNLOCK[1], bytes([1, 0, 0, 0, 0x11, 0]))])
		memory.writes.clear()
		await ctx.poll(memory, None, 0)  # already set: no write
		self.assertEqual(memory.writes, [])

	async def test_poll_unconnected_leaves_menu(self):
		ctx = self.context()
		ctx.slot = None
		memory = menu_memory(menu=1, cursor=0)
		await ctx.poll(memory, None, 0)
		self.assertEqual(memory.writes, [])


class TestClientIsolation(unittest.TestCase):
	def test_client_modules_import_without_pymem(self):
		logic = ["Variables", "probe", "patching", "state", "detect", "guard", "receive", "traps", "deathlink", "Client"]  # Client attaches lazily through gameController
		package = __package__.rsplit(".", 1)[0]
		saved = {name: sys.modules.get(name) for name in ["pymem", "kivy"] + [f"{package}.{m}" for m in logic]}
		try:
			sys.modules["pymem"] = None  # import pymem -> ImportError
			sys.modules["kivy"] = None
			for module in logic:
				sys.modules.pop(f"{package}.{module}", None)
				importlib.import_module(f"{package}.{module}")
		finally:
			for name, module in saved.items():
				if module is None:
					sys.modules.pop(name, None)
				else:
					sys.modules[name] = module
					if name.startswith(package):  # re-imports rebound the package attribute too
						setattr(sys.modules[package], name.rsplit(".", 1)[1], module)


class TestParsePattern(unittest.TestCase):
	def test_parse_pattern_hex_spaces_and_repeats(self):
		self.assertEqual(parse_pattern("00*4 0101 00*6"), bytes(4) + b"\x01\x01" + bytes(6))
		self.assertEqual(parse_pattern("e9dc020000"), bytes.fromhex("e9dc020000"))
		self.assertEqual(parse_pattern("e9 dc 02 00 00"), bytes.fromhex("e9dc020000"))
		self.assertEqual(parse_pattern("20*8 00*2 11*16"), b" " * 8 + bytes(2) + b"\x11" * 16)
		for bad in ("0x00", "zz", "00*x", "000"):
			with self.assertRaises(ValueError):
				parse_pattern(bad)

	def test_scoredat_compact_round_trips(self):
		spec = importlib.util.spec_from_file_location("scoredat_tool", Path(__file__).resolve().parents[2] / "tools" / "scoredat.py")
		if not spec or not Path(spec.origin).exists():
			self.skipTest("tools/ not next to the world (installed apworld)")
		tool = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(tool)
		for raw in (bytes(54) + b"\x01\x01", b" " * 8 + bytes(2) + b"\x11" * 16 + b"\x01" * 6, b"\xe9\xdc\x02\x00\x00"):
			self.assertEqual(parse_pattern(tool.compact(raw)), raw)

	def test_parse_address_offsets(self):
		self.assertEqual(parse_address("029605CC"), 0x029605CC)
		self.assertEqual(parse_address("0x029605FC-30"), 0x029605CC)
		self.assertEqual(parse_address("029605CC+45"), 0x02960611)
		self.assertEqual(parse_address("029605CC-5A4+68D4"), 0x029605CC - 0x5A4 + 0x68D4)
		for bad in ("", "zz", "029605CC - 30", "+-5"):
			with self.assertRaises(ValueError):
				parse_address(bad)
