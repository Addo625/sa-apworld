# 25: Stage 4 gets two checks, one per cat-Orin appearance

Status: done
Blocked by: 08

## Problem
Stage 4 has no midboss location in v1, because cat Orin can't be defeated: she leaves on a timer. The human probes (06) showed she appears **twice**, and the boss field records both appearances cleanly before Satori's run. The human decided on two locations, one per appearance ("more items, more fun"). Each check is earned by surviving that encounter until she leaves.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **Locations:** `[<Character>] Cat Orin - First Appearance` and `[<Character>] Cat Orin - Second Appearance` in each character's Stage 4 region.
  - Their IDs are **appended** to the end of the location table, never inserted, so existing IDs don't shift (as in 21). Names for the shot-type and difficulty variants are appended the same way, so ticket 10 can use them.
  - `test_location_count` becomes 38. Update the extreme-combination tests if their counts are pinned.
- **Rules:** the same stage 4 gate as `Satori Defeated`.
- **Client `detect`:** stage 4 runs of the boss field, in order: run 1 ends → First Appearance, run 2 ends → Second Appearance, run 3 ends → `Satori Defeated`. A run that ends with a menu exit sends nothing (S9 rule).
  - `test_detect_stage4_first_appearance`.
  - `test_detect_stage4_second_appearance`.
  - `test_detect_stage4_satori_after_two_runs`.
  - `test_detect_stage4_quit_mid_encounter_sends_nothing`.
- **Spec:** the Content table row 4 already names both locations.

## Steps
1. World: append the location IDs and add them to the Stage 4 regions. Update the count tests. Green.
2. Client: run counting per stage in `detect`, with the tests. Run the DoD.

## Deferred
- If a later stage 4 recording shows only one appearance on some difficulty, make the second location difficulty-gated, or drop it then.

## Comments
- al-work 2026-10-10: done in one commit. IDs appended after the capture slots (base + 4 difficulty variants × 8 characters/shots). DoD `pytest worlds/th11/test -q` → 136 passed, 994 subtests. The 4 new stage 4 locations widened the stage 5/6 rooms so max gates stopped clamping, and `test_extremes_fill_fixed_seeds` failed seeds 8 (max) and 15 (keys max); `GATE_SLACK` raised 2 → 3 per its ponytail note, which makes every gate's room one smaller (stage 3 max clamp now (2, 3, 1)). No new deferred tickets.
