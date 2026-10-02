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

### Joan fix-board — AST-1944

**Canon take on the transition-window item:** Neither default `("", "telescope")` nor adopted `("", "telescope", "n/a")` forces a statute or pattern edit. `astral.seed.agent-tables-in-repo-json` already treats repo JSON as authoritative in git while live `agent_task` may lag until operator Revert to file (AST-1492 kill-switch). Code that still accepts legacy `"n/a"` is a bounded DB/repo skew bridge, not a second seed source; repo rename to `"telescope"` remains the durable shape. Keeping only `telescope` in code is canon-clean but leaves non-LLM dispatch broken on any env that has deployed the fix without revert — an ops gap, not a canon violation. **Board canon view: OK to adopt the transition tuple** (no F3); follow-up removal is hygiene only.

```text
[board-joan]  CANON: OK

Registry skim (not R1–R7): `astral.seed.agent-tables-in-repo-json` — renaming `agent_id` on the 12 non-LLM rows in `data/admin/agent_task.json` (`n/a` → `telescope`, no new `agent.json` row) is an Archie-approved repo-seed edit on the explicit Revert-to-file path; aligns with kill-switch / no boot-apply law. `task_llm_server_id_or_none` + gated `_dispatch_one_body` check restores the AST-537 / pre–AST-1879 dispatch invariant without weakening AST-1879 per-server key law for real LLM routes; no in-force directive encodes `"n/a"` as the canonical non-LLM sentinel or forbids `telescope`.

`astral.standards.no-hardcoded-sets`: the `("", "telescope")` tuple interprets seed `agent_id` semantics (plus empty / missing row), not a parallel TASK_CONFIG membership set — no REVISE.

**TRANSITION-WINDOW (`("", "telescope", "n/a")`):** Canon-neutral either way. Adopting accepts live DB rows still on `"n/a"` until each env runs `POST …/revert/agent_task`; consistent with seed statute’s repo-vs-DB split and does not require a new carve-out in corpus. Default-only `telescope` is also canon-OK but widens the post-deploy crash window where revert lags — ops, not statute. **Joan: adopt the transition tuple in make-fix** (one-line removal follow-up comment); no F3 unless Archie later wants sentinel semantics written into a directive (optional, not fix-board REVISE).

context_tokens≈8500
```

**Chuckles routing:** the transition tuple is not adopted in make-fix. Susan's AST-1943 To-be says `"telescope"` *instead of* `"n/a"`, and accepting both is a product/deploy call she hasn't made. It is flagged to her on the AST-1943 PR. Default `("", "telescope")` stands, and the post-deploy `agent_task` revert is a required ops step.

### Radia review-fix — AST-1944

`[code-rubric]`  
**Ticket:** AST-1944  
**Publish ref:** `1c91606a25130ed65f020ae87bb9f9f72618e4b3` (`origin/sub/AST-1943/AST-1944-skip-key-gate-non-llm-tasks`)  
**Diff base:** `origin/ftr/AST-1943-non-llm-dispatch-key-gate...origin/sub/AST-1943/AST-1944-skip-key-gate-non-llm-tasks` (mini-parent stacked on ftr — not orphaned)  
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (tree `canon/` at publish tip; no `docs/canon-index.md` on this ref)  
**Overall:** CLEAN  

## Canon scores

*(Frozen **Canon Scope** on Linear AST-1944 description: **none** — same fix-lane process pattern as other dispatcher bugs. Scored **fix-board Joan overlap** from plan-fix § `## Bug: AST-1944` / `### Joan fix-board — AST-1944`; not a substitute for a frozen list.)*

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.seed.agent-tables-in-repo-json | A | | 12× `agent_id` `n/a`→`telescope` in `data/admin/agent_task.json` only; no `agent.json` row; matches Revert-to-file / kill-switch shape |
| astral.standards.no-hardcoded-sets | A | | `("", "telescope")` interprets seed sentinel semantics, not a parallel task membership set |

## Column diff vs plan stage

`no plan-stage scores attached` (no `validate-plan` plan-stage artifact on the issue doc for AST-1944; Joan fix-board only).

## Frame diff

(none)

## Fix-specific checks

- **`[bug-repro]`:** not applicable — clean board opt-out. Fix-board **TESTS: REVISE**; regression work split to gap sibling **AST-1945**; **qa-fix did not run** on this tip. Not scored as missing.
- **`## What must still hold`:** OK — traced each bullet against the diff:
  - Missing / empty / `telescope` `agent_task` → `task_llm_server_id_or_none` returns `None`; gated check `if not ctx or (server_id and not …)` preserves candidate skip and skips server-key gate (AST-537 / no-row keys).
  - LLM paths still call strict `task_llm_server_id` inside the helper first; misconfigured real agents still re-raise after row inspection.
  - `_resolve_task_prompts` / `task_llm_server_id` bodies untouched; `api_admin` untouched.
  - `stage_email_meteorite` fold: strict path attempted before `except` branch (matches plan).
  - Repo JSON: `rg` shows **0** `"n/a"`, **12** `"agent_id": "telescope"`; diff is `agent_id` only on those rows.

## Findings

### fix-now

(none)

### discuss

- **Location:** Deploy / ops (plan § Proposed change deploy step; Susan routing on transition window)  
  **Finding:** Code accepts only `("", "telescope")`, not live DB `"n/a"`. Environments that deploy this fix without `POST /api/admin/repo_json/revert/agent_task` keep crashing on non-LLM dispatch until revert — deliberate product choice (transition tuple **not** adopted).  
  **Recommendation:** No code change on AST-1944; ensure AST-1943 land checklist / PR calls out revert.  
  **Default:** Ship as-is; ops documents revert with parent deploy.

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen canon list at Plan Approved; Radia scored Joan board overlap only.  
  **Recommendation:** Archie may add a frozen list on future fix bugs for Joan/Radia column parity; not blocking this tip.

### advisory

- **Deploy-step risk:** Post-deploy window where live `agent_task` still has `"n/a"` while code no longer treats `"n/a"` as non-LLM at the gate — same as discuss item; monitor on first env roll.
- **Sibling test gap (AST-1945):** Katherine’s test-fix comment documents `test_dispatcher.py` fixture retarget and `test_repo_admin_json.py` sentinel assertions (plus new `TestAst1269AliasAgentTaskSeedRestore` lockstep vs `docs/uat-fixtures/AST-756/expected-agent_task.json`); none of that is in this product diff — expected split, not AST-1944 scope creep.
- **Plan fidelity:** Diff matches plan-fix steps 1–4 (helper, dispatcher gate, JSON rename, no other files). Estimate **1** fits footprint.
- **What's solid:** Small, focused fix; `task_llm_server_id` callers outside dispatch unchanged; AST-1879 conditional preserves per-server key law when `server_id` is non-`None`.

## Chuckles — post-review branching

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | **Normal** (AST-1943 + `origin/ftr/AST-1943-non-llm-dispatch-key-gate`) | **Review Posted** → clean-review shortcut → **User Testing** (`resolve-child` skipped). Not orphaned — no straight-to-`dev` finish-up for this ticket alone. |

context_tokens≈12000

---

`[code-rubric] PROCEED (Commit: 1c91606a2) Non-LLM gate clean`

### Resolution — AST-1944

docs-acceptance: product-only fix. The dispatcher fixture retarget, `[bug-repro]`, `"telescope"` sentinel assertions, AST-756 UAT fixture, and bible updates (Betty `[board-betty] TESTS: REVISE`) land on gap sibling AST-1945, stacked after this ticket on `ftr/AST-1943-non-llm-dispatch-key-gate`.

## Bug: AST-1945 — Non-LLM dispatch gate tests + telescope sentinel (test gap for AST-1944)

Test-only sibling of AST-1944, filed from Betty's `[board-betty] TESTS: REVISE`. AST-1944's product change (`task_llm_server_id_or_none`, the gated `_dispatch_one_body` check, and the 12 `"n/a"` → `"telescope"` rows) is already on `origin/ftr/AST-1943-non-llm-dispatch-key-gate`. Betty lands everything below (qa-fix). **No `src/**` or `data/**` changes.**

### As-is

- The autouse `_task_server_anthropic` fixture (`tests/component/core/test_dispatcher.py:29–33`) pins `dispatcher_mod.task_llm_server_id` → `"anthropic"` for every dispatcher test. So no test ever ran the real resolver on a non-LLM key, which is how the AST-1879 regression shipped.
- After AST-1944 that attribute no longer exists, so the fixture's `monkeypatch.setattr` raises `AttributeError` at setup. Every test in `test_dispatcher.py` errors: 164 on the AST-1944 tip.
- `test_repo_admin_json.py` still asserts `agent_id == "n/a"` at L506, L1378, and L1423.
- `test_alias_identity_lockstep_with_fixture` (L1442) newly fails with `('meteorite_grade_do', 'agent_id'): 'telescope' == 'n/a'`. It compares the catalog with `docs/uat-fixtures/AST-756/expected-agent_task.json`, which still has 12 `"n/a"` rows.
- `task_llm_server_id_or_none` has no unit tests.
- The bible's dispatcher AST-1879 entry (`docs/test-bible/core/dispatcher.md:659–668`) doesn't describe the non-LLM carve-out.

### To-be

- The dispatcher tests run again, with the autouse fixture retargeted to `task_llm_server_id_or_none`.
- A `[bug-repro]` runs `_dispatch_one_body` with the **real** resolver on non-LLM keys. It is red on `origin/dev` and green on this tip.
- Agent unit tests cover all three branches of the new helper.
- Sentinel assertions read `"telescope"`, and the AST-756 fixture is in lockstep.
- Bible entries match. There are no `"n/a"` transition tests; the tuple is exactly `("", "telescope")`.

### Repro

The AST-1944 test-fix run is recorded in the comment on AST-1944. It ran on Python 3.14 from `/home/susan/astral/.venv`.
- `test_dispatcher.py` on the AST-1944 tip: `164 errors`, all `AttributeError: <module 'src.core.dispatcher'> has no attribute 'task_llm_server_id'`.
- Re-run with a throwaway `/tmp` plugin that points the new name at the patched one: 12 failed / 152 passed, the same 12 failures as on ftr before AST-1944. Those pre-existing failures are not this ticket's to fix.
- `pytest …test_repo_admin_json.py::TestAst1269AliasAgentTaskSeedRestore::test_alias_identity_lockstep_with_fixture` gives `assert 'telescope' == 'n/a'`.

### Root cause

The test file stubbed the exact function whose behavior regressed: it patched the resolver everywhere rather than seeding data. The real non-LLM path was therefore never exercised, and the stub broke as soon as the import was renamed. The sentinel literals and the UAT lockstep fixture pin `"n/a"` by value.

### Proposed change

All paths below are Betty's (qa-fix).

1. **`tests/component/core/test_dispatcher.py`: retarget the autouse fixture and add an opt-out.**
   - Add a no-op fixture `real_server_gate` beside `_task_server_anthropic`. It is a plain `@pytest.fixture` returning `None`, with no marker, because `pytest.ini` runs with `--strict-markers` and a new marker would need registering in `pytest.ini`, outside scope.
   - Change `_task_server_anthropic(monkeypatch, request)`:
     ```python
     if "real_server_gate" in request.fixturenames:
         return
     monkeypatch.setattr(dispatcher_mod, "task_llm_server_id_or_none", lambda task_key: "anthropic")
     ```
     Update its docstring to name `task_llm_server_id_or_none`.
   - The opt-out returns **before** the `setattr`. That way the repro also runs on `origin/dev`, where the new attribute doesn't exist, and fails with the real product `ValueError` rather than a setup error.
   - `TestDispatchOne::test_gate_reads_key_for_task_agents_server` (L1068–1090): change `monkeypatch.setattr(dispatcher_mod, "task_llm_server_id", _server)` to `"task_llm_server_id_or_none"`, and change the comment on L1071 to name `task_llm_server_id_or_none`. The assertions are unchanged.
   - Update the `test_skips_without_*` / `test_completes_click_dispatch` docstrings or comments only if they name the old function; no logic change.

2. **`tests/component/core/test_dispatcher.py`: new class `TestAst1944NonLlmGate`, opted out of the stub through `real_server_gate`.** Patch the **data layer**, not the resolver: `monkeypatch.setattr(agent_mod, "get_agent_task", lambda k: rows.get(k))` and `monkeypatch.setattr(agent_mod, "get_agent", lambda i: agents.get(i))`, with `from src.core import agent as agent_mod`. That covers `_resolve_task_prompts`, `task_llm_server_id_or_none`, and `_current_agent_task_run_next`, which the dispatcher imports from `agent`. For the dispatch scaffolding, reuse `test_completes_click_dispatch`'s stubs: `save_dispatch_ledger`, `update_dispatch_ledger`, `compute_batch_cost`, `flush_log_buffer`, `_db_update_dispatch_task`, `_check_circuit_breaker`, `_run_dispatch_loop` as `AsyncMock`, plus the registry entry.
   - **`[bug-repro]` `test_non_llm_key_reaches_handler_without_any_api_key`**, parametrized over the agent_task row for `task_key="fetch_jd"`:
     - `{"task_key": "fetch_jd", "agent_id": "telescope", "current": 1}` (`agents` has no `telescope`)
     - `{"task_key": "fetch_jd", "agent_id": "", "current": 1}`
     - no row (`rows = {}`, the AST-537 invariant)

     Candidate: `{"astral_candidate_id": "cand-1", "candidate_api_keys": {}}`, with no key for any server. Assert `_run_dispatch_loop.assert_awaited_once()` and no `"skipped — no candidate"` warning in `caplog`.
     - **Red on `origin/dev`:** the strict resolver raises out of `_dispatch_one`. The cases raise `Agent 'telescope' referenced by task 'fetch_jd' not found.`, `agent_task 'fetch_jd' has no agent_id assigned…`, and `No agent_task row for 'fetch_jd'…` respectively.
     - **Green on this tip.**
     - Betty proves red by running this node against `origin/dev`'s `src/` with this branch's test file.
   - **`test_non_llm_key_missing_candidate_still_skipped`:** the telescope row, `get_candidate → None`. Assert `_run_dispatch_loop` and `save_dispatch_ledger` not called, and the warning `"cand-1 | dispatch fetch_jd skipped — no candidate or None API key"` (the AST-1944 plan accepts `None` in the server slot). Green on tip.
   - **`test_llm_key_without_server_key_still_skipped`:** the real resolver with a real-looking agent. `rows["evaluate_jd"] = {"task_key": "evaluate_jd", "agent_id": "a1", "current": 1}`, `agents["a1"] = {"agent_id": "a1", "model_id": "deepseek-v4", "brain_setting": "Big"}`. Candidate keys `{"anthropic": "sk-ant"}`. Assert the skip warning names `deepseek`, and no ledger or loop. `resolve_model_brain("deepseek-v4", "Big")["server_id"] == "deepseek"`, which I checked on this tip. Green on both trees.
   - **`test_unknown_real_agent_still_raises`:** `rows["evaluate_jd"]` with `agent_id: "ghost"` and no such agent. `pytest.raises(ValueError, match="Agent 'ghost'")` around `_dispatch_one`. This is loud as before; green on both trees.

3. **`tests/component/core/test_agent_ast1879.py`: new class `TestAst1944TaskLlmServerIdOrNone`.** Betty can pick a new `test_agent_ast1944.py` instead; same content. It patches `agent_mod.get_agent_task` / `agent_mod.get_agent` the same way, which covers all three branches for LOCKED_AT_100 on `agent.py`:
   - `"telescope"` row → `None`. Empty `agent_id` → `None`. No row → `None`.
   - LLM row with a valid agent → the catalog server (strict path, no exception).
   - `agent_id: "ghost"` (missing agent) → re-raises `ValueError("Agent 'ghost' …")`.
   - A valid agent with `model_id: ""` → re-raises `"has no model_id configured"`, so misconfiguration stays loud.
   - Mailbox fold: the `stage_email_meteorite` row has `agent_id: ""`, and the `parse_meteorite_email` row carries a valid agent → returns that agent's server, not `None`.
   - Mailbox fold with no legacy agent: the `stage_email_meteorite` row is empty and there is no `parse_meteorite_email` row → `None`.

4. **`tests/component/core/test_repo_admin_json.py`: sentinel literals.** At L506, L1378, and L1423, change `assert row["agent_id"] == "n/a"` to `"telescope"`.
   - L506 is inside `@pytest.mark.skip(reason=_AST1269_SEED_WIPE_SKIP)` and stays skipped.
   - L1378 / L1423 already fail earlier on ftr at `task_seq` (`assert 3 == 5`, L1377 / L1422, AST-1239 wipe drift). That pre-existing failure is **out of scope**, and those two stay red for that reason only.

5. **`docs/uat-fixtures/AST-756/expected-agent_task.json`: update the fixture (recommended) rather than relax the test.** Do the same literal replace AST-1944 used: exactly 12 `"agent_id": "n/a"` → `"agent_id": "telescope"`, nothing else, byte-identical otherwise.
   - Afterwards `rg -c '"n/a"'` on the fixture prints nothing.
   - Why this option: L1378's loop asserts **one** literal across both the catalog and this fixture (`for src in (cat, fix)`). Relaxing the lockstep test alone would still leave L1378 split between `"telescope"` and `"n/a"`.
   - With the fixture updated, `test_alias_identity_lockstep_with_fixture` (L1442) goes green with no test edit.

6. **`docs/test-bible/core/dispatcher.md`: AST-1879 entry (L659–668), plus an AST-537 cross-reference.**
   - Revise the gate description: `candidate_api_keys[task_llm_server_id_or_none(task_key)]` applies only when a server id comes back. A non-LLM key (`"telescope"` / empty `agent_id` / no row) skips the key check, and a missing candidate is still skipped.
   - Revise the `_task_server_anthropic` row to name `task_llm_server_id_or_none` and the `real_server_gate` opt-out.
   - Add an AST-1944 row for `TestAst1944NonLlmGate`, marking the `[bug-repro]` node.

7. **`docs/test-bible/core/agent.md`: AST-1879 section (around L1536–1543).** Add an AST-1944 row for `TestAst1944TaskLlmServerIdOrNone`, or the new file, covering the branches listed in step 3.

### Blast radius

- `test_dispatcher.py`: every test depends on the autouse fixture. After step 1, the file should return to AST-1944's shim result, 12 failed / 152 passed, plus the new class all green. The 12 failures predate AST-1944 and are unchanged here.
- `test_repo_admin_json.py`: only the three sentinel lines and the lockstep test change outcome.
- `docs/uat-fixtures/AST-756/expected-agent_task.json`: also read by `TestAst1222…::test_alias_rows_grouping_only_and_fixture_lockstep`. Step 4 keeps that test's single literal consistent.
- `test_agent_ast1879.py`: additive only, and the existing `TestAst1879RouteHelpers` is unchanged.
- No product file changes. `api_admin`, `monitor`, and the `_resolve_task_prompts` tests are untouched.

### What must still hold

- AST-1879 dispatcher tests: an LLM task without its server's key is skipped with the server named in the warning, and another platform's key does not count.
- AST-537: dispatch for a key with no `agent_task` row does not raise at the gate. The repro's no-row case is that invariant's first real-resolver test.
- `_resolve_task_prompts` strictness: the existing `do_task` / preview tests keep their raises, and the new agent tests assert that `task_llm_server_id_or_none` re-raises for unknown or misconfigured real agents.
- No test asserts `"n/a"` as an accepted sentinel, because there is no transition window.
- The test-tree and bible edits are Betty's. The engineer touches none of steps 1–7.
