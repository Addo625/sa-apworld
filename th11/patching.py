"""
Code-byte patches guarded by the expected original bytes. Pure: takes any read_bytes/write_bytes object.
"""


class PatchMismatch(Exception):
	pass


def safe_patch(reader_writer, address, expected: bytes, new: bytes) -> None:
	"""Write new only if the bytes at address are exactly expected; otherwise raise and write nothing."""
	current = reader_writer.read_bytes(address, len(expected))
	if current != expected:
		raise PatchMismatch(f"0x{address:08X}: expected {expected.hex(' ')}, found {current.hex(' ')}")
	reader_writer.write_bytes(address, new)
