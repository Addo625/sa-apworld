# 20: Continues design D: a continue triggers a penalty

Status: deferred
Blocked by: 12, 13, 14

## Problem
Option D from planning: each continue costs something. Either a trap fires (from 13) or a DeathLink goes out (from 14).

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Option:** `continue_penalty` = none/trap/deathlink (default none).
- **On a continues-used increment:**
  - trap → one random trap from the enabled weights fires (13's `traps.py`).
  - deathlink → a death is sent, which doesn't count toward amnesty (14).
- Tests: `test_penalty_trap_fires_once_per_continue`, `test_penalty_deathlink_sent`, `test_penalty_none`.

## Steps
1. Option, then the hook in the client loop calling the 13/14 logic, with tests.

## Deferred
- None.
