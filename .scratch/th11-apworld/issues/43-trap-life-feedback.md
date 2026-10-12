# 43: Traps and links that change lives update the HUD (and make a sound)

Status: done
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

## Comments

- 2026-10-12 al-work (43): done. A `-1 Life` trap that writes lives plays `SOUND_IDS["life_lost"]` = `0x04` (`se_pldead00`, from the sound table `0x4A34F0`) through `play_sound`; the cave redraws the stars after any sound, so no new cave code. `/itemsound off` → value only. DeathLink lowers lives through the game's own death (its sound and HUD), RingLink changes only power, so neither needed a hook. Same-tick `+1 Life` and `-1 Life` write two IDs; the cave may play only the second (the redraw still happens). DoD: `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → 385 passed. In-game check: probe batch 44 R6; the sound choice is under its Decisions to confirm. No follow-up ticket (a wrong R6 reopens 43).
