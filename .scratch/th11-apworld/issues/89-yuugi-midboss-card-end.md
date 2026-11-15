# 89: Yuugi's midboss check goes out the moment her midboss card ends

Status: done
Blocked by: None

## Problem
Batch 74 R1 (73 in game): the boss pointer went up at Yuugi's midboss and **stayed up through the boss**. The spell ID was `0x1B` (flags 67) during the midboss card and went to 0 once the midboss was killed or timed out. So 73's card count saw one run of 4 cards, and `Yuugi - Midboss` went out only with the stage clear.

## DoD
- `pytest worlds/th11/test -q` passes with the tests below.
- In game (batch 90 R1): killing Yuugi's midboss sends `Yuugi - Midboss` right away; beating Yuugi sends `Yuugi Defeated` + `Stage 3 Clear`.

## Design
- In a Stage 3 boss-field run, the **first card ending while the boss stays up** is the midboss ending. `detect.step(..., cards, card_ended)` then sends the midboss check only, with the run count unchanged, under the same quit guards as a field drop (menu, -1 lives, retry) plus `locked`/`voided`.
- `Client.poll` keeps `active_card` (the card running at the last poll). `card_ended` = it was running and isn't now.
- The leaves shape (73) is unchanged: a drop with 1 card sends the midboss only. The field drop after the boss's cards sends everything, and the midboss going out twice is harmless.
- **Edge:** a midboss that times out before declaring its card: the boss's first card ending sends the midboss check a little late.

## Test plan
- `test_detect`:
  - `test_detect_stage3_midboss_card_ends`: cards 1 + ended → the midboss, runs unchanged; cards 2 → nothing; not ended → nothing; Stage 1 → nothing.
  - `test_detect_stage3_midboss_card_end_on_a_quit`: a menu, -1 lives or a retry → nothing.
- `test_client.test_stage3_midboss_sends_when_its_card_ends`: the R1 shape, end to end.

## Steps
1. `detect.step`: the midboss trigger. 2. `Client.poll`: `active_card`, `card_ended`. 3. Tests, install.

## Deferred
- None.
