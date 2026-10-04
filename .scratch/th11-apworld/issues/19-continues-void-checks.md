# 19: Continues design C: checks after a continue don't count

Status: deferred
Blocked by: 12

## Problem
Option C from planning, after IN (`ref-projects/in-apworld/Client.py`, continue tracking near `currentContinue`). In normal mode continues stay unlimited, but locations reached after a continue aren't sent until the stage is replayed without one.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Option:** `continue_voids_checks` (default off).
- **`detect.step`** with a continues-used delta in the current stage and the option on → `[]` for that stage. Next stage, no continue → normal checks.
- Tests: `test_checks_voided_after_continue`, `test_next_stage_clean_counts`, `test_option_off_unchanged`.

## Steps
1. Option and slot_data, then the detect filter, with tests.

## Deferred
- None.
