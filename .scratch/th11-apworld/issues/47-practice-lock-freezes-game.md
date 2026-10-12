# 47: Practice locking from 39 corrupts the save and freezes the game at boss dialogs

Status: done
Blocked by: 39

## Problem
Ticket 39 makes Practice offer only received content by **writing the live save struct's practice table** (`[0x4A8EBC, 0x5AC]`, per shot stride `0x68D4`): it sets `unlocked = 0` for everything not received. The game writes the save back to `scoreth11.dat` on exit, so the change is permanent, and **a save left in that state freezes the game at the first line of a pre-boss dialog, even with no client running**.

Evidence (probe batch 44, 2026-10-12):
- **Freeze A/B test, same `.games/sa` files and Wine:**
  - with today's save (after 39's writes), no client: froze after Yamame's first dialog line (T1, and R1 (a));
  - with the 10-11 backup save (`~/archipelago/saves/scoreth11.cheated.dat`, before 33/39 existed), no client: dialog, whole stage and pause all fine (T4).
  - `.games/fresh` (never written by 39), no client: the dialog passed (T3).
- **What 39 changed** (decoded diff of the 10-11 backup vs today's save, `tools/scoredat.py`; today's is kept as `.games/sa/scoreth11_BACKUP.dat`):
  - `unlocked` set to 0 for every shot × difficulty × stage, except Marisa C Lunatic Stage 1 (seed `Batch44`'s start shot, no Lower Difficulty received);
  - **`cleared` bytes left at 1**, producing "cleared but locked" entries, e.g. Reimu A Easy 3 = `0/1`, Marisa B Normal 1–2 = `0/1`.
  - Nothing outside the practice tables changed; ST/Extra, Total and spell history are normal.
- **The invariant the game keeps:** a game-written save (`.games/fresh`) never has `cleared = 1` with `unlocked = 0`; reaching a stage unlocks it, and clearing it implies unlocked. 39's lock breaks that.
- **Exact trigger unknown:** the "cleared but locked" entries, a fully locked difficulty or shot, or the Total chunk no longer matching.

Players are hurt directly: connecting the client damages their own save, and the game hangs on every boss.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below. The ticket comment names the code that reads the practice table at the boss dialog and why the locked state hangs it, or states that the static search failed and which invariant the fix enforces instead. Batch 44 has an in-game check (below).

## Test plan
- **Stop the damage first** (step 1, its own commit):
  - the client never writes a state the game can't produce: never `unlocked = 0` where `cleared = 1`;
  - **never locks an entry that was unlocked when the client first attached**: it may only *add* unlocks for received items, and lock only entries it unlocked itself in this game process;
  - `test_lock_never_clears_unlocked_cleared_entry`, `test_lock_keeps_entries_unlocked_before_attach`.
- **Find the hang** (static, capstone in a pytest scratch per the repo's disassembly note):
  - code reading the practice table (`+0x5AC` from `[0x4A8EBC]`, the `unlocked`/`cleared` bytes) around the pre-boss dialog and stage progress;
  - record the loop or wait that never ends with the 39 state; write it in the comment.
- **Design (decision to confirm in the batch):** with the locks limited as above, a save that already had everything unlocked (like `sa`'s cheated save) keeps it, so Practice is "open" there and only the client's check filter (16) keeps checks honest. Alternative: restore the player's original table on disconnect. List it under batch 44's `## Decisions to confirm`; default to the safe behaviour above.
- **Repair helper:** `tools/scoredat.py --repair <save>` sets `unlocked = 1` wherever `cleared = 1`, so damaged saves can be fixed offline. `test_repair_sets_unlocked_where_cleared`.

## Steps
1. The safe-lock rules and their tests; commit (this alone stops new damage).
2. The static search; the comment.
3. The repair helper and tests. Run the DoD.
4. Add to batch 44:
   - **T5:** with the fixed client connected to `.games/sa` (10-11 save restored), play Practice Stage 1 through Yamame's dialog. Expect no freeze, and the save still has its unlocks after exit (`tools/scoredat.py`).
   - Redo **R1 (b)/(c)** there: (b) froze right on a `+1 Life` while the damaged save was loaded, so the sound hook is untested on a clean save.

## Deferred
- None.

## Comments

- 2026-10-12 al-work: **done.** Step 1: `receive.practice_unlock` only adds received rows, may re-lock only entries this client unlocked in the same game process (`Client.practice_ours`, reset when the game restarts), and sets `unlocked` wherever `cleared` is set, which heals a damaged save live. 39's client test asserting the locks was wrong under the new rule and was replaced (`test_practice_unlocks_received_and_keeps_the_save`). Step 3: `scoredat.encode` (literals-only LZSS + encryption) and `scoredat.repair`, plus `tools/scoredat.py --repair <save>` (keeps `<save>.bak`). DoD: `390 passed`. The repaired copy of `scoreth11_BACKUP.dat` has no `0/1` entry left (`test_repair_tool_fixes_damaged_real_file`).
- **Static search (step 2): it found no code that reads the practice table at the boss dialog.** Every `[0x4A8EBC]` access with the CR stride `0x68D4` that touches the practice table (`+0x5A4 + (level*6 + stage)*8`, so `+0x5A8` = cleared, `+0x5A9` = unlocked) is one of these:
  - `0x43D80A`, `0x43DB52`, `0x43DBD1`: Practice menu, reads `unlocked`. Locked means buzzer `0x25` and skipping the entry.
  - `0x41EB61` / `0x41EB92`: stage end, not a replay, not Extra. Writes `unlocked = 1`, then `cleared = 1`. That's where the game keeps "cleared implies unlocked".
  - `0x41CB46`: run start, reads the HUD hi-score (the score word only).
  - `0x42DAD8`, `0x42E7BC`: end of a Practice run, max of the score word only.
  - `0x4393B0`: unlock-all routine, sets every `unlocked` byte and the Extra bits.
  - `0x4379A1` and `0x437xxx`: load and save, copying whole chunks.

  The other stride sites use rankings (`+0x8`), spell history (`+0x66C + card*0x90`), play counts (`+0x590`) and play time (`+0x594`). No loop or wait reads `unlocked` or `cleared`, so the hang isn't a direct read of those bytes. It may come from something derived at load. **The fix enforces the invariant instead:** the client never writes `cleared = 1` with `unlocked = 0`, never locks an entry the save already had, and `--repair` restores the invariant offline. Batch 44 R7 checks it in game: T5 with the fixed client, T6 with a repaired damaged save. If T6 still freezes, the next suspects are the fully locked shots and difficulties.
- Decision (default implemented) listed under batch 44's `## Decisions to confirm`: Practice stays as open as the save already was; the check filter (16) guards checks.
