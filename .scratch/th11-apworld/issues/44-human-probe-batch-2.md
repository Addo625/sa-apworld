# 44: [human] Probe batch 2

Status: ready-for-human
Blocked by: 42

## Problem
In-game facts for tickets 33, 35, 36, 40, 42 and 43, collected so the human answers them in one session (AGENTS.md: "In-game facts go to the probe batch"). Agents append `R<n>` requests while this batch is open. It's blocked by 42 because R1 needs 42's `/writelog`. Claude prepares a simplified checklist (`.agent-loop/44-simplified.md`) before the session.

## DoD
Every request below has its pasted output under `## Comments`, or "not reached".

## Test plan
Session setup: as in batch 32. One `th11.exe`, the client from the latest `main`, game folder `.games/sa` (everything unlocked) unless a request says otherwise.

### R2, needed by 40 (from batch 32 R9-S3, mistyped there): the hook bytes
- With `/itemsound on` and one item sound played: `/peek 429058 5` → paste (expect `e8 a3 1e 06 00`).

### R3, needed by 33 (done, proof only): a received Extra Stage item opens Extra
Context: 33 found the unlock by static disassembly. Every Extra menu tests bit `0x10` of one byte per shot at `[0x4A8EBC] + 0x2DDF0` (Reimu A..C, Marisa A..C); the client sets that bit for each received shot whose Extra item is in. Run from **`.games/fresh`** (no Extra anywhere). **Back up `.games/fresh/scoreth11.dat` first**: the game saves the unlock on exit. Needs a seed with `extra_stage: apart`, `stage_unlock: by_shot_type`, `shot_type: true`, and admin `/send`.
- **X1:** connected, on the title screen, before any Extra item: `/probe`, paste the `ADDR_EXTRA_UNLOCK` line, then `/peek <its addr> 6` and paste (expect bit `0x10` clear in all six). Is `Extra Start` on the title menu?
- **X2:** `/send <your slot> [<your start shot>] Extra Stage` (e.g. `[Reimu B] Extra Stage`). Within a second, `/peek <addr> 6` again and paste (expect `+0x10` on that shot's byte only). Is `Extra Start` there now? Open it: is only that shot offered on the character and shot screens?
- **X3:** play Extra to Sanae's midboss: paste the client lines (expect the `Sanae - Midboss` check).
- Afterwards restore the backed-up `scoreth11.dat`.
- Used for: the in-game proof of 33. If `Extra Start` doesn't appear in X2 while the bit is set, reopen 33 with the pasted bytes (the title may cache its menu: also try leaving to the title and back).

### R4, needed by 35 (done, proof only): the speed traps, once each
Context: 35 found the speeds by static disassembly, not in batch 32's `/playerfloats` (they aren't floats). SA keeps four int32 = speed × 128 in the player object: `ADDR_SPEED_NORMAL/FOCUS/NORMAL_D/FOCUS_D` = player + `0x890/0x894/0x898/0x89C`. Reuse a seed with `traps: 100` and admin `/send` (R3's works). Game folder `.games/sa`, Practice, any stage, in play.
- **V1:** `/probe`, paste the four `ADDR_SPEED_*` lines (expect positive values around 200–700, focus below normal, diagonal ≈ normal × 0.7).
- **V2:** `/send` each, waiting for the previous one to end: `No Focus` (20 s, focus moves at full speed), `Reverse Movement` (20 s, controls reversed), `Aya Speed` (20 s, unfocused twice as fast, focused half), `Freeze` (3 s, no movement). Paste the `Trap: …` lines and one line per trap on what you saw. After each ends, does movement feel normal again?
- **V3 (leaving a run):** `/send` `Reverse Movement`, and within its 20 s clear the stage (Practice ends at the stage end) or lose every life. Start a new Practice stage: does it move normally? Paste `/probe`'s four `ADDR_SPEED_*` lines there (expect V1's values).
- Used for: the in-game proof of 35. Wrong movement in V2 reopens 35 with the pasted lines. If V3's new stage still moves reversed, the stage doesn't rebuild the speeds, and `traps.tick` must restore them on the first in-run tick instead (a follow-up ticket).

## Decisions to confirm
- (33) The client only sets the Extra bit, it never clears one: a save with Extra already open (like `.games/sa`) keeps every shot's Extra, and Extra runs there send checks without the item. Filtering those runs is deferred ticket 45. In normal mode a `linear` Extra is left to the game (a no-continue clear on Normal+ opens it); only `apart`'s Extra Stage items write the bit. Note that logic (11) counts that `linear` Extra as open once Stage 6 is, but the game needs a no-continue clear. If that's too strict, the client could set the bit once a Stage 6 Clear check is sent.

## Steps
1. Do the setup, then every `R<n>` in order. Paste each under `## Comments`, labeled `R<n>`.
2. Set `Status: done`; the follow-ups unblock.

## Deferred
- None.

## Comments
