<!-- linear-archive: AST-1880 archived 2026-10-08 -->

## Linear archive (AST-1880)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1880/admin-model-brain-pickers-per-platform-keys-invalid-on-missing-key  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851

### Description

## What this implements

After #3. Manage Agents picks model then a model-scoped brain size; Manage Candidates shows one key field per server; Scheduled Actions flags Invalid (AUTO off, Run blocked, tooltip reason) when the candidate lacks the needed platform key; ad-hoc resolve and execution history go through the catalog. Last child, so it also retires the legacy provider path once nothing imports it. Does **not** own the catalog (#1) or storage (#2).

## Citations

`stat.logging.info.api`, `stat.logging.warning`.

## Scope

`src/ui/api/api_admin.py` — model catalog route; agent routes carry model and reject invalid sizes; ad-hoc resolve and execution-history display via catalog; Invalid evaluation + Run/Auto gate for a missing platform key. `src/ui/api/api_candidate.py` — per-server key PATCH and outbound set/not-set. `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` — model + brain-size selects. `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — one key field per server. `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — missing-key reason in the Invalid tooltip. `session_resume/parse` route requires `candidate_id` (in `api_admin.py` above). `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — posts the selected candidate; Parse disabled with none selected. **Legacy retirement:** `src/utils/config.py` — delete `active_provider` / `get_active_llm_provider`, the DeepSeek-only resolvers/pricing, and `CONTACT_ESTELLE_CONFIG["default_brain_setting"]` (no other [config.py](<http://config.py>) edits). `src/external/deepseek.py` — deleted. `tests/component/external/test_deepseek.py` — deleted. `docs/test-bible/external/deepseek.md` — deleted. `src/utils/cost_calculator.py` — delete the DeepSeek-named wrappers (`deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, `calculate_cost_components_deepseek`) (AST-1883). `src/core/monitor.py` — `provider_balance_outage` labels the alert by the task agent's server instead of the global provider (legacy retirement; required by AC 1).

## Acceptance criteria

1. **Global switch gone.** `rg -n "active_provider|get_active_llm_provider" src/` returns nothing. Any hit = fail.
2. **No server or model names outside config.** `rg -n -i "kimi|moonshot|openrouter|deepseek" src/ --glob '!src/utils/config.py'` returns nothing (frontend included). Any hit = fail.
3. **Brain sizes are per model.** `GET /api/admin/agents/models` lists Kimi K2.6 (direct) and Kimi K2.6 via OpenRouter with exactly `Little, Big`, and Claude / DeepSeek V4 with `Little, Medium, Big`. Saving an agent on a Kimi model with brain size Medium returns 400 and leaves the row unchanged. A 200, or a list mismatch = fail.
4. **One key per platform per candidate.** Setting a Kimi key and an OpenRouter key on one candidate via Manage Candidates leaves two rows for that candidate in the candidate key table, both Fernet ciphertext (neither equals the plaintext), and `GET` the candidate shows both servers set. One row, plaintext, or one key overwriting the other = fail.
5. **Invalid on Scheduled Actions.** For a scheduled action whose candidate lacks the key for its task agent's server, `GET` the dispatch-task list returns `empty_render: true` with a reason naming that server, AUTO is forced off, `POST /api/admin/dispatch_tasks/<id>/run` returns 400, and the Invalid tooltip shows the reason. Adding the key flips the row back to valid on the next list. Any of these not holding = fail.
6. **Catalog-driven admin UI.** Manage Agents' brain-size select shows only the selected model's sizes and saving persists model + size (re-GET shows both). Manage Candidates shows exactly one key field per server catalog entry. Field count ≠ server count, or hardcoded options (AC 2 grep) = fail.
7. **DeepSeek client removed.** `test -e src/external/deepseek.py` fails and `rg -n "send_to_deepseek" src/ tests/` returns nothing. Either present = fail.
8. **Session paste uses the selected candidate.** `POST /api/admin/session_resume/parse` without `candidate_id` returns 400 and sends no request; with a candidate holding the key for Ruth's model's server it goes out with that key (component test), and the candidate row is byte-identical before/after. A 200 without a candidate, another key on the wire, or a changed candidate row = fail.

## Boundaries

Stays inside the Scope above. Sibling slices: #1 catalog (except the named legacy deletions), #2 storage, #3 runtime routing.

## Notes for planning

New pattern *Model → server catalog routing* is defined on parent AST-1851 (Architectural definition). Each child must stay green on its own `sub/*`. Delete the legacy provider path only after confirming nothing on ftr imports it.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### betty — 2026-09-29T23:03:28.357Z
7901a931c sub rebuilt: one merge-tests(AST-1880); tree identical; validate-sub-log ok (AST-1890)

#### ada — 2026-09-29T22:19:15.888Z
[qa-handoff]
@Betty White, resolve-child is blocked on the sub's commit sequence, not on product code.

- **Command:** `~/.cursor/scripts/git/validate-sub-log.sh sub/AST-1851/AST-1880-admin-model-pickers-platform-keys AST-1880 ftr/AST-1851-support-openrouter-api-models`
- **Result:** `BLOCKED: duplicate merge-tests(AST-1880) on sub — count=2 (amend on tests, one merge-tests only)`
- **The two deliveries:** `e74930781` (merge of `a0a12194f`) and `eb81cfe3a` (merge of `0ede9b9a7`, the AC 7 fix after Radia's review). `merge-child` runs the same gate, so User Testing would be recalled.
- **Ask:** collapse these into one `merge-tests(AST-1880)` per your tests-delivery procedure. Keep the product and doc commits on top: `387f84ac5` test(), `be239f09a` resolve() (keys-only PUT info line), `5bf9495b0` resolve() (resolution notes). Then reassign me.
- **Already green:** §9a dry-runs into `origin/dev` and the ftr are both clean. Radia's discuss items are resolved (see `## Resolution` in the issue doc). The ticket stays Review Posted.

#### betty — 2026-09-29T22:17:29.860Z
`origin/sub/AST-1851/AST-1880-admin-model-pickers-platform-keys` @ `eb81cfe3a` · AC 7 grep clean

#### radia — 2026-09-29T22:16:24.332Z
`[code-rubric] REVIEW (Commit: 387f84ac5) admin keys; api log gap`

#### ada — 2026-09-29T22:14:43.116Z
387f84ac5 manifest green: pytest 145 passed, Vitest 115 passed (2 skipped). The API Key column fix is in.

#### betty — 2026-09-29T22:12:45.901Z
`origin/sub/AST-1851/AST-1880-admin-model-pickers-platform-keys` @ `e74930781` · manifest in api_admin.md

Product bug, one expected red: the `AdminManageCandidates` API Key column still checks `val === "Set"`, so it shows "⚠️ Not set" even though the API now sends per-server flags. Test: "AST-1880: API Key column lists the labels of servers with a key set". Manifest: `docs/test-bible/ui/api/api_admin.md` § QA test manifest (AST-1880).

#### joan — 2026-09-29T21:45:46.498Z
[plan-rubric] PROCEED (Commit: 16dbe56de) Admin + legacy retirement plan clean

#### ada — 2026-09-29T21:44:15.141Z
16dbe56de plan ready

#### ada — 2026-09-29T21:42:51.822Z
[scope-gate] `src/core/monitor.py` is not in Scope, but the plan needs it.

- **Why:** `provider_balance_outage` (line 83) calls `get_active_llm_provider()` to label the balance-outage email. Scope says "**Legacy retirement:** `src/utils/config.py` — delete `active_provider` / `get_active_llm_provider` …", and AC 1 says "`rg -n "active_provider|get_active_llm_provider" src/` returns nothing." Neither can hold while `monitor.py` imports the function, and no Scope line names `monitor.py`.
- **Needed change (function-level, about 2 lines):** in `provider_balance_outage`, replace the global provider with the refused task agent's server: `get_llm_server(task_llm_server_id(task_key))["label"]`. This stays inside the existing never-raises `try`, and there is no import cycle (`agent.py` does not import `monitor`). The alternative is to drop the provider name from the subject.
- **Ask:** add `src/core/monitor.py — provider_balance_outage labels the alert by the task agent's server (legacy retirement)` to Scope. The plan is otherwise complete at 55c2c84a8 (Stage 3 step 6, marked pending).

---

# AST-1880 — Admin: model + brain pickers, per-platform keys, Invalid on missing key

- **Parent:** [AST-1851 — Support OpenRouter API models for agent work](https://linear.app/astralcareermatch/issue/AST-1851)
- **Ticket:** [AST-1880](https://linear.app/astralcareermatch/issue/AST-1880)
- **Publish ref:** `origin/sub/AST-1851/AST-1880-admin-model-pickers-platform-keys`
- **Canon Scope:** new pattern *Model → server catalog routing* (AST-1851 § Architectural definition); `stat.logging.info.api`, `stat.logging.warning`.

This ticket is the admin layer of *Model → server catalog routing*, and the last child, so it also retires the legacy provider path. Manage Agents picks a catalog model and then one of that model's brain sizes. The agent routes carry `model_id` and return 400 on a size the model doesn't have. Manage Candidates shows one key field per catalog server and stores each through the per-server data API from AST-1878. Scheduled Actions marks a row Invalid (AUTO forced off, Run blocked, tooltip naming the server) when the candidate has no key for the task agent's server. Ad-hoc resolve and the execution-history screen resolve through `resolve_model_brain`. Session paste passes the selected candidate. After that, nothing imports the global `active_provider`, the DeepSeek-only resolvers and pricing, `send_to_deepseek`, or the DeepSeek-named cost wrappers, so they are deleted.

It also closes the items Radia deferred to #4:

- **`api_candidate` key-clear call arity (AST-1878 review):** `clear_candidate_api_key(candidate_id)` is still called with one argument, and `save_candidate_admin(..., candidate_api_key=...)` writes a column that is now dark. Both are replaced by per-server set/clear (Stage 2).
- **`api_admin` ad-hoc Test 500 (AST-1879 review):** `adhoc_test` still passes `tier_meta=` / `api_key_override=` to `run_adhoc_workbench_test`. That raises `TypeError`, which the route turns into a 500. Rewired in Stage 1.
- **Scheduled Actions Run/Auto gate (AST-1879 review):** `_candidate_dispatch_api_key_error` still reads the legacy `candidate_api_key`, so every Run/Auto is blocked on ftr. It becomes server-aware in Stage 1.
- **AC 9 legacy-provider grep (AST-1879 review):** `rg default_brain_setting src/` still hits `CONTACT_ESTELLE_CONFIG` in `config.py`. It clears when Stage 3 deletes the key and its assert. The epic-wide AC 1 / AC 2 / AC 7 greps clear in Stage 3 too.
- **AST-1883 (folded):** delete `deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, `calculate_cost_components_deepseek` from `cost_calculator.py` (Stage 3).

Found during research (in Scope, fixed in Stage 2): **plaintext candidate keys leak on ftr.** `_sanitize_candidate` pops only the legacy `candidate_api_key`, but `get_candidate` now hydrates `candidate_api_keys` (`{server_id: plaintext}`, AST-1878). `GET /api/candidates/<id>` and the `PUT …/data` response therefore return every plaintext key. Stage 2 pops the map and replaces it with set/not-set flags.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`:

- `src/ui/api/api_admin.py`: model catalog route, agent routes with model + size check, ad-hoc resolve, execution-history display, Invalid evaluation + Run/Auto gate, `session_resume/parse` requires `candidate_id` (Stage 1).
- `src/ui/api/api_candidate.py`: per-server key write + outbound set/not-set (Stage 2).
- `AdminAgentPrompts.tsx`, `AdminManageCandidates.tsx`, `AdminScheduledActions.tsx`, `AdminSessionResumePaste.tsx`: the UI rows Scope names (Stage 4).
- `src/utils/config.py`: only the named legacy deletions (Stage 3).
- `src/external/deepseek.py`: deleted (Stage 3).
- `src/utils/cost_calculator.py`: DeepSeek-named wrappers deleted (Stage 3).
- `tests/component/external/test_deepseek.py`, `docs/test-bible/external/deepseek.md`: deleted, but by **Betty** in qa-child. Engineers may not touch `tests/` or `docs/test-bible/**` (the pre-commit hook enforces this).

- `src/core/monitor.py`: `provider_balance_outage` labels the alert by the task agent's server instead of the global provider (Stage 3 step 6). This Scope line was added after the `[scope-gate]` on Linear. The gap was that AC 1 can't hold while `monitor.py` imports `get_active_llm_provider`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Imports: drop `DEEPSEEK_MODEL_PRICING`, `admin_brain_setting_catalog`, `brain_setting_for_anthropic_agent_key`, `get_active_llm_provider`, `infer_brain_setting_from_legacy_model_code`, `resolve_brain_setting_to_anthropic_agent_key`, `resolve_brain_setting_to_deepseek_tier_meta`, `validate_allowed_brain_setting` (plus `AGENT_CONFIG` / `get_model` if they end up unused). Add `LLM_MODEL_CONFIG`, `LLM_SERVER_CONFIG`, `get_llm_server`, `resolve_model_brain`, and `task_llm_server_id` from `src.core.agent`. `GET /agents/models` → model catalog; `/agents/brain_settings` and `_agent_admin_view` removed. `create_agent` / `update_agent` take `model_id`. `_enrich_tasks`, `_resolve_adhoc`, `adhoc_test` via the catalog. `_candidate_dispatch_api_key_error(cid, task_key)` is server-aware and feeds the list's `empty_render` / `invalid_reason`. `session_resume_parse` passes `candidate_id`. `_api_completed` helper + one info line per route this ticket changes. | ui |
| `src/ui/api/api_candidate.py` | Import `set_candidate_api_key`, `LLM_SERVER_CONFIG`. `_sanitize_candidate` → `api_keys: {server_id: {label, set}}`, pops `candidate_api_keys` / `candidate_api_key`. `PUT /<id>/data` body `api_keys: {server_id: key \| ""}` → per-server set/clear. | ui |
| `src/utils/config.py` | Delete `LLM_PROVIDER_CONFIG["active_provider"]`, `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]`, `DEEPSEEK_MODEL_PRICING` + the AST-1851 parity asserts, `DEEPSEEK_CONCURRENCY`, `get_active_llm_provider`, `resolve_brain_setting_to_deepseek_tier_meta`, `deepseek_brain_max_tokens_floor`, `CONTACT_ESTELLE_CONFIG["default_brain_setting"]` + its assert; matching header-inventory lines. Nothing else. | utils |
| `src/utils/cost_calculator.py` | Delete the three DeepSeek-named wrappers (+ header-inventory lines). | utils |
| `src/external/deepseek.py` | Deleted (`git rm`). | external |
| `src/core/monitor.py` | Import `get_llm_server` (config) + `task_llm_server_id` (`src.core.agent`), drop `get_active_llm_provider`. `provider_balance_outage` labels the email with the task agent's server (`get_llm_server(task_llm_server_id(task_key))["label"]`) instead of the global provider. | core |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | Model select + model-scoped brain-size select; Model column; saves `model_id` + `brain_setting`. | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | One key field (+ Show / Clear) per `api_keys` entry; table column lists the servers set. | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Invalid tooltip prefers `invalid_reason`. | ui |
| `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` | Posts `candidate_id: selectedId`; Parse disabled with none selected; copy line updated. | ui |

No other file is touched. No `tests/`, bible, `data/admin/`, `database.py`, or `core/agent.py` edits.

## Stage 1: `api_admin` — catalog route, agent routes, ad-hoc, execution history, Invalid gate, session paste

1. **Model catalog route.** Rewrite `GET /agents/models` (today it lists `AGENT_CONFIG`; no frontend caller uses that shape). Keyed by id per the house array rule:
   ```python
   @admin_bp.route("/agents/models")
   @require_admin
   def list_models():
       """Model → brain-size catalog for Manage Agents (AST-1880); sizes are the model's own, in catalog order."""
       return jsonify({
           mid: {
               "label": m["label"],
               "server_id": m["server"],
               "server_label": get_llm_server(m["server"])["label"],
               "brain_sizes": {
                   bs: {"default_temperature": t["default_temperature"], "default_max_tokens": t["default_max_tokens"]}
                   for bs, t in m["brain_sizes"].items()
               },
           }
           for mid, m in LLM_MODEL_CONFIG.items()
       })
   ```
   AC 3: Kimi K2.6 and Kimi K2.6 via OpenRouter list `Little, Big`; Claude and DeepSeek V4 list `Little, Medium, Big`.
   Delete `GET /agents/brain_settings` (its only caller, Manage Agents, moves to `/agents/models` in Stage 4).

2. **Agent reads.** Delete `_agent_admin_view`. `database._expose_agent_public` (AST-1878) already coerces `brain_setting` and exposes `model_id` + `model_code` (SKU). `list_agents` / `get_agent` / `update_agent` return rows as-is.

3. **`create_agent`.** Require `agent_id`, `model_id`, `brain_setting` (400 when any is missing). Drop the legacy `model_code` input branch. Call `database.save_agent(..., model_id=..., brain_setting=...)` inside `try/except ValueError → 400`. The data layer validates the size against the model before writing, so nothing is written on a 400.
   ⚠️ **Decision (legacy `model_code` input removed):** the Manage Agents UI stops sending it in Stage 4, and a model_code alias can't say which server to use. Accepting it would need an Anthropic-only mapping, which is the global-provider shape this epic removes.

4. **`update_agent`.** Updatable keys become `content`, `model_id`, `brain_setting`, `temperature`, `max_tokens`. Drop the `model_code` branch and the route-level `validate_allowed_brain_setting`. Call `database.update_agent(agent_id, **kwargs)` inside `try/except ValueError → 400`. `update_agent` checks the effective (model, size) pair against the stored row before its UPDATE, including a model-only change against the stored size. AC 3's "Kimi + Medium → 400, row unchanged" therefore holds with no second check in the route.

5. **`_enrich_tasks` (execution-history / task-manager display).** Replace the `get_active_llm_provider()` branch:
   ```python
   if agent:
       brain_setting_eff = (agent.get("brain_setting") or "").strip()
       try:
           route = resolve_model_brain((agent.get("model_id") or "").strip(), brain_setting_eff)
           resolved_model_key = route["sku"]
           model_cfg = route["pricing"]
       except ValueError as e:
           # Display row only — one misconfigured agent must not 500 the whole screen.
           logger.warning("%s | task manager %s agent %s has no routable model: %s", candidate_id or "-", task_key, agent_id, e)
   ```
   `cache_min_tokens` then comes from the catalog pricing row (Kimi/DeepSeek `0`, Claude from `AGENT_CONFIG`).
   ⚠️ **Decision (warn + blank, not 500):** before this change, legacy inference never raised here. `stat.logging.warning` gives who (candidate, task, agent) and why.

6. **`_resolve_adhoc`.** Replace the provider branch:
   ```python
   try:
       route = resolve_model_brain((agent.get("model_id") or "").strip(), (agent.get("brain_setting") or "").strip())
   except ValueError as e:
       return None, (jsonify({"error": str(e)}), 400)
   tier = route["tier"]
   temperature = agent["temperature"] if agent.get("temperature") is not None else tier["default_temperature"]
   max_tokens = agent["max_tokens"] if agent.get("max_tokens") is not None else tier["default_max_tokens"]
   ```
   The returned dict carries `model_code: route["sku"]`, `server_id: route["server_id"]`, `tier`, and `candidate_api_keys: (candidate or {}).get("candidate_api_keys")` in place of `tier_meta` / `api_key_override`. Key selection and the "no key for server → no request" failure stay in core (`run_adhoc`, AST-1879).
   ⚠️ **Decision (drop the `requires_candidate_key` condition):** AST-1877 asserts every `TASK_CONFIG` entry has `requires_candidate_key: True`, so the condition is always true for real tasks. Pure `adhoc` has no config row, and without a map it would always fail the missing-key check. Passing the candidate's map unconditionally lets ad-hoc tests run on the candidate's key for the agent's server.

7. **`adhoc_test`.** Pass `model_code=`, `server_id=`, `tier=`, `candidate_api_keys=` from `resolved`, which removes the `TypeError` 500. A candidate with no key for the server gets core's failure envelope ("Candidate … has no API key for server …"), which the route's existing `if not result.get("success")` path returns.

8. **Server-aware key gate.** Replace `_candidate_dispatch_api_key_error(candidate_id)` with:
   ```python
   def _candidate_dispatch_api_key_error(candidate_id: Optional[str], task_key: str) -> Optional[str]:
       """User-facing reason when Run/Auto can't start: the candidate lacks the key for the task agent's server."""
       if not candidate_id:
           return "This dispatch task has no candidate; set one before Run or Auto."
       cand = get_candidate(candidate_id)
       if not cand:
           return f"Candidate not found: {candidate_id}"
       try:
           server_id = task_llm_server_id(task_key)
       except ValueError:
           # No agent/model behind this task (table runners, notify) — no platform key to require.
           return None
       if (cand.get("candidate_api_keys") or {}).get(server_id):
           return None
       return f"Set this candidate's {get_llm_server(server_id)['label']} API key before using Run or Auto on this task."
   ```
   Update all three call sites to pass the task key: create (`task_key`), update (`effective_task_key`), and `run_dtask` (`row.get("task_key") or ""`). `run_dtask` then returns 400 when the key is missing (AC 5).
   ⚠️ **Decision (no-agent task → no key required):** the dispatcher runs table-runner / notify / mailbox tasks before its own key gate, and they make no LLM call through `task_llm_server_id`. This matches the empty-render soft pass for missing prompts (AST-1791). Before this change, the legacy gate demanded an Anthropic key for every task.

9. **Invalid on the list.** In `list_dtasks`, after `_evaluate_dispatch_empty_render`:
   ```python
   key_err = _candidate_dispatch_api_key_error(row.get("candidate_id"), row.get("task_key") or "")
   row["empty_render"] = bool(er.get("empty_render")) or bool(key_err)
   # AST-1880: missing platform key reason for the Invalid tooltip ("" when the key is present).
   row["invalid_reason"] = key_err or ""
   ```
   The existing AUTO-forced-off block then covers a missing key too. Its warning `why` becomes `key_err` when set (who: candidate + row id + task; why: missing server key). Adding the key flips the row back on the next list (AC 5).
   ⚠️ **Decision (per-row cost):** each row now also reads the candidate and resolves the task agent (`get_agent_task` + `get_agent`). No caching was added (house rule: no performance shortcuts without Susan's OK).

10. **Session paste.** `session_resume_parse` passes `candidate_id=(body.get("candidate_id") or "").strip()` to `run_session_resume_parse`. That already returns 400 with no request when the id is missing, and never writes the candidate row (AST-1878). AC 8.

11. **`stat.logging.info.api`.** Add one helper (same shape as `api_contact._api_completed`):
    ```python
    def _api_completed(candidate_id: Optional[str], route: str, method: str, status: int) -> None:
        """stat.logging.info.api: one completion line at the route that did the work."""
        logger.info("%s | api %s completed: %s %s", candidate_id or "-", route, method, status)
    ```
    Call it on success in the routes whose behaviour this ticket changes: `POST /agents` (201), `PUT /agents/<id>` (200), `POST /adhoc/test` (200), `POST /dispatch_tasks/<id>/run` (200), `POST /session_resume/parse` (its returned status), `POST /dispatch_tasks` and `PUT /dispatch_tasks/<id>` (their success status). GET routes get no info line (the statute excludes idempotent reads).

## Stage 2: `api_candidate` — per-server keys in, set/not-set out

1. **Outbound.** `_sanitize_candidate`:
   ```python
   def _sanitize_candidate(c: dict) -> dict:
       """Strip every key (plaintext map + legacy ciphertext); inject per-server set/not-set. Applied to every outbound candidate."""
       keys = c.pop("candidate_api_keys", None)
       if keys is None and c.get("astral_candidate_id"):
           # List rows come without the hydrated map; core get_candidate is the only ui-legal read.
           keys = (get_candidate(c["astral_candidate_id"]) or {}).get("candidate_api_keys")
       c.pop("candidate_api_key", None)
       c["api_keys"] = {sid: {"label": s["label"], "set": bool((keys or {}).get(sid))} for sid, s in LLM_SERVER_CONFIG.items()}
       return c
   ```
   `has_api_key` is removed; Manage Candidates is its only reader (Stage 4). This closes the plaintext leak described above. AC 4: `GET` the candidate shows both servers `set: true`.
   ⚠️ **Decision (list rows use a per-row `get_candidate`):** `ui` may not import `data` (`stat.layers.import-rules`). The only core read of a candidate's keys is `get_candidate`, which decrypts them, and a core `list_candidate_server_keys` wrapper would mean editing `core/candidate.py`, which is outside Scope. This is correct but not the cheapest option. A thin core wrapper is the efficiency follow-up if Susan wants one.

2. **Inbound.** In `update_candidate_data`, replace `api_key = body.pop("api_key", None)` with `api_keys = body.pop("api_keys", None)`. Before the write block, validate: it must be a dict, every key must be in `LLM_SERVER_CONFIG`, and every value must be a `str`. Otherwise return 400 naming the bad server id. Keep `api_keys is not None` in the "has work" check. In the write block:
   ```python
   for sid, key in (api_keys or {}).items():
       if key.strip():
           set_candidate_api_key(candidate_id, sid, key.strip())
       else:
           clear_candidate_api_key(candidate_id, sid)
   ```
   Setting Kimi and OpenRouter in one save leaves two `candidate_key` rows, both Fernet ciphertext (the data layer encrypts). AC 4. The existing PUT completion info lines stay as they are.

## Stage 3: Legacy retirement

Run after Stages 1–2, once nothing in `src/` imports the symbols (checked with the step 7 greps before deleting).

1. `src/utils/config.py`:
   - Delete the `"active_provider"` key (and its comment) from `LLM_PROVIDER_CONFIG`.
   - Delete the `tier_map["deepseek"]` block.
   - Delete `DEEPSEEK_MODEL_PRICING` and the "AST-1851 parity" assert loops that follow it.
   - Delete `DEEPSEEK_CONCURRENCY` (legacy alias; `deepseek.py` was its only reader).
   - Delete `get_active_llm_provider`, `resolve_brain_setting_to_deepseek_tier_meta`, `deepseek_brain_max_tokens_floor`.
   - Delete `CONTACT_ESTELLE_CONFIG["default_brain_setting"]` and `assert CONTACT_ESTELLE_CONFIG["default_brain_setting"] == BRAIN_MEDIUM`.
   - Update the header-inventory lines that name these symbols.
   - **Left in place (not named in Scope):** `LLM_PROVIDER_CONFIG["brain_settings"]` / `tier_map["anthropic"]`, `validate_allowed_brain_setting`, `resolve_brain_setting_to_anthropic_agent_key`, `anthropic_agent_key_for_brain_setting`, `brain_setting_for_anthropic_agent_key`, `admin_brain_setting_catalog`, `infer_brain_setting_from_legacy_model_code` (`database.py` still imports it). After Stage 1 several of these have no `src/` caller. Listed under **Follow-ups**.
2. `src/utils/cost_calculator.py`: delete `deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, `calculate_cost_components_deepseek` and their header-inventory lines. `usage_to_token_counts` / `calculate_cost_components_from_counts` (AST-1877) are the replacements and are already used by `llm_compat.py` and `database.py`.
3. `git rm src/external/deepseek.py`.
4. Clear the remaining vendor names in in-scope files, so the AC 2 grep has zero hits (comments included; `api_admin.py` lines 399 / 456 are rewritten by Stage 1 anyway).
5. `tests/component/external/test_deepseek.py` and `docs/test-bible/external/deepseek.md`: **Betty deletes these in qa-child** (the engineer's pre-commit hook blocks both paths). Until then `test_deepseek.py` fails on import. It is listed first under **Tests expected to move**.
6. **`src/core/monitor.py`:** replace `get_active_llm_provider` with `get_llm_server` (config) and `task_llm_server_id` (`src.core.agent`; no cycle, since `agent.py` does not import `monitor`). In `provider_balance_outage`:
   ```python
   provider = get_llm_server(task_llm_server_id(task_key))["label"]
   ```
   This stays inside the existing never-raises `try`. The subject and `Provider:` line then name the server the refused task actually called, not a global setting.
7. Verification greps (AC 1, 2, 7, parent AC 11):
   ```bash
   rg -n "active_provider|get_active_llm_provider" src/
   rg -n -i "kimi|moonshot|openrouter|deepseek" src/ --glob '!src/utils/config.py'
   test -e src/external/deepseek.py; rg -n "send_to_deepseek" src/
   rg -n "default_brain_setting" src/
   ```
   All must be empty (and `test -e` must fail). `rg … tests/` for `send_to_deepseek` clears once Betty removes `test_deepseek.py`.

## Stage 4: Frontend

1. **`AdminAgentPrompts.tsx`.**
   - Replace `BrainSettingCatalogRow[]` with `ModelCatalog = Record<string, {label, server_id, server_label, brain_sizes: Record<string, {default_temperature, default_max_tokens}>}>`, fetched from `/api/admin/agents/models`.
   - Add `editModelId` / `addModelId` state.
   - `BrainSettingFields` gets a Model select (`Object.entries(models)`, label shown), then the Brain size select from `models[modelId]?.brain_sizes` only.
   - Changing the model keeps the size when the new model has it. Otherwise it resets to the model's first size and prefills temperature / max tokens from that size's defaults (today's tier-change prefill, now reading the model's row).
   - The existing "unmapped" option stays for a stored size the model lacks.
   - Add and edit bodies send `model_id` + `brain_setting`.
   - Add a "Model" column showing `models[a.model_id]?.label ?? a.model_id ?? "—"`.
   - AC 6: only the selected model's sizes are shown, and a re-GET shows both fields.
2. **`AdminManageCandidates.tsx`.**
   - `CandidateRow.has_api_key` → `api_keys?: Record<string, {label: string; set: boolean}>`.
   - `editForm.api_key` → `api_keys: Record<string, string>`; `clearKey` → `clearKeys: Record<string, boolean>`; `showKey` → `showKeys: Record<string, boolean>`.
   - Render one field per `Object.entries(editTarget.api_keys)`: the label is `${label} API key (leave blank to keep current)`, with a Show/Hide toggle, and a Clear button when `set` (same confirm dialog, naming the server).
   - Save sends `api_keys` with only the servers that changed (typed value, or `""` for cleared). It omits the key when nothing changed.
   - Table column `api_key_status` shows the labels with `set: true`, joined, or "Not set".
   - No placeholder with a vendor-specific key prefix. AC 6: field count equals server count.
3. **`AdminScheduledActions.tsx`.** Add `invalid_reason?: string` to the row type. `invalidTitle` = `row.invalid_reason || (tokens joined) || "Could not validate prompts"`. AC 5 tooltip.
4. **`AdminSessionResumePaste.tsx`.**
   - `const { selectedId } = useCandidate()`.
   - The body adds `candidate_id: selectedId`.
   - Parse is `disabled={!selectedId || !pasteText.trim() || parsing}`, with a `title` explaining a candidate must be selected.
   - Copy: "Uses the selected candidate's API key for Ruth's model; does not save to the database."
   - AC 8.

## Compile / lint (every stage)

- Python: `.venv/bin/python -m py_compile` on each touched `.py`, then `.venv/bin/ruff check` on the same files (F401 catches imports left unused by the Stage 1 swap). Plus an import smoke: `PYTHONPATH=.:src .venv/bin/python -c "import src.ui.api.api_admin, src.ui.api.api_candidate, src.core.monitor, src.utils.cost_calculator"`.
- Frontend (Stage 4): `npm ci` in `src/ui/frontend` (no `node_modules` in the worktree yet), then `npm run build` (`tsc -b && vite build`) and `npm run lint`.
- Stage 3: run the step 7 greps.

## Acceptance mapping (this ticket)

1→S3 steps 1, 6 + S1 steps 5–6 (`api_admin` imports) | 2→S3 steps 2–4 + S1 (rewritten comments) + S4 (no vendor literals) | 3→S1 steps 1, 3–4 | 4→S2 | 5→S1 steps 8–9 + S4 step 3 | 6→S4 steps 1–2 + S1 step 1 | 7→S3 step 3 (+ Betty's `test_deepseek.py` delete) | 8→S1 step 10 + S4 step 4 (Betty intercept test: key on the wire, candidate row byte-identical). Radia deferrals → S1 steps 6–9, S2 step 2, S3 step 1. AST-1883 → S3 step 2. Parent AC 11 (`rg default_brain_setting src/`) → S3 step 1.

## Tests expected to move (Betty — qa-child; engineer does not edit `tests/`)

- **Delete:** `tests/component/external/test_deepseek.py`, `docs/test-bible/external/deepseek.md` (and their rows in `docs/test-bible/README.md` / `docs/ASTRAL_TEST_BIBLE.md`).
- `tests/component/ui/api/test_api_admin.py` + `tests/component/ui/conftest.py`: `/agents/models` shape, `/agents/brain_settings` gone, agent create/update need `model_id`, ad-hoc kwargs, the dispatch gate's `(cid, task_key)` signature + `invalid_reason`, and session paste `candidate_id`.
- `tests/component/utils/test_config.py`: deleted symbols + parity asserts.
- `tests/component/utils/test_cost_calculator.py`, `tests/component/utils/test_cost_calculator_deepseek.py`: deleted wrappers (the second file may retire or move to `calculate_cost_components_from_counts`).
- `tests/component/core/test_monitor.py`: `get_active_llm_provider` monkeypatch → `task_llm_server_id` (+ `get_llm_server` label).
- `tests/component/core/conftest.py`, `test_agent.py`, `test_agent_ast1879.py`, `tests/component/utils/test_llm_external.py`, `tests/component/data/database/test_timesheets.py`: all hit the deleted-symbol grep. Each needs its reference re-checked.
- Candidate API tests (wherever `has_api_key` / `api_key` PUT are covered): `api_keys` in and out, and no plaintext in any response.

## Observations (outside Scope — for Chuckles, not changed here)

- `src/core/dispatcher.py` (#3) calls `task_llm_server_id(task_key)` without a `try` at its key gate. A dispatch task with no agent that reaches that gate (not one of the meteorite ingress / notify / mailbox branches) would raise there. `meteorite_retention` has no `agent_task` row, but I did **not** confirm whether it reaches the gate. Flagging for a check at UAT, not claiming a bug.
- `principal_recruiter_estelle` `max_tokens: 384000` on Kimi K2.6 Big (Radia's AST-1879 discuss item) is adjustable in Manage Agents after this ticket. No cap is added in code.

## Follow-ups (not this ticket)

- Dead Anthropic-legacy helpers left in `config.py` (see S3 step 1 "Left in place"). Deleting them needs a Scope line naming them.
- A core `list_candidate_server_keys` wrapper, if the per-row `get_candidate` on the candidate list is too slow (S2 Decision).

## Revisions

- Scope amended with `src/core/monitor.py` (scope-gate resolved). Its Files Changed row and Stage 3 step 6 are no longer marked pending. No other plan change.

## Estimate

Confirm Chuckles estimate: 5 — revise to 8 because this is four backend files plus four frontend pages plus the legacy deletions, and the Invalid gate, key UI and agent pickers are each a separate round-trip to verify.

## Joan validate

[plan-rubric]
**Ticket:** AST-1880
**Overall:** APPROVED
**Corpus:** `e1f2699fad`
**Publish ref:** `16dbe56de`

## Canon scores

Model → server catalog routing | A | | Stages 1–4: catalog admin routes/UI, server-scoped keys, Invalid gate, legacy path removed
stat.logging.info.api | A | | Stage 1 `_api_completed` on mutating routes this ticket changes; GET reads omitted
stat.logging.warning | A | | Missing-key Invalid/AUTO, task-manager unroutable agent, dispatch skip who/why/consequence

## Traceability

1→S3 steps 1,6 + S1 import swap | 2→S3 steps 2–4 + S1 comment rewrites + S4 (no vendor literals) | 3→S1 steps 1,3–4 | 4→S2 | 5→S1 steps 8–9 + S4 step 3 | 6→S4 steps 1–2 + S1 `/agents/models` | 7→S3 step 3 (+ Betty deletes `test_deepseek.py` for `tests/` grep) | 8→S1 step 10 + S4 step 4 (+ Betty wire/key intercept) | parent 3–4,7,9–14→N/A (#1–#3 or not on this child’s AC list)

## Findings

### discuss

- **Severity:** discuss
- **Location:** **Estimate**
- **Finding:** Plan recommends revising Linear points to **8** while the ticket still shows **5**; scope (four backend surfaces, four frontend pages, Stage 3 deletions, Invalid gate) supports the higher estimate.
- **Recommendation:** Chuckles updates Linear estimate before or at Plan Approved.

- **Severity:** discuss
- **Location:** AC 7 / **Tests expected to move**
- **Finding:** Engineer pre-commit cannot delete `tests/component/external/test_deepseek.py`; `rg send_to_deepseek tests/` stays dirty until Betty’s qa-child pass, though product `src/` clears in Stage 3.
- **Recommendation:** Expected epic handoff — Betty deletes bible/test paths early in qa-child on this sub.

- **Severity:** discuss
- **Location:** Stage 2 `_sanitize_candidate` decision
- **Finding:** List rows may call `get_candidate` per row for set/not-set (correct under layer rules, potentially slow); plan flags a core wrapper follow-up if Susan wants it.
- **Recommendation:** No plan change unless Susan opts into the follow-up.

### acceptable

- **Severity:** acceptable
- **Location:** Scope gate / **Revisions**
- **Finding:** `src/core/monitor.py` server-labeled `provider_balance_outage` is now in Scope, Files Changed, and Stage 3 step 6 — AC 1 can clear without leaving `get_active_llm_provider` in `monitor.py`.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** Stage 2 plaintext leak / Radia deferrals
- **Finding:** Plan closes AST-1878/1879 review items (`api_candidate` arity, ad-hoc `TypeError`, dispatch Run/Auto gate, `default_brain_setting` grep) with explicit stage ownership.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** Stage 3 step 1 “Left in place” / **Follow-ups**
- **Finding:** Anthropic-legacy config helpers may become dead after Stage 1; plan defers deletion to a scoped follow-up rather than silent scope creep.
- **Recommendation:** None unless Susan wants a cleanup ticket.

context_tokens≈155000

[plan-rubric] PROCEED (Commit: 16dbe56de) Admin + legacy retirement plan clean


## Review

- **Branch:** `origin/sub/AST-1851/AST-1880-admin-model-pickers-platform-keys`
- **Build tip:** `df3bcb890` (stages: `0c0bef06e` api_admin catalog route, agent `model_id` routes, catalog ad-hoc/history, server-key Invalid gate, session paste candidate, info.api lines · `482ad1ff5` api_candidate per-server keys in / set-not-set out · `673927ace` legacy retirement + `monitor.py` server label · `df3bcb890` admin UI pages)
- **Build notes:** Built as planned, with one addition. Flask `jsonify` sorts keys in this app, so the model catalog came out Big, Little, Medium instead of catalog order. `GET /agents/models` therefore adds an `order` index on each model and each brain size, and the UI sorts by it. The response stays keyed by id. The AC 1 / AC 2 / AC 7 / `default_brain_setting` greps over `src/` (frontend included) are all empty. `_sanitize_candidate` smoke: a two-key map comes out as `api_keys` set flags with no plaintext. Lint: `ruff --select F` shows only the pre-existing unused `cfg` in `api_admin._enrich_tasks`. ESLint shows only the 2 pre-existing `no-extra-boolean-cast` errors in `AdminScheduledActions.tsx`. `npm run build` passes. `ruff` was installed into the local gitignored `.venv`, and `npm ci` was run in `src/ui/frontend`.
- **For qa-child:** see **Tests expected to move** above. `test_deepseek.py` now fails on import (module deleted), so delete it together with `docs/test-bible/external/deepseek.md`.

## Radia review

[code-rubric]
**Ticket:** AST-1880
**Publish ref:** 387f84ac5
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** DISCUSS

## Canon scores

stat.logging.info.api | C | 2 | `api_candidate.py` `update_candidate_data` — no completion `logger.info` when the PUT only mutates `api_keys`
stat.logging.warning | A | |

## Column diff vs plan stage

stat.logging.info.api — Joan A, Radia C (api_keys-only PUT completion line)

## Frame diff

- [ ] **Estimate:** Confirm Linear estimate matches plan revision (**8** vs ticket **5**) if Chuckles has not already updated.
- [ ] **Parent AC 7 (`rg send_to_deepseek tests/`):** Engineer to confirm on merged ftr after Betty’s qa-child pass (product `src/` clean; two test files still contain the string in negative-assertion / fixture metadata).

## Findings

### fix-now

(none)

### discuss

- **Severity:** discuss  
- **Location:** `src/ui/api/api_candidate.py` — `update_candidate_data`  
- **Finding:** `stat.logging.info.api` expects one completion info line per mutating route. Admin routes use `_api_completed`; candidate `PUT …/data` still logs only when catalog leaves (strengths, resume, etc.) save. A body with **only** `api_keys` updates keys via `set_candidate_api_key` / `clear_candidate_api_key` but emits **no** `api completed` line.  
- **Recommendation:** Add one `logger.info("%s | api %s completed: PUT %s", …)` before the successful return when `api_keys is not None` (or unify with `_api_completed` pattern).  
- **Default:** `resolve-child` adds the single line on the success path; no behavior change.

- **Severity:** discuss  
- **Location:** Parent **AC 7** vs tip `tests/`  
- **Finding:** `src/external/deepseek.py` is gone and `rg send_to_deepseek src/` is empty. `tests/` still matches `send_to_deepseek` in `test_agent_ast1879.py` (forbidden-name tuple) and `test_llm_external.py` (fixture `func_name`). Not product imports; epic grep AC 7 fails until Betty renames strings or documents exceptions.  
- **Recommendation:** qa-child early pass per plan **Tests expected to move** (already deleted `test_deepseek.py` on tip).  
- **Default:** Betty adjusts assertions/fixtures; no #1880 product revert.

- **Severity:** discuss  
- **Location:** Plan **Estimate**  
- **Finding:** Plan recommends **8** points; Linear still **5**.  
- **Recommendation:** Chuckles sync estimate if not done at plan approval.  
- **Default:** Proceed on scope; estimate is bookkeeping.

- **Severity:** discuss  
- **Location:** Stage 2 `_sanitize_candidate` / list candidates  
- **Finding:** List rows may call `get_candidate` per row to hydrate set/not-set flags (plan-flagged perf).  
- **Recommendation:** Optional core list wrapper follow-up if Susan wants it.  
- **Default:** Ship as-is.

### advisory

- **Severity:** advisory  
- **Location:** AST-1878 / AST-1879 Radia deferrals (this brief)  
- **Finding:** **Resolved on tip:** `clear_candidate_api_key(candidate_id, sid)` in `api_candidate.py`; `_resolve_adhoc` + `adhoc_test` use `resolve_model_brain`, `server_id`, `tier`, `candidate_api_keys`; dispatch list/run use `task_llm_server_id` + `_candidate_dispatch_api_key_error` (`invalid_reason`, AUTO off, Run 400); `rg default_brain_setting src/` empty; `rg active_provider|get_active_llm_provider src/` empty; `CONTACT_ESTELLE_CONFIG["default_brain_setting"]` removed with legacy provider retirement; `monitor.py` labels outage by `task_llm_server_id` server label.  
- **Recommendation:** None.

- **Severity:** advisory  
- **Location:** Three-dot diff vs `origin/dev`  
- **Finding:** Includes full epic stack (#1877–#1879); **#1880 code commits** touch `api_admin`, `api_candidate`, `config` legacy deletion, `deepseek.py` removal, `cost_calculator` wrapper removal, `monitor.py`, four admin TSX pages.  
- **Recommendation:** Score canon against #1880 surfaces.

- **Severity:** advisory  
- **Location:** Build note — `GET /agents/models` `order` field  
- **Finding:** Flask `jsonify` key order vs catalog UI order; explicit `order` index added — reasonable addition.  
- **Recommendation:** None.

## What's solid

- **Pattern / AC (product):** Catalog-driven agents (`GET /agents/models`), model-scoped brain validation on save, per-server `api_keys` in/out without plaintext leak, Invalid gate + tooltip reason + Run 400, legacy provider path removed from `src/`.
- **AC 2:** No vendor literals in `src/` outside `config.py` on tip.
- **stat.logging.warning:** Missing-key Invalid (`invalid_reason`, AUTO forced off with who/why), dispatch empty-render warnings, task-manager patterns unchanged where applicable.
- **stat.logging.info.api:** `_api_completed` on agent create/update, ad-hoc test success, session resume parse, dispatch run — matches plan Stage 1.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1880): Radia review — discuss`, post slim upshot, **Review Posted** → datt **REVIEW** → `resolve-child` for the `api_keys` completion log (or Susan waives).
- Betty: finish AC 7 test-tree grep + any remaining bible paths per build notes.
- Susan: optional estimate + list-row perf follow-up.

context_tokens≈45000

## Resolution

- **fix-now:** none.
- **discuss — `api_keys`-only PUT completion log:** took the `Default:`. `update_candidate_data` now emits one `api … completed: PUT 200` line when `api_keys` is the only thing that changed. It stays silent when an artifact save already logged completion, so there is never a second line. Commit `be239f09a`.
- **discuss — AC 7 test-tree grep:** Betty fixed it (`0ede9b9a7`, merged as `eb81cfe3a`). No product change.
- **discuss — Estimate, list-row decrypt:** took the `Default:` (not engineer items). Chuckles keeps 5, and the list decrypt ships as-is.
- **Gates:** §9a dry-run merges into `origin/dev` and `origin/ftr/AST-1851-support-openrouter-api-models` are both clean. `validate-sub-log` is **blocked**: there are two `merge-tests(AST-1880)` commits on the sub (`e74930781`, `eb81cfe3a`). That is test-delivery history, so it went to Betty via `[qa-handoff]`. The ticket stays Review Posted.

## Bug: AST-1909 — Manage Task modal: no Model dropdown of config-driven model keys

> **Scope:** `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` was added to AST-1851's Component and Technical scope after the `[scope-gate]`: "Manage Task modal: model + brain-size selects for the task's agent (catalog-driven); loads `GET /api/admin/agents/models`, saves the task's agent `model_id` + brain size via the existing agent update route; no task-level model, no backend change". The change below stays inside that scope.

### As-is
The Manage Task modal (`AdminTaskPrompts.tsx`) shows the model only as read-only text (`Model: <SKU>` from `editTask.model_code`). The config-driven model picker (`GET /api/admin/agents/models`) is only reachable from Manage Agents, so a model can't be chosen while editing a task.

### To-be
The Manage Task modal has a **Model** select filled from the config model catalog (`LLM_MODEL_CONFIG` keys, via `GET /api/admin/agents/models`) and a **Brain size** select listing only that model's sizes. Saving the task persists the selection.

**Where the selection is stored (settled by the parent, not a new decision).** AST-1851 makes the model **per agent**. Its Purpose says "each agent picks a **model** and a **brain size** valid for that model", Functional scope 1 is "Per-agent model + brain size", and the original brief says "the agent table should point to the model". So the modal writes the **task's assigned agent's** `model_id` + `brain_setting` through the existing `PUT /api/admin/agents/<agent_id>`. There is no task-level model column, which would contradict the parent and need a schema change outside its scope.

### Repro
1. Admin → Manage Tasks → click any task whose agent is a real agent row (e.g. a task on `principal_recruiter_estelle`, which `data/admin/agent_task.json` assigns to 15 tasks).
2. The modal header shows `Model: kimi-k2.6` as plain text. There is no select, so no model can be chosen.
3. Fixture for the component test: `GET /api/admin/tasks/<key>` → `{agent_id: "principal_recruiter_estelle", model_code: "kimi-k2.6", ...}`; `GET /api/admin/agents/principal_recruiter_estelle` → `{model_id: "kimi-k2.6", brain_setting: "Big", ...}`; `GET /api/admin/agents/models` → the four-model catalog with `order` fields (AST-1880 shape).

### Root cause
AST-1880 (Stage 4) put the model + brain-size pickers only on Manage Agents, which is where AST-1851's Component scope assigned them (Functional scope 8, "Admin surfaces", names Manage Agents and Manage Candidates only). The Manage Task modal still renders the legacy read-only `model_code` line from before the per-agent catalog existed.

### Proposed change
All in `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`. **No backend change**: every route needed already exists from AST-1880.

1. **Catalog.** On mount, fetch `GET /api/admin/agents/models` into `models: ModelCatalog` (same `ModelRow` / `BrainSizeRow` types as `AdminAgentPrompts.tsx`, keyed by id). Add the same `byOrder` helper, because `jsonify` sorts keys and `order` carries catalog order. It's duplicated rather than shared because moving it to a shared module would touch a second unscoped file.
2. **Load the agent's current model.** New state: `editModelId`, `editBrainSetting`, and `loadedAgentModel: {model_id, brain_setting} | null`. Whenever `editAgentId` is set (in `openEdit` and when the agent select changes), `GET /api/admin/agents/<editAgentId>` sets all three from the row's `model_id` / `brain_setting`. If the agent id is `""`, `"n/a"`, or a 404, set them to `""` / `null`. That case has no agent row, so no model can be picked.
3. **Selects replace the read-only line.** Replace `<span><strong>Model:</strong> {editTask.model_code || "—"}</span>` with:
   - **Model** `<select>`: `byOrder(models)`, option label `models[id].label`. When there is no agent row it is disabled, with the option "— no agent —".
   - **Brain size** `<select>`: `byOrder(models[editModelId]?.brain_sizes)`.
   - Changing the model keeps the size when the new model has it, otherwise it takes the model's first size. This is the same rule as Manage Agents (`sizeForModel`). Temperature and max tokens are not touched here; they stay agent fields edited in Manage Agents.
   - A hint under the selects: `Applies to agent <editAgentId> — used by <N> task(s)`, where `N = tasks.filter(t => t.agent_id === editAgentId).length`. Every task on that agent changes, and Estelle has 15.
4. **Save.** In `handleSave`, after the existing `PUT /api/admin/tasks/<task_key>` succeeds: if there is an agent row and `(editModelId, editBrainSetting)` differs from `loadedAgentModel`, send `PUT /api/admin/agents/<editAgentId>` with body `{model_id: editModelId, brain_setting: editBrainSetting}`.
   - Non-OK response: throw the response's `error` into the existing error toast. The task fields are already saved, and the agent row is unchanged because the route returns 400 before writing (AST-1880 Stage 1 step 4).
   - Success: the existing success toast and `loadAll()` re-fetch, so the list's Model column shows the new SKU (`_enrich_tasks` resolves it from the agent).
   - When nothing changed, no agent PUT is sent.
   - ⚠️ **Decision (two requests, task first):** the task route doesn't own agent fields and the agent route doesn't own task fields. Keeping them separate needs no backend change and no new scope. If the agent PUT fails, the user sees the error and can retry. Nothing is half-written within either row.
5. **No literals.** Model and size options come only from the catalog response, so the AC 2 grep stays empty.

### Blast radius
- **Shared agents:** the selection changes the model for **every** task on that agent (`principal_recruiter_estelle` 15, `job_analyst_grace` 9, `college_intern_ruth` 7, `content_writer_judith` 6, `ats_expert_atlas` 3). This is the per-agent design working as intended, and the hint in step 3 makes it visible.
- **Routes reused unchanged:** `GET /api/admin/agents/models`, `GET` / `PUT /api/admin/agents/<id>` (AST-1880 Stage 1), and the task `PUT`.
- **Tests:** `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (if present) mocks `api()` by URL. The modal now also calls `/api/admin/agents/models` and `/api/admin/agents/<id>`, so unmatched URLs in existing mocks may need defaults (Betty).
- **No change** to Manage Agents, the dispatcher, or execution-history math.

### What must still hold
- AST-1880 AC 3 / parent AC 5: a Kimi model with brain size Medium is rejected with 400 and the agent row is unchanged. The modal can't offer Medium for Kimi, and the route still enforces it.
- Parent AC 2: `rg -n -i "kimi|moonshot|openrouter|deepseek" src/ --glob '!src/utils/config.py'` stays empty.
- Parent AC 12: Manage Agents' pickers behave exactly as before.
- Task save without a model change sends the same single task `PUT` as today.


### Joan fix-board — AST-1909

```
[board-joan]  CANON: OK
```

**Rationale:** The patch is frontend-only in `AdminTaskPrompts.tsx`: it reuses AST-1880’s catalog route and agent `PUT`, writes the task agent’s `model_id` + `brain_setting` (per-agent model routing from parent **Model → server catalog routing**), and keeps options off `GET /api/admin/agents/models` with no vendor literals (parent AC 2). That extends catalog-driven admin behavior; it does not conflict with in-force logging statutes (no new API routes or completion paths) or config-as-source-of-truth. The task-level vs agent-level storage question is settled in the patch from the parent definition, not an open canon carve-out.

```
AST-1909 board-joan done — CANON: OK.
```


### Radia review — AST-1909

[code-rubric]
**Ticket:** AST-1909
**Publish ref:** 9c7591ea9
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

(parent AST-1851 Canon Scope — UAT-batch bound; ticket carries no frozen ids of its own)

Model → server catalog routing | A | |
stat.logging.debug | X | |
stat.logging.error | X | |
stat.logging.warning | X | |
stat.logging.info.api | X | |

## Column diff vs plan stage

no plan-stage canon scores attached (fix-board only)

## Frame diff

(none)

## [bug-repro]

**Verdict:** OK — `describe("AST-1909 task modal model + brain size")` pins to-be: catalog `GET /api/admin/agents/models`, model + brain selects (not read-only SKU), `sizeForModel` rule, task `PUT` then conditional agent `PUT` with `{model_id, brain_setting}`, no agent `PUT` when unchanged / no agent / 404, shared-agent hint, agent `PUT` 400 toast after task save. Would fail on pre-fix read-only `Model:` line and missing selects.

**Advisory:** qa-fix commit message says `bug-repro`; no first-line `[bug-repro]` tag on the test class (fixture literals `kimi-k2.6` in tests only — not AC 2 `src/`).

## What must still hold

**Verdict:** OK

- **AC 3 / Kimi + Medium:** Kimi brain options in tests are `Little` / `Big` only; switching to Kimi drops invalid `Medium` to first size — UI cannot submit Kimi+Medium; backend 400 path covered by agent-PUT error toast test.
- **Parent AC 2:** no vendor/server literals in `AdminTaskPrompts.tsx` (options from catalog API only).
- **Manage Agents:** product commit touches only `AdminTaskPrompts.tsx` — `AdminAgentPrompts.tsx` unchanged on `9c7591ea9`.
- **Task-only save:** test asserts zero agent `PUT` when model/size unchanged.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Severity:** advisory  
- **Location:** `origin/ftr/AST-1851-support-openrouter-api-models...origin/sub/AST-1901-candidate-keys-json-array` (spawn used **ftr** base per brief)  
- **Finding:** Three-dot range includes **sibling** commits (AST-1904/1905 `builder.py`, feature docs) ahead of AST-1909 on the publish branch. **AST-1909 product** is single-file `9c7591ea9` (+ Betty tests `58098c74c`).  
- **Recommendation:** Score and merge AST-1909 on its commits; do not treat sibling diffs as this fix’s footprint.

- **Severity:** advisory  
- **Location:** Parent **AC 12** wording vs scope-gate  
- **Finding:** Parent AC 12 names Manage Agents / Manage Candidates; this fix extends catalog-driven model picking to **Manage Tasks** per amended Component scope — intentional, not a regression of Manage Agents.  
- **Recommendation:** Optional parent AC note at epic close if Susan wants AC 12 prose to mention Manage Tasks.

## What's solid

- Plan patch followed: catalog on mount, `loadAgentModel` with stale-request guard, selects replace read-only `model_code`, `handleModelChange` matches Manage Agents, two-step save (task then agent), shared-agent hint, no backend changes.
- Extends **Model → server catalog routing** admin surface without task-level model column.
- Component tests cover catalog order, persistence, agent change, disabled states, and agent PUT failure after task PUT.

## Recommended actions (Chuckles)

- Append artifact; `docs(AST-1909): Radia review — clean`; post slim upshot; **Review Posted** → fix-lane **PROCEED** shortcut → **User Testing** (skip `resolve-child`).
- **Parent shape:** AST-1851 UAT-batch, **not orphaned** — normal sub merge path (not straight-to-dev).

context_tokens≈32000

---

`[code-rubric] PROCEED (Commit: 9c7591ea9) task modal catalog picks`
