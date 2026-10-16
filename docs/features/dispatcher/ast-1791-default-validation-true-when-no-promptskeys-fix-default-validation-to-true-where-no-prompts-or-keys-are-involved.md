# AST-1791 — Default validation TRUE when no prompts/keys (fix) (Default validation to TRUE where no prompts or keys are involved)

<!-- linear-archive: AST-1791 archived 2026-10-02 -->

## Linear archive (AST-1791)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1791/default-validation-true-when-no-promptskeys-fix-default-validation-to  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1790 — Default validation to TRUE where no prompts or keys are involved  
**Blocked by / blocks / related:** parent: AST-1790

### Description

## What this implements

Default empty-render validation to pass when a dispatch task has no prompts / no expected tokens (non-agent tasks). Disable AUTO/Run only when prompts reference candidate-scoped tokens that resolve empty.

## Proposed change

- [X] `_evaluate_dispatch_empty_render`: on `ValueError` from `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts`, return `{"empty_render": False, "empty_tokens": []}` with warning that validation passes (no prompts to score)
- [X] Leave blank/`candidate_id` miss and unexpected `Exception` fail-closed (`empty_render: True`)
- [X] `_candidate_dispatch_empty_render_error`: no message change — no-prompt path now returns falsy so helper returns `None`
- [X] `src/utils/config.py` / React unchanged

## Scope

## Component scope

* `src/ui/api/api_admin.py` — **modified** — `_evaluate_dispatch_empty_render` (and any soft-miss / “could not validate prompts” message path that currently forces `empty_render` true when prompt resolution fails for non-agent / no-prompt keys). This is where list enrichment, AUTO/Run gates, and force-AUTO-off all read the boolean.
* `src/utils/config.py` — **unchanged unless needed** — `empty_render_for_prompts` already returns `empty_render: false` when no scored tokens are blank; only touch if the no-prompt policy must live in the helper rather than the api_admin soft-miss branch.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **unchanged** — already trusts `row.empty_render`; fixing the API boolean should clear the UI mute.

## Technical scope

* `src/ui/api/api_admin.py` — **modified function** `_evaluate_dispatch_empty_render`: on soft miss when `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts` cannot load prompts (no `agent_task`, etc.), return `{"empty_render": False, "empty_tokens": []}` instead of True — “no prompts or keys” means validation passes. Keep True only when prompts exist and the helper reports blank expected tokens (and re-check the no-`candidate_id` / candidate-missing branches against product intent for non-agent rows). Adjust `_candidate_dispatch_empty_render_error` messaging if it still says “could not validate prompts” for the no-prompt pass case.
* `src/utils/config.py` — only if plan-fix decides the default belongs in `empty_render_for_prompts` rather than the api_admin catch: document / enforce “no referenced scored tokens → not empty-render” (already the empty-list behavior).

## Notes for planning

Approved ancestor: AST-1766 (Dispatch Validation). Primary touch: `_evaluate_dispatch_empty_render` soft-miss paths in `api_admin.py` (AST-1780). Parent bug: AST-1790. Tests owned by sibling gap AST-1792 (Betty TESTS:REVISE); qa-fix skipped on this tip.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1790-default-validation-no-prompts`, child `sub/AST-1790/<this-id>-<slug>`.

### Comments

#### radia — 2026-09-25T01:18:13.431Z
[code-rubric] PROCEED (Commit: a29cbed6) ValueError soft-miss passes

#### joan — 2026-09-25T01:10:06.826Z
[board-joan]  CANON: OK

context_tokens≈18000

#### betty — 2026-09-25T01:09:14.843Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md (AST-1780) — missing coverage — no-prompt ValueError soft-miss → empty_render false (list/AUTO/Run); AST-1780 tests only monkeypatch eval

#### hedy — 2026-09-25T01:08:21.415Z
`origin/sub/AST-1790/AST-1791-default-validation-no-prompts` @ `56cbf159` · ValueError soft-miss passes

---

_Implementation detail may live in git history on `origin/dev`._
