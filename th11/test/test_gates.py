import unittest

from ..Rules import stage_requirements

BIG = [100] * 6
MAX = (8, 8, 3)


def ramp(mid, end, rooms=BIG):
	return stage_requirements(mid, end, rooms)[0]


class TestStageRequirements(unittest.TestCase):
	def test_ramp_defaults(self):
		self.assertEqual(stage_requirements((0, 0, 0), (0, 0, 0), [-3, 2, 7, 12, 15, 20]), ([(0, 0, 0)] * 6, []))

	def test_ramp_max(self):
		self.assertEqual(ramp(MAX, MAX), [(0, 0, 0)] * 2 + [(4, 4, 1)] + [(8, 8, 3)] * 3)

	def test_ramp_end_below_mid(self):
		self.assertEqual(ramp((6, 4, 2), (2, 0, 1))[2:], [(3, 2, 1), (6, 4, 2), (4, 2, 1), (2, 0, 1)])

	def test_luck_rounds_only_difficulty_up(self):
		"""71: Hard/Normal without Lunatic is 0/1 Lower Difficulty: Stage 5 expects Normal with luck, Hard without;
		odd lives (mid 3) still round down."""
		plain = stage_requirements((3, 0, 0), (4, 0, 1), BIG)[0]
		lucky = stage_requirements((3, 0, 0), (4, 0, 1), BIG, round_up=True)[0]
		self.assertEqual([req[2] for req in plain], [0, 0, 0, 0, 0, 1])
		self.assertEqual([req[2] for req in lucky], [0, 0, 0, 0, 1, 1])
		self.assertEqual([req[0] for req in lucky], [req[0] for req in plain])  # lives 0, 0, 1, 3, 3, 4
		self.assertEqual(stage_requirements((0, 0, 1), (0, 0, 1), BIG, round_up=True)[0][2][2], 1)  # stage 3: (1+1)//2

	def test_ramp_extra(self):
		reqs = stage_requirements(MAX, MAX, [100] * 7, (5, 2, 0))[0]
		self.assertEqual(reqs[6], (5, 2, 0))
		self.assertEqual(len(stage_requirements(MAX, MAX, BIG, (5, 2, 0))[0]), 6)

	def test_clamp_largest_first(self):
		rooms = [100, 100, 100, 5, 100, 100]
		self.assertEqual(ramp((2, 5, 0), (2, 5, 0), rooms=rooms)[3], (2, 3, 0))
		# Ties go lives, then power.
		self.assertEqual(ramp((3, 3, 0), (3, 3, 0), rooms=rooms)[3], (2, 3, 0))

	def test_clamp_difficulty_last(self):
		self.assertEqual(ramp((1, 1, 3), (1, 1, 3), rooms=[100, 100, 100, 2, 100, 100])[3], (0, 0, 2))

	def test_clamp_notes(self):
		_, notes = stage_requirements((1, 1, 3), (1, 1, 3), [100, 100, 100, 2, 100, 100])
		self.assertEqual(len(notes), 3)
		self.assertTrue(all(note.startswith("Stage 4") for note in notes))
		self.assertEqual([note.split()[3] for note in notes], ["lives", "power", "difficulty"])

	def test_no_clamp_when_room_suffices(self):
		self.assertEqual(stage_requirements(MAX, MAX, BIG)[1], [])
