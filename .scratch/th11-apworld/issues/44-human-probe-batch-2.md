# 44: [human] Probe batch 2

Status: ready-for-human
Blocked by: 42

## Problem
In-game facts for tickets 33, 35, 36, 40, 42 and 43, collected so the human answers them in one session (AGENTS.md: "In-game facts go to the probe batch"). Agents append `R<n>` requests while this batch is open. It's blocked by 42 because R1 needs 42's `/writelog`. Claude prepares a simplified checklist (`.agent-loop/44-simplified.md`) before the session.

## DoD
Every request below has its pasted output under `## Comments`, or "not reached".

## Test plan
Session setup: as in batch 32. One `th11.exe`, the client from the latest `main`, game folder `.games/sa` (everything unlocked) unless a request says otherwise.

### R2, needed by 40 (from batch 32 R9-S3, mistyped there): the hook bytes
- With `/itemsound on` and one item sound played: `/peek 429058 5` → paste (expect `e8 a3 1e 06 00`).

## Decisions to confirm

## Steps
1. Do the setup, then every `R<n>` in order. Paste each under `## Comments`, labeled `R<n>`.
2. Set `Status: done`; the follow-ups unblock.

## Deferred
- None.

## Comments
