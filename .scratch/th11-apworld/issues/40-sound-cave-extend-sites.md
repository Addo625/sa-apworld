# 40: Find SA's sound cave and extend routine (static analysis)

Status: ready-for-agent
Blocked by: 29

## Problem
29 built the item-sound plumbing (`receive.sound`, `TouhouContext.play_sound`), but the sound only plays once SA has MoF's code cave: `Variables.ADDR_CUSTOM_SOUND_ID`, `ADDR_SOUND_HACK_1/2`, their `EXPECTED_BYTES`, and `SOUND_IDS` are all `None`, so the client logs "pending the sound cave (ticket 40)". The HUD still doesn't redraw on a received `+1 Life`. Finding both needs a disassembly of `.games/sa/th11.exe` (v1.00a). The unattended 29 run couldn't do it: `objdump`, `xxd` and ad-hoc `python` aren't in `.claude/settings*.json`, so they need approval.

**Human:** either run this ticket interactively, or add `Bash(objdump:*)` (macOS objdump is llvm-objdump and reads PE/i386) to `.claude/settings.json`, then relabel `ready-for-agent`.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, with the sound cave sites and IDs sourced (non-`None`) and the cave installed through `safe_patch`. In-game confirmation goes to the open probe batch.

## Test plan
- **Static analysis notes** (ticket comments): SA's play-sound function (MoF's cave calls `0x43DC90` with `ecx = 0x492590`, the sound manager, and the ID in `edi`), a per-frame hook site analogous to MoF `0x413683` (the cave entry `cmp [id],0x30; jne`), a spare zeroed `.data` dword for the sound ID, and SA's sound IDs for extend, power-up and menu ok. Cross-check thprac `thprac_th11.cpp` hooks around `0x4311xx`/`0x432Axx`.
- **Cave install**: `TouhouContext` installs the cave once per game process (like `patch_continue_lives`) with `safe_patch` on each site, built from `base_address + ADDR_CUSTOM_SOUND_ID`. Test with `FakeMemory`: correct bytes on match, nothing written on `PatchMismatch` (error logged, sound stays off). The existing `test_patch_sites_have_expected_bytes` and `test_patch_sites_dont_overlap_thcrap` then cover the sites.
- **HUD** (best effort, planner lead): the extend routine at `0x420951`–`0x420962` (`mov eax,[0x4A5718]; inc eax; cmp eax,9; …`). Find its function start; if the HUD redraws only through it, either call it from the cave for `+1 Life` (sound kind `extend` → call extend instead of writing `ADDR_LIVES`) or find the HUD's own lives copy near the player object (`0x4A8EB4`) and write it with `ADDR_LIVES`. If neither is found, record that; the sound stays the feedback.

## Steps
1. Disassemble, write the notes and candidate bytes into the comments.
2. Fill `Variables` (addresses, `EXPECTED_BYTES`, `SOUND_IDS`), add the cave install and its tests. Green.
3. HUD part if found, with a test. Add a probe batch request: `/send <slot> +1 Life` in a Practice run plays the sound (and redraws lives).

## Deferred
- In-game check via the probe batch (step 3).

## Comments

- 2026-10-10 al-work (29): created; 29 shipped the plumbing with every sound entry `None`.
- 2026-10-10 human (via Claude): allowed `Bash(objdump:*)` in local settings. Back to ready-for-agent.
