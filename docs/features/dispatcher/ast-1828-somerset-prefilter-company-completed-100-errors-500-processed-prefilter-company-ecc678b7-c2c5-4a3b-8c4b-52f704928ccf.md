# AST-1828 — [✅/Somerset] prefilter_company COMPLETED: 100 error(s) / 500 processed | prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf

<!-- linear-archive: AST-1828 archived 2026-10-07 -->

## Linear archive (AST-1828)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1828/somerset-prefilter-company-completed-100-errors-500-processed  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A Somerset `prefilter_company` AUTO run finished `COMPLETED` with 100 errors out of 500 companies. `monitor.auto_run_error` sent the alert email, which filed this ticket. Almost all of those "errors" were companies routed to **retry**, not companies that actually failed for good.

* **Why retries count as errors.** For prefilter, `src/core/consult.py` computes `total_errors = total − passed − failed − skipped` from the dict `roster.prefilter_company_batch` returns. Every company that `_transition_prefilter_batch_failures` sent to a retry state lands in that remainder. The dispatcher then fires `auto_run_error` whenever `total_errors > 0` (`src/core/dispatcher.py`).
* **Why retries log at ERROR.** The batch-level catch sites in `src/core/roster.py` `_run_batch_company_prefilter` (hydrate failure, per-company decode failure) use `logger.exception`. So do the generic LLM failure line in `src/utils/logging.py` `log_llm_batch_summary` (the DeepSeek `400 Content Exists Risk`) and the dispatcher's gather catch. All of them log ERROR even when the entity is simply retried.
* **Why "retry didn't fix it" is invisible today.** `_prefilter_batch_fail_dest` sends every `HOMEPAGE_READY` failure to `COMPANY_STATES["HOMEPAGE_READY"]["retry_state"]`, which is `WEBSITE_FOUND_RETRY`. Since [AST-1810](https://linear.app/astralcareermatch/issue/AST-1810/fetch-website-availclaim-skip-website-found-retry-rows-with-homepage), `fetch_website` re-scrapes every `WEBSITE_FOUND_RETRY` row back to `HOMEPAGE_READY`, so a second prefilter failure is treated as a first strike again. The company loops `HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY` → `HOMEPAGE_READY` and never reaches `ERROR_PREFILTER`. AST-1810's own review restates the pattern rule (`patt.task.dispatch-retry`): the retry for a trigger is `{trigger}_RETRY`, and `dispatch_claim_states("HOMEPAGE_READY")` already claims `HOMEPAGE_READY_RETRY`. But prefilter's failure routing still points at the cross-named `WEBSITE_FOUND_RETRY`.
* **This batch's specific trigger.** A whole batch failed hydrate with `No rubric criterion matching vector 'JO'`. The encoded-line decoder in `src/core/agent.py` strips colons before matching `_GRADE_SEG`, so a link meta field `JOB:1`–`JOB:5` decodes as a fake grade segment (vector `JO`, grade `B`). I confirmed this locally in round 1. A retry does not fix it reliably, because the model often emits the same single-index `JOB:n` again.

## To-be

Downgrade errors that result in retry to warning, only error in true error case. This is an example of a retry: the job usually works (it's set to auto), the whole batch needs a retry: warning.  Then, if retry didn't fix it: error.

## Proposed steps

1. **Severity follows destination.** Wherever the prefilter batch path routes entities to a retry state (hydrate failure, decode failure, `do_task` failure, missing id), log at WARNING. Log ERROR only when the destination is `error_state` (`ERROR_PREFILTER`).
2. **Retries are not errors in the run summary.** Have `prefilter_company_batch` report how many companies it sent to retry, and have the prefilter branch in `consult.py` count those as not-errors. A run where everything was only retried then finishes without tripping `auto_run_error`. Second-strike failures still count as errors and still email.
3. **Make "retry didn't fix it" reachable (Susan, question 1).** Split prefilter failures by cause:
   * **Parsing failures** (hydrate/decode errors such as this batch's `No rubric criterion matching vector 'JO'`, missing id, `do_task` failure): first strike goes to a new `HOMEPAGE_READY_RETRY` holding (the `{trigger}_RETRY` the claim side already expects, no re-scrape). A failure out of that holding goes to `ERROR_PREFILTER`. Same first-strike/second-strike shape as AST-882 / AST-1155.
   * **Agent-reported failure in its envelope** (the model says the source content is the problem): goes back to `WEBSITE_FOUND_RETRY` so `fetch_website` re-scrapes. That path still has to end in error on a repeat failure per step 6; `plan-fix` confirms it cannot loop `HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY` → `HOMEPAGE_READY` forever.
4. **The LLM provider refusal line** (`log_llm_batch_summary`) currently always logs ERROR. Downgrade it to WARNING per the To-be; the caller logs ERROR only when the entity lands in `error_state`.
5. **Dropped (Susan, question 3):** the `JO` / `JOB:<n>` decode fix in `src/core/agent.py` is out of scope.
6. **AUTO dispatch tasks that already have a retry holding (Susan, question 2, narrowed 2026-09-28).** Apply steps 1–3 to job consult/grade/upshot (`_consult_batch_fail_dest`), prefilter, `fetch_website`, `parse_job_list`, and the candidate craft chain. Retry-routed failures log WARNING and aren't counted; failures out of the holding go to `error_state`, log ERROR, and count. Tasks without a retry holding stay as they are.
7. **Envelope-failure flag in** `src/core/agent.py` **(Susan, 2026-09-28).** `do_task` reports a rubric-encoded `agent_performance.status == "failure"` as an agent failure, so roster can send it to `WEBSITE_FOUND_RETRY`.

## Open questions (for Susan)

None. All answered 2026-09-28:

1. **Second-strike routing:** parsing failures use `HOMEPAGE_READY_RETRY`, then `ERROR_PREFILTER`. Envelope failures (bad source content) go back to `WEBSITE_FOUND_RETRY` for `fetch_website`.
2. **Scope:** every dispatch task set to AUTO retries, then errors — narrowed on AST-1839's scope gate to tasks that already have a retry holding (no new holdings). `src/core/agent.py` added to scope for envelope detection.
3. `JO` **decode bug:** dropped.

## Component scope

* `src/core/roster.py` (modified): the prefilter batch failure paths pick the retry or error destination and log at the matching severity, and `prefilter_company_batch` reports its retried count.
* `src/core/consult.py` (modified): the `prefilter_company` branch of the dispatch-count conversion stops counting retried companies as `total_errors`.
* `src/utils/config.py` (modified): add the `HOMEPAGE_READY_RETRY` company state, route parsing failures from `HOMEPAGE_READY` to it, and add priors so the holding can reach pass/fail/error.
* `src/utils/logging.py` (modified): `log_llm_batch_summary` severity for provider errors.
* `src/core/agent.py` (modified, Susan 2026-09-28): `do_task` flags a rubric-encoded response whose `agent_performance.status` is `failure` as an agent-envelope failure instead of unwrapping it, so roster can send bad-source-content failures to `WEBSITE_FOUND_RETRY`.
* AUTO dispatch tasks that **already** have a retry holding — job consult/grade/upshot (`_consult_batch_fail_dest`), prefilter, `fetch_website`, `parse_job_list`, candidate craft chain (modified): retry-routed failures log WARNING and aren't counted as errors; failures out of the holding log ERROR and count. Their exact files are `plan-fix`'s call. No new retry holdings for tasks that don't have one (Susan 2026-09-28).

## oiTechnical scope

* `src/core/roster.py`: modify `_transition_prefilter_batch_failures` (or its callers) so the log level is chosen from the destination (retry means WARNING, `error_state` means ERROR). Modify the `logger.exception` sites in `_run_batch_company_prefilter` to match. Modify the return dict of `_run_batch_company_prefilter` / `prefilter_company_batch` to carry a retried count. No new table.
* `src/core/consult.py`: modify the prefilter branch of the per-task summary conversion so retried companies are excluded from `total_errors`. Whether they get their own summary key is `plan-fix`'s call.
* `src/utils/config.py`: new `COMPANY_STATES` entry for the retry holding, and a modified `retry_state` on `HOMEPAGE_READY`, so routing matches the `{trigger}_RETRY` claim rule.
* `src/utils/logging.py`: modified function `log_llm_batch_summary`, provider-error level only.
* `src/core/agent.py`: modified function `do_task`. A rubric-encoded response with `agent_performance.status == "failure"` returns `success=False` plus an agent-failure flag. No new table or field.

## Ancestor candidates

- [ ] AST-882: prefilter one retry, then error (`docs/features/roster/ast-882-prefilter-one-retry-error.md`). Designed exactly the "retry once, then error" behavior for prefilter that the To-be asks for.
- [ ] AST-1810: fetch_website scrapes every `WEBSITE_FOUND_RETRY` row and drops the AST-892 second-strike split (commit `d7af2340`; review doc `docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md`). Removed the only thing that let prefilter tell a second strike from a first.
- [ ] AST-641: union claim and count for primary + retry trigger states (`docs/features/dispatcher/ast-641-union-claim-and-count-for-primary-retry-trigger-states-auto-retry.md`). Owns the `{trigger}_RETRY` claim rule (`HOMEPAGE_READY` → `HOMEPAGE_READY_RETRY`) that prefilter routing no longer matches.
- [ ] AST-344: error alerts (`docs/features/monitor/ast-344-error-alerts.md`). Defined the AUTO-run `total_errors > 0` alert email that filed this ticket.
- [ ] AST-1155: incomplete grades go to a retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`). Precedent for first strike to holding, second strike to error, applied to job consult.
- [ ] AST-892: stop fetch_website reclaim of prefilter second-strike companies (`docs/features/roster/ast-892-stop-fetch-website-prefilter-second-strike-reclaim.md`). The original second-strike design that [AST-1810](https://linear.app/astralcareermatch/issue/AST-1810/fetch-website-availclaim-skip-website-found-retry-rows-with-homepage) removed.
- [ ] AST-697: prefilter link-set schema and bracket decode (`docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md`). Only relevant if the `JO` decode fix stays in scope; it added the `JOB:`/`CULT:` prefixes.
- [ ] AST-483: normalize grades segment whitespace in agent decode (`docs/features/boards/ast-483-normalize-grades-segment-whitespace-in-agent-decode.md`). Same `JO`-only caveat; it added the colon strip.

## Original report

2026-09-28 05:30:21  \[INFO\]  softwarefinder_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:21  \[INFO\]  builtinboston_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:21  \[INFO\]  pasadena_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:21  \[INFO\]  nchimss_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:21  \[INFO\]  somerset | dispatch company starting
 prefilter_company — 616 available (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  withvector_io | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  jobs_firstcitizens_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  builtin_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  remotivated_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  linear_health | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  healthcare_digital | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:25  \[INFO\]  ir_phreesia_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  slack_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  careers_amtrak_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  nodesk_co | company state: HOMEPAGE_READY
 -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  technicaltalentgroup_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  careers_quantumscape_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  careers_redpoint_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  remotefirstjobs_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:26  \[INFO\]  python_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:28  \[INFO\]  builtinaustin_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:28  \[INFO\]  theladders_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:28  \[INFO\]  workingnomads_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:28  \[INFO\]  hiringcafe_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:28  \[INFO\]  jobs_massdigitalhealth_org | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:28  \[INFO\]  remotefront_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  nestlejobs_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  bwxt_com | company state: HOMEPAGE_READY
 -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  umassmed_edu | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  jobs_bd_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  yespress_io | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  careers_bixal_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  careers_ford_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  cloudflare_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  spinwheelio_applytojob_com | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  careers_microsoft_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  jobs_boeing_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  careers_agfa_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  tildavps_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  formula5_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  careers_onpay_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  netsafesolutions_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:29  \[INFO\]  remotesource_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:30  \[INFO\]  openmedscience_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:30  \[INFO\]  mindbowser_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:30  \[INFO\]  workcare_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:30  \[INFO\]  jobs_myflorida_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:30  \[INFO\]  ir_pavmed_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:30:30  \[INFO\]  ir_heartbeam_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:39:42  \[INFO\]  access2hc_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:39:42  \[INFO\]  africannewspage_net | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:07  \[ERROR\]  Task was destroyed but it is pending!
 task: <Task pending name='Task-93' coro=<to_thread() running at
 /root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
 wait_for=<Future pending
 cb=\[\_chain_future.<locals>.\_call_check_cancel() at
 /root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
 Task.task_wakeup()\]>>
 2026-09-28 05:41:12  \[INFO\]  dwinsoft_in | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  apideck_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  support_employeenavigator_com | company
 state: HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  developer_atlassian_com_2 | company
 state: HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  seeburger_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  stripe_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  syndelltech_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  plansource_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  informsoftware_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  evidencemd_ai | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  morningstar_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  highmark_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  key_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  gethealthy_uams_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  moffitt_org | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  porh_psu_edu | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  austinregionalclinic_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  my_clevelandclinic_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  globalmed_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  nyuhs_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  healthpointchc_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  about_kaiserpermanente_org | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  nestle_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  nychealthandhospitals_org | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  crosscountry_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  d300_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  simitreehc_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  jobs_onvidahealth_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  slb_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  jobs_gainwelltechnologies_com | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  precisionformedicine_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  legendbiotech_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  mercy_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  ekohealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  nsightcare_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  uclahealthcareers_org_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:12  \[INFO\]  careers_soundphysicians_com | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  infineon_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  quad_com | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  support_apple_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  calix_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  iot_vodafone_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  nordicsemi_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  pcloudy_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  kiwiqa_io | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  developer_paypal_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  docs_customer_io | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  camel_apache_org | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  idpal_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:41:54  \[INFO\]  ndis_gov_au_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  continuumcloud_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  charityengine_net | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  moncrief_tricare_mil | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  isedisde_canada_ca | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  amaassn_org_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  cdphe_colorado_gov | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  merative_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  multco_us | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  behavehealth_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  michigan_gov_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  therapservices_net | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  icanotes_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  mychci_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  lrsoutputmanagement_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  creditforstartups_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  cdw_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  spacex_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  cordis_europa_eu | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  upguard_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  inl_gov_2 | company state: HOMEPAGE_READY
 -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  cisecurity_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  velotic_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  about_att_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  omdia_tech_informa_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  docs_oracle_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  techlynxrecruiters_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  excellentwebworld_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  digital_nhs_uk | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  gnosisfreight_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  cdp_com_3 | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  experienceleague_adobe_com_3 | company
 state: HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  docs_digicert_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  docs_cyberark_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  developers_google_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  developer_sophos_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  unipile_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  docs_sophos_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:01  \[INFO\]  miniorange_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  data_hrsa_gov | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  azahcccs_gov | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  harpercollege_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  balladhealth_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  its_uky_edu | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  aphis_usda_gov | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  ipm_ucanr_edu | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  drchrono_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  uit_stanford_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  dph_sc_gov | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  unric_org | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:42:44  \[INFO\]  mbc_ca_gov_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  thealliance_health | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  gurucul_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  alchemytechgroup_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  techcaliber_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  sas_com_3 | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  amplix_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  varcio_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  spendhound_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  doit_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  turbo360_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  uoflhealth_org_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  aramark_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  bosch_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  childrenshospital_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  moveupstatesc_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  veeva_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  pharmacytimes_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  new_diehl_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  cochrane_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  jjc_edu | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  siteminder_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  healthmeasures_net | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  lseg_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  help_headway_co | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  oracle_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  lenovopress_lenovo_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  cisa_gov_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  help_simcapture_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  duo_com_2 | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  atlas_heart_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  ypsomed_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  ofac_treasury_gov_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  unops_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  digitalstrategy_ec_europa_eu_2 | company
 state: HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  tatacommunications_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  extremenetworks_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  active_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  group_dhl_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  itu_int | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  developer_apple_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  flolive_net | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  nalanetworks_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  docs_confluent_io | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  levelpath_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  resedagroup_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  mhclgdigital_blog_gov_uk | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  workato_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  boomi_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:04  \[INFO\]  alterahealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:32  \[ERROR\]  Fatal error on SSL protocol
 protocol: <asyncio.sslproto.SSLProtocol object at 0x7fa7ece8bd40>
 transport: <\_SelectorSocketTransport closing fd=16>
 Traceback (most recent call last):
   File "/opt/venv/lib/python3.12/site-packages/asyncpg/pool.py", line
 239, in release
     await self.\_con.reset(timeout=budget)
   File "/opt/venv/lib/python3.12/site-packages/asyncpg/connection.py",
 line 1571, in reset
     await self.execute(reset_query)
   File "/opt/venv/lib/python3.12/site-packages/asyncpg/connection.py",
 line 354, in execute
     result = await self.\_protocol.query(query, timeout)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "asyncpg/protocol/protocol.pyx", line 358, in query
   File "asyncpg/protocol/protocol.pyx", line 713, in
 asyncpg.protocol.protocol.BaseProtocol.\_get_timeout
   File "asyncpg/protocol/protocol.pyx", line 717, in
 asyncpg.protocol.protocol.BaseProtocol.\_get_timeout_impl
 AttributeError: 'NoneType' object has no attribute '\_config'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
   File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
 line 1075, in write
     n = self.\_sock.send(data)
         ^^^^^^^^^^^^^^^^^^^^^
 OSError: \[Errno 9\] Bad file descriptor

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
   File "/root/.nix-profile/lib/python3.12/asyncio/sslproto.py", line
 694, in \_write_appdata
     self.\_do_write()
   File "/root/.nix-profile/lib/python3.12/asyncio/sslproto.py", line
 713, in \_do_write
     self.\_process_outgoing()
   File "/root/.nix-profile/lib/python3.12/asyncio/sslproto.py", line
 719, in \_process_outgoing
     self.\_transport.write(data)
   File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
 line 1081, in write
     self.\_fatal_error(exc, 'Fatal write error on socket transport')
   File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
 line 894, in \_fatal_error
     self.\_force_close(exc)
   File "/root/.nix-profile/lib/python3.12/asyncio/selector_events.py",
 line 906, in \_force_close
     self.\_loop.call_soon(self.\_call_connection_lost, exc)
   File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py",
 line 795, in call_soon
     self.\_check_closed()
   File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py",
 line 541, in \_check_closed
     raise RuntimeError('Event loop is closed')
 RuntimeError: Event loop is closed
 2026-09-28 05:43:32  \[ERROR\]  Task was destroyed but it is pending!
 task: <Task cancelling name='telescope-result-poller'
 coro=<\_TelescopeQueue.\_poll_loop() running at
 /app/src/external/telescope.py:297> wait_for=<Future cancelled>>
 2026-09-28 05:43:32  \[WARNING\]  telescope result poll failed:
 RuntimeError: coroutine ignored GeneratorExit
 2026-09-28 05:43:32  \[ERROR\]  Task was destroyed but it is pending!
 task: <Task pending name='telescope-result-poller'
 coro=<\_TelescopeQueue.\_poll_loop() running at
 /app/src/external/telescope.py:305> wait_for=<Future finished
 result=\[<Record oid=2...ype_name=None>, <Record
 oid=2...ype_name=None>\]>>
 2026-09-28 05:43:32  \[INFO\]  psrspeers_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  hikvision_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  raleighnc_gov_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  odh_ohio_gov | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  schneider_im | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  optit_in | company state: HOMEPAGE_READY
 -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  axattechnologies_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  acquia_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:43:57  \[INFO\]  flentas_blog | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  pfizer_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  m42_ae | company state: HOMEPAGE_READY ->
 PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  radiant_digital | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  natlawreview_com_4 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  cubuffs_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  triblive_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  calendar_unt_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  pagerhealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  tv_dartconnect_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  dentgents_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  about_roblox_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  zatca_gov_sa_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  nascar_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  nps_gov | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  cyclones_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  quins_co_uk | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  commonwealthcarealliance_org | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  cbp_gov_3 | company state: HOMEPAGE_READY
 -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  datavant_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  fcbarcelona_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  encoura_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  availity_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  insiderone_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  vitalitygroup_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  riotgames_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  icariohealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  allianz_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  angelashouse_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  brookings_edu_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  edhub_amaassn_org_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  maine_gov | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  info_montgomerycollege_edu | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  acany_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  goldcoasthealthplan_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  co_columbia_wi_us | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  healthcare_ascension_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  it_wisc_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  agrilifeextension_tamu_edu | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  featurebase_app_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  ssga_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  alaska_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:26  \[INFO\]  nola_gov_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  teamrecovery_io | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  epic_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  cliniconex_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  instem_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  blocksurvey_io_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  origamirisk_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  greenlight_guru_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  aigendigitalmarketing_net | company
 state: HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  disneyworld_disney_go_com | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  goarmywestpoint_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  usab_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  store_steampowered_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:44:58  \[INFO\]  magnite_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  techrev_us_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  mainms_org | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  orionhealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  emrsystems_net | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  payzen_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  healthcarefinancenews_com | company
 state: HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:08  \[INFO\]  thoroughcare_net | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  edb_gov_sg | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  ediblehudsonvalley_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  arsenal_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  support_google_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  bowl_com | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  support_kahoot_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  koohne_nc | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  fcbayern_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  circasports_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  buffalobills_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  pechanga_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[ERROR\]
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf | company
 prefilter hydrate
   ValueError: No rubric criterion matching vector 'JO'
   Continuing without this batch's grades
 Traceback (most recent call last):
   File "/app/src/core/roster.py", line 1984, in \_run_batch_company_prefilter
     \_hydrate_response_jobs_grade_reasons(response_companies, rubric_list)
   File "/app/src/core/consult.py", line 345, in
 \_hydrate_response_jobs_grade_reasons
     \_hydrate_grade_reasons_from_rubric(glist, rubric_criteria)
   File "/app/src/core/consult.py", line 309, in
 \_hydrate_grade_reasons_from_rubric
     g\["reason"\] = \_lookup_rubric_reason_for_grade(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   File "/app/src/core/consult.py", line 285, in \_lookup_rubric_reason_for_grade
     raise ValueError(f"No rubric criterion matching vector {vector_label!r}")
 ValueError: No rubric criterion matching vector 'JO'
 2026-09-28 05:46:09  \[ERROR\]  Task was destroyed but it is pending!
 task: <Task pending name='Task-925' coro=<to_thread() running at
 /root/.nix-profile/lib/python3.12/asyncio/threads.py:25>
 wait_for=<Future pending
 cb=\[\_chain_future.<locals>.\_call_check_cancel() at
 /root/.nix-profile/lib/python3.12/asyncio/futures.py:391,
 Task.task_wakeup()\]>>
 2026-09-28 05:46:09  \[INFO\]  pulse2_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  wantapply_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  remotejobs_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  delegatedai_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  temporal_io_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  atlantsecurity_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  technologyadvice_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  kpmguscareers_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  asitechco_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  phsa_ca | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  mountsinai_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  careers_franciscopartners_com_2 | company
 state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  pcisgold_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  signifyhealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  stc_com_sa | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  pharmexec_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  seqster_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  mend_com | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  fda_gov_4 | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  careers_abbvie_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  smu_edu | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  magnoliatribune_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  ohiopharmacists_org | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  medstarhealth_org_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  commure_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  physitrack_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  ysph_yale_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  cancercare_siemenshealthineers_com |
 company state: HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  trialx_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:09  \[INFO\]  globes_co_il | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  jobs_a16z_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  coloradosun_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  careers_jackhenry_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  geekwire_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  talener_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  unr_edu | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  healthflexxinc_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  clarrio_ai | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  publichealth_uic_edu | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  escardio_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  einstein_br | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  invonto_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  dreameyedigital_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  cadmusgroup_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  citrincooperman_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  moh_gov_sa | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  icthealth_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  connectedmhealth_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  jobs_siemensenergy_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  careers_astrazeneca_com_2 | company
 state: HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  jobs_walgreens_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  latenthealth_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  healthcareitleaders_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  camcatbooks_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  oneviewhealthcare_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  renascence_io | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  kansasworks_jobs | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  manufacturingusa_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  marketresearchfuture_com_2 | company
 state: HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  box_com | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  tvbrics_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  elevancesystems_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  cityofhopejobs_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  albanymed_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  worldhealthsummit_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  exhibition_skoch_in | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  verdantix_com_3 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  ximivogue_com_uy | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:36  \[INFO\]  insurancebusinessmag_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  milbank_org | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  capminds_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  ll_mit_edu | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  pophive_org | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  news_research_gatech_edu | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  ukri_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  guides_lib_umich_edu | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  uab_edu | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  research_google_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  cepi_net | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  fsis_usda_gov | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  thryve_health | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  gtri_gatech_edu | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  preciseanalytics_io | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:42  \[INFO\]  astho_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  arkenea_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  prezent_ai | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  codeflamme_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  allstartech_net_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  intuz_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  eliemakodakowo_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  planmysaas_com_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  mintmedical_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  nationsbenefits_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  publichealthontario_ca | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  thenai_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:46:43  \[INFO\]  bennett_ox_ac_uk | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  irvinetechcorp_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  hiring_lat | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  connectitco_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  aistartupjobs_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  aihcassn_org_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  dezyit_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  multiples_vc_2 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  menafn_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  aventrexdigital_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  systematic_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  newlantern_ai | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  lety_ai | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  plura_ai | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  casemed_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  penguinai_co | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  omegahms_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  pryvatenow_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  gehealthcare_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  accountablehq_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  cloudmotiv_ai | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  pronttera_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  hospitalhealth_com_au | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:17  \[INFO\]  revcycleai_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  veradigm_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  topconhealthcare_eu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  aol_com_2 | company state: HOMEPAGE_READY
 -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  qtimaging_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  magnetgroup_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  hipaavault_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  element34_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  dhis2_org | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  careers_greatersatx_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  research_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  health_vic_gov_au | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  brezq_com | company state: HOMEPAGE_READY
 -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  healthdataplatformbc_ca | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  stockstory_org | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  publichealth_pitt_edu | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  browse_welch_jhmi_edu | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  logicplanet_com | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  iqvia_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  lexisnexis_com_3 | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  pivotpointconsulting_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  bowergroupasia_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  insigniacap_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  inetum_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  forbes_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  amentum_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  mendonma_gov | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:30  \[INFO\]  3m_com | company state: HOMEPAGE_READY ->
 PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  covestro_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  apollo_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  jobs_xcelenergy_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  4dayweek_io | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  sentant_net | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  jobs_mmc_vc | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  autonews_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  jobs_svangel_com_2 | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  chillipharm_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  softwarefluxsolution_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  agfahealthcare_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  gomohealth_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  gasimo_org | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  codespaceinfotech_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  jobs_ashbyhq_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  oneskai_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  zyenova_co_zw | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  ca_indeed_com_3 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  textcontrol_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  simple_health | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  starwindsoftware_com | company state:
 HOMEPAGE_READY -> NO_PREFILTER_JOBLISTS (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  blackduck_com | company state:
 HOMEPAGE_READY -> PREFILTER_PASSED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:45  \[INFO\]  remotejobs_org_2 | company state:
 HOMEPAGE_READY -> PREFILTER_FAILED (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  delphyr_ai | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  stocktitan_net_4 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  knack_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  mayoclinic_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  events_weill_cornell_edu | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  littleonline_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  nysna_org | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  polyu_edu_hk | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  faspsych_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  pmcky_org | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  scripps_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  baptisthealth_net | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  stmarys_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  familiestogetheroc_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  mediproducts_net | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  marybridge_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  adventisthealthcare_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  us_milliman_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  zmedsolutions_net | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  zeeyes_ai | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  oumahealth_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  health2conf_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  fortunesoftit_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  dialoghealth_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  eclinicalworks_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  jobs_northwell_edu | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  multicare_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  athenahealth_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  appinventiv_com_3 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  meddra_org | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  solvefy_io | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  zonsource_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  greensighter_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  mobiletheatre_co_za | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  devcom_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  enlightlab_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  ezovion_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[INFO\]  blog_bluebin_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:47:59  \[ERROR\]  LLM deepseek task=prefilter_company 1.2s
 error=Error code: 400 - {'error': {'message': 'Content Exists Risk
 (request_id: 8d66aaf6-438f-40a3-b6dd-d4983d2d0ce6)', 'type':
 'invalid_request_error', 'param': None, 'code':
 'invalid_request_error'}}
 2026-09-28 05:48:00  \[INFO\]  somerset | dispatch company task
 completed: prefilter_company pass:246 fail:154 error:100 (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  prognocis_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  medidata_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  oneadvanced_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  foreseemed_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  instalogic_ae | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  gardner_law | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  ncc_co_ug | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  ailabtech_com_sg | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  purpleskyhealth_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  omnimd_com_2 | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  cliniko_com | company state:
 HOMEPAGE_READY -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)
 2026-09-28 05:48:00  \[INFO\]  vibe_us | company state: HOMEPAGE_READY
 -> WEBSITE_FOUND_RETRY (batch:
 prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf)

### Comments

#### chuckles — 2026-09-28T14:29:18.343Z
@susan AST-1839 is at Plan Discuss. Ada's [scope-gate] needs two calls from you: (1) spotting a model-reported "bad source content" failure needs `src/core/agent.py` — add it to scope (about 6 lines), have roster re-parse the response itself, or drop that path so every prefilter failure goes `HOMEPAGE_READY_RETRY` → `ERROR_PREFILTER`; (2) covering every AUTO task is about 13+ points — keep this child to the tasks that already have a retry state (about 8 points, the rest to a follow-up), or do them all here. Answer on AST-1839, then assign AST-1828 back to Chuckles and I'll amend the scope and restart plan-fix.

#### chuckles — 2026-09-28T14:12:32.351Z
[check-linear] Discussion — Description updated with all three answers (parsing failures to `HOMEPAGE_READY_RETRY` then `ERROR_PREFILTER`, envelope failures to `WEBSITE_FOUND_RETRY`, every AUTO task, `JO` fix dropped); Open questions empty — to continue, assign to Chuckles (@susan)

#### susan — 2026-09-28T14:11:26.597Z
@chuckles i answered the open qs in comment. Could you update the description to reflect my clarifications?

#### susan — 2026-09-28T14:10:38.610Z
Oq 3: drop it.

#### susan — 2026-09-28T14:08:30.882Z
Oq1: yes, homepage_ready_retry should be a used on parsing issues like this. If the agent responded with a failure in its envelope, the issue is with the source content and should get kicked back to the retry for fetch website.

#### chuckles — 2026-09-28T14:02:20.002Z
[check-linear] answered — scope widened to every AUTO dispatch task (retry, then error; Proposed step 6); questions 1 (second-strike routing) and 3 (`JO` decode) still open — to continue, assign to Chuckles (@susan)

#### susan — 2026-09-28T14:01:34.945Z
@chuckles all dispatch tasks set to auto should retry then error

---

_Implementation detail may live in git history on `origin/dev`._
