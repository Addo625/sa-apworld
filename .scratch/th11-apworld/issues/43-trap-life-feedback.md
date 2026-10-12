# 43: Traps and links that change lives update the HUD (and make a sound)

Status: ready-for-agent
Blocked by: 42

## Problem
In batch 32 the human found that `+1 Life` from an item plays the extend sound and redraws the lives stars (40's cave), but the `-1 Life` trap (and lives changed by DeathLink or RingLink) changes the value silently, and the HUD stays stale until the next life change. The human wants the same feedback for traps ("copy the 1-up logic"). Lives already can't go below 0 (`max(lives − 1, 0)` in `traps.py`).

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_trap_life_requests_redraw` and `test_trap_life_never_negative`.

## Test plan
- `traps.tick` and the link handlers request the cave's lives-star redraw whenever they change lives. Add a sound ID for "life lost" if SA has a suitable one (find it next to the extend sound in 40's notes), or redraw without a sound.
- `test_trap_life_requests_redraw`: a `-1 Life` trap at 3 lives → lives 2 written, plus one redraw request.
- `test_trap_life_never_negative`: at 0 lives → no write, no redraw.
- Respects `/itemsound`: off → value only, as today.

## Steps
1. The redraw request path and tests. Run the DoD.
2. Add an in-game check to the open probe batch: `/send` `-1 Life` → the stars update at once.

## Deferred
- None.
