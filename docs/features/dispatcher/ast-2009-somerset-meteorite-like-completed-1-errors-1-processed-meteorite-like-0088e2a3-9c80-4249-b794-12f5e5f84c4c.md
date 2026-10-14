# AST-2009 — [✅/Somerset] meteorite_like COMPLETED: 1 error(s) / 1 processed | meteorite_like-0088e2a3-9c80-4249-b794-12f5e5f84c4c

<!-- linear-archive: AST-2009 archived 2026-10-13 -->

## Linear archive (AST-2009)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2009/somerset-meteorite-like-completed-1-errors-1-processed-meteorite-like  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

A `meteorite_like` dispatch batch on Somerset (`meteorite_like-0088e2a3-…`) ended `pass:0 fail:0 error:1`: the single entity (`c351ecf8-…`) went to `METEORITE_FAILED_TECHNICAL_LIKE` because OpenRouter returned HTTP 429 — `openai/gpt-oss-120b is temporarily rate-limited upstream` on the shared-pool host `DekaLLM`. Astral made exactly one attempt and gave up: `PROVIDER_CALL_BUDGET["max_retries"]` is `0` (AST-1189), so the Anthropic SDK does not retry, and `LLM_SERVER_CONFIG["openrouter"]["concurrency"]` is `None` (AST-1877 deferred that decision until you approved limits), so `llm_compat._create` skips its 429 backoff loop. A transient upstream blip is recorded as a permanent technical failure on the entity.

## To-be

A 429 / rate-limit refusal from OpenRouter is treated as transient: the call is retried with jittered backoff (the same way DeepSeek's 429s already are) and the entity only lands in a technical-fail state if retries are truly exhausted. Ideally an exhausted rate limit holds entity state (like the AST-897 / AST-1867 balance-refusal hold) rather than stamping `METEORITE_FAILED_TECHNICAL_*`, so the next dispatch picks it up again with no manual reset.

## Susan's decisions (2026-10-06 comment)

1. **Retries:** "5 retries with doubling backoff."
2. **Exhausted:** "If it ever fails after 5 retries for 429, then error the whole batch to the error state."

She did **not** name a concurrency cap, a backoff ceiling, or a starting delay. The fix must not invent a concurrency cap or a ceiling. The starting delay (and whether today's 0.5–1.0 jitter stays) goes in the plan as a flagged ⚠️ Decision for review, not a silent default.

## Proposed steps

1. Turn on 429 retry for `openrouter` in `LLM_SERVER_CONFIG`: **5 retries, doubling delay**, no in-flight cap and no ceiling. `llm_compat._create` currently requires `max_concurrent` (and applies `backoff_max_seconds`) whenever a `concurrency` block exists, so both have to become optional rather than being filled with invented numbers.
2. Check that the batch-pinned path (AST-1959 host probe, AST-1960 ledger host) goes through `_create` with the server's retry config, so retries also apply when the batch is pinned to one upstream host.
3. When all 5 retries are spent on a 429, tag the result with a new rate-limit failure class (config next to `PROVIDER_BALANCE_REFUSAL`), and have the dispatcher **stop the batch**: no further provider calls this run, the same short-circuit the balance-outage path uses, with the dispatch ledger row finishing as `FAILED` (the batch error state).
4. Add tests: an OpenRouter 429 is retried up to 5 times with doubling delay, and a 6th consecutive 429 stops the batch and records the ledger as `FAILED`.

## Component scope

* `src/utils/config.py` — modified: the `openrouter` entry in `LLM_SERVER_CONFIG` turns on 429 retry (5 retries, doubling) instead of `None`, and a new rate-limit failure-class config sits next to `PROVIDER_BALANCE_REFUSAL`.
* `src/external/llm_compat.py` — modified: `_create` runs the 429 retry loop without requiring an in-flight cap or a backoff ceiling, and an exhausted 429 comes back tagged with the rate-limit failure class (plus the pinned/probed OpenRouter path, if it skips the retry loop today).
* `src/utils/llm_external.py` — modified: classify and detect an exhausted rate-limit refusal, mirroring `classify_provider_balance_refusal` / `is_provider_balance_refusal`.
* `src/core/dispatcher.py` — modified: on an exhausted rate-limit result, stop the batch (no further calls) and finish the dispatch ledger as `FAILED`, mirroring the balance-outage branches.
* `src/core/consult.py` and `src/core/roster.py` (amended per AST-2010 \[scope-gate\]) — modified: forward the new rate-limit `failure_class` upward on their failure returns, the same way they already forward balance refusal, so the dispatcher actually sees an exhausted 429. Entity routing is unchanged (no hold).

## Technical scope

* `src/utils/config.py` — config change: a retry block on the existing `openrouter` server entry (retry count 5, doubling delay; cap/ceiling keys absent), and a new config dict for the rate-limit failure class (status codes / message substrings), so detection stays config-driven.
* `src/external/llm_compat.py` — modified function `_create`: the semaphore and the delay ceiling only apply when configured. Modified send path: tags an exhausted `RateLimitError` result with the new failure class, so the dispatcher can see it.
* `src/utils/llm_external.py` — a new classifier function and a new predicate function, so the dispatcher can recognize an exhausted rate limit the way it already recognizes balance refusal.
* `src/core/dispatcher.py` — modified batch-runner and run-finalize functions: a rate-limit outage flag on `ctx` short-circuits remaining calls, and the run's final status becomes `FAILED`, so the whole batch errors instead of grinding on through the rate limit.
* `src/core/consult.py` and `src/core/roster.py` (amended per AST-2010 \[scope-gate\]) — modified functions: the failure-return branches (`render_verdict`, the single-entity grade path in `run_consult_task`, the batch envelope failure branch, and roster's matching balance-forwarding sites) carry `failure_class` for the rate-limit class too, so the tag survives the trip from `llm_compat` to the dispatcher.

## Ancestor candidates

- [X] [AST-1877](https://linear.app/astralcareermatch/issue/AST-1877) — model → server catalog / `llm_compat` client (`docs/features/agent/ast-1877-model-server-catalog-compat-client.md`): set `openrouter.concurrency = None`, meaning "no 429 retry until Susan approves limits". This is the direct root cause.
- [ ] [AST-1960](https://linear.app/astralcareermatch/issue/AST-1960) — record the serving host on the dispatch ledger (`docs/features/foundation/ast-1960-record-the-serving-host-on-the-dispatch-ledger.md`), together with AST-1959's per-batch host probe/pin. The 429 came from the pinned upstream host, and the doc discusses 429s on a locked host.
- [ ] [AST-1189](<https://linear.app/astralcareermatch/issue/AST-1189>) — provider call budget / timeout failure class (`docs/features/artifacts/ast-1189-provider-call-budget-timeout-failure-class.md`): set `max_retries: 0`. Its review already warned that this "converts every blip into a task failure" for transient 429s.
- [ ] [AST-897](<https://linear.app/astralcareermatch/issue/AST-897>) — hold entity state on provider balance refusal (`docs/features/agent/ast-897-hold-entity-state-on-provider-balance-refusal.md`): the hold-state pattern step 3 would copy for an exhausted rate limit.
- [ ] [AST-1155](<https://linear.app/astralcareermatch/issue/AST-1155>) — incomplete grades retry-holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`): an earlier example of "transient → hold, not technical fail".

---

## Original report

```
2026-10-06 20:04:31  [INFO]  somerset | dispatch job starting
meteorite_like — 1 available (batch:
meteorite_like-0088e2a3-9c80-4249-b794-12f5e5f84c4c)
2026-10-06 20:04:41  [INFO]  somerset | dispatch job task completed:
meteorite_like pass:0 fail:0 error:1 (batch:
meteorite_like-0088e2a3-9c80-4249-b794-12f5e5f84c4c)
2026-10-06 20:04:41  [WARNING]  c351ecf8-9dc2-4690-a889-97dce5eb3249
-> METEORITE_FAILED_TECHNICAL_LIKE [Error code: 429 - {'type':
'error', 'error': {'type': 'rate_limit_error', 'message': 'Provider
returned error', 'error_type': 'rate_limit_exceeded'}, 'request_id':
'gen-1791317077-BxAhSsQolTZaEuWD34vk', 'metadata': {'raw':
'openai/gpt-oss-120b is temporarily rate-limited upstream. Please
retry shortly, or add your own key to accumulate your rate limits:
https://openrouter.ai/settings/integrations', 'provider_name':
'DekaLLM', 'is_byok': False, 'provider_error_code': '429',
'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry
shortly, add your own provider key
(https://openrouter.ai/settings/integrations), or route to another
provider with provider routing:
https://openrouter.ai/docs/features/provider-routing'}}]
2026-10-06 20:04:41  [WARNING]  LLM openrouter task=meteorite_like
5.5s error=Error code: 429 - {'type': 'error', 'error': {'type':
'rate_limit_error', 'message': 'Provider returned error',
'error_type': 'rate_limit_exceeded'}, 'request_id':
'gen-1791317077-BxAhSsQolTZaEuWD34vk', 'metadata': {'raw':
'openai/gpt-oss-120b is temporarily rate-limited upstream. Please
retry shortly, or add your own key to accumulate your rate limits:
https://openrouter.ai/settings/integrations', 'provider_name':
'DekaLLM', 'is_byok': False, 'provider_error_code': '429',
'limit_source': 'upstream_provider_shared_pool', 'remedy_hint': 'Retry
shortly, add your own provider key
(https://openrouter.ai/settings/integrations), or route to another
provider with provider routing:
https://openrouter.ai/docs/features/provider-routing'}}
```

### Comments

#### chuckles — 2026-10-06T20:45:05.513Z
@susan two defaults to check in UAT. Both live in `LLM_SERVER_CONFIG["openrouter"]` and are a one-line flip:

1. **Starting delay:** retries wait 2s, 4s, 8s, 16s, 32s (about 62s worst case per call), with the existing 0.5–1.0 jitter. You said "doubling" but didn't name a starting delay, so this reuses DeepSeek's existing 2.0s base.
2. **Only OpenRouter stops the batch** on an exhausted 429 (`exhausted_stops_batch: True`). DeepSeek, Kimi and Anthropic behave exactly as today.

Separately, about 104 tests in the touched test files already fail on untouched `dev`, before this fix. The fix adds none. The test runner also expects a `python3.12` binary that the epic worktree doesn't have. Ada and Betty both ran tests through the main `.venv`.

#### chuckles — 2026-10-06T20:44:49.108Z
@susan two defaults to check in UAT. Both live in `LLM_SERVER_CONFIG["openrouter"]` and are a one-line flip:

1. **Starting delay:** retries wait 2s, 4s, 8s, 16s, 32s (about 62s worst case per call), with the existing 0.5–1.0 jitter. You said "doubling" but didn't name a starting delay, so this reuses DeepSeek's existing 2.0s base.
2. **Only OpenRouter stops the batch** on an exhausted 429 (`exhausted_stops_batch: True`). DeepSeek, Kimi and Anthropic behave exactly as today.

Separately, about 104 tests in the touched test files already fail on untouched `dev`, before this fix. The fix adds none. The test runner also expects a `python3.12` binary that the epic worktree doesn't have. Ada and Betty both ran tests through the main `.venv`.

#### susan — 2026-10-06T20:22:42.617Z
1. 5 retries with doubling backoff
2. If it ever fails after 5 retries for 429, then error the whole batch to the error state.

#### chuckles — 2026-10-06T20:14:15.692Z
@susan two decisions before I open `ftr/` and file the fix child. Your AST-1877 check is noted. Nothing has been seeded yet.

1. **OpenRouter 429 retry numbers.** `max_concurrent` / `rate_limit_retries` / `backoff_base_seconds` / `backoff_max_seconds`. Should it copy DeepSeek's **20 / 4 / 2.0s / 30.0s**, or use other values? (AST-1877 left this `None` until you named limits.)
2. **Once retries run out on a 429:** should the entity **hold state** (re-claimed next dispatch, like the balance-refusal hold) or keep today's **`METEORITE_FAILED_TECHNICAL_*`** transition? "Hold" adds `llm_external.py` + `dispatcher.py` to the fix. "Keep" makes it a config-only fix.

Reply here, then reassign to Chuckles (still Todo) and bug-fix picks it straight up.

---

_Implementation detail may live in git history on `origin/dev`._
