# 09: [human] In-game smoke test (v1 DoD part 2)

Status: done
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

- 2026-10-10 human (via Claude): **done, on macOS + Wine 11.** Seed `AP_71333992220941225534` (Mac AP 0.6.7 server, `Players/th11.yaml`, slot `Player1`, start Marisa B); client = Wine AP 0.6.7 with the apworld built from `main` at `eb66909`.
  - **First attempt failed:** 0 checks, and `+1 Life` didn't reach the game. Cause: four `th11.exe` processes were alive in the prefix (leftovers from earlier crashes), and pymem attached to the first one (PID 924), a stale process. After `wineserver -k` and one fresh game, everything below passed.
  - **DoD 1 ✅** Practice Stage 1 as Marisa B to the clear:
    ```
    Player1 found their Marisa A - Alice ([Marisa] Kisume - Midboss)
    Player1 found their +1 Life ([Marisa] Stage 1 Clear)
    Player1 found their Next Stage ([Marisa] Yamame Defeated)
    ```
  - **DoD 2 ✅ (functionally)** Server `/send Player1 +1 Life` while in a stage raised the lives value. ⚠️ The HUD only redraws on the game's own life change, and no sound plays, so there is no visible feedback (follow-up).
  - **DoD 3 ✅** Quitting during Yamame sent no Yamame check. The `[Reimu] Kisume - Midboss` sent in that run (Reimu B) was a real midboss kill earlier in the same run. It counted although Reimu B isn't owned, because the cheated save unlocks every shot (follow-up for 28: lock unowned shots/stages).
  - **Follow-ups:** item feedback (HUD redraw and/or sound), lock Practice to received shots in 28, attach to the newest `th11.exe` or warn on duplicates.
