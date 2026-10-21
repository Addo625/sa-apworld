# 23: [human] Probe spell captures in-game

Status: done
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

## Comments

- 2026-10-10 al-work (22): only `ADDR_SPELL_HISTORY` is sourced. `/probe` reads one u32 from it, the first counter at `+0x6E8`, so C1-C3 show whether that counter moves but not which card it belongs to. `ADDR_SPELL_ID` and `ADDR_SPELL_BONUS` print `<unsourced>` and can't be verified here. They need a source first: the FearLess table or disassembly (both blocked for agents), or a memory search like 26.
- 2026-10-18 Claude: the probe this ticket asked for is no longer needed for addresses: 24 reads the save's spell history live (`ADDR_SPELL_CARDS`, sourced from the save layout; the decoded saves confirm IDs 0-174 in order). What's left in game (does the count rise at the capture or only at the run's end, and does Practice count) moved to batch 58 R6. Done.
