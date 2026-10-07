"""
Memory probe: prints every address table entry so the human can check it in-game.
Pure: the reader only needs base_address and read_bytes(address, size).
"""


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
