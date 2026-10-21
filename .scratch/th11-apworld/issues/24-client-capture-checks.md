# 24: The client sends capture checks; Spell Card Keys on by default

Status: done
Blocked by: 08, 21, 23

## Problem
With 21's locations and 23's verified addresses, the client must send `Stage N - Capture k` when the player captures their k-th *different* card in that stage. Until it does, 21 has to default to `off` (risk K1). This ticket flips the default to `alongside`, the user's target.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the `test_capture_*` tests below and the updated `test_spell_card_keys_default_alongside`.

## Test plan
- **Address fixes:** apply 23's findings to the capture entries (the same flow as 07). Remove `TODO(23)`. If C4 or C5 show different card counts, fix the cap table in the world, and add a test for it.
- **`detect.step(prev_state, state)`** (pure), extended with capture detection:
  - Track the captured card IDs per stage, per character (or shared, per `slot_data.capture_slots`).
  - When a new distinct card is captured, emit slot k = the number captured so far, up to that stage's slot count from `slot_data`.
  - Tests:
    - `test_capture_first_sends_slot1`.
    - `test_capture_same_card_twice_sends_nothing`.
    - `test_capture_failed_card_sends_nothing`.
    - `test_capture_beyond_slot_count_sends_nothing`.
    - `test_capture_shared_mode`.
    - `test_capture_replay_idempotent`: on reconnect, the set of captured cards is rebuilt from checked locations and the history, with no duplicate sends.
- **Default:** `spell_card_keys` default becomes `alongside`. `test_spell_card_keys_default_alongside` replaces 21's default-off test.
- **Docs:** README and `examples/th11.yaml` describe captures and keys.

## Steps
1. Apply 23's address fixes, plus the cap-table fix if needed. Green.
2. Capture detection in `detect`, with its tests, wired into the client loop. Green.
3. Flip the default and update the docs. Run the DoD.

## Deferred
- An in-game capture smoke run: add a `ready-for-human` ticket when promoting, as 09 does for v1.
- 2026-10-18 Claude: done, with a different signal than planned. No spell ID or bonus address is needed: the save's CR chunk ends in 175 card records (name, capture count, attempt count, ID, level; 0x664 + 175 x 0x90 = CLEAR_SIZE), live at `[0x4A8EBC] + 0x66C` per shot. `captures.py` compares the counts poll to poll for the last run's shot; a card whose count rises, and which none of the owner's shots had captured before, sends the stage's next `Capture k` (k = sent + 1, up to min(captures_per_stage, the stage's cap)). Locked runs (the stage filter, Start runs in Practice seeds) send nothing. **The default stays `off`** until batch 58 R6 confirms it in game; flipping it then is one line in `Options.SpellCardKeys`.
- 2026-10-20 Claude: batches 58 and 61 confirmed capture checks in game, and the crash fix held. `spell_card_keys` now defaults to `alongside` (human decision). The core test base sets it to `off`, so the location-count tests keep their numbers.
