# 28: Received Next Stage, Lower Difficulty and shot types unlock Practice

Status: ready-for-agent
Blocked by: 08, 27

## Problem
08 tracks these items but can't apply them: the practice-unlock data was unknown. 26 decoded its layout and 27 found it in memory. This ticket writes it.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **Find the live copy first (27 left this open):** 27 found two heap copies of the practice table, which move every launch: copy 1 at page offset `…215C` (likely the live save struct, table = struct + 0x5A4) and copy 2 at `…05C4` (likely the decoded file buffer).
  - Add `/ptrscan <hex address> [range]`: lists every 4-byte word in `.data` (`0x4A2000–0x4CAE40`) whose value points into `[address − range, address]` (default range 0x1000), with its offset from the target. It's pure over the reader, like `memsearch`. `test_ptrscan_finds_static_pointer`.
  - Then set `needs-human` with these steps for the human:
    1. Start the game and open the Practice menu.
    2. `/memsearch 00000000010100000000000001010000` (or the current save's line from `tools/scoredat.py`).
    3. `/ptrscan <each match − 0x30>`.
    4. Write test (picks the live copy): with the client, flip copy 1's Normal Stage 3 `unlocked` byte and check whether Practice offers Stage 3. Needs a one-off `/poke <addr> <byte>` debug command; add it next to `/ptrscan`.
- **`Variables.py`:** `ADDR_PRACTICE_UNLOCK` = the static pointer chain to the live table, from the human's `/ptrscan` output. Source comment `probe 28`.
- **`items.apply`:**
  - `Next Stage` → the practice-progress fields for every unlocked shot type at every unlocked difficulty, stages ≤ count + 1.
  - `Lower Difficulty` → the unlocked difficulties.
  - Shot type → that shot's rows.
  - **From 10:** the per-group stage items (`[<Char>] Next Stage`, `[<Shot>] Next Stage`, `Stage N`, `[<X>] Stage N`) write their group's rows. 10 logs them as pending unlocks; replace that path.
  - Tests: `test_apply_next_stage_writes_unlock_rows`, `test_apply_lower_difficulty`, `test_apply_shot_type`, and the replay test from 08 extended to these items.
- **Pending replay:** items received before this ticket (tracked by 08) are applied on connect.
- **Lock what isn't received** (09 finding: a fully unlocked save let Reimu B send checks without owning it): on attach and on connect, write the practice table so only received shot types × unlocked difficulties × stages ≤ `Next Stage` + 1 are open, as EoSD rewrites practice access. Restoring the player's own save is the README's job (back up `scoreth11.dat`). `test_lock_unreceived_shots_on_connect`.

## Steps
1. Add the address, with a fixture from 27's output. Green.
2. Write the item rules and tests, and remove 08's "pending unlock table" path. Run the DoD.

## Deferred
- In-game proof: ticket 09's smoke run covers it.
