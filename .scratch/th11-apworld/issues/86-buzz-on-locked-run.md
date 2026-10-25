# 86: A run on anything locked buzzes in the game

Status: done
Blocked by: None

## Problem
85 (D2): Janania started a locked run (Start in a Practice seed) and nothing in the game said so; only one client log line did. The same holds for a locked shot type, difficulty or stage.

## DoD
- `pytest worlds/th11/test -q` passes with the test below.
- In game: starting a run on a locked shot type, difficulty or Start plays the menu buzzer once.

## Test plan
- `test_client.test_locked_run_logs_once` grows to: the locked run start writes `SOUND_IDS["trap"]` once (with `/itemsound` on), and the next tick writes no second buzz.
- An unlocked Practice run start writes no buzz.

## Steps
1. `Client.poll`: where the "isn't unlocked" line is logged, call `self.play_sound(controller, "trap")` (the trap buzzer, 84). It respects `/itemsound` like every other sound.
2. Test, install the apworld.

## Deferred
- None. 88 removes the Start case (Start runs become allowed); the buzzer stays for the other locks.
