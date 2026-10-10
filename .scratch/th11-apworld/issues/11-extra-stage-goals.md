# 11: Extra stage and goals Koishi or both

Status: ready-for-agent
Blocked by: 09

## Problem
EoSD/MoF offer the Extra stage (`extra_stage`: exclude, linear as stage 7, apart with its own unlock item), goals (`goal`: final boss, extra boss, both) and `ending_required` (once, both characters, all shot types). SA's are Utsuho and Koishi, with Sanae as the Extra midboss. This needs Extra addresses (the Extra unlock flag, the Extra boss flags), which 06 may not have reached.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.
`grep -n "TODO(06)" th11/Variables.py` shows no Extra entries. If any are still unverified, first create a `ready-for-human` probe ticket for Extra and block this one on it.

## Test plan
- **Options:** `extra_stage`, `number_life_extra`, `power_extra`, `goal` (utsuho/koishi/both), `ending_required` (once/both_characters/all_shot_types, falling back like EoSD when `shot_type` is off).
- **Locations:** `Sanae - Midboss`, `Koishi Defeated`, `Stage Extra Clear` per character or shot type, only when `extra_stage` ≠ exclude.
- **Items:**
  - `apart` → `Extra Stage` (global, per character or per shot, following `stage_unlock`).
  - `linear` → one more `Next Stage`.
  - Locked `Ending - Koishi` on `Stage Extra Clear` when the goal includes Koishi.
- **Completion:** `victoryCondition` per EoSD. Tests: `test_goal_koishi_once`, `test_goal_both_all_characters`, `test_all_shot_types_falls_back`.
- **Extreme combinations:** `extra_stage=apart` + `goal=both` + `ending_required=all_shot_types` + `shot_type`, passing `test_fill`.
- **Client:**
  - `detect` handles stage 7 (Extra) flags.
  - `items.apply('Extra Stage')` writes the Extra unlock.
  - In normal mode, Extra unlocks after Stage 6 (EoSD `canExtra`); this matters only if 12 is in.
  - Tests for each.

## Steps
1. Verify the Extra entries exist (see the DoD), then add the options, the locations and items, and the rules and completion, with tests.
2. Client Extra detection and unlock, with tests. Update the README and example YAML.

## Deferred
- None.

## Comments

- 2026-10-10 planner: promoted by the human after 09 passed. Written before 06/07 findings; use the current code: `ADDR_MENU_PTR` (not a game mode), in a stage = `ADDR_ENEMY_MANAGER` ≠ 0, boss = `ADDR_IS_BOSS_PRESENT`, power in 0.05 units (max 80). If an address this ticket needs is unsourced (e.g. Extra unlock, menu/continue sites), implement everything else, then set `needs-human` naming the probe needed.
