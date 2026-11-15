# 85: What a normal Start run does in a Practice seed (decision)

Status: done
Blocked by: None

## Problem
Playtest 3 (2026-10-25): Janania started a normal game (title → Start) in a Practice seed, got no checks and saw no message.
- `detect.locked` rejects runs without the Practice flag (`detect.py:51`), and `Client.py:160-163` logs `Start (the normal game; this seed plays from Practice) isn't unlocked: this run sends no checks`.
- That line is **not** behind `/writelog`. It prints only if the client is connected with items when the run starts, so Janania either missed one log line or started before connecting.
- Nothing shows in the game. "Move the message out of writelog" therefore changes nothing: the decision is what Start should do.

## Decision needed (human)
Pick one; each option names the follow-up it promotes.

### D1. Block Start (promote 56): recommended
In Practice seeds, `guard.correct` moves the title cursor from Start (0) to Practice (2). Batch 61 R3 already sourced the rows, so it's code only.
- **Pros:** the mistake can't happen. Smallest change. The existing log line stays as a fallback.
- **Cons:** players who reach for Start by habit get moved without being told why, so it needs a one-line log/README note. Before connecting, nothing is blocked (no slot data yet).

### D2. Keep Start locked, add an in-game cue
When a locked run starts (Start, a locked shot type or a locked difficulty), the client plays the buzzer (`SOUND_IDS["trap"]`) next to the log line.
- **Pros:** covers every lock, not just Start. Tiny.
- **Cons:** the player can still waste a run. A buzzer doesn't say *why*.

### D3. Allow Start runs (needs a continue design)
Drop the Start branch in `detect.locked`.
- **How it plays:**
  - the stages go 1→6 back-to-back. Each stage counts only if it's open for the owner (`stage_open`; key, shot type and difficulty locks still apply);
  - with progressive unlocks, the run is useful up to the first locked stage and plays on for nothing after it;
  - Start already uses the patched non-Practice init (`Client.py:236`): item lives at the start and on each continue, but power isn't patched;
  - resources and life-piece extends carry over between stages, so a stage can be easier or harder than its gate assumed;
  - logic is unchanged: Start is never required.
- **Under each continue design:**

  | Continues | Start run | Pros | Cons |
  |---|---|---|---|
  | A: unlimited, restoring item lives (spec today) | A game over continues on the spot, mid-boss, with full item lives | Nobody gets stuck. Fewer menu trips | **Every gate can be bypassed**: any boss falls to brute force, whereas a Practice retry restarts the stage |
  | B: limited, `+1 Continue` items (18) | Continues are a resource; run out → title, checks kept | Gates matter again; a useful item instead of filler | Needs `ADDR_CONTINUES` verified + ending the run; Practice stays the safer path |
  | C: checks after a continue don't count (19) | Continuing is allowed, but that stage's checks wait for a clean clear | As fair as Practice | "I beat Yuugi, no check?" needs a clear message; per-stage continue tracking |
  | D: penalty per continue (20) | Each continue fires a trap or DeathLink | Multiworld flavor | Punishes teammates for one player's choice; brute force still works |
  | E: no continues | A 1cc attempt | A pure challenge mode | Niche; one mistake throws away a long run |

- **Recommendation:** D3 only together with B or C; under A it undermines the gates.

## DoD / Test plan per option
- **D1** (56's plan):
  - `test_guard`: Practice seed, title menu, cursor 0 → 2; cursor 1/2 left alone; a normal-mode seed leaves cursor 0.
  - In game: the cursor can't rest on Start.
- **D2:** `test_client`: a Start run in a Practice seed writes the trap sound ID once at run start; an unlocked Practice run writes none.
- **D3:**
  - `test_detect`: a non-Practice run in a Practice seed sends the checks of open stages and nothing for locked ones;
  - plus the chosen continue ticket's own tests (18/19).

## Steps
After the decision: promote the matching ticket (56, a new D2 ticket, or this one plus 18/19), then implement it per its plan.

## Deferred
- None.

## Comments
- 2026-10-25 human: "go with D2 and then slowly progress towards D3." Follow-ups, in order:
  - 86: D2, a buzzer on any locked run;
  - 87: continue design C for Practice seeds' Start runs (a continue voids that stage's checks), the recommended pairing for D3;
  - 88: D3, Start runs send checks.
  56 (block Start) stays deferred.
