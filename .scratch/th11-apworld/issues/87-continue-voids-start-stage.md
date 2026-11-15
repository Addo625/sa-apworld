# 87: A continue in a Practice seed's Start run voids that stage's checks

Status: done
Blocked by: None

## Problem
85 (decision: D2 now, then work toward D3). Allowing Start runs in Practice seeds (88) needs a continue design first. Under today's design A (unlimited continues that restore the item lives), a game over mid-boss continues on the spot, so any boss falls to brute force and the lives/power/difficulty gates stop meaning anything. A Practice retry restarts the stage instead.

Design C (from 19, as in the IN apworld) keeps Start as fair as Practice: once a continue is used in a stage, that stage sends no more boss/clear checks in this run. The stage has to be beaten again without a continue. Normal-mode seeds keep design A; 19 stays deferred for them.

## DoD
- `pytest worlds/th11/test -q` passes with the tests below.
- In game (probe batch 74 R3): in a Practice seed's Start run, continuing at a stage boss and beating it sends nothing, the log says why, and the next stage cleared without a continue sends its checks.

## Design
- `ADDR_CONTINUES` (0xA573C, thprac `Globals.continues`, unverified in game) joins the state as `GameState.continues`.
- `detect.step(..., stage_continues=None)`: the continues count when the current stage began. The client keeps it: it's set when a run starts or the stage changes. If `state.continues` > `stage_continues`, then in a non-Practice run (no Practice flag) of a Practice seed, the stage's run checks are dropped. The runs still count, so the run index stays right.
- The client logs once per stage: `A continue in Stage N: its checks wait for a clear without one`.
- Unreadable (`None`) continues: nothing is voided (fail open; batch R3 verifies the address).
- Capture checks are unaffected: a capture needs the card taken without dying anyway.
- Until 88 lands, a Start run in a Practice seed is locked anyway, so 87 alone changes nothing a player sees. Its tests drive `step` directly.

## Test plan
- `test_state`: `ADDR_CONTINUES` decodes into `continues`.
- `test_detect`:
  - Practice seed, Start run (flags 0), continues 0 → 1 during Stage 2 → a boss drop sends `[]`;
  - the same with no continue → the checks;
  - Stage 3 entered with continues already 1 (`stage_continues` = 1) → the checks;
  - a Practice-flag run, and a normal-mode seed, ignore continues;
  - `continues` None → the checks.
- `test_client`: `stage_continues` is captured at run start and at a stage change, and the void line is logged once.

## Steps
1. `state.py`: `ADDR_CONTINUES` in `STATE_ENTRIES`, a `continues` field (default None).
2. `detect.py`: a `voided(state, stage_continues, slot_data)` helper, used in `step`.
3. `Client.poll`: keep `self.stage_continues`; pass it in; log the void once per stage.
4. Batch 74 R3 (verify `ADDR_CONTINUES` and the void in game). Tests, install.

## Deferred
- Normal-mode seeds' continue designs stay 18–20 (deferred).

## Comments
- 2026-10-25 Claude: done. ADDR_CONTINUES stays thprac-sourced until batch 74 R3. Runs found before the first connect are never voided (a ponytail in Client.poll).
- 2026-11-15 Claude: batch 74 R3 confirmed it in game.
