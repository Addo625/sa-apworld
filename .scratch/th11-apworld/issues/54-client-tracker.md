# 54: A Tracker tab in the client shows each stage's gate and the checks left

Status: done
Blocked by: 50

## Problem
Batch 50 / playtest (human): the gates can't be followed while playing. Nothing shows when a stage counts as in logic, what counts toward its gate, or what's missing. Human decision (2026-10-18): a text tracker in the client, as a tab next to Archipelago/Hints (not a PopTracker pack for now).

## What to do
- `th11/tracker.py` `report(item_names, missing_names, slot_data)`: goal progress, item counts, and per received shot one line per stage: OPEN (in logic) / PLAYABLE (open, gate unmet, lists what's missing) / LOCKED (names the stage item), plus checks left. Reuses `receive.stage_open` and `slot_data["stage_requirements"]`.
- `Client`: `/tracker`, and a "Tracker" tab redrawn every second (`make_gui`).
- README "Tracker" section. Tests in `test_tracker.py`.

## Deferred
- First in-game look at the tab: next session (the GUI can't open from Claude's background session).
- A PopTracker pack, if the text tracker isn't enough.
