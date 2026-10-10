# 38: Turn on the shot select guard

Status: ready-for-agent
Blocked by: 32

## Problem
16 built the menu guard rail. The difficulty select guard is on (menu 1, probe 06 S1). The shot select guard is built but off (`Variables.MENU_SHOT = None`): probe 06 S2 saw character select as menu 3 with cursor 1 on Marisa B, which doesn't tell whether the cursor picks the shot (A/B/C) or the character. Until it's on, a player can still pick a locked shot type. That run sends no checks (16's detection filter), but the player only finds that out after playing it. Probe batch 32 R6 answers the cursor question and checks that a cursor write moves the selection.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_shot_menu_from_probe`.

## Test plan
- **Read from 32's comments, R6:** M1 (menu id and cursor per screen: character, shot), M2 (does the difficulty cursor write move the highlight and the confirmed difficulty), M3 (the same for the shot screen).
- **The cursor is the shot of `ADDR_CHARACTER`** (16's default): set `Variables.MENU_SHOT` to that menu id, `# source: probe 32 R6 M1`. `test_shot_menu_from_probe` (in `test_guard.py`): `correct` with the probed menu id and no `shot_menu` argument moves a locked shot's cursor to the nearest unlocked one.
- **The cursor picks the character, and the shot is a separate screen:** use that screen's id as `MENU_SHOT`. If the character screen offers a character with no unlocked shot, also move its cursor to the other character in `correct`, with a test.
- **M2 says a cursor write doesn't move the selection:** the guard needs the cursor-hack approach (MoF `initCursorHack`, minimum cursor patch sites): note that in `.agent-loop/HUMAN.md` and turn this into a `needs-human` plan question instead of guessing addresses.
- If R6 is "not reached" or ambiguous: leave `MENU_SHOT = None`, add a narrower request to the open probe batch, close this ticket per AGENTS.md.

## Steps
1. Set `MENU_SHOT` from R6 (or extend `correct` per the cases above) and add the test. Run the DoD.

## Deferred
- None.
