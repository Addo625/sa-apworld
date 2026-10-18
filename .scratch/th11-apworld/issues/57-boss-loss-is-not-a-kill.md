# 57: Losing to a boss doesn't send its Defeated and Clear checks

Status: ready-for-agent
Blocked by: 58

## Problem
Batch 50 R3 (a normal Start run, Normal difficulty): losing at Parsee sent `[Marisa] Parsee Defeated` and `[Marisa] Stage 2 Clear`. In a Practice seed, 55 now ignores such runs, but normal-mode seeds still count a boss leaving at a game over or continue as a kill.

## What to do
- Find what the state looks like at that moment (lives -1? continue screen? `ADDR_MENU_PTR` set?). `detect.step` already treats `lives == -1` and a menu as a quit; the boss field must be dropping in a state that passes both. If the logs don't show it, ask for a `/probe` at the continue screen through the probe batch.
- Make `step` return no locations for it; a test with that state.

## Deferred
- None.
