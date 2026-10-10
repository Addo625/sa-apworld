# 07: Correct the TH11 address table from the probe results

Status: ready-for-agent
Blocked by: 06

## Problem
Ticket 06 recorded real memory values for each state. Wherever the table disagrees with what the game showed, the table is wrong, and detection and item writes (08) would fail silently.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_probe_fixtures_*` (one per captured state in 06) and `test_every_write_address_in_table`.
`grep -c "TODO(06)" th11/Variables.py` → 0, or each remaining one is listed under Deferred with "not reached in 06".

## Test plan
- **Fixtures:** each `/probe` capture from 06 becomes a fixture (state name → `{entry: value}`).
- **Tests for each fixture:** the decoders return what the human saw:
  - `decode_state(fixture)` → stage, difficulty, character, shot, lives, power, in_game/menu.
  - **Boss signal:** not in the probe fixtures (it was unsourced then). Set `ADDR_IS_BOSS_PRESENT = [0x000A8D7C, 0x1C]` from 06's boss-signal notes (found by `/bossrec`, confirmed by `/bosswatch` on stages 1, 2, 5, 6; the spike code is on branch `spike/boss-scan` for reference). Test `boss_present` with a fake reader where the enemy manager is 0 (stage loading → False), set with +0x1C ≠ 0 (True) and +0x1C = 0 (False).
  - **In-play signal:** `0x4A8ECC` is the menu object pointer, not a game mode (06, S0–S2). Rename it (e.g. `ADDR_MENU_PTR`). "In a stage" = enemy manager pointer `0x4A8D7C` ≠ 0 (06, S8b shows the menu pointer can be 0 outside play). `decode_state` returns that.
  - **Power:** units of 0.05, max 80 (06, S12). Fixtures and comments use that.
  - **Practice unlock, Extra unlock, starting lives:** still unsourced. Keep them `None`, listed under Deferred → 26–28 (practice unlock) and 11/12.
- **`test_every_write_address_in_table`:** every address passed to a writer anywhere in the client package is a `Variables` entry. Check this by introspecting the controller's writer calls with a recording fake.
- **`test_patch_sites_*`** from 04 still pass with the corrected `EXPECTED_BYTES`. A thcrap overlap would be a real conflict: say so in the ticket and don't paper over it.

## Steps
1. Turn the 06 captures into fixtures plus the decoder tests (red where the table is wrong).
2. Fix `Variables.py` entries until the fixture tests pass. Update the `# source:` comments to `probe 06 Sx`.
3. Add the write-address test. Run the DoD.

## Deferred
- Entries not reached in 06 stay unverified and are listed here, with the ticket that first needs each one (11: Extra, 12: menus/continues).
