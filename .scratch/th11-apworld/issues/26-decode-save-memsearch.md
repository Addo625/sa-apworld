# 26: Decode scoreth11.dat and add /memsearch to locate the practice-unlock data

Status: done
Blocked by: 04

## Problem
The client must grant Practice stages, difficulties and shot types (`Next Stage`, `Lower Difficulty`, shot items), but the practice-unlock bytes weren't found in memory (06: `/dump` covered `.data` and one pointer hop, no hit). The game loads them from its save file. The save format is publicly documented, e.g. ThScoreFileConverter's TH11 support on GitHub: an encrypted, LZSS-compressed file of chunks, where the clear-data chunk holds per-character, per-difficulty story/practice progress. If we decode the file, we know the exact byte pattern to search for in memory.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0, including `test_scoredat_*` and `test_memsearch_*`.
`tools/scoredat.py .games/sa/scoreth11.dat` prints each chunk (signature, size) and, for the clear-data chunks, the practice-progress fields per character and difficulty.

## Test plan
- **`th11/scoredat.py`** (pure, stdlib):
  - `decode(raw) -> bytes`: decrypt, then decompress, following the documented TH11 format. Cite the source (URL and commit) in a comment.
  - `chunks(decoded) -> [(signature, offset, size, body)]`.
  - `practice_progress(chunk) -> {difficulty: value}` for the clear-data chunk, with the field offsets from the docs.
  - Tests:
    - `test_scoredat_chunks_roundtrip`: a synthetic decoded buffer with two chunks parses back.
    - `test_scoredat_decode_real_file`: decodes `.games/sa/scoreth11.dat`, skipped if absent (gitignored). Asserts the header signature and that chunk sizes sum to the decoded length.
- **`/memsearch <hex>`** client command: scans the game's readable committed memory for a byte pattern and logs every match address (cap 50). The scanning helper is pure and takes the reader plus a region list; the region listing (pymem / VirtualQueryEx) lives in `gameController`.
  - `test_memsearch_finds_pattern`: fake reader with two regions and a pattern spanning a page boundary.
  - `test_memsearch_caps_results`.
- **`tools/scoredat.py <file>`** prints the decode. It also prints a ready-to-paste `/memsearch` pattern: the clear-data chunk's bytes around the practice-progress fields (at least 16 bytes, unique within the decoded file).

## Steps
1. Read the format docs, then write the decoder and chunk parser with their tests. Green.
2. Write `/memsearch` and its scanning helper with tests. Green.
3. Write `tools/scoredat.py`, run it on the real save, and paste its output (chunk list, practice progress, suggested pattern) in the ticket comments. Run the DoD.

## Deferred
- Running `/memsearch` in-game → 27. Writing the unlock bytes → 28.
- If the docs don't cover TH11's chunk layout, record what was decoded and set `needs-human` with the open question.

## Comments

**al-work (2026-10-10), done.** Commits: `26: decode scoreth11.dat and print practice progress per character`, `26: search the game's memory for a byte pattern with /memsearch` (+ review fixups). DoD: `cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → 143 passed (incl. `test_scoredat_*`, `test_memsearch_*`). Format source: ThScoreFileConverter @ feb02e2fa390cd0e0c599c97cc12399d9c07fd22 (cited in `th11/scoredat.py`). The sandbox only allowed pytest, so the output below comes from `test_scoredat_tool_prints_real_file` (`pytest -s`), which runs `tools/scoredat.py`'s `main` on `.games/sa/scoreth11.dat`:

```
CR at 0x00018 size 0x68D4
  ReimuYukari (unlocked, cleared, score) per stage:
    Easy    1:1/0/0 2:1/0/0 3:1/1/5284700 4:1/1/16980190 5:1/0/0 6:1/0/0
    Normal  1:1/1/11247610 2:1/0/0 3:1/0/0 4:1/0/0 5:1/0/7458420 6:1/0/0
    Hard    1:1/0/0 2:1/1/13583180 3:1/0/0 4:1/0/0 5:1/0/0 6:1/0/0
    Lunatic 1:1/0/0 2:1/0/0 3:1/0/0 4:1/0/0 5:1/0/0 6:1/0/31160340
CR at 0x068EC size 0x68D4   ReimuSuika      all 24 entries 1/0/0
CR at 0x0D1C0 size 0x68D4   ReimuAya        all 24 entries 1/0/0
CR at 0x13A94 size 0x68D4   MarisaAlice     all 24 entries 1/0/0
CR at 0x1A368 size 0x68D4   MarisaPatchouli all 1/0/0 except Normal 2:1/1/5446940
CR at 0x20C3C size 0x68D4   MarisaNitori    all 24 entries 1/0/0
CR at 0x27510 size 0x68D4   Total           all 24 entries 0/0/0
ST at 0x2DDE4 size 0x448
/memsearch 0000000000010000000000000001000056  (first CR chunk's practice table, 17 bytes, unique in file)
```

(Identical rows are condensed here; the tool prints each one.) Each practice entry is 8 bytes: score/10 u32, cleared u8, unlocked u8, 2 pad. The table sits at CR chunk + 0x5A4, with levels as the outer loop and stages 1–6 as the inner loop.

**Open for 27/28:** in this save, `unlocked` = 1 for every stage, difficulty and shot type, including shot types that were never played. Either the save is fully unlocked, or this byte isn't what gates the Practice menu. 27's M2 ("unlock one more Practice stage") can't produce a change on this save. Possible tests: use a fresh save (move `scoreth11.dat` aside), or watch the `cleared` byte / score instead.
