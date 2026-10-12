# 45: An Extra run without its Extra item sends no checks

Status: deferred
Blocked by: 33

## Problem
33 sets the Extra unlock bit for received Extra items but never clears one. A save whose Extra is already open (a cleared game, or the cheated `.games/sa`) lets the player play Extra before logic expects it, and the client sends `Sanae - Midboss`, `Koishi Defeated` and `Stage Extra Clear`. 16 filters runs on locked shots and difficulties the same way; Extra isn't covered.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **`detect.locked`:** a run with `state.stage == 7` is locked when its shot's index is not in `receive.extra_shots(item_names, slot_data)`. Pass the set in from `Client.poll`: compute it once there and hand it to both `unlock_extra` and `detect.step`.
  - Normal-mode linear Extra (left to the game by 33) is never locked by this.
  - Tests: `test_extra_run_without_item_sends_nothing`, `test_extra_run_with_item_sends_midboss`, and the before-connect path (`runs_found`) filtered the same way.
- Not chosen: clearing the bit for unreceived shots. It would rewrite the player's save (the game writes it on exit), and the filter alone keeps logic intact.

## Steps
1. Extend `detect.locked` and its callers with the Extra set, with tests. Run the DoD.

## Deferred
- None.
