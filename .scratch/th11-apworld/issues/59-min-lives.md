# 59: Option min_lives: Practice runs start with min_lives + the +1 Life items

Status: done
Blocked by: 50

## Problem
Batch 50 Q1 (human): a Practice run with no `+1 Life` starts with 0 spare lives. The human wants a YAML option, `min_lives: 0`.

## What to do
- `MinLives` (0-8, default 0) in slot data. `receive.practice_lives` = min(min_lives + received +1 Life, limit_lives, 9) feeds 49's Practice lives patch; normal-mode continues are unchanged. Logic is unchanged (gates still count items).
- `examples/th11.yaml` line; the tracker shows the starting lives. Test in `test_normal`.

## Deferred
- None.
