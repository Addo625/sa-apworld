# 22: Add spell capture address candidates to the probe

Status: done
Blocked by: 07

## Problem
The client must notice when a spell card is captured and know which card it was (ticket 21's slots count *different* cards). No capture-related address exists in `Variables.py` yet. The human probe (23) can only verify entries that already exist, so this ticket adds sourced candidates first, like 04 did for the core table.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_capture_entries_present` and `test_probe_lists_capture_entries`.
`grep -n "TODO(23)" th11/Variables.py` lists every new entry that has no second source.

## Test plan
- **`Variables.py`** gains, MoF style (static offset or pointer chain), each with `# source: …`:
  - the current spell card ID (or −1 when none is active);
  - a capture-success signal: the spell bonus flag or bonus value, or the card's capture count changing;
  - the live spell history (captures and attempts per card per shot type), if it's in memory.
  - `test_capture_entries_present`: the entry names exist and are `ADDR_`-prefixed. `None` with `# TODO(23)` is allowed when they can't be sourced.
- **`probe.format_probe`** lists the new entries. `test_probe_lists_capture_entries` uses a fake reader.

## Steps
1. Source the entries from thprac (`thprac_th11.cpp` on GitHub: spell practice and spell history code) and the FearLess v1.00a CE table, cross-checking the spells.js ID ranges (0–174). Mark sources, and add `TODO(23)` where only one source exists.
2. Add the tests. Run the DoD.

## Deferred
- In-game verification → 23.

## Comments

- 2026-10-10 planner: promoted. A lead from 06's dumps: the heap struct behind static `0x4C343C` (`0x14AF998` in that session) has paired u32 counters at a 0x20 stride from `+0x6E8` that rose during play. Likely the spell history (attempts/captures). Check it against thprac's spell data before using it.
- 2026-10-10 al-work: done. Added `ADDR_SPELL_ID` and `ADDR_SPELL_BONUS` as `None`, plus `ADDR_SPELL_HISTORY = [0xC343C, 0x6E8]` (the 06 lead). All three are `TODO(23)`. thprac_th11.cpp has no spell ID, bonus or history code because its spell practice patches ECL. The FearLess page, web search, `gh` and disassembling th11.exe all needed approval this run didn't have, so the 06 lead is the only source. DoD: pytest 131 passed; `grep TODO(23)` lists all 3.
