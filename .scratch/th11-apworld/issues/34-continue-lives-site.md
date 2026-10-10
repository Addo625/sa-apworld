# 34: Find and patch the continue-lives code site (Normal mode)

Status: ready-for-agent
Blocked by: 12

## Problem
12 built Normal mode's continue-lives patch (MoF `setNormalContinueLives`: a continue restores one life per `+1 Life` received, up to 8), but `ADDR_NORMAL_CONTINUE_LIVES` is `None`, so the client only logs "pending". A static scan of `th11.exe` for `mov dword [0x4A5718], imm32` (`C7 05 18 57 4A 00`) found only `0x41FA4B` (`= 9`, Practice's starting lives, matching probe 06 S3) and the extend cap at `0x420962`. The continue path loads lives from a register (candidates near `0x4327F2` `mov [lives], edx` and `0x41FA3A` `mov [lives], esi`), so the value comes from somewhere else: a constant loaded into a register, a config field, or a global.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_continue_lives_site_bytes` (skipped if `.games/` is absent).

## Test plan
- **Static analysis** (no game needed): `../.venv/bin/pip install capstone` (allowed), disassemble `.games/sa/th11.exe` around every write to `0x4A5718`, and find the continue path (it follows the game-over/continue menu; its lives source is a one-byte immediate or a global).
  - Write the reasoning and the disassembly snippet in this ticket's comments.
- **`Variables.py`:** `ADDR_NORMAL_CONTINUE_LIVES` = the immediate's address, `EXPECTED_BYTES` = the instruction bytes before it. 12's `patch_immediate` uses exactly that shape.
  - If the source is a global rather than an immediate, use a data write through `write_int` instead, and say so in the commit body.
- **`test_continue_lives_site_bytes`:** reads `.games/sa/th11.exe` at the site and asserts `EXPECTED_BYTES` plus the current immediate. The thcrap overlap test (04) must still pass.

## Steps
1. Disassemble, identify the site, and write the comment. Then the entry and the byte test. Run the DoD.
2. Add the in-game check to the open probe batch (AGENTS.md rule): a normal game, lose all lives, continue once, `/probe` → `ADDR_LIVES` equals the received `+1 Life` count.

## Deferred
- None.
