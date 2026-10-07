import pymem

from .Variables import GAME_NAME


class gameController:
	"""The only module touching pymem: attaches to th11.exe by name and exposes raw byte access."""

	def __init__(self):
		self.pm = pymem.Pymem(GAME_NAME)
		self.base_address = self.pm.base_address

	def read_bytes(self, address, size) -> bytes:
		return self.pm.read_bytes(address, size)

	def write_bytes(self, address, data: bytes):
		self.pm.write_bytes(address, data, len(data))
