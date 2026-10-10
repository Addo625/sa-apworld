# 33: Received Extra Stage items unlock the Extra stage

Status: ready-for-agent
Blocked by: 11, 32

## Problem
11 built Extra (options, locations, items, goals), but `Extra Stage` is only logged as a pending unlock: `ADDR_EXTRA_UNLOCK` is `None`. Probe batch 32's R1 finds where SA stores the per-shot Extra unlock.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **`Variables.py`:** `ADDR_EXTRA_UNLOCK` from R1's answer (a save-struct offset, a static pointer chain, or the code site at `+0xEDE8`, whichever R1 proved). Source comment `probe 32 R1`.
- **`receive.apply('Extra Stage')`:** writes the unlock for the received group (global, per character, or per shot, following `stage_unlock` as 11 did). Remove 11's "pending unlock" path for it.
  - Tests: `test_apply_extra_stage_global`, `test_apply_extra_stage_per_shot`, and the replay test extended to `Extra Stage`.
- If R1 says the unlock is derived from clear counts rather than a flag, write the minimal clear data that makes the game offer Extra, and say so in the commit body.

## Steps
1. Read R1, add the entry with a fixture test. Green.
2. Write the item rule and tests. Run the DoD.

## Deferred
- In-game proof: in the next probe batch, "receive `Extra Stage`, Extra is offered".
