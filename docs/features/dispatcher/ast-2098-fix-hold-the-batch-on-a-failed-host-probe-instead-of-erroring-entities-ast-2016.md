# AST-2098 — fix: hold the batch on a failed host probe instead of erroring entities (AST-2016)

<!-- linear-archive: AST-2098 archived 2026-10-16 -->

## Linear archive (AST-2098)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2098/fix-hold-the-batch-on-a-failed-host-probe-instead-of-erroring-entities  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-2016 — [✅/Somerset] meteorite_grade_get COMPLETED: 1 error(s) / 1 processed | meteorite_grade_get-1608033b-39ef-40c8-ba47-bbc3263f1983  
**Blocked by / blocks / related:** parent: AST-2016; blocks: AST-2099

### Description

## What this implements

When the per-batch OpenRouter host probe fails for any reason other than an exhausted 429 (hollow response, no `provider`, or a probe exception), the batch is released as a no-op. Every entity keeps its current state and counts as held, not errored, so there is no `error_state` transition. The run stops issuing calls, and the next dispatch round picks the same entities up and probes again. Missing `usage` reads as zero tokens with no exception traceback, on both the probe and the real call. The probe's error text names what OpenRouter actually returned.

## Scope

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

## Acceptance criteria

1. A hollow probe response (no `usage`, no `provider`) produces no `AttributeError` traceback; the probe timesheet row records zero tokens.
2. A non-429 probe failure leaves every entity in the batch in its input state (no `METEORITE_FAILED_TECHNICAL_GET` or other `error_state` transition), counted as held.
3. The run stops issuing further provider calls after a probe failure, and the batch claim is released so the next round retries.
4. An exhausted-429 probe failure still takes the existing AST-2010 rate-limit path.
5. The probe failure's logged error names the provider's own message when the response carries one.

## Boundaries

* No new alert or retry cap for a persistently failing probe; that's Susan's call (see the bug's Proposed steps item 6).
* No change to the AST-897 / AST-1867 balance-refusal behaviour itself, beyond sharing the hold check.

## Notes for planning

Bug: [AST-2016](https://linear.app/astralcareermatch/issue/AST-2016). Read its As-is / To-be / Proposed steps. Susan's direction: "if the probe fails, release the batch with no-op, let the next round catch it." No ancestor box was checked on the bug.

## Git branch (authoritative)

Parent `ftr/AST-2016-probe-fail-hold`, child `sub/AST-2016/AST-2098-probe-fail-hold`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-09T02:43:29.599Z
[code-rubric] PROCEED (Commit: 19036ccf0) probe hold matches plan

#### ada — 2026-10-09T02:40:15.513Z
`origin/sub/AST-2016/AST-2098-probe-fail-hold` @ `19036ccf0` · Code Complete

For AST-2099 (Betty): exactly one new failure vs the pre-fix tree on the touched-area component suites — `tests/component/external/test_openrouter.py::TestAst1959BatchHostMap::test_failed_probe_is_remembered_for_the_key[send1-…]` asserts the old exact string `"Host probe failed: Probe response named no provider"`; the error now appends the response body (AC 5). The other 86 failures in those suites fail identically on the pre-fix tree.

#### joan — 2026-10-09T02:37:02.160Z
[board-joan]  CANON: REVISE
What: patt.task.dispatch-retry — add "When this doesn't apply" carve-out for failed host probe (no entity attempt); Arc 5 hold — provider-side gate like empty_tokens

#### betty — 2026-10-09T02:36:04.347Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/llm_compat.md § AST-1959 (+ openrouter.md, core/consult.md, core/roster.md, core/dispatcher.md, utils/cost_calculator.md) — no bible entry or test for the repro (`usage=None` → zero tokens and no traceback; non-429 probe error → `failure_class == "provider_probe_failure"`; consult/roster probe hold `total_held` with state unchanged; dispatcher `provider_probe_outage` stop + INTERRUPTED) — and Proposed change step 2 breaks `tests/component/external/test_openrouter.py::TestAst1959BatchHostMap::test_failed_probe_is_remembered_for_the_key[provider=None]` (exact `"Host probe failed: Probe response named no provider"` equality).

Notes for qa-fix: `test_no_provider_raises_after_recording` (`match="named no provider"`) still passes. The llm_compat / consult / roster `"failure_class" not in out` tests use non-probe paths, and the dispatcher outage-key tests set their own ctx keys, so neither group breaks. No product-scope concern.

#### ada — 2026-10-09T02:35:07.260Z
`origin/sub/AST-2016/AST-2098-probe-fail-hold` @ `3f97ce856` · probe failure holds batch

---

_Implementation detail may live in git history on `origin/dev`._
