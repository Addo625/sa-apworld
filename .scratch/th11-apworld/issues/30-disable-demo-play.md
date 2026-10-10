# 30: Demo Play must not send checks

Status: done
Blocked by: 08

## Problem
The title screen's Demo Play replays existing runs. During one, the client detected a boss drop and sent a real check (human, 2026-10-10: a "midboss Orin" check from a demo). Demo runs look like play to the client (the enemy manager exists, the boss field rises and falls). Priority: low, below 29.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **Option A (preferred, MoF prior art):** disable Demo Play with a one-byte patch on its start condition. MoF uses `ADDR_DEMO_CONDITION` → `0x90` (`ref-projects/mof-apworld/gameController.py:714`). Find SA's equivalent condition by static analysis of `.games/sa/th11.exe`, apply it through `safe_patch` with `EXPECTED_BYTES`, and run it on attach.
  - Tests: `test_demo_patch_guarded`, `test_demo_patch_doesnt_overlap_thcrap`.
- **Option B (fallback):** detect a demo and suppress detection. EoSD has `ADDR_IN_DEMO` (`ref-projects/eosd-apworld/variables/th06.py:3`). If SA's flag isn't known, `detect.step` sends nothing while a replay is playing. thprac's `REPLAY_MGR_PTR` (`0x4a8eb8`) ≠ 0 during a demo is a candidate.
  - Test: `test_detect_ignores_demo`.
- Either way, the client logs once that demo checks are suppressed or disabled.

## Steps
1. Try A. If the site can't be identified with confidence, do B.
2. Tests and wiring. Run the DoD.

## Deferred
- **In-game check (human):** idle on the title until a demo plays. A: no demo starts. B: the demo plays and the server gets no check. If B's flag is a guess, set `needs-human` with the `/probe` needed during a demo.

## Comments

- al-work 2026-10-10: Option B. Option A needed static analysis of th11.exe, and no disassembler (python, objdump) could run in the unattended session, so the demo site stays unknown. `decode_state` now counts a run as not in game while `ADDR_IN_DEMO` is non-zero, so a replay sends no checks, deaths or rings and gets no traps or items; `test_detect_ignores_demo` covers it. The flag is `None` (thprac's `0x4a8eb8` is a guess that may also be set during normal play), so the client logs "pending the demo flag" on attach. Probe request: 32 R8; follow-up: 41. DoD: 345 passed.
