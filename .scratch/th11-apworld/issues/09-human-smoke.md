# 09: [human] In-game smoke test (v1 DoD part 2)

Status: ready-for-human
Blocked by: 03, 08

## Problem
Only a real session proves the v1 loop: seed → server → client → game → server.

## DoD
- Clearing Practice Stage 1 with the starting shot type makes the server list `Kisume - Midboss`, `Yamame Defeated` and `Stage 1 Clear` for that character as checked.
- `/send <slot> +1 Life` on the server makes the in-game lives counter go up by 1 within 5 s.
- Quitting to the menu while Yamame is on screen sends nothing.

## Test plan
- Inputs: `tools/check_apworld.sh` output zip (or `Generate.py` with `examples/th11.yaml`), the Wine AP from 05, `th11.exe` v1.00a.
- Expected: the three observations in the DoD. Paste the client log excerpt.

## Steps
1. Generate a seed. Start `MultiServer.py <zip>` on the Mac (in `.ap`, with the venv) or in Wine.
2. Start the TH11 client in Wine, connect to the server, and start `th11.exe` (or `/launch`).
3. Do the three DoD checks. Paste the results and the log under `## Comments`. Set `Status: done`, or `needs-human` with the failure.

## Deferred
- None. Failures become new tickets via `/al-plan`.

## Comments

- 2026-10-10 al-work (from 08), worth one extra look while you're in game:
  - **`+1 Life` timing:** the life is written while a stage is running. Sent on a menu, it waits for the next stage start.
  - **Retry:** a Practice retry (pause → Retry) mid-stage should reset the boss-run count. That holds only if the enemy manager pointer hits 0 on retry, and nobody has probed that. Retry after the midboss, then kill the midboss again. Expected: no `Yamame Defeated` / `Stage 1 Clear` from that midboss kill. If they do get sent, the fix is MoF's score-drop reset.
