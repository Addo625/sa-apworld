# 01: Generate a seed from a minimal TH11 world

Status: ready-for-agent
Blocked by: None (can start immediately)

## Problem
Nothing exists yet. Every later ticket needs a pinned Archipelago checkout, a venv, and a `th11` world that AP discovers, generates and tests. See `../spec.md` (Decisions: Layout, Dev AP, Game identity).

## DoD
`tools/setup_dev.sh && cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with at least one passing test that generated a th11 seed (the `WorldTestBase` default tests).
`git status --short` shows no `.ap/`, `.venv/` or `__pycache__` entries.

## Test plan
- `tools/setup_dev.sh`
  - In: a clean repo. Out: `.ap/` at the tag in `tools/AP_VERSION`, `.venv/` with AP requirements + pytest, and the symlink `.ap/worlds/th11 → ../../th11`.
  - Re-running it is a no-op: no re-clone, no error.
- `th11` world
  - In: AP world discovery. Out: the game `Touhou Chireiden ~ Subterranean Animism` is registered.
  - One region `Menu` with one location `[Reimu] Stage 1 Clear`. One progression item `Reimu A - Yukari`, IDs from `STARTING_ID = 110000`. The completion condition is having that item.
- `th11/test/__init__.py`: a `WorldTestBase` subclass with `game` set. Its inherited tests (`test_all_state_can_reach_everything`, `test_empty_state_can_reach_something`, `test_fill`) pass.

## Steps
1. Pick the newest stable AP release tag that is ≥ 0.6.6 (`git ls-remote --tags https://github.com/ArchipelagoMW/Archipelago`) and write it to `tools/AP_VERSION`.
2. Write `tools/setup_dev.sh` (bash, `set -euo pipefail`):
   - Shallow-clone `.ap` at that tag if missing.
   - Create `.venv` with `python3.12` if missing.
   - `pip install -r .ap/requirements.txt pytest`.
   - `ln -sfn ../../th11 .ap/worlds/th11`.

   Run it.
3. Create `th11/`:
   - `archipelago.json` with game, authors, `minimum_ap_version` = the tag, `world_version` `0.1.0`.
   - `LICENSE`: MIT, keeping Nepley's copyright line because code is ported from their worlds.
   - Minimal `__init__.py` World, following the shape of `ref-projects/mof-apworld/__init__.py` and dropping the client component for now.
4. Add `th11/test/__init__.py` with the `WorldTestBase` subclass. Run the DoD.

## Deferred
- The client launcher component is added in 04.
- Real items, locations and options come in 02.

## Comments

- 2026-10-04 al-work plan broken: the unattended run has no network permission. These were all denied: `git ls-remote --tags https://github.com/ArchipelagoMW/Archipelago` (step 1), `curl` to the GitHub releases API, and WebFetch. Steps 1–2 need network (tag lookup, `git clone`, `pip install`), so the DoD can't be reached. No code was written. Fix one of these: (a) allow `git ls-remote`, `git clone` and `.venv/bin/pip install` (plus `python3.12 -m venv`) for this project in `.claude/settings.json`; or (b) run step 1–2 yourself: write the tag to `tools/AP_VERSION`, clone `.ap`, create `.venv`. The agent will then write `tools/setup_dev.sh` around what already exists.
- 2026-10-04 human: granted option (a) in `.claude/settings.json` (git ls-remote/clone/add/commit, venv, pip install, pytest, WebFetch github.com). Back to ready-for-agent.
- 2026-10-04 al-work stopped (not an attempt; nothing implemented): working tree was dirty at start. Uncommitted: `.claude/settings.json` drops the `Write(./.games/**)` and `Write(./ref-projects/**)` deny rules (modified 22:32, after 1aba69f); untracked `tools/AP_VERSION` (`0.6.8`) and `tools/setup_dev.sh` (looks like steps 1–2 from an interrupted run; `.ap/`, `.venv/`, `th11/` don't exist). Left both untouched. Human: commit, keep or discard them so `git status` is clean, then re-run.
- 2026-10-04 al-work attempt failed: working tree still dirty at start, unchanged since the previous stop (same `.claude/settings.json` deny-rule removal, same untracked `tools/AP_VERSION` + `tools/setup_dev.sh`). Nothing implemented, nothing touched. Counted as an attempt so the loop escalates to needs-human instead of re-running on the same blocker. Next try: once `git status` is clean, keep `tools/` (it already matches steps 1–2) and run `tools/setup_dev.sh`.
