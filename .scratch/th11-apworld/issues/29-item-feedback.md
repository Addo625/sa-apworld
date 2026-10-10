# 29: Show received items in game (sound, HUD refresh)

Status: ready-for-agent
Blocked by: 08

## Problem
09 showed that a received `+1 Life` raises the lives value, but the HUD only redraws on the game's own life change, and nothing is audible, so the player can't tell an item arrived. Both reference worlds play a game sound on item receipt. MoF (same engine family) patches a code cave (`initSoundHack`: `ADDR_SOUND_HACK_1/2`) that plays the sound ID written to `ADDR_CUSTOM_SOUND_ID` (`ref-projects/mof-apworld/gameController.py`, `Variables.py:105, 476-477`). Priority: above 30 (Demo Play).

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below. In-game confirmation is a human step in this ticket's comments (Deferred).

## Test plan
- **Sound** (MoF port):
  - Find SA's sound-play function and a hook site by static analysis of `.games/sa/th11.exe` (v1.00a): compare MoF's hack bytes and call pattern, and cross-check thprac's th11 hooks (`thprac_th11.cpp`, which patches around `0x4311xx`/`0x432Axx`).
  - Every patch site records `EXPECTED_BYTES` and goes through 04's `safe_patch`. The thcrap overlap test must still pass.
  - `receive.apply_new` returns, besides writes, a sound request per item kind: life/extend sound for `+1 Life`, power-up for power, a menu "ok" sound for unlock items.
  - Tests: `test_sound_patch_sites_guarded`, `test_sound_requested_per_item`, `test_sound_patch_sites_dont_overlap_thcrap`.
- **HUD refresh** (best effort): if the HUD keeps its own copy of the lives (search near the player/HUD objects thprac names: `player` at `0x4a8eb4`), write it together with `ADDR_LIVES`. If static analysis can't find it, record that and leave the sound as the feedback.

## Steps
1. Static-analysis notes, with candidate addresses and bytes, written into the ticket comments.
2. Patch sites, sound trigger and tests. Green.
3. HUD copy if found, with a test. Run the DoD. Set `needs-human` for the in-game check (below) if the sites were only verified statically.

## Deferred
- **In-game check (human, after this ticket):** `/send Player1 +1 Life` plays a sound, and the lives row updates if the HUD part landed.

## Comments

- 2026-10-10 planner: lead from a static scan of `th11.exe`. `0x420951`–`0x420962` is the game's extend routine (`mov eax,[0x4A5718]; inc eax; cmp eax,9; mov [0x4A5718],eax; jle …; mov [0x4A5718],9`). Calling the game's own extend path for `+1 Life`, instead of writing the value, should redraw the HUD and play the extend sound. Find the function start and a safe way to invoke it (a code cave or a hook that runs on the game thread, as MoF's sound hack does) before porting the sound hack.
