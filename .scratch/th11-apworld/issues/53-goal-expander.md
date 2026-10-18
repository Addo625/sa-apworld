# 53: Goal options per ending: Utsuho once / both characters / N shots, plus Koishi none / once / both

Status: done
Blocked by: 51

## Problem
The goal was one choice (`goal`: utsuho / koishi / both) times one count (`ending_required`: once / both characters / all shot types). The human wants the two endings counted separately, and "N shot types" instead of only "all six" (decision 2026-10-18).

## What to do
- Options `utsuho_endings` (once / both_characters / shot_types), `utsuho_shots` (1–6) and `koishi_endings` (none / once / both_characters). They replace `goal` and `ending_required` (unreleased, no compatibility shim).
- **The goal is met when both parts are met.** `Rules.goal_met(count, utsuho, utsuho_shots, koishi)`. For shot_types, the Utsuho endings of both characters add up to the shots that cleared (each shot's Stage 6 Clear holds one).
- `generate_early`: `shot_types` turns `shot_type` on, and Koishi > none turns `extra_stage` on (linear), each with a warning. Locked endings: Utsuho always, Koishi when needed. `fill_slot_data` and `receive.goal_reached` read the new keys.
- README and `examples/th11.yaml` updated.

## Deferred
- A live check of a Koishi or N-shots goal: verified only by generation and tests (ticket 51 proved the Utsuho-once path live).
