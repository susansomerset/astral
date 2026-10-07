# AST-1850 — gap: tests for one-shot Telescope loop teardown runner (AST-1849 board-betty REVISE)

<!-- linear-archive: AST-1850 archived 2026-10-07 -->

## Linear archive (AST-1850)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1850/gap-tests-for-one-shot-telescope-loop-teardown-runner-ast-1849-board  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1841 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6  
**Blocked by / blocks / related:** parent: AST-1841

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1849. No test references `close_loop_resources`, `aclose_current_loop`, `_LoopState`, or `_pool._states`, and the plan's Repro cases 1–4 have no node. Add coverage for the new one-shot runner in `src/external/telescope.py`:

* A leak repro: after a coroutine that touched the queue runs through the runner, `_states` is clean, `pool.close` was awaited once, and the poller is done. It must go red against the pre-fix product (bare `asyncio.run`) and green once AST-1849 lands.
* The exception path re-raises with cleanup still done.
* A coroutine that never touches Telescope returns its value with `_states` unchanged.

Bible entry for loop teardown.

## Scope

### Component scope

* `tests/component/external/test_telescope.py` (modified): runner tests. Leak repro red on bare `asyncio.run` / green on the runner, exception-path cleanup, no-touch passthrough.
* `docs/test-bible/external/telescope.md` (modified): bible entry for per-loop teardown (`close_loop_resources` / `aclose_current_loop` / the one-shot runner).

### Technical scope

* Telescope tests: new cases for the one-shot runner and per-loop state release. The repro must fail against the pre-fix product and pass after AST-1849.
* Test bible: new entry naming the teardown coverage.

## Boundaries

Test and bible only; product code stays on AST-1849. Betty lands the tests (engineers are banned from the test tree). No existing test breaks per Betty's blast-radius check (no test patches `asyncio.run` on the five call-site modules). Call-site swaps in `api_admin` / `api_meteorite` / `api_inbox` / `gazer` / `contact` need no new tests unless Betty says otherwise.

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1849 (see that comment). Plan doc: docs/features/foundation/ast-1726-platform-telescope-py-drop-in-playwright-decommission.md (AST-1849's plan-fix patch, Repro cases 1–4).

## Git branch (authoritative)

Parent `ftr/AST-1841-asyncio-run-telescope-loop-teardown`, child `sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests`.

### Comments

#### radia — 2026-09-28T21:50:49.784Z
[code-rubric] PROCEED (Commit: 06d68e26) bug-repro pins teardown

#### hedy — 2026-09-28T21:49:49.619Z
`origin/sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests` @ `06d68e26` · [bug-repro] red→green confirmed.

- `TestAst1849OneShotLoopTeardown::test_run_one_shot_releases_loop_state`: FAILED with src at pre-fix `83a0c352` (AttributeError, no `run_one_shot`), PASSED on tip. Nodes 2–3 same flip; control green both.
- Manifest `TestAst1849OneShotLoopTeardown`: 4 passed.
- Full `test_telescope.py`: 44 passed, 4 failed — only the known pre-existing `TestTelescopePoolHttp` ×3 + `TestAst1750PostTelescopeDebugDump` (retired `_TelescopePool`; also red on origin/dev).

#### betty — 2026-09-28T21:47:55.559Z
[bug-repro]
`origin/sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests` @ `41a1c634` · repro red pre-fix, green on ftr

Repro node: `tests/component/external/test_telescope.py::TestAst1849OneShotLoopTeardown::test_run_one_shot_releases_loop_state`. Red at pre-fix `83a0c352` (nodes 1–3 AttributeError: no `run_one_shot`; control green). All 4 green on ftr `0877d286`. Manifest: `docs/test-bible/external/telescope.md` § AST-1849 · AST-1850. Off-procedure: `origin/tests-clean-base` still missing, so the validator couldn't run; cherry-picked the single commit onto origin/tests as `b3c7f256` (AST-1831/AST-1848 precedent). The marker still needs restoring.

#### joan — 2026-09-28T21:44:57.893Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T21:44:39.861Z
[board-betty] TESTS: OK
Repro shape acceptable. Red-on-AttributeError alone would be weak, but paired with the control node (bare asyncio.run leaves _states entry, pool.close never awaited) and _assert_released checking pool/listener close once + poller done + _states empty, nodes 1–3 would also go red if run_one_shot existed but skipped close_loop_resources. Fixture checked against ftr 0877d286: _get_db never calls asyncpg.connect (listener only opens in the poller with waiters; none here), aclose_current_loop closes exactly what the asserts expect; anchors (pw_mod, TestAst1750PostTelescopeDebugDump, bible AST-1840 · AST-1844) exist. Call-site test not required for this gap. Known residual: a single call site reverting to bare asyncio.run would still pass the suite — As-is overstates slightly; Susan's call whether that's a future ticket.

#### hedy — 2026-09-28T21:41:21.595Z
`origin/sub/AST-1841/AST-1850-asyncio-run-telescope-loop-teardown-tests` @ `bc4fea2d` · four nodes, bible entry planned

---

_Implementation detail may live in git history on `origin/dev`._
