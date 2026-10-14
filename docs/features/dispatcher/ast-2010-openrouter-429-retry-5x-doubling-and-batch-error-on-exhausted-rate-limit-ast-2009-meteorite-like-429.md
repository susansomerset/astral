# AST-2010 — OpenRouter 429 retry (5x doubling) and batch error on exhausted rate limit (AST-2009 meteorite_like 429)

<!-- linear-archive: AST-2010 archived 2026-10-13 -->

## Linear archive (AST-2010)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2010/openrouter-429-retry-5x-doubling-and-batch-error-on-exhausted-rate  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-2009 — [✅/Somerset] meteorite_like COMPLETED: 1 error(s) / 1 processed | meteorite_like-0088e2a3-9c80-4249-b794-12f5e5f84c4c  
**Blocked by / blocks / related:** parent: AST-2009

### Description

## What this implements

The `fix` child for orphaned bug [AST-2009](https://linear.app/astralcareermatch/issue/AST-2009) (OpenRouter 429 on `meteorite_like` recorded as a technical failure after one attempt). Two parts, both approved by Susan on AST-2009:

1. OpenRouter 429s are retried: 5 retries with doubling backoff.
2. If a call still gets a 429 after 5 retries, the whole batch errors: no further provider calls this run, and the dispatch ledger finishes as `FAILED`.

## Scope

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

## Susan's decisions (carried from AST-2009)

1. **Retries:** "5 retries with doubling backoff."
2. **Exhausted:** "If it ever fails after 5 retries for 429, then error the whole batch to the error state."

She did **not** name a concurrency cap, a backoff ceiling, or a starting delay. The fix must not invent a concurrency cap or a ceiling. The starting delay (and whether today's 0.5–1.0 jitter stays) goes in the plan as a flagged ⚠️ Decision for review, not a silent default.

## Notes for planning

Approved ancestor: [AST-1877](https://linear.app/astralcareermatch/issue/AST-1877) (Done; doc `docs/features/agent/ast-1877-model-server-catalog-compat-client.md`). Patch that doc with a `## Bug: <this-id>` block. The full as-is/to-be and the original log live on parent AST-2009.

## Git branch (authoritative)

Orphaned mini-parent: `ftr/AST-2009-openrouter-429-retry`, child `sub/AST-2009/AST-2010-openrouter-429-retry`. Seeded off `origin/dev` by bug-fix.

### Comments

#### radia — 2026-10-06T20:44:00.678Z
[code-rubric] PROCEED (Commit: d2d8bd3b2) OpenRouter 429 batch stop

#### ada — 2026-10-06T20:42:34.732Z
`origin/sub/AST-2009/AST-2010-openrouter-429-retry` @ `d2d8bd3b2` · bug-repro 4/4 red→green; manifest 46/46; no new reds

#### betty — 2026-10-06T20:37:55.745Z
[bug-repro]
`origin/sub/AST-2009/AST-2010-openrouter-429-retry` @ `32053a727` · repro lands red, awaits fix

Manifest + repro node ids: `docs/test-bible/external/llm_compat.md` § AST-2010 (dispatcher: `core/dispatcher.md` § AST-2010).

#### ada — 2026-10-06T20:32:07.643Z
`origin/sub/AST-2009/AST-2010-openrouter-429-retry` @ `c08219c32` · decisions resolved, OpenRouter-only

#### chuckles — 2026-10-06T20:31:20.961Z
Fix-board: Betty `TESTS: REVISE`, Joan `CANON: OK`. Betty lands the tests on this branch through qa-fix, with no separate gap child. Same route Susan chose on AST-2007.

The plan's two ⚠️ Decisions are settled as follows. Ada revises the plan before Betty writes tests against it:

1. **Starting delay / jitter:** start at **2.0s**, doubling, and keep the existing 0.5–1.0 jitter. Susan named "doubling" but no start, so this reuses the existing base rather than inventing a new number. It stays config-owned, and it's flagged for her at UAT.
2. **Which servers stop the batch:** **OpenRouter only**, through an opt-in per-server setting. Susan's answer was about OpenRouter, so DeepSeek's exhausted-429 behavior stays exactly as it is today.

@susan both are easy to flip in config if you want them different. Say so on AST-2009.

#### joan — 2026-10-06T20:31:15.241Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T20:30:25.605Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/llm_compat.md + core/dispatcher.md (no bible entry for 429 exhaustion) — missing repro coverage + broken test — no test covers 6× doubling retry with no cap/ceiling, `provider_rate_limit` tagging (call + probe), the new `llm_external` classifier/predicate, consult/roster `_rate_limit_tag` forwarding, or dispatcher stop + ledger FAILED; existing `TestAst1959ProbeHostLock::test_ac4_failed_probe_fails_the_batch_with_no_fallback` raises 429 on openrouter, asserts `len(c.calls) == 1`, and doesn't patch `time.sleep` (it will make 6 calls and sleep for real).

#### ada — 2026-10-06T20:29:24.372Z
`origin/sub/AST-2009/AST-2010-openrouter-429-retry` @ `639101776` · retry plan, two decisions flagged

#### chuckles — 2026-10-06T20:26:51.936Z
Scope amended on AST-2010 and AST-2009 with option 1: `src/core/consult.py` and `src/core/roster.py` now forward the rate-limit `failure_class` the same way they already forward balance refusal. That's the tag-the-result mechanism Susan approved, so no new design call is needed. Option 2's module-level registry is not taken. Also tag the failed host probe, as you noted.

#### ada — 2026-10-06T20:26:22.933Z
[scope-gate] AST-2010 plan-fix: the dispatcher can't see an exhausted-429 tag without changes in `src/core/consult.py` (and `src/core/roster.py` for company tasks), and neither file is in this ticket's Scope.

**What the scope says.** Technical scope, `llm_compat.py`: "tags an exhausted `RateLimitError` result with the new failure class, so the dispatcher can see it". Technical scope, `dispatcher.py`: "a rate-limit outage flag on `ctx` short-circuits remaining calls". Component scope lists only `config.py`, `llm_compat.py`, `llm_external.py`, `dispatcher.py`.

**Why that isn't enough.** The dispatcher never sees the `send_to_llm_compat` result. It only sees what `consult.run_consult_task` returns. `agent.do_task` passes `failure_class` through unchanged. But `consult.py` only forwards `failure_class` upward when `is_provider_balance_refusal(result)` is true. Every other failure path drops it:
- `render_verdict` (~L1459–1487): any non-balance, non-timeout failure returns `_fail(...)` with no `failure_class`.
- `run_consult_task` single-entity grade path (~L2913–2918): this is the path the AST-2009 repro took (`meteorite_like`, one entity). It returns bare counts and drops `failure_class` for every class, including balance refusal.
- Batch envelope failure (~L1657–1697, e.g. `meteorite_like_batch`): the generic branch returns no `failure_class`.
- Per-row loop (~L1264–1284): it only counts errors.
- `roster.py` has the same balance-only forwarding at ~L921, 952, 1534, 2034, 2268.

So with only the four in-scope files, the new tag is set in `llm_compat` and then dropped in `consult` before it reaches the dispatcher. The batch would never stop and the ledger would never be `FAILED`.

**Kind of change needed.** In `consult.py` (and `roster.py`), forward the new rate-limit `failure_class` upward on those failure returns, the same way the balance-refusal branches already do. Entity routing stays as it is today: the entity still goes to `error_state`, with no hold. The four in-scope files' plan doesn't change.

**In-scope alternative (needs a different kind of change, so it's Susan's or Archie's call).** `llm_compat` records "429 exhausted" in a per-batch registry keyed on `log_batch_id`, the same pattern as the `openrouter._hosts` host map. The dispatcher checks that registry after each `run_consult_task` call, so `consult.py` and `roster.py` stay untouched. The cost is new module-level state, and it isn't the "tag the result" mechanism the Technical scope describes.

After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
