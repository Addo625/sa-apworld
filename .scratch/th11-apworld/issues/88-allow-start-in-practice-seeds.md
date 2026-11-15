# 88: Start runs in a Practice seed send checks

Status: done
Blocked by: 87

## Problem
85 (D3, after D2 and the continue design in 87). Players reach for Start by habit (playtest 3: Janania). With continues voiding a stage's checks (87), a Start run is as fair as Practice, so it can count.

## DoD
- `pytest worlds/th11/test -q` passes with the tests below.
- In game (batch 74 R3): a Practice seed's Start run sends the checks of every stage that is open for the shot type, sends nothing for locked stages, and the log names each locked stage when play enters it.

## Design
- `detect.locked` drops the Start branch. The stage, shot type and difficulty locks still apply per stage, so with progressive unlocks a Start run is useful up to the first locked stage.
- The client announces a locked stage when a run starts **or** play enters a new stage (a Start run moves on by itself). It logs the same "isn't unlocked" line and buzzes (86).
- Lives and power: Start already takes the patched non-Practice run init (the item lives, `Client.py:236`); the power patch runs in the same init. Whether a stage change re-runs the init (resetting to the item power) or carries power over goes to batch R3. Either is acceptable; the logic is unchanged and Start is never required.
- Docs: `Options.py`/README lines that say Start sends nothing in Practice seeds.

## Test plan
- `test_detect.test_practice_seed_ignores_start_runs` becomes: a Start run in a Practice seed is not locked for an open stage, and is locked (`"<shot> Stage N"`) for a closed one.
- `test_client`: a Start run's stage change into a locked stage logs and buzzes once; into an open stage, nothing.

## Steps
1. `detect.locked`: remove the Start branch; update its tests.
2. `Client.poll`: run the lock announcement on a stage change within a run too. Fix the comment at `Client.py:236`.
3. Docs, tests, install. Batch 74 R3 covers the in-game check.

## Deferred
- None.

## Comments
- 2026-10-25 Claude: done. A locked stage entered mid-run logs "this stage sends no checks" and buzzes. Power at each stage start in a Start run goes to batch 74 R3.
- 2026-11-15 Claude: batch 74 R3 confirmed it in game.
