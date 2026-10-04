# How we work

Copy this file into a project's root (Cursor and Codex read `AGENTS.md`; for Claude Code add a `CLAUDE.md` containing `@AGENTS.md`).

## Problem solving: four steps, recursive

Write code only when necessary. Before solving anything:

1. **Is the problem real?** Who suffers from it? Who might? Is the damage measured anywhere? If something is missing, can we show it? If the problem can't be defined well, don't solve it — say so and stop.
2. **Definition of Done.** When can we claim the problem no longer exists? Name an observable, preferably runnable, signal.
3. **Simplest solution that works.** Trivial algorithm, straightforward implementation, room left for improvement. Follow the ponytail ladder: existing code → stdlib → platform → installed deps → minimum new code.
4. **What problems does this solution create?** List them and run steps 1–4 on each. Edge cases must be accounted for, even if handled in a later phase.

## Planning

- Break work into small phases; each phase into steps that each end in a working state.
- Every ticket carries: **Problem**, **DoD** (runnable check), **Test plan** (inputs/outputs of each logical component), **Steps**, **Deferred**.
- Tests are planned before or alongside code — not necessarily written first.

## Execution and git

- Before coding a ticket: re-read its DoD and test plan.
- **A commit is one relevant change**: something the software does differently — a feature, a fix, a behavior change, a removal, a refactor with a stated reason — together with everything it needs (settings, tests, fixtures, ignore files, docs).
  - Test: *would it be a line in a changelog?* and *does reverting it alone leave a working product?* Both must be yes.
  - Plan steps are working order, not commit boundaries; one change may span several steps. Never mix two unrelated changes in one commit.
- **Never a commit on their own:**
  - Tracker updates (closing a ticket, changing status, notes) → ride along in the ticket's last code commit.
  - Fixes to this ticket's unpushed work (review findings, leftovers, mistakes) → fold into the commit they fix: `git commit --fixup <sha>`, then `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <ticket base>` before closing. Only ever rewrite the current ticket's unpushed commits.
  - Plan edits → one commit per planning session (`05: plan notes persistence`).
- Exception: an iteration that changed no code (failed, stuck, plan-broken) makes exactly one tracker-only commit, e.g. `07: block on missing docker permission`.
- **Subject** = `<ticket key>: <action verb> <what the software now does>`, imperative. Name the visible change, not the mechanism: `05: persist notes in sqlite`, not `05: add APP_DB_PATH setting`.
  - Ticket key is the tracker's own id: local `.scratch/` ticket number (`01`), GitHub issue (`#12`), JIRA issue key (`ABC-123`, also links the commit in JIRA). No ticket → no prefix.
- **Body**: why, decisions a reader couldn't guess, constraints (`UPDATE … RETURNING needs SQLite >= 3.35`). Never restate the subject. A ticket's last commit ends with `Closes <ticket key>`.

  ```
  05: persist notes in sqlite

  Notes survive restarts. DB path from APP_DB_PATH (default ./notes.db);
  one connection per request so importing the app creates no file.
  UPDATE ... RETURNING needs SQLite >= 3.35 (bundled with Python 3.13).

  Closes 05
  ```
- Never push unless the git mode is `pr`. The human pushes when they see fit.

## Deferred work

- Edge case that changes behavior → a follow-up ticket labeled `deferred`, blocked by the phase it depends on, fully specified (DoD, Test plan, Steps) so promoting it is just a relabel. Whether something is deferred is the human's call, made during planning; an agent that finds one mid-ticket creates it and lists it in `.agent-loop/HUMAN.md` for that decision.
- Known ceiling of a deliberate shortcut → a `ponytail:` comment naming the ceiling and the upgrade path (harvested with `/ponytail-debt`).

## .agent-loop/HUMAN.md — the loop's note to the human

`.agent-loop/HUMAN.md` (gitignored with the rest of `.agent-loop/`; create the directory if missing) tells the human what the loop needs from them. Whoever changes loop state (planner, worker) **rewrites the whole file** — never appends — from the tracker state and git. Keep it short; when nothing is needed, "Do now" says so.

```
# Your turn — <date time> — loop: stopped (<reason>) | idle | ready to run
## Do now
- [ ] <action> — <why, one line> → <exact command or file to open>
## Review
- Not pushed yet: <commit subjects, or `git log @{u}..`>
- Run to verify: <test command>; <DoD checks of tickets done since last push>
## Status
- done: <ids> · ready: <ids> · needs-human: <ids> · deferred: <ids> (promote: `/al-plan promote <path>`)
## Last run
- <ticket>: <outcome> — log: <log path>
```

## Agent skills

### Issue tracker

Local markdown tickets under `.scratch/th11-apworld/` (no GitHub). See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
