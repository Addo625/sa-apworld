# Touhou 11 ~ Subterranean Animism Apworld

This is an implementation of Touhou 11 (v1.00a `th11.exe`) for [Archipelago](https://github.com/ArchipelagoMW/Archipelago).<br />
Ported from Nepley's EoSD apworld.

## How does this randomizer work ?
At the start, you have only one shot type, zero resources and only the Lunatic difficulty.<br />
You play stage by stage in Practice Mode and unlock the stages progressively. Each item makes the stages easier to clear.<br />
**Goal:** clear Stage 6 (Utsuho) with either character.

## Locations
For each character (Reimu, Marisa), in stages 1 to 6:
* Midboss Defeated (Stage 4 instead: Cat Orin's First and Second Appearance, each survived until she leaves)
* Boss Defeated
* Stage Cleared

## Items
* Shot Types (Reimu A/B/C, Marisa A/B/C)
* Next Stage (Practice Mode)
* +0.50 Power
* +1 Life
* Lower Difficulty

**Filler**: +0.05 Power

## Options
**Exclude Lunatic:** You can exclude the Lunatic difficulty and therefore start on Hard.

**Resources:** You can set the lives, power packs and difficulty expected for stages 3/4 (Yuugi, Satori) and stages 5/6 (Orin, Utsuho). The requirement ramps up stage by stage. If a gate can't fit in the locations open before its stage, it is lowered and generation logs a warning naming the stage.

**Death Link:** Not implemented yet; the option does nothing.

## How to use

**Back up your score.dat if you care about your scores and practice stage access.**

1. Put `th11.apworld` in Archipelago's `custom_worlds` folder and generate with a YAML like [`examples/th11.yaml`](examples/th11.yaml).
2. Launch the game.
3. Launch the Touhou SA client found in the Archipelago launcher.
4. Connect the client to the server.

## Linux / macOS (Wine) Notes

The Windows version of Archipelago must be installed in the same Wine prefix as Touhou.

* The client attaches to the game by process name (`th11.exe`), so it also finds the game when it runs under the thcrap English patch.
* If the client window doesn't render under Wine, start it with `--nogui`.

## Building

`tools/build_apworld.sh` writes `dist/th11.apworld`. `tools/check_apworld.sh` builds it, generates a seed from the zip with the dev Archipelago checkout (`tools/setup_dev.sh`), and checks that AP loaded the zip, not the dev symlink.
