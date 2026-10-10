# 40: Find SA's sound cave and extend routine (static analysis)

Status: done
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
- 2026-10-10 al-work (40): static analysis notes (llvm-objdump of th11.exe v1.00a; relocations stripped, base fixed at 0x400000):
  - **Play sound:** `0x44A1E0`, ID in `esi`; queues it in the 12-slot table at `0x4C44A0` (-1 = free), preserves `edi`, clobbers `eax/ecx/edx`. A positional variant `0x44A260` takes the ID in `edi`. Not MoF's `ecx = sound manager` convention.
  - **Sound IDs:** table at `0x4A34F0`, 8 bytes per ID, first dword = wav index into the name pointers at `0x4A36B0`. `0x2C` → se_extend (played by extend at `0x42096E`), `0x1D` → se_powerup (item pickup `0x423ABA`…), `0x0A` → se_ok00 (≈30 menu sites).
  - **Extend:** `0x420950` (no args): lives+1 capped at 9, else sound `0x2C` and the "Extend" popup (`0x41F010`); its tail `0x42098A` (`mov eax,[pieces]; mov edx,[lives]; push edi; mov edi,[0x4A8D84]; push eax; call 0x41A060; pop edi; ret`) is self-contained: `0x41A060` sets the 9 star sprites of the HUD object `[0x4A8D84]` from lives/pieces (`ret 4`). The cave calls that tail after each item sound, so the client keeps writing `ADDR_LIVES` (with `limit_lives`) and the HUD follows.
  - **Hook:** the supervisor's calc `0x429030` (registered at `0x429913`, runs every frame in all scenes on the game thread) calls the sound queue update `0x44A340` at `0x429058` (`e8 e3 12 02 00`); the client rewrites it to `call 0x48AF00`, and the cave ends `jmp 0x44A340`, so the queued sound plays the same frame. The other caller of `0x44A340` (`0x429653`) is shutdown.
  - **Cave / ID:** `.text` ends at `0x48AE15`, raw size 0x8A000: `0x48AF00` is zero slack in the mapped RX page. The ID dword is `0x4CAF00`, past `.data`'s virtual end `0x4CAE40` in its last RW page; no code references either. 0 = no sound (the slack starts zeroed, unlike MoF's 0x30 sentinel).
  - Known gaps (review): a mismatch at the hook site alone leaves the cave written in the slack (inert, nothing calls it), and the error repeats on each later sound; the cave reads then zeroes the ID, so a client write landing between the two is lost (one sound).
  - thcrap overlap test passes for both sites. thprac's source wasn't checked; its named hooks (`0x4311xx`/`0x432Axx`) are far from both.
- 2026-10-10 al-work (40): done. The commit `40: play a sound and redraw the lives stars for received items` sources `ADDR_CUSTOM_SOUND_ID`, `ADDR_SOUND_HACK_1/2`, `SOUND_IDS`, `SOUND_CAVE`/`SOUND_HOOK`; the client installs the cave through `safe_patch` on the first sound per game process. DoD: `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → 350 passed. In-game check: probe batch 32 R9 (a wrong result reopens 40; no follow-up ticket, like 34's R2).
