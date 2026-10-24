# 72: A retry before any score still restarts the run's power

Status: ready-for-agent
Blocked by: None

## Problem
Playtest (human): very rarely, a restart started with full power. `detect.restarted` spots a Practice retry by the score dropping or lives coming back from -1. A retry made before scoring anything goes from score 0 to 0, so it's missed and the game's own 4.00 (Stage 2+) stays.

## What to do
- `detect.restarted`: in Practice play, also `prev.score == 0 and state.score == 0 and state.power > prev.power`. Collecting power always gives score, so power can't rise at score 0 in normal play.
- Test in `test_detect.TestRetry` and `test_client.test_retry_restarts_practice_power` (a zero-score retry sets the packs' power).

## Deferred
- None.
