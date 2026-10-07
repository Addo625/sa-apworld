import unittest

from ..Rules import stage_requirements

BIG = [100] * 6
MAX = (8, 8, 3)


def ramp(mid, end, keys=0, rooms=BIG):
	return stage_requirements(mid, end, keys, rooms)[0]


class TestStageRequirements(unittest.TestCase):
	def test_ramp_defaults(self):
		self.assertEqual(stage_requirements((0, 0, 0), (0, 0, 0), 0, [-3, 2, 7, 12, 15, 20]), ([(0, 0, 0, 0)] * 6, []))

	def test_ramp_max(self):
		self.assertEqual(ramp(MAX, MAX), [(0, 0, 0, 0)] * 2 + [(4, 4, 1, 0)] + [(8, 8, 3, 0)] * 3)

	def test_ramp_end_below_mid(self):
		self.assertEqual(ramp((6, 4, 2), (2, 0, 1))[2:], [(3, 2, 1, 0), (6, 4, 2, 0), (4, 2, 1, 0), (2, 0, 1, 0)])

	def test_ramp_keys(self):
		self.assertEqual([req[3] for req in ramp((0, 0, 0), (0, 0, 0), keys=9)], [0, 0, 2, 4, 6, 9])

	def test_clamp_largest_first(self):
		rooms = [100, 100, 100, 5, 100, 100]
		self.assertEqual(ramp((2, 5, 0), (2, 5, 0), rooms=rooms)[3], (2, 3, 0, 0))
		# Ties go lives, then power.
		self.assertEqual(ramp((3, 3, 0), (3, 3, 0), rooms=rooms)[3], (2, 3, 0, 0))
		# Keys count toward the room and are cut last on a tie.
		self.assertEqual(ramp((2, 2, 0), (2, 2, 0), keys=4, rooms=[100, 100, 100, 4, 100, 100])[3], (1, 1, 0, 2))

	def test_clamp_difficulty_last(self):
		self.assertEqual(ramp((1, 1, 3), (1, 1, 3), rooms=[100, 100, 100, 2, 100, 100])[3], (0, 0, 2, 0))

	def test_clamp_notes(self):
		_, notes = stage_requirements((1, 1, 3), (1, 1, 3), 0, [100, 100, 100, 2, 100, 100])
		self.assertEqual(len(notes), 3)
		self.assertTrue(all(note.startswith("Stage 4") for note in notes))
		self.assertEqual([note.split()[3] for note in notes], ["lives", "power", "difficulty"])

	def test_no_clamp_when_room_suffices(self):
		self.assertEqual(stage_requirements(MAX, MAX, 0, BIG)[1], [])
