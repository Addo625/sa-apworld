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


def patch_immediate(reader_writer, site, prefix: bytes, value: int) -> None:
	"""Write a one-byte immediate at site (absolute), guarded by the instruction bytes `prefix` right before it,
	so the patch repeats with new values (MoF setNormalContinueLives)."""
	safe_patch(reader_writer, site - len(prefix), prefix, prefix + bytes([value]))
