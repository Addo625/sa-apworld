# 17: [human] Full in-game check under the thcrap English patch

Status: ready-for-human
Blocked by: 09

## Problem
The user plays with thcrap (`th11 (thpatch-en).exe`). The static test in 04 rules out patch-site overlap, but only a real session proves that detection and item writes work with thcrap loaded.

## DoD
Ticket 09's three DoD observations hold when the game is started via `th11 (thpatch-en).exe`.

## Test plan
- **From 06 (S13):** first, one `/probe` at the S3 point (Practice Stage 1, before Kisume) started via `th11 (thpatch-en).exe` (or `th11 custom (thpatch-en).exe` → start). Every static entry should match the plain-exe S3 probe in 06.
- In: the 09 setup, started through thcrap.
- Out: the same server and in-game observations as 09, plus no `PatchMismatch` in the client log.

## Steps
1. Repeat 09 started through thcrap. Paste the results under `## Comments`. Set `Status: done`, or `needs-human` with the failure.

## Deferred
- None.
