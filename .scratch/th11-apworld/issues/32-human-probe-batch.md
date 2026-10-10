# 32: [human] Probe batch 1

Status: ready-for-human
Blocked by: 09

## Problem
In-game facts the agents can't get themselves, collected so the human answers them all in **one** game session (AGENTS.md: "In-game facts go to the probe batch"). Agents append `R<n>` requests here while this batch is open.

## DoD
Every request below has its pasted output under `## Comments`, or the note "not reached". `## Decisions to confirm` has a yes or a change for each item.

## Test plan
Session setup (once):
1. Close every game, then start one game through `custom.exe`. Check that only one `th11.exe` runs (`~/archipelago/wine.sh tasklist 2>/dev/null | grep th11`).
2. Start the client: `cd ~/archipelago/install-wine && ../wine.sh explorer /desktop=AP,1280x800 ArchipelagoLauncher.exe "Touhou SA Client"`.
3. Use the apworld from the latest `main`: `tools/build_apworld.sh && cp dist/th11.apworld ~/archipelago/install-wine/custom_worlds/`.

### R1, needed by 33 (from 11): where SA stores the Extra unlock per shot type
Context: `ADDR_EXTRA_UNLOCK` is `None`. The only lead is thcrap's `fix_extra_stage_relocking` patch at `Rxede8`. 27's practice table has no Extra row.
- **E1:** with a save where at least one shot has Extra and one doesn't, run `tools/scoredat.py` and paste the `CR` chunk's clear counts per shot (the 5 counts after play time; the 5th level is Extra).
- **E2:** in the running game, `/memsearch` the save struct around 27's copy 1 (`…1BB8`) for the field E1 points at; paste matches.
- **E3:** change that byte (with `/poke <addr> <hex byte>`) for a shot without Extra, open the Extra menu, and note whether the shot is now offered.

### R2, needed by 34 (from 12): continue lives come from received `+1 Life` items
Context: 34 found the site by static disassembly. A continue re-runs the game init, whose non-Practice branch sets lives; the client rewrites that store (`base + 0x1FA38`) to its own value, the number of `+1 Life` received (capped by `limit_lives`). The same branch also sets a new run's starting lives. Needs a `normal_static` or `normal_dynamic` seed and R4's `/send` (admin).
- **C1:** connected, `/send` yourself `+1 Life` three times. Start (not Practice) a run, Stage 1, in play: `/probe`, paste the `ADDR_LIVES` line (expect 3). Watch the stage-start loading screen: anything odd?
- **C2:** lose every life, choose to continue: `/probe`, paste `ADDR_LIVES` and `ADDR_CONTINUES` (expect lives 3, continues 1).
- **C3:** `/peek 41FA38 8` and paste (expect `b8 03 00 00 00 eb 17 90`). This assumes th11 loads at 0x400000. If `/probe` shows `ADDR_LIVES` somewhere other than `0x004A5718`, peek at that address − 0x85CE0 instead.
- Used for: confirms `ADDR_NORMAL_CONTINUE_LIVES` in 34. If C1 or C2 shows 2 lives, the init isn't the continue path; reopen 34 with the pasted values.

### R3, needed by 35 (from 13): the player's speed fields
Context: the speed traps rewrite four speed floats (normal, focus, normal diagonal, focus diagonal); in MoF they sit at player + 0x3D4..0x3E0. SA's player pointer is `ADDR_PLAYER_PTR` (from thprac), the fields are unknown.
- **P1:** Practice, Stage 1, **Reimu A**, in play. Run `/playerfloats` and paste the whole output.
- **P2:** same with **Marisa B** (another speed): `/playerfloats`, paste. The speed fields are the ones that differ between P1 and P2 and come in normal/focus pairs, focus about half of normal, diagonal about normal × 0.707.
- **P3:** for the best candidate of the normal speed, `/poke <its addr> 00000000` while holding no focus: does unfocused movement stop (focused still works)? Paste the line and the answer. If the candidates are unclear, skip P3; the agent picks from P1/P2.
- Used for: `ADDR_SPEED_*` = `[ADDR_PLAYER_PTR, offset]` in 35.

### R4, needed by 35 (from 13): each trap once
Context: traps fire 2 s into a run. Needs a seed with `traps: 100` (all filler are traps) and the AP server's `/send` (as admin: `/send <your slot> <item>`).
- In a Practice stage, `/send` each one, waiting for the previous to end: `-50% Power`, `-1 Life`, `Power Drain`, and, only once 35 is done, `No Focus`, `Reverse Movement`, `Aya Speed`, `Freeze`.
- Paste the client log lines (`Trap: …`) and one line per trap on what you saw. Note anything that felt wrong (too long, too short, too harsh).
- Used for: closing out 13's in-game check; durations feed the decisions below.

### R5, needed by 36 (from 14): the kill site, and DeathLink sends
Context: a received DeathLink kills the player by NOP-ing, for 0.1 s, the jump that skips the hit (EoSD/MoF `setKill`; MoF's is `e9 dc 02 00 00` at base + 0x25A91). SA's `ADDR_KILL_CONDITION` is `None`. SA is built on MoF's engine, so the same jump may exist. Reuse R4's seed and connection.
- **K1:** at the title screen, `/memsearch e9dc020000` and paste the output.
- **K2:** for each match whose `base + 0x…` offset is below `0xA0000` (game code), `/peek <match minus 0x20, hex> 64` and paste.
- **K3:** in a Practice stage, for each K2 match: `/poke <match> 9090909090`, note whether the player dies (at once or on the next bullet touch), then **at once** `/poke <match> e9dc020000` to restore. Paste the lines and what happened. Skip if K1 has no match.
- **K4:** `/deathlink on`, then in a Practice stage lose a life: paste the client lines (expect `DeathLink: Sending death to your friends...`). Then in a full run (Start, not Practice) with more lives than it starts with (collect pieces or `/send` `+1 Life`), pause → **Restart**: does the client send a death? Same with a Practice stage after losing a few lives. Paste the lines.
- **K5:** `/deathlink_trigger game_over`, then lose every life in a Practice stage. On the game over screen, `/probe` and paste it; paste whether the client sent a death.
- Used for: `ADDR_KILL_CONDITION` and its `EXPECTED_BYTES` in 36 (K1–K3); K4 confirms sending works and that a restart isn't taken for a death (if it is, 36 adds a guard); K5 confirms the game over send (`ADDR_ENEMY_MANAGER` there decides whether `on_state`'s torn-down-stage case is needed).

### R6, needed by 38 (from 16): the shot select cursor, and the menu guard
Context: 16's guard moves the menu cursor off locked content. It is on for the difficulty select (menu 1, cursor Easy 0 .. Lunatic 3) and off for the shot select: probe 06 S2 saw character select as menu 3 with cursor 1 on Marisa B, which fits both "the cursor is the shot" and "the cursor is the character". Use a seed whose start inventory has one shot type (not all six), receive no Lower Difficulty, and stay connected: only Lunatic is open (Hard and Lunatic with `exclude_lunatic`).
- **M1:** Start (not Practice), on the character screen: `/probe` with the cursor on Reimu, then on Marisa. Then pick Marisa and on the partner screen (if SA has a separate one) `/probe` on A, B and C. Paste the `ADDR_MENU`, `ADDR_MENU_CURSOR`, `ADDR_CHARACTER` and `ADDR_SHOT_TYPE` lines of each, labeled with the screen and the highlighted choice.
- **M2:** on the difficulty select, try to move the cursor onto Easy, Normal and Hard. Does the highlight jump back to Lunatic? Confirm one: which difficulty starts? Paste `/probe`'s `ADDR_DIFFICULTY` line in the stage.
- **M3:** in Practice on Lunatic, pick a shot type you don't have and play to Stage 1's midboss and past it. Paste the client lines; expect no check sent. Then the same with the shot you have: expect the check.
- Used for: `Variables.MENU_SHOT` in 38 (M1); M2 confirms that writing `ADDR_MENU_CURSOR` moves the selection (if not, the guard needs MoF's cursor hack); M3 confirms 16's locked-content filter.

### R7, needed by 39 (from 28): which practice-table copy the game reads, and the static pointer to it
Context: 27 found the practice table twice on the heap; both move every launch. Copy 1 (page offset `…215C`) is likely the live save struct, copy 2 (`…05C4`) the decoded file buffer. Use 27's save (Reimu A, Normal Stages 1–2 cleared, Stage 3 locked) or note which save you use. Do R7 before R3's poke and before R1's E3, so no other poke is in memory.
- **U1:** with the Practice menu open (as in 27's M1), `/memsearch 00000000010100000000000001010000` (Normal Stages 1–2 cleared and unlocked; with another save, use its line from `tools/scoredat.py`). Paste the matches. For each match `M`, the table is `M − 0x30` and its chunk starts at `M − 0x5D4`.
- **U2:** for each match, `/ptrscan <M − 0x30, hex>` and paste. If a match lists 0 pointers, also run `/ptrscan <M − 0x30> 8000` and paste.
- **U3:** for each match, `/peek <M − 0x5D4> 16` and `/peek <M − 0x5D4 + 0x68D4> 16`, and paste. Expect `43 52` ("CR") at the start of both, with the shot index (00, then 01) at byte 12, if the copy keeps the file's chunk order.
- **U4 (write test):** `/poke <copy 1's M + 0x15> 01` (Normal Stage 3 `unlocked`), open Practice → Reimu A → Normal: is Stage 3 offered? Paste the line and the answer. If not, `/poke` the same byte back to `00`, do the same on copy 2's match, and answer again. Afterwards poke every changed byte back to `00` before quitting, since the game may write the save on exit.
- Used for: `ADDR_PRACTICE_UNLOCK` (pointer chain to the copy that U4 shows the menu reads) and the per-shot chunk stride, in 39.

### R8, needed by 41 (from 30): a flag that is set only while a replay plays
Context: the title's Demo Play replays a run, and the client takes it for play (a demo sent a "midboss Orin" check). `ADDR_IN_DEMO` is `None`. The candidate is thprac's replay manager pointer, `ADDR_REPLAY_MGR_PTR` (`0x4a8eb8`), but the game may also keep it for recording during normal play. Fits any time; the demo needs the title screen, no seed.
- **D1:** on the title screen, wait (no input) until a demo starts. During the demo, `/probe` and paste the whole output.
- **D2:** in a run you start yourself (Start, Stage 1, in play), `/probe` and paste it. Then the same in Practice, Stage 1 (R3's P1 state works).
- **D3:** (optional) watch a saved replay from the Replay menu, `/probe` during it, paste it.
- Used for: `ADDR_IN_DEMO` in 41: an entry that is non-zero in D1 (and D3) and zero in both D2 runs. `ADDR_REPLAY_MGR_PTR` qualifies if it is non-zero in D1 and 0 in D2; otherwise the agent compares `ADDR_GAME_FLAGS` and the other lines.

### R9, needed by 40 (from 29): received items play a sound and redraw the lives
Context: 40 found SA's play-sound function by static disassembly. On the first received item with a sound, the client writes a code cave into `.text`'s zero slack (`base + 0x8AF00`) and hooks the per-frame sound update (`base + 0x29058`); the cave plays the sound ID the client writes to `base + 0xCAF00` and redraws the lives stars. Reuse R4's seed and connection (`/send` as admin). Fits right after R4, in a Practice stage, in play.
- **S1:** `/send <your slot> +1 Life` with fewer than 9 lives: do you hear the extend sound, and does the HUD show one more star? Paste the client lines.
- **S2:** `/send` `+0.05 Power` (power-up sound?), then a shot type you don't have yet or `Lower Difficulty` (menu "ok" sound?). One line each on what you heard.
- **S3:** `/peek 429058 5`, `/peek 48AF00 46` and `/peek 4CAF00 4`, paste all three (expect `e8 a3 1e 06 00`, the cave starting `60 8b 35 00 af 4c 00`, and `00 00 00 00`: the sound ID dword is mapped and the cave zeroed it).
- **S4:** close and restart the client (game still running), reconnect, `/send` `+1 Life` again: sound and star as in S1, and no "unexpected game code" error? Paste the lines.
- Used for: confirms `ADDR_SOUND_HACK_1/2`, `ADDR_CUSTOM_SOUND_ID` and `SOUND_IDS` in 40. A crash, silence or a wrong sound reopens 40 with the pasted lines; a missing star with the sound working means the HUD tail call needs another look (40's notes).

## Decisions to confirm
- (13) Trap durations: No Focus, Reverse Movement and Aya Speed 20 s, Freeze 3 s, Power Drain −0.05/s for 20 s. EoSD keeps them until the stage ends; MoF's Aya Speed is ×4/÷4, here ×2/÷2. Only one speed trap at a time; the next waits.
- (13) Trap weight defaults copied from EoSD (−50% Power 20, −1 Life 0, No Focus 20, Reverse 20, Aya 20, Freeze 5, Power Drain 15); `traps` defaults to 0 %.
- (14) DeathLink amnesty N forgives N deaths and sends the next (N = 2: every third death). EoSD sends when the count reaches N, so its 0 and 1 both send every death.
- (14) A DeathLink received outside a run waits and kills the player in the next run (EoSD drops it on entering a stage). The next life lost after a received one is never sent, even if the player died on their own first. A kill that takes no life (bomb, respawn invincibility) is retried every 2 s.
- (14) A received DeathLink while the kill site is unknown (until 36) is only logged; it doesn't wait.
- (15) RingLink sends every power change the game makes in a run, one ring per 0.05 power (MoF's unit). A bomb costs 1.00 power in SA (none in MoF), so each bomb sends −20 rings, and a death sends its power loss too. Rings received outside a run are dropped (MoF).

- (16) `limit_lives` is 0–9, default 9 (SA's max; EoSD's is 0–8, default 8). It caps +1 Life and a normal-mode continue, but never takes lives away (a Practice run starts at 9 whatever the limit).
- (16) A run on a locked shot type or difficulty sends no checks, but counts as a run so the stage's later checks stay aligned. Before connecting, or before the first received items arrive, nothing is filtered (the items are unknown), so those runs' checks are sent on connect.
- (16) The difficulty guard moves the cursor to the nearest unlocked difficulty on every menu with id 1. If another screen also has id 1 (not seen in 06), its cursor would be moved too.

- (34) In the normal modes, the `+1 Life` count also sets the starting lives of every new run, Extra included (vanilla: 2), not only lives after a continue. The game sets both with one instruction, and MoF's patch site does the same. No `+1 Life` received means 0 lives (just the current one) at the start and after a continue.

- (40) Each tick plays at most one item sound (extend > power-up > ok), and the lives stars are redrawn only with it: lives changed by a trap or RingLink (no sound) stay stale on the HUD until the game redraws them.

- (30) A replay counts as not playing, not only for checks: no DeathLink or RingLink sends, no traps or items applied during one (items wait for the next real run). A saved replay watched from the Replay menu is treated the same, if the flag covers it.

## Steps
1. Do the session setup, then every `R<n>` in order. Paste each one's output under `## Comments`, labeled `R<n>`.
2. Answer `## Decisions to confirm`. Set `Status: done`; the follow-ups unblock.

## Deferred
- None.

## Comments
