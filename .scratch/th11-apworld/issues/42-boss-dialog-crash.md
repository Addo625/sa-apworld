# 42: The game crashes at the boss dialog: suspect the item-sound hook

Status: ready-for-agent
Blocked by: 29

## Problem
The game (Wine 11, v1.00a) crashed three times during probe batch 32: on reaching Yamame's pre-boss dialog in Practice Stage 1, on a client reconnect, and on connecting while a title demo played. Each time, the client log just ends with `Lost th11.exe (… GetLastError: 5)`, with no traceback. This blocks real play: every stage has a boss dialog.

**What `/itemsound on` (ticket 40) changes in the game:** the first time a received item has a sound, the client writes two pieces of code into `th11.exe`'s own `.text`:
1. A 46-byte **code cave** at `0x48AF00` (unused space at the end of `.text`).
2. A 5-byte **hook**, `call 0x48AF00` (`e8 a3 1e 06 00`), over the instruction at `0x429058` inside the per-frame sound update.

From then on, every time the game runs `0x429058` it detours into the cave. The cave does:
- `pushad`;
- if the sound-ID dword at `0x4CAF00` is non-zero: clear it, call play-sound (`0x44A1E0`), and if `[0x4A8D84]` ≠ 0, call the lives-star redraw (`0x42098A`);
- `popad`;
- **`jmp 0x44A340`**, as a tail call. This assumes the 5 replaced bytes were exactly `call 0x44A340`.

**This code stays in the game process until the game exits.** `/itemsound off` and client restarts don't remove it. With `/itemsound` never turned on, the game's code is never touched.

**Why the hook is the prime suspect:**
- **Correlation.** All three crashes happened in a process where the cave had been installed:
  1. connecting during a demo, when sound was still on by default (before `ad713d9`); the queued `+1 Life` installed the cave and the game died 0.5 s later;
  2. the 02:19 reconnect, in a game where the previous client had turned `/itemsound on`;
  3. Yamame's dialog in batch Session B, after `/itemsound on` in step B3.
- **Before the cave existed,** Yamame's dialog was reached many times without a crash: probes 06, smoke 09, `/bossrec`, `/bosswatch`.
- **Why the dialog:** the boss dialog is where the boss music starts. The sound/BGM routines take a path there that plain stage play doesn't. If the replaced instruction wasn't exactly `call 0x44A340`, or other code jumps into those 5 bytes, or the hooked routine is entered there with a stack or registers the cave's tail jump doesn't preserve, the detour breaks the game. Item sounds in S1/S2 worked because they run through the common path.
- **Not proven yet:** batch 44 R1 isolates it.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_sound_hook_replaces_exactly_one_call`, `test_no_jump_into_hooked_bytes` and `test_writelog_*`. The ticket comment holds the disassembly evidence. Batch 44 has request R1 (below).

## Test plan
- **Static checks** (capstone in a pytest scratch, per the repo's disassembly note), on `.games/sa/th11.exe` (skipped if absent):
  - `test_sound_hook_replaces_exactly_one_call`: the original 5 bytes at `0x429058` decode as one `call 0x44A340`, and the cave's final `jmp` targets the same address.
  - `test_no_jump_into_hooked_bytes`: no branch in `.text` targets `0x429059..0x42905C`, the middle of the hooked instruction.
  - Record the caller paths into the routine containing `0x429058` (who calls it during dialog or BGM changes) in the ticket comment.
- **If a check fails, or the dialog path looks unsafe:** fix the cave (replay the original instruction exactly), or move the hook to a site that only runs in plain per-frame play, still through `safe_patch` with `EXPECTED_BYTES`, and keep 40's tests green.
- **`/writelog on|off`:** logs every client memory write as `write 0x<addr> <n> bytes (<caller>)`. Off by default. `test_writelog_logs_each_write`, `test_writelog_off_logs_nothing`.
- `/itemsound` stays off by default until batch 44 R1 passes; then flip it on in this ticket's follow-up, or in 40.

## Steps
1. The static checks and caller-path notes. Fix the cave or hook if they show a problem.
2. `/writelog` with tests. Run the DoD.
3. Add **R1** to probe batch 44:
   - fresh game, `/writelog on`;
   - (a) never turn on `/itemsound`, play Practice Stage 1 to Yamame's dialog → crash?
   - (b) restart the game, `/itemsound on`, `/send` one `+1 Life` early in the stage, play to the dialog → crash?
   - Paste the last 20 client lines of each.

   A crash in (b) only confirms the hook. A crash in (a) too means another write: `/writelog` shows the last one.

## Deferred
- Trap and link life-change feedback through the cave → 43 (waits on this).

## Comments

- 2026-10-12 al-work stopped (not counted, see AGENTS.md "Leftover work"): the working tree was not clean at start, so the iteration stopped before touching anything. The dirty files (`th11/Client.py`, `th11/gameController.py`, `th11/probe.py`, `th11/test/test_client.py`, last written 04:20) are this ticket's unfinished work from the 04:20 iteration that hit the session limit (log `.agent-loop/log/20261012-034312-7.txt`): `/writelog` + `probe.log_write`, and the two static tests `test_sound_hook_replaces_exactly_one_call` / `test_no_jump_into_hooked_bytes`. Still missing: the `test_writelog_*` tests, the disassembly/caller-path comment, and R1 in batch 44. Left in place, not stashed. Next: the human keeps it (`git stash` it, the loop's next run can `git stash pop`) or drops it (`git checkout -- th11`), then reruns the loop.
- 2026-10-12 al-work stopped (not counted, see AGENTS.md "Leftover work"): working tree still dirty at start (same four `th11/` files, +57/−1, unchanged since the previous note); stopped before touching anything. This is the 2nd failed attempt, so the next run marks 42 `needs-human`. Fix: `git stash` or `git checkout -- th11`, relabel `ready-for-agent` if needed, rerun the loop.
- 2026-10-12 al-work: 2 failed attempts, both stopped because the working tree was dirty (the same four `th11/` files, +57/−1: the unfinished 04:20 work on this ticket). Marked `needs-human`. Fix: keep the work (`git stash`; the next run can `git stash pop`) or drop it (`git checkout -- th11`), set `Status: ready-for-agent`, then rerun the loop. 40 and 43 wait on this ticket.
- 2026-10-12 planner: reset. The dirty `th11/` files are this ticket's own leftover work (04:20 run, cut off by a session limit). Per AGENTS.md's new "Leftover work" rule, continue from them: add the `test_writelog_*` tests, the disassembly/caller-path comment and batch 44 R1, then commit everything as 42.
