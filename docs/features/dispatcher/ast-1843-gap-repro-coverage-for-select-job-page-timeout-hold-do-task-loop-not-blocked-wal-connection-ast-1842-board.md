# AST-1843 — gap: repro coverage for select_job_page timeout-hold, do_task loop-not-blocked, WAL connection (AST-1842 board)

<!-- linear-archive: AST-1843 archived 2026-10-07 -->

## Linear archive (AST-1843)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1843/gap-repro-coverage-for-select-job-page-timeout-hold-do-task-loop-not  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1825 — [✅/Somerset] select_job_page INTERRUPTED: 1 error(s) / 30 processed | select_job_page-903ff01b-8669-4f0a-bfe8-cc088707621f  
**Blocked by / blocks / related:** parent: AST-1825

### Description

## What this implements

Test and bible gap opened by fix-board on AST-1842 (`[board-betty] TESTS: REVISE`). None of AST-1842's three repros has coverage today. This child lands `[bug-repro]` tests that fail against the pre-fix product and pass once AST-1842 lands on the ftr, plus the matching bible entries:

1. `select_job_page` holds `PJL_READY` (no `NO_JOBLIST` write) when `_find_job_page_from_assembled` gets `failure_class=provider_call_timeout`. Today only the AST-897 balance-refusal hold is covered.
2. `do_task` does not block the event loop while `save_agent_data` is slow or locked, meaning other coroutines keep running during the prompt/response store.
3. `_get_connection` returns a connection with WAL journal mode and the configured busy timeout.

No product change. The product fix is AST-1842.

## Scope

### Component scope

* `tests/component/core/test_roster.py` (modified): add the `select_job_page` timeout-hold repro next to the AST-897 balance-refusal hold test.
* `tests/component/core/test_agent.py` (modified): add a `do_task` repro showing the loop stays responsive while `save_agent_data` blocks.
* `tests/component/data/test_database.py` (modified): add a `_get_connection` repro asserting WAL journal mode and the configured busy timeout.
* `docs/test-bible/core/roster.md` (modified): record the timeout-hold coverage under the `select_job_page` / AST-897 hold entry.
* `docs/test-bible/core/agent.md` (modified): record the loop-not-blocked coverage under the `do_task` prompt-persist (AST-1448) entry.
* `docs/test-bible/data/database.md` (modified): record the connection WAL/busy-timeout coverage.

### Technical scope

* `test_roster.py`: new test case(s). A provider-call-budget timeout result from `_find_job_page_from_assembled` leaves company state at `PJL_READY` and never saves `NO_JOBLIST`. Exact names per plan-fix.
* `test_agent.py`: new test case(s). With `save_agent_data` stubbed to block for a bounded time, a concurrent coroutine still makes progress during `do_task`'s store step. This fails today because the store runs synchronously on the loop.
* `test_database.py`: new test case(s). A connection from `_get_connection` reports `journal_mode=wal` and the busy timeout from config.
* Bible files: modified entries naming the new node ids, so later qa-fix and qa-child passes find them.

## Acceptance criteria

- [X] Each of the three repros is red against pre-fix product (`origin/dev`) and green once AST-1842 is merged into `ftr/AST-1825-select-job-page-db-lock-loop-stall`.
- [X] Bible entries name the new node ids.
- [X] No existing test is weakened or deleted.

## Boundaries

* No product code. AST-1842 owns `agent.py` / `database.py` / `config.py` / `roster.py`.
* Does not add coverage beyond the three repros Betty named.

## Notes for planning

Sibling of AST-1842 (product fix). Board: `[board-betty] TESTS: REVISE`. What: docs/test-bible/core/roster.md + core/agent.md + data/database.md, missing coverage. No roster test holds PJL_READY on failure_class=provider_call_timeout (only the AST-897 balance-refusal hold exists; [roster.py](<http://roster.py>) LOCKED_AT_100 needs the new branch), no do_task loop-not-blocked test around save_agent_data, and no \_get_connection WAL/busy-timeout test. Blast radius breaks nothing existing. Plan-fix patch target: the same doc as AST-1842, `docs/features/agent/ast-1448-persist-prompt-before-provider.md`, appending a `## Bug: AST-1843` section. Test tree is Betty's (qa-fix lands the tests). Precedent: AST-1724 (gap child of AST-1723). Parent mini-epic: AST-1825.

## Git branch (authoritative)

Parent `ftr/AST-1825-select-job-page-db-lock-loop-stall`, child `sub/AST-1825/AST-1843-repro-coverage`. Created at bug-fix dispatch.

## QA test manifest

**qa-fix (Betty)** — `origin/sub/AST-1825/AST-1843-repro-coverage` @ `870e2a0f` (`merge-tests(AST-1843): origin/tests 7c40f2c4`).

`[bug-repro]` nodes (each must be red on pre-fix product, green with AST-1842):

1. `tests/component/core/test_roster.py::TestAst1842SelectJobPageTimeoutHold::test_find_job_page_provider_call_timeout_holds_pjl_ready`
2. `tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop::test_slow_save_agent_data_does_not_block_loop`
3. `tests/component/data/test_database.py::TestAst1842ConnectionWalBusyTimeout::test_get_connection_wal_and_configured_busy_timeout`

**Red** — throwaway worktree at `origin/dev` `31846c28` (pre-AST-1842) + these test files: 3 failed, right reason — (1) `'NO_JOBLIST' == 'PJL_READY'` (timeout saved as verdict); (2) heartbeat max gap `1.52s < 0.2` (5 × 0.3s stores on the loop); (3) `'delete' == 'wal'` (rollback journal).
**Green** — synced sub tip `50621b5e` (ftr with AST-1842) and merged tip `870e2a0f`: 3 passed. Timing test 5/5 stable (2.28s each).

Deviations from plan-fix spec (Betty's call): heartbeat ticks on every wake *before* checking `done` (spec shape missed the freeze — mocked provider never yields, so `do_task` finished inside one freeze and the gap was never recorded; test passed on pre-fix); prompt-store assertion is "any non-RESPONSE block" (real types: SYSTEM/CACHE_A/NO_CACHE/TASK); WAL test asserts literal `wal` first so pre-fix red is the journal mode, then busy_timeout from `ASTRAL_CONFIG["db_connection"]`.

Regression (run with the repros; no new reds):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst1842SelectJobPageTimeoutHold \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_roster.py::test_find_assembled_do_task_failure \
  tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider \
  tests/component/data/test_database.py::TestAst1842ConnectionWalBusyTimeout \
  -q
```

**Known pre-existing reds (red on** `origin/dev` **too — not AST-1842/1843):** `TestAst1448PersistPromptBeforeProvider::{test_do_task_debug_emits_prompt_found_recorded_before_provider, test_prompt_only_batch_is_not_latest_ref, test_bare_run_adhoc_does_not_store_agent_data}`; `test_database.py::TestAst846JobSchemaEnsureDedupeBeforeUniqueIndex` (5, fixture drift `job has no column named company`).

**Bible shasums (origin/tests):** `core/roster.md` a504615e554fbcee5e25796805ebdfbdf73fca2c · `core/agent.md` b700927a828f07a875d5fa5600f5df371bd6bcb2 · `data/database.md` 8b66a6bec48c929eeb47bacc1ac9397d9db454f7

### Comments

#### radia — 2026-09-28T15:25:34.016Z
[code-rubric] PROCEED (Commit: 38aa052d938a12acc2933d6bf73e5b104bc11763) Three bug-repros OK

#### betty — 2026-09-28T15:21:54.673Z
[bug-repro]
`origin/sub/AST-1825/AST-1843-repro-coverage` @ `870e2a0f` · 3 repros red→green
Red @ origin/dev 31846c28 (pre-AST-1842): 3 failed, right reason — NO_JOBLIST≠PJL_READY · loop gap 1.52s≥0.2 · journal delete≠wal.
Green @ sub tip 50621b5e / merged 870e2a0f: 3 passed. Nodes + manifest in issue doc ## QA test manifest.

#### joan — 2026-09-28T15:15:59.689Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T15:15:40.954Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/roster.md + core/agent.md + data/database.md — missing coverage (by design: this is the AST-1842 gap child) — land the 3 [bug-repro] tests at qa-fix: TestAst1842SelectJobPageTimeoutHold (roster), TestAst1842DoTaskStoreOffLoop (agent), TestAst1842ConnectionWalBusyTimeout (database) + bible rows; red on origin/dev, green on ftr 41e75150. Spec anchors verified on tests tree + ftr tip; nothing existing breaks.

#### ada — 2026-09-28T15:14:50.036Z
`origin/sub/AST-1825/AST-1843-repro-coverage` @ `39c7812e` · three repros + bible spec

---

_Implementation detail may live in git history on `origin/dev`._
