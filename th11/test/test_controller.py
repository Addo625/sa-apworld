import sys
import types
import unittest
from unittest import mock


def fake_pymem(base, image=b"MZ\x90\x00"):
	"""A pymem stand-in whose th11.exe module sits at `base` (None: not mapped yet)."""
	module = types.SimpleNamespace(lpBaseOfDll=base) if base is not None else None

	class Pymem:
		base_address = 0x6FFFFFF30000  # what Wine reported right after launch (batch 32 A5)
		process_handle = 1

		def __init__(self, name):
			pass

		def read_bytes(self, address, size):
			return image[:size] if address == base else b"\x00" * size

	pymem = types.ModuleType("pymem")
	pymem.Pymem = Pymem
	pymem.memory = types.ModuleType("pymem.memory")
	pymem.process = types.ModuleType("pymem.process")
	pymem.process.module_from_name = lambda handle, name: module
	return {"pymem": pymem, "pymem.memory": pymem.memory, "pymem.process": pymem.process}


def controller_with(base, image=b"MZ\x90\x00"):
	with mock.patch.dict(sys.modules, fake_pymem(base, image)):
		sys.modules.pop(__package__.rsplit(".", 1)[0] + ".gameController", None)
		from ..gameController import gameController
		try:
			return gameController()
		finally:
			sys.modules.pop(__package__.rsplit(".", 1)[0] + ".gameController", None)


class TestController(unittest.TestCase):
	def test_controller_uses_th11_module_base(self):
		self.assertEqual(controller_with(0x400000).base_address, 0x400000)

	def test_controller_rejects_non_game_base(self):
		for base, image in ((None, b"MZ"), (0x6FFFFFF30000, b"MZ"), (0x400000, b"\x00\x00")):
			with self.assertRaises(RuntimeError, msg=hex(base or 0)):
				controller_with(base, image)
