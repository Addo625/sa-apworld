#!/usr/bin/env python3
"""Print a decoded scoreth11.dat: chunks, practice progress per character, and /memsearch patterns.
Usage: tools/scoredat.py .games/sa/scoreth11.dat [--patterns ~/archipelago/install-wine/memsearch_patterns.json]
       tools/scoredat.py --repair .games/sa/scoreth11.dat  (unlock every cleared or scored Practice entry, ticket 47)
--patterns writes {"practice": hex, "status": hex}, so the client's `/memsearch practice` / `/memsearch status` need no typing."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "th11"))  # th11/__init__ needs AP; scoredat doesn't
import scoredat

PATTERN_SIZE = 16


def unique_pattern(decoded, chunk_offset):
	"""Shortest window (>= 16 bytes) starting at the practice table that occurs once in the decoded file."""
	start = chunk_offset + scoredat.PRACTICE_OFFSET
	end = start + len(scoredat.LEVELS) * len(scoredat.STAGES) * scoredat.PRACTICE_SIZE
	for size in range(PATTERN_SIZE, end - start + 1):
		window = decoded[start:start + size]
		if decoded.count(window) == 1:
			return window
	return None


STATUS_PATTERN = slice(0x0C, 0x2C)  # ST chunk: name padding, then per-shot flag rows (probe batch 32, R1)


def compact(pattern: bytes) -> str:
	"""Short /memsearch form: runs of 3+ equal bytes as `XX*N`, the rest as plain hex (probe.parse_pattern reads it back)."""
	tokens, i = [], 0
	while i < len(pattern):
		j = i
		while j < len(pattern) and pattern[j] == pattern[i]:
			j += 1
		tokens.append(f"{pattern[i]:02x}*{j - i}" if j - i >= 3 else pattern[i:j].hex())
		i = j
	return " ".join(tokens)


def main(path, patterns_out=None):
	decoded = scoredat.decode(Path(path).read_bytes())
	print(f"decoded {len(decoded)} bytes (header 0x{scoredat.HEADER_SIZE:X})")
	pattern = status = None
	for signature, offset, size, body in scoredat.chunks(decoded):
		if signature == "ST":
			status = body[STATUS_PATTERN]
		print(f"{signature} at 0x{offset:05X} size 0x{size:X}")
		if signature != "CR":
			continue
		print(f"  {scoredat.chara(body)} (unlocked, cleared, score) per stage:")
		for level, stages in scoredat.practice_progress(body).items():
			print(f"    {level:8}" + " ".join(f"{stage}:{u}/{c}/{s}" for stage, (u, c, s) in stages.items()))
		pattern = pattern or unique_pattern(decoded, offset)
	if pattern:
		print(f"/memsearch {compact(pattern)}  (first CR chunk's practice table, {len(pattern)} bytes, unique in file)")
	else:
		print("no unique practice-table pattern found")
	if status:
		print(f"/memsearch {compact(status)}  (ST chunk +0x0C..+0x2C: per-shot flags, {len(status)} bytes)")
	if patterns_out:
		named = {name: value.hex() for name, value in (("practice", pattern), ("status", status)) if value}
		Path(patterns_out).expanduser().write_text(json.dumps(named, indent=1))
		print(f"wrote {', '.join(named)} to {patterns_out}: type /memsearch {' or /memsearch '.join(named)}")


def repair(path):
	"""Set `unlocked` wherever `cleared` is or a score exists (47); the old file is kept as <save>.bak. Run with the game closed."""
	path = Path(path)
	raw = path.read_bytes()
	decoded, fixed = scoredat.repair(scoredat.decode(raw))
	if not fixed:
		print(f"{path}: nothing to repair")
		return
	encoded = scoredat.encode(decoded)
	if scoredat.decode(encoded)[scoredat.HEADER_SIZE:] != decoded[scoredat.HEADER_SIZE:]:
		sys.exit(f"{path}: re-encoding failed its round trip, file left as is")
	path.with_name(path.name + ".bak").write_bytes(raw)
	path.write_bytes(encoded)
	print(f"{path}: unlocked {fixed} cleared or scored Practice entries (old file: {path.name}.bak)")


if __name__ == "__main__":
	args = sys.argv[1:]
	if "--repair" in args:
		args.remove("--repair")
		repair(args[0])
		sys.exit()
	out = args[args.index("--patterns") + 1] if "--patterns" in args else None
	main(args[0], out)
