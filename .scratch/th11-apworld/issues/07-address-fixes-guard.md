# 07: Correct the TH11 address table from the probe results

Status: done
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
- Still `None` with `TODO(06)`, not reached in 06:
  - `ADDR_PRACTICE_UNLOCK`: not reached in 06 → 26–28.
  - `ADDR_EXTRA_UNLOCK`: not reached in 06 → 11.
  - `ADDR_PRACTICE_STARTING_LIVES`: not reached in 06 → 12 (08's `+1 Life` starting lives).
  - `ADDR_NORMAL_CONTINUE_LIVES`: not reached in 06 → 12.
- `ADDR_CONTINUES` reads 0 in every 06 probe because no continue was used. Its thprac source is unverified → 12.

## Comments

- 2026-10-10 al-work: done.
  - **Table:** `ADDR_GAME_MODE` is renamed `ADDR_MENU_PTR`. New entry `ADDR_ENEMY_MANAGER` (0x4A8D7C). `ADDR_IS_BOSS_PRESENT = [ADDR_ENEMY_MANAGER, 0x1C]`, and the menu chains build on `ADDR_MENU_PTR`. Source comments now read `probe 06 Sx`. No address changed: every sourced 04 address matched the captures. The problem was what the entries meant (game mode → menu ptr, the practice bit is 0x10, power is in 0.05 units).
  - **Decoders:** `th11/state.py`. `decode_state(values)` and `read_state(reader)` return a `GameState`: `in_game`, `boss_present`, `menu`, `menu_cursor`, `stage`, `difficulty`, `character`, `shot`, `lives`, `power` (`None` when unreadable).
  - **Writes:** `probe.write_int(writer, entry, value)` raises `ValueError` for anything that isn't a sourced table entry.
  - **Tests:** `test/test_state.py` has one `test_probe_fixtures_*` per 06 state (S0–S11b) and the three `boss_present` cases. `test_every_write_address_in_table` is an AST check: no raw `write_bytes` outside the writers, and `safe_patch` only on `EXPECTED_BYTES` entries. Its `_recorded` variant is a recording fake: every sourced entry writes at its resolved address, and raw addresses raise.
  - **thcrap:** `EXPECTED_BYTES` is still empty, so there is no overlap to check. `test_patch_sites_*` pass.
  - **Fixture caveat:** `ADDR_ENEMY_MANAGER` was only probed in S8b (0). The fixtures infer non-zero in a stage and 0 on menus. At game over (S10) it is unknown, so that fixture doesn't assert `in_game`. 08 should detect game over by `lives == -1`.
  - **DoD:** pytest → 70 passed. `grep -c "TODO(06)" th11/Variables.py` → 4, all listed above.
