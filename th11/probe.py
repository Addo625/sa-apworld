"""
Memory probe: prints every address table entry so the human can check it in-game.
Pure: the reader only needs base_address and read_bytes(address, size).
"""
import logging
import struct
import traceback

from .Variables import PROBE_TABLE

write_log = False  # /writelog on: gameController.write_bytes logs every write (42)


def log_write(address, size):
	"""/writelog: one line per game write, naming the client functions that led to it, innermost first."""
	if write_log:
		callers = " < ".join(frame.name for frame in reversed(traceback.extract_stack(limit=6)[:-2]))  # minus this and write_bytes
		logging.getLogger("Client").info(f"write 0x{address:08X} {size} bytes ({callers})")


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
	write_entry(writer, entry, value.to_bytes(4, "little", signed=True))


def write_entry(writer, entry, data: bytes, offset=0):
	"""The one way client logic writes game memory: a table entry (+ offset into the record it points to), never a raw address."""
	if entry is None or entry not in PROBE_TABLE.values():
		raise ValueError(f"write to {entry!r}, which is not a sourced Variables entry")
	writer.write_bytes(resolve(writer, entry) + offset, data)


def float_candidates(data: bytes, low=0.1, high=20.0) -> list:
	"""[(offset, value)] of 4-byte aligned floats in data with low <= |value| <= high (speed-like)."""
	values = struct.unpack(f"<{len(data) // 4}f", data[:len(data) // 4 * 4])
	return [(i * 4, value) for i, value in enumerate(values) if low <= abs(value) <= high]


def parse_address(text: str) -> int:
	"""Hex address with optional hex offsets, no spaces: `029605CC`, `0x029605FC-30`, `029605CC+45-5A4`. Raises ValueError."""
	import re
	parts = re.findall(r"[+-]?[^+-]+", text)
	if not parts or "".join(parts) != text or any(c.isspace() for c in text):
		raise ValueError(text)
	return sum(-int(part[1:], 16) if part[0] == "-" else int(part.lstrip("+"), 16) for part in parts)


def parse_pattern(text: str) -> bytes:
	"""Hex bytes for /memsearch. Spaces are allowed; `XX*N` repeats the bytes XX N times: `00*4 0101 00*6` = 4 zeros, 01 01, 6 zeros.
	Raises ValueError on anything else."""
	out = b""
	for token in text.split():
		hex_part, star, count = token.partition("*")
		out += bytes.fromhex(hex_part) * (int(count) if star else 1)
	return out


def memsearch(reader, regions, pattern: bytes, cap=50, block=0x10000) -> list:
	"""Addresses of pattern in regions [(start, size)], at most cap. Adjacent regions are joined and
	blocks overlap by len(pattern) - 1, so a match may span either boundary. Unreadable blocks are skipped."""
	joined = []
	for start, size in sorted(regions):
		if joined and sum(joined[-1]) == start:
			joined[-1][1] += size
		else:
			joined.append([start, size])
	found = []
	for start, size in joined:
		end = start + size
		for address in range(start, end, block):
			try:
				data = reader.read_bytes(address, min(block + len(pattern) - 1, end - address))
			except Exception:
				continue
			i = data.find(pattern)
			while i != -1 and i < block:  # later matches start in the next block
				found.append(address + i)
				if len(found) >= cap:
					return found
				i = data.find(pattern, i + 1)
	return found


def ptrscan(reader, start, end, target, window=0x1000) -> list:
	"""[(address, value)] of aligned 4-byte words in [start, end) whose value is in [target - window, target]:
	static pointers to the struct holding target. Unreadable memory raises, so it never reads as "no pointers".
	ponytail: one level only; a pointer to a pointer needs a second scan of the heap object it finds."""
	data = reader.read_bytes(start, end - start)
	values = struct.unpack(f"<{len(data) // 4}I", data[:len(data) // 4 * 4])
	return [(start + i * 4, value) for i, value in enumerate(values) if target - window <= value <= target]


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
