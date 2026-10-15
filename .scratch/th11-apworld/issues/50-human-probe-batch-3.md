# 50: [human] Probe batch 3

Status: ready-for-human
Blocked by: None

## Problem
In-game facts for 40 and 48, collected for one short session (AGENTS.md batch rule). Agents may append requests.

## DoD
Every request below has its pasted output under `## Comments`, or "not reached".

## Test plan
Setup as in batch 44: one `th11.exe` from `.games/sa` (clean save), the client from the latest `main`, connected to the `Batch44` seed.

### R1, needed by 48: what the Options screen looks like to the guard
- Title → Option (the settings screen): `/probe` with the cursor on two different rows. Paste the `ADDR_MENU_PTR`, `ADDR_MENU`, `ADDR_MENU_CURSOR` and `ADDR_GAME_FLAGS` lines of each.
- For comparison, the same four lines on the Start difficulty select and on the shot select.

### R2, needed by 40: the hook install no longer crashes
- Three times: start a **fresh** `th11.exe`, connect, `/writelog on`, `/itemsound on`, Practice Stage 1, `/send <slot> +1 Life`. Each time: crash, or sound and star? Paste the writes.
- After one good install: `/peek 429058 5` → paste (expect `e8 a3 1e 06 00`). Play through Yamame's dialog: no crash?

## Steps
1. Do R1 and R2, paste under `## Comments`, set `Status: done`.

## Deferred
- None.

## Comments
