from contextlib import contextmanager

import pymem
import pymem.memory
import pymem.process

from .Variables import GAME_NAME
from .probe import log_write

MEM_COMMIT, PAGE_NOACCESS, PAGE_GUARD = 0x1000, 0x01, 0x100


class gameController:
	"""The only module touching pymem: attaches to th11.exe by name and exposes raw byte access."""

	def __init__(self):
		self.pm = pymem.Pymem(GAME_NAME)
		# Not pm.base_address: right after launch under Wine it named a Wine module (0x6FFFFFF30000, batch 32 A5),
		# so every write failed. th11.exe v1.00a is 32-bit without ASLR: its image is the module named th11.exe.
		module = pymem.process.module_from_name(self.pm.process_handle, GAME_NAME)
		base = module.lpBaseOfDll if module else None
		if base is None or base >= 0x80000000 or self.pm.read_bytes(base, 2) != b"MZ":
			raise RuntimeError(f"{GAME_NAME} image not mapped yet (base {base!r})")  # game_loop retries next tick
		self.base_address = base

	def exe_path(self):
		"""The running th11.exe's file path (QueryFullProcessImageNameW; also works under Wine), or None."""
		import ctypes
		buffer, size = ctypes.create_unicode_buffer(1024), ctypes.c_ulong(1024)
		if ctypes.windll.kernel32.QueryFullProcessImageNameW(self.pm.process_handle, 0, buffer, ctypes.byref(size)):
			return buffer.value
		return None

	def read_bytes(self, address, size) -> bytes:
		return self.pm.read_bytes(address, size)

	def write_bytes(self, address, data: bytes):
		log_write(address, len(data))
		self.pm.write_bytes(address, data, len(data))

	@contextmanager
	def suspended(self):
		"""Freeze every game thread while code is patched, then flush the instruction cache.
		Batch 44 #12: writing the 5-byte sound hook while the game ran it every frame crashed it at install."""
		import ctypes
		ntdll, kernel32 = ctypes.windll.ntdll, ctypes.windll.kernel32
		ntdll.NtSuspendProcess(self.pm.process_handle)
		try:
			yield
		finally:
			kernel32.FlushInstructionCache(self.pm.process_handle, None, 0)
			ntdll.NtResumeProcess(self.pm.process_handle)

	def readable_regions(self) -> list:
		"""[(start, size)] of committed, accessible pages, walked with VirtualQueryEx up to the 32-bit limit."""
		regions, address = [], 0
		while address < 0xFFFF0000:
			try:
				mbi = pymem.memory.virtual_query(self.pm.process_handle, address)
			except Exception:
				if not regions:
					raise  # first query failed: no access, not the end of the address space
				break  # past the last region
			if not mbi.RegionSize:
				break
			if mbi.State == MEM_COMMIT and not mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD):
				regions.append((mbi.BaseAddress, mbi.RegionSize))
			address = mbi.BaseAddress + mbi.RegionSize
		return regions
