# AST-546 — Debug logging backfill: external LLM wrappers

<!-- linear-archive: AST-546 archived 2026-06-23 -->

## Linear archive (AST-546)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-546/debug-logging-backfill-external-llm-wrappers  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Backfill **AST-538** debug logging across **external** LLM wrapper modules (Anthropic, DeepSeek, etc.). Today Susan sees timing/token lines at INFO but not structured debug detail around request/response context when `debug=True`.

## Functional scope

* Wrap external call sites with shared debug helper: model, task key, timing, token counts, truncated response preview.
* Use 50-line / 15+omit+15 rule for raw LLM text in debug.

## Boundaries

* No API parameter or retry logic changes.
* Does not log secrets or full prompts at INFO when `debug=False`.
* Blocked until **AST-538** helper exists.

## Acceptance criteria

1. Debug LLM call logs task context + truncated response preview under `|` lines.
2. Existing INFO timing lines unchanged when `debug=False`.

## Dependencies and blockers

* **AST-538**

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T04:31:06.825Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-546 (parent) | ftr/ast-546-debug-logging-backfill-external-llm-wrappers |
| AST-620 | sub/AST-546/AST-620-external-llm-wrapper-debug |

**Epic worktree:** `astral-AST-546/` — one active sub checked out at a time.

**Parent:** AST-546

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
