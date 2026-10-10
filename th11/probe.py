"""
Memory probe: prints every address table entry so the human can check it in-game.
Pure: the reader only needs base_address and read_bytes(address, size).
"""
from .Variables import PROBE_TABLE


def read_int(reader, address, signed=False) -> int:
	return int.from_bytes(reader.read_bytes(address, 4), "little", signed=signed)


def resolve(reader, entry) -> int:
	"""Static offset or MoF-style pointer chain [base, off, ...] -> absolute address."""
	if isinstance(entry, int):
		return reader.base_address + entry
	address = reader.base_address + entry[0]
	for offset in entry[1:]:
		address = read_int(reader, address) + offset
	return address


def read_entry(reader, entry):
	"""Signed int at a table entry, or None if unsourced or unreadable (e.g. a chain through a null pointer)."""
	if entry is None:
		return None
	try:
		return read_int(reader, resolve(reader, entry), signed=True)
	except Exception:
		return None


def write_int(writer, entry, value):
	"""The one way client logic writes game memory: a table entry, never a raw address."""
	if entry is None or entry not in PROBE_TABLE.values():
		raise ValueError(f"write to {entry!r}, which is not a sourced Variables entry")
	writer.write_bytes(resolve(writer, entry), value.to_bytes(4, "little", signed=True))


def format_probe(reader, table) -> str:
	lines = []
	for name, entry in table.items():
		if entry is None:
			lines.append(f"{name} = <unsourced>")
			continue
		try:
			address = resolve(reader, entry)
			value = read_int(reader, address, signed=True)
		except Exception:
			lines.append(f"{name} = <unreadable>")
			continue
		lines.append(f"{name} = {value} (addr 0x{address:08X})")
	return "\n".join(lines)
