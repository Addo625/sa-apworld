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

## Comments
- 2026-10-12 planner, **from batch 32 R1: the save-flag hypothesis failed.** Decoding both saves showed `ST+0x2C..0x31` as `00` in `fresh` and `01` in `sa` (everything unlocked). But poking those 6 bytes, then 12 (`+0x2C..0x37`), to `01` in both live copies didn't make Extra Start appear, even after returning to the title. Before asking for another game session, **find what the Extra menu actually checks by static analysis** of `.games/sa/th11.exe`:
  - start from thcrap's `fix_extra_stage_relocking` patch site (`Rx ede8` = `0x4EDE8`, in `.games/sa/thcrap/repos/nmlgc/base_tsa/th11.v1.00a.js`) and the code reading the save struct behind `0x4A8EBC`;
  - capstone in a pytest scratch, per the repo's disassembly note.

  Then add one request to probe batch 44 with the exact poke and the expected menu result (AGENTS.md batch rule).
