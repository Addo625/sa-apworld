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

- 2026-10-12 Claude (from batch 32): the difficulty guard works but feels broken. Writing `ADDR_MENU_CURSOR` back every 0.5 s poll lets the cursor reach a locked difficulty for a moment before it snaps back, so the human saw it "move only sometimes, as if locked". Prefer blocking the move: patch the menu's cursor bounds or skip-locked check, as MoF's cursor hack does, through `safe_patch` with `EXPECTED_BYTES`, and keep the snap as a fallback. Apply the same to the shot guard (menu 3, cursor = shot, from R6-M1).
- 2026-10-12 planner, **from batch 32 R6:**
  - Character select = menu 2 (cursor 0 = Reimu, 1 = Marisa). Shot select = **menu 3, cursor = shot index 0/1/2 (A/B/C)**, for the character highlighted. `ADDR_SHOT_TYPE` only changes on confirm, so the guard must read the cursor, not `ADDR_SHOT_TYPE`. Set `Variables.MENU_SHOT = 3`.
  - M2 confirmed the difficulty snap works (see the UX note above).
  - **Also (human request):** when a run starts on a shot type or difficulty that isn't received, log one client line, e.g. `Reimu A isn't unlocked: this run sends no checks`, so a player knows why nothing is sent (M3: a locked Reimu A run sent nothing silently). `test_locked_run_logs_once`.
