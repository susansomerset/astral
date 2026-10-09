<!-- linear-archive: AST-1877 archived 2026-10-08 -->

## Linear archive (AST-1877)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1877/modelserver-catalog-shared-compat-client-support-openrouter-api-models  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 5  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851; blocks: AST-1878

### Description

## What this implements

Config gains the server and model catalogs (per-model brain sizes, pricing, request-extras support), and one Anthropic-Messages-compatible client is added. **Additive only:** the legacy provider symbols (`active_provider`, `get_active_llm_provider`, DeepSeek-only resolvers/pricing) and `deepseek.py` stay importable so the tree stays green until #4 deletes them. Costing reads catalog pricing. Does **not** touch the DB (#2), runtime routing (#3), or admin UI (#4).

## Citations

new pattern *Model → server catalog routing*; `stat.logging.debug`, `stat.logging.error`.

## Scope

`src/utils/config.py` — server catalog; model catalog with ordered brain sizes, SKU/flags/floors/defaults, pricing; modified resolvers; per-model brain-size validation; startup env validation; every `TASK_CONFIG` entry requires the candidate key; derived timesheet providers. `src/external/llm_compat.py` — new send function, today's result contract, server extras, `llm_external` reuse. `src/utils/cost_calculator.py` — pricing via model catalog. `src/utils/llm_external.py` — docstrings only. `env.example` — per-server env vars.

## Acceptance criteria

9. **Request extras, ZDR not enforced.** A server entry's request extras from config appear in the outbound request body (intercepted-request component test with a test extra), and the shipped OpenRouter entry sends no `provider.zdr`. Extras dropped, or `zdr` sent in this release = fail.

## Boundaries

Stays inside the Scope above. Sibling slices: #2 data, #3 runtime routing, #4 admin UI + legacy deletion.

## Notes for planning

New pattern *Model → server catalog routing* is defined on parent AST-1851 (Architectural definition). Each child must stay green on its own `sub/*`. Additive only: legacy provider symbols and `deepseek.py` stay importable until #4.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-29T20:39:49.770Z
[code-rubric] PROCEED (Commit: d2bd76b0d) catalogs + compat clean

#### betty — 2026-09-29T20:34:03.139Z
`origin/sub/AST-1851/AST-1877-model-server-catalog-compat-client` @ `d2bd76b0d` · catalog + compat tests landed

#### joan — 2026-09-29T20:20:22.017Z
[plan-rubric] PROCEED (Commit: e9662278f) Catalog + compat plan clean

#### ada — 2026-09-29T20:18:25.466Z
`origin/sub/AST-1851/AST-1877-model-server-catalog-compat-client` @ `e9662278f` · finalized against amended Scope

#### ada — 2026-09-29T19:56:17.294Z
[scope-gate]

Plan is complete on the publish ref except one Scope line that cannot land green on this sub, plus one partition gap. Both look like small Scope moves Chuckles can make — no approach change.

1. **Move to #2 (AST-1878):** "agent model field in repo-admin columns" (`src/utils/config.py` → `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]`).
   Scope quote (#1): *"`src/utils/config.py` — … agent model field in repo-admin columns."*
   Why not here: `_validate_agent_repo_json_rows` requires each `data/admin/agent.json` row's keys to equal that tuple exactly, and `fetch_agent_repo_json_export_rows` SELECTs those columns from `agent`. The DB column (and which column it is) and the agent.json values are #2's. Adding the name in #1 makes Revert-to-file raise on every row and breaks export on this sub. It belongs with #2's column + seed change (one line in config.py — a second named config.py exception, like #4's).

2. **Partition gap — `src/utils/cost_calculator.py` legacy names:** #1 keeps `deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, `calculate_cost_components_deepseek` as catalog-backed wrappers because `src/external/deepseek.py` (#4 deletes) and `database.backfill_deepseek_agent_timesheet_costs` (#2) still import them. Parent AC 2's grep will hit them, and no child after #1 has `cost_calculator.py` in Scope. Suggest adding "`src/utils/cost_calculator.py` — delete the DeepSeek-named wrappers" to #4's legacy-retirement Scope (and #2 switching the backfill to `calculate_cost_components_from_counts`).

Re-spawn me once Scope is amended and I'll flip to Plan Ready (plan already omits item 1).

#### ada — 2026-09-29T19:56:16.414Z
`origin/sub/AST-1851/AST-1877-model-server-catalog-compat-client` @ `b1ebeedd` · plan published; scope-gate below

---

# AST-1877 — Model/server catalog + shared compat client

- **Parent:** [AST-1851 — Support OpenRouter API models for agent work](https://linear.app/astralcareermatch/issue/AST-1851)
- **Ticket:** [AST-1877](https://linear.app/astralcareermatch/issue/AST-1877)
- **Publish ref:** `origin/sub/AST-1851/AST-1877-model-server-catalog-compat-client`
- **Canon Scope:** new pattern *Model → server catalog routing* (defined on AST-1851 § Architectural definition); `stat.logging.debug`, `stat.logging.error`.

This ticket introduces the *Model → server catalog routing* pattern in config and ships the one client for every Anthropic-Messages-compatible server. `config.py` gains a **server catalog** (endpoint, auth style, thinking-off payload, request extras, optional concurrency) and a **model catalog** (model → server, ordered per-model brain sizes with SKU / thinking payload / output floor / defaults, per-SKU pricing), with resolvers, per-model brain-size validation, catalog-consistency startup validation, `requires_candidate_key: True` on every task, and timesheet providers derived from server ids. `src/external/llm_compat.py` adds `send_to_llm_compat`, which has the same result contract as `send_to_deepseek`, is parameterized by server id and SKU, never reads an env key, and applies server request extras. `cost_calculator.py` prices through the catalog. **Additive only:** `active_provider`, `get_active_llm_provider`, `LLM_PROVIDER_CONFIG`, the DeepSeek resolvers, `DEEPSEEK_MODEL_PRICING`, and `src/external/deepseek.py` stay importable and behave as today. Nothing in `src/core/`, `src/data/`, or `src/ui/` changes. DB is #2 (AST-1878), routing is #3 (AST-1879), admin + legacy deletion is #4 (AST-1880).

## Scope gate

Every row in **Files Changed** is named in this ticket's amended `## Scope` (AST-1883, approved by Susan), and every stage is the kind of change that Scope describes.

- **Repo-admin agent model column:** moved to #2 (AST-1878). Its Scope now carries the one `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]` edit. Nothing in this plan touches `REPO_ADMIN_JSON_CONFIG`.
- **DeepSeek-named cost wrappers:** `cost_calculator.py` keeps `deepseek_usage_to_token_counts`, `calculate_cost_components_deepseek_from_counts`, and `calculate_cost_components_deepseek` as catalog-backed wrappers so `src/external/deepseek.py` and `database.backfill_deepseek_agent_timesheet_costs` stay green. #2 switches the backfill to `calculate_cost_components_from_counts` (added in Stage 3), and #4 (AST-1880) deletes the wrappers.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `LLM_SERVER_CONFIG`, `LLM_MODEL_CONFIG`, resolvers, per-model brain validation, catalog startup validation, `requires_candidate_key` flips + assert, derived `ALLOWED_TIMESHEET_PROVIDERS`, `DEEPSEEK_CONCURRENCY` alias, legacy parity asserts, header inventory | utils |
| `src/utils/cost_calculator.py` | Pricing via model catalog; generic token-count + cost-from-counts functions; legacy names delegate | utils |
| `src/external/llm_compat.py` | **New** — `send_to_llm_compat` | external |
| `src/utils/llm_external.py` | Docstrings only (drop vendor names) | utils |
| `env.example` | Reword `ANTHROPIC_API_KEY` comment; no per-server env vars | root |

No other file is touched. No DB, core, UI, `data/admin/`, `tests/`, or bible edits.

---

## Stage 1: Server + model catalogs and resolvers

**Done when:** `python -c "from src.utils.config import LLM_SERVER_CONFIG, LLM_MODEL_CONFIG, resolve_model_brain; print(resolve_model_brain('kimi-k2.6','Big')['sku'])"` prints `kimi-k2.6`, `model_brain_sizes('kimi-k2.6')` is `('Little', 'Big')`, `model_brain_sizes('claude')` / `('deepseek-v4')` are `('Little', 'Medium', 'Big')`, and every existing import from `src.utils.config` still works.

1. In `src/utils/config.py`, immediately **after** the closing `}` of `LLM_PROVIDER_CONFIG` (currently line 5079, before the `# PROVIDER_BALANCE_REFUSAL` comment), insert a section header comment and `LLM_SERVER_CONFIG`:

   ```python
   # ---------------------------------------------------------------------------
   # LLM_SERVER_CONFIG — the platform/protocol behind a model (AST-1851). Operators never pick a
   # server; an agent picks a model and LLM_MODEL_CONFIG names its server. Adding a server is a
   # config edit only — no server name appears in code outside this file.
   #   protocol           — "anthropic" (src.external.anthropic) | "anthropic_compat" (src.external.llm_compat)
   #   base_url           — Anthropic SDK base_url (SDK appends /v1/messages); None = SDK default
   #   auth               — "x-api-key" | "bearer" (how the candidate's platform key is sent)
   #   thinking_off_params — body fields sent when the brain size has thinking off
   #   request_extras     — body fields sent on every request (e.g. OpenRouter provider.zdr —
   #                        NOT set in this release; ZDR enforcement is future scope)
   #   concurrency        — None, or process-wide in-flight cap + 429 backoff for this server
   # ---------------------------------------------------------------------------
   LLM_SERVER_CONFIG = {
       "anthropic": {
           "label": "Anthropic",
           "protocol": "anthropic",
           "base_url": None,
           "auth": "x-api-key",
           "thinking_off_params": {},
           "request_extras": {},
           "concurrency": None,
       },
       "kimi": {
           "label": "Kimi",
           "protocol": "anthropic_compat",
           "base_url": "https://api.moonshot.ai/anthropic",
           "auth": "bearer",
           "thinking_off_params": {"thinking": {"type": "disabled"}},
           "request_extras": {},
           "concurrency": None,
       },
       "openrouter": {
           "label": "OpenRouter",
           "protocol": "anthropic_compat",
           "base_url": "https://openrouter.ai/api",
           "auth": "bearer",
           "thinking_off_params": {"thinking": {"type": "disabled"}},
           "request_extras": {},
           "concurrency": None,
       },
       "deepseek": {
           "label": "DeepSeek",
           "protocol": "anthropic_compat",
           "base_url": "https://api.deepseek.com/anthropic",
           "auth": "x-api-key",
           "thinking_off_params": {"thinking": {"type": "disabled"}},
           "request_extras": {},
           # DeepSeek's real limit follows account balance (observed 25-26); keep max_concurrent below it.
           "concurrency": {
               "max_concurrent": 20,
               "rate_limit_retries": 4,
               "backoff_base_seconds": 2.0,
               "backoff_max_seconds": 30.0,
           },
       },
   }
   LLM_SERVER_PROTOCOLS = ("anthropic", "anthropic_compat")
   LLM_SERVER_AUTH_STYLES = ("x-api-key", "bearer")
   ```

   ⚠️ **Decision (vendor facts, verified 2026-09-29):** Kimi's Anthropic endpoint is `https://api.moonshot.ai/anthropic` with bearer auth (`ANTHROPIC_AUTH_TOKEN` in Moonshot's Claude Code docs). OpenRouter's Anthropic Messages endpoint is `POST https://openrouter.ai/api/v1/messages` with `Authorization: Bearer`, so `base_url` is `https://openrouter.ai/api`. DeepSeek keeps today's URL and `x-api-key` (what `deepseek.py` sends now).

   ⚠️ **Decision (concurrency — Susan's recommended default, she did not override):** only `deepseek` carries a `concurrency` block, holding today's `DEEPSEEK_CONCURRENCY` values verbatim. `kimi` / `openrouter` get `None`, meaning no in-flight cap and no 429 retry, until Susan approves limits for them.

2. Directly below `LLM_SERVER_AUTH_STYLES`, move the timesheet provider set here and derive it (delete the old literal block at the `# Timesheet rows (database ledgers)` comment, currently lines 4886–4889, including its 3-line comment header):

   ```python
   # Timesheet rows (database ledgers): provider string validated on insert = a server id.
   ALLOWED_TIMESHEET_PROVIDERS = tuple(LLM_SERVER_CONFIG)
   ```

   Existing values `"anthropic"` and `"deepseek"` remain members, so `database.insert_agent_timesheet` callers are unaffected.

3. Directly below `ALLOWED_TIMESHEET_PROVIDERS`, add `LLM_MODEL_CONFIG`:

   ```python
   # ---------------------------------------------------------------------------
   # LLM_MODEL_CONFIG — what an agent row picks (AST-1851). model id → server + ordered brain
   # sizes (dict order = UI order) + per-SKU pricing. Adding a model is a config edit only.
   #   brain_sizes[<size>]:
   #     sku                 — vendor model string sent as `model`
   #     thinking            — bool; False sends the server's thinking_off_params
   #     thinking_params     — body fields sent when thinking is True (ignored when False)
   #     max_tokens_floor    — int | None; output-token floor applied over the agent's max_tokens
   #     default_temperature / default_max_tokens — used when the agent row leaves them null
   #   pricing[<sku>]: model_label, cpm_input, cpm_output, cpm_cache_read, cpm_cache_write,
   #     cache_min_tokens (USD per million tokens; cache_write 0 where the vendor does not bill it)
   # ---------------------------------------------------------------------------
   LLM_MODEL_CONFIG = {
       "kimi-k2.6": {
           "label": "Kimi K2.6",
           "server": "kimi",
           "brain_sizes": {
               BRAIN_LITTLE: {
                   "sku": "kimi-k2.6",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": 0.6,
                   "default_max_tokens": 16000,
               },
               BRAIN_BIG: {
                   "sku": "kimi-k2.6",
                   "thinking": True,
                   "thinking_params": {"thinking": {"type": "enabled"}},
                   "max_tokens_floor": None,
                   "default_temperature": 1.0,
                   "default_max_tokens": 32000,
               },
           },
           # Moonshot list price 2026-09 — https://platform.kimi.ai (K2.6: $0.95 in / $4.00 out / $0.16 cache hit)
           "pricing": {
               "kimi-k2.6": {
                   "model_label": "Kimi K2.6",
                   "cpm_input": 0.95,
                   "cpm_output": 4.00,
                   "cpm_cache_read": 0.16,
                   "cpm_cache_write": 0.0,
                   "cache_min_tokens": 0,
               },
           },
       },
       "kimi-k2.6-openrouter": {
           "label": "Kimi K2.6 via OpenRouter",
           "server": "openrouter",
           "brain_sizes": {
               BRAIN_LITTLE: {
                   "sku": "moonshotai/kimi-k2.6",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": 0.6,
                   "default_max_tokens": 16000,
               },
               BRAIN_BIG: {
                   "sku": "moonshotai/kimi-k2.6",
                   "thinking": True,
                   "thinking_params": {"thinking": {"type": "adaptive"}},
                   "max_tokens_floor": None,
                   "default_temperature": 1.0,
                   "default_max_tokens": 32000,
               },
           },
           # OpenRouter bills per upstream host; catalog uses Moonshot list price (conservative).
           "pricing": {
               "moonshotai/kimi-k2.6": {
                   "model_label": "Kimi K2.6 (OpenRouter)",
                   "cpm_input": 0.95,
                   "cpm_output": 4.00,
                   "cpm_cache_read": 0.16,
                   "cpm_cache_write": 0.0,
                   "cache_min_tokens": 0,
               },
           },
       },
       "claude": {
           "label": "Claude",
           "server": "anthropic",
           "brain_sizes": {
               BRAIN_LITTLE: {
                   "sku": "claude-haiku-4-5",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": AGENT_CONFIG["claude-haiku-4-5"]["default_temperature"],
                   "default_max_tokens": AGENT_CONFIG["claude-haiku-4-5"]["default_max_tokens"],
               },
               BRAIN_MEDIUM: {
                   "sku": "claude-sonnet-4-6",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": AGENT_CONFIG["claude-sonnet-4-6"]["default_temperature"],
                   "default_max_tokens": AGENT_CONFIG["claude-sonnet-4-6"]["default_max_tokens"],
               },
               BRAIN_BIG: {
                   "sku": "claude-opus-4-6",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": AGENT_CONFIG["claude-opus-4-6"]["default_temperature"],
                   "default_max_tokens": AGENT_CONFIG["claude-opus-4-6"]["default_max_tokens"],
               },
           },
           # AGENT_CONFIG stays the Anthropic pricing source (send_to_anthropic prices by alias key).
           "pricing": {k: AGENT_CONFIG[k] for k in ("claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6")},
       },
       "deepseek-v4": {
           "label": "DeepSeek V4",
           "server": "deepseek",
           # AST-694: Little = v4-flash; Medium = v4-pro; Big = v4-pro + AST-1391 output floor.
           # Big is thinking-off today (legacy tier_map thinking=False; its reasoning_effort was never sent).
           "brain_sizes": {
               BRAIN_LITTLE: {
                   "sku": "deepseek-v4-flash",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": 1.0,
                   "default_max_tokens": 8192,
               },
               BRAIN_MEDIUM: {
                   "sku": "deepseek-v4-pro",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": None,
                   "default_temperature": 1.0,
                   "default_max_tokens": 16000,
               },
               BRAIN_BIG: {
                   "sku": "deepseek-v4-pro",
                   "thinking": False,
                   "thinking_params": {},
                   "max_tokens_floor": 384000,
                   "default_temperature": 1.0,
                   "default_max_tokens": 16000,
               },
           },
           # https://api-docs.deepseek.com/quick_start/pricing — snapshot 2026-06-03
           "pricing": {
               "deepseek-v4-flash": {
                   "model_label": "DeepSeek V4 Flash",
                   "cpm_input": 0.14,
                   "cpm_output": 0.28,
                   "cpm_cache_read": 0.0028,
                   "cpm_cache_write": 0.0,
                   "cache_min_tokens": 0,
               },
               "deepseek-v4-pro": {
                   "model_label": "DeepSeek V4 Pro",
                   "cpm_input": 0.435,
                   "cpm_output": 0.87,
                   "cpm_cache_read": 3.625,
                   "cpm_cache_write": 0.0,
                   "cache_min_tokens": 0,
               },
           },
       },
   }
   ```

   ⚠️ **Decision (model ids):** `kimi-k2.6`, `kimi-k2.6-openrouter`, `claude`, `deepseek-v4` are the catalog keys #2 seeds into `agent.json` (parent AC 3/4). SKUs are verified: `kimi-k2.6` on Moonshot and `moonshotai/kimi-k2.6` on OpenRouter.

   ⚠️ **Decision (OpenRouter pricing — Susan's recommended default):** Moonshot list rates. OpenRouter's actual charge varies by upstream host ($0.43–$1.09 input per M on 2026-09-29).

   ⚠️ **Decision (Kimi thinking payloads):** Kimi direct Big sends `{"thinking": {"type": "enabled"}}` (Moonshot's documented on/off shape, the same shape DeepSeek uses today). OpenRouter's schema requires `budget_tokens` with `enabled`, so OpenRouter Big sends `{"type": "adaptive"}`, which needs no budget number that would otherwise have to be invented. Little sends the server's `thinking_off_params`.

   ⚠️ **Decision (Kimi defaults):** temperature 0.6 with thinking off and 1.0 with thinking on (Moonshot's K2 recommendation; temperature is not sent when thinking is on, matching `send_to_deepseek`). `default_max_tokens` is 16000 for Little (same as `deepseek-v4-pro`) and 32000 for Big (thinking shares the output budget). There is no floor. Agent rows can override both. These numbers are defaults, not caps, and Susan or Joan may revise them.

   ⚠️ **Decision (DeepSeek parity):** the SKUs, pricing, defaults, and the Big 384000 floor are copied verbatim from `LLM_PROVIDER_CONFIG["tier_map"]["deepseek"]` / `DEEPSEEK_MODEL_PRICING`. Big stays thinking-off because that is its effective behavior today (`send_to_deepseek` ignores `reasoning_effort` when `thinking` is False).

4. Directly below `LLM_MODEL_CONFIG`, add the resolvers (all raise `ValueError` with the valid choices; none reads env):

   ```python
   def get_llm_server(server_id: str) -> Dict[str, Any]:
       """Server catalog entry. Raises ValueError if unknown."""
       s = LLM_SERVER_CONFIG.get(server_id)
       if not s:
           raise ValueError(f"Unknown LLM server {server_id!r}. Valid: {list(LLM_SERVER_CONFIG)}")
       return s


   def get_llm_model(model_id: str) -> Dict[str, Any]:
       """Model catalog entry. Raises ValueError if unknown."""
       m = LLM_MODEL_CONFIG.get(model_id)
       if not m:
           raise ValueError(f"Unknown LLM model {model_id!r}. Valid: {list(LLM_MODEL_CONFIG)}")
       return m


   def model_brain_sizes(model_id: str) -> tuple[str, ...]:
       """This model's brain sizes in catalog (UI) order."""
       return tuple(get_llm_model(model_id)["brain_sizes"])


   def validate_brain_setting_for_model(model_id: str, brain_setting: str) -> None:
       """Per-model brain-size check (replaces the global BRAIN_SETTINGS check for model-bound callers)."""
       sizes = model_brain_sizes(model_id)
       if brain_setting not in sizes:
           raise ValueError(
               f"Invalid brain_setting {brain_setting!r} for model {model_id!r}. Allowed: {list(sizes)}"
           )


   def get_sku_pricing(sku: str, server_id: Optional[str] = None) -> Dict[str, Any]:
       """Pricing row for a vendor SKU; server_id narrows the search. Raises on unknown or ambiguous SKU."""
       hits = [
           m["pricing"][sku]
           for m in LLM_MODEL_CONFIG.values()
           if sku in m["pricing"] and (server_id is None or m["server"] == server_id)
       ]
       if not hits:
           raise ValueError(f"Unknown SKU {sku!r} for pricing (server={server_id!r})")
       if len(hits) > 1:
           raise ValueError(f"SKU {sku!r} is priced on more than one server — pass server_id")
       return hits[0]


   def resolve_model_brain(model_id: str, brain_setting: str) -> Dict[str, Any]:
       """model + brain size → server id/entry, SKU, tier meta (the brain_sizes row), pricing."""
       validate_brain_setting_for_model(model_id, brain_setting)
       m = get_llm_model(model_id)
       tier = m["brain_sizes"][brain_setting]
       return {
           "model_id": model_id,
           "server_id": m["server"],
           "server": get_llm_server(m["server"]),
           "sku": tier["sku"],
           "tier": tier,
           "pricing": m["pricing"][tier["sku"]],
       }
   ```

   ⚠️ **Decision:** the legacy resolvers (`validate_allowed_brain_setting`, `resolve_brain_setting_to_*`, `deepseek_brain_max_tokens_floor`, `admin_brain_setting_catalog`, …) are **not modified**. Their callers in `src/core/`, `src/data/`, and `src/ui/` belong to #2–#4, and "additive only" keeps them green. The "modified resolvers" in Scope are the new catalog resolvers above. #4 deletes the legacy ones.

**Stage 1 commit:** `code(AST-1877): server + model catalogs and resolvers`

---

## Stage 2: Validation, task flags, legacy parity, inventory, env.example

**Done when:** `python -c "import src.utils.config"` succeeds. `python -c "from src.utils.config import TASK_CONFIG as T; print([k for k,v in T.items() if v.get('requires_candidate_key') is not True])"` prints `[]`. `validate_llm_provider_environment()` returns `None` with `DEEPSEEK_API_KEY` and `ANTHROPIC_API_KEY` both unset, and raises `ValueError` if a model names an unknown server.

1. In `src/utils/config.py` `TASK_CONFIG`, change `"requires_candidate_key": False` → `True` on exactly these three entries: `simple_resume_parse` (currently line 280), `select_job_page` (currently line 508), `contact_estelle_turn` (currently line 1140). No other key on those entries changes.

2. Directly after the closing `}` of `TASK_CONFIG` (currently line 1145), before the first `assert TASK_CONFIG["qualify_meteorite"]…` line, add:

   ```python
   # AST-1851: every LLM task runs on the candidate's platform key — a system-key task is a bug.
   assert all(cfg.get("requires_candidate_key") is True for cfg in TASK_CONFIG.values()), [
       k for k, cfg in TASK_CONFIG.items() if cfg.get("requires_candidate_key") is not True
   ]
   ```

   ⚠️ **Decision (why this stays green before #3):** `do_task` reads the flag only to (a) log the existing "no candidate_data" warning, (b) take `ctx["candidate_api_key"]` as override (None → today's env fallback in `send_to_deepseek`, unchanged until #3), and (c) `_effective_entity_type` returns `"candidate"` when the task has no `entity_type` and an index is passed, which only feeds hop-ledger labels and caller hydration, and neither path applies to these three tasks. The api_admin ad-hoc path uses the candidate key only when a candidate is selected. No call stops going out in this ticket.

3. Replace the `DEEPSEEK_CONCURRENCY = { … }` literal (currently lines 5101–5106) with an alias so the values have one source:

   ```python
   DEEPSEEK_CONCURRENCY = LLM_SERVER_CONFIG["deepseek"]["concurrency"]  # legacy name for deepseek.py (#4 deletes)
   ```

   Replace the preceding comment's DeepSeek sentences ("DEEPSEEK_CONCURRENCY — process-wide cap …" and "DeepSeek's real limit follows …", and "429s are retried …") with one line: `# DEEPSEEK_CONCURRENCY — legacy alias of LLM_SERVER_CONFIG["deepseek"]["concurrency"] (AST-1851).` Keep the PROVIDER_CALL_BUDGET comment lines unchanged.

4. Leave `DEEPSEEK_MODEL_PRICING` and `LLM_PROVIDER_CONFIG` literal (legacy readers use `default_temperature` / `default_max_tokens` keys the catalog pricing rows do not carry). Directly **after** `DEEPSEEK_MODEL_PRICING`'s closing `}`, add parity asserts so the legacy blocks cannot drift from the catalog before #4 deletes them:

   ```python
   # AST-1851 parity: legacy DeepSeek blocks must match LLM_MODEL_CONFIG until #4 deletes them.
   for _bs, _legacy in LLM_PROVIDER_CONFIG["tier_map"]["deepseek"].items():
       assert LLM_MODEL_CONFIG["deepseek-v4"]["brain_sizes"][_bs]["sku"] == _legacy["vendor_model"], _bs
   for _sku, _legacy in DEEPSEEK_MODEL_PRICING.items():
       for _k in ("cpm_input", "cpm_output", "cpm_cache_read", "cpm_cache_write"):
           assert LLM_MODEL_CONFIG["deepseek-v4"]["pricing"][_sku][_k] == _legacy[_k], (_sku, _k)
   ```

5. Replace the body and docstring of `validate_llm_provider_environment()` (keep the name; `src/core/bootstrap.py` calls it). It no longer reads any env var:

   ```python
   def validate_llm_provider_environment() -> None:
       """Fatal startup check: LLM catalogs are consistent. No provider key comes from env (AST-1851)."""
       for sid, s in LLM_SERVER_CONFIG.items():
           if s["protocol"] not in LLM_SERVER_PROTOCOLS:
               raise ValueError(f"LLM server {sid!r}: protocol {s['protocol']!r} not in {LLM_SERVER_PROTOCOLS}")
           if s["auth"] not in LLM_SERVER_AUTH_STYLES:
               raise ValueError(f"LLM server {sid!r}: auth {s['auth']!r} not in {LLM_SERVER_AUTH_STYLES}")
           if s["protocol"] == "anthropic_compat" and not s["base_url"]:
               raise ValueError(f"LLM server {sid!r}: anthropic_compat requires base_url")
       for mid, m in LLM_MODEL_CONFIG.items():
           get_llm_server(m["server"])
           if not m["brain_sizes"]:
               raise ValueError(f"LLM model {mid!r}: no brain sizes")
           for bs, tier in m["brain_sizes"].items():
               if bs not in BRAIN_SETTINGS:
                   raise ValueError(f"LLM model {mid!r}: brain size {bs!r} not in {BRAIN_SETTINGS}")
               if tier["sku"] not in m["pricing"]:
                   raise ValueError(f"LLM model {mid!r} {bs}: SKU {tier['sku']!r} has no pricing row")
   ```

   ⚠️ **Decision (Susan's recommended default):** startup requires no provider key env var (parent: "no system-key fallback"). Catalog consistency is what can be fatal at boot. `send_to_deepseek`'s env fallback still exists at call time until #3/#4. `get_active_llm_provider()` is untouched.

6. In the module docstring's `Config sections:` list, add two lines after the `AGENT_CONFIG` line:

   ```
     LLM_SERVER_CONFIG — LLM servers (endpoint, auth, thinking-off body, request extras, concurrency) (AST-1851)
     LLM_MODEL_CONFIG  — LLM models → server + per-model brain sizes (SKU, thinking, floor, defaults) + per-SKU pricing (AST-1851)
   ```

7. In `env.example`, replace the two comment lines above `ANTHROPIC_API_KEY=` (`# Anthropic Claude API (required for all agents)` and `# Get from: …`) with:

   ```
   # Anthropic Claude API — fallback for the Anthropic client only. Agent tasks use each candidate's
   # per-platform keys (Manage Candidates); no other LLM platform key is read from env (AST-1851).
   # Get from: https://console.anthropic.com/settings/keys
   ```

   The `ANTHROPIC_API_KEY=` line stays; `src/external/anthropic.py` still reads it. No per-server env vars are added.

**Stage 2 commit:** `code(AST-1877): catalog validation, candidate-key tasks, legacy parity`

---

## Stage 3: Cost calculator prices through the catalog

**Done when:** for the same inputs, `calculate_cost_components` / `calculate_cost_with_cache` / `calculate_cost` / `calculate_cost_components_deepseek_from_counts` return the same numbers as before, and `calculate_cost_components_from_counts(10, 20, 30, 0, sku="kimi-k2.6", server_id="kimi")` equals the per-type sum from `LLM_MODEL_CONFIG["kimi-k2.6"]["pricing"]["kimi-k2.6"]`.

1. In `src/utils/cost_calculator.py`, change the module docstring to `Cost calculation utilities for LLM API calls.\n\nPure functions. Pricing from LLM_MODEL_CONFIG via get_sku_pricing (AST-1851).` and the import line to `from src.utils.config import get_sku_pricing`.

2. In `calculate_cost`, `calculate_cost_with_cache`, `calculate_cost_components`: replace the `m = AGENT_CONFIG.get(model_code)` + `if not m: raise ValueError(...)` pair with `m = get_sku_pricing(model_code)` (it raises `ValueError` on an unknown SKU). Change "Model alias key from AGENT_CONFIG" in the Args docstrings to "Vendor SKU (catalog pricing key)", and the `Raises:` lines to "If model_code has no catalog pricing row". The math is unchanged.

3. Add below `calculate_cost_components` (new, server-agnostic; used by `llm_compat`):

   ```python
   def usage_to_token_counts(usage) -> dict:
       """Map Anthropic-Messages usage to agent_timesheets buckets.

       cache_miss = usage.input_tokens (fresh input after the last cache breakpoint);
       cache_read / cache_write default 0 when the server omits them.
       """
       return {
           "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
           "cache_miss": usage.input_tokens,
           "output": usage.output_tokens,
           "cache_write": getattr(usage, "cache_creation_input_tokens", 0) or 0,
       }


   def calculate_cost_components_from_counts(
       cache_read: int, cache_miss: int, output: int, cache_write: int, *, sku: str, server_id: str | None = None,
   ) -> dict:
       """Granular cost components from token integers, priced by catalog SKU (same keys as calculate_cost_components)."""
       m = get_sku_pricing(sku, server_id)
       return {
           "calc_cost_cache_write": (cache_write / 1_000_000) * m["cpm_cache_write"],
           "calc_cost_cache_read": (cache_read / 1_000_000) * m["cpm_cache_read"],
           "calc_cost_no_cache_input": (cache_miss / 1_000_000) * m["cpm_input"],
           "calc_cost_output": (output / 1_000_000) * m["cpm_output"],
       }
   ```

4. Change the body of `calculate_cost_components_deepseek_from_counts` to `return calculate_cost_components_from_counts(cache_read, cache_miss, output, cache_write, sku=vendor_model)` and its docstring to `"""Legacy name (deepseek.py / database.py importers) — delegates to catalog pricing."""`. Leave `deepseek_usage_to_token_counts` (it pins `cache_write` to 0, which is legacy DeepSeek semantics) and `calculate_cost_components_deepseek` unchanged. Both now reach catalog pricing through the delegating function.

   ⚠️ **Decision:** `get_sku_pricing` without `server_id` resolves by SKU alone. Every current SKU is unique across the catalog, so the Anthropic and legacy DeepSeek call sites need no server name in this file. An ambiguous SKU raises and never picks one silently.

**Stage 3 commit:** `code(AST-1877): cost calculator prices via model catalog`

---

## Stage 4: Shared Anthropic-Messages-compatible client

**Done when:** `python -c "from src.external.llm_compat import send_to_llm_compat"` imports cleanly. `rg -n -i "kimi|moonshot|openrouter|deepseek" src/external/llm_compat.py src/utils/llm_external.py` returns nothing. A call with a stubbed `_get_client` sends `request_extras` + the tier's thinking payload in `extra_body`, uses the passed key only, and returns the `send_to_deepseek` result shape.

1. Create `src/external/llm_compat.py`. Module docstring:
   `"""One client for every Anthropic-Messages-compatible server in LLM_SERVER_CONFIG (AST-1851).\n\nParameterized by server id + SKU; key always passed by the caller (no env fallback)."""`
   The file must not contain the strings `kimi`, `moonshot`, `openrouter`, `deepseek` (any case), including in comments, logs, and labels.

2. Imports (only these):

   ```python
   import random
   import threading
   import time
   from datetime import datetime
   from typing import Any, Callable, Dict, List, Optional

   from anthropic import Anthropic, RateLimitError
   import httpx as _httpx

   from src.external.anthropic import _parse_api_response, _parse_json_response, _parse_python_code_response
   from src.utils.config import PROVIDER_EMPTY_RESPONSE, get_llm_server
   from src.utils.cost_calculator import calculate_cost_components_from_counts, usage_to_token_counts
   from src.utils.integration_io import require_controlled_external_io
   from src.utils.llm_external import (
       await_provider_call_with_budget,
       classify_provider_balance_refusal,
       classify_provider_call_timeout,
       extract_api_response_text,
       is_unusable_provider_response,
       normalize_provider_error,
       provider_call_http_timeout_seconds,
       provider_call_max_retries,
       provider_call_timeout_error_message,
       provider_call_wait_timeout_seconds,
   )
   from src.utils.logging import get_logger, log_batch_id, log_llm_batch_summary

   __all__ = ["send_to_llm_compat"]

   logger = get_logger(__name__)
   ```

   ⚠️ **Decision:** the three response parsers are imported from `src/external/anthropic.py`, not copied. The `anthropic.py` and `deepseek.py` copies differ only in comments and `# pragma` markers (verified by AST diff), and `anthropic.py` is permanent. `llm_external.py` is docstrings-only in this ticket, so they cannot move there.

3. `_get_client(server: Dict[str, Any], api_key: str) -> Anthropic`:

   ```python
   def _get_client(server: Dict[str, Any], api_key: str) -> Anthropic:
       # Exactly one explicit credential: the SDK then skips ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN
       # env lookup, so no other platform's key can ride along.
       cred = {"auth_token": api_key} if server["auth"] == "bearer" else {"api_key": api_key}
       return Anthropic(
           base_url=server["base_url"],
           timeout=_httpx.Timeout(provider_call_http_timeout_seconds()),
           max_retries=provider_call_max_retries(),
           **cred,
       )
   ```

4. Per-server concurrency (only for servers whose `concurrency` is not None):

   ```python
   _slots: Dict[str, threading.BoundedSemaphore] = {}
   _slots_lock = threading.Lock()


   def _create(client: Anthropic, api_kwargs: Dict[str, Any], server_id: str, concurrency: Optional[Dict[str, Any]]) -> Any:
       """Blocking messages.create in a worker thread; servers with a concurrency block get a
       process-wide slot cap and jittered 429 backoff (slot held only during the call)."""
       if not concurrency:
           return client.messages.create(**api_kwargs)
       with _slots_lock:
           sem = _slots.setdefault(server_id, threading.BoundedSemaphore(int(concurrency["max_concurrent"])))
       attempts = int(concurrency["rate_limit_retries"]) + 1
       base = float(concurrency["backoff_base_seconds"])
       cap = float(concurrency["backoff_max_seconds"])
       for attempt in range(attempts):
           try:
               with sem:
                   return client.messages.create(**api_kwargs)
           except RateLimitError:
               if attempt == attempts - 1:
                   raise
               delay = min(base * (2 ** attempt), cap) * random.uniform(0.5, 1.0)
               logger.warning("%s 429; retry %d/%d in %.1fs", server_id, attempt + 1, attempts - 1, delay)
               time.sleep(delay)
   ```

   ⚠️ **Decision:** the semaphore map is keyed by server id, so the deepseek cap is separate from `deepseek.py`'s own `_call_slots` while both clients exist. #3 moves traffic off `deepseek.py`, and #4 deletes it, so the two caps never both carry production load.

5. `send_to_llm_compat` signature (keyword-only after `content_blocks`):

   ```python
   async def send_to_llm_compat(
       content_blocks: List[Dict[str, Any]],
       *,
       server_id: str,
       sku: str,
       tier: Dict[str, Any],
       api_key: str,
       system_blocks: Optional[List[Dict[str, Any]]] = None,
       temperature: Optional[float] = None,
       max_tokens: Optional[int] = None,
       response_format: Optional[str] = None,
       prompt_label: str = "(unknown)",
       candidate_id: Optional[str] = None,
       task_key_uuid: Optional[str] = None,
       no_cache_prompt_tokens: int = 0,
       no_cache_live_tokens: int = 0,
       batch_size: int = 1,
       record_timesheet: Optional[Callable[..., None]] = None,
   ) -> Dict[str, Any]:
   ```

   `tier` is the `LLM_MODEL_CONFIG[...]["brain_sizes"][size]` row (as returned in `resolve_model_brain(...)["tier"]`, possibly with `thinking` overridden by the caller). There is **no** `debug` / `api_key_override` parameter: `stat.logging.debug` says callees don't take `debug=` for logging, and the key is mandatory.

6. `send_to_llm_compat` body. Mirror `send_to_deepseek` (`src/external/deepseek.py` lines 226–527) step for step, with **only** these differences:
   a. First line: `require_controlled_external_io("llm_compat.send_to_llm_compat")`. Then, before any `try`: `server = get_llm_server(server_id)`. If `server["protocol"] != "anthropic_compat"`, raise `ValueError(f"Server {server_id!r} is not anthropic_compat")`. If `not sku`, raise `ValueError("sku is required for send_to_llm_compat")`. If `not api_key`, raise `ValueError(f"No API key for server {server_id!r}")`. None of these send a request.
   b. `client = _get_client(server, api_key)` (no env fallback).
   c. `api_kwargs = {"model": sku, "max_tokens": max_tokens, "messages": [{"role": "user", "content": content_blocks}]}`. Thinking and extras travel in the body via `extra_body`:
      ```python
      thinking_on = bool(tier.get("thinking"))
      thinking_body = (tier.get("thinking_params") or {}) if thinking_on else server["thinking_off_params"]
      api_kwargs["extra_body"] = {**thinking_body, **server["request_extras"]}
      if temperature is not None and not thinking_on:
          api_kwargs["temperature"] = temperature
      if system_blocks:
          api_kwargs["system"] = system_blocks
      ```
      Do **not** carry over `deepseek.py`'s `output_config` / `reasoning_effort` logic or the `files-api` beta header. The thinking body comes verbatim from config, and no task sends document blocks today (`rg '"type": "document"' src/` is empty).
   d. The call is `_create(client, api_kwargs, server_id, server["concurrency"])` inside `await_provider_call_with_budget(..., timeout_seconds=provider_call_wait_timeout_seconds())`.
   e. Before the call: `logger.debug("Calling messages.create: server=%s %s", server_id, api_kwargs)`. After a successful call, once the response exists: `logger.debug("Response from messages.create: %s", response)`. Both are ungated and untruncated (`stat.logging.debug`). Remove every `if debug:` block, every `logger.set_debug_flag`, and every `emit_llm_call_debug` call present in the mirrored code.
   f. Token counts: `counts = usage_to_token_counts(response.usage)`. Cost: `calculate_cost_components_from_counts(counts["cache_read"], counts["cache_miss"], counts["output"], counts["cache_write"], sku=sku, server_id=server_id)`. Timesheet kwargs are identical to `send_to_deepseek`'s except `model_code=sku` and `provider=server_id`.
   g. Every `log_llm_batch_summary(logger, "deepseek", …)` becomes `log_llm_batch_summary(logger, server_id, …)`. It stays the single per-call WARNING line on failure (`stat.logging.error` § Resolution 3). No `logger.error` / `logger.exception` is added, because the caller owns entity-state error logging.
   h. The return dicts are unchanged: success is `{"success": True, "api_response", "parsed_response", "timesheet"}`. The hollow-response, `max_tokens`-truncated JSON, parse-error, inner-except, and outer-except branches keep the same keys and `failure_class` rules (`PROVIDER_EMPTY_RESPONSE`, `"max_tokens"`, timeout class, balance-refusal class). The `record_timesheet` try/except-pass wrappers also stay as they are.

7. In `src/utils/llm_external.py`, docstrings only:
   - Line 1: `"""Shared helpers for Anthropic and Anthropic-Messages-compatible external LLM clients (AST-687 / AST-538 / AST-1851)."""`
   - `extract_api_response_text` docstring: `"""Return model answer text; skip thinking blocks that lack `.text` (extended thinking)."""`
   No code changes.

**Stage 4 commit:** `code(AST-1877): shared anthropic-compat client`

---

## Acceptance mapping (this ticket)

- **AC 9 (request extras, ZDR not enforced):** `send_to_llm_compat` merges `server["request_extras"]` into `extra_body`, so a test that patches a server entry's `request_extras` sees the extra in the intercepted body. The shipped `openrouter` entry has `request_extras: {}`, so no `provider.zdr` is sent. **Betty (qa-child) lands the AC 9 intercepted-request component test** (patch a server's `request_extras` with a test extra, stub `_get_client`, assert the extra is in the outbound body and the shipped `openrouter` body carries no `provider.zdr`). The engineer build does not touch `tests/`.
- **AC 1 / 2 / 15:** these are epic-level greps that pass only after #4. This ticket keeps `llm_compat.py`, `llm_external.py`, and the new `cost_calculator.py` functions free of vendor names. #4 deletes the remaining `cost_calculator.py` legacy names (AST-1883).

## Pre-commit gate (every stage)

`python3 -m py_compile` on every `.py` file changed in the stage (build-child §7 — the repo's compile/lint step; no linter is configured), then `python3 -c "import src.utils.config, src.utils.cost_calculator"` (plus `, src.external.llm_compat` from Stage 4) from the worktree root. Both must pass before each `code()` commit.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

Revision 1 — 2026-09-29
Driven by: gate AST-1883 Done — Susan approved both `[scope-gate]` moves; Scope amended on AST-1877 / AST-1878 / AST-1880 / AST-1851.
Changes: Scope gate section now records the approved moves (repo-admin agent column → #2; DeepSeek-named cost wrapper deletion → #4) instead of an open stop. `config.py` line anchors updated for the `origin/dev` sync (+14 lines after 2406: LLM_PROVIDER_CONFIG close 5079, timesheet block 4886–4889, DEEPSEEK_CONCURRENCY 5101–5106; TASK_CONFIG anchors unchanged). Stages are otherwise unchanged.

## Joan validate

[plan-rubric]
**Ticket:** AST-1877
**Overall:** APPROVED
**Corpus:** `e1f2699fad`
**Publish ref:** `e9662278f`

## Canon scores

Model → server catalog routing | A | | catalogs + resolvers + compat client match parent Architectural definition
stat.logging.debug | A | | Stage 4: ungated call/response debug; no debug= param
stat.logging.error | A | | Stage 4: log_llm_batch_summary WARNING; caller owns entity ERROR

## Traceability

9→S4 (`request_extras` in `extra_body`; shipped OpenRouter `{}`) | parent 2-partial→S3–4 + Acceptance mapping (vendor-free outside config.py) | 14→S2 (three flips + assert all `requires_candidate_key`) | 10-partial→S1 (`ALLOWED_TIMESHEET_PROVIDERS` from server ids) | parent 1,3–8,11–13,15–16→N/A (sibling #2–#4 or epic grep after #4)

## Findings

### discuss

- **Severity:** discuss
- **Location:** Ticket `## Scope` vs plan Stage 2 §7
- **Finding:** Linear Scope still says `env.example — per-server env vars` while the plan correctly adds none and rewords the Anthropic fallback comment only (parent: no platform keys from env).
- **Recommendation:** Optional Scope wording cleanup on the ticket; build from the plan.

- **Severity:** discuss
- **Location:** Acceptance mapping (AC 9) vs Files Changed / Pre-commit
- **Finding:** Child AC 9 names an intercepted-request **component test**; the plan implements extras in Stage 4 and describes the test shape but excludes `tests/` (engineer ban). No explicit “Betty / qa-child lands AC 9 component test” line unlike several agent epics.
- **Recommendation:** Add one plan sentence so qa-child manifest cannot miss AC 9 before this child’s UT.

### acceptable

- **Severity:** acceptable
- **Location:** Scope gate / AST-1883
- **Finding:** Repo-admin agent column and DeepSeek-named wrapper deletion moves are recorded; Files Changed matches amended Scope.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** Stage 2 `validate_llm_provider_environment`
- **Finding:** Boot checks catalog consistency only; `send_to_deepseek` env fallback remains until #3/#4 — documented and keeps sub green.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** Canon Scope (not on list)
- **Finding:** `astral.config.config-source-of-truth` plainly governs catalog placement; plan complies; id omitted from frozen list (Archie may amend at Discussion if desired).
- **Recommendation:** Do not score off-list; no plan change required.

context_tokens≈95000

## Review

- **Branch:** `origin/sub/AST-1851/AST-1877-model-server-catalog-compat-client`
- **Build tip:** `2ad269d79` (stages: `874e59e8d` catalogs + resolvers · `125ba5b96` validation / candidate-key tasks / parity · `10546a9de` cost calculator · `2ad269d79` compat client)
- **Build notes:** Stage 4 omits `extract_api_response_text` from the planned import list because it is unused once the `emit_llm_call_debug` blocks are gone; the response debug line logs the full response object. Cost calculator outputs are byte-identical to pre-change for every Claude/DeepSeek SKU (probe under `debug/spikes/ast-1877/`). `src/ui/api/api_admin.py` import could not be smoke-tested locally (`asyncpg` not installed); `database`, `agent`, `bootstrap`, `anthropic`, `deepseek` import cleanly.
- **For qa-child:** AC 9 intercepted-request test (see Acceptance mapping); existing tests that assert `ALLOWED_TIMESHEET_PROVIDERS == ("anthropic","deepseek")`, `validate_llm_provider_environment` requiring `DEEPSEEK_API_KEY`, or `requires_candidate_key: False` on `simple_resume_parse` / `select_job_page` / `contact_estelle_turn` are now stale by design.

## Radia review

[code-rubric]
**Ticket:** AST-1877
**Publish ref:** d2bd76b0d
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

Model → server catalog routing | A | |
stat.logging.debug | A | |
stat.logging.error | A | |

## Column diff vs plan stage

(aligned)

## Frame diff

- [ ] **Boundaries — Linear `## Scope`:** Replace `env.example — per-server env vars` with wording that matches the plan (reword Anthropic fallback comment only; no new platform env vars). Engineer to confirm against shipped `env.example`.

## Findings

### fix-now

(none)

### discuss

- **Severity:** discuss  
- **Location:** Linear issue `## Scope` (env.example line) vs plan Stage 2 §7 and tip `env.example`  
- **Finding:** Linear still says per-server env vars; the diff only rewords the Anthropic comment and does not add platform keys.  
- **Recommendation:** Optional Description cleanup when Chuckles next touches the ticket.  
- **Default:** Leave Linear Scope unchanged; plan + `env.example` on `d2bd76b0d` are authoritative for build and UT.

### advisory

- **Severity:** advisory  
- **Location:** `tests/component/external/test_llm_compat.py`, `tests/component/utils/test_config.py`, `tests/component/utils/test_cost_calculator.py`, `docs/test-bible/**`  
- **Finding:** sibling test carry (qa-child / merge-tests): Betty’s manifest and bible updates ride the sub; not engineer product scope on the original “no tests” plan line.  
- **Recommendation:** None for resolve-child product work.

- **Severity:** advisory  
- **Location:** Canon Scope (off frozen list)  
- **Finding:** `astral.config.config-source-of-truth` plainly governs catalog placement; implementation matches (catalogs in `config.py`, client reads `get_llm_server` / tier from caller). Id omitted from frozen list — Archie may amend at Discussion if desired.  
- **Recommendation:** Do not score off-list; no code change required for this review.

## What's solid

- `LLM_SERVER_CONFIG` / `LLM_MODEL_CONFIG`, resolvers, catalog-only `validate_llm_provider_environment()`, global `requires_candidate_key` assert, derived `ALLOWED_TIMESHEET_PROVIDERS`, and DeepSeek parity asserts match the parent *Model → server catalog routing* definition and the plan stages.
- `send_to_llm_compat` is server-id + SKU driven, no env key, merges `request_extras` into `extra_body`, mirrors `send_to_deepseek` failure/success shape; no vendor strings in `llm_compat.py` / updated `llm_external.py` docstrings.
- `stat.logging.debug`: ungated `logger.debug` call/response around `messages.create`; no `debug=` on the public API.
- `stat.logging.error`: failures use `log_llm_batch_summary` only; no new `logger.error` / `logger.exception` in `llm_compat.py`.
- AC 9 covered on tip: component tests patch `request_extras` and assert shipped OpenRouter body has no `provider.zdr`.

## Recommended actions

- Chuckles: append this artifact, `docs(AST-1877): Radia review — clean`, post slim upshot, move to **Review Posted** → datt **PROCEED** to User Testing (no resolve-child canon fixes).
- Optional downstream: tick Frame diff Boundaries row if Susan wants Linear Scope aligned with plan.

context_tokens≈42000

## Bug: AST-2010 — OpenRouter 429 retry (5× doubling) and batch error on exhausted rate limit

Fix child of orphaned bug AST-2009. Scope = AST-2010 `## Scope` (amended per its `[scope-gate]`: `consult.py` + `roster.py` added; option 1, no module-level registry). The ticket carries no Canon Scope list.

### As-is

An OpenRouter 429 (`rate_limit_error`, upstream shared-pool host) gets exactly one attempt. `PROVIDER_CALL_BUDGET["max_retries"]` is `0` (AST-1189), so the SDK never retries. `LLM_SERVER_CONFIG["openrouter"]["concurrency"]` is `None` (this ticket's Stage 4 deferred limits), so `llm_compat._create` skips its backoff loop. The entity goes to its technical-fail state (`METEORITE_FAILED_TECHNICAL_LIKE` in the AST-2009 log), and the batch keeps calling the same rate-limited pool for every remaining entity. The ledger finishes `COMPLETED`.

### To-be

1. An OpenRouter 429 is retried **5 times with doubling backoff** (6 calls max). Susan: "5 retries with doubling backoff."
2. If the 6th call still 429s, the result is tagged `provider_rate_limit`. The dispatcher **stops the batch** (no further provider calls this run) and the dispatch ledger finishes **`FAILED`**. Susan: "If it ever fails after 5 retries for 429, then error the whole batch to the error state."
3. Entity routing does not change. The entity whose call exhausted takes the same failure route it takes today (no hold). Entities not yet called are skipped, and their claim is released, exactly like the AST-1867 balance-outage short-circuit.
4. No concurrency cap and no backoff ceiling on OpenRouter.

### Repro

Component-level fixture (no DB row needed). Patch the Anthropic client so `messages.create` raises `anthropic.RateLimitError` (status 429) whose `str()` is the AST-2009 body: `Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error', ...}, 'metadata': {'provider_name': 'DekaLLM', 'limit_source': 'upstream_provider_shared_pool', ...}}`. Patch `time.sleep` and `random.uniform` so they record calls. Then:

- `send_to_llm_compat(..., server_id="openrouter", ...)` with no `log_batch_id` set (no probe). **Today:** 1 `create` call, result has no `failure_class`. **After:** 6 calls, 5 sleeps (base × 1, 2, 4, 8, 16 × jitter), result `failure_class == "provider_rate_limit"`.
- Dispatcher: `_run_unified` on a 2-entity `meteorite_like` task (`batch_call_mode=0`, `_warm_then_gather`) with `consult.run_consult_task` stubbed to return `{**summary, "failure_class": "provider_rate_limit"}` for the warm entity. **After:** the gather entity is never sent, `ctx["provider_rate_limit_outage"]` is set, and the ledger's `final_status == "FAILED"`.

### Root cause

Two gaps:

1. **No retry.** `openrouter.concurrency = None`. On top of that, `_create` treats a `concurrency` block as all-or-nothing: it requires `max_concurrent` and `backoff_max_seconds`. So turning on retry alone would force an invented cap and ceiling.
2. **No batch stop.** Nothing classifies a 429 as its own failure class. Even if `llm_compat` tagged it, `consult.py` and `roster.py` only pass `failure_class` upward when `is_provider_balance_refusal(result)` is true, so the tag would be dropped before `dispatcher._run_unified` saw it.

### Proposed change

**`src/utils/config.py`**

- `LLM_SERVER_CONFIG["openrouter"]["concurrency"]` becomes `{"rate_limit_retries": 5, "backoff_base_seconds": 2.0, "exhausted_stops_batch": True}`. There are no `max_concurrent` and no `backoff_max_seconds` keys. The `2.0` follows Decision 1 and `exhausted_stops_batch` follows Decision 2, both resolved.
- Header comment line `concurrency — …` becomes: `None, or 429 retry for this server: rate_limit_retries + backoff_base_seconds (delay doubles per retry); optional max_concurrent (process-wide in-flight cap), backoff_max_seconds (delay ceiling), exhausted_stops_batch (True: a 429 still refused after the retries stops the dispatch batch, ledger FAILED).`
- DeepSeek's block is unchanged. It has no `exhausted_stops_batch` key, so it keeps today's exhausted-429 behavior.
- New dict directly after `PROVIDER_BALANCE_REFUSAL`, with a one-line comment `# PROVIDER_RATE_LIMIT — 429 still refused after the server's retries (AST-2010).`:

  ```python
  PROVIDER_RATE_LIMIT = {
      "failure_class": "provider_rate_limit",
      "http_status_codes": (429,),
      "message_substrings": ("error code: 429", "rate_limit_error"),
  }
  ```

  The substrings are lower-case, matched against `str(...).lower()`. `"error code: 429"` is the Anthropic SDK's `APIStatusError` prefix. It is what lets the host-probe **string** error be classified.

**`src/utils/llm_external.py`**

- Import `PROVIDER_RATE_LIMIT`.
- `classify_provider_rate_limit(exc_or_msg: Any) -> Optional[str]`. Same body shape as `classify_provider_balance_refusal`: status from `status_code` or `response.status_code` in `http_status_codes`, otherwise substring match on `str(exc_or_msg).lower()`. It returns `PROVIDER_RATE_LIMIT["failure_class"]` or `None`, and accepts an exception **or** a string (the probe path hands it a string).
- `is_provider_rate_limit(result) -> bool`: mirror of `is_provider_balance_refusal`.

**`src/external/llm_compat.py`**

- `_create`: `max_concurrent` and `backoff_max_seconds` become optional.
  - Semaphore: only when `concurrency.get("max_concurrent")`. Otherwise use `contextlib.nullcontext()`.
  - Delay: `base * 2 ** attempt`, then `min(…, cap)` only when `backoff_max_seconds` is present, then `* random.uniform(0.5, 1.0)` (existing jitter kept, Decision 1).
  - The retry count, the "raise on last attempt" rule and the WARNING line stay as they are.
  - The docstring says the cap and ceiling apply only when configured.
- Tagging is gated on the server's opt-in. In `send_to_llm_compat`, right after `server = get_llm_server(server_id)` (before the outer `try`, so both `except` blocks see it), add `stops_batch = bool((server["concurrency"] or {}).get("exhausted_stops_batch"))`. Only OpenRouter sets it, so DeepSeek, Kimi and Anthropic results are never tagged.
  - **Both `except Exception` blocks in `send_to_llm_compat`** (inner and outer). After the timeout check, the existing `fc = classify_provider_balance_refusal(e)` becomes `fc = classify_provider_balance_refusal(e) or (stops_batch and classify_provider_rate_limit(e))`. Balance wins on a tie, and timeout already wins over both.
  - **Host probe failure branch** (`if probe_err is not None:`). Add `"failure_class": PROVIDER_RATE_LIMIT["failure_class"]` to the returned dict when `stops_batch and classify_provider_rate_limit(probe_err)`.
  - The probe already goes through `_send` → `_create` with `server["concurrency"]`, so it gets the same 5 retries. No change to `openrouter.py`. Waiters on the same batch key get the same cached `probe_err` string, so they are tagged identically.

**`src/core/consult.py`**

Import `is_provider_rate_limit`. Add a private one-liner:

```python
def _rate_limit_tag(r) -> Dict[str, Any]:
    return {"failure_class": r["failure_class"]} if is_provider_rate_limit(r) else {}
```

Splice `**_rate_limit_tag(<inner result>)` into these returns. Routing, state transitions and counts are unchanged at every site:

1. `render_verdict` final generic failure: `return {**_fail(...), **_rate_limit_tag(result)}`.
2. `run_consult_task`, single-entity grade/LIKE path (`if len(entities) == 1:`): both returns carry `**_rate_limit_tag(rv)`. The success return can't carry a tag, so in practice only the failure return does.
3. `_run_batch_consult`, envelope failure generic return (after `_transition_batch_consult_failures`): `**_rate_limit_tag(result)`. The wrappers (`meteorite_like_batch` → `_consult_scored_dispatch_batch_encoded`, `evaluate_*`, qualify) already preserve extra keys (`dict(result)` / `{**result}`).
4. `run_consult_task`, final batch normalizer (`# Normalize batch result shapes`): `**_rate_limit_tag(r)`.
5. `run_consult_task`, company `prefilter_company` normalizer: `**_rate_limit_tag(r)`.
6. `_run_analysis_upshot_batch` per-row loop: keep `rl = {}`; in the `if not result.get("success"):` branch set `rl = rl or _rate_limit_tag(result)`; add `**rl` to the final summary return.

**`src/core/roster.py`**

Import `is_provider_rate_limit`, plus the same private `_rate_limit_tag` one-liner.

1. `_find_job_page_from_assembled`, generic `select_job_page` failure return (`state="NO_JOBLIST"`, `response_type: "SELECT_FAILED"`): add `**_rate_limit_tag(res)`. `run_select_job_page_dispatch` and `jobs_found_process_job_site` already return it unchanged.
2. `run_company_task`, `JOBS_FOUND` branch: `tag = _rate_limit_tag(result)` right after the call. Splice `**tag` into the branch's three returns (errors / passed / failed).
3. `run_company_task`, `select_job_page` branch: same, into its three returns after the balance check.
4. `_run_batch_company_prefilter`, generic `do_task` failure return (`{"passed": 0, ..., "retried": retried}`): add `**_rate_limit_tag(result)`. `prefilter_company_batch` keeps keys.

**`src/core/dispatcher.py`**

- Import `is_provider_rate_limit`.
- New `_note_provider_rate_limit_outage(ctx, task, result)` beside `_note_provider_balance_outage`.
  - On first hit it sets `ctx["provider_rate_limit_outage"] = {"error": result.get("error") or ""}`. Later hits are no-ops.
  - It logs one WARNING: `"%s | dispatch %s %s\n  LLM provider rate limit: still 429 after retries (%s)\n  The batch is stopping"`.
- `_run_unified`, all three call sites (`_consult_chunk`, the full-batch call, `_one`): after the balance check, `if is_provider_rate_limit(result): _note_provider_rate_limit_outage(ctx, task, result)`. The two short-circuit guards become `if ctx.get("provider_balance_outage") or ctx.get("provider_rate_limit_outage"):`.
- `_run_dispatch_loop`: the post-run outage break also breaks on `ctx.get("provider_rate_limit_outage")`, with a debug line `loop stop: provider rate limit run_count=%s`.
- Run finalize (`_dispatch_one_body`, after `await _tracked()`): if `ctx.get("provider_rate_limit_outage")`, then `final_status = "FAILED"`; elif balance outage, `INTERRUPTED` (unchanged). FAILED takes precedence if both are set. The circuit breaker already runs only on `COMPLETED`.
- The `monitor.provider_balance_outage` alert branch is unchanged. A FAILED run with `total_errors > 0` already gets `monitor.auto_run_error`.

### Decisions (resolved — Chuckles on AST-2010 after fix-board; flagged for Susan at UAT)

1. ✅ **Starting delay and jitter:** `backoff_base_seconds: 2.0`, doubling, with today's `× uniform(0.5, 1.0)` jitter kept. Retry waits are about 1–2, 2–4, 4–8, 8–16 and 16–32s, at most 62s of sleep per call, well inside the 610s `PROVIDER_CALL_BUDGET` wait. Changing it later is a config-only edit.
2. ✅ **Which servers stop the batch:** **OpenRouter only**, through the opt-in `exhausted_stops_batch: True` in its retry block. DeepSeek's exhausted-429 behavior stays exactly as it is today. Kimi and Anthropic have no retry block and don't change.

### Blast radius

- **DeepSeek:** no behavior change. `_create` runs the same way (its block keeps `max_concurrent` and `backoff_max_seconds`), and with no `exhausted_stops_batch` key its exhausted 429 is never tagged and never stops the batch.
- **AST-1959 / AST-1960 probe pin:** the probe now retries on 429. A probe that exhausts is tagged, so every caller in the batch returns a tagged failure and the batch stops. `openrouter.py` is unchanged.
- **AST-1867 balance outage:** separate ctx key, same guards. Balance-only runs still finish `INTERRUPTED`.
- **Known limits (unchanged from the balance precedent):**
  - Calls already in flight in a `gather` finish.
  - The `_run_analysis_upshot_batch` row loop keeps going for its remaining rows. The dispatcher only stops at chunk/entity boundaries.
  - The meteorite ingress runners (`ctx={}`) and company paths without a balance branch (`resolve_*`, `vet_inflow`, `parse_job_list`, gazer fetches) don't forward the tag.
  - The AST-1867 single-entity grade path still drops *balance* `failure_class`. That's a pre-existing gap, out of scope.
- **Tests (Betty):**
  - `tests/component/external/test_llm_compat.py`: any test raising `RateLimitError` on `openrouter` (probe or call) now loops 6× and calls `time.sleep`, so patch sleep. **Known break for qa-fix:** `TestAst1959ProbeHostLock::test_ac4_failed_probe_fails_the_batch_with_no_fallback` raises 429 on openrouter and asserts `len(c.calls) == 1`. After the fix it makes **6** calls, and `time.sleep` must be patched or it sleeps for real. Its result should also now carry `failure_class == "provider_rate_limit"`.
  - DeepSeek 429 tests: the retry loop is unchanged and the exhausted result stays untagged. A new negative test is worth adding: a DeepSeek exhausted 429 has no `failure_class` and does not set `ctx["provider_rate_limit_outage"]`.
  - `test_dispatcher.py`: outage / final_status tests.
  - `test_config.py`: `LLM_SERVER_CONFIG` shape.
  - New: llm_external classifier/predicate, consult/roster forwarding.

### What must still hold

- AST-1877 AC: no vendor/server names in `llm_compat.py`; behavior comes from `LLM_SERVER_CONFIG` only.
- `_create` holds the slot only during the call, never during the sleep, for capped servers.
- `PROVIDER_CALL_BUDGET["max_retries"]` stays `0`. All retrying is ours.
- The timeout class still wins over balance, and balance over rate limit.
- AST-1867: balance refusal still holds entity state, stops the batch and finishes `INTERRUPTED`.
- AST-1189 / AST-1842 select_job_page hold-on-timeout is unchanged.
- Kimi / Anthropic: a 429 behaves exactly as today.
- DeepSeek: retry loop and exhausted-429 outcome are exactly as today (no tag, no batch stop).
- No concurrency cap or backoff ceiling is added for OpenRouter.

### Joan fix-board (AST-2010)

```
[board-joan]  CANON: OK
```

```text
AST-2010 board-joan done — CANON: OK.
```

**Reasoning:** Read the `## Bug: AST-2010` plan-fix block on `origin/sub/AST-2009/AST-2010-openrouter-429-retry`. No frozen Canon Scope on the child. `docs/canon-index.md` is not on this ref; overlap skim used `canon/docs/DIRECTIVES-DIRECTORY.md` and active directives touching `config.py`, `llm_compat` / provider config, dispatcher logging, and batch processing.

The change adds `PROVIDER_RATE_LIMIT` and OpenRouter retry knobs in `config.py`, classifiers beside existing `PROVIDER_BALANCE_REFUSAL`, config-driven `_create` retry (optional cap/ceiling), and dispatcher/consult/roster forwarding modeled on the AST-1867 balance-outage precedent. That fits **config as source of truth** (`astral.config.config-source-of-truth` / registry-not-literals): new behavior literals live in `config.py`, not scattered magic.

Nothing **in force** requires today’s behavior (OpenRouter single attempt, mandatory `max_concurrent` + `backoff_max_seconds` when concurrency is set, or balance-only batch short-circuit). `patt.task.dispatch-retry` is entity `_RETRY` routing, not HTTP 429 backoff. `stat.logging.error` / `stat.logging.info.dispatcher` allow a configured fail path with provider lines at WARNING and terminal batch outcomes (`FAILED` for exhausted 429 vs `INTERRUPTED` for balance) without amending those statutes. AST-1877’s “no vendor/server names in `llm_compat`” is plan acceptance criteria the patch explicitly preserves.

Decision 2 (DeepSeek exhausted 429 also stops the batch) is a bounded product choice in the plan’s review section, not a conflict with an active directive and not an Archie-only canon rewrite — same mechanism as balance outage, documented blast radius.

No F3 `validate-plan` fix mode for canon unless product later chooses to codify provider-outage semantics; this triage pass does not require it.

context_tokens≈42000

### Radia review-fix (AST-2010)

## Canon scores

(no frozen Canon Scope list in AST-2010 description — zero ids to score; fix-board `[board-joan] CANON: OK` was qualitative overlap only, not per-directive grades)

## Column diff vs plan stage

no plan-stage scores attached (no `validate-plan` fix-mode column; Joan fix-board only)

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] OK** — qa-fix landed on this branch (`32053a727` → product at tip). Repro nodes pin concrete To-be behavior, not tautologies:
- `test_llm_compat.py::TestAst2010OpenRouterRateLimit::test_retry_only_block_doubles_with_no_cap_or_ceiling` — 6 `_create` attempts, sleeps `[2,4,8,16,32]`, no `_slots` (pre-fix `KeyError: 'max_concurrent'`).
- `::test_openrouter_exhausted_429_is_tagged` — 6 SDK calls, 5 sleeps, `failure_class == "provider_rate_limit"`.
- `test_dispatcher.py::TestAst2010ProviderRateLimitOutage::test_bug_repro_rate_limit_stops_batch_ledger_failed` — 2-entity `meteorite_like` / warm-then-gather: `consult.await_count == 1`, ledger `FAILED`, `1/…/1` errors (pre-fix `6` consult calls, `COMPLETED`).
- `test_consult.py::TestAst2010RateLimitForwarding::test_run_consult_task_single_entity_forwards_tag` — AST-2009 meteorite_like path forwards tag (pre-fix drop).
- `TestAst1959ProbeHostLock::test_ac4_failed_probe_fails_the_batch_with_no_fallback` revised: 6 probe attempts, sleep patched, all four callers tagged.

**## What must still hold — OK** (traced on diff `origin/ftr/AST-2009-openrouter-429-retry...origin/sub/AST-2009/AST-2010-openrouter-429-retry`):
| Item | Verdict |
|------|---------|
| AST-1877 AC: no vendor/server names in `llm_compat.py`; behavior from `LLM_SERVER_CONFIG` | OK — OpenRouter retry/tagging via `concurrency` + `exhausted_stops_batch`; literals in `config.py` / `PROVIDER_RATE_LIMIT`. |
| `_create` holds slot only during call, not during sleep (capped servers) | OK — `time.sleep` remains outside `with sem:`; DeepSeek block unchanged in config test. |
| `PROVIDER_CALL_BUDGET["max_retries"]` stays `0` | OK — not touched (`5446` still `0`). |
| Timeout > balance > rate limit | OK — both except paths check `classify_provider_call_timeout` before balance/rate-limit merge. |
| AST-1867 balance: hold, batch stop, `INTERRUPTED` | OK — balance paths untouched; `TestAst1867ProviderBalanceOutage` kept in manifest; rate limit uses separate ctx key. |
| AST-1189 / AST-1842 select_job_page hold-on-timeout | OK — no timeout/hold logic changed; rate-limit tags ride generic failure returns without `state_held`. |
| Kimi / Anthropic 429 unchanged | OK — Kimi `concurrency` still absent (`test_exhausted_429_untagged_without_opt_in` → 1 call). |
| DeepSeek retry + exhausted 429 untagged, no batch stop | OK — config assertion unchanged; llm_compat + dispatcher untagged guard tests. |
| No OpenRouter cap or backoff ceiling | OK — retry-only block; last sleep 32s proves no ceiling. |

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**
- Ticket carries **no frozen canon list** — canon rubric is empty by design on this fix child; if Archie wants bug fixes scored like feature children, amend Canon Scope on the ticket (not blocking this diff).
- Issue doc Joan fix-board prose still says “Decision 2 (DeepSeek exhausted 429 also stops the batch)” in one sentence; **resolved decisions** in the same block say **OpenRouter only** — doc typo only, matches code.
- UAT flags from plan: `backoff_base_seconds: 2.0` and OpenRouter-only batch stop (Susan can flip in config).

## What's solid

- Plan-fix patch implemented end-to-end: config registry, optional cap/ceiling `_create`, opt-in tagging (call + probe string), consult/roster `_rate_limit_tag` at every planned site, dispatcher mirror of AST-1867 with `FAILED` precedence.
- Betty manifest breadth matches blast radius (classifier, forwarding, dispatcher three call sites, AST-1959 AC4 revision, AST-1867/897 regressions).

## Chuckles — post-review branching

| Gate | Parent shape |
|------|----------------|
| **PROCEED** (C7 complete) | **Normal** (AST-2009 live, `origin/ftr/AST-2009-openrouter-429-retry` base) → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |

context_tokens≈55000
```

```
[code-rubric] PROCEED (Commit: d2d8bd3b2) OpenRouter 429 batch stop
```

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/5a94aa7a2e8adb362a74dc722922906a/2a285525-22da-4411-898b-3be6363b2983/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/8ef746de-2715-4978-86a8-7c3d8b8302c3/store.db` |
| Radia | review | `/home/susan/.cursor/chats/5a94aa7a2e8adb362a74dc722922906a/6fcdfd82-1f6d-46ab-a5b0-7b94d18b776e/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2009 (parent) | ftr/AST-2009-openrouter-429-retry |
| AST-2010 | sub/AST-2009/AST-2010-openrouter-429-retry |

**Epic worktree:** `astral-AST-2009/` — one active sub checked out at a time.
