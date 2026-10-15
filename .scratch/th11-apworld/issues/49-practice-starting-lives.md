# 49: Practice starts with lives from received +1 Life items

Status: deferred
Blocked by: 50

## Problem
Batch 44 (human): Practice always starts with the maximum lives (the game's default, 9), so `+1 Life` items barely matter in Practice mode. EoSD/MoF set Practice starting lives to the received `+1 Life` count (MoF `ADDR_PRACTICE_STARTING_LIVES`, a code-site immediate). SA's `ADDR_PRACTICE_STARTING_LIVES` is unsourced; 34's static scan found the Practice init `mov [0x4A5718], 9` at `0x41FA4B`. The human hasn't decided whether this is wanted ("not sure this should be that way, but sure, for now").

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_practice_starting_lives_patch_guarded`.

## Test plan
- `ADDR_PRACTICE_STARTING_LIVES` = the immediate at `0x41FA4B` (`c7 05 18 57 4a 00 09 00 00 00`); `EXPECTED_BYTES` = the 6 bytes before the immediate. Patched like 34's continue lives (`patch_immediate`), with the value = received `+1 Life` count (capped by `limit_lives`), in Practice mode only.
- `test_practice_starting_lives_patch_guarded`, plus the thcrap overlap test.

## Steps
1. The entry, the patch and the tests. Add an in-game check (a new Practice run starts with N lives) to the open batch.

## Deferred
- Promote only if the human wants it (decision).
