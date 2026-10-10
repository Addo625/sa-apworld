# 34: Find and patch the continue-lives code site (Normal mode)

Status: done
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

## Comments

**Static analysis (capstone over `.games/sa/th11.exe`, image base 0x400000).** Every write to lives `[0x4A5718]`: the game init (`0x41FA38`/`0x41FA49`/`0x41FA56`), the extend (`0x420959`/`0x420960`), the death decrement (`0x4327F0`, `0x433D30`), and the replay/stage snapshot loads (`0x435AD1`, `0x43702B`). None of them sits in a continue handler. Continues (`ADDR_CONTINUES`, `0x4A573C`) are only incremented at `0x41FEE3`. That code also sets game flag 8 (`or [0x4A5758], 8`) and flag 1, and the init then runs with flag 8 set. In the init, flag 8 keeps the continues count (`0x41F9DC`), picks the `call 0x41F880` path (`0x41FCBB`), and resets lives through the normal branch:

```
0041F947  be02000000           mov esi, 2
0041F94C  8bd6                 mov edx, esi
0041F94E  6689907c030000       mov word ptr [eax + 0x37c], dx    ; ANM interrupt 2, read at 0x44B4F9
...
0041FA12  f60558574a0010       test byte ptr [0x4a5758], 0x10    ; Practice
0041FA36  7508                 jne 0x41fa40
0041FA38  893518574a00         mov dword ptr [0x4a5718], esi     ; <- site
0041FA3E  eb1b                 jmp 0x41fa5b
0041FA40  a164574a00           mov eax, dword ptr [0x4a5764]     ; Practice: [0x4a5764] ? it-1 : 9
0041FA45  3bc3                 cmp eax, ebx
0041FA47  750c                 jne 0x41fa55
0041FA49  c70518574a0009000000 mov dword ptr [0x4a5718], 9
0041FA53  eb06                 jmp 0x41fa5b
0041FA55  48                   dec eax
0041FA56  a318574a00           mov dword ptr [0x4a5718], eax
0041FA5B  e850070100           call 0x4301b0                     ; doesn't read eax (overwrites it at 0x4301B7)
```

This is the MoF layout: MoF's continue site `0x17955` and Practice site `0x1796A` also sit 0x15 apart in one init. In SA the lives immediate is `mov esi, 2`, and `esi` also feeds an ANM interrupt word, so patching it would change the loading-screen animation. So the client rewrites the normal branch's 8 bytes instead: `b8 LL 00 00 00 eb 17 90` = `mov eax, LL; jmp 0x41FA56; nop`, which reuses the Practice branch's `mov [lives], eax` and falls through to the same `0x41FA5B`. This replaces 12's `patch_immediate` with `patch_value`, which accepts the original bytes or an earlier version of its own patch, so it repeats with new values. `test_continue_lives_site_bytes` checks the original bytes and the jump target against the exe, and the thcrap overlap test covers the site.

Done: commit `34: restore lives from received +1 Life on a Normal-mode continue`. DoD `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → 348 passed, none skipped. In-game check: probe batch 32 R2; default listed under 32's Decisions to confirm (starting lives follow the count too). No follow-up ticket: if R2 confirms, nothing is left; if not, R2 says to reopen 34.
