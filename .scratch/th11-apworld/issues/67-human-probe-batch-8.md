# 67: [human] Probe batch 8: captures sent mid-stage

Status: ready-for-human
Blocked by: None

## Problem
66 sends a capture check the moment a card ends captured, reading the running card from the game. It needs an in-game check, and a watch for any return of the dialog crash (58), since the client reads a few dwords in play again.

## Test plan
Setup: the client from the latest `main` (Claude reinstalled it). A seed with `spell_card_keys` on, and a fresh save.

### R1: a capture sends its check right away
- Practice Stage 1 or 2: capture a card you never captured with that character. Within about a second, mid-stage, the client logs `Spell card N captured: ...` and the server shows the check.
- Fail a card (bomb or get hit during it): nothing is sent.
- Capture the same spell again: `this spell was captured before`, nothing sent.

### R2: no dialog crashes
- Play through Stage 1 and 2 including every dialog, twice. Any crash: paste the last 20 client lines, and Wine's crash details if shown.

## Comments
