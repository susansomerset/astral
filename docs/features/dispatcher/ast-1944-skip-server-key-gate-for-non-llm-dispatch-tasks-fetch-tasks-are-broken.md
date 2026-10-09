# AST-1944 — Skip server-key gate for non-LLM dispatch tasks (fetch tasks are broken)

<!-- linear-archive: AST-1944 archived 2026-10-08 -->

## Linear archive (AST-1944)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1944/skip-server-key-gate-for-non-llm-dispatch-tasks-fetch-tasks-are-broken  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 1  
**Parent:** AST-1943 — fetch tasks are broken  
**Blocked by / blocks / related:** parent: AST-1943; blocks: AST-1945

### Description

## What this implements

Non-LLM dispatch tasks (`fetch_jd`, `recheck_no_openings`, and any `agent_task` row with `agent_id: "n/a"`, an empty `agent_id`, or no `agent_task` row) dispatch again. Today the AST-1879 per-server key gate in `_dispatch_one_body` (`src/core/dispatcher.py`) calls `task_llm_server_id(task_key)` for every task. That function calls `_resolve_task_prompts`, which raises `ValueError: Agent 'n/a' referenced by task '<key>' not found.`, so every fetch tick crashes before it starts. After this fix, tasks without an LLM agent skip the server-key check. The candidate-exists skip stays, and LLM-backed tasks keep the exact AST-1879 behavior (`candidate_api_keys[server_id]` required).

## Scope

### Component scope

* `src/core/agent.py` (modified): `task_llm_server_id` currently assumes every dispatch key has a real LLM agent, so it must tolerate non-LLM task keys.
* `src/core/dispatcher.py` (modified): the AST-1879 server-key gate in `_dispatch_one_body` must skip when the task has no LLM server and still enforce the candidate-exists check.
* `data/admin/agent_task.json` (modified): Susan's To-be: the non-LLM sentinel `agent_id` becomes `"telescope"` instead of `"n/a"` on every row that carries it (repo-wins at bootstrap).

### Technical scope

* `src/core/agent.py`: modified function. `task_llm_server_id` (or a new small predicate helper beside it) returns a "no LLM server" result for `agent_id` `"n/a"`, empty, or no `agent_task` row, instead of letting `_resolve_task_prompts` raise. Non-LLM tasks have no model, so there is no server to gate on.
* `src/core/dispatcher.py`: modified function. `_dispatch_one_body` makes the `candidate_api_keys[server_id]` check conditional on a server id existing, so non-LLM tasks reach their handlers as they did before AST-1879.
* `data/admin/agent_task.json`: modified data rows only. Every `"agent_id": "n/a"` becomes `"agent_id": "telescope"`. No new agent row, no schema change, and the "no LLM server" check in `src/core/agent.py` recognizes `"telescope"` as the sentinel in place of `"n/a"`.

## Acceptance criteria

* `agent_task.json` non-LLM rows carry `agent_id: "telescope"` (no `"n/a"` left).
* `fetch_jd` / `recheck_no_openings` with `agent_id: "telescope"` dispatch without raising, and their handlers run.
* A task with no `agent_task` row (AST-537 invariant: `gaze`, `recheck_no_openings`) does not raise at the key gate.
* An LLM-backed task whose candidate has no key for its agent's server is still skipped with the AST-1879 warning.
* A missing candidate row is still skipped.
* `_resolve_task_prompts` stays strict for `do_task` / preview callers.

## Boundaries

* No change to `api_admin` dispatch Run/Auto gate (AST-1880's area).
* `agent_task.json`: only the `"n/a"` → `"telescope"` sentinel rename (per AST-1943 § To-be). No other row or field changes, and no new `telescope` agent row.

## Notes for planning

As-is / To-be / Proposed steps: see mini-parent AST-1943 Description. Regression source: AST-1879 commit `85d426b0f`.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1943-non-llm-dispatch-key-gate`, child `sub/AST-1943/<child-segment>`. Created at bug-fix.

### Comments

#### radia — 2026-10-02T19:28:46.121Z
[code-rubric] PROCEED (Commit: 1c91606a2) Non-LLM gate clean

#### katherine — 2026-10-02T19:26:51.335Z
`origin/sub/AST-1943/AST-1944-skip-key-gate-non-llm-tasks` @ `1c91606a2` (no new commits). Lighter check: qa-fix didn't run, so there was no manifest or `[bug-repro]`.

Ran `tests/component/core/test_dispatcher.py`, `test_repo_admin_json.py`, and `test_agent_ast1879.py` on the sub branch and on `origin/ftr/AST-1943-non-llm-dispatch-key-gate`. Python 3.14 from `/home/susan/astral/.venv`, the only interpreter available; nothing installed.

**No new product failures.**
- `test_agent_ast1879.py`: same results on both trees, nothing new.
- `test_dispatcher.py`: 164 setup errors on the sub branch, all `AttributeError: src.core.dispatcher has no attribute 'task_llm_server_id'` from the autouse `_task_server_anthropic` fixture. I re-ran it with a throwaway `/tmp` pytest plugin (nothing in `tests/`) that points `task_llm_server_id_or_none` at the patched name: **12 failed / 152 passed, the exact same 12 failures as ftr, 0 new.**
- `test_repo_admin_json.py`: the 18 failures shared with ftr were already failing before this change.

**Owned by AST-1945** (they pin the old sentinel or the old import, so they don't count against Tests Passed):
1. `test_dispatcher.py`: the autouse `_task_server_anthropic` fixture and `TestDispatchOne::test_gate_reads_key_for_task_agents_server` patch `src.core.dispatcher.task_llm_server_id` and need to retarget to `task_llm_server_id_or_none`. Today this errors every test in the file.
2. `test_repo_admin_json.py::TestAst1269AliasAgentTaskSeedRestore::test_alias_identity_lockstep_with_fixture`: **new on the sub branch, and not in the expected list.** It asserts lockstep between `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json`, and fails with `('meteorite_grade_do', 'agent_id'): 'telescope' == 'n/a'`. The plan left that UAT fixture untouched, so Betty decides between updating the fixture's 12 rows and relaxing the test.
3. `"n/a"` assertions at L506 (the class is `@pytest.mark.skip`), and at L1378 / L1423 (those tests already fail on ftr for other reasons). They need flipping to `"telescope"` once they run.

#### joan — 2026-10-02T19:22:31.074Z
[board-joan]  CANON: OK

Registry skim (not R1–R7): `astral.seed.agent-tables-in-repo-json` — renaming `agent_id` on the 12 non-LLM rows in `data/admin/agent_task.json` (`n/a` → `telescope`, no new `agent.json` row) is an Archie-approved repo-seed edit on the explicit Revert-to-file path; aligns with kill-switch / no boot-apply law. `task_llm_server_id_or_none` + gated `_dispatch_one_body` check restores the AST-537 / pre–AST-1879 dispatch invariant without weakening AST-1879 per-server key law for real LLM routes; no in-force directive encodes `"n/a"` as the canonical non-LLM sentinel or forbids `telescope`.

`astral.standards.no-hardcoded-sets`: the `("", "telescope")` tuple interprets seed `agent_id` semantics (plus empty / missing row), not a parallel TASK_CONFIG membership set — no REVISE.

**TRANSITION-WINDOW (`("", "telescope", "n/a")`):** Canon-neutral either way. Adopting accepts live DB rows still on `"n/a"` until each env runs `POST …/revert/agent_task`; consistent with seed statute’s repo-vs-DB split and does not require a new carve-out in corpus. Default-only `telescope` is also canon-OK but widens the post-deploy crash window where revert lags — ops, not statute. **Joan: adopt the transition tuple in make-fix** (one-line removal follow-up comment); no F3 unless Archie later wants sentinel semantics written into a directive (optional, not fix-board REVISE).

context_tokens≈8500

#### betty — 2026-10-02T19:20:41.862Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/dispatcher.md (AST-1879 / AST-537) — missing coverage + broken tests — the autouse `_task_server_anthropic` fixture in tests/component/core/test_dispatcher.py pins `task_llm_server_id` → "anthropic" for every dispatcher test, so no test runs the real non-LLM gate (that is how the regression shipped). Fix renames the import, so that fixture plus `test_gate_reads_key_for_task_agents_server` (L33, L1078) must retarget to `task_llm_server_id_or_none`. tests/component/core/test_repo_admin_json.py L506/L1378/L1423 assert `agent_id == "n/a"` and must flip to "telescope". qa-fix needs a [bug-repro]: `_dispatch_one_body` with an unpatched resolver for a telescope / empty / no-row key reaches the handler (red on origin/dev); also unit tests for `task_llm_server_id_or_none` in agent.md (telescope→None, unknown agent re-raises, stage_email_meteorite fold still resolves to a server). The plan's §5 list matches. The transition-window "n/a" tuple is a product/deploy call, not a test call. Tests work the same under either default.

#### katherine — 2026-10-02T19:19:55.586Z
`origin/sub/AST-1943/AST-1944-skip-key-gate-non-llm-tasks` @ `bdbc2ca46` · telescope rename folded in

#### chuckles — 2026-10-02T19:18:34.426Z
@Katherine Johnson Option 2: rename to `"telescope"`. Susan added that line to AST-1943 § To-be before she approved it, and the Boundaries clause you hit was a filing mistake. I've amended the Component scope / Technical scope on AST-1943 and the `## Scope` / Boundaries / AC on AST-1944 to add `data/admin/agent_task.json` (every `"n/a"` becomes `"telescope"`, no new agent row). The sentinel check recognizes `"telescope"` instead of `"n/a"`. If you think the live DB needs a transition window that also accepts `"n/a"`, put it in the plan as an explicit item for the board to weigh. Don't add it silently.

#### katherine — 2026-10-02T19:17:46.207Z
[scope-gate] @susan

`origin/sub/AST-1943/AST-1944-skip-key-gate-non-llm-tasks` @ `a60b6c1e9`. The plan is drafted in `docs/features/dispatcher/ast-537-…-no-openings.md` § Bug: AST-1944.

The gate fix fits this ticket's Scope (`src/core/agent.py`: new helper `task_llm_server_id_or_none`; `src/core/dispatcher.py`: the key check runs only when a server id exists). One instruction conflicts and needs your call before Plan Ready:

- AST-1943 § To-be: *"Use 'telescope' instead of 'n/a' for the agent_id."*
- AST-1944 § Boundaries: *"No change to `agent_task.json` rows. `"n/a"` stays a valid sentinel."*
- AST-1944 § Scope names only `agent.py` and `dispatcher.py`. It does not include `data/admin/agent_task.json` (12 `"n/a"` rows, repo-wins at bootstrap).

Which one wins?
1. **Keep `"n/a"`** (the Boundaries as written). The plan stands as-is.
2. **Rename to `"telescope"`.** Scope gains `data/admin/agent_task.json`, and the sentinel tuple becomes `("", "telescope")`, or `("", "n/a", "telescope")` during the transition. Betty's side picks up `test_repo_admin_json.py`. No `telescope` agent row is proposed.

After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
