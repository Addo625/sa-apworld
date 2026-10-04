# 18: Continues design B: limited continues as items

Status: deferred
Blocked by: 12

## Problem
Option B from planning: an opt-in `limited_continues` that restores EoSD's "continues are an item" feel. "+1 Continue" items are added to the pool, and the client ends the run when the player continues more times than they have items.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Option:** `limited_continues` (default off). On → 3 `+1 Continue` (useful) items, as in EoSD. Test: `test_continue_items_only_when_enabled`.
- **`continues.on_continue(used, owned)`** → allow, or end the run.
  - The used-continues counter address comes from the table; probe it in a human ticket if it is missing.
  - Ending the run reuses the 14 kill mechanism if available, or a return-to-title.
  - Tests: allowed while used ≤ owned, ends the run at used > owned.

## Steps
1. Option and pool, with tests.
2. Verify the continues-used address, then the client logic, with tests.

## Deferred
- None.
