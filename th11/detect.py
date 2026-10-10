"""
Location detection: compares two decoded GameStates. Pure, no memory access.
"""
from .Locations import location_table
from .Variables import DIFFICULTY_LIST, STAGE4_APPEARANCES, STAGES_LIST, lowest_unlocked


def run_checks(stage):
	"""Checks sent when each boss-field run of a stage ends, the last one with the clear."""
	checks = STAGES_LIST[stage - 1]
	if stage == 3:  # Yuugi stays from midboss into boss: one run. Ticket 22 splits it by spell ID.
		runs = [checks]
	elif stage == 4:  # Two cat-Orin runs (ticket 25), then Satori.
		runs = [[check] for check in STAGE4_APPEARANCES] + [checks]
	else:
		runs = [[check] for check in checks]
	# No tally signal: the field drops 1.7 s before the clear bonus (06 bossrec), so the last run's end is the clear.
	runs[-1] = runs[-1] + [f"Stage {'Extra' if stage == 7 else stage} Clear"]
	return runs


def location_names(state, names, slot_data, lower):
	"""Run check names -> location names for this character or shot type, and difficulty (slot_data options).
	lower: Lower Difficulty items received; check_multiple_difficulty also sends every unlocked lower difficulty."""
	owner = state.shot if slot_data.get("shot_type") else state.character
	if not slot_data.get("difficulty_check") or state.stage not in range(1, 7):  # Extra has no difficulty checks
		return [f"[{owner}] {name}" for name in names]
	difficulties = []
	if state.difficulty in range(4):
		lowest = state.difficulty
		if slot_data.get("check_multiple_difficulty"):
			lowest = min(lowest, lowest_unlocked(lower, slot_data.get("exclude_lunatic")))
		difficulties = DIFFICULTY_LIST[lowest:state.difficulty + 1]
	located = []
	for name in names:  # clears stay per owner
		located += [f"[{owner}] {name}"] if name.endswith(" Clear") else [f"[{d}][{owner}] {name}" for d in difficulties]
	return located


def step(prev, state, runs=0, slot_data=None, lower=0):
	"""-> (location IDs, boss runs ended so far this stage). Pass the returned runs to the next call."""
	if not prev.in_game or prev.stage != state.stage:
		runs = 0
	ended = prev.boss_present and not state.boss_present
	# A drop with a menu exit (S9) or a game over is a quit, not a kill.
	if not ended or not state.in_game or state.menu is not None or state.lives == -1:
		return [], runs
	if state.stage not in range(1, 8) or state.character is None:
		return [], runs + 1
	# ponytail: a midboss that leaves on its timer counts as beaten; add a defeat signal (HP, spell bonus) if that matters.
	checks = run_checks(state.stage)
	names = checks[runs] if runs < len(checks) else []
	return [location_table[name] for name in location_names(state, names, slot_data or {}, lower)], runs + 1
