# 27: [human] Run /memsearch for the practice-unlock pattern

Status: done
Blocked by: 26

## Problem
26 produces the save's practice-progress byte pattern. Only a running game shows where that data lives in memory.

## DoD
`## Comments` holds the `/memsearch` output (match addresses) from a running game, plus a second run after unlocking one more Practice stage, showing which match changed.

## Test plan
- Copy the `/memsearch <hex>` line from 26's comments.
- **M1:** game at the title menu, run it, paste the matches.
- **M2:** reach a new stage in a normal game (as in 06 S8), back at the Practice menu, run it again with the pattern 26 gives for the changed state, paste the matches.

## Steps
1. Restart the client with the latest apworld (26's build).
2. Do M1 and M2 and paste the output. Set `Status: done`.

## Deferred
- None.

- 2026-10-10 human (via Claude), macOS + Wine 11, apworld from `main`:
  - **Mirror check (cheated save):** `/memsearch 0000000000010000000000000001000056` → 2 matches, `0x0373215C` and `0x03F205C4`. The save is in memory in the file's layout.
  - **Fresh save** (`scoreth11.dat` moved aside), normal game on Normal with Reimu A, Stages 1–2 cleared. `tools/scoredat.py`: ReimuYukari Normal 1:1/1/0 and 2:1/1/0; every other entry of every shot is 0/0/0.
  - **M1** (Practice menu, same session): `/memsearch 00000000010100000000000001010000` (Normal Stage 1 + 2 entries) → 2 matches, `0x0382218C` and `0x040B05F4`.
  - **M2:** after another normal game in which Stage 3 stayed locked in Practice, the patterns expecting a set Stage 3 entry gave 0 matches. That's consistent: the table didn't change.
  - **Findings for 28:**
    - `unlocked` = 1 ⇔ that stage is offered in Practice. On this save it's set by *clearing* the stage in a normal game (Stages 1–2 cleared → 1–2 offered, 3 locked).
    - Practice table start = match − 0x30 (Normal Stage 1 is entry 6). Both sessions agree on the page offsets: copy 1 at `…215C` (`0x0373215C`/`0x0382215C`), likely the live in-memory save struct (table = struct + 0x5A4, so struct ≈ `…1BB8`); copy 2 at `…05C4` (`0x03F205C4`/`0x040B05C4`), likely the raw decoded file buffer (file offset 0x18 + 0x5A4).
    - Open: which copy the Practice menu reads, and the static pointer path to it. Both are 28's first step (`/ptrscan` plus one human run).
