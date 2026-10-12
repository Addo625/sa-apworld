# 36: DeathLink kill site

Status: done
Blocked by: 32

## Problem
14 sends deaths and has the kill wired (`TouhouContext.kill`: NOP the kill site for 0.1 s, guarded by `EXPECTED_BYTES`), but `ADDR_KILL_CONDITION` is `None`, so a received DeathLink is only logged.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with `ADDR_KILL_CONDITION` sourced from 32 R5 (or, if R5 found no working site, a new probe-batch request and this ticket's note saying so).

## Test plan
- `Variables.ADDR_KILL_CONDITION` = the K3 address that killed, minus the image base; `EXPECTED_BYTES["ADDR_KILL_CONDITION"]` = its original bytes from K2 (the full jump, 5 bytes for `e9 rel32`, 6 for `0f 8x rel32`); source comment `probe 32 R5`.
- `test_patch_sites_dont_overlap_thcrap` passes with it (thcrap must not patch the same bytes).
- `test_deathlink.TestClientKill` already covers the patch/restore; switch its stand-in (`0x25A91`, `KILL_JUMP`) to the real entry and drop the `mock.patch`.
- `TestClientDeathLink.test_incoming_pending_without_kill_site` no longer applies: delete it, and drop the "pending … ticket 36" log in `on_deathlink`.
- K4: if a pause-menu Restart sent a death, guard it in `deathlink.on_state` (e.g. ignore a drop when the stage or power reset with it) with a test from K4's values.

## Steps
1. Read 32's R5 comments. No site that killed in K3 → add a request to the open probe batch for another lead (thprac's invincibility patch, a disassembly), set this ticket blocked by it, stop.
2. Set the entry and bytes, update the tests above.
3. K4 guard if needed.

## Deferred
- None.

## Comments

## Comments
- 2026-10-12 planner, **from batch 32 R5:** MoF's kill jump (`e9 dc 02 00 00`) doesn't exist in SA's code (the only match was in a Wine DLL). Sending works (K4a/K4b/K5 ✅). For receiving, kill by calling the game's own death path on the game thread through a code cave, like 40's sound cave (the cave mechanism plays sounds in game, but see 42 before reusing the same hook). Lead: the death routine around `dec dword [0x4A5718]` at `0x433D32` (static scan). Find its entry and preconditions statically, then add a batch 44 request: receive a DeathLink in a Practice stage → the player dies.
- 2026-10-12 al-work (36): static disassembly (`.agent-loop/th11.dis`, v1.00a):
  - `0x433D30` is a bare `dec [lives]; ret` with no callers (dead code). The real death is `0x4327D0` (player in `eax`): lives-1, bomb stock reset, HUD stars, sets player state 2. Its only caller is `0x431238`.
  - The player calc `0x431070` switches on player + `0x928` through the table `0x431BA4`: 0 → `0x431095` (respawn, to 1 after 60 frames), 1 → `0x4311AC` (play), 2 → `0x4312B9` (dying, game over or to 0), 3 → `0x43153A`, 4 → `0x431225` (hit).
  - State 4: if player + `0x948` (frame timer) >= 8, call `0x4327D0`; else with the bomb key (`[0x4C93C0]` bit 2) and enough power, deathbomb back to 1. The hit routine `0x432A90` (called by the four collision checks `0x431EDF`, `0x432054`, `0x43227B`, `0x43273F`) sets state 4, zeroes the timer and plays sound 4.
  - So no code patch or cave is needed: the client writes 4 into `ADDR_PLAYER_STATE` while it reads 1. 1 → 2 only goes through 4, so the read-then-write can't land on a dying player. The ticket's NOP-site test plan (`ADDR_KILL_CONDITION`, `EXPECTED_BYTES`, thcrap overlap) no longer applies; the entry is removed.
  - K4: 32 R5 K4b saw no death sent on Restart, so no guard; `on_state`'s ponytail comment now records that.
- 2026-10-12 al-work (36): done. `ADDR_PLAYER_STATE` sourced statically; `kill` writes the hit state, `/receivedeath` tests it without another player. DoD: `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → 368 passed. Review: the write skips the collision guards (invincibility, bomb, HUD flag `+0x4438`), listed under batch 44's Decisions with R5 D5 (boss dialog). In-game check: probe batch 44 R5 (a failed D2 reopens 36; no follow-up ticket, like 33's R3). Deferred: none.
