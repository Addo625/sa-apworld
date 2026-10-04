# Spec: Touhou 11 (Subterranean Animism) Archipelago World

## Problem Statement

No Archipelago (AP) world exists for Touhou 11, Subterranean Animism (SA). SA players, starting with the repo owner, cannot add it to a multiworld. Nepley's MIT-licensed worlds cover Touhou 6, 7, 8 and 10 (copies are in `ref-projects/`, which is gitignored). A web search found no SA world.

## Definition of Done (v1)

1. **Automated (agent):** `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test test/general -q` passes, and `tools/check_apworld.sh` prints `apworld loaded from custom_worlds` and creates an output zip.
2. **Manual (human, Wine):** start the AP server from that output and run the TH11 client in the Wine prefix. Launch `th11.exe` and connect. Clearing Practice Stage 1 with the starting shot type sends `Yamame Defeated`, `Kisume - Midboss` and `Stage 1 Clear` to the server. Server `/send <slot> +1 Life` makes the in-game lives counter go up by 1 within 5 s.

## Solution

Port the structure of the MoF world (`ref-projects/mof-apworld`, the same engine family) and fill it in with EoSD's design (`ref-projects/eosd-apworld`) for items, locations, goals and options, adapted to SA. Keep the MIT notice when porting. Where SA differs, follow SA; the user explicitly wants that freedom.

### Decisions

- **Layout:** the world package is `th11/` (it is installed as `worlds/th11`). The repo root holds tooling, docs, `.scratch/`, and the gitignored `.games/` and `ref-projects/`.
- **Dev AP:** a clone of `ArchipelagoMW/Archipelago` in the gitignored `.ap/`, pinned to the release tag in `tools/AP_VERSION`, with a symlink `.ap/worlds/th11 → ../../th11`. The venv is `.venv/` (Python 3.12) with AP's requirements installed. `archipelago.json` sets `minimum_ap_version` to that tag.
- **Game identity:** `game = "Touhou Chireiden ~ Subterranean Animism"`, short name `Touhou SA`, `STARTING_ID = 110000`.
- **Target exe:** original v1.00a `th11.exe` (sha256 `2978b17f6184d100d249d4311348dd30c5c32ec75c014b667a525b797d3d8813`). The client attaches by process name with `pymem.Pymem("th11.exe")`, as MoF does. This also works under the thcrap English patch, because thcrap still runs `th11.exe`. PowerShell is not used, since it doesn't exist in Wine. The Steam build is out of scope.
- **Runtime:** the game and a Windows Archipelago install both run in the same Wine 9 prefix (`~/.wine`) on macOS. If Kivy won't render, the client falls back to `--nogui`.
- **Client logic boundary:** everything testable (location mapping, boss/clear detection, item application, the bytes guard) lives in modules that never import `pymem` or `kivy`. They receive a memory-reader/writer object. Unit tests run on macOS with a fake reader. Only a thin controller module imports `pymem`.
- **Address table ("data extraction"):** one Variables-style module of offsets for v1.00a. It is seeded from thprac (`touhouworldcup/thprac`, `thprac_th11.cpp`) and the FearLess CE table for v1.00a, and the source of each entry is noted in a comment. The human confirms it in-game with the client's `/probe` command.
- **Code patches:** every code-byte patch site records its expected original bytes, and the client refuses to patch if they differ. A static test checks that no patch site overlaps the binhacks or breakpoints in `.games/sa/thcrap/repos/nmlgc/base_tsa/th11.v1.00a.js`. `Rx` addresses are relative to the image base `0x400000`.
- **Bombs:** SA has no bomb stock, because bombs spend power. EoSD's "+1 Bomb" items and bomb gates are replaced by "+0.50 Power" packs, which are progression items. Gates are lives + power + difficulty.
- **Continues:** design A, as in MoF: continues are unlimited, and continuing restores your item-earned lives (`setNormalContinueLives`). Designs B, C and D are deferred tickets.

### Content (settled from `thcrap/repos/thpatch/lang_en/th11/spells.js`)

| Stage | Midboss location | Boss location |
|---|---|---|
| 1 | Kisume - Midboss | Yamame Defeated |
| 2 | Parsee - Midboss | Parsee Defeated |
| 3 | Yuugi - Midboss | Yuugi Defeated |
| 4 | none: the midboss has no spell card and leaves on a timer | Satori Defeated |
| 5 | Cat Orin - Midboss | Orin Defeated |
| 6 | Orin - Midboss | Utsuho Defeated |
| Extra | Sanae - Midboss | Koishi Defeated |

Each stage also has a `Stage N Clear` location (`Stage Extra Clear` for Extra). Location names follow EoSD's scheme: `[<Character or Shot>] <check>`, and `[<Difficulty>][<Character or Shot>] <check>` when difficulty checks are on.

**Shot types** (item names): `Reimu A - Yukari`, `Reimu B - Suika`, `Reimu C - Aya`, `Marisa A - Alice`, `Marisa B - Patchouli`, `Marisa C - Nitori`. One random shot type is precollected.

### Items (full design; v1 builds only the core subset)

- **Core:** shot types, `Next Stage` (global, progressive), `+1 Life`, `+0.50 Power`, `Lower Difficulty` ×3, locked `[<Character>] Ending - Utsuho` items on the Stage 6 clears, and filler `+0.05 Power`.
- **Deferred:**
  - Next Stage by character or by shot type.
  - Extra Stage items.
  - `[<Character>] Ending - Koishi`.
  - Traps: `-50% Power`, `-1 Life`, `No Focus`, `Reverse Movement`, `Aya Speed`, `Freeze`, `Power Drain`. EoSD's Max Rank and -1 Bomb are dropped because SA has no rank and no bomb stock.
  - `+1 Continue`, only with continues design B.

### Options (full design: EoSD parity)

- **Core (v1):**
  - `exclude_lunatic`.
  - Gates: `number_life_mid`, `power_mid`, `difficulty_mid` for stages 3/4, and `_end` for stages 5/6.
  - `death_link` is present but off, from `PerGameCommonOptions`; it does nothing until ticket 14.
- **Deferred:**
  - `mode` (normal dynamic/static) and `stage_unlock` (by character, by shot type).
  - `extra_stage` (linear, apart) with Extra gates.
  - `shot_type`, `difficulty_check`, `check_multiple_difficulty`.
  - `goal` (koishi, both) and `ending_required`.
  - `death_link_trigger`, `death_link_amnesty`, `ring_link`, `limit_lives`.
  - `traps` and per-trap weights.

Filler count is always computed as locations minus placed items. It is never hand-tuned.

## Risk tree

- **R1. Wrong or unverified addresses.** The agent can't run the game.
  - DoD: the human runs `/probe` in every state listed in ticket 06 and the output matches expectations.
  - Solution: a probe command (04), a human probe run (06), then fixes (07).
- **R2. Attaching under Wine.**
  - DoD: `/probe` attaches to `th11.exe` running under Wine, both vanilla and thcrap.
  - Solution: attach by name. `/launch` is only a convenience.
- **R3. Midboss detection.**
  - Stage 4's midboss is undetectable, so it gets no location (settled).
  - Negative case: when the boss flag clears because of a menu exit, retry, or a game over, no location is sent. This is unit-tested.
- **R4. Fill failures.**
  - DoD: tests run `WorldTestBase` (including `test_fill`) and AP's `test/general` on the extreme option combinations: fewest locations against maximum gates, per goal.
  - Solution: compute filler instead of hand-tuning counts.
- **R5. score.dat or exe-memory damage.**
  - DoD: a unit test checks that every write address is in the table, and the bytes guard is tested. The README tells the user to back up `score.dat`.
- **R6. AP version drift.**
  - DoD: `.ap` is checked out at the tag in `tools/AP_VERSION`, and the Wine AP install is at least that version.
- **R7. Windows AP missing in Wine.**
  - Solution: human ticket 05.

## Testing Decisions

- Test only external behavior.
  - Generation: seeds generate and are beatable; location and item names and IDs are unique; gates block what they should, using `WorldTestBase` helpers (`collect_by_name`, `can_reach_location`).
  - Client: given fake memory states, the logic emits the right location IDs and writes the right bytes.
- Prior art: AP's own `worlds/*/test` suites built on `test.bases.WorldTestBase`. Nepley's worlds have no tests.
- The highest seam for generation is AP's `WorldTestBase`. For the client, it is the reader-injected logic module.

## Out of Scope

- The Steam release of SA, which is a different exe with different addresses.
- Publishing to GitHub or the AP index. The human pushes when they choose.
- A content-extraction script for th11.dat. There are about 15 names, and they are written by hand from `spells.js`.

## Tickets

Ticket files are in `issues/`. Tickets 01–09 make up v1. Tickets 10–20 are `deferred` and fully specified.
