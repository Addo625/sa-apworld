# 26: Decode scoreth11.dat and add /memsearch to locate the practice-unlock data

Status: ready-for-agent
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
