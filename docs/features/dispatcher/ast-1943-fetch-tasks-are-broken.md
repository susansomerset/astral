# AST-1943 — fetch tasks are broken

<!-- linear-archive: AST-1943 archived 2026-10-08 -->

## Linear archive (AST-1943)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1943/fetch-tasks-are-broken  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Every scheduled non-LLM dispatch task (`fetch_jd`, `recheck_no_openings`, and any other `agent_task` row with `agent_id: "n/a"`) crashes before it starts. `_dispatch_one_body` in `src/core/dispatcher.py` (line \~1342) now calls `task_llm_server_id(task_key)` for every task as part of the [AST-1879](https://linear.app/astralcareermatch/issue/AST-1879/route-agent-calls-by-model-server-support-openrouter-api-models-for) per-server API-key gate. That function calls `_resolve_task_prompts`, which looks up agent `'n/a'`, fails to find it, and raises `ValueError: Agent 'n/a' referenced by task '<key>' not found.` The thread target logs `dispatch task <key> crashed`, and no fetch runs.

Before [AST-1879](https://linear.app/astralcareermatch/issue/AST-1879/route-agent-calls-by-model-server-support-openrouter-api-models-for) (commit `85d426b0f`), this gate only checked that the candidate had *some* `candidate_api_key`. It never resolved an agent, so non-LLM tasks passed.

## To-be

Non-LLM dispatch tasks run again. They have no LLM agent, so the per-server key gate does not apply to them. That covers an `agent_id` of `"n/a"`, an empty `agent_id`, or no `agent_task` row at all, as AST-537 requires for `gaze` / `recheck_no_openings`. The dispatcher still skips when the candidate row is missing. LLM-backed tasks keep the [AST-1879](https://linear.app/astralcareermatch/issue/AST-1879/route-agent-calls-by-model-server-support-openrouter-api-models-for) behavior exactly: they need `candidate_api_keys[server_id]` for their agent's server.

Use "telescope" instead of "n/a" for the agent_id.

## Proposed steps

1. Teach `task_llm_server_id` (or a small sibling helper next to it in `src/core/agent.py`) to answer "this task has no LLM agent" instead of raising. That case covers a missing `agent_task` row, an empty `agent_id`, and the `"n/a"` sentinel. It returns `None` (or a falsy value) rather than calling `_resolve_task_prompts`.
2. In `_dispatch_one_body`, apply the server-key check only when a server id comes back. With no server id, keep only the `not ctx` (missing candidate) skip and carry on into the task.
3. Leave `_resolve_task_prompts` itself strict, because `do_task` and preview callers still need it to raise on a misconfigured LLM task.
4. Rename the non-LLM sentinel `"n/a"` → `"telescope"` in `data/admin/agent_task.json` and in the step-1 check.
5. Regression coverage (Betty's call): `fetch_jd` / `recheck_no_openings` with `agent_id: "telescope"` dispatch without raising, and an LLM task with no key for its server is still skipped.

## Component scope

* `src/core/agent.py` (modified): `task_llm_server_id` currently assumes every dispatch key has a real LLM agent, so it must tolerate non-LLM task keys.
* `src/core/dispatcher.py` (modified): the [AST-1879](https://linear.app/astralcareermatch/issue/AST-1879/route-agent-calls-by-model-server-support-openrouter-api-models-for) server-key gate in `_dispatch_one_body` must skip when the task has no LLM server and still enforce the candidate-exists check.
* `data/admin/agent_task.json` (modified): Susan's To-be: the non-LLM sentinel `agent_id` becomes `"telescope"` instead of `"n/a"` on every row that carries it (repo-wins at bootstrap).

## Technical scope

* `src/core/agent.py`: modified function. `task_llm_server_id` (or a new small predicate helper beside it) returns a "no LLM server" result for `agent_id` `"n/a"`, empty, or no `agent_task` row, instead of letting `_resolve_task_prompts` raise. Non-LLM tasks have no model, so there is no server to gate on.
* `src/core/dispatcher.py`: modified function. `_dispatch_one_body` makes the `candidate_api_keys[server_id]` check conditional on a server id existing, so non-LLM tasks reach their handlers as they did before [AST-1879](https://linear.app/astralcareermatch/issue/AST-1879/route-agent-calls-by-model-server-support-openrouter-api-models-for).
* `data/admin/agent_task.json`: modified data rows only. Every `"agent_id": "n/a"` becomes `"agent_id": "telescope"`. No new agent row, no schema change, and the "no LLM server" check in `src/core/agent.py` recognizes `"telescope"` as the sentinel in place of `"n/a"`.

## Ancestor candidates

- [ ] AST-1879: Route agent calls by model → server (`docs/features/agent/ast-1879-route-agent-calls-by-model-server.md`). It introduced the `task_llm_server_id` dispatcher gate (commit `85d426b0f`) that crashes here. This is the direct regression source.
- [ ] AST-537: Regression tests, dispatch without agent_task rows (`docs/features/dispatcher/ast-537-regression-tests-dispatch-without-agent-task-rows-gaze-recheck-no-openings.md`). It states the invariant this breaks: non-LLM dispatch keys must not require agent/task seeding at dispatch time.
- [ ] AST-1880: Admin model pickers / platform keys (`docs/features/agent/ast-1880-admin-model-pickers-platform-keys.md`). This is AST-1879's follow-on (#4) that owns the `api_admin` dispatch Run/Auto key gate. That gate may need the same non-LLM carve-out.
- [ ] AST-1443: Update agent_task.json (`docs/features/agent/ast-1443-update-agent-taskjson.md`). It is the source of the `agent_id: "n/a"` rows for `fetch_jd` / `recheck_no_openings`.

## Original report

```
2026-10-02T19:04:44.825804494Z [err]  src.core.dispatcher: somerset | dispatch task recheck_no_openings crashed
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1647, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 1002, in _dispatch_one
    await _dispatch_one_body(task, debug)
  File "/app/src/core/dispatcher.py", line 1342, in _dispatch_one_body
    server_id = task_llm_server_id(task_key)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 1838, in task_llm_server_id
    agent_row, _ = _resolve_task_prompts(task_key)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 550, in _resolve_task_prompts
    raise ValueError(
ValueError: Agent 'n/a' referenced by task 'recheck_no_openings' not found.
2026-10-02T19:04:55.912870697Z [err]  src.core.dispatcher: somerset | dispatch task fetch_jd crashed
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1647, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 1002, in _dispatch_one
    await _dispatch_one_body(task, debug)
  File "/app/src/core/dispatcher.py", line 1342, in _dispatch_one_body
    server_id = task_llm_server_id(task_key)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 1838, in task_llm_server_id
    agent_row, _ = _resolve_task_prompts(task_key)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 550, in _resolve_task_prompts
    raise ValueError(
ValueError: Agent 'n/a' referenced by task 'fetch_jd' not found.
2026-10-02T19:06:11.586520329Z [err]  src.core.dispatcher: somerset | dispatch task fetch_jd crashed
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1647, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 1002, in _dispatch_one
    await _dispatch_one_body(task, debug)
  File "/app/src/core/dispatcher.py", line 1342, in _dispatch_one_body
    server_id = task_llm_server_id(task_key)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 1838, in task_llm_server_id
    agent_row, _ = _resolve_task_prompts(task_key)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 550, in _resolve_task_prompts
    raise ValueError(
ValueError: Agent 'n/a' referenced by task 'fetch_jd' not found.
2026-10-02T19:07:55.319360460Z [err]  src.core.dispatcher: somerset | dispatch task fetch_jd crashed
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1647, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 1002, in _dispatch_one
    await _dispatch_one_body(task, debug)
  File "/app/src/core/dispatcher.py", line 1342, in _dispatch_one_body
    server_id = task_llm_server_id(task_key)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 1838, in task_llm_server_id
    agent_row, _ = _resolve_task_prompts(task_key)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 550, in _resolve_task_prompts
    raise ValueError(
ValueError: Agent 'n/a' referenced by task 'fetch_jd' not found.
```

### Comments

#### chuckles — 2026-10-02T19:45:17.771Z
@susan PR #209 is ready for review. One required deploy step and one open decision before UAT are in the PR comment: the `agent_task` Revert-to-file per environment, and an optional `"n/a"` bridge, which is not adopted.

---

_Implementation detail may live in git history on `origin/dev`._
