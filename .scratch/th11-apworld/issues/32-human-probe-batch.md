# 32: [human] Probe batch 1

Status: ready-for-human
Blocked by: 09

## Problem
In-game facts the agents can't get themselves, collected so the human answers them all in **one** game session (AGENTS.md: "In-game facts go to the probe batch"). Agents append `R<n>` requests here while this batch is open.

## DoD
Every request below has its pasted output under `## Comments`, or the note "not reached". `## Decisions to confirm` has a yes or a change for each item.

## Test plan
Session setup (once):
1. Close every game, then start one game through `custom.exe`. Check that only one `th11.exe` runs (`~/archipelago/wine.sh tasklist 2>/dev/null | grep th11`).
2. Start the client: `cd ~/archipelago/install-wine && ../wine.sh explorer /desktop=AP,1280x800 ArchipelagoLauncher.exe "Touhou SA Client"`.
3. Use the apworld from the latest `main`: `tools/build_apworld.sh && cp dist/th11.apworld ~/archipelago/install-wine/custom_worlds/`.

### R1, needed by 33 (from 11): where SA stores the Extra unlock per shot type
Context: `ADDR_EXTRA_UNLOCK` is `None`. The only lead is thcrap's `fix_extra_stage_relocking` patch at `Rxede8`. 27's practice table has no Extra row.
- **E1:** with a save where at least one shot has Extra and one doesn't, run `tools/scoredat.py` and paste the `CR` chunk's clear counts per shot (the 5 counts after play time; the 5th level is Extra).
- **E2:** in the running game, `/memsearch` the save struct around 27's copy 1 (`…1BB8`) for the field E1 points at; paste matches.
- **E3:** change that byte (with 28's `/poke`, once it exists, or a memory editor) for a shot without Extra, open the Extra menu, and note whether the shot is now offered.

## Decisions to confirm

## Steps
1. Do the session setup, then every `R<n>` in order. Paste each one's output under `## Comments`, labeled `R<n>`.
2. Answer `## Decisions to confirm`. Set `Status: done`; the follow-ups unblock.

## Deferred
- None.

## Comments
