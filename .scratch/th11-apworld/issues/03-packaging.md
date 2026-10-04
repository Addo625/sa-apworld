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
