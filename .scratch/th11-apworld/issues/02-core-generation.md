# 02: Generate beatable core TH11 seeds (practice mode, global unlock, goal Utsuho)

Status: needs-human
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

## Comments

- 2026-10-04 al-work plan broken: "all gates at maximum" can't pass `test_fill`, and the ticket's own life-gate test rules out shrinking the ranges enough to fix it.
  - **Evidence.** Before stages 3/4 open, only the Stage 1–2 locations of both characters are reachable: 2 × 6 = 12. Two of them must hold a `Next Stage` (stage 2 needs it) and the other character's shot. That leaves 10 slots for the Mid gate items. At max, the Mid gate needs 8 lives + 8 power + 3 `Lower Difficulty` = 19. AP's fill failed as expected ("No more spots to place 25 items"). `test_stage3_blocked_by_life_gate` requires `number_life_mid=8` to be legal, and `difficulty_mid` is fixed at 0–3. So even with `power_mid` capped at 0, the worst case is 8 + 3 = 11 > 10. EoSD has the same ranges and the same hole (it has no tests).
  - **Committed** (green, defaults and single gates): the world in `th11/` and every named test except the two max-gate `WorldTestBase` classes, which I removed. Run `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → 21 passed.
  - **Also blocks the DoD:** `test/general` fails only on `test_no_failed_world_loads`, because `pokemon_emerald`, `soe` and `zillion` don't load. Their extra requirements aren't installed: `setup_dev.sh` installs only `.ap/requirements.txt`. The other 372 passed (runtime 69 s). Installing `worlds/*/requirements.txt` needs approval for `.venv/bin/pip install -r worlds/soe/requirements.txt -r worlds/zillion/requirements.txt`, or for running `ModuleUpdate.py` once.
  - **Decide one:**
    - (a) Clamp the gates at generation (`generate_early`). The Mid total (lives + power + difficulty) stays ≤ 10, the End total stays within what's reachable, and the player gets a warning.
    - (b) Make the "max" extreme test the largest fillable combination (e.g. life 8, power 0, difficulty 2), and document that higher combinations need other worlds' locations.
    - (c) Accept the failure solo and only test max gates in a multiworld with a filler-heavy partner.

    My pick is (a): it keeps the ranges at EoSD parity and never produces an unfillable seed.
