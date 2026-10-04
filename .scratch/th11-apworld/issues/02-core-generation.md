# 02: Generate beatable core TH11 seeds (practice mode, global unlock, goal Utsuho)

Status: ready-for-agent
Blocked by: 01

## Problem
The v1 world needs EoSD's core randomization adapted to SA. See `../spec.md`: Content, Items (core), Options (core). The design source is `ref-projects/eosd-apworld` (Items, Locations, Regions, Rules, Options, `__init__`), with SA adaptations from `ref-projects/mof-apworld`.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the named tests below.
`cd .ap && ../.venv/bin/python -m pytest test/general -q` → exit 0. It covers ID and name uniqueness and the data package for all installed worlds; note the runtime in the ticket comments.

## Test plan
- **Locations:** per character `Reimu` and `Marisa`, the stage 1–6 checks from the spec's Content table plus `Stage N Clear` = 2 × (6 stages × midboss/boss + 6 clears − Stage 4 midboss) = 2 × 17 = 34 locations. Extra and difficulty locations exist in the table (IDs reserved, as EoSD does) but are not created.
  - `test_location_count`: 34 created locations by default.
- **Items:**
  - 6 shot types, one of them precollected.
  - `Next Stage` ×5: Stage 1 is always open, stages 2–6 are unlocked in order.
  - `+1 Life` ×8. Check SA's lives cap in `ref-projects`/thprac; MoF uses 9.
  - `+0.50 Power` ×N, progression. N = enough packs to reach 4.00, from 0 (8 packs).
  - `Lower Difficulty` ×3, or ×2 with `exclude_lunatic`.
  - Locked `[Reimu] Ending - Utsuho` and `[Marisa] Ending - Utsuho` on the two `Stage 6 Clear` locations.
  - Filler `+0.05 Power` = remaining locations.
  - `test_item_count_matches_locations`.
- **Rules:**
  - A stage N region needs `Next Stage` ≥ N−1 and a shot type of that character.
  - Stages 3/4 need lives ≥ `number_life_mid`, power packs ≥ `power_mid`, and `Lower Difficulty` ≥ `difficulty_mid` (minus 1 with `exclude_lunatic`, floored at 0).
  - Stages 5/6 use the `_end` equivalents.
  - Tests: `test_stage3_blocked_without_next_stage`, `test_stage3_blocked_by_life_gate` (`number_life_mid=8` → not reachable with 7 lives, reachable with 8), `test_power_gate`.
- **Goal:** the completion condition is any `Ending - Utsuho` (EoSD `ONE_ENDING`). `test_goal_requires_ending`.
- **Extreme combinations** (`WorldTestBase` subclasses with `options`), each passing `test_fill` and `test_all_state_can_reach_everything`:
  - All gates at maximum.
  - `exclude_lunatic` + maximum difficulty gates.
  - Defaults.
- **`fill_slot_data`:** returns every option the client needs (the gates, `exclude_lunatic`). `test_slot_data_keys`.

## Steps
1. Write the constants module (names, lists, IDs) for SA, mirroring `eosd-apworld/variables/globals.py` without addresses. Then write `Items.py` and `Locations.py`, reserving IDs for the deferred categories so they never shift later. Location and item count tests go green.
2. Write `Regions.py` and `Rules.py` (EoSD's Early/Mid/Late region shape) and `Options.py` (core options only). Rule tests go green.
3. Write `create_items` with computed filler and the locked endings, then `fill_slot_data`. Extreme-combination tests and `test/general` go green.

## Deferred
- `stage_unlock`, `shot_type`, `difficulty_check` → 10.
- Extra + goals → 11.
- Normal mode → 12.
- Traps → 13.
