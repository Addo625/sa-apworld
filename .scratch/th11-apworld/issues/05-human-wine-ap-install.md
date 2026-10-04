# 05: [human] Install Windows Archipelago in Wine and start the TH11 client

Status: ready-for-human
Blocked by: 03, 04

## Problem
The client and the game must share a Wine prefix (`~/.wine`, Wine 9.0), and that prefix has no Archipelago. The agent can't install a GUI app and click through it.

## DoD
In the Wine AP Launcher, "Touhou SA Client" starts and its console shows the CommonClient prompt. If the GUI doesn't render, `wine ArchipelagoLauncher.exe "Touhou SA Client" -- --nogui` (or the equivalent CLI) gives a prompt instead.

## Test plan
- Installed AP version ≥ `tools/AP_VERSION`.
- `th11.apworld` (from `tools/build_apworld.sh`) copied into the Wine AP's `custom_worlds/`.
- The client starts → you see the prompt. `/probe` without the game running → a clear "th11.exe not found" message, not a crash.

## Steps
1. Download the Windows AP installer at least as new as `tools/AP_VERSION` and run `wine <installer>.exe`. Install to the default path.
2. `tools/build_apworld.sh`, then copy `dist/th11.apworld` into `~/.wine/drive_c/ProgramData/Archipelago/custom_worlds/` (or wherever the installer put AP).
3. Start the Launcher with `wine`, open "Touhou SA Client", and run `/probe` with no game running.
4. Paste what happened (GUI or `--nogui`, the exact commands that worked) under `## Comments`. Set `Status: done`.

## Deferred
- A launcher script that starts client + game together (EoSD's Linux tip) → only if it turns out to be needed.
