# 70: Never pause the game; patch code only on a settled menu

Status: ready-for-agent
Blocked by: None

## Problem
A crash at game launch (`.agent-loop/backtace-69-1608.txt`: a page fault in wow64 32-bit code at `0x7bd7123d`, an address in no module, i.e. a thread resumed into a corrupted context), a freeze on a dialog textbox, a freeze while loading, and a crash 1 s after the first item sound of a game process. All of them line up with the client freezing the game (`gameController.suspended()`, NtSuspendProcess). Under Wine on Apple silicon (Rosetta, wow64), the thread signals that implement it are a weak spot.

## What to do
The full plan is in `.claude/plans/crash-fix-no-suspend.md`:
- remove `suspended()`;
- make code writes (lives patches, the sound hook) only on a settled menu (`state.menu is not None and not state.in_game`);
- install the sound code on a menu, the hook as one aligned 4-byte write;
- item sounds back to opt-in until clean sessions confirm.

## Deferred
- None. Waiting for the human's go.
