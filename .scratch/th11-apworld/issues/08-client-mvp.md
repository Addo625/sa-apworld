# 08: The client sends stage checks and applies lives, power and stage unlocks

Status: ready-for-agent
Blocked by: 02, 07

## Problem
With verified addresses, the client must turn the game state into AP location checks, and received items into game state. That covers practice mode with global unlock, and goal Utsuho. Port the loop shape from `ref-projects/mof-apworld/Client.py` and `gameHandler.py`, and keep all the logic in the pure modules (spec: Client logic boundary).

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the `test_detect_*`, `test_apply_*` and `test_goal_*` tests below. The in-game proof is ticket 09.

## Test plan
- **`detect.step(prev_state, state)`** returns location IDs. It takes the decoded states from the 07 fixtures/decoders.
  - `test_detect_midboss`: midboss flag 1→0 during the midboss phase of stage 1 with lives unchanged by a game over → `[Reimu] Kisume - Midboss`.
  - `test_detect_boss`: the same for the boss phase → `[Reimu] Yamame Defeated`.
  - `test_detect_clear`: entering the stage-clear tally → `[Reimu] Stage 1 Clear`.
  - `test_detect_negative_menu_exit`: boss flag 1→0 because the game left `in_game` (quit, retry, game over) → `[]`.
  - `test_detect_stage4_no_midboss`: stage 4 emits only `Satori Defeated` and the clear.
  - `test_detect_marisa`: the character is mapped from the state.
- **`items.apply(item_name, state)`** returns writes `[(entry, value)]`.
  - `+1 Life` → lives +1, capped, plus practice/continue starting lives = AP count.
  - `+0.50 Power` / `+0.05 Power` → power +N, capped at 4.00.
  - `Next Stage` → the practice-unlock bytes for stages ≤ count+1, for every unlocked shot type at every unlocked difficulty.
  - `Lower Difficulty` → the unlocked difficulties.
  - Shot type → that shot's unlock rows.
  - Tests: `test_apply_life`, `test_apply_life_cap`, `test_apply_power_cap`, `test_apply_next_stage_writes_unlock_rows`, `test_apply_shot_type`.
- **Goal:** `test_goal_sent_on_ending_item`. A received `Ending - Utsuho` (locked on the Stage 6 clear) → the client sends `StatusUpdate` CLIENT_GOAL, as EoSD `checkVictory` does.
- **Reconnect:** the items are replayed idempotently. `test_apply_replay_is_idempotent`: applying the full received list twice gives the same writes.

## Steps
1. `detect.py`, plus its tests, using the 07 decoders.
2. `items.py`, plus its tests, including the cap, the practice-unlock rows and idempotent replay.
3. Wire both into `Client.py`:
   - A main loop polling every ~0.5 s through `gameController`.
   - `LocationChecks` on detect.
   - Item application on `ReceivedItems`.
   - The goal.
   - Reconnect when the game process restarts.

   Run the DoD.

## Deferred
- Normal mode → 12.
- Traps → 13.
- DeathLink → 14.
- RingLink → 15.
- Lives limit and menu guard rails → 16.
