# 50: [human] Probe batch 3

Status: done
Blocked by: None

## Problem
In-game facts for 40 and 48, collected for one short session (AGENTS.md batch rule). Agents may append requests.

## DoD
Every request below has its pasted output under `## Comments`, or "not reached".

## Test plan
Setup: one `th11.exe` from `.games/sa` with a **brand-new save** (none in the folder), the client from the latest `main`, connected to seed `AP_44200369373081064148` (slot `Playtest1`, start shot Marisa C). Checklist: `.agent-loop/50-simplified.md`, followed by a full playtest of that seed.

### R1, needed by 48: what the Options screen looks like to the guard
- Title → Option (the settings screen): `/probe` with the cursor on two different rows. Paste the `ADDR_MENU_PTR`, `ADDR_MENU`, `ADDR_MENU_CURSOR` and `ADDR_GAME_FLAGS` lines of each.
- For comparison, the same four lines on the Start difficulty select and on the shot select.

### R2, needed by 40: the hook install no longer crashes
- Three times: start a **fresh** `th11.exe`, connect, `/writelog on`, `/itemsound on`, Practice Stage 1, `/send <slot> +1 Life`. Each time: crash, or sound and star? Paste the writes.
- After one good install: `/peek 429058 5` → paste (expect `e8 a3 1e 06 00`). Play through Yamame's dialog: no crash?

### R3, needed by 52: a stage the items haven't opened sends nothing
- Before any `Next Stage`: Start (normal game) with Marisa C, and play into Stage 2. Expect the client line `Marisa C Stage 2 isn't unlocked: this run sends no checks`, and no Stage 2 check when its midboss or boss goes down. Paste the lines.

### R4, needed by 49: Practice starts with the received lives
- In a menu, note how many `+1 Life` you've received (the client's `/received`). Start a Practice run: do the HUD stars equal that number (0 if none)? Then `/send Playtest1 +1 Life`, go back to the menu, start Practice again: one more star?

### R5, needed by 43: the -1 Life trap buzzes
- With `/itemsound on` (after R2 passed) and at least 2 lives, in a run: `/send Playtest1 -1 Life`. About 2 s later: a buzzer (not the death sound), and the stars update at once?

## Steps
1. Do R1 and R2, paste under `## Comments`, set `Status: done`.

## Deferred
- None.

## Comments

- 2026-10-18 human (via Claude, from `.agent-loop/50-simplified-results.md`):
  - **R1:** Options screen: `ADDR_MENU = 1`, `ADDR_MENU_CURSOR = 3`, `ADDR_GAME_FLAGS = 4` (`ADDR_MENU_PTR` 0x394D0E8). The guard still moves the cursor there. The difficulty and shot select comparisons weren't pasted; probe 06 had the difficulty select at flags 0 and the character/shot select at 4. → 48.
  - **R2:** the install worked (`write 0x004CAF00` after `+1 Life`, no crash), and `/peek 429058 5` = `e8 a3 1e 06 00`. → 40: sound on by default.
  - **R3:** a normal Start run into Stage 2 sent Stage 2 checks. Not a 52 bug: Kisume's midboss gave `Next Stage` in the same run, so Stage 2 was open. But losing to Parsee in that run sent `Parsee Defeated` + `Stage 2 Clear`. → 55 (Practice seeds ignore Start runs), 56 (deferred: block Start), 57 (a boss loss isn't a kill).
  - **R4:** set aside by the human (Practice lives look doubled when an item arrives mid-run); Q1 → 59 `min_lives`.
  - **R5:** buzzer and HUD OK.
  - **Q2:** the gates can't be tracked → 54 (Tracker tab).
  - The full playtest comes in a separate file.
