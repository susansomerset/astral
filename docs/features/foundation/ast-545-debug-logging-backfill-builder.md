# AST-545 — Debug logging backfill: builder

<!-- linear-archive: AST-545 archived 2026-06-23 -->

## Linear archive (AST-545)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-545/debug-logging-backfill-builder  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Backfill **AST-538** debug logging across **builder** / artifact HTML generation paths. Debug should show which template keys resolved and what content shaped the output — without dumping full HTML unless truncated.

## Functional scope

* Instrument resume/cover letter builder entry points with debug helper.
* Apply long-content truncation for large HTML/text blobs.

## Boundaries

* No builder output shape changes.
* Blocked until **AST-538** lands.

## Acceptance criteria

1. Debug artifact build logs section/key resolution detail.
2. Large renders use 15+omit+15 truncation.
3. `debug=False` unchanged.

## Dependencies and blockers

* **AST-538**

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T05:09:21.821Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-545 (parent) | ftr/ast-545-debug-logging-backfill-builder |
| AST-623 | sub/AST-545/AST-623-builder-artifact-debug |

**Epic worktree:** `astral-AST-545/` — one active sub checked out at a time.

**Parent:** AST-545

— Chuckles

#### chuckles — 2026-06-14T04:32:21.708Z
@susan Queued — three In Progress parents still assignee Chuckles (AST-542, AST-543, AST-546). Resume dispatch when those land via prep-uat → origin/dev.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
