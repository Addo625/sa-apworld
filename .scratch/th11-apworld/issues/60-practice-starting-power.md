# 60: Practice runs start with the power of the +0.50 Power packs received

Status: done
Blocked by: None

## Problem
Human (2026-10-18): `+0.50 Power` "doesn't really exist". A pack only added 0.50 once, in the run it arrived; every new Practice run started at the game's own power. Logic treats packs as permanent (the power gates), so the gates didn't match the game. Same gap 49 closed for lives. Batch 50 R4's double life has the same cause: an item waiting in a menu is in the run's start lives and was then added again.

## What to do
- `receive.practice_power`: at a Practice run's start (`ADDR_GAME_FLAGS & 0x10`, the poll after entering play), power = max(the game's start power, packs × 0.50, at most 4.00). A client write, not a code patch: the game's init (`0x41FA68`-`0x41FA94`) sets power from the stage and a value read in many places.
- `apply_new(started=True)` skips waiting `+1 Life` and `+0.50 Power` (already in the start values); `+0.05 Power` still adds. Mid-run items work as before.
- The tracker shows the starting power. Test in `test_receive`.

## Deferred
- Batch 58 R5: confirm in game, and whether a Practice retry from the pause menu keeps the power (the client may miss a retry; `ponytail` in `Client.poll`).
