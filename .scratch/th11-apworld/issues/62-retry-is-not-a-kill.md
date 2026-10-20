# 62: A retry or game over never sends boss checks, and a Practice retry starts a fresh run

Status: done
Blocked by: 61

## Problem
Batch 61: retrying during Yamame (and in S2) sent `Yamame Defeated` + `Stage 1 Clear`, and Give up and Retry started at the game's 4.00 power. At a game over, lives read -1 with the boss still up (61 R4); a retry restores lives and drops the boss field, which `step` counted as a kill. A retry never leaves play, so the client's run start (60) never fired.

## What to do
- `GameState.score` (`ADDR_SCORE`). `detect.restarted`: in Practice play, lives back from -1 or the score dropping.
- `step`: a boss drop at or right after a game over, or on a restart, is a quit; a restart resets the stage's run count.
- `Client.poll`: a restart is a run start (power, waiting items).
- Tests: `test_detect.TestRetry`, `test_client.test_retry_restarts_practice_power`.

## Deferred
- None. Also closes 57 (normal-mode boss loss: the drop right after lives -1 is now a quit).
