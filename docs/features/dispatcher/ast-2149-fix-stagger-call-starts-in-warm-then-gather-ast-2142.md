# AST-2149 — fix: stagger call starts in _warm_then_gather (AST-2142)

<!-- linear-archive: AST-2149 archived 2026-10-16 -->

## Linear archive (AST-2149)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2149/fix-stagger-call-starts-in-warm-then-gather-ast-2142  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2142 — Batch_mode "each" is throwing 429's  
**Blocked by / blocks / related:** parent: AST-2142

### Description

## What this implements

Fix for [AST-2142](https://linear.app/astralcareermatch/issue/AST-2142). Today `_warm_then_gather` (batch_mode "each", `batch_call_mode = 0`) starts every claimed entity in the same instant after the warm call, so 15–20 OpenRouter calls collide, get 429s from Parasail's shared upstream pool, and retry in lockstep until one exhausts AST-2010's 5 retries and stops the batch. Susan's direction: a **config-driven stagger** between call starts, beginning at 1 second. Calls stay async and overlapping, and **no new cap anywhere**: caps live only on the `dispatch_task` record. The As-is, To-be and log are on AST-2142.

## Citations

none at intake — plan-fix names the statutes/patterns that govern the change.

## Scope

### Component scope

* `src/utils/config.py` — modified — new stagger setting in `ASTRAL_CONFIG` next to `cache_warm_delay_seconds`; one source of truth for the interval.
* `src/core/dispatcher.py` — modified — `_warm_then_gather` spaces out when each concurrent call starts, using that setting.

### Technical scope

* `src/utils/config.py` — new field in `ASTRAL_CONFIG` (float seconds, default 1.0, 0 = off). It is config-driven per Susan, with no number hard-coded in the dispatcher.
* `src/core/dispatcher.py` — modified function `_warm_then_gather`. Each entity after the first waits its own index × stagger before calling `one_fn`, while everything stays inside the existing single `asyncio.gather`, so concurrency, `return_exceptions` handling, and result order are preserved.

## Acceptance criteria

1. A new `ASTRAL_CONFIG` setting (seconds, default `1.0`) beside `cache_warm_delay_seconds` controls the stagger; `0` gives today's behavior exactly.
2. In `_warm_then_gather`, after the warm call and warm delay, the *k*-th remaining entity starts about *k* × stagger later. All of them still run concurrently inside one `asyncio.gather`, results keep entity order, and the `return_exceptions` / per-entity error handling is unchanged.
3. No `max_concurrent` or other in-flight cap is added to `LLM_SERVER_CONFIG` or `llm_compat`.

## Boundaries

* The `batch_call_mode = 1` chunked consult path (`dispatcher.py` \~L883, its own `asyncio.gather` over chunks) is untouched.
* AST-2010 retry/backoff and `exhausted_stops_batch` are unchanged.
* The AST-1959 host lock and BYOK are out of scope.

## Notes for planning

Ancestors were offered but none was checked. Nearest context: AST-2010 (429 retry policy; plan sections in `docs/features/agent/ast-1877-model-server-catalog-compat-client.md`) and AST-1875 (dispatcher config knob, `docs/features/dispatcher/ast-1875-add-a-selection-box-on-scheduled-tasks-to-set-concurrent-tasks-limit.md`).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-2142-gather-call-stagger`, child `sub/AST-2142/AST-2149-gather-call-stagger`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-12T18:40:12.033Z
[code-rubric] PROCEED (Commit: 952c67083) gather stagger clean

#### chuckles — 2026-10-12T18:34:27.184Z
Fix-board `[board-betty] TESTS: REVISE` filed as gap sibling [AST-2153](https://linear.app/astralcareermatch/issue/AST-2153) (repro + bible + fixture drift); qa-fix does not run on this ticket.

#### joan — 2026-10-12T18:34:04.292Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T18:33:42.748Z
Correction to the [board-betty] drift note: drop TestAst2093 (~L2323/2333). Its class fixture already patches `dispatcher_mod.asyncio.sleep` with an AsyncMock, so the stagger costs it nothing. The real-sleep drift is limited to the 3-entity TestAst1867 / TestAst2010 / TestAst2098 cases. Verdict unchanged: TESTS: REVISE.

#### betty — 2026-10-12T18:33:35.934Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/dispatcher.md (no stagger entry) — missing coverage — `TestWarmThenGather` only exercises 2 entities, so nothing asserts start spacing among `entities[1:]`; add the plan's Repro as a `[bug-repro]` node (deterministic `asyncio.sleep` AsyncMock, 4 entities, `gather_stagger_seconds=1.0` → awaited with exactly 1.0 and 2.0, never 0; plus a `=0` node asserting no extra sleeps / identical output) and a bible row.

Breakage check: nothing goes red. The existing 2-entity `TestWarmThenGather` cases (incl. `test_skips_delay_when_cache_warm_disabled`) hit i=0 → no stagger sleep; tests that monkeypatch `_warm_then_gather` or use `batch_call_mode=1` are unaffected. Drift only: the TestAst1867 / TestAst2010 / TestAst2098 fixtures zero `cache_warm_delay_seconds` but run real `_warm_then_gather` over 3-entity claims (~L1734–2120), and TestAst2093 claims 3–5 entities (~L2323/2333). With the new 1.0s default each of these sleeps for real, about 1–3s per test. qa-fix should zero `gather_stagger_seconds` beside the warm delay in those fixtures.

#### ada — 2026-10-12T18:32:49.350Z
`origin/sub/AST-2142/AST-2149-gather-call-stagger` @ `fa8d6a863` · offset stagger inside gather

---

_Implementation detail may live in git history on `origin/dev`._
