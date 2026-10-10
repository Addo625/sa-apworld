# 28: Received Next Stage, Lower Difficulty and shot types unlock Practice

Status: ready-for-agent
Blocked by: 08, 27

## Problem
08 tracks these items but can't apply them: the practice-unlock data was unknown. 26 decoded its layout and 27 found it in memory. This ticket writes it.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **`Variables.py`:** `ADDR_PRACTICE_UNLOCK` from 27's matches. Use a pointer chain if the match moved between M1 and M2. Source comment `probe 27`.
- **`items.apply`:**
  - `Next Stage` → the practice-progress fields for every unlocked shot type at every unlocked difficulty, stages ≤ count + 1.
  - `Lower Difficulty` → the unlocked difficulties.
  - Shot type → that shot's rows.
  - Tests: `test_apply_next_stage_writes_unlock_rows`, `test_apply_lower_difficulty`, `test_apply_shot_type`, and the replay test from 08 extended to these items.
- **Pending replay:** items received before this ticket (tracked by 08) are applied on connect.

## Steps
1. Add the address, with a fixture from 27's output. Green.
2. Write the item rules and tests, and remove 08's "pending unlock table" path. Run the DoD.

## Deferred
- In-game proof: ticket 09's smoke run covers it.
