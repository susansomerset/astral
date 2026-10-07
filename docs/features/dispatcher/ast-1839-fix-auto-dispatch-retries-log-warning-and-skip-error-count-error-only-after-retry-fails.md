# AST-1839 — fix: AUTO dispatch retries log WARNING and skip error count; error only after retry fails

<!-- linear-archive: AST-1839 archived 2026-10-07 -->

## Linear archive (AST-1839)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1839/fix-auto-dispatch-retries-log-warning-and-skip-error-count-error-only  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-1828 — [✅/Somerset] prefilter_company COMPLETED: 100 error(s) / 500 processed | prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf  
**Blocked by / blocks / related:** parent: AST-1828

### Description

## What this implements

AUTO dispatch failures that route an entity to a retry holding log WARNING and don't count toward the run's `total_errors`, so they no longer trigger the `auto_run_error` alert email. A failure out of that retry holding goes to the task's `error_state`, logs ERROR, counts as an error, and emails. For prefilter, parsing failures (hydrate/decode, missing id, `do_task` failure) first go to a new `HOMEPAGE_READY_RETRY` holding and then `ERROR_PREFILTER`. Agent-envelope failures (bad source content) go back to `WEBSITE_FOUND_RETRY` for `fetch_website` and still end in error on a repeat failure. The same retry-then-error rule applies to every AUTO dispatch task that already has a retry holding; no new holdings for tasks without one.

## Scope

## Component scope

* `src/core/roster.py` (modified): the prefilter batch failure paths pick the retry or error destination and log at the matching severity, and `prefilter_company_batch` reports its retried count.
* `src/core/consult.py` (modified): the `prefilter_company` branch of the dispatch-count conversion stops counting retried companies as `total_errors`.
* `src/utils/config.py` (modified): add the `HOMEPAGE_READY_RETRY` company state, route parsing failures from `HOMEPAGE_READY` to it, and add priors so the holding can reach pass/fail/error.
* `src/utils/logging.py` (modified): `log_llm_batch_summary` severity for provider errors.
* `src/core/agent.py` (modified, Susan 2026-09-28): `do_task` flags a rubric-encoded response whose `agent_performance.status` is `failure` as an agent-envelope failure instead of unwrapping it, so roster can send bad-source-content failures to `WEBSITE_FOUND_RETRY`.
* AUTO dispatch tasks that **already** have a retry holding — job consult/grade/upshot (`_consult_batch_fail_dest`), prefilter, `fetch_website`, `parse_job_list`, candidate craft chain (modified): retry-routed failures log WARNING and aren't counted as errors; failures out of the holding log ERROR and count. Their exact files are `plan-fix`'s call. No new retry holdings for tasks that don't have one (Susan 2026-09-28).

## Technical scope

* `src/core/roster.py`: modify `_transition_prefilter_batch_failures` (or its callers) so the log level is chosen from the destination (retry means WARNING, `error_state` means ERROR). Modify the `logger.exception` sites in `_run_batch_company_prefilter` to match. Modify the return dict of `_run_batch_company_prefilter` / `prefilter_company_batch` to carry a retried count. No new table.
* `src/core/consult.py`: modify the prefilter branch of the per-task summary conversion so retried companies are excluded from `total_errors`. Whether they get their own summary key is `plan-fix`'s call.
* `src/utils/config.py`: new `COMPANY_STATES` entry for the retry holding, and a modified `retry_state` on `HOMEPAGE_READY`, so routing matches the `{trigger}_RETRY` claim rule.
* `src/utils/logging.py`: modified function `log_llm_batch_summary`, provider-error level only.
* `src/core/agent.py`: modified function `do_task`. A rubric-encoded response with `agent_performance.status == "failure"` returns `success=False` plus an agent-failure flag. No new table or field.

## Boundaries

Product code only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). The `JO` / `JOB:<n>` decode bug is out of scope (Susan dropped it); `src/core/agent.py` is only in scope for the agent-envelope failure flag. No new retry holdings for AUTO tasks that don't already have one. Don't change alert email formatting in `src/core/monitor.py`, only what counts as an error.

## Notes for planning

Parent bug AST-1828's Description (As-is / To-be / Proposed steps 1–6, Open questions answered 2026-09-28) is authoritative. Susan approved the reading by reassigning. Scope-gate answers (Susan, 2026-09-28, on this ticket): (1) `src/core/agent.py` added to scope for the envelope-failure flag (Ada's option a); (2) only AUTO tasks that already have a retry holding. Tasks without one stay as they are, and there's no follow-up ticket. The counting approach (central re-read in `run_consult_task` vs per-function `retried` keys) is Ada's call. Ada estimated about 8 for this scope; children cap at 5, so confirm or flag it at Plan Ready. No ancestor box was checked, so there's no related-issue link. Feature doc to patch (Chuckles' best read, the top-ranked candidate): `docs/features/roster/ast-882-prefilter-one-retry-error.md`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1828-auto-retry-warn-then-error`, child `sub/AST-1828/AST-1839-auto-retry-warn-then-error`. Created at bug-fix.

### Comments

#### radia — 2026-09-28T19:32:12.488Z
[code-rubric] PROCEED (Commit: 36f385a2) Destination-based logging and retry counts. Clean: no fix-now or discuss items; the statute carve-out and test updates land on gap AST-1846.

#### ada — 2026-09-28T19:30:01.487Z
`origin/sub/AST-1828/AST-1839-auto-retry-warn-then-error` @ `36f385a2` · touched-area run: 19 new failures, all from the intended routing/count/severity change (for Betty on AST-1846). 267 others fail identically on the pre-fix tree (env/dev drift), not this change.

- `tests/component/core/test_candidate.py::TestAst972RequestedStageDispatch::test_artifacts_dispatch_retry_failure_errors`
- `tests/component/core/test_consult.py::TestAnalysisUpshotPrepAndBatch480::test_batch_company_missing_moves_to_retry`
- `tests/component/core/test_consult.py::TestAnalysisUpshotPrepAndBatch480ExtraBranches::test_batch_do_task_failure_transitions_error`
- `tests/component/core/test_consult.py::TestAnalysisUpshotPrepAndBatch480ExtraBranches::test_batch_missing_company_transitions_and_counts_error`
- `tests/component/core/test_consult.py::TestAst642PerEntityBatchRetry::test_analysis_upshot_primary_failure_to_retry_holding`
- `tests/component/core/test_roster.py::TestAst1155PrefilterIncompleteRetry::test_prefilter_company_incomplete_routes_to_website_found_retry`
- `tests/component/core/test_roster.py::TestAst702PrefilterBatchHelpers::test_prefilter_batch_fail_dest_from_homepage_ready`
- `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch::test_do_task_failure_transitions_batch`
- `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch::test_skips_not_ready_without_do_task`
- `tests/component/core/test_roster.py::TestAst882PrefilterOneRetryThenError::test_batch_do_task_failure_second_strike_to_error`
- `tests/component/core/test_roster.py::TestAst882PrefilterOneRetryThenError::test_not_ready_wfr_left_alone_for_fetch_website`
- `tests/component/core/test_roster.py::TestAst882PrefilterOneRetryThenError::test_prefilter_fail_first_strike_retries`
- `tests/component/core/test_roster.py::TestAst891ParseJobListBatch::test_passes_batch_session_and_counts_definite_outcomes`
- `tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal::test_prefilter_fail_ordinary_api_still_retries`
- `tests/component/utils/test_config.py::TestAst1807ImplicitRetryHelpers::test_state_prior_states_cross_base_feeders`
- `tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned`
- `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions`
- `tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig::test_prefilter_input_state_and_retry_on_homepage_ready`
- `tests/component/utils/test_logging_batch.py::TestLogLlmBatchSummary::test_empty_error_string_uses_error_path_not_healthy_summary`

#### joan — 2026-09-28T19:20:55.892Z
[board-joan]  CANON: REVISE

What: `stat.logging.error` + `stat.logging.warning` need a destination-based severity carve-out (retry holding → WARNING plus a debug traceback; terminal `error_state` → ERROR) and an amendment to Resolution §3's `log_llm_batch_summary` level. The canon patch goes to a sibling gap child (orphaned-bug board rule), not F3 inline.

#### betty — 2026-09-28T19:18:56.634Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md § AST-882 + utils/config.md + core/consult.md + utils/logging + core/agent.md + core/candidate.md — broken tests + missing repro coverage — `test_roster.py` hard-asserts HR→`WEBSITE_FOUND_RETRY` first strike (`_prefilter_batch_fail_dest` L2254, `TestAst882PrefilterOneRetryThenError` L2272, plus L6031/L6292) and `COMPANY_STATES`/transition asserts for HOMEPAGE_READY; no existing node covers the repro (HR→`HOMEPAGE_READY_RETRY`→`ERROR_PREFILTER`, envelope WFR-once via history, `retried` excluded from `total_errors`, WARNING-vs-ERROR by `retry_base(dest)`, `do_task` `agent_failure` flag, `parse_job_list_batch` retry/terminal counting, candidate `error_state` → `total_errors: 1`, `log_llm_batch_summary` WARNING level).

#### ada — 2026-09-28T19:17:54.276Z
`origin/sub/AST-1828/AST-1839-auto-retry-warn-then-error` @ `c8f4378e` · retry WARNING, second-strike ERROR

Confirm estimate: 8 (7 product files: agent, config, logging, roster prefilter+parse, consult batch/upshot/verdict, candidate). Over the 5 cap; not split per Susan.

#### chuckles — 2026-09-28T19:14:26.545Z
[check-linear] answered — scope amended on AST-1839 and AST-1828 (`src/core/agent.py` added for the envelope-failure flag; only AUTO tasks that already have a retry holding). Both assigned to Chuckles; AST-1839 resumes plan-fix from Plan Discuss.

#### susan — 2026-09-28T19:13:06.007Z
@chuckles Please incorporate my answers in the previous comment and reassign to yourself, then unblock the other ticket that is assigned to @susan.

#### susan — 2026-09-28T19:12:07.804Z
1. Add agent.py to the scope.
2. Don't add additional task retries that aren't already written.  Not worth the hassle at this time

#### ada — 2026-09-28T14:28:54.507Z
[scope-gate] @susan — AST-1839 plan-fix stopped before the doc patch. Two gaps; the plan can't be written without judgment calls until they're settled.

**1. Envelope failures need `src/core/agent.py` (not in scope).**
Scope covers `roster.py` / `consult.py` / `config.py` / `logging.py` + "every other AUTO dispatch task's failure-routing and summary-count code". prefilter_company is rubric-encoded (`output_type: grades_encoded_prefilter_links`), so `do_task` skips `_validate_response_schema` and unwraps `agent_payload` at `agent.py:2421`, dropping `agent_performance.status`. A model-reported "source content is the problem" failure is indistinguishable from a decode failure in roster, so answer 1's envelope → `WEBSITE_FOUND_RETRY` split can't be routed from in-scope files.
Options: (a) amend scope — `agent.py` `do_task`: rubric-encoded response with `agent_performance.status == "failure"` returns `success=False, agent_failure=True` (~6 lines); roster routes it to WFR, and a repeat envelope failure (state_history already has `HOMEPAGE_READY → WEBSITE_FOUND_RETRY`) goes to `ERROR_PREFILTER`. (b) roster re-parses `api_response` text itself (duplicates agent.py parsing). (c) drop the envelope path: every prefilter failure goes `HOMEPAGE_READY_RETRY → ERROR_PREFILTER`.

**2. "Every AUTO task retries, then errors" → well over 5 points.**
Only these have a retry holding today: job consult/grade/upshot (`_consult_batch_fail_dest`), prefilter, `fetch_website`, `parse_job_list`, candidate craft chain. No holding: `vet_inflow_discovery`, `inflow_resolve_website`, `resolve_website`, `recheck_no_openings` (stay put); `fetch_job_pages`, `fetch_jd`, `fetch_culture_pages`, `select_job_page`, `gaze` (straight to terminal); build-artifact soft failures + all cover-letter tasks (stay put, re-claimed every run, uncapped); inbox mailbox (never alerts). Giving each a `{trigger}_RETRY` holding + error state means new product states (some tasks have no `error_state` at all) — a materially different size, est. 13+.
Options: (a) this child = tasks that already have a holding (WARNING + uncounted on retry, ERROR + counted on second strike, prefilter loop fix), rest to a follow-up — est. 8; (b) all tasks here, 13+.

**Also open (my call if you'd rather not weigh in):** counting — central (`run_consult_task` re-reads claimed entities' states after the batch; anything in a `*_RETRY` state via `retry_base` = retried, not error; one helper, all tasks) vs per-function `retried` keys.

After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
