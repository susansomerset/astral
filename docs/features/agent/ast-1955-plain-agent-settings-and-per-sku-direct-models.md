<!-- linear-archive: AST-1955 archived 2026-10-08 -->

## Linear archive (AST-1955)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1955/plain-agent-settings-and-per-sku-direct-models-refactor-agent-settings  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1953 — Refactor agent settings and ingest per-endpoint model options  
**Blocked by / blocks / related:** parent: AST-1953; blocks: AST-1958; blocks: AST-1957; blocks: AST-1956

### Description

## What this implements

Adds the settings columns to the agent row and stops requiring `brain_setting` and `mode`. Splits direct models into one id per SKU. Removes the mode table, the host pin and the per-size layer from config, and adds the settings resolver. Does **not** touch the call path (#2), the admin routes and UI (#3), or live rows (#4).

## Citations

`stat.logging.debug`.

## Scope

* `src/utils/config.py` (**modified**):
  * **Modified direct models:** `claude` and `deepseek-v4` become one model entry per SKU, each with its SKU, pricing row (unchanged), default output budget and floor. `kimi-k2.6` stays one entry with its Little default. The `brain_sizes` layer, `can_think` and `thinking_params` leave every model.
  * **Modified OpenRouter table and builder:** each of the 95 slugs keeps its price and max output. The host-slug, quantization and reasoning columns go, because nothing reads them once the pin and mode are gone. The listing default is min(16,000, max output).
  * **New settings resolver:** model id + agent settings → server, SKU, pricing, default output budget, the provider object (OpenRouter only, empty keys omitted), and the temperature/effort to send. It replaces `resolve_model_brain`.
  * **Modified repo-JSON column list for** `agent`**:** the settings in, `brain_setting` and `mode` out.
  * **Removed:** `AGENT_MODE_CONFIG`, the mode constants, `AGENT_MODES`, `validate_agent_mode`, `OPENROUTER_QUANT_BRAIN_SIZE`, `OPENROUTER_THINKING_PARAMS`, `_openrouter_pin`, `resolve_model_brain`, `model_brain_sizes`, `validate_brain_setting_for_model`, and the `brain_settings` / tier-map helpers left with no caller.
* `src/data/database.py` (**modified**):
  * **Modified agent schema-ensure:** adds the setting columns. It does **not** drop `brain_setting` / `mode`, because the migration needs to read them first (DDL only, per AST-1497).
  * **Modified agent writes:** save, update allow-list, repo-JSON apply and repo-JSON validation write the settings (type checks only) and no longer read, require or validate `brain_setting` / `mode`.
  * **Modified public view:** returns the settings and not `brain_setting` / `mode`.
* `data/admin/agent.json`, `docs/uat-fixtures/AST-756/expected-agent.json` (**modified**):
  * every row gains the settings, using the Functional scope 8 starting values (computed by hand for the 7 seed rows);
  * direct rows get per-SKU model ids;
  * every row loses `brain_setting` and `mode`.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/utils/test_config.py`
  * `tests/component/data/database/test_agents.py`
  * `tests/component/core/test_repo_admin_json.py`
  * `docs/test-bible/utils/config.md`
  * `docs/test-bible/data/database/agents.md`

## Acceptance criteria

"Stubbed client" means the component-test stubs of the Anthropic SDK client used by `test_llm_compat.py`, `test_anthropic.py` and `test_agent.py`.

5. **Proxies gone from code.**
   * **Check:** `rg -n "_openrouter_pin|AGENT_MODE|OPENROUTER_QUANT_BRAIN_SIZE|resolve_model_brain|validate_agent_mode|brain_setting|brain_sizes|can_think" src/` returns nothing.
   * **Fails if:** any hit.
6. **Direct models per SKU.**
   * **Check:** `claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-6`, `deepseek-v4-flash`, `deepseek-v4-pro` and `kimi-k2.6` are model ids, and `claude` / `deepseek-v4` are not.
   * **Check (stubbed client):** an agent on `deepseek-v4-pro` with `max_tokens: 384000` sends `max_tokens == 384000`.
   * **Fails if:** an old id remains, a SKU is missing, or the budget differs.
7. **Default output budget.**
   * **Check:** with `max_tokens` empty:
     * `gryphe/mythomax-l2-13b` resolves to 3686 (its max output);
     * `qwen/qwen3.5-27b` resolves to 16000;
     * `claude-sonnet-4-6` resolves to its existing SKU default.
   * **Fails if:** any differs.
8. **Seed carries the settings.**
   * **Check:** every row in `data/admin/agent.json` has the seven settings keys and no `brain_setting` or `mode`, and direct rows use per-SKU ids. The AST-756 fixture matches field-for-field, and reverting the agent table from the seed succeeds.
   * **Fails if:** a key is missing or retired, the fixture drifts, or revert fails.

## Boundaries

Does not touch [agent.py](<http://agent.py>) / llm_compat.py / [anthropic.py](<http://anthropic.py>) (#2), api_admin.py / AdminAgentPrompts.tsx (#3), or the live-row migration (#4). AC 5's `rg` over `src/` closes only once #2 and #3 land on ftr.

## Notes for planning

Parent AST-1953 Description is the authority (Functional scope, Technical scope, Susan's 2026-10-03 answers). Code it loosely — no vocabulary lists, no pre-send gating (Susan).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1953-agent-settings`, child `sub/AST-1953/AST-1955-plain-agent-settings`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-03T23:04:10.141Z
[code-rubric] PROCEED (Commit: c2410f0c) Catalog settings land clean

#### betty — 2026-10-03T23:00:19.808Z
`origin/sub/AST-1953/AST-1955-plain-agent-settings` @ `c2410f0cb` · manifest in config.md bible

#### katherine — 2026-10-03T22:47:11.874Z
`origin/sub/AST-1953/AST-1955-plain-agent-settings` @ `7b1ba21b2`

#### joan — 2026-10-03T22:44:20.095Z
[plan-rubric] PROCEED (Commit: e4253c590) Plan traceability complete

#### katherine — 2026-10-03T22:43:31.644Z
[plan-discuss] round=1 reply

`origin/sub/AST-1953/AST-1955-plain-agent-settings` @ `e4253c590`

- **fix-now (AC 6 stubbed client):** new **AC boundaries** table after Scope gate. The `deepseek-v4-pro` / `max_tokens: 384000` wire check is N/A on this sub and closes with AST-1956's call path (`test_llm_compat.py` / `test_agent.py`). This sub's part: the catalog gives `deepseek-v4-pro` no floor and a 16000 default, so nothing changes the agent's own `max_tokens` (assertable in `test_config.py` here). The table also maps AC 5, 7 and 8.
- **discuss (AC 8 field-for-field):** Stage 3 step 2 now spells it out: same seven settings fields and same Functional scope 8 value rule, no `brain_setting` / `mode`; not row parity with the seed (fixture stays 6 rows, `model_code`, stale content, per the AST-1947 precedent). The exact step change is noted if Susan wants a seed copy instead.

No stage steps, files or estimate changed. Revision 1 is logged under `## Revisions`.

#### joan — 2026-10-03T22:42:49.443Z
[plan-discuss] round=1 concern
[plan-rubric] REVIEW (Commit: 3593697ee) AC6 stub untraced

#### joan — 2026-10-03T22:42:31.833Z
[plan-rubric] REVIEW (Commit: 3593697ee) AC6 stub untraced

#### katherine — 2026-10-03T22:40:58.983Z
`origin/sub/AST-1953/AST-1955-plain-agent-settings` @ `3593697ee` · plan ready, sequencing risk noted

---

# AST-1955 — Plain agent settings and per-SKU direct models

- **Ticket:** [AST-1955](https://linear.app/astralcareermatch/issue/AST-1955) · **Parent:** [AST-1953](https://linear.app/astralcareermatch/issue/AST-1953) Refactor agent settings and ingest per-endpoint model options
- **Publish ref:** `sub/AST-1953/AST-1955-plain-agent-settings` (origin only)
- **Canon Scope:** `stat.logging.debug`

The agent row stops carrying `brain_setting` / `mode` and gains seven plain, optional settings (`quantization`, `temperature`, `reasoning_effort`, `provider_allow_fallbacks`, `provider_only`, `provider_ignore`, `provider_sort`), type-checked only. The model catalog becomes one model id per SKU (`claude` → three ids, `deepseek-v4` → two), the OpenRouter table drops its host/quantization/reasoning pin columns, and a settings resolver replaces `resolve_model_brain`. The mode table, host pin and per-size layer leave `config.py`. The seed and the AST-756 fixture move to the new columns. This ticket does **not** touch `agent.py` / `llm_compat.py` / `anthropic.py` (AST-1956), `api_admin.py` / `AdminAgentPrompts.tsx` (AST-1957), or live rows (AST-1958).

## Scope gate

Every file below is named in this ticket's `## Scope`. Tests and bibles listed there are Betty's (`qa-child`) — no test-tree edits here.

## AC boundaries (checks this sub cannot close alone)

| AC | Check | Closed here by | Closes on ftr after |
|----|-------|----------------|---------------------|
| 5 | `rg … src/` returns nothing | Stage 1 + Stage 2 Done-when `rg` over `config.py` / `database.py` | AST-1956 (`agent.py`, `llm_compat.py`) and AST-1957 (`api_admin.py`, `AdminAgentPrompts.tsx`) — per ticket **Boundaries** |
| 6 | Model ids per SKU; old ids gone | Stage 1 step 8 + Done-when | — (closes here) |
| 6 | **Stubbed client:** agent on `deepseek-v4-pro` with `max_tokens: 384000` sends `max_tokens == 384000` | **N/A on this sub.** The stubbed Anthropic SDK client is driven through `agent.do_task` → `llm_compat`, and AST-1956 rewrites that call path against `resolve_agent_settings`. This sub's part of the check: `resolve_agent_settings("deepseek-v4-pro", …)` returns `tier["max_tokens_floor"] is None` and `tier["default_max_tokens"] == 16000` (Stage 1 step 8), so nothing in the catalog raises or lowers an agent's own `max_tokens`. Betty can assert those two values in `tests/component/utils/test_config.py` on this sub. | AST-1956 — the wire assertion lives with the call-path tests (`test_llm_compat.py` / `test_agent.py`, Betty's manifest for AST-1956 or the ftr rollup) |
| 7 | Default output budget | Stage 1 step 11 expected results | — (closes here) |
| 8 | Seed carries the settings; fixture field-for-field; revert succeeds | Stage 3 | Revert-from-seed test collection — see **Sequencing risk** |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Per-SKU direct models; OpenRouter table/builder slimmed; new `resolve_agent_settings`; agent repo-JSON columns; removals; startup catalog check | utils |
| `src/data/database.py` | Agent schema-ensure adds settings columns; save / update / repo-JSON validate / apply / export write settings; public view returns settings | data |
| `data/admin/agent.json` | Seven settings keys per row, per-SKU `model_id`, `brain_setting` / `mode` removed | seed |
| `docs/uat-fixtures/AST-756/expected-agent.json` | Seven settings keys per row, `brain_setting` / `mode` removed | fixture |

**Editor note:** `.cursorignore` has an unanchored `data/` line, which also hides `src/data/`. Editor tools refuse `src/data/database.py` and `data/admin/agent.json`; read and edit those two via the shell (e.g. `rg`/`sed -n` to read, a Python one-off to write). Do **not** edit `.cursorignore` (out of scope).

## Settings contract (used by every stage)

| Key | Python type when set | DB column | Empty means |
|-----|----------------------|-----------|-------------|
| `quantization` | `str` | `TEXT` | `None` / `""` |
| `temperature` | `int` or `float` (not `bool`) | `REAL` | `None` (0.0 is a value) |
| `reasoning_effort` | `str` | `TEXT` | `None` / `""` |
| `provider_allow_fallbacks` | `bool` | `INTEGER` (0/1) | `None` |
| `provider_only` | `list[str]` | `TEXT` (JSON array) | `None` / `[]` |
| `provider_ignore` | `list[str]` | `TEXT` (JSON array) | `None` / `[]` |
| `provider_sort` | `str` | `TEXT` | `None` / `""` |

No vocabulary lists, no per-model checks, no range checks (Susan: "code it loosely").

⚠️ **Decision (list storage):** `provider_only` / `provider_ignore` are stored as JSON-array text in SQLite, and in the repo seed they are `null` or that same JSON-array **string** (e.g. `"[\"crusoe\"]"`), never a JSON array. Reason: `src/core/repo_admin_json.load_repo_admin_json_file` rejects any list value in a seed row (`_reject_nested_json` — "flat JSON scalars only"), and `repo_admin_json.py` is outside this ticket's Scope. The public view (`get_agent` / `list_agents`) decodes them to real lists, so the resolver and the API see `list[str]`. Rejected alternatives: (a) teach the loader to allow lists of scalars — needs `repo_admin_json.py`, not in Scope; (b) comma-separated text — a second ad-hoc format for the same value. All 7 seed rows start with both lists `null`, so the seed shows no encoded strings today.

## Stage 1: Config — per-SKU catalog, slim OpenRouter table, settings resolver, removals

**Done when:** `python3 -c "import src.utils.config as c; c.validate_llm_provider_environment()"` succeeds; `LLM_MODEL_CONFIG` has 101 ids including `claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-6`, `deepseek-v4-flash`, `deepseek-v4-pro`, `kimi-k2.6` and not `claude` / `deepseek-v4`; `rg -n "_openrouter_pin|AGENT_MODE|OPENROUTER_QUANT_BRAIN_SIZE|resolve_model_brain|validate_agent_mode|brain_setting|brain_sizes|can_think" src/utils/config.py` returns nothing.

All edits in `src/utils/config.py`.

1. **Header (lines ~19–23).** Replace the `LLM_MODEL_CONFIG`, `OPENROUTER_MODEL_TABLE` and `AGENT_MODE_CONFIG` lines with:
   ```
     LLM_MODEL_CONFIG  — LLM models (one id per vendor SKU) → server + SKU + output default/floor + pricing (AST-1851, AST-1955)
     OPENROUTER_MODEL_TABLE — OpenRouter catalog rows expanded into LLM_MODEL_CONFIG (price, max output) (AST-1938, AST-1955)
   ```
   (the `AGENT_MODE_CONFIG` header line is deleted).

2. **Repo-JSON columns (`REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]`, ~line 4400).** Set the tuple to exactly:
   `("agent_id", "content", "model_id", "max_tokens", "quantization", "temperature", "reasoning_effort", "provider_allow_fallbacks", "provider_only", "provider_ignore", "provider_sort", "updated_at")`.

3. **Delete the legacy brain-tier block.** Remove:
   - the `LLM_PROVIDER_CONFIG` comment banner and `BRAIN_LITTLE = "Little"` / `BRAIN_MEDIUM = "Medium"` (lines ~4950–4955, just above `CONTACT_ESTELLE_CONFIG` — keep `CONTACT_ESTELLE_CONFIG` and everything after it intact);
   - `BRAIN_BIG`, `BRAIN_SETTINGS` and `LLM_PROVIDER_CONFIG` (lines ~5032–5044, just after the `CONTACT_TASK_CONFIG` asserts);
   - `validate_allowed_brain_setting`, `resolve_brain_setting_to_anthropic_agent_key` (~5527–5544);
   - the `# --- AST-495 helpers` comment and `anthropic_agent_key_for_brain_setting` (~5571–5574).
   None has a caller in `src/` outside this file and `src/data/database.py` (Stage 2 drops that import). `scripts/migrations/remap_openrouter_agents.py` still imports `AGENT_MODE_*` / `BRAIN_BIG`; AST-1958 deletes that script.

4. **`LLM_SERVER_CONFIG` comment (~line 5054).** Change `#   thinking_off_params — body fields sent when the brain size has thinking off` to `#   thinking_off_params — body fields that turn thinking off on this server`. No value changes in `LLM_SERVER_CONFIG`.

5. **`OPENROUTER_MODEL_TABLE` (~5109–5214).**
   - Replace the banner comment's second line and last two lines so it reads: `slug → (cpm_input, cpm_output, cpm_cache_read, host max output tokens)`, and `_build_openrouter_models() turns each row into one LLM_MODEL_CONFIG entry (model id = slug).` Keep the price/snapshot provenance lines.
   - On **every** row, delete tuple elements 4–6 (host slug, quantization, reasoning flag). `"z-ai/glm-4.6": (0.43, 1.75, 0.08, "venice", "fp4", True, 16384),` becomes `"z-ai/glm-4.6": (0.43, 1.75, 0.08, 16384),`. Do it with a one-off regex rewrite, then verify in Python against the pre-edit table (`git show HEAD:src/utils/config.py`): same 95 slugs, same order, and `new[slug] == old[slug][:3] + (old[slug][6],)` for every slug.
   - Immediately after the table, add:
     ```python
     # Output default for an OpenRouter agent that leaves max_tokens empty, capped at the slug's max output (AST-1955).
     OPENROUTER_DEFAULT_MAX_TOKENS = 16000
     ```

6. **Delete** `OPENROUTER_QUANT_BRAIN_SIZE`, `OPENROUTER_THINKING_PARAMS`, `_openrouter_pin`, the whole `AGENT_MODE_CONFIG` banner, `AGENT_MODE_DETERMINISTIC`, `AGENT_MODE_CREATIVE`, `AGENT_MODE_CONFIG`, `AGENT_MODES` and `validate_agent_mode` (~5215–5253).

7. **`LLM_MODEL_CONFIG` banner (~5255–5271).** Replace with:
   ```python
   # ---------------------------------------------------------------------------
   # LLM_MODEL_CONFIG — what an agent row picks (AST-1851). One model id per vendor SKU (AST-1955);
   # dict order = UI order. Adding a model is a config edit only.
   #   label               — picker label
   #   server              — LLM_SERVER_CONFIG id
   #   sku                 — vendor model string sent as `model`
   #   max_tokens_floor    — int | None; output-token floor applied over the agent's max_tokens
   #   default_max_tokens  — used when the agent row leaves max_tokens empty
   #   pricing[<sku>]: model_label, cpm_input, cpm_output, cpm_cache_read, cpm_cache_write,
   #     cache_min_tokens (USD per million tokens; cache_write 0 where the vendor does not bill it)
   # ---------------------------------------------------------------------------
   ```

8. **`LLM_MODEL_CONFIG` body.** Replace the three entries (`kimi-k2.6`, `claude`, `deepseek-v4`) with six, in this order. Pricing rows are moved verbatim (same dicts / same `AGENT_CONFIG` references); no `can_think`, `thinking_params` or `brain_sizes` key anywhere.

   | id | label | server | sku | max_tokens_floor | default_max_tokens | pricing |
   |----|-------|--------|-----|------------------|--------------------|---------|
   | `kimi-k2.6` | `Kimi K2.6` | `kimi` | `kimi-k2.6` | `None` | `16000` | existing `kimi-k2.6` row (keep the Moonshot provenance comment) |
   | `claude-haiku-4-5` | `Claude Haiku 4.5` | `anthropic` | `claude-haiku-4-5` | `None` | `AGENT_CONFIG["claude-haiku-4-5"]["default_max_tokens"]` | `{"claude-haiku-4-5": AGENT_CONFIG["claude-haiku-4-5"]}` |
   | `claude-sonnet-4-6` | `Claude Sonnet 4.6` | `anthropic` | `claude-sonnet-4-6` | `None` | `AGENT_CONFIG["claude-sonnet-4-6"]["default_max_tokens"]` | `{"claude-sonnet-4-6": AGENT_CONFIG["claude-sonnet-4-6"]}` |
   | `claude-opus-4-6` | `Claude Opus 4.6` | `anthropic` | `claude-opus-4-6` | `None` | `AGENT_CONFIG["claude-opus-4-6"]["default_max_tokens"]` | `{"claude-opus-4-6": AGENT_CONFIG["claude-opus-4-6"]}` |
   | `deepseek-v4-flash` | `DeepSeek V4 Flash` | `deepseek` | `deepseek-v4-flash` | `None` | `8192` | existing `deepseek-v4-flash` row (keep the DeepSeek pricing provenance comment once, above flash) |
   | `deepseek-v4-pro` | `DeepSeek V4 Pro` | `deepseek` | `deepseek-v4-pro` | `None` | `16000` | existing `deepseek-v4-pro` row |

   Keep the one-line comment `# AGENT_CONFIG stays the Anthropic pricing source (send_to_anthropic prices by alias key).` above `claude-haiku-4-5`.

   ⚠️ **Decision:** `kimi-k2.6` keeps its Little default (16000), per Scope. `deepseek-v4-pro` has no floor: Functional scope 4 moves the old Big 384k floor to the agent's own `max_tokens` (the seed's Big row gets it in Stage 3; live rows get it in AST-1958).

9. **`_build_openrouter_models`.** Replace the function with:
   ```python
   def _build_openrouter_models() -> None:
       """Append one LLM_MODEL_CONFIG entry per OPENROUTER_MODEL_TABLE row (AST-1938, AST-1955). Model id,
       label, SKU and pricing key are all the slug; the output default is min(16000, the slug's max output)."""
       for slug, (cpm_in, cpm_out, cpm_cache, max_out) in OPENROUTER_MODEL_TABLE.items():
           LLM_MODEL_CONFIG[slug] = {
               "label": slug,
               "server": "openrouter",
               "sku": slug,
               "max_tokens_floor": None,
               "default_max_tokens": min(OPENROUTER_DEFAULT_MAX_TOKENS, max_out),
               "pricing": {
                   slug: {
                       "model_label": slug,
                       "cpm_input": cpm_in,
                       "cpm_output": cpm_out,
                       "cpm_cache_read": cpm_cache,
                       "cpm_cache_write": 0.0,
                       "cache_min_tokens": 0,
                   },
               },
           }
   ```
   No `max_output_tokens` key: nothing outside `resolve_model_brain` read it, and the default is computed here once.

10. **Delete** `model_brain_sizes`, `validate_brain_setting_for_model` and `resolve_model_brain`. Keep `get_llm_server`, `get_llm_model`, `get_sku_pricing` unchanged.

11. **Add the settings resolver** where `resolve_model_brain` was (after `get_sku_pricing`):
    ```python
    def resolve_agent_settings(model_id: str, agent: Dict[str, Any]) -> Dict[str, Any]:
        """model id + the agent row's plain settings → server, SKU, pricing and the tier a call sends (AST-1955).
        Settings pass through as stored; an empty one comes back None and is not sent. Nothing is derived or checked."""
        m = get_llm_model(model_id)
        provider = None
        if m["server"] == "openrouter":
            # Provider routing object from the agent row; empty keys omitted, no host pin.
            provider = {k: v for k, v in (
                ("quantizations", [agent["quantization"]] if agent.get("quantization") else None),
                ("allow_fallbacks", agent.get("provider_allow_fallbacks")),
                ("only", agent.get("provider_only") or None),
                ("ignore", agent.get("provider_ignore") or None),
                ("sort", agent.get("provider_sort") or None),
            ) if v is not None} or None
        tier = {
            "sku": m["sku"],
            "max_tokens_floor": m["max_tokens_floor"],
            "default_max_tokens": m["default_max_tokens"],
            "temperature": agent.get("temperature"),
            "reasoning_effort": agent.get("reasoning_effort") or None,
            "provider": provider,
        }
        return {
            "model_id": model_id,
            "server_id": m["server"],
            "server": get_llm_server(m["server"]),
            "sku": m["sku"],
            "tier": tier,
            "pricing": m["pricing"][m["sku"]],
        }
    ```
    Expected results (for Betty's manifest): `openai/gpt-oss-120b` + `{"quantization": "bf16", "provider_allow_fallbacks": True}` → `tier["provider"] == {"quantizations": ["bf16"], "allow_fallbacks": True}`; adding `provider_only: ["crusoe"]`, `provider_sort: "price"` adds `only` / `sort`; all-empty except fallbacks → `{"allow_fallbacks": True}`; `temperature: 0.0` → `0.0`; `gryphe/mythomax-l2-13b` → `default_max_tokens == 3686`; `qwen/qwen3.5-27b` → `16000`; `claude-sonnet-4-6` → `AGENT_CONFIG["claude-sonnet-4-6"]["default_max_tokens"]` (16000); non-OpenRouter models → `tier["provider"] is None`.

    ⚠️ **Decision (return shape):** same top-level keys as `resolve_model_brain` (`model_id`, `server_id`, `server`, `sku`, `tier`, `pricing`), and `tier` keeps `sku` / `max_tokens_floor` / `default_max_tokens` / `temperature`, so AST-1956's `agent.py` reads the same keys it reads today. `tier` loses `thinking` / `thinking_params` / `request_extras` and gains `reasoning_effort` and `provider`. How those go on the wire (effort field, `none` → thinking disabled, merging `provider` into the body) is AST-1956's.
    ⚠️ **Decision:** `"openrouter"` is compared by id inside `config.py`. That is the one place server names may appear (LLM_SERVER_CONFIG banner rule); no new server flag is added.

12. **`validate_llm_provider_environment`.** Replace the model loop (`for mid, m in LLM_MODEL_CONFIG.items(): …`) with:
    ```python
        for mid, m in LLM_MODEL_CONFIG.items():
            get_llm_server(m["server"])
            if m["sku"] not in m["pricing"]:
                raise ValueError(f"LLM model {mid!r}: SKU {m['sku']!r} has no pricing row")
            # Raises on an unknown or ambiguous SKU for this server (AST-1938).
            get_sku_pricing(m["sku"], m["server"])
    ```
    The server loop above it is unchanged.

13. **Logging.** No logger calls added or changed. `resolve_agent_settings` is a pure catalog lookup. The `_send_to_server` debug line (`stat.logging.debug`) belongs to AST-1956.

14. `python3 -m py_compile src/utils/config.py`, then run the **Done when** checks.

## Stage 2: Database — agent settings columns, writes, public view

**Done when:** `python3 -c "import src.data.database, src.core.repo_admin_json"` succeeds. On a temp SQLite DB, `save_agent("a", "x", model_id="openai/gpt-oss-120b", quantization="bf16", provider_only=["crusoe"])` then `get_agent("a")` returns `quantization == "bf16"`, `provider_only == ["crusoe"]`, `provider_allow_fallbacks is True`, `resolved_model_key == "openai/gpt-oss-120b"`, and no `brain_setting` / `mode` key. `rg -n "brain_setting|validate_agent_mode|BRAIN_SETTINGS|brain_sizes" src/data/database.py` returns nothing.

All edits in `src/data/database.py` (shell-edit — see Editor note). `src/data/` does not log (`stat.logging.debug` Don't list): add no logger calls.

1. **Module docstring, `agent` line (line 14).** Replace with:
   `- agent    — Agent: agent_id TEXT PK, content TEXT, model_id TEXT (LLM_MODEL_CONFIG key), max_tokens INTEGER, plain call settings sent as stored — quantization TEXT, temperature REAL, reasoning_effort TEXT, provider_allow_fallbacks INTEGER (bool), provider_only / provider_ignore TEXT (JSON array of provider slugs), provider_sort TEXT (AST-1955) — updated_at TIMESTAMP.`

2. **Config import list (~lines 72–122).** Remove `validate_brain_setting_for_model`, `validate_agent_mode`, `BRAIN_SETTINGS`. Keep `get_llm_model` and `LLM_MODEL_CONFIG`.

3. **Replace `_coerce_agent_brain_setting`, `_expose_agent_public` and `_validate_agent_model_brain` (~132–158)** with:
   ```python
   # Agent call settings (AST-1955): optional, type-checked only — no vocabulary, no per-model check.
   _AGENT_SETTING_TYPES: Dict[str, tuple] = {
       "quantization": (str,),
       "temperature": (int, float),
       "reasoning_effort": (str,),
       "provider_allow_fallbacks": (bool,),
       "provider_only": (list,),
       "provider_ignore": (list,),
       "provider_sort": (str,),
   }
   AGENT_SETTING_COLUMNS: Tuple[str, ...] = tuple(_AGENT_SETTING_TYPES)
   # List settings live in SQLite (and the repo seed) as JSON-array text.
   _AGENT_LIST_SETTINGS = frozenset({"provider_only", "provider_ignore"})
   _AGENT_PUBLIC_COLUMNS = ("agent_id", "content", "model_id", "max_tokens", *AGENT_SETTING_COLUMNS, "updated_at")


   def _check_agent_setting(name: str, value: Any) -> None:
       """None or the setting's type; list settings hold strings; a bool is not a temperature."""
       ok = value is None or (
           isinstance(value, _AGENT_SETTING_TYPES[name])
           and not (name == "temperature" and isinstance(value, bool))
           and (name not in _AGENT_LIST_SETTINGS or all(isinstance(s, str) for s in value))
       )
       if not ok:
           kinds = "/".join(t.__name__ for t in _AGENT_SETTING_TYPES[name])
           raise ValueError(f"{name} must be {kinds} or null (got {value!r})")


   def _agent_setting_to_db(name: str, value: Any) -> Any:
       return json.dumps(value) if name in _AGENT_LIST_SETTINGS and value is not None else value


   def _agent_setting_from_db(name: str, value: Any) -> Any:
       if value is None:
           return None
       if name in _AGENT_LIST_SETTINGS:
           return json.loads(value)
       return bool(value) if name == "provider_allow_fallbacks" else value


   def _check_agent_model_id(model_id: Any) -> None:
       """model_id stays validated as today: non-empty and a catalog key (raises on unknown)."""
       if model_id is None or not str(model_id).strip():
           raise ValueError("model_id must be non-empty when provided")
       get_llm_model(str(model_id).strip())


   def _expose_agent_public(row_dict: Dict[str, Any]) -> Dict[str, Any]:
       """Settings decoded to API types; resolved_model_key = the model's SKU (None without a catalog model)."""
       out = dict(row_dict)
       for name in AGENT_SETTING_COLUMNS:
           if name in out:
               out[name] = _agent_setting_from_db(name, out[name])
       mid = out.get("model_id")
       # Rows still on a retired model id (before the AST-1958 run-once migration) list with no SKU.
       out["resolved_model_key"] = LLM_MODEL_CONFIG.get(mid, {}).get("sku") if mid else None
       return out
   ```
   ⚠️ **Decision:** `_expose_agent_public` does not raise on a model id missing from the catalog. Between deploy and AST-1958's run, live rows still say `claude` / `deepseek-v4`. Raising here would blank the whole Manage Agents list when Susan most needs to see those rows. Writes still reject unknown ids (`_check_agent_model_id`), and the call path still fails on them, as the parent's Sequencing note expects.
   ⚠️ **Decision:** `model_id` keeps today's existence check. Today it happens indirectly through the brain-size check; `_check_agent_model_id` makes it explicit (Functional scope 1: "`model_id` … stay[s] exactly as [it is] today").

4. **`_validate_agent_repo_json_rows` (~670–690).** Keep the key-set check and the `agent_id` check. Delete the `brain_setting required` block and the `validate_brain_setting_for_model` / `validate_agent_mode` try-block. After the `agent_id` check, add:
   ```python
           try:
               _check_agent_model_id(row.get("model_id"))
               for name in AGENT_SETTING_COLUMNS:
                   value = row[name]
                   # Seed carries list settings as JSON-array text (the loader allows flat scalars only).
                   if name in _AGENT_LIST_SETTINGS and isinstance(value, str):
                       value = json.loads(value)
                   _check_agent_setting(name, value)
           except ValueError as e:
               raise ValueError(f"agent repo JSON row {i}: {e}") from e
   ```
   (`json.JSONDecodeError` subclasses `ValueError`.) The old "model_id required" message becomes "model_id must be non-empty when provided", prefixed with the row number.

5. **`fetch_agent_repo_json_export_rows` (~710).** Keep the SELECT. Return rows with `provider_allow_fallbacks` converted to `bool` when not `None`, so an export writes `true` / `false` and re-loads through step 4:
   ```python
       rows = [_row_to_dict(r) for r in conn.execute(
           f"SELECT {cols_sql} FROM agent ORDER BY agent_id",
       ).fetchall()]
       for row in rows:
           if row["provider_allow_fallbacks"] is not None:
               row["provider_allow_fallbacks"] = bool(row["provider_allow_fallbacks"])
       return rows
   ```
   List settings export as their stored JSON text (a flat scalar, which matches the seed's form).

6. **`apply_agent_repo_json_startup` (~730–765).** Keep the ensure, validate, `ids` and delete-absent logic, the `content` coercion and the `updated_at` default. Replace the per-row column handling and the two SQL statements so they write every repo column except `agent_id`, taken from `_agent_repo_json_columns()`, and nothing else:
   ```python
       cols = [c for c in _agent_repo_json_columns() if c != "agent_id"]
       ...
           vals = {**row, "content": content, "model_id": str(row["model_id"]).strip(), "updated_at": updated}
           params = [vals[c] for c in cols]
           if existing is None:
               conn.execute(
                   f"INSERT INTO agent (agent_id, {', '.join(cols)}) VALUES ({', '.join('?' * (len(cols) + 1))})",
                   (aid, *params),
               )
           else:
               conn.execute(
                   f"UPDATE agent SET {', '.join(f'{c} = ?' for c in cols)} WHERE agent_id = ?",
                   (*params, aid),
               )
   ```
   List settings go in verbatim (already JSON text or `None`); booleans bind as 0/1 through sqlite3. Retired columns still on a live table are left untouched (UPDATE, not INSERT OR REPLACE).

7. **`_ensure_agent_schema` (~5926–5971).**
   - `CREATE TABLE agent`: columns `agent_id TEXT PRIMARY KEY, content TEXT, model_id TEXT, max_tokens INTEGER, quantization TEXT, temperature REAL, reasoning_effort TEXT, provider_allow_fallbacks INTEGER, provider_only TEXT, provider_ignore TEXT, provider_sort TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`.
   - Add-missing-columns list: `("model_id", "TEXT"), ("max_tokens", "INTEGER"), ("quantization", "TEXT"), ("temperature", "REAL"), ("reasoning_effort", "TEXT"), ("provider_allow_fallbacks", "INTEGER"), ("provider_only", "TEXT"), ("provider_ignore", "TEXT"), ("provider_sort", "TEXT")`. The two retired columns are no longer added.
   - Drop loop: change `for col_name in ("temperature", "model_code"):` to `for col_name in ("model_code",):` and its comment to `# AST-1948: model_id is the one model indicator.`
   - Replace the trailing AST-1497 comment with `# AST-1497: DDL-only — no content backfills on ensure; retired columns stay until the AST-1958 run-once migration reads and drops them.`

   ⚠️ **Decision:** `temperature` must leave the AST-1948 drop loop. If it stayed, the next process start would drop the new column. On a DB that still carries a pre-AST-1948 `temperature` column, the old values survive; AST-1958 overwrites every row's temperature. Fresh tables never get the retired columns (no rows to migrate). No SQL `DEFAULT` on `provider_allow_fallbacks` — see step 8.

8. **`save_agent` (~5974–6030).** New signature (drop `mode`, `brain_setting`):
   ```python
   def save_agent(
       agent_id: str,
       content: str,
       *,
       model_id: Optional[str] = None,
       max_tokens: Optional[int] = None,
       quantization: Optional[str] = None,
       temperature: Optional[float] = None,
       reasoning_effort: Optional[str] = None,
       provider_allow_fallbacks: Optional[bool] = None,
       provider_only: Optional[List[str]] = None,
       provider_ignore: Optional[List[str]] = None,
       provider_sort: Optional[str] = None,
   ) -> None:
       """Upsert an agent row (AST-1955). Settings are type-checked only; on an existing row None leaves a column as is.
       New rows default provider_allow_fallbacks to True."""
   ```
   Body:
   - `settings = {"quantization": quantization, "temperature": temperature, "reasoning_effort": reasoning_effort, "provider_allow_fallbacks": provider_allow_fallbacks, "provider_only": provider_only, "provider_ignore": provider_ignore, "provider_sort": provider_sort}`; `_check_agent_setting(n, v)` for each, before opening the connection.
   - `mid = model_id.strip() if model_id is not None else None`; if `mid is not None`: `_check_agent_model_id(mid)` (keeps the "model_id must be non-empty when provided" message).
   - Inside `_with_conn`: `existing = conn.execute("SELECT agent_id FROM agent WHERE agent_id = ?", ...)`.
     - **New row:** `if settings["provider_allow_fallbacks"] is None: settings["provider_allow_fallbacks"] = True`; INSERT `agent_id, content, model_id, max_tokens, <7 settings>, updated_at` with `_agent_setting_to_db` applied to each setting.
     - **Existing row:** `sets = ["content = ?", "updated_at = ?"]`, then append `model_id`, `max_tokens` and each setting **only when not None** (same rule `max_tokens` follows today), values through `_agent_setting_to_db`.
   ⚠️ **Decision:** "default true" for `provider_allow_fallbacks` is applied on new-row insert, not as a SQL `DEFAULT`, because an `ALTER … DEFAULT` would silently fill live rows (AST-1497: no backfill on ensure). The seed sets it explicitly; AST-1958 sets it on live rows.

9. **`get_agent` (~6035).** Change `SELECT *` to `SELECT {', '.join(_AGENT_PUBLIC_COLUMNS)} FROM agent WHERE agent_id = ?`. Retired columns still on a live table never reach the API.

10. **`list_agents` (~6050).** Docstring: `"""Return all agents including model_id / max_tokens / call settings / resolved_model_key."""`. In the SELECT, replace `model_id, brain_setting, mode, max_tokens, updated_at,` with `model_id, max_tokens, quantization, temperature, reasoning_effort, provider_allow_fallbacks, provider_only, provider_ignore, provider_sort, updated_at,`. The rest is unchanged.

11. **`update_agent` (~6070–6110).**
    - `_UPDATE_AGENT_ALLOWED = frozenset({"content", "model_id", "max_tokens", *AGENT_SETTING_COLUMNS})`.
    - Delete the `mode` check. Before building `pairs`: `if "model_id" in cols: _check_agent_model_id(kwargs["model_id"])`, then `_check_agent_setting(c, kwargs[c])` for each `c in cols` that is a setting.
    - `params = [_agent_setting_to_db(c, kwargs[c]) if c in _AGENT_SETTING_TYPES else kwargs[c] for c in cols]`. Passing `None` clears a setting (partial-update semantics unchanged).
    - Delete the `if "model_id" in cols or "brain_setting" in cols:` pre-read block inside `_with_conn`. The UPDATE's `rowcount` already returns 0 for a missing agent.

12. `python3 -m py_compile src/data/database.py`, then run the **Done when** checks.

## Stage 3: Seed and AST-756 fixture

**Done when:** every row in both files has the seven settings keys and no `brain_setting` / `mode`. `python3 -c "from src.core import repo_admin_json as r; from src.data import database as d; d._validate_agent_repo_json_rows(r.load_repo_admin_json_file('agent'))"` passes. On a temp DB, `apply_agent_repo_json_startup` with the seed rows followed by `fetch_agent_repo_json_export_rows` returns rows equal to the seed.

1. **`data/admin/agent.json`** (shell-edit with a Python one-off; keep `content` and `updated_at` byte-identical). For each row: delete `brain_setting` and `mode`; set the values below; write keys in `REPO_ADMIN_JSON_CONFIG` column order (Stage 1 step 2); serialize with `json.dumps(rows, indent=2, ensure_ascii=True) + "\n"` (the file's current format). Every row also gets `quantization: null`, `provider_allow_fallbacks: true`, `provider_only: null`, `provider_ignore: null`, `provider_sort: null`.

   Values follow Functional scope 8, from what each row's call sends today. `deepseek-v4` and `claude` could not think; `kimi-k2.6` could, and on Deterministic it sent thinking-off.

   | agent_id | was (model / size / mode) | `model_id` | `max_tokens` | `temperature` | `reasoning_effort` |
   |----------|---------------------------|------------|--------------|---------------|--------------------|
   | `ats_expert_atlas` | deepseek-v4 / Big / Creative | `deepseek-v4-pro` | `384000` (was 16000; Big floor) | `0.6` | `null` |
   | `college_intern_ruth` | deepseek-v4 / Little / Deterministic | `deepseek-v4-flash` | `8192` | `0.2` | `null` |
   | `contact_recruiter_estelle` | kimi-k2.6 / Little / Deterministic | `kimi-k2.6` | `null` | `0.2` | `"none"` |
   | `content_writer_judith` | kimi-k2.6 / Big / Creative | `kimi-k2.6` | `16000` | `null` | `null` |
   | `job_analyst_grace` | deepseek-v4 / Medium / Deterministic | `deepseek-v4-pro` | `16000` | `0.2` | `null` |
   | `principal_recruiter_estelle` | kimi-k2.6 / Big / Creative | `kimi-k2.6` | `384000` | `null` | `null` |
   | `web_scraper_laslo` | deepseek-v4 / Medium / Deterministic | `deepseek-v4-pro` | `16000` | `0.2` | `null` |

   (Functional scope 8's "kimi Big with empty `max_tokens` → 32000" does not apply: both kimi Big rows already set `max_tokens`.)

2. **`docs/uat-fixtures/AST-756/expected-agent.json`** (6 rows, `model_code`-keyed). For each row: delete `brain_setting` and `mode`; add `quantization: null`, `provider_allow_fallbacks: true`, `provider_only: null`, `provider_ignore: null`, `provider_sort: null`, `reasoning_effort: null`, and `temperature` = `0.2` where `mode` was `Deterministic` (`job_analyst_grace`, `web_scraper_laslo`, `college_intern_ruth`) and `0.6` where it was `Creative` (`ats_expert_atlas`, `content_writer_judith`, `principal_recruiter_estelle`). All its models are Claude SKUs, which could not think. `model_code`, `content`, `max_tokens`, `updated_at` and row order are unchanged. Serialize with `json.dumps(rows, indent=2, ensure_ascii=True, sort_keys=True) + "\n"` (the file's current format).

   ⚠️ **Decision:** the fixture gets the same column add/drop as the seed, and its stale content and `model_code` stay as they are. That's the AST-1947 precedent (`131911492` edited both files' columns only). Its `model_code` values are already per-SKU Claude ids.

   **AC 8 "matches field-for-field" means, in this plan:** every fixture row carries the same seven settings fields as the seed, with values set by the same Functional scope 8 rule, and neither file has `brain_setting` or `mode`. It does **not** mean row parity with the 7-row seed: the fixture stays at 6 rows, keeps its `model_code` key, and keeps its stale `content`, as it has since AST-1947. If Susan wants the fixture rebuilt as a copy of the seed (7 rows, `model_id`, current content), this step changes to "write the seed rows, sorted keys, to the fixture" and needs a revision.

3. Validate both files parse (`python3 -m json.tool` on each), then run the **Done when** checks.

## Sequencing risk (for Betty / Chuckles — not a step)

Removing `resolve_model_brain` breaks the imports in `src/core/agent.py` and `src/ui/api/api_admin.py` until AST-1956 / AST-1957 land on ftr. The parent's Sequencing section accepts this. One test-harness side effect: `tests/component/core/conftest.py` has an autouse fixture that imports `src.core.candidate` → `src.core.agent`. So **every test under `tests/component/core/`, including `test_repo_admin_json.py`, fails at collection on this sub alone.** `tests/component/utils/` and `tests/component/data/` are not affected (their import chain stops at config/database). AC 8's revert-from-seed check therefore needs either a manifest that runs it after AST-1956 is on ftr, or a home outside `tests/component/core/`. That's Betty's call in `qa-child`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-10-03
Driven by: Joan `[plan-discuss] round=1 concern` (`99b70f203`) — fix-now: AC 6 stubbed-client check unmapped; discuss: AC 8 "field-for-field" meaning.
Changes: Added **AC boundaries** after Scope gate. It maps AC 5–8, marks AC 6's stubbed-client `max_tokens` wire check N/A on this sub (closes with AST-1956's call path), and names this sub's catalog-side part of that check (`deepseek-v4-pro`: no floor, default 16000). Stage 3 step 2 now defines "field-for-field" as same settings fields and same value rule, not row parity with the seed, and names the exact change if Susan wants a seed copy instead. No stage steps, files or estimate changed.

## Joan validate

[plan-rubric] PROCEED (Commit: e4253c590) Plan traceability complete

**Ticket:** AST-1955  
**Overall:** APPROVED  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Publish ref:** `sub/AST-1953/AST-1955-plain-agent-settings` @ `e4253c590d8eb099237f68a636a10657235c257f`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |

## Traceability

5 → **AC boundaries** + Stage 1/2 done-when `rg` (full `src/` deferred per table) · 6 → Stage 1 step 8/11 + **AC boundaries** (ids here; stub wire N/A → AST-1956; catalog floor/default in `test_config.py`) · 7 → Stage 1 step 11 expected results · 8 → Stage 3 + **AC boundaries** / **Sequencing risk** for revert collection

## Findings

### acceptable

- **Location:** Plan tail — `## Joan validate` through prior REVISE artifact (after `## Revisions`)
- **Finding:** Round-1 validate stdout was appended into the published plan doc; belongs on the issue doc only and still describes the pre-`e4253c590` traceability gap.
- **Recommendation:** Chuckles strips that block on the next plan publish; no engineer stage change.

- **Location:** Plan structure — no `## Self-assessment`
- **Finding:** Estimate confirm + staged done-when + **Sequencing risk** carry complexity; same as prior pass.
- **Recommendation:** None blocking.

## Plan Discuss

One completed round (`round=1 concern` / `round=1 reply`). Round-1 fix-now (AC 6 stub) and discuss (AC 8 wording) are addressed in **AC boundaries** and Stage 3 step 2.

context_tokens≈52000
[plan-rubric] PROCEED (Commit: e4253c590) Plan traceability complete
```

AST-1955 plan approved.
[AST-1953 | AST-1955] Joan/validate validate-plan - complete a7560af8 model=composer-2.5 - (19s) > OK

## Review

- **Branch:** `sub/AST-1953/AST-1955-plain-agent-settings`
- **Build commits:** `2857d1738` (Stage 1 config) · `8376631f9` (Stage 2 database) · `8708be5fd` (Stage 3 seed + fixture)
- **Build notes:** all three stages executed as written; each stage's Done-when checks were run green on a temp SQLite DB. No deviations. Imports of `src/core/agent.py`, `src/ui/api/api_admin.py` and `scripts/migrations/remap_openrouter_agents.py` break until AST-1956 / AST-1957 / AST-1958 land, as the parent's Sequencing section expects (see **Sequencing risk**).

## Radia review

[code-rubric]

**Ticket:** AST-1955  
**Publish ref:** `c2410f0cbe321b97ec060c9a99345349dea4ade9` (`origin/sub/AST-1953/AST-1955-plain-agent-settings`)  
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51  
**Overall:** CLEAN  

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned) — Joan validate round 2: `stat.logging.debug` A.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `docs/features/agent/ast-1955-plain-agent-settings-and-per-sku-direct-models.md` (plan tail)
- **Finding:** Round-1 Joan validate artifact remains embedded in the published plan after round-2 APPROVED; Joan round 2 already flagged this for Chuckles strip on next plan publish.
- **Recommendation:** Chuckles removes the superseded `## Joan validate — round 1` block when appending this review (doc hygiene only).

- **Location:** `tests/component/core/test_repo_admin_json.py` + bible § AST-1955 sequencing
- **Finding:** `resolve_model_brain` removal still breaks `tests/component/core/` collection until AST-1956 lands on `ftr`; Betty documented stub/local verification. Changes on this sub are API-aligned (`save_agent` / revert / validation), not sibling product scope.
- **Recommendation:** No action on AST-1955 tip; keep revert-from-seed / full core collection on ftr rollup per plan **Sequencing risk**.

- **Location:** Estimate confirm **3**
- **Finding:** Diff is large (config + database + seed + fixture + manifests) but matches the three staged plan surfaces and Betty bible blocks; footprint fits the confirmed estimate.
- **Recommendation:** None.

## What's solid

- Three-dot diff vs `origin/dev` is confined to planned product paths (`src/utils/config.py`, `src/data/database.py`, seed, AST-756 fixture) plus Betty tests/bible; no `agent.py`, `llm_compat.py`, or `api_admin.py` smuggling.
- Stage 1 done-when proxies hold on tip: legacy symbols absent from `config.py`; `resolve_agent_settings` matches plan shape (provider object, tier fields, OpenRouter vs direct).
- Stage 2 done-when proxies hold: brain/mode validation removed from `database.py`; public column list and settings encode/decode follow the plan contract.
- Stage 3: seven seed rows carry all seven settings keys; fixture rows carry settings columns without `brain_setting` / `mode`.
- `stat.logging.debug`: no new `logger.debug` / gated debug / `src/data` debug noise in the diff; pure resolver left logging-free per plan Stage 1 §13 and Stage 2 module rule.

## Recommended actions (downstream — not for Radia)

- Chuckles: append this artifact to the issue doc, `docs(AST-1955): Radia review — clean`, push `origin/sub/AST-1953/AST-1955-plain-agent-settings`, post slim upshot `--as radia`, move **Review Posted** → datt **PROCEED** path to **User Testing** (no fix-now canon items).
- Optional doc hygiene: strip superseded Joan round-1 block from the plan file when writing the review commit.

context_tokens≈48000
