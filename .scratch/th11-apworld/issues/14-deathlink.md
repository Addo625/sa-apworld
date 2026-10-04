# 14: DeathLink

Status: deferred
Blocked by: 09

## Problem
EoSD supports DeathLink with `death_link_trigger` (on a life lost or on game over) and `death_link_amnesty` (deaths before one is sent). MoF never implemented it. Both directions are needed: our deaths go out, and a death coming in kills the player.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Options:** `death_link` (common), `death_link_trigger`, `death_link_amnesty`. Exposed in `slot_data`, and changeable from the client by command, as in EoSD.
- **`deathlink.on_state(prev, state, cfg)`** → send / no send.
  - Lives drop → counts toward amnesty.
  - Game over with trigger=game_over → send.
  - No send on a menu exit.
  - Tests for each.
- **Incoming death:** kill the player with EoSD's kill approach (a code site through `safe_patch`, or lives=0 plus a hit, whichever 06/probe shows works). Only while in game; queued otherwise. A death caused by the incoming link is never echoed back out.
- **Human:** add a `ready-for-human` ticket at promotion: two clients, one death each way.

## Steps
1. Options and the pure logic, with tests.
2. Find and verify the kill mechanism. Create a human probe ticket if the address is unknown.
3. Wire into the client with the tag handling (`DeathLink` tag), plus the no-echo test.

## Deferred
- None.
