# 55: Practice-mode seeds send nothing from normal Start runs

Status: done
Blocked by: 50

## Problem
Batch 50 R3: in a Practice-mode seed, a normal Start run counts. It skips the item-based lives, power and difficulty that Practice applies, and a boss loss in it sent `Parsee Defeated` + `Stage 2 Clear` (57).

## What to do
- `GameState.flags` (`ADDR_GAME_FLAGS`); `state.PRACTICE_FLAG = 0x10` (16 in Practice play, 0 in normal play and Extra).
- `detect.locked`: Practice-mode seed, stage 1-6, flags readable without the bit → "Start (the normal game; this seed plays from Practice)", so the run sends nothing and the client logs it. Extra is unaffected.
- README line. Test in `test_detect.TestStageGate`.

## Deferred
- 56: block Start from the title menu in Practice seeds.
