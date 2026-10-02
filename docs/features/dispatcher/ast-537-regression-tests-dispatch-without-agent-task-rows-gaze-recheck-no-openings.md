# AST-537 — Regression tests: dispatch without agent_task rows (gaze, recheck_no_openings)

<!-- linear-archive: AST-537 archived 2026-06-23 -->

## Linear archive (AST-537)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-537/regression-tests-dispatch-without-agent-task-rows-gaze-recheck-no  
**Status at archive:** Done  
**Project:** Astral Dispatcher (inherited from AST-533)  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-533 — BUG: Scheduled Actions ignore dispatch task_key — consult hardcodes state→task routing  
**Blocked by / blocks / related:** parent: AST-533

### Description

## Purpose

**AST-531** `_dispatch_one` probes `run_next` via `_current_agent_task_run_next` for every scheduled row. Non-LLM dispatch keys (`gaze`, `recheck_no_openings`, …) have no `agent_task` row — runtime must not require Manage Tasks seeding for those hops.

Hotfix (AST-533 UAT): `_current_agent_task_run_next` returns `''` when `get_agent_task` is missing.

## Scope

* Component test: `_dispatch_one` does not raise for `task_key=gaze` / `recheck_no_openings` when no `agent_task` row (mock candidate + dispatch loop).
* Optional: stub LLM path vs Playwright-only path so we catch regressions without live agent_task DB rows.

## Parent

AST-533 — dispatch task_key honesty epic.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._

## Bug: AST-1944 — Skip server-key gate for non-LLM dispatch tasks (fetch tasks are broken)

Mini-parent: AST-1943. Regression source: AST-1879 Stage 3, commit `85d426b0f` (`docs/features/agent/ast-1879-route-agent-calls-by-model-server.md`). This bug breaks the invariant stated in § Purpose above: non-LLM dispatch keys must not need agent/agent_task resolution at dispatch time.

### As-is

Every scheduled non-LLM dispatch task crashes before its handler runs. Affected tasks are `fetch_jd`, `recheck_no_openings`, `gaze`, and every other `agent_task` row whose `agent_id` is `"n/a"` or empty. `_dispatch_one_body` (`src/core/dispatcher.py:1342`) calls `task_llm_server_id(task_key)` for every task. That call goes through `_resolve_task_prompts`, and `get_agent("n/a")` returns `None`, so it raises `ValueError: Agent 'n/a' referenced by task '<key>' not found.` `_task_thread_target` then logs `dispatch task <key> crashed`.

### To-be

A task with no LLM agent skips the per-server key check and reaches its handler, as it did before AST-1879. "No LLM agent" means an `agent_id` of `"n/a"`, an empty `agent_id`, or no `agent_task` row. A missing candidate row is still skipped. LLM-backed tasks keep the AST-1879 behavior exactly: they need `candidate_api_keys[server_id]` for their agent's server, and a misconfigured LLM task still raises loudly. `_resolve_task_prompts` stays strict for `do_task` and preview.

### Repro

Verified on `origin/dev` (contains `85d426b0f`). Line 1342 is `server_id = task_llm_server_id(task_key)`. Before the commit, the gate was `if not ctx or not ctx.get("candidate_api_key")`.

Fixture (repo data, `data/admin/agent_task.json`, unchanged):

```json
{"task_key": "fetch_jd", "agent_id": "n/a"}
{"task_key": "recheck_no_openings", "agent_id": "n/a"}
```

Steps: call `_dispatch_one_body({"task_key": "fetch_jd", "candidate_id": "<any existing candidate>", ...}, debug=False)` with the real `get_agent_task`. `get_agent("n/a")` is `None`, so it raises `ValueError` from `src/core/agent.py:550` before any handler runs. The same thing happens for `recheck_no_openings`, and for a `task_key` with no `agent_task` row (`No agent_task row for '<key>'`). Production log in AST-1943 § Original report.

Other non-LLM rows on the same path today: `inflow_discovery`, `find_company_website`, `fetch_website`, `fetch_job_pages`, `gaze`, `fetch_culture_pages`, `meteorite_grade_do`, `meteorite_grade_get`, `scrape_meteorite`, `land_meteorite` (all `"n/a"`). Also `bootstrap_candidate_context`, `stage_email_meteorite`, `propose_application_responses` (empty `agent_id`).

### Root cause

AST-1879 replaced the candidate-has-any-key check with a per-server check. To find the server it unconditionally resolves the task's agent row through `_resolve_task_prompts`. That function is deliberately strict: it raises on a missing row, an empty `agent_id`, or an unknown agent. So the gate now assumes every dispatch key is LLM-backed. The admin Run/Auto twin (`_candidate_dispatch_api_key_error`, `src/ui/api/api_admin.py:2058`) already catches `ValueError` and returns "no key required". The dispatcher path got no such carve-out.

### Proposed change

1. **`src/core/agent.py`: new helper directly below `task_llm_server_id`.** `task_llm_server_id` itself is unchanged.

   ```python
   def task_llm_server_id_or_none(task_key: str) -> Optional[str]:
       """task_llm_server_id, or None when the task has no LLM agent (AST-1944).

       No agent_task row, empty agent_id, or the "n/a" sentinel → no model, no server to gate on.
       Any other resolution failure (unknown real agent, missing model_id) still raises — a
       misconfigured LLM task must stay loud.
       """
       try:
           return task_llm_server_id(task_key)
       except ValueError:
           row = get_agent_task(resolve_task_key_for_content(task_key))
           if ((row or {}).get("agent_id") or "").strip() in ("", "n/a"):
               return None
           raise
   ```

   - It tries the strict path first. That way the `stage_email_meteorite` mailbox fold in `_resolve_task_prompts` (empty `agent_id` falls back to `parse_meteorite_email`) still resolves to a real server and stays gated. Only if the fold also finds no agent does the empty `agent_id` count as non-LLM.
   - It re-raises when `agent_id` names a real but missing agent, or a real agent with no `model_id` / `brain_setting`. That matches AST-1879 today (dispatch crashes loudly), not a silent bypass.

2. **`src/core/dispatcher.py` `_dispatch_one_body`, lines 1341–1354.** In the line-30 import, replace `task_llm_server_id` with `task_llm_server_id_or_none`. Line 1342 is its only use in this module. Apply the server check only when a server id comes back:

   ```python
   # AST-1879: the key for the task agent's server only — another platform's key does not count.
   # AST-1944: no LLM agent (n/a / empty / no agent_task row) → no server to gate; candidate check stays.
   server_id = task_llm_server_id_or_none(task_key)
   if not ctx or (server_id and not (ctx.get("candidate_api_keys") or {}).get(server_id)):
   ```

   The skip debug/warning block stays as-is. For a non-LLM task it fires only when `ctx` is missing, and its `server_id` slot then prints `None`, which is acceptable for a debug/warning line.

3. **No other files.** `_resolve_task_prompts`, `task_llm_server_id`, `api_admin` (AST-1880's area), `monitor.provider_balance_outage`, and `agent_task.json` are untouched.

4. **Regression coverage is Betty's call (qa-fix).** Suggested cases follow AST-1944's acceptance criteria:
   - `fetch_jd` / `recheck_no_openings` with `agent_id: "n/a"` reach the handler.
   - A key with no `agent_task` row does not raise at the gate.
   - An LLM task whose candidate lacks its server key is skipped with the AST-1879 warning.
   - A missing candidate is skipped.
   - An `agent_id` naming an unknown agent still raises.

Alternatives considered and rejected:
- Change `task_llm_server_id` to return `Optional[str]`. This breaks `api_admin._candidate_dispatch_api_key_error` (`get_llm_server(None)`), which is out of scope.
- Bare `try/except ValueError` in the dispatcher, the same as `api_admin`. This silently lets misconfigured LLM tasks past the gate.
- Extract the row lookup out of `_resolve_task_prompts`. That is a bigger refactor of a strict function the AC says to leave alone.

**Open decision: needs Susan before Plan Ready (`[scope-gate]` on AST-1944).** AST-1943 § To-be says *"Use 'telescope' instead of 'n/a' for the agent_id."* AST-1944 § Boundaries says *"No change to `agent_task.json` rows. `"n/a"` stays a valid sentinel."* AST-1944 § Scope names only `agent.py` and `dispatcher.py`. If the rename is wanted:
- Scope gains `data/admin/agent_task.json`, which is repo-wins at bootstrap (`src/data/database.py:6315`): 12 `"n/a"` rows become `"telescope"`.
- The sentinel tuple in step 1 becomes `("", "n/a", "telescope")` or `("", "telescope")`.
- Betty's side picks up `tests/component/core/test_repo_admin_json.py`, which asserts `"n/a"`.
- No `telescope` agent row exists in `data/admin/agent.json`, and none is proposed: a row with no `model_id` would still raise in `_agent_llm_route`.

Steps 1–3 above stand either way. Only the sentinel literal and the data file differ.

### Blast radius

- `_dispatch_one_body` is the single entry for every scheduled and AUTO dispatch tick. Today all non-LLM keys are down, and after the fix they run again.
- Other `task_llm_server_id` callers are unchanged: `api_admin._candidate_dispatch_api_key_error` (already tolerant via `except ValueError`) and `monitor.provider_balance_outage` (fires only for LLM balance refusals).
- `_resolve_task_prompts` callers (`do_task`, preview, empty-render) are unchanged.
- `tests/component/core/test_dispatcher.py` mocks `task_llm_server_id` and must retarget to `src.core.dispatcher.task_llm_server_id_or_none` (Betty, qa-fix). `test_agent_ast1879.py`, `test_monitor.py`, and `test_api_admin.py` reference the unchanged function.

### What must still hold

- AST-537: dispatch for `gaze` / `recheck_no_openings` must not need an `agent_task` row or agent seeding.
- AST-1879: an LLM task needs the candidate's key for *its agent's* server. Another platform's key does not count, and the skip warning text is unchanged.
- A missing candidate row is still skipped before any handler.
- `_resolve_task_prompts` raises on a missing row, an empty `agent_id`, or an unknown agent, for `do_task` / preview.
- The `stage_email_meteorite` → `parse_meteorite_email` fold still resolves to a real agent and stays gated.
- `api_admin` Run/Auto key gate behavior is unchanged (AST-1880).
