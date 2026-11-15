"""
Location detection: compares two decoded GameStates. Pure, no memory access.
"""
from .Locations import location_table
from .guard import unlocked_difficulties
from .Options import Mode
from .receive import stage_open
from .state import PRACTICE_FLAG
from .Variables import DIFFICULTY_LIST, STAGE4_APPEARANCES, STAGES_LIST, lowest_unlocked


def run_checks(stage, cards=0):
	"""Checks sent when each boss-field run of a stage ends, the last one with the clear.
	cards: distinct spell cards seen during the run (Stage 3 only)."""
	checks = STAGES_LIST[stage - 1]
	if stage == 3:
		# Yuugi sometimes stays from midboss into boss (22), sometimes leaves between them (73), so any run may be
		# the last. The midboss declares one card, Yuugi three before she falls: 2+ cards seen means she fell.
		return [checks + ["Stage 3 Clear"]] if cards >= 2 else [checks[:1]]
	if stage == 4:  # Two cat-Orin runs (ticket 25), then Satori.
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


def locked(state, shots, lower, slot_data, received=None):
	"""-> the shot type, difficulty or stage the run plays that the received items don't unlock, or None.
	received: the item names; None skips the stage check (52/45)."""
	if state.shot not in shots:
		return state.shot or "this shot type"
	if state.difficulty in range(4) and state.difficulty not in unlocked_difficulties(lower, slot_data):
		return DIFFICULTY_LIST[state.difficulty]
	if received is not None and state.stage in range(1, 8) and not stage_open(received, slot_data, state.shot, state.stage):
		return f"{state.shot} Stage {'Extra' if state.stage == 7 else state.stage}"
	return None


def voided(state, stage_continues, slot_data):
	"""A continue used in this stage of a Practice seed's Start run (87): the stage's checks wait for a clear without
	one, as a Practice retry restarts the stage. stage_continues: the continues count when the stage began; None (or
	an unreadable count) voids nothing. Normal-mode seeds keep unlimited continues (18-20 deferred)."""
	return (slot_data.get("mode", Mode.option_practice) == Mode.option_practice and state.stage in range(1, 7)
		and state.flags is not None and not state.flags & PRACTICE_FLAG
		and None not in (state.continues, stage_continues) and state.continues > stage_continues)


def restarted(prev, state):
	"""A Practice run restarted without leaving play (batch 61): Retry at a game over (lives come back from -1) or
	Give up and Retry (the score drops). Practice only: a normal-mode continue also restores lives, but play goes on."""
	if not (prev.in_game and state.in_game and state.flags is not None and state.flags & PRACTICE_FLAG):
		return False
	if prev.lives == -1 and state.lives is not None and state.lives >= 0:
		return True
	return prev.score is not None and state.score is not None and state.score < prev.score


def step(prev, state, runs=0, slot_data=None, lower=0, shots=None, received=None, stage_continues=None, cards=0,
	card_ended=False):
	"""-> (location IDs, boss runs ended so far this stage). Pass the returned runs to the next call.
	shots: unlocked shot types; a run on a locked shot or difficulty sends nothing. None: don't check (not connected).
	stage_continues: the continues count when this stage began (see voided). cards: see run_checks.
	card_ended: the spell card active last poll has ended."""
	restart = restarted(prev, state)
	if not prev.in_game or prev.stage != state.stage or restart:
		runs = 0
	ended = prev.boss_present and not state.boss_present
	# Yuugi stays on the field from midboss into boss (batch 74 R1): her midboss ends with the run's first card, killed
	# or timed out alike. Only its own check goes out; the field drop sends the rest.
	midboss = state.stage == 3 and prev.boss_present and state.boss_present and card_ended and cards == 1
	# A drop with a menu exit (S9), at or right after a game over (61 R4: lives -1 with the boss still up), or on a
	# retry is a quit, not a kill.
	if not (ended or midboss) or not state.in_game or state.menu is not None or -1 in (state.lives, prev.lives) or restart:
		return [], runs
	counted = runs + 1 if ended else runs
	if state.stage not in range(1, 8) or state.character is None:
		return [], counted
	if shots is not None and locked(state, shots, lower, slot_data or {}, received):
		return [], counted
	if voided(state, stage_continues, slot_data or {}):
		return [], counted
	# ponytail: a midboss that leaves on its timer counts as beaten (74 R1: a timed-out Yuugi midboss looks like a kill);
	# add a defeat signal (HP, spell bonus) if that matters.
	return run_locations(state, runs, slot_data or {}, lower, cards), counted


def run_locations(state, run, slot_data, lower, cards=0):
	"""Location IDs for the run-th boss-field run of state's stage ending (Stage 3 goes by cards, not the index)."""
	checks = run_checks(state.stage, cards)
	names = checks[0] if state.stage == 3 else checks[run] if run < len(checks) else []
	return [location_table[name] for name in location_names(state, names, slot_data, lower)]
