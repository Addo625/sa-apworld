# 41: Source the demo flag so replays send no checks

Status: ready-for-agent
Blocked by: 32

## Problem
30 made the client treat a replay as not playing (`state.decode_state`: `in_game` is False while `ADDR_IN_DEMO` is non-zero), but the flag is `None`: SA's demo flag is unknown, so a title demo still sends checks. Probe batch 32 R8 reads the candidate (`ADDR_REPLAY_MGR_PTR`, thprac's `0x4a8eb8`) during a demo and during normal play.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the test below.

## Test plan
- From 32's `## Comments`, R8: pick the entry that is non-zero in D1 (demo) and zero in both D2 runs (Start, Practice). Set `ADDR_IN_DEMO` to it (e.g. `ADDR_IN_DEMO = ADDR_REPLAY_MGR_PTR`) with a `source: probe 32 R8 …` comment. If it's a bit of a flags word rather than a zero/non-zero value, read it as an entry and mask it in `decode_state`.
- `test_state`: add R8's D1 values as a state case expecting `in_game=False`, and a D2 case expecting `in_game=True`.
- No entry fits (R8 shows none differs, or R8 "not reached") → `needs-human` with what was seen.

## Steps
1. Read R8, set `ADDR_IN_DEMO`, add the two state cases. Run the DoD.
2. Update the client's attach log only if its wording no longer fits.

## Deferred
- In-game check (human): idle on the title until a demo passes a boss; the server gets no check, and the client logs `Demo Play: replays send no checks` on attach.

- 2026-10-11 Claude: lead applied ahead of this ticket, because a title demo applied queued items and the item-sound cave crashed the game. `decode_state` treats `ADDR_GAME_FLAGS & 0x20` as a demo (R8-D1: 32 in both title demos; 16 in Practice and 0 in normal play from 06). This ticket still replaces it with a dedicated flag if D2/D3 show `ADDR_REPLAY_MGR_PTR` or another entry is cleaner, and confirms 0x20 never appears in real play.
- 2026-10-12 planner, **from batch 32 R8:** `GAME_FLAGS` is 32 in two title demos, 0 in a normal run (A8), 16 in Practice (B3), and 20 at a Practice Game Over (B7). `ADDR_REPLAY_MGR_PTR` is non-zero in all of them, so it can't be used. Make `GAME_FLAGS & 0x20` the named demo signal (replace the interim code in `decode_state`; `ADDR_IN_DEMO` stays `None` or becomes a bit entry, whichever reads cleaner), and update the probe docs and tests. D3 (a saved replay) wasn't run, so note that saved replays are assumed to set the same bit.
