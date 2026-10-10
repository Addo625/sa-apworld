"""
Location detection: compares two decoded GameStates. Pure, no memory access.
"""
from .Locations import location_table
from .Variables import STAGE4_APPEARANCES, STAGES_LIST


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


def step(prev, state, runs=0):
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
	return [location_table[f"[{state.character}] {name}"] for name in names], runs + 1
