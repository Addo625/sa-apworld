# 47: Practice locking from 39 corrupts the save and freezes the game at boss dialogs

Status: ready-for-agent
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
