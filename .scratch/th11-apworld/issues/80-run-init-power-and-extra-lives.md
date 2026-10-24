# 80: Every run start, retry and Extra start gets the item power and lives from the game's own run init

Status: needs-human
Blocked by: the Cheat Engine check below (human chose to confirm the sites first, 2026-10-24)

## Problem
Windows playtest (2026-10-22):
- **Retry spam gives full power.** The client spots retries from score and lives (62) and writes power after the game's run init. A quick retry at score 0 slips through, and the game's own 4.00 (Stage 2+) stays.
- **The shot looks odd until the next power change.** The game sets the shot level from power during init; a later memory write changes power but not the shot.
- **Extra starts without the run's lives and power.** Extra isn't a Practice run: it takes the init's non-Practice branch (lives from `esi` = 2, power 0 on the stage 7 path).

Lives are already right on every retry, because they come from a code patch inside that same init function (49, `0x41FA49`).

## What to do (after the check)
- **Power:** patch the init's power block (`0x41FA68`-`0x41FA98`). Stage 1 / Extra set 0; stages 2-6 copy `[0x4A5748]`. Its start becomes `mov dword [0x4A56E8], packs*10` + `jmp 0x41FA99` (12 bytes), guarded by `EXPECTED_BYTES`.
  - Practice-mode seeds only (normal seeds keep the game's carried power on a continue).
  - Re-patched on a menu when the pack count changes, like lives. The client stops writing power at run start.
- **Extra lives:** in Practice-mode seeds, also patch the non-Practice lives site (`ADDR_NORMAL_CONTINUE_LIVES`, `0x41FA38`) with the Practice lives value. Start runs use it too but send nothing in Practice seeds.
- **Tests:** guard bytes against the real exe (as 49), patch values, client patching on a menu.

## Cheat Engine check (human)
1. Run `th11.exe`, attach Cheat Engine.
2. Add address `0x4A56E8` (4 bytes, power in units of 0.05), then right-click → "Find out what writes to this address".
3. In Practice Stage 2 or later: start a run from the menu, then pause → Retry a few times. Note each instruction address listed and its count. Expected: `0x41FA7D` on stages 2-6 (`0x41FA8C`/`0x41FA94` on Stage 1), plus the client's own writes.
4. Same for lives at `0x4A5718` while starting the **Extra** stage. Expected: `0x41FA38`.
5. Optional: a breakpoint at `0x41FA68`. It should hit once per run start and once per retry.

Paste the instruction lists under `## Comments`.

## Deferred
- None.

## Comments

### 3

| Count | Instruction |
| :--- | :--- |
| 6 | 0041FA7D - 89 0D E8564A00 - mov [004A56E8],ecx |
| 1 | 004312E7 - C7 05 E8564A00 00000000 - mov [004A56E8],00000000 |
| 1 | 004312E0 - A3 E8564A00 - mov [004A56E8],eax |

Looks like it's the first line that's relevant to us

### 4

0041FA38 - 89 35 18574A00  - mov [004A5718],esi (CORRECT)
004327F0 - 89 15 18574A00  - mov [004A5718],edx

### 5

The breakpoint did not hit. I turned on both "What reads" and "What writes to this address" and `0x41FA68` seems untouched. If needed, I can try to track the "correct" address of "stage start" or something


### Note
When entering a stage via restart or menu, the client logs it alwasys - make sure its only when '/writelog' is activated
Also, if now we are to make changes with the addresses, make sure to clean up the old ones (accessible via git)