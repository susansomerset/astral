# AST-541 — Debug logging backfill: agent

<!-- linear-archive: AST-541 archived 2026-06-23 -->

## Linear archive (AST-541)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-541/debug-logging-backfill-agent  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Backfill **AST-538** debug logging across **agent** paths (`do_task`, `run_next`, token overlay, LLM call boundaries). UAT needs to see prompt assembly context and hop outcomes when debugging chains — not only success/failure summaries.

## Functional scope

* Instrument agent entry/exit, `run_next` chain steps, and token resolution branches with index headers + `|` detail.
* Long LLM payloads use 50-line / 15+omit+15 truncation via shared helper.

## Boundaries

* No change to agent business logic or cache semantics.
* Blocked until **AST-538** helper exists.

## Acceptance criteria

1. Daisy-chained task run with `debug=True` shows per-hop agent detail (task key, batch id, index) before external LLM call.
2. Truncation helper used for responses >50 lines.
3. `debug=False` unchanged.

## Dependencies and blockers

* **AST-538**

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T04:00:46.577Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-541 (parent) | ftr/ast-541-debug-logging-backfill-agent |
| AST-618 | sub/AST-541/AST-618-agent-do-task-run-next-token-debug |

**Epic worktree:** `astral-AST-541/` — one active sub checked out at a time.

**Parent:** AST-541

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
