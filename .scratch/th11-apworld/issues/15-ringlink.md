# 15: RingLink (power sharing)

Status: ready-for-agent
Blocked by: 09

## Problem
EoSD and MoF link power gains and losses across players through RingLink.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Option:** `ring_link`, toggleable from the client (`/ringlink`), as in EoSD.
- **`ringlink.delta(prev_power, power)`** → the amount to send, in RingLink units with the MoF conversion.
  - Power from our own items or traps is not sent.
  - Tests for each.
- **Incoming:** power changes, capped and floored, only in game. Incoming deltas are not echoed. Tests for each.

## Steps
1. Option and the pure logic, with tests.
2. Client wiring: the `RingLink` tag, the bounce handler, and source-id filtering per the RingLink protocol MoF uses.

## Deferred
- None.

## Comments

- 2026-10-10 planner: promoted by the human after 09 passed. Written before 06/07 findings; use the current code: `ADDR_MENU_PTR` (not a game mode), in a stage = `ADDR_ENEMY_MANAGER` ≠ 0, boss = `ADDR_IS_BOSS_PRESENT`, power in 0.05 units (max 80). If an address this ticket needs is unsourced (e.g. Extra unlock, menu/continue sites), implement everything else, then set `needs-human` naming the probe needed.
