# 76: A collected capture check no longer blocks the stage's other capture checks

Status: done
Blocked by: None

## Problem
Windows 2-player playtest (2026-10-22): when Janania finished, collect marked capture checks in Addo's world as found (`[Reimu] Stage 5 - Capture 2`, ...). The client numbered the next capture "sent + 1", so every new Stage 5 spell re-sent the checked Capture 2. Capture 1, which held Addo's Next Stage (needed for Extra), was never sent. The tracker looked frozen for the same reason.

## What to do
- `captures.capture_location` fills the stage's lowest capture check that isn't checked yet (the server's checked set plus this session's sends). It's stateless, so collect, release and reconnects all work.
- Test: `test_capture_fills_the_lowest_unchecked_after_a_collect`.

## Deferred
- None.
