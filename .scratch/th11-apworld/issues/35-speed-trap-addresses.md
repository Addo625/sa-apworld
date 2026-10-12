# 35: Source the speed fields so speed traps work

Status: ready-for-agent
Blocked by: 32

## Problem
13 built the speed traps (No Focus, Reverse Movement, Aya Speed, Freeze) against `ADDR_SPEED_NORMAL`, `ADDR_SPEED_FOCUS`, `ADDR_SPEED_NORMAL_D`, `ADDR_SPEED_FOCUS_D`, which are `None`: the client logs "pending the speed addresses" and drops those traps. Probe batch 32 R3 finds the fields.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_speed_entries_from_probe`.

## Test plan
- **Read from 32's comments, R3:** P1/P2 `/playerfloats` dumps (offset → float per shot type), P3's poke result.
- **`Variables.py`:** each `ADDR_SPEED_*` = `[ADDR_PLAYER_PTR, offset]`, `# source: probe 32 R3 P1/P2`. Order: normal, focus, normal diagonal, focus diagonal (`traps.SPEED_ENTRIES`). If SA has no diagonal fields, say so in the commit and shrink `SPEED_ENTRIES` / `trapped_speeds` to the fields that exist.
- **`test_speed_entries_from_probe`** (in `test_traps.py`): a `FakeMemory` holding P1's player object at a fake pointer; `read_float` on each entry returns P1's values; `tick` with "Freeze" then expiry writes zeros, then P1's values, at those addresses.
- **Leaving a run:** `traps.tick` forgets an active speed trap without restoring (EoSD; the player object may be gone), assuming each stage rebuilds the speeds. Add that check to the open probe batch: during a Reverse Movement, clear the stage (or die to game over) and check movement is normal in the next stage/run. If it isn't, restore on the first in-run tick instead, with a test.
- If R3 is "not reached" or ambiguous: leave the entries `None`, add a narrower request to the open probe batch, and close this ticket per AGENTS.md.

## Steps
1. Fill the entries from R3 and add the test. Run the DoD.
2. Update 32 R4's note (or the next batch) so the human sends the four speed traps once.

## Deferred
- None.

## Comments
- 2026-10-12 planner, **from batch 32 R3: inconclusive.** `/playerfloats` lists every speed-like float in 4 KB of the player object (~85 each for Reimu A and Marisa B), mostly options and bullets. No clear normal/focus/diagonal set. Differences: `+0x84/+0x8C/+0x94/+0x9C` (0.12 → 0.88/0.99), `+0x8E4/+0x8E8` (1 → 1.75). Change the method:
  1. statically find the per-shot speed table (6 shots × normal/focus floats in `.rdata`) and the code copying it into the player;
  2. **and/or** add `/playerfloats diff` (one snapshot while moving unfocused, one while focused; print only the floats that changed between them).

  Then add a batch 44 request (two snapshots, plus one `/poke` confirm), and keep the speed traps pending until then.
