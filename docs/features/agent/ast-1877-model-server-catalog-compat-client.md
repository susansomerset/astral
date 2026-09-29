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
