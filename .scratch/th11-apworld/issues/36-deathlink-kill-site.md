# 36: DeathLink kill site

Status: ready-for-agent
Blocked by: 32

## Problem
14 sends deaths and has the kill wired (`TouhouContext.kill`: NOP the kill site for 0.1 s, guarded by `EXPECTED_BYTES`), but `ADDR_KILL_CONDITION` is `None`, so a received DeathLink is only logged.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with `ADDR_KILL_CONDITION` sourced from 32 R5 (or, if R5 found no working site, a new probe-batch request and this ticket's note saying so).

## Test plan
- `Variables.ADDR_KILL_CONDITION` = the K3 address that killed, minus the image base; `EXPECTED_BYTES["ADDR_KILL_CONDITION"]` = its original bytes from K2 (the full jump, 5 bytes for `e9 rel32`, 6 for `0f 8x rel32`); source comment `probe 32 R5`.
- `test_patch_sites_dont_overlap_thcrap` passes with it (thcrap must not patch the same bytes).
- `test_deathlink.TestClientKill` already covers the patch/restore; switch its stand-in (`0x25A91`, `KILL_JUMP`) to the real entry and drop the `mock.patch`.
- `TestClientDeathLink.test_incoming_pending_without_kill_site` no longer applies: delete it, and drop the "pending … ticket 36" log in `on_deathlink`.
- K4: if a pause-menu Restart sent a death, guard it in `deathlink.on_state` (e.g. ignore a drop when the stage or power reset with it) with a test from K4's values.

## Steps
1. Read 32's R5 comments. No site that killed in K3 → add a request to the open probe batch for another lead (thprac's invincibility patch, a disassembly), set this ticket blocked by it, stop.
2. Set the entry and bytes, update the tests above.
3. K4 guard if needed.

## Deferred
- None.

## Comments
