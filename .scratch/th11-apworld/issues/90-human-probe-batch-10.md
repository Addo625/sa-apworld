# 90: [human] Probe batch 10: Yuugi's midboss, again

Status: ready-for-human
Blocked by: None

## Problem
89 sends Yuugi's midboss check when her midboss card ends. This checks it in game.

## Test plan
Setup: the client with 89 installed; a Practice seed with Stage 3 open (`/send <you> Next Stage` twice from the server console) and an unlocked difficulty.

### R1, checks 89: Yuugi's midboss
1. Practice Stage 3. Kill Yuugi's midboss.
2. Paste: whether `Yuugi - Midboss` arrived right when the midboss ended (not at the stage clear).
3. Beat Yuugi. Paste: whether `Yuugi Defeated` and `Stage 3 Clear` arrived then.
4. If you can, once more letting the midboss time out: the midboss check should still arrive when it ends.

## Comments
