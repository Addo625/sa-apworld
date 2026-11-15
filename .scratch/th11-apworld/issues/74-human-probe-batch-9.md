# 74: [human] Probe batch 9: Yuugi's midboss, the luck option, Start runs

Status: done
Blocked by: None

## Problem
73 splits Yuugi's midboss from the boss by counting spell cards. This batch checks it in game. 71 (A Little Bit of Luck) needs a glance in game. 87 and 88 (Start runs in Practice seeds, continues) need one Start run.

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
A seed with `a_little_bit_of_luck: 'true'` (and Hard/Normal gates without Lunatic): the spoiler shows the gate rounded up (Stage 5 asks for Normal, two Lower Difficulty).

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

### R1
Boss pointer became non-zero (`315379856`) when midboss appeared.

During midboss, spell-id=`001B` and spell-flag=`67`

After midboss defeat/timeout (same result), boss pointer did not change, spell-id became `0`.

Beating the midboss did not send `Yuugi - Midboss`, but it was sent after clearing the stage - regressions from a problem we've had before

### R2
Tracker does not show by itself the required difficulty for each Stage (which is good). However, by looking at the spoilers I can confirm that on 1 example, the extra luck worked - last `lower diff` item was in stage 4. So, so far so good!
Having the tracker show required difficulty per stage is stale, and not needed IMO

### R3

Byte chaneged after a a continue. Entering S3 prints line, couldn't check audio due to physical technical limitations
Lives and power Carry over

### Outcome (2026-11-15 Claude)
- R1: failed. Yuugi stayed on the field from midboss into boss, so 73's card count sent the midboss check only at the clear. Fixed by 89 (the midboss card ending); its in-game check is batch 90.
- R2: passes (spoiler). The tracker showing a per-stage difficulty was never built and isn't wanted.
- R3: passes. The continues counter moves on a continue, Stage 2's checks were withheld with the log line, and a locked Stage 3 logs on entry. The buzz wasn't heard; it is 84's sound path. Lives and power carry over between stages, which 88 allowed.
