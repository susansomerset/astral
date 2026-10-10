# AST-1945 — Non-LLM dispatch gate tests + telescope sentinel (test gap for AST-1944)

<!-- linear-archive: AST-1945 archived 2026-10-08 -->

## Linear archive (AST-1945)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1945/non-llm-dispatch-gate-tests-telescope-sentinel-test-gap-for-ast-1944  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 1  
**Parent:** AST-1943 — fetch tasks are broken  
**Blocked by / blocks / related:** parent: AST-1943

### Description

## What this implements

Test gap from fix-board on AST-1944 (`[board-betty] TESTS: REVISE`). The autouse `_task_server_anthropic` fixture in `tests/component/core/test_dispatcher.py` pins `task_llm_server_id` → `"anthropic"` for every dispatcher test, so no test exercises the real non-LLM gate. That is how the AST-1879 regression shipped. AST-1944 renames the dispatcher import to `task_llm_server_id_or_none` and flips the 12 `agent_task.json` sentinels `"n/a"` → `"telescope"`, so the existing tests that pin either one break. The bible's AST-1879 / AST-537 dispatcher entries don't describe the non-LLM gate carve-out.

## Scope

### Component scope

* `tests/component/core/test_dispatcher.py` (modified): retarget the autouse `_task_server_anthropic` fixture and `test_gate_reads_key_for_task_agents_server` from `task_llm_server_id` to `task_llm_server_id_or_none`. Add the `[bug-repro]`: `_dispatch_one_body` with an unpatched resolver for a `telescope` / empty / no-row key reaches the handler (red on `origin/dev`). An LLM task missing its server key and a missing candidate are still skipped.
* `tests/component/core/test_repo_admin_json.py` (modified): the `agent_id == "n/a"` assertions (L506 / L1378 / L1423) flip to `"telescope"`.
* `tests/component/core/` agent tests (modified or new, Betty's file choice): unit tests for `task_llm_server_id_or_none`. `telescope` → `None`, empty / no-row → `None`, an unknown real agent still raises, and the `stage_email_meteorite` → `parse_meteorite_email` fold still resolves to a server.
* `docs/uat-fixtures/AST-756/expected-agent_task.json` (modified, or the test relaxed: Betty's call): `test_alias_identity_lockstep_with_fixture` compares `agent_task.json` to this snapshot, which still carries the 12 `"n/a"` rows.
* `docs/test-bible/core/dispatcher.md` (modified): AST-1879 / AST-537 entries document the non-LLM gate carve-out and the new repro.
* `docs/test-bible/core/agent.md` (modified): entry for `task_llm_server_id_or_none`.

### Technical scope

* Test files: modified test functions and fixtures plus new test functions only. No product code (that is AST-1944).
* Bible files: modified/added entries only.

## Acceptance criteria

* The `[bug-repro]` dispatcher test is red against `origin/dev` and green on `origin/ftr/AST-1943-non-llm-dispatch-key-gate` once AST-1944 is merged.
* No dispatcher test pins the resolver for the non-LLM repro path.
* The `test_repo_admin_json.py` sentinel assertions read `"telescope"`.
* Bible entries match the tests.

## Boundaries

* No product changes (`src/**`, `data/**`) here. Those are AST-1944.
* No `"n/a"` transition-window tests. The sentinel tuple is `("", "telescope")` unless Susan decides otherwise.

## Notes for planning

Filed from Betty's `[board-betty] TESTS: REVISE` on AST-1944. Plan doc to patch: `docs/features/dispatcher/ast-537-regression-tests-dispatch-without-agent-task-rows-gaze-recheck-no-openings.md` (`## Bug: <this ticket>` block). Blocked by AST-1944.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1943-non-llm-dispatch-key-gate`, child `sub/AST-1943/<child-segment>`. Created at bug-fix.

### Comments

#### radia — 2026-10-02T19:44:36.494Z
[code-rubric] PROCEED (Commit: 5cde1c750) Bug-repro gate tests OK

#### katherine — 2026-10-02T19:42:36.633Z
`origin/sub/AST-1943/AST-1945-non-llm-gate-tests-clean` @ `5cde1c750` · no product change needed

#### chuckles — 2026-10-02T19:41:21.577Z
Publish ref moved to `sub/AST-1943/AST-1945-non-llm-gate-tests-clean` (registry updated). The `merge-tests` on the original `sub/AST-1943/AST-1945-non-llm-gate-tests` pulled AST-1940's unshipped epic in through shared `origin/tests` history: AST-1941's `code()` in `src/core/agent.py`, AST-1942's tests, and their docs. The clean ref is `3a2da94aa`, plus `test(AST-1945)` cherry-picked from `d273f6017` (byte-identical for every AST-1945 file), plus one `merge-tests(AST-1945)`. The old ref is left untouched. @Betty White: heads-up that `origin/tests` now carries `ftr/AST-1940`, so any merge-tests onto another epic's sub will drag it along until AST-1940 lands on dev.

#### betty — 2026-10-02T19:39:48.647Z
[bug-repro]
`origin/sub/AST-1943/AST-1945-non-llm-gate-tests` @ `8d557e83d` · repro red on dev, green ftr

#### joan — 2026-10-02T19:32:30.964Z
[board-joan]  CANON: OK

Registry skim (not R1–R7; no `docs/canon-index.md` on publish ref `origin/sub/AST-1943/AST-1945-non-llm-gate-tests`): scope is `tests/**`, `docs/test-bible/**`, and `docs/uat-fixtures/AST-756/expected-agent_task.json` only — no in-force statute or pattern amendment. `astral.seed.agent-tables-in-repo-json` already treats UAT fixture twins as non-authoritative mirrors; updating the AST-756 lockstep file’s 12 `"n/a"` → `"telescope"` literals to match repo seed on ftr is alignment, not a second source of truth. Bible rows documenting `task_llm_server_id_or_none`, the `real_server_gate` opt-out, and `[bug-repro]` non-LLM gate behavior describe product law already on ftr (AST-1944); they do not introduce new carve-outs. Plan pins tests to `("", "telescope")` only (no `"n/a"` transition coverage) — canon-neutral with Joan’s AST-1944 board note that dual-sentinel adoption was product/ops, not corpus REVISE.

context_tokens≈12000

#### betty — 2026-10-02T19:31:57.187Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/dispatcher.md (AST-1879/AST-1944) + core/agent.md + core/repo_admin_json.md — broken tests + missing coverage — this ticket is the test work, so qa-fix must land all 7 plan steps. On ftr 6398b5d32: the autouse stub breaks every test in test_dispatcher.py, there is no real-resolver non-LLM gate test, `task_llm_server_id_or_none` has no unit tests, and three test_repo_admin_json.py sentinel asserts plus the AST-756 lockstep fail on "n/a". I checked the plan's mechanics and they hold: `_dispatch_one` is try/finally only, so a ValueError reaches `pytest.raises` and the repro is red on origin/dev; `get_agent_task`/`get_agent` are module-level names in agent.py, so patching `agent_mod` covers the real resolver; `--strict-markers` justifies the `real_server_gate` fixture over a marker; the fixture has exactly 12 "n/a". One routing note for Chuckles: step 5 edits `docs/uat-fixtures/AST-756/expected-agent_task.json`, which is neither the test tree nor the bible, and engineers have historically updated it as a `code()` "fixture twin" (AST-1910, AST-1784). Betty will take it in qa-fix unless you route it to the engineer. L1378/L1423 stay red on the pre-existing task_seq drift, which is out of scope.

#### katherine — 2026-10-02T19:30:53.455Z
`origin/sub/AST-1943/AST-1945-non-llm-gate-tests` @ `660827534` · repro, retarget, telescope, fixture

---

_Implementation detail may live in git history on `origin/dev`._
