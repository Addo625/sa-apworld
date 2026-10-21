# 75: Spell Card Key locks: hold X keys or the stage stays closed

Status: ready-for-agent
Blocked by: None

## Problem
Spell Card Keys are a soft gate today: `spell_card_keys_required` (a % of the pool's keys) only steers item placement, and the game never blocks anything. In a solo seed keys feel like filler (human, 2026-10-21). The human wants keys to really lock stages while avoiding BK. Design grilled 2026-10-22.

## Decisions
- **The job:** keys are a finale ticket, plus one optional mid-run toll. Locks apply in **Practice mode only**; normal seeds ignore them, with a warning.
- **Held, not spent:** the toll ≤ the final lock; the generator raises the final lock to the toll if a YAML sets it lower.
- **A locked stage needs its `Next Stage` AND the keys.** Keys count from anyone's captures (no per-character keys).
- **Slack:** the game opens a lock at X keys, while logic plans for X + `key_lock_slack`.
- **Lowering:** if the pool or the checks before a lock can't hold enough keys, the generator lowers the lock (and the pool count) with a warning.
- **Removed:** the soft key gate (`spell_card_keys_required`, the quarter ramp in `stage_requirements`) and `keys_only`.

## Options (Spell Card Keys section)
| Option | Values | Default |
|---|---|---|
| `spell_card_keys` | toggle: captures and keys on/off (replaces off/alongside/keys_only) | on |
| `spell_card_keys_in_pool` | a **count** of Spell Card Keys, at most the capture checks | 12 |
| `spell_card_keys_local` | toggle: keys stay in your own world | false |
| `key_lock_toll` | keys held to open the toll stage and later | 0 |
| `key_lock_toll_stage` | 3 / 4 / 5 | 5 |
| `key_lock_final` | keys held for the final target | 6 |
| `key_lock_final_target` | `stage_6` (Stage 6 and Extra) / `goal` / `extra` | `stage_6` |
| `key_lock_slack` | extra keys logic places before each lock | 2 |

## What to do
- **`Options.py`:** the options above. `CapturesPerStage` / `CaptureSlots` stay as they are.
- **`__init__.py`:**
  - `generate_early` clamps the locks (≤ the pool, toll ≤ final) with warnings;
  - `spell_card_keys_local` adds Spell Card Key to `local_items`;
  - the key count is the absolute option, capped by the capture checks;
  - keys are progression only when a lock is > 0, otherwise filler;
  - slot data carries the clamped locks and the target.
- **`Rules.py`:**
  - drop the key quarter ramp from `stage_requirements`;
  - `stage_unlocked(..., locks)` adds the key count per level in Practice mode: toll stage and up need the toll; Stage 6 and Extra need the final lock (target `stage_6`), or Extra only (target `extra`);
  - logic uses X + slack, while the client passes X;
  - `goal_met(..., keys)` for target `goal`.
- **`receive.py`:** `stage_open`, `practice_open`, `extra_shots` and `goal_reached` read the locks from slot data. The Practice menu then hides a key-locked stage, runs on it send nothing, and Extra stays locked.
- **`tracker.py`** (human's layout):
  - right under the goal line, and **only when a lock is set**: one key row, e.g. `Keys 4 held · Stage 5 opens at 3 (open) · Stage 6 opens at 6 (2 more)`. It shrinks to `Keys 7 held (all locks open)` once every lock is open;
  - a LOCKED stage line names `Spell Card Key k/X` next to `Next Stage` only when keys block it;
  - open stages never mention keys, and the slack never appears.
- **Docs:** README (Spell Card Keys: locks, held totals, Practice only, slack, final target) and `examples/th11.yaml`.

## Test plan
- **`test_key_locks`:**
  - the toll stage is unreachable below X + slack keys and reachable at it;
  - the final target stage_6 / goal / extra;
  - locks 0 leave keys as filler;
  - clamping warnings;
  - `spell_card_keys_local` keeps keys in the player's world;
  - fill over fixed seeds with locks (added to the extremes).
- **`test_receive`:** `practice_open` hides a key-locked stage until X keys (not X + slack); `goal_reached` with target goal.
- **`test_tracker`:** the key row appears only with locks, shows held/opens-at/N-more, shrinks when all are open; the LOCKED line names the keys.
- **`test_generate` / `test_captures`:** update for the absolute pool count and the removed soft gate.

## Deferred
- In-game check through the next probe batch: the Practice menu hides the toll stage until X keys (`/send <slot> Spell Card Key`), and the final target behaves.
