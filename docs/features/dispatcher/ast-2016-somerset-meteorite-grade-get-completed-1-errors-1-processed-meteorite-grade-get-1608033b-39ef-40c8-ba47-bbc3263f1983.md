# AST-2016 — [✅/Somerset] meteorite_grade_get COMPLETED: 1 error(s) / 1 processed | meteorite_grade_get-1608033b-39ef-40c8-ba47-bbc3263f1983

<!-- linear-archive: AST-2016 archived 2026-10-16 -->

## Linear archive (AST-2016)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2016/somerset-meteorite-grade-get-completed-1-errors-1-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

On the OpenRouter path (`openai/gpt-oss-120b`, batch `meteorite_grade_get-1608033b…`), the per-batch host probe ([AST-1959](https://linear.app/astralcareermatch/issue/AST-1959)) got back a hollow response: no `usage` and no `provider`. Three things then go wrong:

* **Timesheet traceback.** `_record_probe` calls `_timesheet_kwargs_for`, and `usage_to_token_counts(None)` raises `AttributeError: 'NoneType' object has no attribute 'input_tokens'`. That logs a full ERROR traceback; the row is still written with zero tokens, per [AST-1966](https://linear.app/astralcareermatch/issue/AST-1966).
* **Uninformative error.** `probe_host` finds no `provider` and raises the generic `"Probe response named no provider"`, which throws away whatever the response actually carried.
* **Entity burned.** The probe error comes back from `send_to_llm_compat` as an ordinary failure, so consult routes the job to its task `error_state` (`METEORITE_FAILED_TECHNICAL_GET`). The job is lost to a transient routing problem that says nothing about the job itself.

The main (non-probe) call path has the same `usage_to_token_counts(response.usage)` weakness at the top of its `try`.

## To-be

> I think if the probe fails, release the batch with no-op, let the next round catch it. — Susan

A failed host probe (hollow response, no provider, or a probe exception that isn't an exhausted 429) is a **no-op for the batch**. Every entity keeps its current state (held, not errored, so no `error_state` transition), the batch claim is released as it already is in the dispatcher's `finally`, and the next dispatch round picks the same entities up and probes again. This follows the same shape as the provider balance-refusal hold ([AST-897](<https://linear.app/astralcareermatch/issue/AST-897>) / [AST-1867](https://linear.app/astralcareermatch/issue/AST-1867)). Exhausted-429 probe failures keep their existing [AST-2010](https://linear.app/astralcareermatch/issue/AST-2010) rate-limit path. The probe's error string names what OpenRouter actually returned when the body has anything. Missing `usage` counts as zero tokens with no exception traceback, on both the probe and the real call.

## Proposed steps

1. Make `usage_to_token_counts` return all-zero buckets when `usage` is `None`.
2. In `probe_host`, pull any provider error text off a hollow response before the provider check, so the raised message says what came back.
3. Add a probe-failure failure class in config, alongside `PROVIDER_BALANCE_REFUSAL` / `PROVIDER_RATE_LIMIT`. In `send_to_llm_compat`'s probe-error return, tag non-429 probe failures with it.
4. At the consult/roster sites that hold state on balance refusal today, hold state for a probe failure the same way: no `error_state` transition, counted as held. The cleanest route is one shared "state-held" predicate covering both classes rather than a second copy of each branch; that's plan-fix's call.
5. Let the dispatcher stop the rest of the run on a probe failure, like the balance and rate-limit outages do. That way one dead probe doesn't keep firing calls this round, and the run exits with the claim released.
6. Risk for plan-fix to weigh, not a blocker: if a probe fails *persistently* (for example, no zero-data-retention host exists for the SKU), these entities stay held every round and never surface as errors. The WARNING log line is the only signal. Whether that needs an alert or a cap is Susan's call; nothing is added here without her say-so.

## Component scope

* `src/utils/cost_calculator.py` (modified): `usage_to_token_counts` is where the `NoneType` crash happens; it needs to tolerate missing usage.
* `src/external/openrouter.py` (modified): `probe_host` produces the uninformative "named no provider" error and needs to describe what a hollow/error probe response actually carried.
* `src/utils/config.py` (modified): needs a probe-failure failure-class definition alongside the other `PROVIDER_*` dicts.
* `src/utils/llm_external.py` (modified): home of the provider-failure classifiers and predicates; needs the probe-failure predicate (or a shared state-held predicate).
* `src/external/llm_compat.py` (modified): the probe-error return in `send_to_llm_compat` needs to tag non-429 probe failures with the new class.
* `src/core/consult.py` (modified): the job consult paths (which `meteorite_grade_get` runs through) currently route a probe failure to `error_state`; they need to hold state instead, as they already do for balance refusal.
* `src/core/roster.py` (modified): its company paths have the same balance-refusal hold branches and need the same treatment so a probe failure doesn't error a company.
* `src/core/dispatcher.py` (modified): needs to note a probe-failure outage and skip the rest of the run, as it does for balance/rate-limit outages.

## Technical scope

* `src/utils/cost_calculator.py`: modified function. `usage_to_token_counts` returns zero counts for a `None` usage object, so no caller needs its own guard.
* `src/external/openrouter.py`: modified function. `probe_host` extracts provider error text from a hollow response and includes it in the raised error.
* `src/utils/config.py`: new config dict. A probe-failure entry carrying its `failure_class`, following the existing `PROVIDER_*` shape.
* `src/utils/llm_external.py`: new function. A predicate for the probe-failure class, or one shared state-held predicate covering balance refusal plus probe failure, so the hold sites check one thing.
* `src/external/llm_compat.py`: modified function. The probe-error branch of `send_to_llm_compat` sets the new `failure_class` when the error isn't classified as a rate limit.
* `src/core/consult.py`: modified functions. The balance-refusal hold branches widen to probe failure, so the entity keeps its state and is counted held rather than errored.
* `src/core/roster.py`: modified functions. Same widening at its balance-refusal hold branches.
* `src/core/dispatcher.py`: modified functions. A probe-failure outage note alongside `_note_provider_rate_limit_outage`, plus the skip-the-rest checks that already test the balance/rate-limit outage keys. No new tables or fields.

## Ancestor candidates

- [ ] [AST-1959](https://linear.app/astralcareermatch/issue/AST-1959) — Per-batch probe and host lock on the OpenRouter path (`docs/features/foundation/ast-1959-per-batch-probe-and-host-lock-on-the-openrouter-path.md`). Owns `probe_host` / `get_batch_host` / `_record_probe` and its "no fallback" probe-failure rule, which this fix amends.
- [ ] [AST-1867](https://linear.app/astralcareermatch/issue/AST-1867) — Report provider balance refusal as one batch-level outage: held count, stop batch, no breaker trip (`docs/features/dispatcher/ast-1867-fix-report-provider-balance-refusal-as-one-batch-level-outage-held-count-stop-batch-clear-alert-no-breaker-trip.md`). The batch-level "held + stop + release" pattern Susan's to-be maps onto.
- [ ] [AST-897](<https://linear.app/astralcareermatch/issue/AST-897>) — Hold entity state on provider balance refusal (`docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md`). The per-entity state-hold branches this fix widens.
- [ ] [AST-1966](https://linear.app/astralcareermatch/issue/AST-1966) — Background reconcile per call, unpriced rows recorded (`docs/features/agent/ast-1966-background-reconcile-per-call-unpriced-rows-recorded.md`). Owns the "always a row, zero counts" timesheet fallback that logged the traceback.
- [ ] [AST-1190](<https://linear.app/astralcareermatch/issue/AST-1190>) — Empty/unusable provider response surfacing (`docs/features/artifacts/ast-1190-empty-unusable-provider-response-surfacing.md`). Weaker now: under Susan's to-be a hollow probe is held rather than routed through the empty-response failure path.
- [ ] [AST-1964](https://linear.app/astralcareermatch/issue/AST-1964) — Model routing type and OpenRouter generation-stats lookup (`docs/features/agent/ast-1964-model-routing-type-and-openrouter-generation-stats-lookup.md`). Weakest: generation stats could show the real upstream error after the fact.

---

## Original report

```
2026-10-07 18:10:34  [INFO]  somerset | dispatch job starting
meteorite_grade_get — 1 available (batch:
meteorite_grade_get-1608033b-39ef-40c8-ba47-bbc3263f1983)
2026-10-07 18:10:47  [ERROR]  - | timesheet token counts on openrouter
openai/gpt-oss-120b
  AttributeError: 'NoneType' object has no attribute 'input_tokens'
  Recording the row with zero tokens
Traceback (most recent call last):
  File "/app/src/external/llm_compat.py", line 153, in _timesheet_kwargs_for
    counts = usage_to_token_counts(response.usage)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/utils/cost_calculator.py", line 84, in usage_to_token_counts
    "cache_miss": usage.input_tokens,
                  ^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'input_tokens'
2026-10-07 18:10:48  [INFO]  somerset | dispatch job task completed:
meteorite_grade_get pass:0 fail:0 error:1 (batch:
meteorite_grade_get-1608033b-39ef-40c8-ba47-bbc3263f1983)
2026-10-07 18:10:48  [WARNING]  1397d420-506d-45b9-844f-1f220cde19b0
-> METEORITE_FAILED_TECHNICAL_GET [Host probe failed: Probe response
named no provider]
2026-10-07 18:10:48  [WARNING]  LLM openrouter
task=meteorite_grade_get 10.9s error=Host probe failed: Probe response
named no provider
```

### Comments

#### chuckles — 2026-10-09T06:36:14.693Z
Recurred: [AST-2110](https://linear.app/astralcareermatch/issue/AST-2110) — qualify_job_listings-f1992266-e52b-492e-a18d-2ff1a065331c, 2026-10-09 06:33:39.

#### chuckles — 2026-10-09T03:20:30.893Z
AST-2099 REVIEW — Betty's qa-fix tests are done but unpublished; gated on [AST-2104](https://linear.app/astralcareermatch/issue/AST-2104) (shared astral-tests `tests` branch carries a forbidden sync merge from the AST-2086 run).

---

_Implementation detail may live in git history on `origin/dev`._
