# 27: [human] Run /memsearch for the practice-unlock pattern

Status: ready-for-human
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
