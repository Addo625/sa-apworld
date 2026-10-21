# 63: A spell counts once for captures, whatever the difficulty

Status: done
Blocked by: 61

## Problem
Each difficulty's version of an attack is its own card ID, so capturing the same spell on another difficulty filled another capture slot. Human (2026-10-20): count the attack, not the difficulty ("serialize the attacks per stage").

## What to do
- The save's card records give the order: 0-1 Kisume Hard/Lunatic, then each 4 IDs one attack on E/N/H/L (2-161), then Extra (162-174). `captures.spell_slot(card)` maps a card to its attack; "captured before" checks every card of that slot (owner's records + server data storage, now `th11_spells_<team>_<slot>`).
- Docs: README, `CapturesPerStage`, the example YAML. Tests in `test_captures` and `test_client`.

## Deferred
- Batch 64 R2: capture one spell on two difficulties in game.
