# 46: Block the menu cursor on locked choices instead of snapping it back

Status: ready-for-agent
Blocked by: 38

## Problem
16 and 38 guard the difficulty (menu 1), character (menu 2) and shot (menu 3) selects by writing `ADDR_MENU_CURSOR` back on every 0.5 s poll. Probe 32 R6 M2: it works, but the cursor reaches a locked choice for a moment and then snaps back, so the human saw it "move only sometimes, as if locked" and thought the menu was broken. MoF's `initCursorHack` instead patches the menu's cursor-move code so a locked choice is skipped.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below; then the probe batch request below confirms in game that the cursor skips locked choices without a flicker.

## Test plan
- **Find the sites (static, no game):** in `th11.exe`, the cursor-move handlers of menus 1, 2 and 3 (they write menu object `+0x24`, `ADDR_MENU_CURSOR`). Record each site with `# source: disassembly 0x…` and its `EXPECTED_BYTES`.
- **Patch:** a code cave (like the sound cave, `safe_patch`) that after a move reads a per-menu allowed-mask the client writes into slack memory, and steps on past masked choices. The client writes the masks from `guard.unlocked_difficulties` / `guard.unlocked_shots` each poll.
  - Tests against `FakeMemory`: the cave installs only over the expected bytes (`test_cursor_cave_refuses_unexpected_code`), the masks match the received items (`test_cursor_masks_from_items`).
- Keep `guard.correct` and its write as the fallback (cave refused, or masks not yet written).
- Unknown addresses go to the open probe batch per AGENTS.md (e.g. confirm the cave in game: move across a locked difficulty with no flicker).

## Steps
1. Locate the cursor-move sites by disassembly; record them in `Variables`.
2. Write the cave and mask writes with tests. Run the DoD.
3. Add the in-game check to the open probe batch.

## Deferred
- None.

## Comments
- 2026-10-12 al-work (38): split out of 38's notes (the "prefer blocking the move" UX note). 38 shipped the snap guard for menus 2 and 3, which has the same flicker.
- 2026-10-18 Claude (human promoted it; a bounded static search, not finished):
  - **Not found:** no `inc`/`dec`/`add`/`sub` of the cursor (`menu + 0x24`) sits within 40 instructions of a menu-id read (`menu + 0xB0`). The cursor is set by a computed `mov`.
  - **Leads:**
    - menu-id writes at `0x411924` (`mov [eax+0xB0], edx`) and `0x4139AE` (`mov [ebx+0xB0], edx`), plus `0x40460C` / `0x404988` (`[ebx+0xB0]`);
    - one cursor-like `inc dword [edi+0x24]` at `0x40F136`.
  - **Next:**
    - disassemble the functions around `0x411924`/`0x4139AE`;
    - find where the difficulty/shot select reads input and stores `menu + 0x24`;
    - patch that store through a cave that skips choices flagged locked in a client-written byte table (MoF `initCursorHack`), with `safe_patch` and `EXPECTED_BYTES`;
    - in-game check in the next probe batch.
  - Until then the 0.5 s snap (16/38) stays.
