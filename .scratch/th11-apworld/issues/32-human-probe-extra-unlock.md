# 32: [human] Find where SA stores the Extra unlock per shot type

Status: ready-for-human
Blocked by: 09

## Problem
11 needs `items.apply('Extra Stage')` to open the Extra stage, but `ADDR_EXTRA_UNLOCK` in `th11/Variables.py` is still `None` (`TODO(06)`). The only lead is thcrap's `fix_extra_stage_relocking` patch at `Rxede8` (a code site, not the flag itself). The Practice table found in 27 has no Extra row (`th11/scoredat.py`: levels Easy–Lunatic, stages 1–6), so the flag lives somewhere else in the save struct or is derived from clear data.

## DoD
`## Comments` holds: what decides that a shot type is offered Extra (a save field, a derived clear count, or code at `th11.exe+0xede8`), its location relative to 27's save struct or a static pointer, and one before/after observation that proves it (Extra offered vs. not offered for the same shot).

## Test plan
- **E1:** with a save where at least one shot has Extra and one doesn't, run `tools/scoredat.py` and paste the `CR` chunk's clear counts per shot (the 5 counts after play time; the 5th level is Extra).
- **E2:** in the running game, `/memsearch` the save struct around 27's copy 1 (`…1BB8`) for the field E1 points at; paste matches.
- **E3:** change that byte (with 28's `/poke`, once it exists, or a memory editor) for a shot without Extra, open the Extra menu, and note whether the shot is now offered.

## Steps
1. Do E1–E3 and paste the output under `## Comments`. Set `Status: done`.
2. Then relabel 11 `ready-for-agent`: it sets `ADDR_EXTRA_UNLOCK` and writes it on `Extra Stage`.

## Deferred
- None.

## Comments
