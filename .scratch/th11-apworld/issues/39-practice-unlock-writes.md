# 39: Received Next Stage, Lower Difficulty and shot types unlock Practice

Status: done
Blocked by: 32

## Problem
08 tracks these items but can't apply them: the practice-unlock data's live address is unknown. 26 decoded its layout, 27 found two heap copies, 28 added `/ptrscan` and asked probe batch 32 (R7) which copy the game reads and what points to it. This ticket writes it.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including the tests below.

## Test plan
- **Read 32's R7 comments first:**
  - U4 names the copy the Practice menu reads; U2 lists the static pointers into it (`base + X -> value`, `target - d`).
  - U3 confirms the per-shot stride (`0x68D4` = `scoredat.CLEAR_SIZE` if both peeks start with `CR` and shot 00/01).
  - If U2 shows no static pointer to the live copy (only a heap one, needing a second level), that's a new R in the next probe batch: `/ptrscan` on the heap pointer's address. Don't guess: per AGENTS.md, build the item rules against a fake reader with the entry left `None`, add the request, open a follow-up for the address, and close 39.
- **`Variables.py`:** `ADDR_PRACTICE_UNLOCK = [X, d']` with `d'` = table − value, the pointer chain to shot 0's practice table (the table is chunk + `scoredat.PRACTICE_OFFSET`). Source comment `probe 32 R7`. Add it to `PROBE_TABLE`, so `write_entry` accepts it. Shot `s`, level `l`, stage `n` `unlocked` byte = table + `s * 0x68D4 + (l * 6 + n − 1) * 8 + 5`. Since `write_entry` only takes table entries, either add a pure `practice_writes(...) -> [(offset, value)]` written through one helper that resolves `ADDR_PRACTICE_UNLOCK` once, or write the whole 4 × 6 × 8-byte table per shot. Pick the smaller one.
- **`receive.py`:**
  - `Next Stage` → the `unlocked` byte for every received shot type at every unlocked difficulty, stages ≤ count + 1.
  - `Lower Difficulty` → the unlocked difficulties (`Variables.lowest_unlocked`).
  - Shot type → that shot's rows.
  - **From 10:** the per-group stage items (`[<Char>] Next Stage`, `[<Shot>] Next Stage`, `Stage N`, `[<X>] Stage N`) write their group's rows.
  - Remove those names from `PENDING_UNLOCK` (Extra items stay pending for 33).
  - Tests: `test_apply_next_stage_writes_unlock_rows`, `test_apply_lower_difficulty`, `test_apply_shot_type`, and the replay test from 08 extended to these items.
- **Pending replay:** items received before this ticket (tracked by 08) are applied on connect. The table is a full function of the received list, so recompute it from all items rather than diffing.
- **Lock what isn't received** (09 finding: a fully unlocked save let Reimu B send checks without owning it): on attach and on connect, write the practice table so only received shot types × unlocked difficulties × stages ≤ `Next Stage` + 1 are open, as EoSD rewrites practice access. Unlike the life and power items, unlock writes don't need a run (the menu reads them). Restoring the player's own save is the README's job (back up `scoreth11.dat`). `test_lock_unreceived_shots_on_connect`.

## Steps
1. Add the address from R7, with a fake-memory fixture laid out like R7's output. Green.
2. Write the item rules and tests, and remove 08's "pending unlock" path for these items. Run the DoD.

## Deferred
- In-game proof: ticket 09's smoke run covers it.
- `cleared` bytes and scores are left alone; only `unlocked` gates Practice (27 finding).

- 2026-10-12 planner, **from batch 32 R7:**
  - `ADDR_PRACTICE_UNLOCK = [0x4A8EBC, 0x5AC]`: static `0x4A8EBC` points to the live save struct; `+0x5AC` is Reimu A (Yukari)'s practice table.
  - Entries are 8 bytes: score/10 u32, `cleared` u8, `unlocked` u8, 2 pad. Levels Easy..Lunatic outer, stages 1–6 inner, so Normal Stage 3's `unlocked` is at table + `0x45`.
  - Per-shot stride `0x68D4` (save format, `th11/scoredat.py`; order Yukari, Suika, Aya, Alice, Patchouli, Nitori).
  - Proof: poking copy 1's Normal Stage 3 `unlocked` to 1 offered Stage 3 in the Practice menu live, and 0 locked it again. The other heap copy (the file buffer) has no effect.
  - The `0x4C38AC` pointer from U2 points to an unaligned address near copy 2; ignore it.

## Comments

- 2026-10-12 al-work: done. `receive.practice_open`, `receive.practice_unlock` and `Client.unlock_practice` rewrite each shot's `unlocked` bytes every tick from the full received list. Scores and `cleared` bytes are kept, and nothing is written before ReceivedItems arrives or while the save pointer is null. `write_entry` now takes an offset for the other shots' tables. Normal mode opens all six stages of a received shot, matching `stage_unlocked(normal=True)`. DoD: 379 passed. No deferred tickets; in-game proof rides on the next smoke run.
