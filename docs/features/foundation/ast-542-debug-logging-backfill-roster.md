# AST-542 — Debug logging backfill: roster

<!-- linear-archive: AST-542 archived 2026-06-23 -->

## Linear archive (AST-542)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-542/debug-logging-backfill-roster  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Backfill **AST-538** debug logging across **roster** / inflow paths (discovery, vet, ingest, locate/parse handoffs). Susan's original pain point: 95-term batch showed summary counts but not CSE hits or ingest outcomes.

## Functional scope

* `vet_inflow_discovery`, `ingest_new_companies`, website resolution, and related batch loops log **what was found** and **what was recorded** per index.
* Warnings (e.g. slug owned by another candidate) appear under the matching index header with `|` detail.

## Boundaries

* No change to roster state machine or ingest rules.
* Blocked until **AST-538** helper + Code Rules land.

## Acceptance criteria

1. Debug inflow batch logs Google CSE result summary and vet/ingest record outcome per index N/M.
2. Matches sample shape documented on **AST-538**.
3. `debug=False` unchanged.

## Dependencies and blockers

* **AST-538**

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T04:31:27.514Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-542 (parent) | ftr/ast-542-debug-logging-backfill-roster |
| AST-621 | sub/AST-542/AST-621-roster-inflow-vet-ingest-debug |

**Epic worktree:** `astral-AST-542/` — one active sub checked out at a time.

**Parent:** AST-542

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
