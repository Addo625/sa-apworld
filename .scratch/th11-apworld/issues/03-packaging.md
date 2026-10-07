# 03: Build th11.apworld and prove AP loads the zip

Status: ready-for-agent
Blocked by: 02

## Problem
Players install worlds as `.apworld` zips. We need a build, an example YAML and a README, plus proof that AP loaded the zip and not the dev symlink. AP refuses to register the same game twice, so the symlink has to be out of the way during the check.

## DoD
`tools/check_apworld.sh` → exit 0. It prints `apworld loaded from custom_worlds` and the path of a new `.ap/output/AP_*.zip`, and leaves `.ap/worlds/th11` restored as a symlink.

## Test plan
- `tools/build_apworld.sh`
  - In: `th11/`. Out: `dist/th11.apworld`, a zip whose top folder is `th11/`, containing `archipelago.json` and no `__pycache__`, `test/` or `.DS_Store`.
  - Check: `unzip -l dist/th11.apworld` lists `th11/archipelago.json` and no `test/`.
- `tools/check_apworld.sh`
  1. Builds.
  2. Moves the symlink aside.
  3. Copies the zip to `.ap/custom_worlds/`.
  4. Copies `examples/th11.yaml` to `.ap/Players/` (only that YAML).
  5. Runs `Generate.py`, then asserts that the module file of the th11 world (`worlds.AutoWorld.AutoWorldRegister.world_types[game].__file__`, printed by a one-liner) contains `custom_worlds`.
  6. Always restores the symlink and removes the copies, via a `trap`.
- `examples/th11.yaml`: every core option at its default. Generate succeeds with it.

## Steps
1. Write `build_apworld.sh` (stdlib `zip` / `python -m zipfile`) and add `dist/` to `.gitignore`.
2. Write `examples/th11.yaml` and `check_apworld.sh` with the trap-based restore. Run the DoD.
3. Write a README, using `ref-projects/eosd-apworld/README.md` as the model: locations, items, options, how to use, the score.dat backup warning, and the Wine notes (Windows AP in the same prefix, client attaches to `th11.exe` by name, `--nogui` fallback).

## Deferred
- Publishing to the AP index or GitHub releases: out of scope, the human decides.

## Comments

- 2026-10-07 al-work plan broken: the agent can't run the DoD. Running `tools/*.sh`, `chmod`, `unzip` and `git stash` all need approval, and the project allowlist (`.claude/settings.json`) doesn't cover them.
  - **Drafted but never run** (committed only to keep the tree clean): `tools/build_apworld.sh`, `tools/check_apworld.sh`, `examples/th11.yaml`, README, and `dist/` in `.gitignore`. The scripts aren't executable yet (`chmod` was denied) and were written by reading AP's source, so treat them as untested.
  - **Changes from the test plan:**
    - The check passes `--player_files_path <tmpdir>` holding only `examples/th11.yaml`, instead of copying the YAML into `.ap/Players/`, so any YAMLs already there can't get in.
    - It deletes the symlink and recreates it with `ln -sfn ../../th11` (the same command as `setup_dev.sh`) instead of moving it aside.
    - It sets `SKIP_REQUIREMENTS_UPDATE=1`, because `Generate.py` runs `ModuleUpdate.update()`, which would stop at an `input()` prompt for the soe/zillion requirements that aren't installed.
  - **Unblock:** run `chmod +x tools/build_apworld.sh tools/check_apworld.sh`, then add `"Bash(tools/build_apworld.sh)"`, `"Bash(tools/check_apworld.sh)"` and `"Bash(unzip -l:*)"` to `.claude/settings.json` `allow` (or run `tools/check_apworld.sh` yourself and paste the output here). Then relabel `ready-for-agent`. The next run verifies the drafts and folds any fixes into this commit.
- 2026-10-07 human: scripts made executable; allowed `tools/build_apworld.sh`, `tools/check_apworld.sh`, `unzip -l` in local settings. Back to ready-for-agent.
