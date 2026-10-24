# 73: Beating Yuugi's midboss sends only the midboss check

Status: ready-for-agent
Blocked by: 74

## Problem
Playtest (human): after clearing Stage 3 with Marisa, a Reimu run beat Yuugi's midboss and got all three checks (`Yuugi - Midboss`, `Yuugi Defeated`, `Stage 3 Clear`). `detect.run_checks(3)` treats Stage 3 as one boss-field run, because early probes had Yuugi staying on screen from midboss into boss (ticket 22). Here she left after the midboss, so the client took the midboss for the whole fight. What makes her leave (character, killing her versus timing out) is unknown.

## What to do
- Read batch 74 R1.
- If the boss field drops between midboss and boss: Stage 3 becomes two runs like the others, and the single-run case keeps working (a run that saw the boss's spell cards counts as the boss).
- If it doesn't: tell the phases apart by the spell-card object (`ADDR_SPELL_ID`).
- Test in `test_detect` with both shapes.

## Deferred
- None.
