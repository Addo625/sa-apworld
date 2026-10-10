import importlib
import json
import re
import sys
import unittest
from pathlib import Path

from .. import Variables
from ..patching import PatchMismatch, safe_patch
from ..probe import format_probe

BASE = 0x400000
THCRAP = Path(__file__).resolve().parents[2] / ".games/sa/thcrap/repos/nmlgc/base_tsa"


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


class TestClientIsolation(unittest.TestCase):
	def test_client_modules_import_without_pymem(self):
		logic = ["Variables", "probe", "patching", "state", "Client"]  # Client attaches lazily through gameController
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
