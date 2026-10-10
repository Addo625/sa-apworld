#!/usr/bin/env python3
"""Print a decoded scoreth11.dat: chunks, practice progress per character, and a /memsearch pattern.
Usage: tools/scoredat.py .games/sa/scoreth11.dat"""
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


def main(path):
	decoded = scoredat.decode(Path(path).read_bytes())
	print(f"decoded {len(decoded)} bytes (header 0x{scoredat.HEADER_SIZE:X})")
	pattern = None
	for signature, offset, size, body in scoredat.chunks(decoded):
		print(f"{signature} at 0x{offset:05X} size 0x{size:X}")
		if signature != "CR":
			continue
		print(f"  {scoredat.chara(body)} (unlocked, cleared, score) per stage:")
		for level, stages in scoredat.practice_progress(body).items():
			print(f"    {level:8}" + " ".join(f"{stage}:{u}/{c}/{s}" for stage, (u, c, s) in stages.items()))
		pattern = pattern or unique_pattern(decoded, offset)
	if pattern:
		print(f"/memsearch {pattern.hex()}  (first CR chunk's practice table, {len(pattern)} bytes, unique in file)")
	else:
		print("no unique practice-table pattern found")


if __name__ == "__main__":
	main(sys.argv[1])
