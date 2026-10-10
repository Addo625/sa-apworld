# Touhou 11 ~ Subterranean Animism Apworld

This is an implementation of Touhou 11 (v1.00a `th11.exe`) for [Archipelago](https://github.com/ArchipelagoMW/Archipelago).<br />
Ported from Nepley's EoSD apworld.

## How does this randomizer work ?
At the start, you have only one shot type, zero resources and only the Lunatic difficulty.<br />
You play stage by stage in Practice Mode and unlock the stages progressively. Each item makes the stages easier to clear.<br />
**Goal:** clear Stage 6 (Utsuho), the Extra stage (Koishi) or both; once, with both characters or with every shot type (see **Goal** and **Ending Required**).

## Locations
For each character (Reimu, Marisa), or each shot type with **Shot Type Check**, in stages 1 to 6:
* Midboss Defeated (Stage 4 instead: Cat Orin's First and Second Appearance, each survived until she leaves)
* Boss Defeated
* Stage Cleared

With **Difficulty Check**, midboss and boss checks exist once per difficulty (`[Hard][Reimu] Yamame Defeated`).

With **Extra Stage**: `Sanae - Midboss`, `Koishi Defeated` and `Stage Extra Clear` per character or shot type (no difficulty checks).

## Items
* Shot Types (Reimu A/B/C, Marisa A/B/C)
* Next Stage (Practice Mode): global, per character or per shot type; `Stage 2` .. `Stage 6` without Progressive Stage Unlock
* Extra Stage (with **Extra Stage** apart, or linear without Progressive Stage Unlock), grouped like Next Stage. Not written to the game yet: its unlock address is still unknown.
* +0.50 Power
* +1 Life
* Lower Difficulty

**Filler**: +0.05 Power

## Options
**Mode:** practice (stage by stage in Practice Mode), normal_dynamic or normal_static. Normal mode is a full run from Stage 1: there are no Next Stage items (an apart Extra keeps its Extra Stage item), and the gates are lives, power, difficulty and shot type. With difficulty_check, normal_dynamic acts as normal_static. normal_dynamic keeps each run at the lowest difficulty your Lower Difficulty items open (never Easy). In Normal mode a continue is meant to restore one life per `+1 Life` received (up to 8); that needs the continue-lives code site (ticket 34) and does nothing until then.

**Stage Unlock:** Stage unlocks are global, per character, or per shot type. Per shot type needs Shot Type Check or Difficulty Check; otherwise it acts as per character.

**Progressive Stage Unlock:** On, `Next Stage` items unlock stages in order. Off, each stage has its own item; logic still expects the earlier stages' items, and gates are lowered more to keep seeds fillable.

**Shot Type Check:** Each shot type has its own checks instead of each character.

**Difficulty Check:** Midboss and boss checks are separate per difficulty; a difficulty's checks need its Lower Difficulty items.

**Multiple Difficulty Check:** With Difficulty Check, beating a boss also sends its checks on the lower difficulties you have unlocked.

**Exclude Lunatic:** You can exclude the Lunatic difficulty and therefore start on Hard.

**Resources:** You can set the lives, power packs and difficulty expected for stages 3/4 (Yuugi, Satori) and stages 5/6 (Orin, Utsuho). The requirement ramps up stage by stage. If a gate can't fit in the locations open before its stage, it is lowered and generation logs a warning naming the stage.

**Extra Stage:** exclude, linear (a 7th stage: one more Next Stage, or an Extra Stage item after Stage 6 without Progressive Stage Unlock) or apart (its own Extra Stage item; logic still expects Stage 6 first). Lives and power packs expected for Koishi are set separately.

**Goal:** Utsuho, Koishi or both. Koishi and both need the Extra stage; without it the goal is Utsuho.

**Ending Required:** once (either character), both characters, or all shot types (needs Shot Type Check; otherwise both characters).

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
