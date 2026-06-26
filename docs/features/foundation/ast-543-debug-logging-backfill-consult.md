# AST-543 — Debug logging backfill: consult

<!-- linear-archive: AST-543 archived 2026-06-23 -->

## Linear archive (AST-543)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-543/debug-logging-backfill-consult  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Backfill **AST-538** debug logging across **consult** batch and grading paths (encoded rubric, job consult stages). Debug runs must show per-job inputs, grading branches, and pass/fail reasons — not only batch totals.

## Functional scope

* Instrument consult claim loops, rubric evaluation, and state transitions with index headers + `|` detail.
* Lazy-import patterns unchanged; logging only.

## Boundaries

* No consult scoring or state machine changes.
* Blocked until **AST-538** lands.

## Acceptance criteria

1. Debug consult batch shows per-job detail before summary line.
2. `debug=False` unchanged.

## Dependencies and blockers

* **AST-538**

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T04:31:01.939Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-543 (parent) | ftr/ast-543-debug-logging-backfill-consult |
| AST-619 | sub/AST-543/AST-619-consult-claim-loop-grading-debug |

**Epic worktree:** `astral-AST-543/` — one active sub checked out at a time.

**Parent:** AST-543

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
