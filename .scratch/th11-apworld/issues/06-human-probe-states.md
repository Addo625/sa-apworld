# 06: [human] Run /probe in every game state and record the output

Status: ready-for-human
Blocked by: 05

## Problem
Ticket 04's address table is sourced but unverified, and only someone playing can put the game into each state. Back up `score.dat` (in the game folder or `%APPDATA%\ShanghaiAlice\th11` inside Wine) first.

## DoD
`## Comments` holds one fenced `/probe` output per state below. Each is labeled with the state and with what the screen showed for lives, power, stage, difficulty, character and shot.

## Test plan
Capture `/probe` in each state. Launch `th11.exe` itself, without thcrap, unless noted. Write what you see next to each one.
- **S0:** title menu.
- **S1:** difficulty select, cursor on Normal. **S1b:** cursor on Lunatic.
- **S2:** character/shot select on Marisa B.
- **S3:** Practice Stage 1, Normal, Reimu A, before the midboss.
- **S4:** Kisume (midboss) on screen.
- **S5:** after the midboss leaves.
- **S6:** Yamame (boss) on screen.
- **S7:** stage-clear tally.
- **S8:** back in the menu after S7. Also: does Practice now offer Stage 2? Look up the unlock byte.
- **S9:** quit to the menu during the boss (the negative case).
- **S10:** a game over screen.
- **S11:** a life lost (lives −1), and after collecting a life piece.
- **S12:** after bombing (power drop).
- **For stages 2–6 and Extra:** boss-present flag(s) with the midboss up and with the boss up. Reach those stages by playing through, or with thprac (it runs under Wine), or, once 07/08 land, through practice unlocks written by the client.
- **S13:** one `/probe` with thcrap (`th11 (thpatch-en).exe`) at S3, to confirm attach-by-name works through thcrap.

## Steps
1. Back up `score.dat`.
2. Go through S0–S13 and paste each output under `## Comments`.
3. For any stage you can't reach, write "not reached". Ticket 07 then carries those entries as unverified. Set `Status: done`.

## Deferred
- A full in-game check of stages 2–6 and Extra under thcrap → 17.
