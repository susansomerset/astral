# AST-1860 — [✅/Somerset] select_job_page COMPLETED: 24 error(s) / 24 processed | select_job_page-9763cb58-c6d2-4441-a92a-59b49af4372d

<!-- linear-archive: AST-1860 archived 2026-10-07 -->

## Linear archive (AST-1860)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1860/somerset-select-job-page-completed-24-errors-24-processed-select-job  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

DeepSeek refused every `select_job_page` call in batch `select_job_page-9763cb58-…` with HTTP 402 "Insufficient Balance". The AST-897 / AST-1842 state hold did its job: `_find_job_page_from_assembled` in `src/core/roster.py` kept every company in `PJL_READY`, so nothing drained into `NO_JOBLIST`. What's still broken is the batch-level handling:

* **Each refusal counts as a per-company error.** `run_company_task`'s `select_job_page` branch sees `result["error"]` and returns `total_errors: 1` (with a `_warn_company` line) for all 24 companies, the same as a real per-company failure. The run rolls up as `pass:0 fail:0 error:24`.
* **The alert email doesn't say what happened.** `src/core/monitor.py` `auto_run_error` sends the subject `[✅/Somerset] select_job_page COMPLETED: 24 error(s) / 24 processed` (the `✅` is the deploy label, not a success marker) with a 48-line log dump. There's no headline saying "DeepSeek is out of credit". You have to read the body to learn it's a billing outage rather than 24 broken companies.
* **Every call still goes out.** The whole batch fires, and every 402 is logged twice (once as `LLM deepseek … error=` and once as `<company> -> - [...]`).
* **The circuit breaker will fire.** `src/core/dispatcher.py` `_check_circuit_breaker` auto-disables a dispatch task after 3 consecutive runs with 0 passed and 0 failed. Balance-refusal runs are exactly that shape, so an unpaid provider silently turns off the AUTO task. It stays off after credit is restored, until someone re-enables it by hand.

## To-be

A provider balance refusal is reported as one clear, provider-level outage, not as N company errors. The alert names the provider and the cause ("DeepSeek: insufficient balance") in the subject line. Held companies are not counted as errors. The batch stops sending calls once the provider has refused for balance. The circuit breaker does not auto-disable a task because of balance refusals, so AUTO resumes on its own once credit is back. The AST-897 state hold stays exactly as it is.

## Proposed steps

1. In `run_company_task`'s `select_job_page` branch (and the equivalent held paths), return a distinct `total_held` count (or equivalent) instead of `total_errors: 1` when `result.get("state_held")` / `is_provider_balance_refusal(result)`, and skip the per-company `_warn_company`.
2. Carry a batch-level `provider_balance_refusal` flag (provider + first error text) up through `_run_unified`'s accumulated summary. Once it's set, skip the remaining entities in the batch instead of issuing more calls.
3. In `_dispatch_one_body`, when that flag is set: send a dedicated alert through `monitor.py` whose subject leads with the provider and "insufficient balance", with a short body (not the full per-company dump). Exclude the run from `_check_circuit_breaker`'s zero-progress count.
4. Leave the AST-897 / AST-1842 state-hold gates untouched.

**Open product questions for Susan (these are why this is at Discussion, not Todo):**

* Should the batch stop after the first 402 (as proposed), or keep calling every entity as it does today?
* Should a balance outage get its own alert email, or just a better subject line on the existing `auto_run_error` email?
* Should the circuit breaker ignore balance-refusal runs (as proposed), or is auto-disable the behavior you want while the provider is unpaid?
* [AST-1858](https://linear.app/astralcareermatch/issue/AST-1858/abrams-prefilter-company-completed-500-errors-500-processed-prefilter) and [AST-1859](https://linear.app/astralcareermatch/issue/AST-1859/somerset-prefilter-company-completed-16-errors-16-processed-prefilter) (`prefilter_company`, 500/500 and 16/16 errors, same time window) look like the same DeepSeek outage on a different task. Should this fix cover the batch-counting and alert path for every task (prefilter's held return in `roster.py` already sets `state_held`), or stay limited to `select_job_page`?
* Out of scope unless you say otherwise: automatic failover to Anthropic when DeepSeek refuses for balance (no failover exists today).

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

## Ancestor candidates

- [X] AST-897 — Hold entity state on provider balance refusal (`docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md`). Owns the 402 classification and state hold this bug builds on. It handled per-entity state, not batch counting or alerting.
- [ ] [AST-1842](https://linear.app/astralcareermatch/issue/AST-1842/fix-agent-data-writes-off-event-loop-sqlite-lock-hardening-select-job) — `select_job_page` state hold on balance refusal / provider timeout (cited in the `src/core/roster.py` `_find_job_page_from_assembled` comment). Extended the AST-897 hold to `select_job_page` specifically.
- [ ] AST-1189 — Provider call budget / timeout failure class (`docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md`). Sibling failure class that uses the same hold gate. Relevant only if the fix should also cover timeouts.
- [ ] no ancestor candidate found

---

## Original report

```
2026-09-29 17:54:56  [INFO]  somerset | dispatch company starting
select_job_page — 24 available (batch: select_job_page-9763cb58-c6d2-4441-a92a-59b49af4372d)
2026-09-29 17:55:30  [WARNING]  LLM deepseek task=select_job_page 0.9s error=Error code: 402 - {'error': {'message': 'Insufficient Balance (request_id: 801dc3e8-72ef-4e12-9d54-3785a46348f6)', 'type': 'unknown_error', 'param': None, 'code': 'invalid_request_error'}}
… (same 402 "Insufficient Balance" repeated for all 24 companies, each logged twice: `LLM deepseek task=select_job_page … error=` and `<company> -> - [Error code: 402 …]`) …
2026-09-29 17:55:31  [INFO]  somerset | dispatch company task completed: select_job_page pass:0 fail:0 error:24 (batch: select_job_page-9763cb58-c6d2-4441-a92a-59b49af4372d)
```

Affected companies: publichealth_pitt_edu, cstn_me, cpcc_edu, fgb_net, firstquality_com, vacareers_va_gov, bryanuniversity_edu, geaerospace_com, nasa_gov, cadmusgroup_com, citrincooperman_com_2, ypsomed_com, multco_us, info_montgomerycollege_edu, active_com, pmcky_org, scripps_org, unr_edu, adventisthealthcare_com, us_milliman_com, stmarys_org, eclinicalworks_com, multicare_org, athenahealth_com.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
