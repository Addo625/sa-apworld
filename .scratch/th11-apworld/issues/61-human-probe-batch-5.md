# 61: [human] Probe batch 5

Status: ready-for-human
Blocked by: None

## Problem
Batch 58 left: the dialog crash (R3), menu dumps that were all of the title (R1), the Extra check (R2), plus re-checks of 60's power and 24's capture fixes. One session. Agents may append requests.

## Test plan
Setup: the client from the latest `main` (Claude reinstalled it), seed `AP_96277890279384246223`, slot **`Playtest2`**, `/writelog on`. Keep the game folder's save as is: captures already sent stay recorded on the server now.

### R1, needed by 24: the dialog crash is gone
- Practice Stage 1 and Stage 2, play through every dialog. Then a Start run through Yamame's dialog.
- If it still crashes: `/itemsound off`, restart the game, and try once more. Paste the last 20 client lines either way.

### R2, needed by 48: what tells the Options screen apart
On each screen, **first `/probe`**, then `/peek <the ADDR_MENU addr on that screen's probe>-B0 256`:
(a) title, (b) Option, (c) Start → difficulty select, (d) Practice → difficulty select, (e) Esc from the character select back to the difficulty select. Paste each probe's `ADDR_MENU_PTR` / `ADDR_MENU` lines and the peek, labeled.

### R3, needed by 56: the title cursor rows
- `/send Playtest2 Extra Stage` (the global form of the item). Does Extra Start become selectable?
- On the title, `/probe` with the cursor on Start, Extra Start and Practice Start. Paste the `ADDR_MENU` and `ADDR_MENU_CURSOR` lines.

### R4, needed by 57: the continue screen after losing to a boss
- In a Start run, lose all lives during a boss. On the continue prompt: `/probe` → paste. Quit, then `/probe` on the next screen → paste.

### R5, needed by 60: Practice power on later stages
- Practice Stage 2 or later: is the power 0.50 × the packs from `/received` (not 4.00)?

### R6, needed by 24: captures
- Capture a card you never captured with that character: does the client log `Spell card N captured: ...` after the run (back on a menu), and the server show the check?
- Capture Kisume's card again: the client logs `captured before`, and nothing is sent.

## Decisions to confirm
- 24: the same spell on another difficulty is a different card (each difficulty has its own card ID in the game). Should it count as the same card instead?
- 24: once R1 and R6 pass, `spell_card_keys` defaults to `alongside`.

## Comments
