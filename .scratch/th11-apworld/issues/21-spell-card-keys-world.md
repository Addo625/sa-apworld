# 21: Spell captures become checks, and Spell Card Keys gate stages (world side)

Status: deferred
Blocked by: 02

## Problem
SA's core skill reward, capturing spell cards, isn't part of the randomizer, and a solo seed has only 34 locations to hold gate items. The user's design is Celeste-style (strawberries): captures are checks, and a separate `Spell Card Key` currency item in the pool gates stages alongside lives, power and difficulty. See `../spec.md` "Gates and Spell Card Keys" for the settled decisions. This ticket covers generation only. The client side is 22–24, so the option defaults to `off` until 24 flips it (risk K1).

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below and the new option sets in `test_extremes_fill_fixed_seeds`.

## Test plan
- **Options** (docstrings explain each one for players):
  - `spell_card_keys`: `off` (default, until 24) / `alongside` / `keys_only`.
  - `captures_per_stage`: 0–6, default 2.
  - `capture_slots`: `per_character` (default) / `shared`.
  - `spell_card_keys_in_pool`: 0–100 %, default 50.
  - `spell_card_keys_required`: 0–100 %, default 75.
  - `test_spell_card_keys_default_off`.
- **Locations:**
  - Per stage 1–6, k = 1..min(`captures_per_stage`, cap[stage]) with cap = 2/4/4/4/5/6 (a constant, with a comment that 23 verifies it).
  - Names: `[<Character>] Stage N - Capture k`, or `Stage N - Capture k` when `shared`.
  - IDs are appended after the existing table, never inserted, for k = 1..6 on stages 1–6 and k = 1..13 on Extra, for `ALL_CHARACTERS_LIST` and the shared names. Only stages 1–6 are created.
  - Per-character slots go in that character's stage region. A shared slot goes in a `Stage N Captures` region entered from either character's stage N region.
  - Tests:
    - `test_capture_count_default_alongside`: 24 = 2 × (2 × 6).
    - `test_capture_count_shared`: 12.
    - `test_stage1_capped_at_2`: `captures_per_stage=6` → stage 1 has 2 slots.
    - `test_off_creates_none`.
- **Items:**
  - `Spell Card Key`: progression, ID appended to the item table. The pool holds round(in_pool% × capture locations); the rest of the capture locations' share is filler.
  - Required by stage 6: R = floor(required% × keys). R goes into 02's `stage_requirements(..., keys_required=R, ...)`, which ramps it as 0, 0, R/4, R/2, 3R/4, R (floored) and clamps with the rest.
  - Tests:
    - `test_key_count_rounding`.
    - `test_key_gate_stage3`: with 12 keys and 75 %, stage 3 needs 2.
    - `test_item_count_matches_locations` covers the capture options.
- **`keys_only`:**
  - Gates use keys only; lives, power and difficulty are pooled as `useful`.
  - With zero keys (0 captures or 0 %), it logs a warning and acts as `alongside`.
  - Tests: `test_keys_only_ignores_lives`, `test_keys_only_zero_keys_falls_back`.
- **Shared slots:** `test_shared_slot_opens_from_either_character`, where the starting shot can be either character's.
- **`slot_data`** adds `spell_card_keys`, `captures_per_stage` and `capture_slots`. Update `test_slot_data_keys`.
- **`test_extremes_fill_fixed_seeds`** adds these option sets:
  - `alongside`, `captures_per_stage=6`, 100 % in pool, 100 % required, max gates (the clamp trims keys, and that must still fill);
  - `alongside` with `captures_per_stage=0`;
  - `shared` + `keys_only`.

## Steps
1. Options, plus the location and item table entries (append-only IDs), with the count tests. Green.
2. Regions and the shared region, with the key requirement fed into `stage_requirements`. Add the key gate and shared-slot tests. Green.
3. `keys_only` and its fallback, `slot_data`, and the extreme sets in the fixed-seed test (tune `GATE_SLACK` if needed). Run the DoD.

## Deferred
- Detecting captures in the client and flipping the default to `alongside` → 24.
- Extra-stage capture slots: IDs reserved here, created with 11.
- Toning down capture difficulty beyond `captures_per_stage`: to be planned separately with the user.
