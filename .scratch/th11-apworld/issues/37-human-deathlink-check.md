# 37: [human] DeathLink with two clients

Status: ready-for-human
Blocked by: 36

## Problem
DeathLink's two directions are only tested against fake memory (14, 36). Nobody has seen a death go out to another player, or a received one kill the player.

## DoD
The two checks below pasted under `## Comments`, each with what happened.

## Test plan
Setup: a seed with two slots and `death_link: true` on both (two Touhou SA slots, or one Touhou SA slot and any game with DeathLink); host it, connect both clients.
- **D1 (out):** in a Touhou SA Practice stage, lose a life. The other client logs the DeathLink (and its player dies). Paste both clients' lines.
- **D2 (in):** die in the other game. The Touhou SA player dies within about a second, and its client does **not** send a death back. Paste the lines.
- **D3 (amnesty):** `/deathlink_amnesty 1`, lose two lives: only the second is sent.

## Steps
1. Setup, then D1–D3. Paste under `## Comments`, set `Status: done`.

## Deferred
- None.

## Comments
