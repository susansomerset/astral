# AST-2000 — Runtime empty token is an error: no model call, entity to error_state (Tokens are unexpectedly empty)

<!-- linear-archive: AST-2000 archived 2026-10-13 -->

## Linear archive (AST-2000)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2000/runtime-empty-token-is-an-error-no-model-call-entity-to-error-state  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1986 — Tokens are unexpectedly empty.  
**Blocked by / blocks / related:** parent: AST-1986; blocks: AST-2006; blocks: AST-2005; related: AST-1987

### Description

## What this implements

Fix for [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986). At runtime, any token that resolves empty in a `do_task` prompt is an error: the prompt is not sent, one ERROR line names the task, entity and empty tokens, and the entity goes to the task's `error_state` (or stays at its input state with the claim released). It is never counted as "failed" and never detours through retry holding. The Manage Tasks token-count probe goes silent. As-is / To-be / Proposed steps / Susan's answered decisions live on the bug's Description.

## Citations

`astral.dispatch.entity-state-bound`, `astral.standards.in-scope-only` (from ancestor AST-1779).

## Scope

### Component scope

* `src/utils/config.py` — modified: `resolve_tokens` can collect empty tokens for the caller instead of only warning.
* `src/core/agent.py` — modified: `do_task` runs the runtime empty-token guard before the provider call; `resolved_task_system` passes the collector through.
* `src/core/consult.py` — modified: job dispatch / batch failure routing sends an empty-token failure to `error_state` (or the input state) instead of retry holding, and counts it as an error.
* `src/ui/api/api_admin.py` — modified: `_enrich_tasks` stops emitting empty-token warnings from its token-count probe.
* `src/core/roster.py`, `src/core/meteorite.py`, `src/core/candidate.py`, `src/core/contact.py`, `src/core/intake.py` — audited; changed only where `success: False` currently routes to a retry holding state or a "failed" outcome.

### Technical scope

* `src/utils/config.py` — modified function `resolve_tokens`: new optional keyword-only collector argument, appended per empty token across all sources; default behaviour unchanged.
* `src/core/agent.py` — modified functions `do_task` (collect, check, return failure with `empty_tokens` before the provider call) and `resolved_task_system` (keyword-only pass-through).
* `src/core/consult.py` — modified functions `_consult_batch_fail_dest` (or a sibling helper) and `_run_dispatch_chain_job_batch`: an empty-token result goes to `error_state`, or the input state when none is configured, with no retry holding and counted as an error.
* `src/ui/api/api_admin.py` — modified function `_enrich_tasks`: `warn_on_empty=False` on its probe resolves.
* Other `do_task` callers — modified only if their `success: False` branch sends the entity to retry holding or "failed".

## Boundaries

* Admin preview (`/api/admin/tasks/<task>/preview`) is unchanged: it still warns.
* No schema change.
* Not the Railway log fields work ([AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) owns that).

## Notes for planning

Approved ancestor: AST-1779 (`docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md`), which owns `empty_render_for_prompts` / `warn_on_empty`. Prior art for "empty token -> don't call the model": AST-530's `_mid_chain_empty_caller_tokens` in `src/core/agent.py`.

## Git branch (authoritative)

Mini-parent `ftr/AST-1986-runtime-empty-token-error`; this child `sub/AST-1986/AST-2000-runtime-empty-token-error`. Seeded by bug-fix.

### Comments

#### radia — 2026-10-06T05:43:24.221Z
[code-rubric] REVIEW (Commit: 4987dddc) AST-1995 spill; candidate retry edge

#### ada — 2026-10-06T05:41:32.515Z
`origin/sub/AST-1986/AST-2000-runtime-empty-token-error` @ `4987dddc` · lighter check (no qa-fix): py_compile OK on 7 files; touched-area component suites (test_config, test_agent*, test_candidate, test_consult, test_intake, test_roster, test_api_admin*) → 2241 passed / 157 failed, **identical failing set on pre-fix tree `2cfcf9e7`** (0 new, 0 fixed). For [AST-2006](https://linear.app/astralcareermatch/issue/AST-2006): `TestDoTask::test_mid_chain_empty_caller_skips_api` already fails pre-fix at hydration ("job not found: job-1"), before either guard — rewrite as planned.

#### joan — 2026-10-06T05:34:12.454Z
[board-joan]  CANON: OK

context_tokens≈28000

#### betty — 2026-10-06T05:33:47.091Z
[board-betty] TESTS: OK
Round 2. All test work sits in AST-2006 (blocked by AST-2000): new coverage + the TestDoTask::test_mid_chain_empty_caller_skips_api rewrite; AST-2000 touches no tests/ or bible. Revised routing only changes behavior when do_task returns empty_tokens, which no existing consult / roster / candidate / intake test sets, so nothing else breaks. Meteorite unchanged → no test owed. Note for AST-2006 (not a blocker here): my round-1 "_empty_token_fail_dest … → None" wording is superseded. The new contract is first non-retry error_state, else FAILED_TECHNICAL, mid-chain hop error_state first, never left at the hop label; plus the roster terminals ERROR_PREFILTER / ERROR_LOCATE_JOB_PAGE / COULD_NOT_PARSE_JOBLIST and candidate REQUESTED_*_ERROR. AST-2006 bible list should also add core/candidate.md + core/intake.md.

#### ada — 2026-10-06T05:32:49.263Z
`origin/sub/AST-1986/AST-2000-runtime-empty-token-error` @ `35d647d0916ec74f5692288224d501ac2f4f82c2` · straight to error_state

#### chuckles — 2026-10-06T05:21:21.386Z
[plan-discuss] Blocked on Susan's decision on [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986): either the empty-token routing follows `patt.task.dispatch-retry` (`_RETRY` first, then `error_state`, never stays in state), or that pattern gets a carve-out. When she answers, revise the `## Bug: AST-2000` routing to match, then return to Plan Ready for a fresh fix-board.

#### joan — 2026-10-06T05:20:52.739Z
[board-joan]  CANON: REVISE
What: patt.task.dispatch-retry — record AST-2000 carve-out (empty_tokens: skip _RETRY detour; input-state hold when error_state unset/retry-holding) — plan contradicts “always applies” + “failure never stays in state”

context_tokens≈24000

#### betty — 2026-10-06T05:20:10.043Z
[board-betty] TESTS: REVISE
What: no bible entry for a runtime empty-token guard (utils/config.md § AST-530 / AST-1779, core/agent.md, core/consult.md, core/roster.md, ui/api/api_admin.md) — missing coverage — none of the three repros (_enrich_tasks quiet probe; do_task no provider call + empty_tokens/empty_token_task + single ERROR; _run_batch_consult → error_state not retry_state) nor resolve_tokens empty_tokens collector, _empty_token_fail_dest (unset / retry-holding / same-state → None), the analysis_upshot / render_verdict / dispatch-chain / roster prefilter|select_job_page|parse_job_list / candidate requested-artifacts / intake total_errors routes has a test. Existing test to rewrite: core/agent TestDoTask::test_mid_chain_empty_caller_skips_api pins the deleted AST-530 _mid_chain_empty_caller_tokens contract (still passes on the CALLER_SYSTEM substring; rewrite to assert empty_tokens / empty_token_task + one ERROR). Shared _agent_rows fixture has no tokens, and resolve_tokens default-WARNING tests (TestResolveTokens, TestAst1779*) keep default args — no broad do_task fixture fallout expected.

#### ada — 2026-10-06T05:18:51.992Z
`origin/sub/AST-1986/AST-2000-runtime-empty-token-error` @ `062b2b634a590d18f9ba332fc37bae48444f994f` · empty-token guard planned

---

_Implementation detail may live in git history on `origin/dev`._
