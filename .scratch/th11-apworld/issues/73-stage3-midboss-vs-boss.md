# 73: Beating Yuugi's midboss sends only the midboss check

Status: done
Blocked by: None

## Problem
Playtest (human): after clearing Stage 3 with Marisa, a Reimu run beat Yuugi's midboss and got all three checks (`Yuugi - Midboss`, `Yuugi Defeated`, `Stage 3 Clear`). `detect.run_checks(3)` treats Stage 3 as one boss-field run, because early probes had Yuugi staying on screen from midboss into boss (ticket 22). Here she left after the midboss, so the client took the midboss for the whole fight. Both shapes happen, so the boss field alone can't tell them apart. Playtest 3 (2026-10-25) asked again to move the midboss check back to its place.

## DoD
- `pytest worlds/th11/test -q` passes with the new `test_detect` cases.
- In game (batch 74 R1):
  - killing Yuugi's midboss sends only `Yuugi - Midboss`;
  - beating Yuugi sends `Yuugi Defeated` and `Stage 3 Clear`.

## Design
Count the spell cards, which needs no card-ID table and no probe to build. The midboss declares exactly one card. Yuugi as boss declares three before she can go down (`CAPTURE_CAPS[2] = 4`). When a Stage 3 boss-field run ends:
- **fewer than 2 distinct cards seen in that run** → `Yuugi - Midboss` only;
- **2 or more** → `Yuugi - Midboss`, `Yuugi Defeated`, `Stage 3 Clear`. Re-sending the midboss is harmless.

This covers both shapes:
- **Yuugi leaves:** run 1 sees 1 card, run 2 sees 3.
- **Yuugi stays:** one run sees 4.

## Test plan
- `detect.run_checks(3, cards)`:
  - with 0 or 1 → `[["Yuugi - Midboss"]]`;
  - with 2 or more → the midboss, `Yuugi Defeated` and `Stage 3 Clear`.
  - Other stages ignore `cards`.
- `test_detect`:
  - the field drops after the midboss with 1 card → midboss only, and the next run with 3 cards → Defeated + Clear;
  - one run with 4 cards → all three;
  - update the existing `run_stage(3, 1)` case (`test_detect.py:56`).
- `test_client`: card IDs read while the boss is up reach `detect.step`. The set clears when the field drops, on a stage change and on a restart. It also works without `spell_card_keys`.

## Steps
1. `th11/detect.py`:
   - `run_checks(stage, cards=0)`; `step(..., cards=0)` and `run_locations(..., cards=0)` pass it through;
   - for Stage 3 the run index no longer matters;
   - fix the stale comment.
2. `th11/Client.py` `poll`: a `run_cards` set of the distinct card IDs seen during the current boss-field run.
   - Read `ADDR_SPELL_FLAGS`/`ADDR_SPELL_ID` the way `detect_captures` does (`Client.py:260`), but even without `spell_card_keys`, since `detect_captures` returns early.
   - Pass `len(run_cards)` into `detect.step`, and clear the set when a run ends, on a stage change, or on a restart.
   - `runs_found` (runs found while disconnected) keeps the card count with each run.
3. Tests as above. Install the apworld.

## Deferred
- None.

## Comments
- 2026-10-25 Claude: redesigned from the field-shape split to the card count, so this ticket no longer waits for batch 74. Batch 74 R1 is now the in-game check, done with Cheat Engine.
- 2026-10-25 Claude: done. In-game check: batch 74 R1.
