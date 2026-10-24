"""
Code-byte patches guarded by the expected original bytes. Pure: takes any read_bytes/write_bytes object.
"""
from . import Variables


class PatchMismatch(Exception):
	pass


# What each patch site holds once this client has patched it, so /selftest can tell its own work from another
# program's (vpatch, thprac, a different build).
PATCHED = {
	"ADDR_PRACTICE_STARTING_LIVES": lambda code: code in {Variables.PRACTICE_STARTING_LIVES_CODE(v) for v in range(256)},
	"ADDR_NORMAL_CONTINUE_LIVES": lambda code: code in {Variables.NORMAL_CONTINUE_LIVES_CODE(v) for v in range(256)},
	"ADDR_PRACTICE_STARTING_POWER": lambda code: code in {Variables.PRACTICE_STARTING_POWER_CODE(v) for v in range(256)},
	"ADDR_SOUND_HACK_1": lambda code: code == Variables.SOUND_HOOK,
	"ADDR_SOUND_HACK_2": lambda code: code == Variables.SOUND_CAVE,
}


def build_name(sha256: str):
	"""th11.exe's build from its SHA-256 (Variables.KNOWN_BUILDS), or None for a build nobody has checked."""
	return Variables.KNOWN_BUILDS.get(sha256.lower())


def selftest(reader):
	"""-> one line per code site the client patches: original, patched by this client, or changed by something else.
	A changed site means that patch would refuse to apply (PatchMismatch), so its feature stays off."""
	lines = []
	for name, original in Variables.EXPECTED_BYTES.items():
		address = reader.base_address + getattr(Variables, name)
		try:
			current = reader.read_bytes(address, len(original))
		except Exception as e:
			lines.append(f"{name} (0x{address:08X}): unreadable ({e})")
			continue
		if current == original:
			status = "OK (original game code)"
		elif PATCHED[name](current):
			status = "OK (already patched by this client)"
		else:
			status = f"CHANGED by something else: expected {original.hex(' ')}, found {current.hex(' ')}"
		lines.append(f"{name} (0x{address:08X}): {status}")
	return lines


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
