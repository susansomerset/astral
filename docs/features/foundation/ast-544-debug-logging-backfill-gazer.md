# AST-544 — Debug logging backfill: gazer

<!-- linear-archive: AST-544 archived 2026-06-23 -->

## Linear archive (AST-544)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-544/debug-logging-backfill-gazer  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Backfill **AST-538** debug logging across **gazer** / roster watch paths (company gaze, job list cache interactions). Align with dispatcher + roster index conventions.

## Functional scope

* Per-entity index headers and `|` detail for gaze claim/process loops.
* Log discovery context Susan needs during UAT (URLs checked, states transitioned).

## Boundaries

* No gazer business logic changes.
* Blocked until **AST-538** helper exists.

## Acceptance criteria

1. Debug gaze batch shows per-company/job index detail.
2. `debug=False` unchanged.

## Dependencies and blockers

* **AST-538**

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T04:52:24.968Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-544 (parent) | ftr/ast-544-debug-logging-backfill-gazer |
| AST-622 | sub/AST-544/AST-622-gazer-company-gaze-job-cache-debug |

**Epic worktree:** `astral-AST-544/` — one active sub checked out at a time.

**Parent:** AST-544

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
