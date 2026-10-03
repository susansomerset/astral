# AST-1794 — Silence no-agent empty_render warning (fix)

<!-- linear-archive: AST-1794 archived 2026-10-02 -->

## Linear archive (AST-1794)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1794/silence-no-agent-empty-render-warning-fix  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1793 — Agent of n/a for dispatch task should not generate an error  
**Blocked by / blocks / related:** parent: AST-1793

### Description

## What this implements

Stop empty-render list enrichment from logging a warning/error when a dispatch task has intentional agent n/a / no prompts to score (e.g. `stage_email_meteorite`). Keep `empty_render: false` pass behavior from AST-1791; silence the soft-miss warning only.

## Scope

## Component scope

* `src/ui/api/api_admin.py` — **modified** — `_evaluate_dispatch_empty_render` ValueError soft-miss branch currently logs the “has no agent_id / no prompts to validate” warning that operators see as an error for intentional n/a agent tasks.
* `src/utils/config.py` — **unchanged** — `empty_render_for_prompts` and prompt-load policy are not the issue; logging is api_admin-only.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **unchanged** — UI already trusts `empty_render`; this bug is log noise, not a mute/boolean regression.

## Technical scope

* `src/ui/api/api_admin.py` — **modified function** `_evaluate_dispatch_empty_render`: on `ValueError` from `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts` (no `agent_task`, empty `agent_id`, missing agent), stop emitting `logger.warning` while still returning `empty_render: false`. Do not change the fail-closed branches or the successful `empty_render_for_prompts` path.

## Notes for planning

No ancestor box was checked on AST-1793 — plan from this ticket's As-is/To-be/Proposed steps. Residual noise after AST-1791 ValueError → empty_render false path in `api_admin.py`. Parent bug: AST-1793.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1793-no-agent-empty-render-warning`, child `sub/AST-1793/<this-id>-<slug>`.

### Comments

#### radia — 2026-09-25T14:48:33.784Z
[code-rubric] PROCEED (Commit: 22eee5cd) soft-miss warning silenced; board REVISE → gap AST-1795

#### joan — 2026-09-25T14:41:19.424Z
[board-joan]  CANON: OK

ValueError soft-miss is a pass, not a failed item — `stat.logging.warning` Resolution #4 (nothing failed → no warning). Fail-closed branches keep warning/exception logging; plan avoids `stat.logging.info.api` route spam. No statute update needed.

context_tokens≈14000

#### betty — 2026-09-25T14:40:57.106Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md (TestAst1791NoPromptValueErrorEmptyRender) — missing coverage — ValueError soft-miss return covered; silence of `no prompts to validate` warning not asserted

#### hedy — 2026-09-25T14:39:43.463Z
`origin/sub/AST-1793/AST-1794-no-agent-empty-render-warning` @ `bfc7a4e86c64af387ee9c41eb80350f48a173986` · silence soft-miss warning

---

_Implementation detail may live in git history on `origin/dev`._
