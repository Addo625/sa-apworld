# 83: The YAML sets how long the timed traps last

Status: done
Blocked by: None

## Problem
The human (2026-10-24): No Focus, Reverse Movement, Aya Speed and Power Drain always lasted 20 seconds. The duration should be a YAML setting.

## What to do
- `trap_duration` (seconds, 5-60, default 20) in the options and slot data. The client's `TrapState(duration)` uses it for the three speed traps and Power Drain. Freeze keeps 3 seconds, since it stops the player outright.
- `examples/th11.yaml` line. Tests: `test_traps.TestTrapDuration`; `trap_duration` in the slot data keys.

## Deferred
- None.
