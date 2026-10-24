# 84: Every trap buzzes the moment it begins

Status: done
Blocked by: None

## Problem
The human (2026-10-24): only `-1 Life` made a sound, and only because its lives write triggered one. Every trap should sound when it begins, not when it's received: a trap waits for a run, the 2 s run-start delay, or another speed trap to end.

## What to do
- `traps.tick` sets `TrapState.fired` to the trap it fired that tick. The client plays the trap sound for any fired trap: the menu buzzer `0x25`, renamed `life_lost` → `trap`. It's still gated by `/itemsound`, and played after the trap's writes so a `-1 Life`'s stars are redrawn.
- Test: `test_every_trap_buzzes_when_it_begins` (silent while No Focus waits on unreadable speeds, a buzz when it starts); the `-1 Life` test uses the new name.

## Deferred
- None.
