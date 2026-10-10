# 06: [human] Run /probe in every game state and record the output

Status: done
Blocked by: 05

## Problem
Ticket 04's address table is sourced but unverified, and only someone playing can put the game into each state. Back up the save first: `scoreth11.dat` in the game folder.

## DoD
`## Comments` holds one fenced `/probe` output per state below. Each is labeled with the state and with what the screen showed for lives, power, stage, difficulty, character and shot.

## Test plan
Capture `/probe` in each state. Launch `th11.exe` itself, without thcrap, unless noted. Write what you see next to each one.
- **S0:** title menu.
- **S1:** difficulty select, cursor on Normal. **S1b:** cursor on Lunatic.
- **S2:** character/shot select on Marisa B.
- **S3:** Practice Stage 1, Normal, Reimu A, before the midboss.
- **S4:** Kisume (midboss) on screen.
- **S5:** after the midboss leaves.
- **S6:** Yamame (boss) on screen.
- **S7:** stage-clear tally.
- **S8 (do this last, on a fresh save):** this state finds the practice-unlock bytes. On a fresh save, Practice stages are locked and unlock only through **normal play**: a stage becomes available in Practice once you reach it in a normal game. Clearing a Practice stage unlocks nothing.
  1. `mv scoreth11.dat scoreth11.dat.cheated` (keep any modified save aside).
  2. **S8a:** open the Practice menu and `/probe`. Nothing should be offered.
  3. Start a normal game (not Practice), clear Stage 1 or at least reach Stage 2, then quit to the menu.
  4. **S8b:** open the Practice menu again and `/probe`. Note which stages are offered.
  5. Whatever differs between S8a and S8b points at the unlock bytes. Restore the old save afterwards if you want it.
- **S9:** quit to the menu during the boss (the negative case).
- **S10:** a game over screen.
- **S11:** a life lost (lives −1), and after collecting a life piece.
- **S12:** after bombing (power drop).
- **For stages 2–6 and Extra:** boss-present flag(s) with the midboss up and with the boss up. Reach those stages by playing through, or with thprac (it runs under Wine), or, once 07/08 land, through practice unlocks written by the client.
- **S13 (moved to 17, 2026-10-10):** one `/probe` through thcrap at S3, to confirm attach-by-name and the addresses under the English patch. The human can't run it for a while; ticket 17 already covers the full thcrap check.

## Steps
1. Back up `scoreth11.dat`.
2. Go through S0–S13 and paste each output under `## Comments`.
3. For any stage you can't reach, write "not reached". Ticket 07 then carries those entries as unverified. Set `Status: done`.

## Deferred
- A full in-game check of stages 2–6 and Extra under thcrap → 17.

## Comments

- 2026-10-09 human (via Claude). **Setup:** macOS, Wine 11.0 (Gcenx build) in its own prefix (`~/archipelago/wineprefix`), Windows AP 0.6.7 in `~/archipelago/install-wine`, client started with `ArchipelagoLauncher.exe "Touhou SA Client"`, plain `th11.exe` (v1.00a). `/probe` attaches under Wine (R2 ok). In-game music doesn't play under Wine; that doesn't matter for probing.
  - **S0, title menu.** Screen: title menu (no run active).
    ```
    ADDR_GAME_MODE = 52159048 (addr 0x004A8ECC)
    ADDR_MENU = 0 (addr 0x031BE2F8)
    ADDR_MENU_CURSOR = 0 (addr 0x031BE26C)
    ADDR_GAME_FLAGS = 0 (addr 0x004A5758)
    ADDR_STAGE = 0 (addr 0x004A5728)
    ADDR_DIFFICULTY = 1 (addr 0x004A5720)
    ADDR_CHARACTER = 0 (addr 0x004A5710)
    ADDR_SHOT_TYPE = 0 (addr 0x004A5714)
    ADDR_IS_BOSS_PRESENT = <unsourced>
    ADDR_LIVES = 0 (addr 0x004A5718)
    ADDR_LIFE_PIECES = 0 (addr 0x004A571C)
    ADDR_POWER = 0 (addr 0x004A56E8)
    ADDR_SCORE = 0 (addr 0x004A56E4)
    ADDR_CONTINUES = 0 (addr 0x004A573C)
    ADDR_PRACTICE_UNLOCK = <unsourced>
    ADDR_EXTRA_UNLOCK = <unsourced>
    ADDR_PRACTICE_STARTING_LIVES = <unsourced>
    ADDR_NORMAL_CONTINUE_LIVES = <unsourced>
    ```
    Note for 07: `ADDR_GAME_MODE` = 0x031BE248 looks like a pointer into the same heap block as `ADDR_MENU`/`ADDR_MENU_CURSOR` (0x031BE2xx), not a mode number. Compare it across states.
  - **S1, difficulty select, cursor on Normal.** Differences from S0: `ADDR_GAME_MODE = 62416248` (0x03B86578), `ADDR_MENU = 1 (addr 0x03B86628)`, `ADDR_MENU_CURSOR = 1 (addr 0x03B8659C)`, `ADDR_STAGE = 3`, `ADDR_SHOT_TYPE = 1`, `ADDR_LIVES = 9`, `ADDR_POWER = 80`, `ADDR_SCORE = 620`. The rest are unchanged (`ADDR_DIFFICULTY = 1`, `ADDR_CHARACTER = 0`, `ADDR_GAME_FLAGS = 0`, `ADDR_CONTINUES = 0`, `ADDR_LIFE_PIECES = 0`, the same 5 unsourced).
  - **S1b, difficulty select, cursor on Lunatic.** Same as S1 except `ADDR_MENU_CURSOR = 3`.
  - **Analysis (for 07):**
    - `0x004A8ECC` is the menu object pointer, not a game mode. In S0 and S1, `ADDR_MENU` = value + 0xB0 and `ADDR_MENU_CURSOR` = value + 0x24. Rename it (e.g. `ADDR_MENU_PTR`) and find a real state indicator from the in-game probes.
    - Cursor: Normal = 1, Lunatic = 3 (Easy 0 … Lunatic 3). `ADDR_DIFFICULTY` only changes on confirm.
    - The stage/lives/power/score values before a run are probably left over from the title demo or an earlier game; S3+ will confirm the addresses.
  - **S2, character select, cursor on Marisa B.** `ADDR_GAME_MODE = 58160792` (0x03777698), `ADDR_MENU = 3 (addr 0x03777748)`, `ADDR_MENU_CURSOR = 1 (addr 0x037776BC)`, `ADDR_GAME_FLAGS = 4`, `ADDR_STAGE = 3`, `ADDR_DIFFICULTY = 1`, `ADDR_CHARACTER = 1`, `ADDR_SHOT_TYPE = 1`, `ADDR_LIVES = 9`, `ADDR_LIFE_PIECES = 0`, `ADDR_POWER = 62`, `ADDR_SCORE = 1134416`, `ADDR_CONTINUES = 0`, the same 5 unsourced.
  - **S3, Practice Stage 1, Normal, Reimu A, before Kisume.** `ADDR_GAME_MODE = 0`, `ADDR_MENU`/`ADDR_MENU_CURSOR = <unreadable>`, `ADDR_GAME_FLAGS = 16`, `ADDR_STAGE = 1`, `ADDR_DIFFICULTY = 1`, `ADDR_CHARACTER = 0`, `ADDR_SHOT_TYPE = 0`, `ADDR_LIVES = 9`, `ADDR_LIFE_PIECES = 0`, `ADDR_POWER = 0`, `ADDR_SCORE = 0`, `ADDR_CONTINUES = 0`.
  - **S4, Kisume (midboss) on screen.** As S3 except `ADDR_POWER = 33`, `ADDR_SCORE = 97475`.
  - **S6, Yamame (boss) on screen.** As S3 except `ADDR_LIVES = 6`, `ADDR_LIFE_PIECES = 2`, `ADDR_POWER = 0`, `ADDR_SCORE = 151531`.
  - **S7, stage-clear tally.** As S3 except `ADDR_LIVES = 6`, `ADDR_LIFE_PIECES = 0`, `ADDR_POWER = 14`, `ADDR_SCORE = 1124761`.
  - **S8:** pending. The human used an unlock-everything cheat, so this save shows every practice stage. S8 was rewritten (Test plan) to run last on a fresh save, since practice stages unlock through normal play, not by clearing Practice stages. The other states don't depend on unlock state, so they continue on the current save. The save file is `.games/sa/scoreth11.dat`, not `score.dat`.
  - **Analysis (for 07):**
    - `0x004A8ECC` (menu pointer) is non-zero in menus and 0 in play, so it can serve as an "in game" signal (S3–S7). The menu offsets +0xB0 and +0x24 hold in S2 too.
    - `ADDR_GAME_FLAGS`: 0 on title and difficulty select, 4 on character select, 16 in Practice play. Possibly bit flags; check them in normal (non-practice) play.
    - `ADDR_STAGE`, `ADDR_DIFFICULTY`, `ADDR_CHARACTER` and `ADDR_SHOT_TYPE` match the selection in S2–S7 (Marisa = 1, B = 1; Reimu A = 0/0).
    - Lives, power and score change plausibly through the stage. The score looks stored /10. Power: see the S12 correction below (units of 0.05, max 80). It drops to 0 after a death (S6). Values outside a run are leftovers from the previous run or the title demo.
    - `ADDR_IS_BOSS_PRESENT` is unsourced, and S4/S6 look identical apart from resources. The boss signal has to be found before 08 can detect midboss and boss kills. Candidates: thprac `thprac_th11.cpp`, a CE search (changed/unchanged between S3 → S4 → S5 → S6).
  - **S5, after the midboss leaves.** As S3 except `ADDR_POWER = 44`, `ADDR_SCORE = 25235`. The score is lower than in S4 (97475), so this was probably a separate run.
  - **S9, quit to the menu during Yamame** (Esc no longer crashes when the game is started through `custom.exe`). `ADDR_GAME_MODE = 60379904` (0x03995300, a menu pointer again), `ADDR_MENU = 0 (addr 0x039953B0)`, `ADDR_MENU_CURSOR = 2 (addr 0x03995324)`, `ADDR_GAME_FLAGS = 0`, `ADDR_STAGE = 1`, `ADDR_DIFFICULTY = 0`, `ADDR_CHARACTER = 0`, `ADDR_SHOT_TYPE = 0`, `ADDR_LIVES = 6`, `ADDR_LIFE_PIECES = 1`, `ADDR_POWER = 50`, `ADDR_SCORE = 169454`, `ADDR_CONTINUES = 0`.
  - **S10, game over screen** (an Extra run: stage 7, difficulty 4). `ADDR_GAME_MODE = 0`, menu entries `<unreadable>`, `ADDR_GAME_FLAGS = 0`, `ADDR_STAGE = 7`, `ADDR_DIFFICULTY = 4`, `ADDR_CHARACTER = 0`, `ADDR_SHOT_TYPE = 0`, `ADDR_LIVES = -1`, `ADDR_LIFE_PIECES = 0`, `ADDR_POWER = 0`, `ADDR_SCORE = 352257`, `ADDR_CONTINUES = 0`.
  - **S11a, right after losing a life** (Practice Stage 1, Easy). As S3 except `ADDR_DIFFICULTY = 0`, `ADDR_LIVES = 8` (from 9), `ADDR_POWER = 0`, `ADDR_SCORE = 87527`.
  - **S11b, after collecting a life piece.** `ADDR_GAME_FLAGS = 16`, `ADDR_DIFFICULTY = 0`, `ADDR_LIVES = 6`, `ADDR_LIFE_PIECES = 1`, `ADDR_POWER = 50`, `ADDR_SCORE = 169454` (the same values as S9, so S9 was probably taken right after this, in the same run).
  - **S12, after a bomb.** No paste. The human watched `ADDR_POWER` drop by exactly 20 per bomb.
  - **Analysis (for 07/08):**
    - **Power is stored in units of 0.05:** 20 = 1.00, the bomb cost, and the max is 80 = 4.00 (seen as a leftover in S1). So `+0.50 Power` = +10 and `+0.05 Power` = +1, capped at 80.
    - **Leaving play:** on quit (S9) the menu pointer turns non-zero again, while stage, lives, power and score keep their last values. So 08's negative case (quit/retry during a boss → no check) can key on "menu pointer became non-zero".
    - **Game over:** `ADDR_LIVES = -1` (S10).
    - **`ADDR_GAME_FLAGS`:** 16 in Practice play (S3–S7, S11), 0 in Extra play and at game over (S10), 4 on character select. 0x10 looks like a Practice-mode bit. Confirm with a normal-game probe during S8.
    - **`ADDR_DIFFICULTY`:** Easy 0, Normal 1, Hard 2, Lunatic 3, Extra 4. `ADDR_STAGE`: Extra = 7.
  - **Boss signal (spike `spike/boss-scan`, 2026-10-09/10).** `ADDR_IS_BOSS_PRESENT = [0x4A8D7C, 0x1C]`: the enemy manager's boss-object pointer, non-zero while a midboss or boss is up.
    - **Found** with `/bossrec` on Practice Stage 1 (`bossrec_20261009_225945.jsonl`): the only candidate was on at 36.0–58.7 s (Kisume) and 97.5–167.7 s (Yamame), off 1.7 s before the +500000 clear bonus. MoF's 0x9E24/0x9E94 are non-zero all stage in SA, so they're not used.
    - **Confirmed** with `/bosswatch` on Practice Stage 2: boss on, off, on, off, then back in the menu, matching Parsee's midboss and boss. Unlike MoF, one field covers the stage 2 midboss.
    - **Open for 08:** a midboss that leaves on its timer probably clears the field like a defeated one. A second signal (HP or the spell bonus) may be needed to count only real defeats. Stage 3 (Yuugi midboss) and stages 4–6 aren't watched yet; one `/bosswatch` run each confirms them.
    - **`/bosswatch` per stage (human, 2026-10-10):**
      - **Stage 3:** one ON/off pair only. Yuugi appears as midboss, stays through the second half of the stage and becomes the end boss, so the field doesn't separate `Yuugi - Midboss` from `Yuugi Defeated`. Needs a second signal for the midboss→boss transition (e.g. a `/bossrec` of Stage 3, searching for a field that changes *inside* the single on-run: phase/spell counter, HP bar reset).
      - **Stage 4:** the midboss (Orin as a cat) appears twice, and both are recorded cleanly, plus Satori. The spec has no stage 4 midboss location (it leaves on a timer). Open idea: a location for the second appearance only.
      - **Stage 5:** normal, midboss and boss.
      - **Stage 6:** not watched yet.
      - **Human's call:** stages 3/4 are the special cases (4 bosses across 2 stages). Worst case, leave them simplified (no separate Yuugi midboss check, no stage 4 midboss check) rather than block on them.
      - **Update 2026-10-10:**
        - **Stage 6:** normal like 1/2/5 (midboss and boss runs).
        - **Extra (stage 7):** assumed normal, not watched.
        - **Stage 3:** the Yuugi midboss→boss split will come from the spell-card tracker planned for captures (current spell ID, ticket 22). Ticket 08 sends both Yuugi checks when the single run ends until then.
        - **Stage 4:** the human decided on two locations, one per cat-Orin appearance (ticket 25).
        - **S13:** moved to ticket 17.
  - **S8a (fresh save, Practice menu):** same as S0. **S8b (after clearing Stage 1 on Easy in a normal game, back at the Practice menu):** `ADDR_GAME_MODE = 0`, menu entries `<unreadable>`, `ADDR_GAME_FLAGS = 0`, `ADDR_STAGE = 0`, `ADDR_DIFFICULTY = 1`, `ADDR_CHARACTER = 0`, `ADDR_SHOT_TYPE = 0`, `ADDR_IS_BOSS_PRESENT = <unreadable>` (enemy manager ptr 0), lives/power/score 0, same 4 unsourced.
    - The unlock bytes aren't in the table, so `/probe` can't show them. Next: a `/dump before` / `/dump after` diff of the blocks behind the static pointers (MoF keeps practice access at `[0x4783C, 0x4E9 + 8·i]`, one 8-byte record per shot × difficulty × stage).
    - **For 08:** the menu pointer reads 0 on this screen, so "menu pointer 0" alone doesn't mean "in play". A stage is running when the enemy manager pointer (`0x4A8D7C`) is non-zero; use that, or both.
  - **Practice-unlock search (2026-10-10), not found:**
    - `/dump` before/after a normal-game Stage 2 unlock (Marisa B Easy) and before/after the "unlock all" cheat (Marisa C Lunatic) showed no unlock bytes in `.data` or one pointer hop from it.
    - Byproducts: `0x4C9A00`/`0x4C9B00` are keyboard state tables (current/previous). The heap struct behind `0x4C343C` (`0x14AF998`) has paired counters at a 0x20 stride from `+0x6E8` that rose during play: likely spell-card attempt/capture history (for 22).
    - **Moved to 26–28:** decode the save format, `/memsearch` for the decoded pattern, then the item writes.
  - **Closed 2026-10-10:** every state needed by 07 is recorded. S13 → 17, practice unlock → 26–28, Yuugi midboss split → 22 (spell ID).
