# 58: [human] Probe batch 4

Status: ready-for-human
Blocked by: None

## Problem
In-game facts for 48, 56 and 57, plus a first look at 54's Tracker tab, collected in one session (with the playtest if it fits). Agents may append requests.

## Test plan
Setup: the client from the latest `main`, connected to any seed (Playtest1 is fine), `/writelog on`.

### R1, needed by 48: what tells the Options screen apart from the difficulty select
`ADDR_MENU` reads 1 on both, and `ADDR_GAME_FLAGS` bit 4 is the game's "new high score" bit (set at `0x41EFA4`, cleared at run start), so neither works. Dump the menu object on each screen and compare:
- `/probe`, then `/peek <ADDR_MENU addr>-B0 256`. (`ADDR_MENU addr` is the `(addr 0x...)` on the `ADDR_MENU` line; e.g. `/peek 0394D198-B0 256`.)
- Do this on (a) the title, (b) Option, (c) Start → the difficulty select, (d) Practice → the difficulty select, (e) Esc from the character select back to the difficulty select.
- Paste each `ADDR_MENU` line and the peek output, labeled.

### R2, needed by 56: the title cursor rows
- On the title, `/probe` with the cursor on Start, then Extra Start, then Practice Start. Paste the `ADDR_MENU` and `ADDR_MENU_CURSOR` lines of each.

### R3, needed by 57: the continue screen after losing to a boss
- In a normal-mode run (Start), lose all lives during a boss fight. On the continue prompt: `/probe` → paste everything. Then pick "No"/quit, and `/probe` again on the next screen.

### R4, needed by 54: the Tracker tab
- Does the client show a **Tracker** tab next to Archipelago/Hints? Does it update within a second or two when an item arrives or a check is sent? Is it readable (font, scrolling)? A screenshot or a short note.

### R5, needed by 60: Practice runs start with the packs' power (and no double life)
- Note `/received`: how many `+0.50 Power` and `+1 Life`. Start a Practice run: is the power 0.50 × packs (at most 4.00), and the lives as before?
- In the menu, `/send <slot> +0.50 Power` and `/send <slot> +1 Life`, then start Practice: exactly +0.50 power and one more star (batch 50 R4 got two)?
- Pause → Retry: does the power stay?

## Decisions to confirm
- 59: `min_lives` adds to the +1 Life count (not a floor), so every item still raises the start. OK?

## Comments
