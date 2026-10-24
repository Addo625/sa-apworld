# 78: Spell Card Keys beyond what logic needs show as useful, not filler

Status: done
Blocked by: None

## Problem
Windows playtest (2026-10-22): a Spell Card Key showed as a plain (filler) item in the client. By design since 75, only the keys logic counts on (the largest lock + slack) are progression, because all-progression keys failed fill. The rest were filler, even though they still open the game's key locks.

## What to do
- With any key lock set, the keys beyond `keys_needed()` are `useful`; without locks every key stays filler. Fill treats useful like filler, so nothing changes for generation.
- Test: `TestDefaults.test_item_count_matches_locations` counts 8 progression + 4 useful.

## Deferred
- None.
