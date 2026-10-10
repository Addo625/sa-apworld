import contextlib
import importlib.util
import io
import struct
import unittest
from pathlib import Path

from .. import scoredat

ROOT = Path(__file__).resolve().parents[2]
SAVE = ROOT / ".games/sa/scoreth11.dat"


def chunk(signature: bytes, data: bytes) -> bytes:
	size = scoredat.CHUNK_HEADER_SIZE + len(data)
	tail = struct.pack("<i", size) + data
	return struct.pack("<2sHI", signature, 0, sum(tail)) + tail


class TestScoredat(unittest.TestCase):
	def test_scoredat_chunks_roundtrip(self):
		clear = bytearray(scoredat.CLEAR_SIZE - scoredat.CHUNK_HEADER_SIZE)
		struct.pack_into("<i", clear, 0, 3)  # MarisaAlice
		hard_stage_2 = scoredat.PRACTICE_OFFSET - scoredat.CHUNK_HEADER_SIZE + (2 * len(scoredat.STAGES) + 1) * scoredat.PRACTICE_SIZE
		struct.pack_into("<IBB", clear, hard_stage_2, 12345, 1, 1)
		first, second = chunk(b"CR", bytes(clear)), chunk(b"ST", b"\x01\x02\x03\x04")
		decoded = bytes(scoredat.HEADER_SIZE) + first + second
		parsed = scoredat.chunks(decoded)
		self.assertEqual([(s, o, n) for s, o, n, _ in parsed], [
			("CR", scoredat.HEADER_SIZE, len(first)),
			("ST", scoredat.HEADER_SIZE + len(first), len(second)),
		])
		self.assertEqual(parsed[1][3], second)
		self.assertEqual(scoredat.chara(parsed[0][3]), "MarisaAlice")
		progress = scoredat.practice_progress(parsed[0][3])
		self.assertEqual(progress["Hard"][2], (1, 1, 123450))
		self.assertEqual(progress["Hard"][1], (0, 0, 0))
		self.assertEqual(sorted(progress), sorted(scoredat.LEVELS))

	def test_scoredat_rejects_bad_checksum(self):
		bad = bytearray(chunk(b"ST", b"\x01\x02"))
		bad[-1] ^= 0xFF
		with self.assertRaises(ValueError):
			scoredat.chunks(bytes(scoredat.HEADER_SIZE) + bad)

	@unittest.skipUnless(SAVE.exists(), "no local save (.games is gitignored)")
	def test_scoredat_decode_real_file(self):
		decoded = scoredat.decode(SAVE.read_bytes())
		self.assertEqual(decoded[:4], b"TH11")
		parsed = scoredat.chunks(decoded)
		self.assertEqual(scoredat.HEADER_SIZE + sum(size for _, _, size, _ in parsed), len(decoded))
		clears = [body for signature, _, _, body in parsed if signature == "CR"]
		self.assertEqual([scoredat.chara(body) for body in clears], scoredat.CHARAS)

	@unittest.skipUnless(SAVE.exists(), "no local save (.games is gitignored)")
	def test_scoredat_tool_prints_real_file(self):
		spec = importlib.util.spec_from_file_location("scoredat_tool", ROOT / "tools/scoredat.py")
		tool = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(tool)
		out = io.StringIO()
		with contextlib.redirect_stdout(out):
			tool.main(SAVE)
		print(out.getvalue())  # pytest -s shows it
		self.assertIn("/memsearch ", out.getvalue())
