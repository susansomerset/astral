# AST-537 — Regression tests: dispatch without agent_task rows (gaze, recheck_no_openings)

<!-- linear-archive: AST-537 archived 2026-06-23 -->

## Linear archive (AST-537)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-537/regression-tests-dispatch-without-agent-task-rows-gaze-recheck-no  
**Status at archive:** Done  
**Project:** Astral Dispatcher (inherited from AST-533)  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-533 — BUG: Scheduled Actions ignore dispatch task_key — consult hardcodes state→task routing  
**Blocked by / blocks / related:** parent: AST-533

### Description

## Purpose

**AST-531** `_dispatch_one` probes `run_next` via `_current_agent_task_run_next` for every scheduled row. Non-LLM dispatch keys (`gaze`, `recheck_no_openings`, …) have no `agent_task` row — runtime must not require Manage Tasks seeding for those hops.

Hotfix (AST-533 UAT): `_current_agent_task_run_next` returns `''` when `get_agent_task` is missing.

## Scope

* Component test: `_dispatch_one` does not raise for `task_key=gaze` / `recheck_no_openings` when no `agent_task` row (mock candidate + dispatch loop).
* Optional: stub LLM path vs Playwright-only path so we catch regressions without live agent_task DB rows.

## Parent

AST-533 — dispatch task_key honesty epic.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
