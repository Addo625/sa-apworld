# 66: A spell capture sends its check the moment the card ends captured

Status: done
Blocked by: None

## Problem
Batch 64 (human): capture checks only arrived back on a menu. Since batch 58's dialog crash, the client read the spell history (25 KB per shot) only on menus.

## What to do
- Static disassembly: the spell-card object `[0x4A8D6C]` holds the running card's ID (+0x8DC) and flags (+0x8E0, bit 1 active). The capture handler adds 1 to that card's count in the live save the moment it ends captured (`0x40CE4C`-`0x40CE62`).
- `Client.detect_captures`: in play, read the ID and flags; at a card's start, read its one count; at its end, read it again. A rise is a capture: 63's spell slot, "captured before" (single dwords for the slot's other cards and the owner's shots, plus server storage), then the check. No 25 KB reads remain.
- Tests: `test_client.test_capture_sends_its_check_during_the_run`, `test_captures.test_count_address`. README and example YAML updated.

## Deferred
- Batch 67: confirm in game (the check arrives mid-stage; failed cards and replays send nothing; no dialog crashes return).
