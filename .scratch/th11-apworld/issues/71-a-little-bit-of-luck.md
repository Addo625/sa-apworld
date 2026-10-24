# 71: Option "A Little Bit of Luck" rounds the difficulty gate up

Status: done
Blocked by: None

## Problem
Playtest (human, `players-64/addo.yaml`): with `difficulty_mid: hard`, `difficulty_end: normal` and no Lunatic, Stage 5 expects Hard, because the ramp `0, 0, mid/2, mid, (mid+end)/2, end` rounds down: (0+1)//2 = 0. `difficulty_mid: normal` is too easy (Normal from Stage 4). The human wants a toggle that rounds up, for difficulty only.

## What to do
- `ALittleBitOfLuck` toggle (`a_little_bit_of_luck`, default off). `Rules.stage_requirements(..., round_up)` rounds only the difficulty's Stage 3 and Stage 5 halves up; the fit cut still applies.
- README (the ramp formula, gates as a placement promise), `examples/th11.yaml`. Tests: `test_gates.test_luck_rounds_only_difficulty_up`, `test_generate.TestLuck`.

## Deferred
- None.

## Comments
- 2026-10-21 Claude: done. A seed from the human's YAML with the option on gives `stage_requirements` `(1,0,0,2), (2,0,0,4), (3,0,1,6), (4,0,1,9)` for stages 3-6.
