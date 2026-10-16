# AST-1790 — Default validation to TRUE where no prompts or keys are involved

<!-- linear-archive: AST-1790 archived 2026-10-02 -->

## Linear archive (AST-1790)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1790/default-validation-to-true-where-no-prompts-or-keys-are-involved  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

non-agent tasks are now disabled because it doesn't have any tokens.  Only DISable if there are tokens EXPECTED that are MISSING.

## As-is

Scheduled Actions rows whose `task_key` has no `agent_task` / no prompt texts (non-agent dispatch tasks) are treated as `empty_render: true`. That mutes AUTO and Run/Sweep, and the API rejects AUTO-on / Run — even though nothing in the prompts expects a candidate token fill.

## To-be

Validation defaults to pass (`empty_render: false` / allow AUTO and Run) when there are **no prompts or keys involved**. Disable only when prompts **reference** candidate-scoped tokens that resolve empty for that row’s candidate (tokens expected and missing).

## Proposed steps

1. In `_evaluate_dispatch_empty_render` (`src/ui/api/api_admin.py`), stop treating “no agent_task / cannot load prompt texts” soft misses as `empty_render: true` — return `empty_render: false` (and empty `empty_tokens`) when there are no prompts to validate.
2. Keep the real fail path: when prompts load and `empty_render_for_prompts` finds candidate-scoped tokens that resolve to `""`, still return `empty_render: true`.
3. Leave UI (`AdminScheduledActions.tsx`) and the shared helper (`empty_render_for_prompts`) alone unless a caller still forces true for the no-prompt case after step 1.
4. Spot-check: a non-agent `dispatch_task` stays runnable; an agent task with a blank `{$FIRST_NAME}` (etc.) still disables.

## Component scope

* `src/ui/api/api_admin.py` — **modified** — `_evaluate_dispatch_empty_render` (and any soft-miss / “could not validate prompts” message path that currently forces `empty_render` true when prompt resolution fails for non-agent / no-prompt keys). This is where list enrichment, AUTO/Run gates, and force-AUTO-off all read the boolean.
* `src/utils/config.py` — **unchanged unless needed** — `empty_render_for_prompts` already returns `empty_render: false` when no scored tokens are blank; only touch if the no-prompt policy must live in the helper rather than the api_admin soft-miss branch.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **unchanged** — already trusts `row.empty_render`; fixing the API boolean should clear the UI mute.

## Technical scope

* `src/ui/api/api_admin.py` — **modified function** `_evaluate_dispatch_empty_render`: on soft miss when `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts` cannot load prompts (no `agent_task`, etc.), return `{"empty_render": False, "empty_tokens": []}` instead of True — “no prompts or keys” means validation passes. Keep True only when prompts exist and the helper reports blank expected tokens (and re-check the no-`candidate_id` / candidate-missing branches against product intent for non-agent rows). Adjust `_candidate_dispatch_empty_render_error` messaging if it still says “could not validate prompts” for the no-prompt pass case.
* `src/utils/config.py` — only if plan-fix decides the default belongs in `empty_render_for_prompts` rather than the api_admin catch: document / enforce “no referenced scored tokens → not empty-render” (already the empty-list behavior).

## Ancestor candidates

- [X] AST-1766 — Dispatch Validation (parent epic; Done) — introduced empty-render disable of AUTO/Run/Sweep
- [ ] AST-1780 — List enrich, AUTO/Run gates, force AUTO off — owns `_evaluate_dispatch_empty_render` soft-miss → `empty_render: true`
- [ ] AST-1779 — Empty-token predicate helper — owns `empty_render_for_prompts` (returns false when no blank scored tokens)
- [ ] AST-1782 — Scheduled Actions disable AUTO and Run/Sweep — UI mute that surfaces the bad boolean
- [ ] AST-1781 — Revalidate on agent_task / artifact version — same empty-render force-off path for version hooks

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
