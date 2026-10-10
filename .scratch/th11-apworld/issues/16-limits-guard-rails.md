# 16: Lives limit and menu guard rails

Status: ready-for-agent
Blocked by: 09

## Problem
EoSD has `limit_lives` (a client-side cap) and a guard rail that keeps the player from picking locked characters, shots or difficulties in the menus. Without the guard rail, players can play content they haven't unlocked yet, and the client would then send checks they shouldn't get. This needs the menu and cursor addresses.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Option:** `limit_lives` (0–max), changeable with `/limits`. Test: `items.apply('+1 Life')` respects the limit.
- **`guard.correct(menu_state, unlocked)`** → a corrected cursor, or None.
  - A locked difficulty or shot under the cursor → move to the nearest unlocked one.
  - Tests per menu.
- **Detection:** locations are not sent while playing a locked shot or difficulty. Test: `test_detect_ignores_locked_shot`.
- **Human:** add a `ready-for-human` ticket at promotion: try to select a locked shot and difficulty.

## Steps
1. `limit_lives`, with tests.
2. Confirm the menu and cursor addresses exist. Create a human probe ticket if they don't.
3. The guard and the locked-content detection filter, with tests. Wire them into the client loop.

## Deferred
- None.

## Comments

- 2026-10-10 planner: promoted by the human after 09 passed. Written before 06/07 findings; use the current code: `ADDR_MENU_PTR` (not a game mode), in a stage = `ADDR_ENEMY_MANAGER` ≠ 0, boss = `ADDR_IS_BOSS_PRESENT`, power in 0.05 units (max 80). If an address this ticket needs is unsourced (e.g. Extra unlock, menu/continue sites), implement everything else, then set `needs-human` naming the probe needed.
