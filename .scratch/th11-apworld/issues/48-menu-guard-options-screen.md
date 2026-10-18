# 48: The menu guard must leave the Options screen alone

Status: ready-for-agent
Blocked by: 58

## Problem
Batch 44 (human): while connected, the guard (16/38) also forces the cursor on the **Options** screen (volume and similar), not only on the difficulty and shot selects. It keys on the menu id alone (difficulty = 1, shot = 3), and the Options screen evidently uses one of those ids.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_guard_ignores_options_screen`.

## Test plan
- From batch 50 R1, find what tells the Options screen apart: its `ADDR_MENU`/cursor values, and any field (e.g. `ADDR_MENU_PTR`, `ADDR_GAME_FLAGS`, a parent-menu id) that differs from the difficulty and shot selects.
- `guard.correct` returns `None` on the Options screen. `test_guard_ignores_options_screen` uses a fixture from R1's probe; the existing guard tests stay green.

## Steps
1. Read R1, add the distinguishing condition and the test. Run the DoD.

## Deferred
- None.

## Comments
- 2026-10-18 Claude: batch 50 R1: Options reads `ADDR_MENU = 1`, cursor 3, `ADDR_GAME_FLAGS = 4`. The flag doesn't help: `th11.exe` sets bit 4 when the score passes the high score (`0x41EF9F`: `or eax,4` after `cmp [0x4A56E0],eax`) and clears it at run start (`0x41FAA4`), so it's leftover state, not a screen id (the character select's 4 in probe 06 is the same leftover, or another of its setters). Next: batch 58 R1 dumps the menu object on each screen. Then, in `guard.correct`, return `None` when the distinguishing field says Options, plus `test_guard_ignores_options_screen` built from R1's dump.
