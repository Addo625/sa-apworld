# 10: Choose check and unlock granularity (by character, by shot type, by difficulty)

Status: ready-for-agent
Blocked by: 09

## Problem
EoSD lets the player choose how stage unlocks are grouped (`stage_unlock`: global, by character, by shot type), whether checks are per shot type (`shot_type`) or per difficulty (`difficulty_check`, `check_multiple_difficulty`). MoF adds `progressive_stage`. v1 only has global unlocks with checks per character. It was deferred until the detection approach was proven in-game (09).

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.
`tools/check_apworld.sh` → exit 0.

## Test plan
- **Options:** `stage_unlock` (global/by_character/by_shot_type), `progressive_stage` (MoF), `shot_type`, `difficulty_check`, `check_multiple_difficulty`. Docstrings follow EoSD.
- **Location counts:**
  - `shot_type` → per shot type (6 × 17).
  - `difficulty_check` → adds the `[<Difficulty>][<Char>]` midboss/boss locations for each difficulty not excluded.
  - Tests: `test_count_shot_type`, `test_count_difficulty`, `test_count_both`.
- **Rules:**
  - `by_character` → stage N needs `[<Char>] Next Stage` ≥ N−1 and a shot of that character.
  - `by_shot_type` without `shot_type`/`difficulty_check` falls back to by_character, as EoSD does.
  - A difficulty location needs `Lower Difficulty` ≥ (3 − difficulty index), adjusted for `exclude_lunatic`.
  - Tests for each mode.
- **Gate room** (from 02's fit check): room is computed per `stage_unlock` mode. `by_character` needs (k−1) `[<Char>] Next Stage` per character. Difficulty locations are gated by `Lower Difficulty`, so they don't count as room. `test_room_by_character`, `test_room_skips_difficulty_locations`.
- **Extreme combinations:** each passes `test_fill` and joins 02's `test_extremes_fill_fixed_seeds`. Fewest locations is `by_shot_type` + no extra checks (fallback); most is `shot_type` + `difficulty_check` + all gates at maximum.
- **Client** (pure):
  - `detect.step` emits shot-type and difficulty location IDs according to `slot_data`.
  - `check_multiple_difficulty` also emits the lower unlocked difficulties (EoSD `setCurrentStageBossBeaten(otherDifficulties)`).
  - `items.apply` writes unlock rows per character or per shot.
  - Tests for each.

## Steps
1. Options and the location/item tables (IDs already reserved in 02), with count tests.
2. Region and rule changes, with rule tests and the extreme combinations.
3. Client mapping in `detect` and `items`, with tests. Update the README and `examples/th11.yaml`.

## Deferred
- An in-game check of difficulty-separated checks: covered by the next human smoke run after promotion. Add a `ready-for-human` ticket when promoting.

## Comments

- 2026-10-07 human: promoted to ready-for-agent as written. Still blocked by 09 (in-game smoke), so the loop picks it up only after 09 is done.

- 2026-10-10 planner: promoted by the human after 09 passed. Written before 06/07 findings; use the current code: `ADDR_MENU_PTR` (not a game mode), in a stage = `ADDR_ENEMY_MANAGER` ≠ 0, boss = `ADDR_IS_BOSS_PRESENT`, power in 0.05 units (max 80). If an address this ticket needs is unsourced (e.g. Extra unlock, menu/continue sites), implement everything else, then set `needs-human` naming the probe needed.
