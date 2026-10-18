# 51: [human] Prove a playable seed live: unlocks, a locked save, stages 3–4, the goal

Status: ready-for-human
Blocked by: None

## Problem
Everything a playable seed needs is built and unit-tested, but four things were never seen working in the game:
1. **Practice unlocks from items:** 39 as fixed by 47. Batch 44 only showed that the locks no longer freeze the game.
2. **A save that starts locked:** by decision 47 the client only adds unlocks, so `sa`'s cheated save hides the gates.
3. **The goal:** a Stage 6 clear → the locked `Ending - Utsuho` → the client reports `CLIENT_GOAL`.
4. **Detection on stages 3 and 4:** Yuugi's single run sends both checks; Stage 4 sends two cat-Orin checks, then Satori. Only stages 1–2 ever sent real checks.

## DoD
`## Comments` holds results for P1–P4, D3, D4, G1 (or G2) and S1, each passing or with its fix committed and the step re-run.

## Test plan
One session, checklist `.agent-loop/51-simplified.md`:
- **Seed:** `AP_55021807634502987350`, slot `Play1`. Practice, `stage_unlock: global`, progressive stages, goal Utsuho once, no traps, no DeathLink. Start shot Marisa A.
- **Save:** `.games/sa` with **no save file**, so the game creates a new, locked one. The old save is kept at `~/archipelago/saves/scoreth11.sa-1018.dat`.
- **Steps:**
  - P1: locked save before and after connect;
  - P2: Lower Difficulty;
  - P3: Next Stage;
  - P4: a new shot;
  - D3: Stage 3 detection;
  - D4: Stage 4 detection;
  - G1: a real Utsuho clear (G2: send the ending, as a fallback);
  - S1: the save afterwards, with no "cleared but locked" entries.

Where a failure would point:
- **unlocks:** `Client.unlock_practice`, `receive.practice_open` / `practice_unlock`, `ADDR_PRACTICE_UNLOCK = [0x4A8EBC, 0x5AC]`;
- **goal:** `Client.check_goal`, `receive.goal_reached` → `Rules.goal_met`, the locked endings in `th11/__init__.py`;
- **stages 3/4:** `detect.run_checks` / `step`, `Variables.STAGE4_APPEARANCES`.

## Steps
1. Run the session and paste the results into `.agent-loop/51-simplified-results.md`.
2. Claude files them here, fixes failures directly (normal work mode, not the loop), and closes the ticket.

## Deferred
- An `Ending - Koishi` / `goal: both` live check needs an Extra clear (ticket 11's goals). Its reporting can be checked the same way as G2.

## Comments
