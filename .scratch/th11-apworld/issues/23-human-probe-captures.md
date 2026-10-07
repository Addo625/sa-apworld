# 23: [human] Probe spell captures in-game

Status: deferred
Blocked by: 22

## Problem
22's capture entries are sourced but unverified, and the per-stage card caps (2/4/4/4/5/6) come from memory plus how spells.js groups its IDs. Only someone playing can confirm both. Back up `score.dat` first.

## DoD
`## Comments` holds one fenced `/probe` output per state below, each labeled with the state and with what the screen showed (card name, captured or not).

## Test plan
Use practice mode with `th11.exe`, no thcrap.
- **C1:** Stage 1, Lunatic, Reimu A: during Kisume's card (not yet captured).
- **C2:** right after capturing it (the bonus shown).
- **C3:** during Yamame's first card, then after *failing* it (bomb or death).
- **C4:** count the cards in Stage 1 on Easy and on Lunatic, and write both numbers.
- **C5:** Stage 4 with one shot type: count Satori's cards and note their names.
- **C6:** quit to the menu and probe again. Does the spell history in memory still show C2's capture?

## Steps
1. Back up `score.dat`.
2. Go through C1–C6 and paste each output under `## Comments`.
3. Write "not reached" for anything you couldn't reach. Set `Status: done`.

## Deferred
- None.
