# 74: [human] Probe batch 9: Yuugi's midboss, and the luck option

Status: ready-for-human
Blocked by: None

## Problem
73 needs to know how Stage 3's boss field behaves between Yuugi's midboss and boss. 71 (A Little Bit of Luck) needs a glance in game.

## Test plan
Setup: the client from the latest `main`, `/writelog on`.

### R1, needed by 73: Yuugi's midboss
Practice Stage 3, once with Reimu and once with Marisa:
- During the midboss: `/probe`. Paste `ADDR_IS_BOSS_PRESENT`, `ADDR_SPELL_ID`, `ADDR_SPELL_FLAGS`.
- Right after the midboss is gone (if she leaves the screen): `/probe`, same lines.
- During the boss fight: `/probe`, same lines.
- Note for each run whether you killed the midboss or it timed out, and which checks the client sent when.

### R2, needed by 71: the luck option
A seed with `a_little_bit_of_luck: 'true'` (and Hard/Normal gates without Lunatic): the Tracker's Stage 5 line asks for Normal (`Normal: Lower Difficulty 0/1`) until you have one.

## Comments
