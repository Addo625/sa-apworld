# 58: [human] Probe batch 4

Status: done
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

### R6, needed by 24: a spell capture sends a capture check
Seed `AP_96277890279384246223`, slot **`Playtest2`** (Playtest1's settings + `spell_card_keys: alongside`): `python MultiServer.py output/AP_96277890279384246223.zip`. Captures persist in the save, so use one where Kisume's Lunatic card was never captured with that character (e.g. a fresh save).
- Practice Stage 1, Lunatic (Kisume's card exists on Hard/Lunatic only). Capture Kisume's card: does the client log `Spell card 1 captured: [<character>] Stage 1 - Capture 1` right away, or only when the run ends?
- Capture the same card again in a later run: nothing new is sent.
- Fail a card (bomb or get hit): nothing is sent.
- Paste the client lines.

## Decisions to confirm
- 24: once R6 passes, `spell_card_keys` defaults to `alongside` (the target from 21). Until then it stays `off`.
- 59: `min_lives` adds to the +1 Life count (not a floor), so every item still raises the start. OK?

## Comments

### R1

ADDR_MENU = 0 (addr 0x02D51F80)
ADDR_GAME_FLAGS = 0 (addr 0x004A5758)

#### a
/peek 02D51F80-B0 256
0x02D51ED0: c8 03 4a 01 b8 03 4a 01 18 fc cb 02 48 fc cb 02 68 fe 4a 01 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3f 00 00 80 3f 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 38 42 00 00 00 00 00 00 00 00 09 00 00 00 0a 00 00 00 00 00 20 41 48 79 4a 00 01 00 00 00 00 00 21 3f 00 00 c2 3e 00 00 3f 3f 00 00 c2 3e 00 00 21 3f 00 00 0f 3f 00 00 3f 3f 00 00 0f 3f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#### b
0x02D51ED0: c8 03 4a 01 b8 03 4a 01 18 fc cb 02 48 fc cb 02 68 fe 4a 01 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3f 00 00 80 3f 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 38 42 00 00 00 00 00 00 00 00 09 00 00 00 0a 00 00 00 00 00 20 41 48 79 4a 00 01 00 00 00 00 00 21 3f 00 00 c2 3e 00 00 3f 3f 00 00 c2 3e 00 00 21 3f 00 00 0f 3f 00 00 3f 3f 00 00 0f 3f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#### c
0x02D51ED0: c8 03 4a 01 b8 03 4a 01 18 fc cb 02 48 fc cb 02 68 fe 4a 01 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3f 00 00 80 3f 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 38 42 00 00 00 00 00 00 00 00 09 00 00 00 0a 00 00 00 00 00 20 41 48 79 4a 00 01 00 00 00 00 00 21 3f 00 00 c2 3e 00 00 3f 3f 00 00 c2 3e 00 00 21 3f 00 00 0f 3f 00 00 3f 3f 00 00 0f 3f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#### d
0x02D51ED0: c8 03 4a 01 b8 03 4a 01 18 fc cb 02 48 fc cb 02 68 fe 4a 01 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3f 00 00 80 3f 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 38 42 00 00 00 00 00 00 00 00 09 00 00 00 0a 00 00 00 00 00 20 41 48 79 4a 00 01 00 00 00 00 00 21 3f 00 00 c2 3e 00 00 3f 3f 00 00 c2 3e 00 00 21 3f 00 00 0f 3f 00 00 3f 3f 00 00 0f 3f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#### e
0x02D51ED0: c8 03 4a 01 b8 03 4a 01 18 fc cb 02 48 fc cb 02 68 fe 4a 01 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 e4 1e d5 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 3f 00 00 80 3f 00 00 00 00 00 00 00 00 00 00 f0 41 00 00 38 42 00 00 00 00 00 00 00 00 09 00 00 00 0a 00 00 00 00 00 20 41 48 79 4a 00 01 00 00 00 00 00 21 3f 00 00 c2 3e 00 00 3f 3f 00 00 c2 3e 00 00 21 3f 00 00 0f 3f 00 00 3f 3f 00 00 0f 3f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

### R2

**the `/send [Reimu A] Extra Stage` does not unlock the extra stage - cannot check**

### R3

**CONSISTENT CRASH** at first message of dialogs - can't complete stage

### R4 

Works well, for each stage shows the count of checks left (maybe worth to think of a way to split it _textwise_ between boss checks and spell checks)

### R5

From stage 2 onwards, I start with 4 Power (max). I always get the correct amount of lives.

### Claude, 2026-10-19
- **R1:** the five dumps are byte-identical and all at the title's menu object (`ADDR_MENU = 0`), so the address wasn't re-read per screen. Redo as batch 61 R1, with a fresh `/probe` on each screen.
- **R2:** with global unlocks the item is `Extra Stage` (the README now lists the names per grouping), and the server's form is `/send <slot> <item>`: `/send Playtest2 Extra Stage`. Redo as batch 61 R2.
- **R3:** the crash happened at every dialog. Suspect: 24 read 25 KB of save data every poll during play. Now the save is read only on menus and at stage transitions. Re-test is batch 61 R3, which also carries the continue screen request.
- **R4:** OK. The counts now split into boss checks and captures (`685d262`).
- **R5:** stage 2+ started at 4.00 because the client kept the game's power when it was higher. Practice now starts at exactly packs × 0.50 (60, `e45d0c8`). Lives OK.
- **R6 (from the chat):** a capture was detected and sent. Kisume captured twice sent Capture 1 and 2: a crash lost the first capture from the save, so the card looked new. Captured cards now also live in server data storage (24, `bb232d1`).
