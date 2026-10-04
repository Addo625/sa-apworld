# 13: Traps

Status: deferred
Blocked by: 09

## Problem
EoSD swaps a percentage of filler for weighted traps. The SA-relevant subset is: `-50% Power`, `-1 Life`, `No Focus`, `Reverse Movement`, `Aya Speed`, `Freeze`, `Power Drain`. Max Rank and -1 Bomb are dropped because SA has no rank and no bomb stock.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Generation:**
  - `traps` (0–100 % of filler) and one weight option per trap.
  - `test_traps_zero_none`, `test_traps_100_all_filler_are_traps`, `test_trap_weights_zero_excluded`.
- **Client** (pure, `traps.py`, following EoSD/MoF `trap_loop`):
  - `-50% Power` → power halved.
  - `-1 Life` → lives −1, floored at 0, never killing the player.
  - `Power Drain` → −0.05/s over N s.
  - `No Focus`, `Reverse Movement`, `Aya Speed` and `Freeze` → timed state with a restore at expiry. Speed addresses come from the table. They are code or data sites, and code sites go through `safe_patch`.
  - Tests for each trap: writes, then restore after expiry.
  - Traps queue while not in game and fire on entering it.
- **Human:** add a `ready-for-human` ticket at promotion to `/send` each trap once.

## Steps
1. Generation options and pool, with tests.
2. Probe and confirm the speed/focus addresses. If they are missing from 06, create a human probe ticket first and block on it.
3. `traps.py` and the client loop, with tests.

## Deferred
- None.
