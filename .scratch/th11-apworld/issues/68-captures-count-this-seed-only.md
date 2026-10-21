# 68: A spell counts as captured before only if this seed recorded it

Status: ready-for-agent
Blocked by: None

## Problem
Batch 67 (human, seed from `~/archipelago/Archipelago/players-64/addo.yaml`, `capture_slots: per_character`): after unlocking another Reimu shot, captures sent nothing, and "per character" should have given Reimu checks.

Client logs (`~/archipelago/install-wine/logs/Launcher_2026_10_21_*.txt`):
- `Spell card 0 captured (this spell was captured before ...)`: Kisume's card, on the first Kisume capture of the seed;
- `Spell card 11 captured (... before ...)`: Parsee's card.

Cause, in `Client.card_ended`: "captured before" is true if the **game save** shows the spell captured before, or the server's data storage does. Because of the save check, any spell captured before this seed blocks the check: in an older save, by a locked shot's run (locked runs send nothing but still count in the game), or with another of the character's shots before it was received. "Use a fresh save" in the README hides this but doesn't fix it.

Note: `per_character` does share one set of slots across a character's three shots (Reimu A/B/C). So the same spell with Reimu B after Reimu A correctly sends nothing. That's by design (`shot_type: true` gives per-shot checks), and the README should say it plainly.

## What to do
- `card_ended`: "captured before" = only the server data storage entry `<owner>:<spell slot>` (and this session's `captures_seen`). Drop `before > 0` and the reads of the slot's other cards and the owner's other shots. The capture itself is still the count rising during an unlocked run.
- A locked run's capture records nothing (already: `locked` returns before the storage write).
- README / `examples/th11.yaml`: drop "use a fresh save"; say `per_character` means one set per character, shared by its 3 shots.
- Tests (`test_client`): a spell with a save count > 0 from before the seed now sends; the same spell after storage has it sends nothing; Reimu B after Reimu A, per_character, sends nothing; with `shot_type`, it sends.

## Deferred
- None.
