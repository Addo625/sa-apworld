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
- **E3:** change that byte (with 28's `/poke`, once it exists, or a memory editor) for a shot without Extra, open the Extra menu, and note whether the shot is now offered.

(R2 is reserved for 34's continue-lives check.)

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

## Decisions to confirm
- (13) Trap durations: No Focus, Reverse Movement and Aya Speed 20 s, Freeze 3 s, Power Drain −0.05/s for 20 s. EoSD keeps them until the stage ends; MoF's Aya Speed is ×4/÷4, here ×2/÷2. Only one speed trap at a time; the next waits.
- (13) Trap weight defaults copied from EoSD (−50% Power 20, −1 Life 0, No Focus 20, Reverse 20, Aya 20, Freeze 5, Power Drain 15); `traps` defaults to 0 %.
- (14) DeathLink amnesty N forgives N deaths and sends the next (N = 2: every third death). EoSD sends when the count reaches N, so its 0 and 1 both send every death.
- (14) A DeathLink received outside a run waits and kills the player in the next run (EoSD drops it on entering a stage). The next life lost after a received one is never sent, even if the player died on their own first. A kill that takes no life (bomb, respawn invincibility) is retried every 2 s.
- (14) A received DeathLink while the kill site is unknown (until 36) is only logged; it doesn't wait.

## Steps
1. Do the session setup, then every `R<n>` in order. Paste each one's output under `## Comments`, labeled `R<n>`.
2. Answer `## Decisions to confirm`. Set `Status: done`; the follow-ups unblock.

## Deferred
- None.

## Comments
