# 04: TH11 client attaches to the game and prints a memory probe

Status: ready-for-agent
Blocked by: 01

## Problem
The agent can't run the game, so the TH11 address table (the "data extraction" the user asked for) must ship with a way for the human to check it: a `/probe` client command. The command also has to work with no Windows Python in Wine, which is why it lives inside the AP client. See `../spec.md`: Target exe, Client logic boundary, Address table, Code patches.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_probe_*`, `test_patch_sites_*` and `test_client_modules_import_without_pymem`.
`grep -c "source:" th11/Variables.py` ≥ the number of `ADDR_` entries: every address cites thprac, FearLess or MoF-analogue.

## Test plan
- **`Variables.py`** (v1.00a): one entry per value the client needs, as a static offset or a pointer chain `[base, off, ...]`, MoF style. Required entries:
  - Game mode/state, menu, menu cursor.
  - Stage, difficulty, character, shot type.
  - Lives, life pieces, power, score, continues used.
  - Boss-present flag(s).
  - Practice-unlock table (character × shot × difficulty × stage).
  - Extra unlock.
  - Practice/continue starting-lives code sites. These are code patches and carry `EXPECTED_BYTES`.
- **`probe.format_probe(reader, table)`** (pure):
  - In: a fake reader returning fixed bytes. Out: one line per entry, `NAME = value (addr 0x…)`, in table order.
  - A read error on an entry prints `NAME = <unreadable>` and doesn't abort the probe.
  - Tests: `test_probe_formats_all_entries`, `test_probe_survives_read_error`.
- **`patching.safe_patch(reader_writer, addr, expected, new)`** (pure): writes only if the current bytes equal `expected`; otherwise it raises `PatchMismatch` and writes nothing.
  - Tests: `test_patch_sites_refuse_on_mismatch`, `test_patch_sites_write_on_match`.
- **`test_patch_sites_dont_overlap_thcrap`:** parses `.games/sa/thcrap/repos/nmlgc/base_tsa/th11.v1.00a.js`, resolves `Rx` addresses relative to `0x400000` and absolute `0x` addresses, gives each a length (`code` bytes length, else 1 for breakpoints, using `cavesize` when present), and asserts that no `EXPECTED_BYTES` range intersects them. The test is skipped if `.games/` is absent, since it's gitignored.
- **`test_client_modules_import_without_pymem`:** imports the logic modules with `pymem` and `kivy` blocked in `sys.modules`.
- **Client** (manual, ticket 06):
  - The launcher shows a "Touhou SA Client" component.
  - `/probe` attaches with `pymem.Pymem("th11.exe")` and prints `format_probe`.
  - `/launch` starts the exe from the `game_exe` settings path, as EoSD does.

## Steps
1. Build the address table from thprac (`thprac_th11.cpp` on GitHub) and the FearLess v1.00a table (https://fearlessrevolution.com/viewtopic.php?t=6088), cross-checking against MoF's layout. Mark each entry `# source: …`. Entries you can't source get `None` and a `# TODO(06)` note.
2. Write `probe.py` and `patching.py` (pure) with their tests, plus the thcrap overlap test and the import-isolation test.
3. Write a thin `gameController.py` (the only module importing pymem; `Pymem("th11.exe")`, `read_bytes`/`write_bytes`) and a minimal `Client.py` (CommonClient context, `/probe`, `/launch`; no game loop yet). Register the launcher component in `__init__.py`, following the EoSD and MoF pattern.

## Deferred
- Location detection and item application → 08.
- Address corrections → 07.
