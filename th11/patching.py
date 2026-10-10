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


def patch_value(reader_writer, site, original: bytes, code, value: int) -> None:
	"""Write code(value) over original at site (absolute); value is one byte. An earlier code(v) is accepted in place
	of original, so the patch repeats with new values (MoF setNormalContinueLives)."""
	# ponytail: one non-atomic write of live code; the game running it mid-write could crash. It runs once per
	# run start/continue, so the window is tiny; suspend the game's threads around the write if that's ever seen.
	current = reader_writer.read_bytes(site, len(original))
	if current != original and current not in {code(v) for v in range(256)}:
		raise PatchMismatch(f"0x{site:08X}: expected {original.hex(' ')} or an earlier patch, found {current.hex(' ')}")
	reader_writer.write_bytes(site, code(value))
