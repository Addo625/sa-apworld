# 64: [human] Probe batch 6

Status: done
Blocked by: None

## Problem
In-game checks for 62 (retries) and 63 (one capture per spell). Short; it fits in any play session. Agents may append requests.

## Test plan
Setup: the client from the latest `main` (Claude reinstalled it). Any Practice seed with `spell_card_keys` on; a **new seed and a fresh save** give clean capture slots (`AP_25461530409882312899`'s Stage 1 slots are used up).

### R1, needed by 62: retries send nothing and start fresh
- Practice Stage 1 or 2, fight the boss, lose all lives, pick Retry: no `Defeated`/`Clear` check is sent, and power is 0.50 × your packs.
- Fight the boss again, pause → Give up and Retry: same.
- Then actually beat the boss: its checks are sent.

### R2, needed by 63: the same spell on two difficulties counts once
- Capture a spell on one difficulty (e.g. Yamame's first card on Easy), go back to the menu: one capture check.
- Capture the same spell on another difficulty: the client logs "this spell was captured before", and nothing is sent.

## Comments

### R1

No checks for the first two runs

Third run gave the checks

### R2

Both bullets happened just as expected!

- 2026-10-21 Claude: both passed. Retries send nothing and the real kill counts (62); the same spell on another difficulty sends nothing (63).
