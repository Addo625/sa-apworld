import pymem
import pymem.memory

from .Variables import GAME_NAME

MEM_COMMIT, PAGE_NOACCESS, PAGE_GUARD = 0x1000, 0x01, 0x100


class gameController:
	"""The only module touching pymem: attaches to th11.exe by name and exposes raw byte access."""

	def __init__(self):
		self.pm = pymem.Pymem(GAME_NAME)
		self.base_address = self.pm.base_address

	def read_bytes(self, address, size) -> bytes:
		return self.pm.read_bytes(address, size)

	def write_bytes(self, address, data: bytes):
		self.pm.write_bytes(address, data, len(data))

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
