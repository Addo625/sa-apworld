import unittest

from ..Locations import location_table
from ..tracker import location_stage, report

# Playtest1's gates: stages 3-4 lives 1-2, power 1-2, Hard; 5-6 up to 4/4, Normal.
SLOT = {"mode": 0, "stage_unlock": 0, "progressive_stage": 1, "stage_requirements": [
	[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 0], [2, 2, 1, 0], [3, 3, 1, 0], [4, 4, 2, 0]]}
MARISA = [name for name in location_table if name.startswith("[Marisa] ") and "Capture" not in name]


def stage_line(lines, shot, stage):
	start = next(i for i, line in enumerate(lines) if line.startswith(shot))
	return next(line for line in lines[start:] if line.strip().startswith(f"Stage {stage}:"))


class TestTracker(unittest.TestCase):
	def test_fresh_start_opens_stage_1_only(self):
		lines = report(["Marisa C - Nitori"], MARISA, SLOT)
		self.assertIn("OPEN", stage_line(lines, "Marisa C", 1))
		self.assertIn("LOCKED, needs Next Stage 0/1", stage_line(lines, "Marisa C", 2))

	def test_open_stage_with_unmet_gate_is_playable(self):
		lines = report(["Marisa C - Nitori", "Next Stage", "Next Stage", "+1 Life"], MARISA, SLOT)
		line = stage_line(lines, "Marisa C", 3)
		self.assertIn("PLAYABLE", line)
		self.assertIn("+0.50 Power 0/1", line)
		self.assertIn("Hard: Lower Difficulty 0/1", line)
		self.assertNotIn("+1 Life", line)

	def test_met_gate_is_open(self):
		items = ["Marisa C - Nitori", "Next Stage", "Next Stage", "+1 Life", "+0.50 Power", "Lower Difficulty"]
		self.assertIn("Stage 3: OPEN", stage_line(report(items, MARISA, SLOT), "Marisa C", 3))

	def test_checks_left_drop_when_checked(self):
		line = lambda missing: stage_line(report(["Marisa C - Nitori"], missing, SLOT), "Marisa C", 1)
		self.assertIn("left: 3 boss checks", line(MARISA))
		self.assertIn("left: 2 boss checks", line([name for name in MARISA if name != "[Marisa] Kisume - Midboss"]))
		self.assertIn("left: 3 boss checks, 1 capture", line(MARISA + ["[Marisa] Stage 1 - Capture 1"]))
		self.assertIn("all checked", line([]))

	def test_goal_line(self):
		self.assertIn("not yet", report([], [], SLOT)[0])
		self.assertIn("DONE", report(["[Marisa] Ending - Utsuho"], [], SLOT)[0])

	def test_location_stage(self):
		self.assertEqual(location_stage("[Hard][Marisa C] Parsee Defeated"), ("Marisa C", 2, False))
		self.assertEqual(location_stage("[Reimu] Stage Extra Clear"), ("Reimu", 7, False))
		self.assertEqual(location_stage("Stage 3 - Capture 2"), (None, 3, True))
		self.assertEqual(location_stage("[Marisa] Cat Orin - Second Appearance"), ("Marisa", 4, False))
