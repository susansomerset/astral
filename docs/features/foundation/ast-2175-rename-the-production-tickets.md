# AST-2175 — Rename the production tickets

<!-- linear-archive: AST-2175 archived 2026-10-16 -->

## Linear archive (AST-2175)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2175/rename-the-production-tickets  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

**Scope:** AST tickets in **Discussion** filed by the production alert email (`src/core/monitor.py` subject: `[<env>/<Candidate>] <task_key> <STATUS>: N error(s) / M processed | <batch_id>`). As of 2026-10-12 that is five tickets, all already diagnosed (`## Prior occurrences` / `## As-is` in each body):

1. Re-list Discussion tickets matching the alert-subject pattern right before renaming (pick up any new arrivals; diagnose-less ones get a title from their first `[ERROR]` line).
2. Retitle each as a plain sentence naming the failure — **no prefixes**: no `[<env>/<Candidate>]`, no `<task_key>:` lead, no status/counts/`<batch_id>`. That's log content; it stays in the body log and the attached original email title. The task name appears only where the sentence needs it to say what broke. Proposed:

| Ticket | New title |
| -- | -- |
| [AST-2163](https://linear.app/astralcareermatch/issue/AST-2163) | `One omitted rubric vector sends a meteorite_like job to ERROR` |
| [AST-2162](https://linear.app/astralcareermatch/issue/AST-2162) | `Duplicate vector code in a grade line fails the whole meteorite_grade_do hop` |
| [AST-2160](https://linear.app/astralcareermatch/issue/AST-2160) | `5-char grade segments decode to no grades in meteorite_grade_do` |
| [AST-2157](https://linear.app/astralcareermatch/issue/AST-2157) | `No-job_link self-heal still errors in prod (AST-2143 fix not deployed)` |
| [AST-2154](https://linear.app/astralcareermatch/issue/AST-2154) | `Pinned-host 429 stops the meteorite_like batch and errors the job` |

3. Apply via one `issueUpdate { title }` per ticket as `--as chuckles` (`linear_proxy save-issue` has no `--title` flag; use `linear_gate.gql` one-off — no repo change). Touch title only: no status, assignee, label, or description edits.
4. Re-fetch each ticket and confirm the new title stuck.

## Done when

* Every production-alert ticket in Discussion has a distinct, prefix-free title that says what failed.
* Nothing else on those tickets changed.

## Not in scope

* Changing the alert email subject in `monitor.py` or having `fix-intake` retitle new arrivals automatically — separate ticket if wanted.

## Risks / open questions

* none

---

## Original brief

Please review the issues in Discussion that were reported and emailed to linear from the production platform and retitle each issue to be more meaningful (and concise) than the generic "COMPLETED: 1 error(s)…" because they all look identical now.

**Susan, plan round 1:** No, drop the duplicative title prefixes. That is log content not issue title.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
