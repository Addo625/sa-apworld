# 61: [human] Probe batch 5

Status: done
Blocked by: None

## Problem
Batch 58 left: the dialog crash (R3), menu dumps that were all of the title (R1), the Extra check (R2), plus re-checks of 60's power and 24's capture fixes. One session. Agents may append requests.

## Test plan
Setup: the client from the latest `main` (Claude reinstalled it), seed `AP_96277890279384246223`, slot **`Playtest2`**, `/writelog on`. Keep the game folder's save as is: captures already sent stay recorded on the server now.

### R1, needed by 24: the dialog crash is gone
- Practice Stage 1 and Stage 2, play through every dialog. Then a Start run through Yamame's dialog.
- If it still crashes: `/itemsound off`, restart the game, and try once more. Paste the last 20 client lines either way.

### R2, needed by 48: what tells the Options screen apart
On each screen, **first `/probe`**, then `/peek <the ADDR_MENU addr on that screen's probe>-B0 256`:
(a) title, (b) Option, (c) Start → difficulty select, (d) Practice → difficulty select, (e) Esc from the character select back to the difficulty select. Paste each probe's `ADDR_MENU_PTR` / `ADDR_MENU` lines and the peek, labeled.

### R3, needed by 56: the title cursor rows
- `/send Playtest2 Extra Stage` (the global form of the item). Does Extra Start become selectable?
- On the title, `/probe` with the cursor on Start, Extra Start and Practice Start. Paste the `ADDR_MENU` and `ADDR_MENU_CURSOR` lines.

### R4, needed by 57: the continue screen after losing to a boss
- In a Start run, lose all lives during a boss. On the continue prompt: `/probe` → paste. Quit, then `/probe` on the next screen → paste.

### R5, needed by 60: Practice power on later stages
- Practice Stage 2 or later: is the power 0.50 × the packs from `/received` (not 4.00)?

### R6, needed by 24: captures
- Capture a card you never captured with that character: does the client log `Spell card N captured: ...` after the run (back on a menu), and the server show the check?
- Capture Kisume's card again: the client logs `captured before`, and nothing is sent.

## Decisions to confirm
- 24: the same spell on another difficulty is a different card (each difficulty has its own card ID in the game). Should it count as the same card instead?
- 24: once R1 and R6 pass, `spell_card_keys` defaults to `alongside`.

## Comments

### R1

No crash in neither stages

**New Bug:** Upon failing S1 and retrying during Yamame (specifically the last attack), when started a "play again", it gave me the items for defeating Yamame and clearing S1. (We have also encountered this bug when testing Normal Mode, but deferred it). Happened in S2 as well
**New Bug:** When choosing _give up and Retry_ I start with full Power instead of however many I've acquired. (S2 onwards). When beginning with X Power, I still have the sprite of full power (not that it matters)

**New Bug**: After this incident above, when I've captured the Yamame cards for the first time (only the 2nd playthrough of S1), I received no check.
**New Bug:** When going back to the main menu after dying, I received _Stage 2 Capture 1_, 


Looks like two of the bugs are related to _Give up and Retry_ option, and other two related to the spell card keys - worth investigating.


### R2

#### title

ADDR_MENU_PTR = 48103456 (addr 0x004A8ECC)
ADDR_MENU = 0 (addr 0x02DE00D0)

0x02DE0020: 00 00 00 00 02 00 00 00 00 00 00 00 08 e8 b7 02 38 e8 b7 02 a8 fa b7 02 18 4b 4a 01 01 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00

#### Option

ADDR_MENU_PTR = 48103456 (addr 0x004A8ECC)
ADDR_MENU = 1 (addr 0x02DE00D0)

0x02DE0020: 00 00 00 00 02 00 00 00 00 00 00 00 50 46 df 02 80 46 df 02 c8 fc b7 02 28 4e 4a 01 03 00 00 00 02 00 00 00 02 00 00 00 02 00 00 00 05 00 00 00 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00

#### Game Start Diff. Select

ADDR_MENU_PTR = 48103456 (addr 0x004A8ECC)
ADDR_MENU = 1 (addr 0x02DE00D0)

0x02DE0020: 00 00 00 00 02 00 00 00 00 00 00 00 50 46 df 02 80 46 df 02 c8 fc b7 02 28 4e 4a 01 05 00 00 00 02 00 00 00 02 00 00 00 02 00 00 00 04 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 05 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00

#### Practice Start Diff. Select

ADDR_MENU_PTR = 48103456 (addr 0x004A8ECC)
ADDR_MENU = 1 (addr 0x02DE00D0)
0x02DE0020: 00 00 00 00 02 00 00 00 00 00 00 00 50 46 df 02 80 46 df 02 c8 fc b7 02 28 4e 4a 01 05 00 00 00 02 00 00 00 02 00 00 00 02 00 00 00 04 00 00 00 02 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 05 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00

#### Back to Difficulty

ADDR_MENU_PTR = 48103456 (addr 0x004A8ECC)
ADDR_MENU = 1 (addr 0x02DE00D0)

0x02DE0020: 00 00 00 00 02 00 00 00 00 00 00 00 50 46 df 02 80 46 df 02 c8 fc b7 02 28 4e 4a 01 05 00 00 00 02 00 00 00 02 00 00 00 02 00 00 00 04 00 00 00 02 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00

### R3

Extra Stage is unselectable, even when "refreshing" the main menu

**Game Start**
ADDR_MENU = 0 (addr 0x02DE00D0)
ADDR_MENU_CURSOR = 0 (addr 0x02DE0044)

**Practice Start**
ADDR_MENU = 0 (addr 0x02DE00D0)
ADDR_MENU_CURSOR = 2 (addr 0x02DE0044)


### R4

#### Midboss Probes

ADDR_MENU_PTR = 0 (addr 0x004A8ECC)
ADDR_ENEMY_MANAGER = 50465208 (addr 0x004A8D7C)
ADDR_MENU = <unreadable>
ADDR_MENU_CURSOR = <unreadable>
ADDR_GAME_FLAGS = 16 (addr 0x004A5758)
ADDR_STAGE = 3 (addr 0x004A5728)
ADDR_DIFFICULTY = 1 (addr 0x004A5720)
ADDR_CHARACTER = 0 (addr 0x004A5710)
ADDR_SHOT_TYPE = 0 (addr 0x004A5714)
ADDR_IS_BOSS_PRESENT = 48289064 (addr 0x030209D4)
ADDR_REPLAY_MGR_PTR = 21646104 (addr 0x004A8EB8)
ADDR_LIVES = -1 (addr 0x004A5718)
ADDR_LIFE_PIECES = 0 (addr 0x004A571C)
ADDR_POWER = 0 (addr 0x004A56E8)
ADDR_SCORE = 32277 (addr 0x004A56E4)
ADDR_CONTINUES = 0 (addr 0x004A573C)
ADDR_PLAYER_PTR = 48103456 (addr 0x004A8EB4)
ADDR_SPEED_NORMAL = 576 (addr 0x02DE08B0)
ADDR_SPEED_FOCUS = 256 (addr 0x02DE08B4)
ADDR_SPEED_NORMAL_D = 407 (addr 0x02DE08B8)
ADDR_SPEED_FOCUS_D = 181 (addr 0x02DE08BC)
ADDR_PLAYER_STATE = 2 (addr 0x02DE0948)
ADDR_SPELL_CARDS = -276105591 (addr 0x02B4CCB4)
ADDR_PRACTICE_UNLOCK = 0 (addr 0x02B4CBF4)
ADDR_EXTRA_UNLOCK = 0 (addr 0x02B7A438)
ADDR_PRACTICE_STARTING_LIVES = 1461192135 (addr 0x0041FA49)
ADDR_NORMAL_CONTINUE_LIVES = 1461204361 (addr 0x0041FA38)
ADDR_CUSTOM_SOUND_ID = 0 (addr 0x004CAF00)
ADDR_SOUND_HACK_1 = 102671336 (addr 0x00429058)
ADDR_SOUND_HACK_2 = 3509088 (addr 0x0048AF00)


ADDR_MENU_PTR = 48103456 (addr 0x004A8ECC)
ADDR_ENEMY_MANAGER = 0 (addr 0x004A8D7C)
ADDR_MENU = 0 (addr 0x02DE00D0)
ADDR_MENU_CURSOR = 2 (addr 0x02DE0044)
ADDR_GAME_FLAGS = 0 (addr 0x004A5758)
ADDR_STAGE = 3 (addr 0x004A5728)
ADDR_DIFFICULTY = 1 (addr 0x004A5720)
ADDR_CHARACTER = 0 (addr 0x004A5710)
ADDR_SHOT_TYPE = 0 (addr 0x004A5714)
ADDR_IS_BOSS_PRESENT = <unreadable>
ADDR_REPLAY_MGR_PTR = 0 (addr 0x004A8EB8)
ADDR_LIVES = -1 (addr 0x004A5718)
ADDR_LIFE_PIECES = 0 (addr 0x004A571C)
ADDR_POWER = 0 (addr 0x004A56E8)
ADDR_SCORE = 32277 (addr 0x004A56E4)
ADDR_CONTINUES = 0 (addr 0x004A573C)
ADDR_PLAYER_PTR = 0 (addr 0x004A8EB4)
ADDR_SPEED_NORMAL = <unreadable>
ADDR_SPEED_FOCUS = <unreadable>
ADDR_SPEED_NORMAL_D = <unreadable>
ADDR_SPEED_FOCUS_D = <unreadable>
ADDR_PLAYER_STATE = <unreadable>
ADDR_SPELL_CARDS = -276105591 (addr 0x02B4CCB4)
ADDR_PRACTICE_UNLOCK = 0 (addr 0x02B4CBF4)
ADDR_EXTRA_UNLOCK = 0 (addr 0x02B7A438)
ADDR_PRACTICE_STARTING_LIVES = 1461192135 (addr 0x0041FA49)
ADDR_NORMAL_CONTINUE_LIVES = 1461204361 (addr 0x0041FA38)
ADDR_CUSTOM_SOUND_ID = 0 (addr 0x004CAF00)
ADDR_SOUND_HACK_1 = 102671336 (addr 0x00429058)
ADDR_SOUND_HACK_2 = 3509088 (addr 0x0048AF00)

#### EndBoss Probe

ADDR_MENU_PTR = 0 (addr 0x004A8ECC)
ADDR_ENEMY_MANAGER = 21647168 (addr 0x004A8D7C)
ADDR_MENU = <unreadable>
ADDR_MENU_CURSOR = <unreadable>
ADDR_GAME_FLAGS = 16 (addr 0x004A5758)
ADDR_STAGE = 1 (addr 0x004A5728)
ADDR_DIFFICULTY = 1 (addr 0x004A5720)
ADDR_CHARACTER = 0 (addr 0x004A5710)
ADDR_SHOT_TYPE = 0 (addr 0x004A5714)
ADDR_IS_BOSS_PRESENT = 48155784 (addr 0x014A4F5C)
ADDR_REPLAY_MGR_PTR = 21646104 (addr 0x004A8EB8)
ADDR_LIVES = -1 (addr 0x004A5718)
ADDR_LIFE_PIECES = 3 (addr 0x004A571C)
ADDR_POWER = 0 (addr 0x004A56E8)
ADDR_SCORE = 207777 (addr 0x004A56E4)
ADDR_CONTINUES = 0 (addr 0x004A573C)
ADDR_PLAYER_PTR = 48103456 (addr 0x004A8EB4)
ADDR_SPEED_NORMAL = 576 (addr 0x02DE08B0)
ADDR_SPEED_FOCUS = 256 (addr 0x02DE08B4)
ADDR_SPEED_NORMAL_D = 407 (addr 0x02DE08B8)
ADDR_SPEED_FOCUS_D = 181 (addr 0x02DE08BC)
ADDR_PLAYER_STATE = 2 (addr 0x02DE0948)
ADDR_SPELL_CARDS = -276105591 (addr 0x02B4CCB4)
ADDR_PRACTICE_UNLOCK = 0 (addr 0x02B4CBF4)
ADDR_EXTRA_UNLOCK = 0 (addr 0x02B7A438)
ADDR_PRACTICE_STARTING_LIVES = 1461192135 (addr 0x0041FA49)
ADDR_NORMAL_CONTINUE_LIVES = 1461204361 (addr 0x0041FA38)
ADDR_CUSTOM_SOUND_ID = 0 (addr 0x004CAF00)
ADDR_SOUND_HACK_1 = 102671336 (addr 0x00429058)
ADDR_SOUND_HACK_2 = 3509088 (addr 0x0048AF00)

### R5

It works fine when loading into a level from the menu, in some shot types it's visually bugged but works.
However, when loading from "Give up and retry", as detailed in R1, I start with full Power

### R6

As noted before - I think it DOES work as you mentioed in R6 
`Spell card 12 captured (captured before, or no capture check left in this stage)`
`Spell card 16 captured: Stage 2 - Capture 2`
`Addo found their +0.05 Power (Stage 2 - Capture 2)`

### Claude, 2026-10-20
- **R1:** no crash, which confirms the cause (24's save reads in play). The retry bugs (checks from a retry, full power after Give up and Retry) are fixed in 62, which also closes 57. The other two weren't bugs: this is the `Addo` seed (`capture_slots: shared`), whose Stage 1 had only 2 capture slots, both used by batch 58's double Kisume; and captures are sent on the next menu by design.
- **R2:** menu +0x1C tells the Options screen apart (title 1, Option 3, difficulty 5). Human: README warning for now, 48 deferred with that fix.
- **R3:** `Addo` has `extra_stage: linear`: Extra opens with the 6th Next Stage, not an `Extra Stage` item. Title cursor: Start 0, Practice 2 (→ 56).
- **R4:** game over = lives -1 with the boss still up → 62.
- **R5:** retry power → 62.
- **R6:** works. The same spell on another difficulty now counts once (63). Keys default to alongside (24).
- **Questions:** the tracker shows one block per character now (54). `sayilovebeer` isn't in `th11.exe` as text, and a cheat unlock can't send checks anyway (the stage, shot and difficulty filters). Life pieces can't identify *which* attack was captured, so captures stay on the save's counts.
