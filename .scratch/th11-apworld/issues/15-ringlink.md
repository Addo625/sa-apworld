# 15: RingLink (power sharing)

Status: deferred
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
