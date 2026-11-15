# 92: every code patch freezes the game by construction

Status: done
Blocked by: None

## Problem
The `ponytail:` at `patching.py:59` said `patch_value` writes live code non-atomically, so the game could run half-written bytes and crash. That was stale: 40 added `gameController.suspended()` (NtSuspendProcess + FlushInstructionCache) and 49/80 wrapped all three `patch_value` callers in it. What was left: freezing was a convention at each call site, so a new caller that forgot it would reopen the crash batch 44 #12 hit (a torn 5-byte hook write), and the comment misled readers.

## DoD
- `pytest worlds/th11/test -q` passes with the tests below.
- No `suspended` left in `Client.py`; `patching.safe_patch` and `patch_value` freeze the game themselves.
- In game (optional): the item sound and Practice lives/power patches still work.

## Design
- `patching.frozen(reader_writer)`: `reader_writer.suspended()`, or `nullcontext` for readers without it (test fakes). `safe_patch` and `patch_value` run their check **and** write inside it, so nothing can change the bytes between the two.
- The call-site wrappers in `Client` go. The sound cave write is now frozen too; it isn't run until the hook points at it, but one more freeze per game process costs nothing.

## Test plan
- `test_client.TestCodePatchesFreezeGame.test_hook_written_while_game_is_suspended`: the cave and the hook are each written between a suspend and a resume.
- `test_client.TestCodePatchesFreezeGame.test_patches_write_only_frozen`: `patch_value` and `safe_patch` write only frozen; a refused patch (someone else's bytes) writes nothing and still resumes.

## Steps
1. `patching`: `frozen`, used by both patchers; drop the ponytail. 2. `Client`: drop the four wrappers. 3. Tests, install.

## Deferred
- NtSuspendProcess's NTSTATUS isn't checked: no failure has been seen, and Wine implements it.
- A hard kill of the client between suspend and resume would leave the game frozen; the window is microseconds.
