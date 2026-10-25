# 74: [human] Probe batch 9: Yuugi's midboss, the luck option, Start runs

Status: ready-for-human
Blocked by: None

## Problem
73 splits Yuugi's midboss from the boss by counting spell cards. This batch checks it in game. 71 (A Little Bit of Luck) needs a glance in game.

## Test plan
Setup: the client with 73, 87 and 88 installed.

### R1, checks 73: Yuugi's midboss (Cheat Engine)
1. Cheat Engine → attach to `th11.exe` → **Add Address Manually** three times. For each, tick *Pointer* and give the base and offset (4-byte values):
   - boss pointer: `th11.exe+A8D7C`, offset `1C`;
   - spell ID: `th11.exe+A8D6C`, offset `8DC`;
   - spell flags: `th11.exe+A8D6C`, offset `8E0`.
2. Practice Stage 3, once with Reimu and once with Marisa. Kill the midboss in one run; if you can, let it time out in another.
3. Paste:
   - whether the boss pointer drops to 0 between the midboss and the boss;
   - the spell ID during the midboss card and during each boss card;
   - which checks the client sent, and when.
4. Pass: the midboss sends only `Yuugi - Midboss`, and beating Yuugi sends `Yuugi Defeated` + `Stage 3 Clear`.
   - If it fails, the pasted IDs show whether the midboss declares more than one card, or none when it times out.

### R2, needed by 71: the luck option
A seed with `a_little_bit_of_luck: 'true'` (and Hard/Normal gates without Lunatic): the Tracker's Stage 5 line asks for Normal (`Normal: Lower Difficulty 0/1`) until you have one.

### R3, checks 87 and 88: Start runs in a Practice seed
Setup: a Practice seed with Stages 1–2 open for your shot type and Stage 3 locked; `/writelog` on.
1. Cheat Engine: add `th11.exe+A573C` (4-byte, no pointer), the continues counter.
2. Title → **Start**. Clear Stage 1 cleanly. In Stage 2, game over at the boss, continue, and beat the boss.
3. Play into Stage 3.
4. Paste:
   - the continues value before and after the continue (does it go 0 → 1? does it reset on a new Start?);
   - the checks sent: expected all of Stage 1, none of Stage 2's boss/clear after the continue, and a "continue in Stage 2" log line;
   - entering Stage 3: an "isn't unlocked" line and a buzz;
   - from the `/writelog` "Run start" line and the HUD: your power at Stage 1's start and at Stage 2's start (item power each stage, or carried over?).
5. Pass: as expected above. If the counter doesn't move, 87 voids nothing; the follow-up is finding the right address.

## Comments
