# 65: [human] Probe batch 7: the crash ~1 s after a midboss

Status: done
Blocked by: None

## Problem
2026-10-21 (human): the game crashed twice ~1 s after beating Kisume (Stage 1 midboss), once with a spell capture; once it froze while a Practice stage loaded. The client logs show "Lost th11.exe" ~55 s later, which is when Wine's crash dialog was closed. In that second, the client applied the midboss check's item:
- 23:38: `+0.50 Power`, then a power write and the item sound;
- 23:41: a power write with no item and no sound, i.e. a "run start/retry" write, possibly a false retry detection mid-stage;
- 00:17: `Next Stage`, then a Practice table write and the first sound in that game process, which installs the sound code with the game paused.

No single client action is common to all three. The faulting address decides the fix.

## Test plan
Setup: the client from the latest `main` (Claude reinstalled it), `/writelog on`. The client now also logs `Run start (...)` lines and `Applied: <items>`.

### R1: the faulting address
When the game crashes, Wine's "Program Error" dialog → **Show Details**: paste the first ~20 lines (`Unhandled exception: ... at address 0x...`, the registers, the backtrace). If there's no dialog, start the game with `WINEDEBUG=err+all ~/archipelago/wine.sh custom.exe` and paste the terminal's last lines.

### R2: with item sounds on
Practice Stage 1: beat Kisume (capture her card if you can), ×3 or until it crashes. Paste the client lines from 5 s before each midboss to 5 s after.

### R3: with item sounds off (A/B)
`/itemsound off`, restart the game, and repeat R2 ×3.

### R4: the loading freeze
If a stage freezes while loading, paste the client lines just before it.

## What the answer decides
- Fault in the sound code (`0x48AF00`-`0x48AF2E`) or the HUD stars (`0x41A060`-`0x41A0ED`): drop the HUD redraw, or turn sounds off by default again (40).
- A `Run start (retry ...)` line mid-stage: `detect.restarted` misfires (62); fix its signal.
- Crashes in R3 too, elsewhere: Wine itself; look at the Wine setup.

## Comments
- 2026-10-21 Claude: no crash in this session, and no client write or log line tied to the earlier ones. The crashes are inconsistent; revisit on Windows (17) or when one comes with Wine's fault address.
