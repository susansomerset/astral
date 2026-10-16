# AST-1867 — fix: report provider balance refusal as one batch-level outage (held count, stop batch, clear alert, no breaker trip)

<!-- linear-archive: AST-1867 archived 2026-10-07 -->

## Linear archive (AST-1867)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1867/fix-report-provider-balance-refusal-as-one-batch-level-outage-held  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1860 — [✅/Somerset] select_job_page COMPLETED: 24 error(s) / 24 processed | select_job_page-9763cb58-c6d2-4441-a92a-59b49af4372d  
**Blocked by / blocks / related:** parent: AST-1860

### Description

## What this implements

When an LLM provider refuses calls for insufficient balance (HTTP 402, `failure_class=provider_balance_refusal`), a dispatch run reports one provider-level outage instead of N per-company errors. Held companies are counted as held, not errors. The batch stops issuing provider calls once a balance refusal comes back. The alert email's subject names the provider and "insufficient balance" and its body is short. The circuit breaker does not auto-disable the dispatch task over balance-refusal runs, so AUTO resumes on its own once credit is restored. The AST-897 / AST-1842 per-entity state hold is unchanged.

## Scope

## Component scope

* `src/core/roster.py` — modified: `run_company_task`'s `select_job_page` branch (and the JOBS_FOUND held branch) must stop counting a balance-held result as an error.
* `src/core/dispatcher.py` — modified: the batch loop / accumulated summary has to carry a balance-refusal flag, stop issuing calls once it's set, route the alert, and keep the run out of the circuit breaker.
* `src/core/monitor.py` — modified: needs a provider-outage alert (or a subject/body variant of `auto_run_error`) that names the provider and the cause.
* `src/utils/config.py` — modified (possibly): if the alert subject template or the breaker exclusion is configured rather than hard-coded, it goes in `PROVIDER_BALANCE_REFUSAL` or next to it.

## Technical scope

* `src/core/roster.py` — modified function: `run_company_task` returns a held count (new summary field) instead of an error count when the inner result has `state_held` or a balance-refusal `failure_class`, so held companies aren't reported as errors.
* `src/core/dispatcher.py` — modified functions: `_run_unified` (and its per-entity accumulator) records a batch-level balance-refusal marker and short-circuits the remaining entities. `_dispatch_one_body` uses that marker to pick the alert path. `_check_circuit_breaker` (or the ledger summary it reads) excludes balance-refusal runs from its zero-progress count, so AUTO isn't disabled over billing.
* `src/core/monitor.py` — new or modified function: a provider-balance alert (new function, or a branch in `auto_run_error`) whose subject leads with provider + "insufficient balance" and whose body is a short summary, not the full batch log.
* `src/utils/config.py` — new field(s), only if needed: alert subject wording and/or the breaker-exclusion switch, kept in config per the config-source-of-truth rule.

## Boundaries

Product code only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). Do not change the AST-897 / AST-1842 state-hold gates (`is_provider_balance_refusal` classification, `_find_job_page_from_assembled` held return, prefilter held return). No provider failover (out of scope per the bug). No new limits, caps, retries, or shortcuts beyond stopping the batch on a balance refusal.

## Notes for planning

Parent bug AST-1860's Description (As-is / To-be / Proposed steps) is authoritative. Susan approved it as written by reassigning, with no comments, so the proposed defaults answer the open questions: stop the batch after the first balance refusal, send a dedicated/clearer alert, and exclude balance-refusal runs from the circuit breaker. The AST-1858 / AST-1859 `prefilter_company` question was left unanswered: make the batch-level counting, short-circuit, alert, and breaker path generic in the dispatcher (task-agnostic, keyed on `state_held` / `failure_class`), but only touch roster call sites that are needed. Ancestor Susan checked: AST-897 (`docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md`), which is archived, so there's no related link. Related precedent on dev: AST-1839 (`36f385a2`, retry-routed failures skip `total_errors`), AST-1842 (select_job_page hold).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1860-provider-balance-outage`, child `sub/AST-1860/AST-1867-provider-balance-outage`. Created at bug-fix.

### Comments

#### radia — 2026-09-29T18:26:07.565Z
[code-rubric] PROCEED (Commit: 144b8850) plan-faithful outage path

#### ada — 2026-09-29T18:19:43.797Z
`origin/sub/AST-1860/AST-1867-provider-balance-outage` @ `144b8850` · lighter check (no qa-fix on this tip; no new push)

- `py_compile` roster/dispatcher/monitor: OK
- `pytest tests/component/core/test_{roster,dispatcher,monitor}.py`: 371 passed / 71 failed; 69 of those fail identically on `origin/dev` @ `fbe9486e` (host drift, e.g. `TestCircuitBreaker` arity, `TestAutoRunErrorSubjectPrefix`).
- Only tip-vs-dev delta: `TestAst897HoldStateOnBalanceRefusal::test_run_company_task_jobs_found_balance_{hold,failure_class}_skips_error_state` — expected; AST-1870 flips them to the held contract.

#### joan — 2026-09-29T18:08:51.769Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T18:08:36.565Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md (+ no bible entry for dispatcher/monitor outage path) — broken tests + missing coverage — `tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal::test_run_company_task_jobs_found_balance_hold_skips_error_state` and `::test_run_company_task_jobs_found_balance_failure_class_skips_error_state` assert `total_errors == 1` on a balance hold (fix §1b returns `total_held: 1`, `total_errors: 0`); no existing test covers the repro: select_job_page balance-hold counting (§1a), `_run_unified` skip-after-refusal / `_run_dispatch_loop` stop (§2c–2e), `_dispatch_one_body` INTERRUPTED + `provider_balance_outage` alert instead of `auto_run_error` and breaker skip (§2f), or new `monitor.provider_balance_outage` (§3). Regression guard needed: AST-1189 call-budget `state_held` (no failure_class) still counts `total_errors: 1` (D1).

#### ada — 2026-09-29T18:07:10.164Z
`origin/sub/AST-1860/AST-1867-provider-balance-outage` @ `718d9986` · one outage, stop, alert

---

_Implementation detail may live in git history on `origin/dev`._
