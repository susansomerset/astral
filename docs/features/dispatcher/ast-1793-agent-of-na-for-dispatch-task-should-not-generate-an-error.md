# AST-1793 — Agent of n/a for dispatch task should not generate an error

<!-- linear-archive: AST-1793 archived 2026-10-02 -->

## Linear archive (AST-1793)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1793/agent-of-na-for-dispatch-task-should-not-generate-an-error  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

```
ui.api.api_admin: somerset | dispatch empty_render task_key='stage_email_meteorite' — agent_task 'stage_email_meteorite' has no agent_id assigned. Configure via Manage Tasks.; no prompts to validate, empty_render false
```

## As-is

List enrichment for mailbox / non-agent dispatch rows (e.g. `stage_email_meteorite`, agent n/a) correctly returns `empty_render: false` after AST-1791, but still emits a `logger.warning` that reads like an error: `agent_task '…' has no agent_id assigned. Configure via Manage Tasks.; no prompts to validate, empty_render false` — one noise line per candidate poll.

## To-be

When a dispatch task has no agent / no prompts to score (intentional n/a, not a misconfiguration), empty-render evaluation still passes (`empty_render: false`) and does **not** generate a warning or error log for that soft miss. Real fail paths (blank candidate, missing candidate, unexpected exception, blank expected tokens) keep their existing logs.

## Proposed steps

1. In `src/ui/api/api_admin.py` `_evaluate_dispatch_empty_render`, change the `ValueError` branch after `_dispatch_empty_render_prompt_texts` so the intentional no-prompt pass no longer calls `logger.warning` (keep the `{"empty_render": False, "empty_tokens": []}` return).
2. Leave blank/`candidate_id` miss and unexpected `Exception` branches on their current warning / exception logging.
3. Spot-check: refresh Scheduled Actions for somerset `stage_email_meteorite` — no empty-render warning spam; AUTO/Run still allowed for that row.

## Component scope

* `src/ui/api/api_admin.py` — **modified** — `_evaluate_dispatch_empty_render` ValueError soft-miss branch currently logs the “has no agent_id / no prompts to validate” warning that operators see as an error for intentional n/a agent tasks.
* `src/utils/config.py` — **unchanged** — `empty_render_for_prompts` and prompt-load policy are not the issue; logging is api_admin-only.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **unchanged** — UI already trusts `empty_render`; this bug is log noise, not a mute/boolean regression.

## Technical scope

* `src/ui/api/api_admin.py` — **modified function** `_evaluate_dispatch_empty_render`: on `ValueError` from `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts` (no `agent_task`, empty `agent_id`, missing agent), stop emitting `logger.warning` while still returning `empty_render: false`. Do not change the fail-closed branches or the successful `empty_render_for_prompts` path.

## Ancestor candidates

- [ ] AST-1791 — Default validation TRUE when no prompts/keys (fix) — Done; introduced this exact `logger.warning` text on the ValueError → `empty_render: false` pass (`api_admin.py`)
- [ ] AST-1790 — Default validation to TRUE where no prompts or keys are involved — Done mini-parent of AST-1791/1792; residual noise after that fix lane
- [ ] AST-1780 — List enrich, AUTO/Run gates, force AUTO off — Done; owns `_evaluate_dispatch_empty_render` in `api_admin.py`
- [ ] AST-1766 — Dispatch Validation — Done parent epic for empty-render AUTO/Run gating

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
