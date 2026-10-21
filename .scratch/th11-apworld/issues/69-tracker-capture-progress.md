# 69: The tracker says what still counts as a capture

Status: ready-for-agent
Blocked by: 68

## Problem
Batch 67 (human): the tracker showed Reimu with captures left on a stage where every capture attempt sent nothing. The count of open capture checks was right, but nothing says which spells can still fill them: only a spell this owner hasn't captured in this seed counts (one per spell, any difficulty, shared by a character's shots under per_character).

## What to do
- `tracker.report` gets the captured entries (the server data storage `<owner>:<spell slot>`, passed in by `Client.tracker_lines`).
- Per owner block: `Captured spells: N` (this seed), plus a legend line: "A capture check needs a spell <owner> hasn't captured in this seed, on any difficulty".
- Per stage, the capture part reads `captures k/slots`, not just "N captures" left.
- When a stage's capture checks are all sent, say `captures done`.
- Test in `test_tracker`.

## Deferred
- Listing which spells per stage are still new needs a spell-slot → stage table (40 slots). The client could learn it from the stage it saw each slot on, or a static table could be added; add it if the count isn't enough.
