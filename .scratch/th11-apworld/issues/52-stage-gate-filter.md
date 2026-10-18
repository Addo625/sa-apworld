# 52: Runs on stages the items haven't opened send no checks

Status: done
Blocked by: 51

## Problem
Ticket 51: the check filter (16) blocked only unreceived shots and difficulties. A stage the game unlocks by itself (playing ahead, or a full Start run in a Practice seed) still sent its checks, so the stage gates could be skipped. Human decision (2026-10-18): filter stages too.

## What to do
- `receive.stage_open(item_names, slot_data, shot, level)` asks the same rule logic (`Rules.stage_unlocked`) whether the received items open that stage for that shot. `detect.locked` returns `"<shot> Stage N"` when they don't. Normal modes are unaffected (their stages are always open); Extra is stage 7 (45).
- The client passes the received names; the "isn't unlocked: this run sends no checks" log covers stages too.

## Deferred
- None.
