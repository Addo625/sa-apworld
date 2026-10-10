# 11: Extra stage and goals Koishi or both

Status: needs-human
Blocked by: 09, 32

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
- 2026-10-10 al-work: everything but the Extra unlock write is in (97055a2 world, next commit client). `ADDR_EXTRA_UNLOCK` is still `None` (`TODO(06)`), so per the DoD 32 is the `ready-for-human` probe and this ticket is blocked on it.
  - Done: options `extra_stage`/`number_life_extra`/`power_extra`/`goal`/`ending_required` with the EoSD fallbacks; Extra locations; `Extra Stage` items (apart, or linear without progressive stages) and a 6th `Next Stage` (linear, progressive); locked `Ending - Koishi`; completion and the client's goal check share `Rules.goal_met`. Detection of stage 7 was already in (`test_detect_extra_has_no_difficulty_checks`, `test_detect_clear`). `Extra Stage` is logged as a pending unlock. README and example YAML updated.
  - Decision: logic puts Extra after Stage 6 even when apart (apart + Extra gate 8/8 failed fill on 9 of 100 fixed seeds; 0 once chained). Extra adds `EXTRA_SLACK` = 2 per unlock group (measured). Linear without progressive stages has no `Next Stage` to add, so it uses the `Extra Stage` item (no `Stage 7` item exists).
  - Left after 32: set `ADDR_EXTRA_UNLOCK` from 32's findings, make `receive.apply` write it on `Extra Stage` (per group like `stage_unlock`), with a test. Normal-mode `canExtra` waits for 12.
