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

The non-LLM sentinel in `data/admin/agent_task.json` is `"telescope"` in place of `"n/a"` (AST-1943 § To-be). A task with no LLM agent skips the per-server key check and reaches its handler, as it did before AST-1879. "No LLM agent" means an `agent_id` of `"telescope"`, an empty `agent_id`, or no `agent_task` row. A missing candidate row is still skipped. LLM-backed tasks keep the AST-1879 behavior exactly: they need `candidate_api_keys[server_id]` for their agent's server, and a misconfigured LLM task still raises loudly. `_resolve_task_prompts` stays strict for `do_task` and preview.

### Repro

Verified on `origin/dev` (contains `85d426b0f`). Line 1342 is `server_id = task_llm_server_id(task_key)`. Before the commit, the gate was `if not ctx or not ctx.get("candidate_api_key")`.

Fixture (repo data, `data/admin/agent_task.json`, before the fix):

```json
{"task_key": "fetch_jd", "agent_id": "n/a"}
{"task_key": "recheck_no_openings", "agent_id": "n/a"}
```

Steps: call `_dispatch_one_body({"task_key": "fetch_jd", "candidate_id": "<any existing candidate>", ...}, debug=False)` with the real `get_agent_task`. `get_agent("n/a")` is `None`, so it raises `ValueError` from `src/core/agent.py:550` before any handler runs. The same thing happens for `recheck_no_openings`, and for a `task_key` with no `agent_task` row (`No agent_task row for '<key>'`). Production log in AST-1943 § Original report.

Other non-LLM rows on the same path today: `inflow_discovery`, `find_company_website`, `fetch_website`, `fetch_job_pages`, `gaze`, `fetch_culture_pages`, `meteorite_grade_do`, `meteorite_grade_get`, `scrape_meteorite`, `land_meteorite` (all `"n/a"`). Also `bootstrap_candidate_context`, `stage_email_meteorite`, `propose_application_responses` (empty `agent_id`).

### Root cause

AST-1879 replaced the candidate-has-any-key check with a per-server check. To find the server it unconditionally resolves the task's agent row through `_resolve_task_prompts`. That function is deliberately strict: it raises on a missing row, an empty `agent_id`, or an unknown agent. So the gate now assumes every dispatch key is LLM-backed. The admin Run/Auto twin (`_candidate_dispatch_api_key_error`, `src/ui/api/api_admin.py:2058`) already catches `ValueError` and returns "no key required". The dispatcher path got no such carve-out.

### Proposed change

1. **`data/admin/agent_task.json`: sentinel rename, data rows only.** Change every `"agent_id": "n/a"` to `"agent_id": "telescope"`. There are exactly 12 rows: `inflow_discovery`, `find_company_website`, `fetch_website`, `fetch_job_pages`, `recheck_no_openings`, `gaze`, `fetch_jd`, `fetch_culture_pages`, `meteorite_grade_do`, `meteorite_grade_get`, `scrape_meteorite`, `land_meteorite`.
   - Change no other field. `updated_at` and `task_key_uuid` stay as they are.
   - Rows with an empty `agent_id` (`bootstrap_candidate_context`, `stage_email_meteorite`, `propose_application_responses`) stay empty.
   - Don't add a `telescope` row to `data/admin/agent.json`.
   - Do the edit as a literal string replace so the file's key order and formatting are unchanged. Afterwards `rg -c '"n/a"' data/admin/agent_task.json` must print nothing, and `rg -c '"agent_id": "telescope"' data/admin/agent_task.json` must print `12`.

2. **`src/core/agent.py`: new helper directly below `task_llm_server_id`.** `task_llm_server_id` itself is unchanged.

   ```python
   def task_llm_server_id_or_none(task_key: str) -> Optional[str]:
       """task_llm_server_id, or None when the task has no LLM agent (AST-1944).

       No agent_task row, empty agent_id, or the "telescope" sentinel → no model, no server to gate on.
       Any other resolution failure (unknown real agent, missing model_id) still raises — a
       misconfigured LLM task must stay loud.
       """
       try:
           return task_llm_server_id(task_key)
       except ValueError:
           row = get_agent_task(resolve_task_key_for_content(task_key))
           if ((row or {}).get("agent_id") or "").strip() in ("", "telescope"):
               return None
           raise
   ```

   The sentinel tuple is exactly `("", "telescope")`. `"n/a"` is not accepted unless the board adopts the transition item below.

   - It tries the strict path first. That way the `stage_email_meteorite` mailbox fold in `_resolve_task_prompts` (empty `agent_id` falls back to `parse_meteorite_email`) still resolves to a real server and stays gated. Only if the fold also finds no agent does the empty `agent_id` count as non-LLM.
   - It re-raises when `agent_id` names a real but missing agent, or a real agent with no `model_id` / `brain_setting`. That matches AST-1879 today (dispatch crashes loudly), not a silent bypass.

3. **`src/core/dispatcher.py` `_dispatch_one_body`, lines 1341–1354.** In the line-30 import, replace `task_llm_server_id` with `task_llm_server_id_or_none`. Line 1342 is its only use in this module. Apply the server check only when a server id comes back:

   ```python
   # AST-1879: the key for the task agent's server only — another platform's key does not count.
   # AST-1944: no LLM agent (telescope / empty / no agent_task row) → no server to gate; candidate check stays.
   server_id = task_llm_server_id_or_none(task_key)
   if not ctx or (server_id and not (ctx.get("candidate_api_keys") or {}).get(server_id)):
   ```

   The skip debug/warning block stays as-is. For a non-LLM task it fires only when `ctx` is missing, and its `server_id` slot then prints `None`, which is acceptable for a debug/warning line.

4. **No other files.** `_resolve_task_prompts`, `task_llm_server_id`, `api_admin` (AST-1880's area), `monitor.provider_balance_outage`, `data/admin/agent.json`, and `docs/uat-fixtures/AST-756/expected-agent_task.json` (a historical UAT snapshot) are untouched.

5. **Regression coverage is Betty's call (qa-fix).** Suggested cases follow AST-1944's acceptance criteria:
   - Repo `agent_task.json` has no `"n/a"` left, and the 12 rows carry `"telescope"`.
   - `fetch_jd` / `recheck_no_openings` with `agent_id: "telescope"` reach the handler.
   - A key with no `agent_task` row does not raise at the gate.
   - An LLM task whose candidate lacks its server key is skipped with the AST-1879 warning.
   - A missing candidate is skipped.
   - An `agent_id` naming an unknown agent still raises.

Alternatives considered and rejected:
- Change `task_llm_server_id` to return `Optional[str]`. This breaks `api_admin._candidate_dispatch_api_key_error` (`get_llm_server(None)`), which is out of scope.
- Bare `try/except ValueError` in the dispatcher, the same as `api_admin`. This silently lets misconfigured LLM tasks past the gate.
- Extract the row lookup out of `_resolve_task_prompts`. That is a bigger refactor of a strict function the AC says to leave alone.

**Deploy step (required, not code): apply the renamed rows to each environment's database.** The repo JSON does *not* reach the live database on deploy. `REPO_ADMIN_JSON_CONFIG` (`src/utils/config.py:4392–4394`) says *"Server start does not apply these files (AST-1455)"*. The only path is the admin "Revert to file" endpoint, `POST /api/admin/repo_json/revert/agent_task` → `revert_repo_admin_json_table("agent_task")`. The `src/data/database.py:6315` comment ("repo-wins at bootstrap") predates AST-1455 and is stale.
- Until that revert runs on an environment, its live rows still say `"n/a"`, and with the `("", "telescope")` tuple non-LLM dispatch there keeps crashing exactly as today.
- Whoever lands AST-1943 on an environment runs the revert right after deploy. Note it in the AST-1943 PR body (prep-uat / finish-up).
- The revert loads the whole `agent_task` table from the repo file, so any live-only Manage Tasks edits that aren't in the repo are overwritten. That's the same as every existing Revert to file.

**⚠ TRANSITION-WINDOW: flagged for the board, not adopted by default.** Alternative: make the step 2 tuple `("", "telescope", "n/a")` so non-LLM dispatch works on every environment from deploy, whether or not the revert has run. Remove `"n/a"` in a follow-up once every environment is reverted.
- Cost: a second, dead sentinel in code, plus a follow-up ticket to remove it.
- Default stays `("", "telescope")` per Chuckles' scope-gate reply. Fix-board decides whether to adopt this. If adopted, make-fix adds `"n/a"` to the tuple with a one-line comment naming the removal follow-up, and nothing else changes.

### Blast radius

- `_dispatch_one_body` is the single entry for every scheduled and AUTO dispatch tick. Today all non-LLM keys are down, and after the fix they run again.
- Other `task_llm_server_id` callers are unchanged: `api_admin._candidate_dispatch_api_key_error` (already tolerant via `except ValueError`) and `monitor.provider_balance_outage` (fires only for LLM balance refusals).
- `_resolve_task_prompts` callers (`do_task`, preview, empty-render) are unchanged.
- `tests/component/core/test_dispatcher.py` mocks `task_llm_server_id` and must retarget to `src.core.dispatcher.task_llm_server_id_or_none` (Betty, qa-fix). `test_agent_ast1879.py`, `test_monitor.py`, and `test_api_admin.py` reference the unchanged function.
- `tests/component/core/test_repo_admin_json.py` asserts `row["agent_id"] == "n/a"` at lines 506, 1378, and 1423, and must flip to `"telescope"` (Betty, qa-fix).
- Live databases on every environment: see the deploy step under Proposed change. Without a revert, the rename has no effect there.
- `api_admin._candidate_dispatch_api_key_error` and `_evaluate_dispatch_empty_render` keep working with `"telescope"`. `get_agent("telescope")` is also `None`, so they hit the same `ValueError` path as before. The `AST-1794: n/a agent` comment at `api_admin.py:2017` becomes slightly stale, but `api_admin` is out of scope, so it's left alone.
- No frontend or extension code matches on `"n/a"`. The Manage Tasks UI just shows `"telescope"` as the row's agent id.

### What must still hold

- AST-537: dispatch for `gaze` / `recheck_no_openings` must not need an `agent_task` row or agent seeding.
- AST-1879: an LLM task needs the candidate's key for *its agent's* server. Another platform's key does not count, and the skip warning text is unchanged.
- A missing candidate row is still skipped before any handler.
- `_resolve_task_prompts` raises on a missing row, an empty `agent_id`, or an unknown agent, for `do_task` / preview.
- The `stage_email_meteorite` → `parse_meteorite_email` fold still resolves to a real agent and stays gated.
- `api_admin` Run/Auto key gate behavior is unchanged (AST-1880). Non-LLM tasks still need no key there.
- `agent_task.json` changes only in `agent_id` on the 12 sentinel rows. Every other row and field is byte-identical, and there is no new `agent.json` row.
- `"telescope"` never resolves to a real agent, so `do_task` / preview on a non-LLM key still raises `Agent 'telescope' … not found` (strict, unchanged).
