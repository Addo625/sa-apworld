# 12: Normal mode (dynamic/static difficulty), continues design A

Status: done
Blocked by: 09

## Problem
EoSD's `mode` option also offers Normal mode: a full run with only the starting resources, where gates are just lives, power, difficulty and character. The difficulty is either dynamic (forced to the lowest unlocked one) or static. Under continues design A (user decision), SA continues are unlimited and continuing restores your item-earned lives (MoF `setNormalContinueLives`); there is no continue item. This needs the menu, difficulty-cursor and continue-lives addresses.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the tests below.

## Test plan
- **Option:** `mode` = practice/normal_dynamic/normal_static.
  - In normal modes there are no `Next Stage` items, so stage rules are always true (EoSD `constructStageRule`).
  - Easy is excluded in dynamic mode, as EoSD does.
  - Test: `test_normal_no_next_stage_items`.
- **Fill:** normal mode with all gates at minimum has fewer progression items, so `test_fill` checks that filler covers the gap.
- **Client** (pure):
  - Dynamic mode sets the difficulty to the lowest unlocked one when entering the game (`items.difficulty_for(state)`).
  - The continue-lives code site is patched through `safe_patch` to the AP life count.
  - Detection in normal mode works across stages 1→6 in one run.
  - Tests: `test_dynamic_difficulty_lowest_unlocked`, `test_continue_lives_patch_uses_guard`, `test_normal_run_stage_transitions`.
- **Human:** add a `ready-for-human` smoke ticket at promotion: one normal run through stage 2, then continue once and check that lives equal the AP count.

## Steps
1. Option, rules and item-pool changes, with tests.
2. Client difficulty forcing and the continue-lives patch, with tests. Update the README.

## Deferred
- Continue variants: B → 18, C → 19, D → 20.

## Comments

- 2026-10-10 planner: promoted by the human after 09 passed. Written before 06/07 findings; use the current code: `ADDR_MENU_PTR` (not a game mode), in a stage = `ADDR_ENEMY_MANAGER` ≠ 0, boss = `ADDR_IS_BOSS_PRESENT`, power in 0.05 units (max 80). If an address this ticket needs is unsourced (e.g. Extra unlock, menu/continue sites), implement everything else, then set `needs-human` naming the probe needed.

- 2026-10-10 al-work: not started, working tree dirty. Run 20261010-160855-2 hit the session limit mid step 2 and left uncommitted work in th11/{Client,Variables,detect,patching,receive}.py (dynamic difficulty writes, continue-lives patch via `patch_immediate`, `/peek` `/poke`), with no tests yet. Left untouched. Human: commit it as WIP, or `git stash`, then rerun the loop.

- 2026-10-10 al-work attempt failed: working tree still dirty with the same uncommitted step-2 work (run 20261010-164554-2); nothing implemented. Counts toward AL_MAX_FAILS so the loop stops instead of re-failing. Human: commit as WIP or `git stash`, then rerun.

- 2026-10-10 al-work attempt failed: working tree still dirty with the same uncommitted step-2 work (run 20261010-164554-3); left untouched, nothing implemented. Second counted failure: the next run marks 12 `needs-human`. Human: `git stash` or commit it as WIP (or `git checkout -- th11/` to drop it), then rerun.

- 2026-10-10 al-work (run 20261010-164554-4): 2 failed attempts reached AL_MAX_FAILS → `needs-human`. Both failures had one cause: the uncommitted step-2 work in th11/{Client,Variables,detect,patching,receive}.py (+93/−7, no tests) blocks every run's clean-tree check. Not code failures. Human: `git stash` / commit as WIP / `git checkout -- th11/`, then set `Status: ready-for-agent` (optionally drop the two failure notes) and run `agent-loop`.
- 2026-10-10 human (via Claude): finished step 2 from the interrupted run's uncommitted work. Added the plan's tests (`test_dynamic_difficulty_lowest_unlocked`, `test_continue_lives_patch_uses_guard`, `test_normal_run_stage_transitions`). The write guard allows `/poke` (a human-typed debug write) and checks `patch_immediate` callers like `safe_patch`. Suite: 252 passed.
  - The continue-lives code site is still unknown: no `mov [0x4A5718], imm` sits near the continue code (static scan of `th11.exe`), so it goes to 34 (static analysis with a disassembler, not a game session). Until then the client logs "pending" and patches nothing.
  - The planned human smoke run (continue once, lives = AP count) moves to 34's in-game check.
