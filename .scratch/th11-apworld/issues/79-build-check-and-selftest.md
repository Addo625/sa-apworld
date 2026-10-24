# 79: The client names the th11.exe build on attach, and /selftest checks its patch sites

Status: done
Blocked by: None

## Problem
The human asked whether addresses differ between distributions. All copies so far (the human's Mac and Windows, Janania's) come from one zip, and the Windows exe's SHA-256 equals thcrap's `th11 v1.00a (original)` (`versions.js`). The Steam release is a different file (Steam's DRM stub) and hasn't been checked. Players need a quick way to know whether their copy matches, without a probe session.

## What to do
- `Variables.KNOWN_BUILDS`: SHA-256 → build name (original v1.00a; the Steam ones marked unverified), from thcrap's table.
- `gameController.exe_path()` (QueryFullProcessImageNameW). On attach, the client hashes the exe and logs its build, or warns on an unknown one.
- `/selftest` (`patching.selftest`): each `EXPECTED_BYTES` site read from the running game: original, already patched by this client, or changed by something else (another build, vpatch/thprac).
- Tests: `TestSelftest`. A one-off check against the human's real exe: all four sites match.

## Deferred
- Steam: ~10 minutes inside the refund window: launch through Steam, connect, read the attach line, `/selftest`, Practice Stage 1 to the midboss. Then mark the Steam hash verified (or not) in `KNOWN_BUILDS`.
