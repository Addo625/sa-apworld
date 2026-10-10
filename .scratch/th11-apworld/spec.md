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
| 4 | Cat Orin appears twice and leaves on a timer each time: `Cat Orin - First Appearance`, `Cat Orin - Second Appearance` (human decision 2026-10-10, ticket 25) | Satori Defeated |
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
- Toning down capture difficulty beyond `captures_per_stage`. The user will plan it separately.
- Extra-stage capture slots: IDs are reserved in 21, and the slots are built with 11.
- Smaller power packs (0.25, 0.20), which the user dropped.
- A content-extraction script for th11.dat. There are about 15 names, and they are written by hand from `spells.js`.

## Gates and Spell Card Keys (planned 2026-10-07)

### Problem
- Max gate settings make solo seeds unfillable. This was measured in 02's comment: AP's fill reports "No more spots to place 25 items", and in a multiworld that stops every player's generation.
- The core seed has only 34 locations, so gates can't grow, and the game's main skill reward, spell captures, isn't part of the randomizer.

### DoD
- 02: `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_extremes_fill_fixed_seeds`, which runs over a fixed seed list with these option sets:
  - max gates;
  - max gates + `exclude_lunatic`;
  - max gates + excluded stage 1–2 checks;
  - defaults.
- 21: the same command, including the spell-card option sets.
- 24 (with the human probe 23): capturing a card in practice sends the next `Stage N - Capture k` check.

### Solution
1. **Per-stage gates (02).** A pure function `stage_requirements(mid, end, keys_required, rooms) -> (requirements, notes)`.
   - `mid` and `end` are `(lives, power, difficulty)` tuples, with difficulty already adjusted for `exclude_lunatic`.
   - Each resource ramps: stages 1–2 → 0, stage 3 → floor(mid/2), stage 4 → mid, stage 5 → floor((mid+end)/2), stage 6 → end.
   - Keys: stages 1–2 → 0, stage k ≥ 3 → floor(R·(k−2)/4).
2. **Fit check and clamp (02).**
   - Room for stage k = this world's created locations in stages < k, minus `exclude_locations`, minus (k−1) `Next Stage`, minus 1 for the other character's shot, minus `GATE_SLACK` (3; raised from 2 in 25, when stage 4's two cat-Orin checks unclamped the max gates and seeds 8 and 15 failed), plus 1 per 10 required keys (21: a flat slack of 2–5 failed 50-key seeds, and raising it would cut no-key gates).
   - While a stage's total exceeds its room, take one off the largest of lives, power and keys. Difficulty is cut only once those are 0.
   - Each cut is logged as a warning, and `slot_data.stage_requirements` holds the clamped values.
3. **Spell Card Keys (21, world side).** Capture-slot locations and a `Spell Card Key` item, with IDs appended to the tables. It defaults to `off` until the client sends captures.
4. **Client side (22–24).** Capture address candidates, the human in-game probe, detection, and then the default flips to `alongside`.

### Decisions
- Power packs stay `+0.50 Power`. The user dropped the smaller-pack idea.
- `spell_card_keys`: `off` / `alongside` / `keys_only`, with `alongside` as the target default.
  - In `keys_only`, gates use keys only and lives, power and difficulty become `useful`.
  - `keys_only` with zero keys warns and acts as `alongside`.
- Capture locations are numbered slots, `[<Character>] Stage N - Capture k` (shared: `Stage N - Capture k`). Slot k is checked by the k-th *different* card captured in that stage with that character, across runs and on any difficulty.
- `captures_per_stage`: 0–6, default 2. Each stage is capped at the fewest cards any difficulty offers, 2/4/4/4/5/6. Stage 1 is small because Kisume's card is Hard/Lunatic only. The difficulty assignment comes from memory plus spells.js's ID grouping, and 23 verifies it.
- `capture_slots`: `per_character` (default) or `shared` (character-agnostic).
- `spell_card_keys_in_pool`: the % of capture locations that hold a key (default 50).
- `spell_card_keys_required`: the % of the pool needed by stage 6 (default 75).
- Settings that don't fit: always clamp and warn, never `OptionError` or smaller ranges.
  - In a multiworld, room counts only this world's locations, so a gate may be cut that would have filled. This trade-off is accepted.

### Risk tree
- **K1. Default-on before the client can send captures** → unbeatable default seeds. 21 asserts the default is `off`, and 24 flips it with its client tests.
- **K2. The card-per-difficulty table is from memory.** 23 counts the cards per stage on Easy and Lunatic, and 24 fixes the caps if they differ.
- **K3. Tight fills.** `test_extremes_fill_fixed_seeds` uses fixed seeds. `GATE_SLACK` is raised until it's green, and the final value is recorded.
- **K4. Capture detection needs to know which card was captured.** 22 sources the current-spell-ID and capture entries. 24 unit-tests that only different cards count, and that a replay sends nothing twice.
- **K5. Shared slots with per-character unlocks.** 21 tests that a shared slot opens from either character.
- **K6. The room formula assumes global unlock and no gated locations.** Ticket 10's test plan computes room per `stage_unlock` mode.
- **K7. `test/general` needs other worlds' requirements:** soe, zillion (installed via git+https), and pokemon_emerald, which has no requirements.txt, so its load error has to be found. This is a human Do-now item, not part of 02.

## Tickets

Ticket files are in `issues/`. Tickets 01–09 make up v1. Tickets 10–24 are `deferred` and fully specified (21–24: Spell Card Keys). Added 2026-10-10: 25 (two stage 4 cat-Orin checks), 26–28 (practice-unlock data: decode the save, `/memsearch` in-game, write the unlocks). 21 and 22 promoted to `ready-for-agent`. 2026-10-10 after 09: 10–16 promoted (17 is `ready-for-human`); 29 (item feedback), 30 (Demo Play sends checks, low priority) added; 28 also locks unreceived shots.
