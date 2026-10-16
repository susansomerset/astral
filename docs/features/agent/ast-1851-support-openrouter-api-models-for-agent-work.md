# AST-1851 — Support OpenRouter API models for agent work

<!-- linear-archive: AST-1851 archived 2026-10-08 -->

## Linear archive (AST-1851)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Astral's agents all run on one global vendor switch (`LLM_PROVIDER_CONFIG["active_provider"]`, today DeepSeek), and DeepSeek is not zero-data-retention. Susan wants agent work on ZDR-capable hosting and the freedom to trial other models on content generation — starting with Kimi K2.6 for Estelle and Judith on Kimi tokens she has already bought — without each new model turning into a code change. The outcome: each agent picks a **model** and a **brain size** valid for that model; `config.py` maps every model to the **server** (platform/protocol) that serves it — Kimi direct, OpenRouter (ZDR-capable; enforcement is future scope), Anthropic, DeepSeek, … — and a server is never something an operator chooses, only the pipe behind a model. Each candidate holds one API key per platform, the platform list comes from config, and a candidate missing the key a task needs is **Invalid** — no system-key fallback.

## Functional scope

 1. **Per-agent model + brain size.** Every agent names a catalog model and one of *that model's* brain sizes. Models declare their own brain sizes — some three (Little/Medium/Big), some two, some more. Changing an agent's model is just saving a new model + brain size. The global active-provider switch goes away.
 2. **Model catalog in config.** Each model names its server and, per brain size, the vendor SKU, thinking/reasoning flags, output-token floor, temperature/max-token defaults, and pricing. Starting catalog: **Kimi K2.6 (Kimi direct)** — Little (thinking off) and Big (thinking on); **Kimi K2.6 via OpenRouter** — same two sizes; **Claude** — today's Little/Medium/Big = Haiku/Sonnet/Opus; **DeepSeek V4** — today's Little/Medium/Big. Adding a model is a config edit only.
 3. **Server catalog in config.** Each server entry carries its endpoint, auth style, and request extras it always sends — designed for per-request parameters such as OpenRouter's `provider.zdr`, but ZDR is **not** enforced in this release (Susan: future scope). Operators never pick a server. Adding a server is a config edit only — no server or model name appears in code outside `config.py`.
 4. **One shared client for Anthropic-Messages-compatible servers.** Kimi, OpenRouter, and DeepSeek all expose an Anthropic-Messages-compatible endpoint; one external client serves them, parameterized by the server entry. Anthropic stays on its existing client.
 5. **One API key per platform per candidate.** A candidate stores one encrypted key per server (the platform that issued it); two models on the same platform share that key. Susan enters keys manually per candidate — no migration of the old single key; the legacy `candidate.candidate_api_key` value is no longer read or written.
 6. **No key, no run.** A candidate-key task uses only the candidate's key for its model's server — no env fallback, never another platform's key. A scheduled action whose candidate lacks that key shows **Invalid** on Scheduled Actions (same treatment as today's empty-render Invalid: AUTO forced off, Run blocked, tooltip names the missing platform key), and the dispatcher skips it at run time. **Every LLM task is a candidate-key task** (Susan: tasks running on a system key is a bug) — `select_job_page` and `contact_estelle_turn` join the rest; Estelle's Slack turn loads the resolved candidate's keys and fails with a clear reason when no candidate / no key. The Admin **session resume paste** (`simple_resume_parse`) runs with the globally selected candidate's key — Parse is refused with no candidate selected — and still never binds or persists the parse onto that candidate.
 7. **Contact Estelle is her own agent record.** Estelle for Slack contact becomes a discrete `agent` row, separate from Estelle for deep analysis; `contact_estelle_turn` points at it, and the hardcoded conversational brain override is removed — the contact row's own model + brain size apply.
 8. **Admin surfaces.** Manage Agents: model select, then a brain-size select listing only that model's sizes. Manage Candidates: one key field per server in the catalog (set / replace / clear).
 9. **Cost ledger per server.** Timesheet rows record the real server and vendor SKU, token volumes per token type (fresh input, cache read, cache write, output), and the transaction cost computed across those types from catalog pricing; the allowed timesheet-provider set derives from the server catalog.
10. **Seed update.** `data/admin/agent.json` names a model for every agent — Estelle (analysis) and Judith on Kimi K2.6 (Kimi direct), Big; a new contact-Estelle row (content copied from `principal_recruiter_estelle`) on Kimi K2.6 (Kimi direct), Little; Atlas, Ruth, Grace, Laslo on DeepSeek V4 at their current brain sizes (unchanged behaviour until Susan re-picks them in Manage Agents).

## Component scope

* `src/utils/config.py` — **modified** — server + model catalogs (per-model brain sizes, pricing, request extras), resolvers, retire `active_provider`, per-model brain-size validation, every `TASK_CONFIG` entry requires the candidate key, derived timesheet providers, agent model field in `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]`.
* `src/external/deepseek.py` — **deleted** — replaced by the server-agnostic client below.
* `src/external/llm_compat.py` — **new** — one Anthropic-Messages-compatible client for every non-Anthropic server.
* `tests/component/external/test_deepseek.py` — **deleted** — covers the deleted `deepseek.py`.
* `docs/test-bible/external/deepseek.md` — **deleted** — bible page for the deleted `deepseek.py`.
* `src/utils/cost_calculator.py` — **modified** — price from the model catalog instead of `DEEPSEEK_MODEL_PRICING`.
* `src/utils/llm_external.py` — **modified** — docstrings stop naming DeepSeek (AC 2).
* `env.example` — **modified** — per-server env vars, if Open question 1 keeps any.
* `src/data/database.py` — **modified** — agent model field; per-server candidate key table; candidate hydration returns the key map; legacy single key no longer read/written; per-model brain-size validation on agent save; timesheet provider validation; header inventory.
* `src/core/candidate.py` — **modified** — per-server key save/clear wrappers; session resume parse takes a candidate id and uses its key map.
* `data/admin/agent.json` — **modified** — model on every agent row; new contact-Estelle row.
* `data/admin/agent_task.json` — **modified** — `contact_estelle_turn` points at the contact-Estelle agent.
* `src/core/agent.py` — **modified** — `do_task` / `run_adhoc` route by agent model → server → brain size; pick the matching candidate key.
* `src/core/dispatcher.py` — **modified** — run-time skip gate checks the key for the task agent's server.
* `src/core/meteorite.py` — **modified** — pass the candidate key map (not the single key) into task ctx.
* `src/core/contact.py` — **modified** — Estelle turn passes the resolved candidate ctx (key map) into `do_task`.
* `src/ui/api/api_admin.py` — **modified** — agent routes carry model; model catalog route (with per-model brain sizes); ad-hoc resolve and execution-history display by model; Scheduled Actions Invalid check + Run/Auto gate for a missing platform key; session resume parse route requires `candidate_id`.
* `src/ui/api/api_candidate.py` — **modified** — per-server key set/clear and per-server set/not-set on outbound candidates.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` — **modified** — model select + model-scoped brain-size select.
* `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — **modified** — one key field per catalog server.
* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — Invalid tooltip shows the missing-key reason.
* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — **modified** — sends the selected candidate; Parse disabled with none selected.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` — **modified** — Manage Task modal: model + brain-size selects for the task's agent (catalog-driven) ([AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys), UAT).

## Technical scope

* `src/utils/config.py`: new server catalog block (endpoint, auth style, request extras, e.g. OpenRouter's `provider.zdr` — not set in this release); new model catalog block keyed by model id → server + ordered brain sizes, each with SKU / flags / max-tokens floor / defaults, plus per-SKU pricing (folds in today's `AGENT_CONFIG` tier use, DeepSeek tier map, and `DEEPSEEK_MODEL_PRICING`); modified resolvers so model + brain size → server + tier meta + pricing; per-model brain-size validation replaces the global `BRAIN_SETTINGS` check; remove `active_provider` / `get_active_llm_provider`; modified startup env validation per Open question 1; allowed timesheet providers derived from server ids; (the agent model field in the repo-admin agent columns is #2's — [AST-1883](https://linear.app/astralcareermatch/issue/AST-1883/unblock-ast-1877-ok-to-move-two-scope-lines-to-ast-1878-ast-1880)).
* `src/external/llm_compat.py`: new send function (same result contract as today's `send_to_deepseek`) taking the server entry, SKU, tier flags, and key; applies server request extras; reuses `llm_external` timeout / balance / empty-response classification.
* `src/utils/cost_calculator.py`: modified cost functions look pricing up through the model catalog.
* `src/utils/llm_external.py`: modified docstrings only.
* `src/data/database.py`: agent model field (plan-child picks: repurpose the legacy `model_code` column or add a new one — exactly one column holds the catalog model id), in save/update allowlist and repo JSON validate/import/export; brain size validated against the model on save; new candidate key table (candidate id + server id + Fernet ciphertext + timestamps) with set/clear/list helpers; modified `get_candidate` to hydrate a server → key map and stop exposing the legacy single key; modified timesheet insert validation; header inventory updated.
* `src/core/candidate.py`: modified admin save/clear wrappers take a server id; modified `run_session_resume_parse` requires a candidate id and adds that candidate's key map to its synthetic ctx (token view unchanged — no bind/persist).
* `data/admin/agent.json`: modified rows gain the model field (values per Functional scope 10).
* `src/core/agent.py`: modified `do_task` resolves server + tier from agent model + brain size (conversational brain override removed), selects the candidate key for that server with no fallback, and dispatches to the Anthropic client or the shared compat client; modified `run_adhoc` / workbench wrapper route by server instead of `tier_meta is not None`.
* `src/core/dispatcher.py`: modified skip gate checks the key for the task agent's server.
* `src/core/meteorite.py`: modified ctx hand-off carries the key map.
* `src/core/contact.py`: modified Estelle turn builds `do_task` ctx from the resolved candidate (key map included); no candidate → turn fails with a reason, no call goes out.
* `src/ui/api/api_admin.py`: new GET model catalog route (models + their brain sizes) replacing the global brain-settings catalog; modified agent routes accept/return model and reject a brain size the model lacks; modified ad-hoc resolve and execution-history display via model catalog; modified dispatch Invalid evaluation and Run/Auto gate add a missing-platform-key reason; modified `session_resume/parse` route requires `candidate_id` (400 without) and passes it to core.
* `src/ui/api/api_candidate.py`: modified PATCH accepts per-server keys (non-empty = set, empty = clear); modified outbound strip exposes per-server set/not-set.
* `AdminAgentPrompts.tsx` / `AdminManageCandidates.tsx`: modified forms render from the catalog endpoints — no literal model or server names.
* `AdminScheduledActions.tsx`: modified Invalid tooltip renders the server-provided missing-key reason alongside today's missing-token list.
* `AdminSessionResumePaste.tsx`: modified Parse posts the `CandidateContext` selected candidate id; disabled with a hint when none is selected.
* `AdminTaskPrompts.tsx`: modified Manage Task modal loads `GET /api/admin/agents/models` and saves the task's agent `model_id` + brain size via the existing agent update route — per-agent design, no task-level model, no backend change ([AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys)).

## Architectural definition

**Patterns to reuse:** no established pattern applies — none of the in-force patterns (artifact / entity batch / task chain) govern LLM routing.

**New patterns proposed (Archie approval needed before children depend on it):**

* **Model → server catalog routing** — agent row names a model + brain size; config maps model → server + per-model brain sizes + pricing; the server entry owns endpoint, auth, and request extras; one compat client serves every Anthropic-Messages-compatible server. Introduced by child 1; reused by any future model/server addition.

**Applicable statutes:**

* `stat.logging.debug` — provider call params/response stay on the gated debug channel in the new client. [file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)
* `stat.logging.error` — provider failures logged once at the handler with live facts. [file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>)
* `stat.logging.warning` — dispatch skip / AUTO-off for a missing platform key is a per-item who+why warning. [file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>)
* `stat.logging.info.api` — agent-model and candidate-key admin routes log once on completion. [file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)

## Acceptance criteria

 1. **Global switch gone.** `rg -n "active_provider|get_active_llm_provider" src/` returns nothing. Any hit = fail.
 2. **No server or model names outside config.** `rg -n -i "kimi|moonshot|openrouter|deepseek" src/ --glob '!src/utils/config.py'` returns nothing (frontend included). Any hit = fail.
 3. **Agent rows name catalog models with valid sizes.** Every row in `data/admin/agent.json` has a model id that is a config model-catalog key and a brain size in that model's list (a Python one-liner loading both prints nothing). Any missing/unknown model or size = fail.
 4. **Seed values.** `principal_recruiter_estelle` and `content_writer_judith` carry the Kimi K2.6 (Kimi direct) model id with brain size Big; the new contact-Estelle row carries Kimi K2.6 (Kimi direct) with Little; the other four agents carry the DeepSeek V4 model id with their pre-epic brain sizes. Any other value = fail.
 5. **Brain sizes are per model.** `GET /api/admin/agents/models` lists Kimi K2.6 (direct) and Kimi K2.6 via OpenRouter with exactly `Little, Big`, and Claude / DeepSeek V4 with `Little, Medium, Big`. Saving an agent on a Kimi model with brain size Medium returns 400 and leaves the row unchanged. A 200, or a list mismatch = fail.
 6. **One key per platform per candidate.** Setting a Kimi key and an OpenRouter key on one candidate via Manage Candidates leaves two rows for that candidate in the candidate key table, both Fernet ciphertext (neither equals the plaintext), and `GET` the candidate shows both servers set. One row, plaintext, or one key overwriting the other = fail.
 7. **Right key, no fallback.** A candidate-key task for an agent on server X, for a candidate with keys for X and Y, sends X's key (component test intercepting the outbound client). With no X key, the task fails with an error naming X and no request goes out — not with Y's key, not with an env key. Any outbound request in the no-key case = fail.
 8. **Invalid on Scheduled Actions.** For a scheduled action whose candidate lacks the key for its task agent's server, `GET` the dispatch-task list returns `empty_render: true` with a reason naming that server, AUTO is forced off, `POST /api/admin/dispatch_tasks/<id>/run` returns 400, and the Invalid tooltip shows the reason. Adding the key flips the row back to valid on the next list. Any of these not holding = fail.
 9. **Request extras, ZDR not enforced.** A server entry's request extras from config appear in the outbound request body (intercepted-request component test with a test extra), and the shipped OpenRouter entry sends no `provider.zdr`. Extras dropped, or `zdr` sent in this release = fail.
10. **Ledger per server.** An Estelle (analysis) task run writes an `agent_timesheets` row whose provider is the Kimi direct server id, model is the K2.6 SKU, token columns hold the call's fresh-input / cache-read / cache-write / output volumes, and cost equals the per-type sum from catalog pricing (component test recomputes it). Provider `deepseek`, zero tokens, or a cost mismatch = fail.
11. **Contact Estelle is a discrete agent.** `data/admin/agent_task.json`'s `contact_estelle_turn` row names the new contact-Estelle agent (not `principal_recruiter_estelle`); `rg -n "default_brain_setting" src/` returns nothing; an Estelle Slack turn goes out at the contact row's model + brain size (component test). Any of these not holding = fail.
12. **Catalog-driven admin UI.** Manage Agents' brain-size select shows only the selected model's sizes and saving persists model + size (re-GET shows both). Manage Candidates shows exactly one key field per server catalog entry. Field count ≠ server count, or hardcoded options (AC 2 grep) = fail.
13. **Legacy key retired.** `get_candidate` no longer returns a single `candidate_api_key` string (component test), and no save path writes the legacy column. Either still present = fail.
14. **No system-key tasks.** `python -c` over `TASK_CONFIG` finds no entry without `requires_candidate_key: True`; an Estelle Slack turn for a candidate with a key for her model's server goes out with that key (component test), and one for an unresolved Slack user sends no request. Any flag missing or any outbound request in the no-candidate case = fail.
15. **DeepSeek client removed.** `test -e src/external/deepseek.py` fails and `rg -n "send_to_deepseek" src/ tests/` returns nothing. Either present = fail.
16. **Session paste uses the selected candidate.** `POST /api/admin/session_resume/parse` without `candidate_id` returns 400 and sends no request; with a candidate holding the key for Ruth's model's server it goes out with that key (component test), and the candidate row is byte-identical before/after. A 200 without a candidate, another key on the wire, or a changed candidate row = fail.

## Open questions

None.

## Proposed child tickets

#### 1!!!: **Model/server catalog + shared compat client - Ada**

Config gains the server and model catalogs (per-model brain sizes, pricing, request-extras support), and one Anthropic-Messages-compatible client is added. **Additive only:** the legacy provider symbols (`active_provider`, `get_active_llm_provider`, DeepSeek-only resolvers/pricing) and `deepseek.py` stay importable so the tree stays green until #4 deletes them. Costing reads catalog pricing. Does **not** touch the DB (#2), runtime routing (#3), or admin UI (#4).
**Citations:** new pattern *Model → server catalog routing*; `stat.logging.debug`, `stat.logging.error`.
**Scope:** `src/utils/config.py` — server catalog; model catalog with ordered brain sizes, SKU/flags/floors/defaults, pricing; modified resolvers; per-model brain-size validation; startup env validation; every `TASK_CONFIG` entry requires the candidate key; derived timesheet providers. `src/external/llm_compat.py` — new send function, today's result contract, server extras, `llm_external` reuse. `src/utils/cost_calculator.py` — pricing via model catalog. `src/utils/llm_external.py` — docstrings only. `env.example` — per-server env vars.
Estimate: 5

#### 2!!: **Agent model field + per-platform candidate keys - Hedy**

After #1. The `agent` table and seed carry a model; brain size is validated against it; candidates store one encrypted key per server and hydrate as a server → key map; the legacy single key goes dark. Does **not** change call routing (#3) or admin routes/UI (#4).
**Citations:** new pattern *Model → server catalog routing*.
**Scope:** `src/data/database.py` — agent model field (save/update allowlist, repo JSON), per-model brain-size validation on save, candidate key table + set/clear/list helpers, `get_candidate` key map without the legacy key, timesheet insert validation, header inventory; backfill switches to `calculate_cost_components_from_counts`. `src/utils/config.py` — **only** add the agent model field to `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` ([AST-1883](https://linear.app/astralcareermatch/issue/AST-1883/unblock-ast-1877-ok-to-move-two-scope-lines-to-ast-1878-ast-1880) approved exception). `src/core/candidate.py` — per-server save/clear wrappers; `run_session_resume_parse` requires a candidate id and adds its key map to the synthetic ctx (no bind/persist). `data/admin/agent.json` — model on every row; new contact-Estelle row (content copied from `principal_recruiter_estelle`, Kimi K2.6 direct, Little). `data/admin/agent_task.json` — `contact_estelle_turn` points at the contact-Estelle agent.
Estimate: 5

#### 3!: **Route agent calls by model → server - Katherine**

After #2. `do_task` and the ad-hoc runner pick server + tier from agent model + brain size, use only that server's candidate key (no fallback), and call the Anthropic client or the shared compat client; dispatcher skip gate, meteorite hand-off, and Estelle's Slack turn read the key map. Does **not** own admin routes or UI (#4).
**Citations:** new pattern *Model → server catalog routing*; `stat.logging.warning`, `stat.logging.error`.
**Scope:** `src/core/agent.py` — `do_task` server/tier/key resolution, conversational brain override removed, client dispatch; `run_adhoc` / workbench wrapper route by server. `src/core/dispatcher.py` — skip gate on the task agent's server key. `src/core/meteorite.py` — ctx hand-off carries key map. `src/core/contact.py` — Estelle turn passes resolved candidate ctx; no candidate → fail with reason.
Estimate: 5

#### 4: **Admin: model + brain pickers, per-platform keys, Invalid on missing key - Ada**

After #3. Manage Agents picks model then a model-scoped brain size; Manage Candidates shows one key field per server; Scheduled Actions flags Invalid (AUTO off, Run blocked, tooltip reason) when the candidate lacks the needed platform key; ad-hoc resolve and execution history go through the catalog. Last child, so it also retires the legacy provider path once nothing imports it. Does **not** own the catalog (#1) or storage (#2).
**Citations:** `stat.logging.info.api`, `stat.logging.warning`.
**Scope:** `src/ui/api/api_admin.py` — model catalog route; agent routes carry model and reject invalid sizes; ad-hoc resolve and execution-history display via catalog; Invalid evaluation + Run/Auto gate for a missing platform key. `src/ui/api/api_candidate.py` — per-server key PATCH and outbound set/not-set. `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` — model + brain-size selects. `src/ui/frontend/src/pages/AdminManageCandidates.tsx` — one key field per server. `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — missing-key reason in the Invalid tooltip. `session_resume/parse` route requires `candidate_id` (in `api_admin.py` above). `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` — posts the selected candidate; Parse disabled with none selected. **Legacy retirement:** `src/utils/config.py` — delete `active_provider` / `get_active_llm_provider`, the DeepSeek-only resolvers/pricing, and `CONTACT_ESTELLE_CONFIG["default_brain_setting"]` (no other [config.py](<http://config.py>) edits). `src/external/deepseek.py` — deleted. `tests/component/external/test_deepseek.py` — deleted. `docs/test-bible/external/deepseek.md` — deleted. `src/utils/cost_calculator.py` — delete the DeepSeek-named wrappers (`deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, `calculate_cost_components_deepseek`) ([AST-1883](https://linear.app/astralcareermatch/issue/AST-1883/unblock-ast-1877-ok-to-move-two-scope-lines-to-ast-1878-ast-1880)).
Estimate: 5

**New patterns:** #1 introduces *Model → server catalog routing*; #2–#4 consume it, and any future model or server is a config-only addition on top of it.

**Monolith check:** 10 functional items, 4 children — split by layer (config/external → data → core → UI).

**Scope partition check:** every Component scope file appears in exactly one child's Scope line above, with **named exceptions** (each child must stay green on its own `sub/*`): `src/utils/config.py` is #1's, #2 touches it only to add the agent model field to the repo-admin agent columns, and #4 only to delete the legacy provider symbols; `src/utils/cost_calculator.py` is #1's, and #4 deletes its DeepSeek-named wrappers ([AST-1883](https://linear.app/astralcareermatch/issue/AST-1883/unblock-ast-1877-ok-to-move-two-scope-lines-to-ast-1878-ast-1880), approved).

---

## Original brief

[https://platform.kimi.ai/console/projects/api-keys](<https://platform.kimi.ai/console/projects/api-keys>)

We need to start sending some task work to OpenRouter to see if other models do a better job with the content generation (and support ZDR).  We will use the model for Estelle and Judith going forward with a Kimi K2.6 model, the other agents may use something else as a replacement to DeepSeek (which is emphatically not ZDR).

Make sure with this change that we can support multiple api-keys for each candidate, starting with these three and potentially more in the future as needed (read: do not hardcode the three keys). So, the agent table should point to the model (not the server, specifically) and the [config.py](<http://config.py>) needs to point the models (and their corresponding brain size settings) to their server (e.g. kimi directly or OpenRouter or anthropic, or whatever).

### Comments

#### chuckles — 2026-10-01T00:36:20.147Z
AST-1909 blocked at merge-child — its sub picked up AST-1902 epic commits via a shared astral-tests merge-tests; needs @susan call before merging into ftr (details on AST-1909).

#### chuckles — 2026-10-01T00:13:32.631Z
[fix-intake]
Filed AST-1909 from the 2026-10-01T00:12Z [bug] (it is at Discussion, assigned to Susan for diagnosis review).

#### susan — 2026-10-01T00:12:46.477Z
\[bug\] I cannot select the model from a dropdown list of config-driven model keys in the Manage Task modal.

#### chuckles — 2026-09-30T22:38:24.209Z
[fix-intake]
Filed AST-1901 from the 2026-09-30T22:37Z [bug] (it is at Discussion, assigned to Susan for diagnosis review).

#### susan — 2026-09-30T22:37:25.660Z
\[bug\] @chuckles This implementation for the candidate key management is completely wrong.  It needs to be an array of JSON between model and key, not 4 hardcoded keys.  Candidate_key should not exist.

#### chuckles — 2026-09-30T22:03:30.551Z
[fix-intake]
Filed AST-1900 from the 2026-09-30T22:00Z [bug] (it is at Discussion, assigned to Susan for diagnosis review).

#### susan — 2026-09-30T22:00:15.531Z
\[bug\]

```
2026-09-30T00:20:40.744305978Z [inf]  Mounting volume on: /var/lib/containers/railwayapp/bind-mounts/0336ed6f-d19b-432e-819f-939b147a3708/vol_8bvr5t0127ic9dq5
2026-09-30T00:20:41.856594409Z [err]  [2026-09-30 00:20:41 +0000] [1] [INFO] Starting gunicorn 26.2.0
2026-09-30T00:20:41.856598179Z [err]  [2026-09-30 00:20:41 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
2026-09-30T00:20:41.856602789Z [err]  [2026-09-30 00:20:41 +0000] [1] [INFO] Using worker: sync
2026-09-30T00:20:41.856607779Z [err]  [2026-09-30 00:20:41 +0000] [4] [INFO] Booting worker with pid: 4
2026-09-30T00:20:41.856611679Z [err]  [2026-09-30 00:20:41 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl
2026-09-30T00:20:41.873951091Z [inf]  Starting Container
2026-09-30T19:35:59.572260876Z [err]  /opt/venv/lib/python3.12/site-packages/stytch/core/client_base.py:86: UserWarning: Test version of Stytch not intended for production use
2026-09-30T19:35:59.572263616Z [err]    warnings.warn("Test version of Stytch not intended for production use")
2026-09-30T19:49:47.764248448Z [wrn]  src.utils.auth: Bearer token validation failed: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
2026-09-30T21:59:28.420652199Z [err]  src.core.dispatcher: somerset | dispatch task prefilter_company crashed
Traceback (most recent call last):
  File "/app/src/core/dispatcher.py", line 1642, in _task_thread_target
    loop.run_until_complete(_dispatch_one(task))
  File "/root/.nix-profile/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/src/core/dispatcher.py", line 997, in _dispatch_one
    await _dispatch_one_body(task, debug)
  File "/app/src/core/dispatcher.py", line 1337, in _dispatch_one_body
    server_id = task_llm_server_id(task_key)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 1839, in task_llm_server_id
    return _agent_llm_route(agent_row)["server_id"]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 1829, in _agent_llm_route
    raise ValueError(f"Agent '{aid}' has no model_id configured.")
ValueError: Agent 'job_analyst_grace' has no model_id configured.
```

#### chuckles — 2026-09-29T22:20:18.929Z
AST-1880 gated on AST-1890 — duplicate merge-tests on sub fails validate-sub-log; clearing needs a history rewrite (forbidden) or a validator waiver.

#### chuckles — 2026-09-29T22:16:26.837Z
AST-1880 REVIEW — Radia: add api completed log on api_keys-only candidate PUT (Ada resolve); `send_to_deepseek` still in two test files breaks AC 7 (Betty).

#### chuckles — 2026-09-29T19:30:12.719Z
@susan

- Folded your session-paste answer in: Parse runs with the selected candidate's key and is refused with none selected (still no bind/persist).
- One thing needs your OK before dispatch: as drafted, #1 deleted `deepseek.py` and the global provider switch while #2–#4 still import them, so #1's branch would not build. I rewrote it so #1 is additive and **#4 does the deletions**. That means `config.py` is touched by two children (#1 builds the catalogs, #4 only deletes the dead legacy symbols) — a named exception to the one-file-one-child rule. OK to dispatch with that exception? (Move to Todo + assign me if yes.)

#### chuckles — 2026-09-29T19:13:32.926Z
@susan

- Folded "this is a bug" in: every LLM task now requires the candidate key, and Estelle's Slack turn uses the resolved candidate's key (fails cleanly with no candidate).
- Still missing before dispatch — `simple_resume_parse` is the Admin **session resume paste**; it deliberately runs with **no candidate**, so it has no key to use. Which fix: **(a)** the paste form takes a candidate and uses that candidate's key; **(b)** keep one system key for this single tool (env var named in config); or **(c)** retire the session paste?

#### chuckles — 2026-09-29T05:33:41.611Z
@susan

1. Three tasks don't require a candidate key today — `simple_resume_parse`, `select_job_page`, and `contact_estelle_turn` (Estelle's Slack chat) — so they run on the system env key. With Estelle on Kimi, where does their key come from: **(a)** one system env key per platform in Railway (e.g. a Kimi key), used only by these no-candidate tasks; or **(b)** use the candidate's platform key whenever a candidate is resolved, and fail when there isn't one?

#### chuckles — 2026-09-29T05:22:59.128Z
@susan

1. I read "these three" keys as **Kimi, OpenRouter, and Anthropic**, with DeepSeek retired — right? The key already stored on each candidate is labeled "Anthropic" in the UI but actually gets sent to DeepSeek today; should it migrate to the Anthropic slot, or be dropped?
2. Estelle + Judith on Kimi K2.6: call **Kimi directly** (the platform.kimi.ai key — Kimi says API data isn't stored for training, but it isn't a formal ZDR guarantee) or route K2.6 **through OpenRouter** with ZDR enforced on every request?
3. The other four agents (Atlas, Ruth, Grace, Laslo): which model replaces DeepSeek in this epic — or do they stay on DeepSeek until a later ticket picks one?
4. Kimi K2.6 brain tiers — proposed: Little = thinking off, Medium = thinking off, Big = thinking on. OK, or different?
5. System fallback keys: today a candidate with no key falls back to the server's env key (`DEEPSEEK_API_KEY`). Keep one env fallback key per server (named in config), or candidate keys only with no fallback?

---

_Implementation detail may live in git history on `origin/dev`._
