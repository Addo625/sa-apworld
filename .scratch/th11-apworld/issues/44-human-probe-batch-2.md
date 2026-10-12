# 44: [human] Probe batch 2

Status: ready-for-human
Blocked by: 42

## Problem
In-game facts for tickets 33, 35, 36, 40, 42 and 43, collected so the human answers them in one session (AGENTS.md: "In-game facts go to the probe batch"). Agents append `R<n>` requests while this batch is open. It was blocked by 42 because R1 needs 42's `/writelog` (now in). Claude prepares a simplified checklist (`.agent-loop/44-simplified.md`) before the session.

## DoD
Every request below has its pasted output under `## Comments`, or "not reached".

## Test plan
Session setup: as in batch 32. One `th11.exe`, the client from the latest `main`, game folder `.games/sa` (everything unlocked) unless a request says otherwise.

### R1, needed by 42 → 40: does the boss dialog crash without the sound hook?
Context: 42's disassembly found nothing wrong with the hook (see 42's comment): it replaces exactly one `call 0x44A340`, nothing jumps into its middle, and while no item sound is pending the cave is only `pushad; test; jz; popad; jmp 0x44A340`. So a crash at the dialog with **no** sound pending points away from the hook. Game folder `.games/sa`, any connected seed with admin `/send`, Practice Stage 1.
- **(a) never hooked:** start a **fresh** `th11.exe` (the hook stays until the game exits), connect, `/writelog on`. Do **not** turn on `/itemsound`. Play Practice Stage 1 to Yamame's pre-boss dialog and click through it into the fight. Crash? Paste the last 20 client lines (with the crash, they end in `Lost th11.exe`).
- **(b) hooked:** quit and start a fresh `th11.exe`, connect, `/writelog on`, `/itemsound on`. Early in Practice Stage 1, `/send <your slot> +1 Life`: hear the extend sound? Then `/peek 429058 5` (this is R2). Play to Yamame's dialog **without** further `/send`s, click through it. Crash? Paste the last 20 client lines and say how long before the crash the last item arrived.
- **(c) sound during the dialog** (only if (b) didn't crash; same game, `/itemsound` still on): restart Practice Stage 1 from the pause menu, play to Yamame's dialog, and while its text is up `/send <your slot> +1 Life`. Sound, star redraw, crash? Paste the last 20 client lines.
- Used for: (a), (b), (c) OK → 40 turns `/itemsound` on by default. (b) crashes, (a) doesn't → the installed-but-idle hook is to blame after all; 40 moves the hook to another site. Only (c) crashes → the cave's redraw call at the dialog (42's lead 2); 40 skips the redraw outside stage play. (a) crashes → not the hook: the last `write 0x…` lines name the client write to suspect; a new ticket from them.

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

### R5, needed by 36 (done, proof only): a received DeathLink kills the player
Context: MoF's kill jump isn't in SA (32 R5), so 36 found SA's player state by static disassembly: `ADDR_PLAYER_STATE` = player + `0x928`, 0 respawn, 1 play, 2 dying, 4 hit. A bullet sets 4; the game then takes the life after 8 frames unless the bomb key deathbombs. The client kills by writing 4 while it reads 1. `/receivedeath` stands in for another player's death. Game folder `.games/sa`, any connected seed, Practice, any stage, in play.
- **D1:** `/deathlink on`. In play, `/probe` and paste the `ADDR_PLAYER_STATE` line (expect 1).
- **D2:** `/receivedeath`. Within a second, does the player die (death explosion, one life fewer)? Is the death sound played? Paste the client lines: expect `DeathLink: test death received` and **no** `Sending death` (a received death isn't echoed). After the respawn, `/probe` again (expect 1).
- **D3 (deathbomb):** hold the bomb key, then `/receivedeath`. Does a bomb go off and save the player (no life lost), or does the player die anyway (expected, see Decisions)? If saved: release it; about 2 s later the client retries; does the player die then?
- **D4 (respawning):** `/receivedeath` twice within a second of each other, or right after a death: does the player lose exactly one life per `/receivedeath`, never two at once? Paste the lines.
- **D5 (boss dialog, last: it may crash):** Practice Stage 1, reach Yamame's pre-boss dialog with `/itemsound` off, `/receivedeath` while the text is up. Does the player die, does the dialog continue normally, does the game keep running? Paste the lines.
- Used for: the in-game proof of 36. No death in D2 reopens 36 with the `/probe` lines: the next lead is calling the hit routine `0x432A90` (player in `eax`) through a code cave, which waits on 42.

## Decisions to confirm
- (33) The client only sets the Extra bit, it never clears one: a save with Extra already open (like `.games/sa`) keeps every shot's Extra, and Extra runs there send checks without the item. Filtering those runs is deferred ticket 45. In normal mode a `linear` Extra is left to the game (a no-continue clear on Normal+ opens it); only `apart`'s Extra Stage items write the bit. Note that logic (11) counts that `linear` Extra as open once Stage 6 is, but the game needs a no-continue clear. If that's too strict, the client could set the bit once a Stage 6 Clear check is sent.
- (36) A received DeathLink skips the hit itself: no hit sound or flash, and the deathbomb window only if the player's frame timer (player + `0x948`) is still under 8, which it likely isn't. The death routine plays its own explosion. If R5 D2 looks too abrupt, a cave calling the hit routine `0x432A90` gives the full hit (after 42).
- (36) It also skips the collision path's guards (`0x431EA6`–`0x431EDB`): respawn invincibility (player + `0x8BB4`), a running bomb, player + `0x8BC4` bit 2, and an unknown HUD flag `[0x4A8D84] + 0x4438`. So a received death kills even while invincible or bombing, like a DeathLink should. If R5 D5 shows a kill during the boss dialog misbehaves, the client must also read that flag (a follow-up).

## Steps
1. Do the setup, then every `R<n>` in order. Paste each under `## Comments`, labeled `R<n>`.
2. Set `Status: done`; the follow-ups unblock.

## Deferred
- None.

## Comments
