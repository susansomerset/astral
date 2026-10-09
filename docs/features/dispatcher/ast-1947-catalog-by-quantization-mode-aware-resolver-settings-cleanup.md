<!-- linear-archive: AST-1947 archived 2026-10-08 -->

## Linear archive (AST-1947)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1947/catalog-by-quantization-mode-aware-resolver-settings-cleanup-support  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 5  
**Parent:** AST-1946 — Support "Big" brain OpenRouter models  
**Blocked by / blocks / related:** parent: AST-1946; blocks: AST-1950; blocks: AST-1948

### Description

## What this implements

Replaces the OpenRouter catalog with the brief's 95 slugs, each with one quantization brain size, host pin and brief price, and retires `kimi-k2.6-openrouter` into the table. Adds the Deterministic / Creative mode and a resolver that turns model + size + mode into the tier a call uses. Strips the old per-size thinking/temperature fields, the Anthropic default temperatures and the dead legacy helpers. Updates the agent repo-JSON columns (`mode` in, `temperature` out) and the seed and fixture files. Does **not** touch the database, call paths, admin routes or UI (#2, #3) or the migration (#4). Katherine built AST-1938's table and builder.

## Citations

`stat.logging.debug` (mode-derived thinking/temperature and the pin stay visible in the compat client's existing ungated debug body logging; no `debug=` parameter).

## Scope

* `src/utils/config.py` (**modified**):
  * **New quantization-to-size map:** a small constant: int4/fp4 → Little, int8/fp8 → Medium, fp16/bf16 → Big.
  * **Modified OpenRouter table:** replaced by the brief's 95 rows. Each row holds IN / OUT / CACHE from the brief, the host routing slug, the host quantization, the reasoning flag and the host max output. The last three come from `GET https://openrouter.ai/api/v1/models/<slug>/endpoints`, matched on the brief's PROVIDER **and** QUANT (AST-1938's snapshot method). The 12 removed slugs leave the table. The row layout and field names are `plan-child`'s call.
  * **Modified builder:** each row becomes one model with one brain size, the row's quantization size. It records whether the host can think, its max output, and `request_extras` pinning `provider.order = [host]`, `allow_fallbacks = false` and `quantizations = [row quantization]`. The uniform quantization pin replaces the one-off `gemma-4-31b-it` constant (DeepInfra hosts that slug at two quantizations).
  * **New mode constants:** Deterministic = thinking off, temperature 0.2, OpenRouter output cap 16k. Creative = thinking on when the model can think, otherwise temperature 0.6, OpenRouter output cap 32k.
  * **Modified catalog shape:** brain-size tiers no longer carry `thinking`, `thinking_params` or `default_temperature`. Each model carries one "can think" flag plus its thinking payload: OpenRouter per host (adaptive), `kimi-k2.6` yes (`enabled`), `claude` and `deepseek-v4` no. SKUs, pricing, `default_max_tokens` and `max_tokens_floor` on direct models are unchanged.
  * **Modified resolver:** the model + brain-size resolver also takes the agent's mode and returns the tier a call uses. That tier's thinking flag and temperature come from the mode. It carries the thinking flag and payload under the keys `llm_compat` already reads, which is why `llm_compat.py` needs no change. On OpenRouter its output default comes from the mode cap (capped at host max); on direct models it is the size's existing default. Validation helpers reject an unknown mode.
  * **Modified repo-JSON config:** the agent table's column list gains `mode` and drops `temperature`.
  * **Removed:** the `kimi-k2.6-openrouter` entry (`moonshotai/kimi-k2.6` is built from its brief row), the `default_temperature` keys in `AGENT_CONFIG`, and the dead helpers `brain_setting_for_anthropic_agent_key` and `admin_brain_setting_catalog` (no callers; their route no longer exists). Also `infer_brain_setting_from_legacy_model_code`, whose only caller is the legacy fallback removed from `database.py`.
* `data/admin/agent.json`, `docs/uat-fixtures/AST-756/expected-agent.json` (**modified**): each agent row gains `mode` (per Functional scope item 8) and loses `temperature`. No other field changes.
* `tests/component/utils/test_config.py`, `tests/component/external/test_llm_compat.py`, `docs/test-bible/utils/config.md`, `docs/test-bible/external/llm_compat.md` (**modified**, Betty in `qa-child`).

## Acceptance criteria

All `python -c` checks run from the repo root on the shipped tree. "The brief" means the 95 rows in this ticket's Original brief. `SIZE = {"int4": "Little", "fp4": "Little", "int8": "Medium", "fp8": "Medium", "fp16": "Big", "bf16": "Big"}`.

1. **OpenRouter catalog = the brief.**
   * **Check:** `{k for k, m in LLM_MODEL_CONFIG.items() if m["server"] == "openrouter"}` equals the brief's 95 slugs. The script prints both set differences.
   * **Fails if:** either difference is non-empty.
2. **One size per OpenRouter model, from the quantization.**
   * **Check:** for each brief slug, `model_brain_sizes(slug) == (SIZE[QUANT],)`. Spot checks: `gryphe/mythomax-l2-13b` → `('Big',)`, `qwen/qwen3-32b` → `('Medium',)`, `moonshotai/kimi-k2.6` → `('Little',)`.
   * **Fails if:** any other tuple appears.
3. **Pricing = the brief.**
   * **Check:** for each brief slug, `get_sku_pricing(slug, "openrouter")` has `cpm_input` / `cpm_output` / `cpm_cache_read` equal to IN / OUT / CACHE, with `cpm_cache_write == 0`.
   * **Fails if:** any mismatch prints, or any lookup raises.
4. **Host and quantization pin.**
   * **Check:** every brief slug's tier has `request_extras == {"provider": {"order": [<host routing slug>], "allow_fallbacks": False, "quantizations": [QUANT]}}`. Spot checks: `undi95/remm-slerp-l2-13b` → `mancer` / `fp8`, `google/gemma-4-31b-it` → `deepinfra` / `fp4`.
   * **Fails if:** any pin is missing, wrong, or allows fallbacks.
5. **Output default by mode on OpenRouter.**
   * **Check:** the resolved OpenRouter tier's `default_max_tokens == min(16000 Deterministic | 32000 Creative, host max output)`. Spot checks: `gryphe/mythomax-l2-13b` Creative → 3686, `qwen/qwen3.5-27b` Creative → 32000, `qwen/qwen3.5-27b` Deterministic → 16000.
   * **Fails if:** any violator prints.
6. **Direct models persist; no stray thinking/temperature settings.**
   * **Check:**
     * For `claude`, `kimi-k2.6` and `deepseek-v4`, model ids, brain-size tuples, tier SKUs, `default_max_tokens`, `max_tokens_floor` and pricing rows equal pre-epic `origin/dev` values.
     * No stored tier in `LLM_MODEL_CONFIG` has a `thinking`, `thinking_params` or `default_temperature` key. These appear only on the tier the resolver returns for a call.
     * `rg -n "default_temperature|brain_setting_for_anthropic_agent_key|admin_brain_setting_catalog|infer_brain_setting_from_legacy_model_code" src/` returns nothing.
     * `rg -n "temperature" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing.
   * **Fails if:** any direct value differs, a stored tier keeps one of those keys, or any hit.
7. **Starting modes in the seed.**
   * **Check:** in `data/admin/agent.json`, exactly `ats_expert_atlas`, `content_writer_judith` and `principal_recruiter_estelle` are `Creative` and the other four are `Deterministic`. No row has `temperature`. `docs/uat-fixtures/AST-756/expected-agent.json` matches field-for-field.
   * **Fails if:** any row differs or the fixture drifts.
8. `kimi-k2.6-openrouter` **retired; catalog boots.**
   * **Check:**
     * `"kimi-k2.6-openrouter" not in LLM_MODEL_CONFIG` and `rg -n "kimi-k2.6-openrouter" src/` returns nothing.
     * `validate_llm_provider_environment()` returns without raising.
     * `GET /api/admin/agents/models` returns **98** ids.
   * **Fails if:** any hit, `v()` raises, or the count isn't 98.
9. **No slug or mode literal outside config.**
   * **Check:**
     * `rg -n "apodex/|bytedance/ui-tars|ibm-granite/|inclusionai/|meta/muse|microsoft/|minimax/|sao10k/l3|thedrummer/|z-ai/glm-4|moonshotai/kimi-k2\.[57]" src/ --glob '!src/utils/config.py'` returns nothing.
     * `rg -n "0\.6\b|0\.2\b" src/core/agent.py src/ui/api/api_admin.py src/data/database.py` returns no mode temperature literal.
   * **Fails if:** any hit.

## Boundaries

Does **not** touch the database, call paths, admin routes or UI (#2, #3) or the migration (#4). Sibling slices: #1 catalog/resolver/config, #2 database/agent/api_admin, #3 Manage Agents UI, #4 remap migration. Blocked by: none.

## Notes for planning

AC 7 and AC 12 are shared with #2 (and AC 7 with #3); this child owns their config/catalog halves. Removing `infer_brain_setting_from_legacy_model_code` and the agent repo-JSON `temperature` column touches names `database.py` still uses until #2 lands — plan how this sub stays importable and green on its own. Parent AST-1946 Description (Functional scope, Technical scope, Original brief with all 95 rows) is authoritative.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1946-big-brain-openrouter`, child `sub/AST-1946/AST-1947-catalog-quant-mode`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-03T02:47:10.640Z
[code-rubric] PROCEED (Commit: 0d5db0f6f) Catalog + mode resolver clean

#### betty — 2026-10-03T02:43:31.859Z
`origin/sub/AST-1946/AST-1947-catalog-quant-mode` @ `0d5db0f6f` · catalog + mode tests ready

#### joan — 2026-10-03T02:33:19.364Z
[plan-rubric] PROCEED (Commit: 52411898) Option A pair landing

#### chuckles — 2026-10-03T02:30:37.757Z
Sequencing gap resolved: Susan picked **A** in [AST-1951](https://linear.app/astralcareermatch/issue/AST-1951). AST-1947 and AST-1948 land as a pair; no Scope change. QA manifest stays on `test_config.py` / `test_llm_compat.py`. The AC 8 endpoint count (98 ids) is checked on `ftr/AST-1946-big-brain-openrouter` after AST-1948 merges. ftr won't boot between the two merges; that's accepted. Plan goes to Plan Ready as written.

#### katherine — 2026-10-03T01:55:36.379Z
[scope-gate] `origin/sub/AST-1946/AST-1947-catalog-quant-mode` @ `52411898b` · plan written, sequencing blocked

@susan Notes for planning asks: *"plan how this sub stays importable and green on its own."* With Scope as written, it can't. Every repair is in #2's files:

- **Import fails:** `src/data/database.py:103` imports `infer_brain_setting_from_legacy_model_code`. Scope § Removed deletes it, so `src.data.database` (and the app) won't import until #2 lands.
- **Runtime TypeError:** `resolve_model_brain(model_id, brain_setting)` is called with two args at `agent.py:1831`, `api_admin.py:389`, `api_admin.py:1542` and `database.py:146` (agent public view). Scope § Modified resolver adds the `mode` argument.
- **Runtime KeyError:** `tier["default_temperature"]` is read at `agent.py:2080`, `api_admin.py:1548`, and `api_admin.py:206`, which is `GET /agents/models`, the endpoint this ticket's AC 8 counts. Scope § Modified catalog shape drops that key.
- **Repo-JSON:** the `mode` column swap breaks the agent export SELECT until #2's schema change.

Fixing any of these needs `database.py`, `agent.py` or `api_admin.py`, which are all #2's files. The agent `mode` column the call sites need also only exists after #2. This ticket's own test files (`test_config.py`, `test_llm_compat.py`) don't import `database`, so they stay runnable.

Options are in the plan's § Sequencing gap:
- **A (recommended, no Scope change):** #1 and #2 land as a pair. #1's QA manifest stays on the config and compat tests. The AC 8 endpoint count is checked on ftr after #2. Cost: ftr won't boot between the two merges.
- **B:** widen #1 into #2's call sites. It would need a placeholder agent mode.
- **C:** repartition so #1 is additive only. It would need interim stored thinking/temperature values.

The plan is written for A. Pick A and I'll move it to Plan Ready as-is. Pick B or C and I'll re-plan.

---

# AST-1947 — Catalog by quantization, mode-aware resolver, settings cleanup

- **Parent:** [AST-1946 — Support "Big" brain OpenRouter models](https://linear.app/astralcareermatch/issue/AST-1946)
- **Ticket:** [AST-1947](https://linear.app/astralcareermatch/issue/AST-1947)
- **Publish ref:** `origin/sub/AST-1946/AST-1947-catalog-quant-mode`
- **Canon Scope:** `stat.logging.debug`. No pattern applies (parent § Architectural definition: `no established pattern applies`).

This ticket swaps the OpenRouter catalog for the 95 slugs in Susan's AST-1946 brief and makes the agent's **mode** decide thinking and temperature. Each OpenRouter model offers exactly one brain size, set by its host's quantization: int4/fp4 → Little, int8/fp8 → Medium, fp16/bf16 → Big. Each one is pinned to the brief's host at the brief's quantization with fallbacks off, and priced at the brief's IN / OUT / CACHE. `kimi-k2.6-openrouter` is retired; `moonshotai/kimi-k2.6` is now an ordinary table row. Stored brain sizes lose `thinking`, `thinking_params` and `default_temperature`. Instead, each model carries a `can_think` flag and its thinking payload, and `resolve_model_brain` gains a required `mode` argument. The tier it returns gets `thinking` / `thinking_params` / `temperature` from the mode, plus a mode-capped output default on OpenRouter. The agent repo-JSON columns swap `temperature` for `mode`, and the seed and the AST-756 fixture follow. Dead helpers and the Anthropic default temperatures are removed. Database, call paths, admin routes, UI and the migration belong to siblings #2–#4 and are not touched here.

## Sequencing gap (blocks Plan Ready — `[scope-gate]` on AST-1947)

Ticket § Notes for planning: *"plan how this sub stays importable and green on its own."* The Scope can't do that. Doing every Scope item as written breaks sibling #2's files on this sub until #2 lands, and every repair is a change to a file this ticket does not own:

| # | Breaks when | Where (sibling #2's files) | Caused by (this ticket's Scope) |
|---|-------------|----------------------------|---------------------------------|
| 1 | **import time** — `src.data.database` fails to import, so the Flask app, dispatcher and every test that imports `database` fail | `src/data/database.py:103` imports `infer_brain_setting_from_legacy_model_code` | Scope § Removed: that helper |
| 2 | runtime `TypeError` | `resolve_model_brain(model_id, brain_setting)` calls at `src/core/agent.py:1831`, `src/ui/api/api_admin.py:389`, `src/ui/api/api_admin.py:1542`, `src/data/database.py:146` (agent public view, so every agent read) | Scope § Modified resolver: also takes mode |
| 3 | runtime `KeyError` | `tier["default_temperature"]` at `src/core/agent.py:2080`, `src/ui/api/api_admin.py:1548`, and `src/ui/api/api_admin.py:206` (`GET /agents/models`, the endpoint **this ticket's AC 8** counts) | Scope § Modified catalog shape: tiers drop `default_temperature` |
| 4 | runtime `sqlite3.OperationalError` | `fetch_agent_repo_json_export_rows` SELECTs config columns, so `mode` does not exist until #2's schema-ensure. `apply_agent_repo_json_startup` stores `temperature = NULL` and drops `mode` | Scope § Modified repo-JSON config |

The Scope gives no in-scope way out. #2's Scope has no `config.py` lines, so this ticket can't hand it the helper's removal. Keeping the old names alive fails this ticket's own AC 6 grep. And repairing the call sites from here needs an agent `mode` column that only #2 creates.

**This ticket's own component files stay runnable either way.** `tests/component/utils/test_config.py` imports `src.utils.config`. `tests/component/external/test_llm_compat.py` imports `src.external.llm_compat` → `src.utils.config` / `cost_calculator` / `llm_external` / `logging`. Neither imports `src.data.database`.

**Options for Susan / Chuckles (pick one; the plan below is written for A):**

- **A — land #1 and #2 as a pair (recommended; no Scope change).** Build this plan as written. Until #2 lands, this sub is green only for the config and compat component tests, so Betty's `qa-child` manifest stays on `test_config.py` / `test_llm_compat.py`. AC 8's `GET /api/admin/agents/models` = 98 is checked on `origin/ftr/AST-1946…` after #2 merges, the same way AC 6 and AC 9 already share halves with #2. The cost: `ftr` does not boot between #1's `merge-child` and #2's.
- **B — widen #1 into #2's files** (`database.py` import + legacy fallback, the four resolver call sites, the three `default_temperature` reads). Not recommended. The call sites need the agent's mode, and the agent row has no `mode` until #2's schema change, so #1 would have to invent a placeholder mode. That pulls most of #2 into #1.
- **C — repartition** so #1 is additive only (95-row table, pins, prices, mode constants) and every caller-breaking change (stored-tier reshape, resolver arg, helper removal, column swap) moves to #2 with `config.py` lines. Not recommended. The one-size-per-model OpenRouter tiers have no correct stored thinking/temperature without the mode resolver, so #1 would have to invent interim values that #2 then deletes.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`, and every stage is the kind of change Scope describes for that file. The sequencing gap above is the one Scope conflict, and it is raised as `[scope-gate]`, not absorbed.

- `src/utils/config.py`: new quantization-to-size map, the 95-row table, the builder, mode constants plus `validate_agent_mode` ("Validation helpers reject an unknown mode"), model-level `can_think` / `thinking_params` / `max_output_tokens`, the mode-aware `resolve_model_brain`, the repo-JSON column swap, and the listed removals. `_openrouter_pin` and `OPENROUTER_THINKING_PARAMS` belong to the table and builder ("row layout and field names are `plan-child`'s call"). The header-inventory and schema-comment edits document those changes.
- `data/admin/agent.json`, `docs/uat-fixtures/AST-756/expected-agent.json`: `temperature` → `mode` per row, nothing else.
- `stat.logging.debug`: no logging is added or changed. `src/external/llm_compat.py` is not touched. Its existing ungated `logger.debug("Calling messages.create: server=%s %s", server_id, api_kwargs)` and `Response from messages.create` lines keep logging the full body, including the mode-derived thinking/temperature and the quantization pin. No `debug=` parameter is added.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Header inventory lines. `REPO_ADMIN_JSON_CONFIG` agent columns `temperature` → `mode`. `AGENT_CONFIG` loses `default_temperature`. Remove `infer_brain_setting_from_legacy_model_code`. Replace `OPENROUTER_MODEL_TABLE` (95 rows, new layout), drop `OPENROUTER_PIN_QUANTIZATIONS` / `OPENROUTER_TIER_DEFAULTS`, add `OPENROUTER_QUANT_BRAIN_SIZE` / `OPENROUTER_THINKING_PARAMS`, rewrite `_openrouter_pin`. New `AGENT_MODE_*` constants + `validate_agent_mode`. `LLM_MODEL_CONFIG` schema comment; `kimi-k2.6` / `claude` / `deepseek-v4` reshaped; `kimi-k2.6-openrouter` deleted. Rewrite `_build_openrouter_models`, `resolve_model_brain`. Remove `brain_setting_for_anthropic_agent_key`, `admin_brain_setting_catalog`. | utils |
| `data/admin/agent.json` | 7 rows: `"temperature": …` line → `"mode": "…"` | data (seed) |
| `docs/uat-fixtures/AST-756/expected-agent.json` | 6 rows: drop `"temperature"`, add `"mode"` (sorted-key position) | fixture |

No other file is touched. No `tests/` or bible edits; Betty owns those (see **Tests expected to move**).

## Snapshot source (for reviewers)

Prices (IN / OUT / CACHE) are copied verbatim from the brief (parent § Original brief). Host routing slug, reasoning flag and max output come from `GET https://openrouter.ai/api/v1/models/<slug>/endpoints`, snapshot **2026-10-03**. For each brief row I took the endpoint whose `provider_name` equals the brief's PROVIDER **and** whose `quantization` equals the brief's QUANT. All 95 rows matched exactly one endpoint.

- **Host routing slug:** the endpoint `tag` before `/`, as in AST-1938 (`Mancer 2` → `mancer`, `OpenInference` → `open-inference`, `InferenceNet` → `inference-net`).
- **Reasoning:** `"reasoning" in supported_parameters` on that endpoint.
- **Max output:** that endpoint's `max_completion_tokens`.
- **Cross-checks against the parent:** 19 Little / 55 Medium / 21 Big; 57 reasoning-capable. The 12 removed slugs match the parent's list exactly, and 31 slugs are new. On host + price I count 46 unchanged and 18 moved, against the parent's 45 / 19. No unchanged row differs in reasoning or max output either. Every row is rewritten from the snapshot anyway, so the split changes nothing in the build.
- **Only one host serves a brief slug at two quantizations:** `google/gemma-4-31b-it` (DeepInfra fp4 = the brief row, plus fp8). The uniform `quantizations: [<row quant>]` pin covers it, which is why the one-off `OPENROUTER_PIN_QUANTIZATIONS` constant goes.
- AC spot values hold on the snapshot: `gryphe/mythomax-l2-13b` Parasail fp16, max 3686; `qwen/qwen3.5-27b` SiliconFlow fp8, max 235929; `undi95/remm-slerp-l2-13b` → `mancer` / `fp8`; `google/gemma-4-31b-it` → `deepinfra` / `fp4`; `moonshotai/kimi-k2.6` Inceptron int4 → Little.

---

## Stage 1: Catalog, mode constants, mode-aware resolver, cleanup (`config.py`)

**Done when:** `python3 -c "from src.utils.config import validate_llm_provider_environment as v, LLM_MODEL_CONFIG as C; v(); print(len(C))"` prints `98`. `resolve_model_brain("z-ai/glm-4.6", "Little", "Creative")["tier"]` has `thinking is True` and `thinking_params == {"thinking": {"type": "adaptive"}}`. `resolve_model_brain("gryphe/mythomax-l2-13b", "Big", "Creative")["tier"]["default_max_tokens"] == 3686`. `resolve_model_brain("claude", "Medium", "Wild")` raises `ValueError`.

1. **Header inventory** (module docstring, `Config sections:`). Replace these two lines:

   ```
     LLM_MODEL_CONFIG  — LLM models → server + per-model brain sizes (SKU, thinking, floor, defaults) + per-SKU pricing (AST-1851)
     OPENROUTER_MODEL_TABLE — OpenRouter shortlist rows expanded into LLM_MODEL_CONFIG (price, provider pin, reasoning, max output) (AST-1938)
   ```

   with these three:

   ```
     LLM_MODEL_CONFIG  — LLM models → server + can-think flag + per-model brain sizes (SKU, floor, output default) + per-SKU pricing (AST-1851, AST-1947)
     OPENROUTER_MODEL_TABLE — OpenRouter catalog rows expanded into LLM_MODEL_CONFIG (price, host + quantization pin, reasoning, max output) (AST-1938, AST-1947)
     AGENT_MODE_CONFIG — agent mode (Deterministic | Creative) → thinking, temperature, OpenRouter output cap (AST-1947)
   ```

   Also on the `AGENT_CONFIG    — Anthropic model catalog (pricing, defaults)` line, change `(pricing, defaults)` to `(pricing, output defaults)`.

2. **`REPO_ADMIN_JSON_CONFIG`.** In `"tables"` → `"agent"` → `"columns"`, replace the element `"temperature",` with `"mode",` in the same position. The tuple then reads `agent_id, content, model_id, brain_setting, mode, max_tokens, updated_at`.

3. **`AGENT_CONFIG`.**
   - Delete the `"default_temperature": 0.3,` line from each of `claude-haiku-4-5`, `claude-sonnet-4-6` and `claude-opus-4-6`. Nothing else in those dicts changes.
   - In the banner comment, replace `# cpm_* = cost per million tokens. temperature/max_tokens = defaults for new agents.` with `# cpm_* = cost per million tokens. default_max_tokens = that Claude size's output default (LLM_MODEL_CONFIG reads it).`

4. **Delete** the whole `def infer_brain_setting_from_legacy_model_code(...)` function (docstring and body), directly after `BRAIN_SETTINGS: tuple[str, str, str] = …`. Leave two blank lines between `BRAIN_SETTINGS` and `LLM_PROVIDER_CONFIG = {`.

5. **Replace the OpenRouter block.** Delete everything from the `# OPENROUTER_MODEL_TABLE — OpenRouter shortlist (AST-1937 brief)…` banner's opening `# ----` line through the end of `def _openrouter_pin` (its `return {"provider": pin}` line). That covers the old banner, `OPENROUTER_MODEL_TABLE`, `OPENROUTER_PIN_QUANTIZATIONS`, `OPENROUTER_TIER_DEFAULTS` and `_openrouter_pin`. In the same place, insert exactly this, with the rows from **Appendix A** in the order shown there:

   ```python
   # ---------------------------------------------------------------------------
   # OPENROUTER_MODEL_TABLE — the OpenRouter catalog (AST-1946 brief, 95 slugs). slug → (cpm_input,
   #   cpm_output, cpm_cache_read, host routing slug, host quantization, reasoning-capable, host max output tokens).
   # Prices: Susan's brief (AST-1946, 2026-10). Host slug / reasoning / max output:
   #   https://openrouter.ai/api/v1/models/<slug>/endpoints snapshot 2026-10-03 — the endpoint whose
   #   provider_name AND quantization equal the brief's PROVIDER and QUANT.
   # _build_openrouter_models() turns each row into one LLM_MODEL_CONFIG entry (model id = slug) with one
   # brain size: the host quantization's size (OPENROUTER_QUANT_BRAIN_SIZE).
   # ---------------------------------------------------------------------------
   OPENROUTER_MODEL_TABLE = {
       <Appendix A rows>
   }
   # Host quantization → the one brain size an OpenRouter model offers (AST-1947). No Huge.
   OPENROUTER_QUANT_BRAIN_SIZE = {
       "int4": BRAIN_LITTLE,
       "fp4": BRAIN_LITTLE,
       "int8": BRAIN_MEDIUM,
       "fp8": BRAIN_MEDIUM,
       "fp16": BRAIN_BIG,
       "bf16": BRAIN_BIG,
   }
   # Thinking payload for OpenRouter hosts whose endpoint is reasoning-capable.
   OPENROUTER_THINKING_PARAMS = {"thinking": {"type": "adaptive"}}


   def _openrouter_pin(slug: str) -> Dict[str, Any]:
       """Tier request_extras pinning a table slug to its host at the row's quantization, fallbacks off."""
       row = OPENROUTER_MODEL_TABLE[slug]
       return {"provider": {"order": [row[3]], "allow_fallbacks": False, "quantizations": [row[4]]}}


   # ---------------------------------------------------------------------------
   # AGENT_MODE_CONFIG — the agent row's mode decides thinking and temperature on every model (AST-1947).
   #   thinking        — True = think when the model can (LLM_MODEL_CONFIG can_think); never forces it on
   #   temperature     — sent when the call does not think (llm_compat drops it when thinking is on)
   #   max_tokens_cap  — output default on models with max_output_tokens (OpenRouter), capped at the host max
   # ---------------------------------------------------------------------------
   AGENT_MODE_DETERMINISTIC = "Deterministic"
   AGENT_MODE_CREATIVE = "Creative"
   AGENT_MODE_CONFIG = {
       AGENT_MODE_DETERMINISTIC: {"thinking": False, "temperature": 0.2, "max_tokens_cap": 16000},
       AGENT_MODE_CREATIVE: {"thinking": True, "temperature": 0.6, "max_tokens_cap": 32000},
   }
   AGENT_MODES: tuple[str, ...] = tuple(AGENT_MODE_CONFIG)


   def validate_agent_mode(mode: str) -> None:
       """Reject anything but a configured agent mode."""
       if mode not in AGENT_MODE_CONFIG:
           raise ValueError(f"Invalid mode {mode!r}. Allowed: {list(AGENT_MODES)}")
   ```

   ⚠️ **Decision:** the pin always carries `quantizations: [<row quant>]`, the shape AC 4 asserts. Routing slugs stay **base** slugs, as AST-1938 decided. The quantization filter, not a suffixed `tag`, selects the endpoint.

   ⚠️ **Decision:** Creative keeps `temperature: 0.6` even on thinking models. `llm_compat` already omits `temperature` when thinking is on (`if temperature is not None and not thinking_on`). So one key gives "think, else 0.6" with no per-model branch in the resolver.

6. **`LLM_MODEL_CONFIG` schema comment.** In the banner above `LLM_MODEL_CONFIG = {`, replace the block from `#   brain_sizes[<size>]:` through `#                           server's request_extras (size wins). OpenRouter provider pin (AST-1938).` with:

   ```
   #   can_think          — bool; Creative mode thinks only where this is True (AST-1947)
   #   thinking_params    — body fields sent when the resolved call thinks ({} when can_think is False)
   #   max_output_tokens  — optional int (OpenRouter host max output). When present, the resolved
   #                        default_max_tokens = min(mode max_tokens_cap, this) instead of the size's default
   #   brain_sizes[<size>] — stored rows carry no thinking / temperature; resolve_model_brain adds
   #                         thinking, thinking_params and temperature from the agent's mode (AST-1947):
   #     sku                 — vendor model string sent as `model`
   #     max_tokens_floor    — int | None; output-token floor applied over the agent's max_tokens
   #     default_max_tokens  — used when the agent row leaves max_tokens null (OpenRouter: listing default)
   #     request_extras      — optional dict (default {}): body fields for this size only, merged after the
   #                           server's request_extras (size wins). OpenRouter host + quantization pin.
   ```

   The `#   pricing[<sku>]: …` lines below it stay as they are.

7. **`kimi-k2.6` entry.**
   - Directly after `"server": "kimi",`, insert:
     ```python
             "can_think": True,
             "thinking_params": {"thinking": {"type": "enabled"}},
     ```
   - In `BRAIN_LITTLE`, delete `"thinking": False,`, `"thinking_params": {},` and `"default_temperature": 0.6,`.
   - In `BRAIN_BIG`, delete `"thinking": True,`, `"thinking_params": {"thinking": {"type": "enabled"}},` and `"default_temperature": 1.0,`.
   - `sku`, `max_tokens_floor` (None), `default_max_tokens` (16000 / 32000) and `pricing` are unchanged.

8. **Delete the whole `"kimi-k2.6-openrouter": { … },` entry**, from its key line through its closing `},`.

9. **`claude` entry.**
   - Directly after `"server": "anthropic",`, insert:
     ```python
             "can_think": False,
             "thinking_params": {},
     ```
   - In each of `BRAIN_LITTLE` / `BRAIN_MEDIUM` / `BRAIN_BIG`, delete the `"thinking": False,`, `"thinking_params": {},` and `"default_temperature": AGENT_CONFIG[...]["default_temperature"],` lines. `sku`, `max_tokens_floor`, `default_max_tokens` (still read from `AGENT_CONFIG`) and `pricing` are unchanged.

10. **`deepseek-v4` entry.**
    - Directly after `"server": "deepseek",`, insert the same two lines as step 9 (`"can_think": False,` / `"thinking_params": {},`).
    - Replace the comment `# Big is thinking-off today (legacy tier_map thinking=False; its reasoning_effort was never sent).` with `# can_think False: no thinking payload has ever been sent to DeepSeek direct (AST-1947).`
    - In each of the three sizes, delete `"thinking": False,`, `"thinking_params": {},` and `"default_temperature": 1.0,`. `sku`, `max_tokens_floor` (None / None / 384000), `default_max_tokens` (8192 / 16000 / 16000) and `pricing` are unchanged.

11. **Replace `_build_openrouter_models`** (the whole function: docstring and body) with:

    ```python
    def _build_openrouter_models() -> None:
        """Append one LLM_MODEL_CONFIG entry per OPENROUTER_MODEL_TABLE row (AST-1938, AST-1947). Model id,
        label, SKU and pricing key are all the slug; the one brain size is the host quantization's size."""
        listing_cap = AGENT_MODE_CONFIG[AGENT_MODE_DETERMINISTIC]["max_tokens_cap"]
        for slug, (cpm_in, cpm_out, cpm_cache, _host, quant, reasoning, max_out) in OPENROUTER_MODEL_TABLE.items():
            LLM_MODEL_CONFIG[slug] = {
                "label": slug,
                "server": "openrouter",
                "can_think": reasoning,
                "thinking_params": OPENROUTER_THINKING_PARAMS if reasoning else {},
                "max_output_tokens": max_out,
                "brain_sizes": {
                    OPENROUTER_QUANT_BRAIN_SIZE[quant]: {
                        "sku": slug,
                        "max_tokens_floor": None,
                        # Listing default only (models endpoint / form pre-fill); calls re-derive it from mode.
                        "default_max_tokens": min(listing_cap, max_out),
                        "request_extras": _openrouter_pin(slug),
                    },
                },
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

    The module-level `_build_openrouter_models()` call after it stays.

    ⚠️ **Decision:** stored OpenRouter sizes keep a `default_max_tokens`, set to `min(16000, host max)`. `GET /agents/models` (`api_admin.py:207`) and the Manage Agents size pre-fill (`AdminAgentPrompts.tsx:139`) read the stored per-size `default_max_tokens`, and #2 / #3 keep those reads (they only drop the temperature half). The Deterministic cap is the conservative listing value. The call path always uses the resolver's mode-capped value (AC 5).

    ⚠️ **Decision:** the old "skip slugs a hand-written entry already prices on openrouter" guard goes with `kimi-k2.6-openrouter`. No hand-written OpenRouter entry is left. `validate_llm_provider_environment` → `get_sku_pricing(…, server)` still raises on any duplicate SKU.

12. **Replace `resolve_model_brain`** (the whole function) with:

    ```python
    def resolve_model_brain(model_id: str, brain_setting: str, mode: str) -> Dict[str, Any]:
        """model + brain size + agent mode → server id/entry, SKU, pricing and the tier a call uses (AST-1947).
        The tier is the stored size row plus thinking / thinking_params / temperature from the mode, under the
        keys llm_compat reads; on models with max_output_tokens its output default is the mode cap (≤ host max)."""
        validate_brain_setting_for_model(model_id, brain_setting)
        validate_agent_mode(mode)
        m = get_llm_model(model_id)
        mc = AGENT_MODE_CONFIG[mode]
        thinking = mc["thinking"] and m["can_think"]
        tier = {
            **m["brain_sizes"][brain_setting],
            "thinking": thinking,
            "thinking_params": m["thinking_params"] if thinking else {},
            "temperature": mc["temperature"],
        }
        if "max_output_tokens" in m:
            tier["default_max_tokens"] = min(mc["max_tokens_cap"], m["max_output_tokens"])
        return {
            "model_id": model_id,
            "server_id": m["server"],
            "server": get_llm_server(m["server"]),
            "sku": tier["sku"],
            "tier": tier,
            "pricing": m["pricing"][tier["sku"]],
        }
    ```

    ⚠️ **Decision:** `mode` is a required positional argument with no default. A default would quietly choose a mode for callers that haven't been converted (sibling #2), which is the confusion Susan asked to clear out. See **Sequencing gap** row 2.

    ⚠️ **Decision:** the resolved temperature key is `temperature`, not `default_temperature`. AC 6's grep bans `default_temperature` everywhere in `src/`. #2 switches `agent.py` / `api_admin.py` to read `tier["temperature"]`.

13. **Delete** `def brain_setting_for_anthropic_agent_key(...)` and `def admin_brain_setting_catalog(...)` (both whole functions, after `anthropic_agent_key_for_brain_setting`). Keep two blank lines before the `# NAV_CONFIG` banner. `anthropic_agent_key_for_brain_setting`, `resolve_brain_setting_to_anthropic_agent_key`, `validate_allowed_brain_setting`, `get_model` and `LLM_PROVIDER_CONFIG` stay (not in Scope).

14. `validate_llm_provider_environment` is **not** changed. Its tier loop reads only `sku`, `request_extras` and pricing, all still present on every stored size.

**Stage commit:** `code(AST-1947): OpenRouter catalog by quantization, agent mode constants + mode-aware resolver, settings cleanup`

---

## Stage 2: Seed and fixture rows (`agent.json`, AST-756 fixture)

**Done when:** in `data/admin/agent.json` every row's keys equal `REPO_ADMIN_JSON_CONFIG["tables"]["agent"]["columns"]`. `ats_expert_atlas`, `content_writer_judith` and `principal_recruiter_estelle` are `Creative`, and the other four are `Deterministic`. The fixture's six rows have the same `mode` per `agent_id` and no `temperature`.

Mode rule (Functional scope item 8): `brain_setting == "Big"` → `"Creative"`, else `"Deterministic"`.

1. **`data/admin/agent.json`** — replace exactly one line per row, in place (4-space indent, trailing comma kept):

   | Line | `agent_id` (brain) | Replace | With |
   |------|--------------------|---------|------|
   | 7 | `ats_expert_atlas` (Big) | `"temperature": 0.3,` | `"mode": "Creative",` |
   | 16 | `college_intern_ruth` (Little) | `"temperature": 0.3,` | `"mode": "Deterministic",` |
   | 25 | `contact_recruiter_estelle` (Little) | `"temperature": null,` | `"mode": "Deterministic",` |
   | 34 | `content_writer_judith` (Big) | `"temperature": 0.3,` | `"mode": "Creative",` |
   | 43 | `job_analyst_grace` (Medium) | `"temperature": 0.3,` | `"mode": "Deterministic",` |
   | 52 | `principal_recruiter_estelle` (Big) | `"temperature": 0,` | `"mode": "Creative",` |
   | 61 | `web_scraper_laslo` (Medium) | `"temperature": 0.3,` | `"mode": "Deterministic",` |

2. **`docs/uat-fixtures/AST-756/expected-agent.json`** — this file uses sorted keys. In each row, delete the `"temperature": …,` line and insert the `"mode"` line directly after that row's `"max_tokens": …,` line (`mode` sorts between `max_tokens` and `model_code`):

   | `agent_id` (brain) | Delete (current line) | Insert after `"max_tokens"` |
   |--------------------|-----------------------|-----------------------------|
   | `job_analyst_grace` (Medium) | 8: `"temperature": 0.3,` | `"mode": "Deterministic",` |
   | `ats_expert_atlas` (Big) | 17: `"temperature": 0.3,` | `"mode": "Creative",` |
   | `content_writer_judith` (Big) | 26: `"temperature": 0.3,` | `"mode": "Creative",` |
   | `web_scraper_laslo` (Medium) | 35: `"temperature": 0.3,` | `"mode": "Deterministic",` |
   | `principal_recruiter_estelle` (Big) | 44: `"temperature": 0,` | `"mode": "Creative",` |
   | `college_intern_ruth` (Little) | 53: `"temperature": 0.3,` | `"mode": "Deterministic",` |

   ⚠️ **Decision:** the fixture is **not** a full twin of `agent.json`. It has 6 rows (no `contact_recruiter_estelle`), older `content`, a legacy `model_code`, no `model_id`, and different `updated_at` values. Scope says "No other field changes", so only `temperature` → `mode` is edited. AC 7's "matches field-for-field" is read as: `mode` agrees with `agent.json` for each shared `agent_id`, and no row has `temperature`. `test_repo_admin_json.py` already compares the two through `_ast787_fixture_repo_row` (Betty).

3. Both files must still parse: `python3 -c "import json; [json.load(open(p)) for p in ('data/admin/agent.json', 'docs/uat-fixtures/AST-756/expected-agent.json')]"`.

**Stage commit:** `code(AST-1947): agent seed + AST-756 fixture — mode in, temperature out`

---

## Verification (build-child §7, before each commit)

- `python3 -m py_compile src/utils/config.py`
- Lint: `ruff check --select F,E9 src/utils/config.py`, or `python3 -m pyflakes src/utils/config.py` if ruff is missing. **Neither is installed on this host as of planning.** If both are still missing at build time, stop and comment on the parent. Do not commit unlinted (Susan's rule).
- After Stage 1, run these `python3 -c` checks from the repo root. `BRIEF` = the 95 rows of parent § Original brief; `SIZE` as in the ticket's AC preamble.
  - **AC 1:** OpenRouter model-id set minus brief slugs, and the reverse: both `set()`.
  - **AC 2:** `model_brain_sizes(slug) == (SIZE[QUANT],)` for all 95. Spot: mythomax-l2-13b `('Big',)`, qwen3-32b `('Medium',)`, kimi-k2.6 `('Little',)`.
  - **AC 3:** `get_sku_pricing(slug, "openrouter")` matches IN/OUT/CACHE, `cpm_cache_write == 0` for all 95.
  - **AC 4:** each slug's stored tier `request_extras == {"provider": {"order": [host], "allow_fallbacks": False, "quantizations": [QUANT]}}`. Spot: remm-slerp-l2-13b `mancer`/`fp8`, gemma-4-31b-it `deepinfra`/`fp4`.
  - **AC 5:** for every slug × mode, `resolve_model_brain(slug, size, mode)["tier"]["default_max_tokens"] == min(cap, max_output_tokens)`. Spot: mythomax Creative 3686, qwen3.5-27b Creative 32000 / Deterministic 16000.
  - **AC 6 (config half):** no stored tier in `LLM_MODEL_CONFIG` has `thinking`, `thinking_params` or `default_temperature`. Direct models compared against these `origin/dev` values: `claude` sizes `('Little','Medium','Big')`, SKUs haiku/sonnet/opus-4-x, `default_max_tokens` 8192/16000/16000. `kimi-k2.6` `('Little','Big')`, 16000/32000. `deepseek-v4` `('Little','Medium','Big')`, flash/pro/pro, 8192/16000/16000, Big floor 384000, others `None`.
    ⚠️ **Decision:** "pricing rows equal pre-epic" is compared on pricing fields only (`model_label`, `cpm_*`, `cache_min_tokens`). The Claude pricing rows are the `AGENT_CONFIG` dicts, which lose `default_temperature` because the Scope says so.
  - **AC 6 / AC 9 greps:** `rg -n "default_temperature|brain_setting_for_anthropic_agent_key|admin_brain_setting_catalog|infer_brain_setting_from_legacy_model_code" src/utils/config.py` returns nothing. On this sub, the remaining `src/` hits are in #2 / #3 files (Sequencing gap rows 1–3, plus `AdminAgentPrompts.tsx`). The AC 9 slug grep (`--glob '!src/utils/config.py'`) returns nothing.
  - **AC 8 (config half):** `"kimi-k2.6-openrouter" not in LLM_MODEL_CONFIG`, `rg -n "kimi-k2.6-openrouter" src/` returns nothing, `validate_llm_provider_environment()` passes, and `len(LLM_MODEL_CONFIG) == 98`. The `GET /api/admin/agents/models` count runs after #2 (Sequencing gap option A).
  - **Mode wiring (feeds parent AC 5):** `resolve_model_brain` tiers: `z-ai/glm-4.6` Little Creative → `thinking=True`, adaptive payload. `microsoft/phi-4` Big Creative → `thinking=False`, `temperature=0.6`. `z-ai/glm-4.6` Deterministic → `thinking=False`, `temperature=0.2`. `kimi-k2.6` Little Creative → `thinking=True`, `{"thinking": {"type": "enabled"}}`. `deepseek-v4` Big Creative → `thinking=False`, 0.6, floor 384000. `claude` Medium Deterministic → SKU `claude-sonnet-4-6`, 0.2. Unknown mode → `ValueError`.
- After Stage 2: **AC 7** seed/fixture check as in its Done-when.

## Tests expected to move (Betty, `qa-child`)

Not edited here (the test tree is off-limits to engineers). Listed so the manifest can account for them:

- `tests/component/utils/test_config.py`: AST-1938 table/builder tests (76 rows, Little/Medium expansion, `OPENROUTER_TIER_DEFAULTS`, `OPENROUTER_PIN_QUANTIZATIONS`, 79-model count), `kimi-k2.6-openrouter` pin/price tests, tier `thinking` / `default_temperature` assertions on direct models, `infer_brain_setting_from_legacy_model_code` / `brain_setting_for_anthropic_agent_key` / `admin_brain_setting_catalog` tests, `REPO_ADMIN_JSON_CONFIG` agent columns, and any two-arg `resolve_model_brain` call. New coverage: ticket AC 1–6 and 8 (config half).
- `tests/component/external/test_llm_compat.py`: the `kimi-k2.6-openrouter` Little/Big calls (they now use `moonshotai/kimi-k2.6` Little through a mode-resolved tier) and any tier fixture built with `default_temperature`. New coverage: parent AC 5's wire checks driven by `resolve_model_brain(…, mode)` tiers.
- **Outside this child's test files (sibling #2's, listed so nobody is surprised):** `tests/component/core/test_repo_admin_json.py` (AST-787 fixture comparison and columns), `tests/component/core/test_agent.py` and `tests/component/ui/api/test_api_admin.py` fail on this sub until #2 lands (Sequencing gap).

## Estimate

Confirm Chuckles estimate: 5 — agree

Blocked on the sequencing decision above (`[scope-gate]`), not on size.

---

## Appendix A — `OPENROUTER_MODEL_TABLE` rows (paste verbatim, 4-space indent, in this order)

```python
    "apodex/apodex-1.1-mini:free": (0.0, 0.0, 0.0, "novita", "bf16", True, 235929),
    "bytedance-seed/seed-1.6": (0.25, 2.0, 0.0, "seed", "fp8", True, 32768),
    "bytedance-seed/seed-1.6-flash": (0.08, 0.3, 0.0, "seed", "fp8", True, 32768),
    "bytedance-seed/seed-2-1-turbo": (0.5, 2.5, 0.0, "seed", "fp8", True, 235929),
    "bytedance-seed/seed-2.0-code": (0.5, 3.0, 0.0, "seed", "fp8", True, 131072),
    "bytedance-seed/seed-2.0-lite": (0.25, 2.0, 0.0, "seed", "fp8", True, 131072),
    "bytedance-seed/seed-2.0-mini": (0.1, 0.4, 0.0, "seed", "fp8", True, 131072),
    "bytedance/ui-tars-1.5-7b": (0.1, 0.2, 0.1, "parasail", "bf16", False, 2048),
    "deepseek/deepseek-chat": (0.32, 0.89, 0.0, "deepinfra", "fp4", False, 16384),
    "deepseek/deepseek-chat-v3-0324": (0.25, 1.0, 0.0, "siliconflow", "fp8", False, 147456),
    "deepseek/deepseek-chat-v3.1": (0.25, 0.95, 0.13, "deepinfra", "fp4", True, 32768),
    "deepseek/deepseek-r1-0528": (0.5, 2.18, 0.0, "siliconflow", "fp8", True, 147456),
    "deepseek/deepseek-v3.1-terminus": (0.27, 1.0, 0.0, "siliconflow", "fp8", True, 147456),
    "deepseek/deepseek-v3.2": (0.26, 0.42, 0.14, "siliconflow", "fp8", True, 147456),
    "deepseek/deepseek-v3.2-exp": (0.27, 0.41, 0.0, "siliconflow", "fp8", True, 147456),
    "deepseek/deepseek-v4-flash": (0.0, 1.22, 0.0, "open-inference", "fp8", True, 943718),
    "deepseek/deepseek-v4-flash-0731": (0.01, 0.95, 0.0, "open-inference", "fp8", True, 943718),
    "deepseek/deepseek-v4-flash-vision-exp": (0.22, 0.65, 0.01, "deepinfra", "fp8", True, 262144),
    "deepseek/deepseek-v4.1-flash": (0.02, 0.68, 0.0, "open-inference", "fp4", True, 943718),
    "google/gemma-2-27b-it": (0.65, 0.65, 0.0, "nextbit", "int4", False, 2048),
    "google/gemma-3-12b-it": (0.05, 0.15, 0.0, "deepinfra", "bf16", False, 16384),
    "google/gemma-3-27b-it": (0.08, 0.45, 0.04, "parasail", "fp8", False, 117964),
    "google/gemma-3-4b-it": (0.05, 0.1, 0.0, "deepinfra", "bf16", False, 16384),
    "google/gemma-4-26b-a4b-it": (0.07, 0.34, 0.0, "deepinfra", "fp8", True, 16384),
    "google/gemma-4-31b-it": (0.09, 0.34, 0.05, "deepinfra", "fp4", True, 16384),
    "gryphe/mythomax-l2-13b": (0.08, 0.11, 0.0, "parasail", "fp16", False, 3686),
    "ibm-granite/granite-4.2-8b": (0.1, 0.15, 0.05, "coreweave", "bf16", True, 117964),
    "inclusionai/ling-3.0-flash-fin": (0.06, 0.18, 0.01, "deepinfra", "fp4", True, 235929),
    "inclusionai/ling-3.0-flash-vl": (0.06, 0.18, 0.01, "deepinfra", "fp16", True, 32768),
    "meta-llama/llama-3.1-70b-instruct": (0.4, 0.4, 0.0, "deepinfra", "fp8", False, 16384),
    "meta-llama/llama-3.1-8b-instruct": (0.22, 0.22, 0.22, "coreweave", "bf16", False, 117964),
    "meta-llama/llama-3.2-3b-instruct": (0.05, 0.33, 0.0, "parasail", "bf16", False, 117964),
    "meta-llama/llama-3.3-70b-instruct": (0.1, 0.32, 0.0, "deepinfra", "fp8", False, 16384),
    "meta-llama/llama-4-maverick": (0.27, 0.85, 0.0, "novita", "fp8", False, 8192),
    "meta-llama/llama-4-scout": (0.1, 0.3, 0.0, "deepinfra", "fp8", False, 16384),
    "meta/muse-glimmer-30b": (0.3, 1.2, 0.04, "deepinfra", "bf16", True, 16384),
    "microsoft/phi-4": (0.07, 0.14, 0.0, "deepinfra", "bf16", False, 14745),
    "minimax/minimax-m3": (0.23, 0.96, 0.05, "coreweave", "fp4", True, 235929),
    "mistralai/mistral-nemo": (0.02, 0.03, 0.0, "deepinfra", "fp8", False, 16384),
    "mistralai/mistral-small-24b-instruct-2501": (0.05, 0.08, 0.0, "deepinfra", "fp8", False, 16384),
    "mistralai/mistral-small-3.2-24b-instruct": (0.08, 0.2, 0.0, "deepinfra", "fp8", False, 16384),
    "moonshotai/kimi-k2-0905": (0.6, 2.5, 0.0, "novita", "fp8", False, 98304),
    "moonshotai/kimi-k2-thinking": (0.6, 2.5, 0.15, "novita", "bf16", True, 98304),
    "moonshotai/kimi-k2.5": (0.45, 2.25, 0.07, "siliconflow", "int4", True, 235929),
    "moonshotai/kimi-k2.6": (0.43, 2.45, 0.12, "inceptron", "int4", True, 235929),
    "moonshotai/kimi-k2.7-code": (0.67, 3.35, 0.18, "inceptron", "int4", True, 235929),
    "nousresearch/hermes-3-llama-3.1-70b": (0.7, 0.7, 0.0, "deepinfra", "fp8", False, 16384),
    "nvidia/nemotron-3-nano-30b-a3b": (0.05, 0.2, 0.03, "crusoe", "fp8", True, 235929),
    "nvidia/nemotron-3-super-120b-a12b": (0.08, 0.45, 0.0, "dekallm", "fp8", True, 235929),
    "nvidia/nemotron-3-ultra-550b-a55b": (0.5, 2.2, 0.1, "deepinfra", "fp4", True, 16384),
    "nvidia/nemotron-3.5-lightning": (0.06, 0.16, 0.03, "deepinfra", "bf16", True, 32768),
    "openai/gpt-oss-120b": (0.03, 0.18, 0.03, "dekallm", "bf16", True, 117964),
    "openai/gpt-oss-20b": (0.02, 0.1, 0.0, "akashml", "fp4", True, 117964),
    "qwen/qwen-2.5-72b-instruct": (0.36, 0.4, 0.0, "deepinfra", "fp8", False, 16384),
    "qwen/qwen3-14b": (0.1, 0.22, 0.0, "nextbit", "int4", True, 36864),
    "qwen/qwen3-235b-a22b-2507": (0.09, 0.58, 0.0, "novita", "fp8", False, 16384),
    "qwen/qwen3-30b-a3b": (0.12, 0.5, 0.0, "deepinfra", "fp8", True, 16384),
    "qwen/qwen3-30b-a3b-instruct-2507": (0.09, 0.3, 0.0, "siliconflow", "fp8", False, 235929),
    "qwen/qwen3-32b": (0.08, 0.28, 0.0, "deepinfra", "fp8", True, 16384),
    "qwen/qwen3-coder": (0.3, 1.0, 0.1, "deepinfra", "fp4", False, 65536),
    "qwen/qwen3-coder-30b-a3b-instruct": (0.07, 0.28, 0.0, "siliconflow", "fp8", False, 235929),
    "qwen/qwen3-coder-next": (0.12, 0.8, 0.07, "parasail", "bf16", False, 235929),
    "qwen/qwen3-next-80b-a3b-instruct": (0.09, 1.1, 0.0, "deepinfra", "fp8", False, 16384),
    "qwen/qwen3-vl-235b-a22b-instruct": (0.2, 0.88, 0.11, "deepinfra", "fp8", False, 16384),
    "qwen/qwen3-vl-30b-a3b-instruct": (0.15, 0.6, 0.0, "deepinfra", "fp8", False, 16384),
    "qwen/qwen3-vl-30b-a3b-thinking": (0.29, 1.0, 0.0, "siliconflow", "fp8", True, 235929),
    "qwen/qwen3-vl-8b-instruct": (0.25, 0.75, 0.12, "parasail", "bf16", False, 235929),
    "qwen/qwen3.5-27b": (0.25, 2.0, 0.0, "siliconflow", "fp8", True, 235929),
    "qwen/qwen3.5-35b-a3b": (0.14, 1.0, 0.05, "deepinfra", "fp8", True, 81920),
    "qwen/qwen3.5-397b-a17b": (0.45, 3.0, 0.22, "deepinfra", "fp8", True, 81920),
    "qwen/qwen3.5-9b": (0.1, 0.15, 0.0, "deepinfra", "bf16", True, 81920),
    "qwen/qwen3.6-27b": (0.3, 3.2, 0.0, "siliconflow", "fp8", True, 235929),
    "qwen/qwen3.6-35b-a3b": (0.1, 0.95, 0.1, "deepinfra", "fp8", True, 65536),
    "qwen/qwen3.8-27b": (0.09, 2.2, 0.09, "ionstream", "fp8", True, 65536),
    "qwen/qwen3.8-27b:free": (0.0, 0.0, 0.0, "modelrun", "fp4", True, 235929),
    "sao10k/l3-lunaris-8b": (0.04, 0.05, 0.0, "parasail", "bf16", False, 7372),
    "sao10k/l3.3-euryale-70b": (0.65, 0.75, 0.0, "nextbit", "bf16", False, 16384),
    "stepfun/step-3.7-flash": (0.2, 1.15, 0.04, "novita", "fp8", True, 256000),
    "tencent/hunyuan-a13b-instruct": (0.14, 0.57, 0.0, "siliconflow", "fp8", True, 117964),
    "tencent/hy-mt2-30b-a3b": (0.07, 0.3, 0.0, "tencent", "fp8", False, 4096),
    "tencent/hy-mt2-7b": (0.07, 0.3, 0.0, "tencent", "fp8", False, 4096),
    "tencent/hy3": (0.13, 0.53, 0.03, "deepinfra", "fp4", True, 131072),
    "thedrummer/cydonia-24b-v4.1": (0.3, 0.5, 0.15, "parasail", "bf16", False, 117964),
    "thedrummer/skyfall-36b-v2": (0.55, 0.8, 0.25, "parasail", "fp8", False, 29491),
    "thedrummer/unslopnemo-12b": (0.4, 0.4, 0.0, "parasail", "bf16", False, 819200),
    "undi95/remm-slerp-l2-13b": (0.35, 0.65, 0.0, "mancer", "fp8", False, 5529),
    "xiaomi/mimo-v2.5": (0.4, 2.0, 0.08, "venice", "fp8", True, 65536),
    "xiaomi/mimo-v2.6-flash": (0.12, 0.28, 0.01, "inference-net", "fp8", True, 943718),
    "xiaomi/mimo-v2.6-pro": (0.43, 0.87, 0.0, "deepinfra", "fp8", True, 943718),
    "z-ai/glm-4.6": (0.43, 1.75, 0.08, "venice", "fp4", True, 16384),
    "z-ai/glm-4.7": (0.4, 1.75, 0.08, "deepinfra", "fp4", True, 131072),
    "z-ai/glm-4.7-flash": (0.06, 0.4, 0.01, "venice", "fp8", True, 16384),
    "z-ai/glm-5.2": (0.17, 3.07, 0.2, "morph", "fp8", True, 943718),
    "z-ai/glm-5.3": (0.13, 2.99, 0.15, "morph", "fp8", True, 943718),
    "z-ai/glm-5.3-flash": (0.03, 0.93, 0.01, "open-inference", "fp4", True, 943718),
```


## Joan validate

[plan-rubric]
**Ticket:** AST-1947
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `origin/sub/AST-1946/AST-1947-catalog-quant-mode` @ `52411898b5b376835b8d2b2cfee06cbc12012f5c`

## Canon scores
stat.logging.debug | A |

## Traceability
**AC1** → Stage 1 + Verification (`OPENROUTER_MODEL_TABLE` / builder; set-diff vs brief). **AC2** → Stage 1 step 5/11 (`OPENROUTER_QUANT_BRAIN_SIZE`, one tier per slug). **AC3** → Stage 1 + Appendix A prices. **AC4** → Stage 1 `_openrouter_pin` + `quantizations`. **AC5** → Stage 1 `resolve_model_brain` + `AGENT_MODE_CONFIG` caps. **AC6** → Stage 1 catalog reshape + greps on `config.py` / stored tiers; `AdminAgentPrompts.tsx` temperature grep **N/A on this sub** (#3). **AC7** → Stage 2 seed + AST-756 fixture. **AC8** → Stage 1 (`kimi-k2.6-openrouter`, `validate_llm_provider_environment`, `len==98`); `GET /api/admin/agents/models` count **on `ftr` after AST-1948** (option A, Chuckles AST-1947 comment). **AC9** → Verification slug `rg` + config-only ownership; `0.2`/`0.6` literal grep on `agent.py` / `api_admin.py` / `database.py` **paired with #2** (out of Files Changed). Parent **AC1–6** (catalog/mode/resolver) → Stages 1–2; **AC7** config half → AC6 greps here, UI half #3; **AC8–10** → #2/#3; **AC11** → AC8; **AC12** → AC9; **AC13** → #4.

## Findings

### discuss
- **Severity:** discuss  
  **Location:** `## Estimate` (plan tail)  
  **Finding:** Still says “Blocked on the sequencing decision” though Susan chose **A** on AST-1951 and Chuckles recorded resolution on AST-1947.  
  **Recommendation:** Optional plan tidy (confirm line only); does not block build under option A.

- **Severity:** discuss  
  **Location:** Verification vs child **AC6** / **AC9**  
  **Finding:** Verification spells out config-half and slug grep; shared halves (frontend temperature grep, core/api/db mode literals) rely on option A + Betty manifest on `test_config.py` / `test_llm_compat.py` only.  
  **Recommendation:** Keep qa-child manifest narrow per plan; run shared AC checks on `ftr` after #2/#3 as already stated for AC8 endpoint count.

### acceptable
- **Severity:** acceptable  
  **Location:** `## Sequencing gap` heading  
  **Finding:** Wording still reads “blocks Plan Ready” while status is Plan Ready post–option A.  
  **Recommendation:** Historical scope-gate record; engineer may retitle when convenient.

context_tokens≈32000


## Review

- **Branch:** `origin/sub/AST-1946/AST-1947-catalog-quant-mode`
- **Build tip:** `131911492`. Stages: `220dc5a0d` (OpenRouter catalog by quantization, agent mode constants and mode-aware resolver, settings cleanup in `config.py`) and `131911492` (agent seed and AST-756 fixture: `mode` in, `temperature` out).
- **Sequencing:** built under option A ([AST-1951](https://linear.app/astralcareermatch/issue/AST-1951)). Until AST-1948 lands, `src.data.database` does not import on this sub, as § Sequencing gap expects. Joan's two optional tidy notes (the `## Estimate` tail line and the Sequencing gap heading) are left as the historical scope-gate record.
- **Build notes:** built as planned. Stage 1 step 5 was spliced verbatim from this doc (step 5 code block plus Appendix A). Stage 2 was applied by the plan's line numbers, with each line's current text and its row's `agent_id` asserted before editing. Verified on the shipped tree:
  - `validate_llm_provider_environment()` passes, with 98 models.
  - AC 1–5 hold for all 95 brief slugs against the parent brief text (no set difference, no size / price / pin / mode-cap violations). Spot values: mythomax-l2-13b `('Big',)`, Creative 3686; qwen3-32b `('Medium',)`; kimi-k2.6 `('Little',)`; qwen3.5-27b 32000 / 16000; remm-slerp-l2-13b `mancer`/`fp8`; gemma-4-31b-it `deepinfra`/`fp4`.
  - AC 6 (config half): no stored tier has `thinking` / `thinking_params` / `default_temperature`, direct SKUs / defaults / floors are unchanged, and the four-name grep on `config.py` is empty.
  - AC 7: seed keys equal the config columns; atlas, judith and principal_estelle are Creative and the other four Deterministic; the fixture agrees per `agent_id`; no `temperature` remains.
  - AC 8 (config half): `kimi-k2.6-openrouter` is gone. AC 9 slug grep is empty.
  - Mode wiring matches § Verification for all seven cases, and `"Wild"` raises `ValueError`.
  - Lint: `py_compile` and `ruff check --select F,E9` are clean. ruff was not on the host; it ran from a throwaway `pip install --target /tmp/ruffenv ruff`, with no repo or system change.
- **Git note:** the spawn prompts pass `--ftr AST-1946`, but the parent ref is `ftr/AST-1946-big-brain-openrouter`, so `sync-child.sh` skipped the ftr merge. That changed nothing here: ftr is at `22810969c`, this sub's base. `validate-sub-log.sh --stage=build` passes against the full ref name.
- **For qa-child:** manifest stays on `tests/component/utils/test_config.py` and `tests/component/external/test_llm_compat.py` (option A). See **Tests expected to move**. `test_repo_admin_json.py`, `test_agent.py` and `test_api_admin.py` stay red until AST-1948.


## Radia review

```text
[code-rubric]
**Ticket:** AST-1947
**Publish ref:** `0d5db0f6f839bb2668f3c2b0cff7ef010f8857c3` (`origin/sub/AST-1946/AST-1947-catalog-quant-mode`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores
| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |

## Column diff vs plan stage
(aligned) — Joan: `stat.logging.debug` **A**; diff review matches.

## Frame diff
- [ ] **AC 6 (shared):** After AST-1948 / UI sibling land on `ftr`, `rg` for `default_temperature`, the four removed helper names, and `temperature` in `AdminAgentPrompts.tsx` is empty across `src/` (Linear AC text; config half satisfied on this sub).
- [ ] **AC 8 (shared):** `GET /api/admin/agents/models` returns **98** on `ftr` after AST-1948 (endpoint read path uses `resolve_model_brain(..., mode)`).
- [ ] **AC 9 (shared):** No `0.2` / `0.6` mode-temperature literals in `src/core/agent.py`, `src/ui/api/api_admin.py`, or `src/data/database.py` after AST-1948.

## Findings

### fix-now
(none)

### discuss
- **Severity:** discuss  
  **Location:** Linear **Acceptance criteria** AC 6 vs plan **Verification** / Joan **Traceability**  
  **Finding:** AC 6 still requires whole-`src/` greps (including `AdminAgentPrompts.tsx`) that cannot pass until siblings #2–#3; the shipped diff correctly limits itself to the config half (stored tiers clean, `config.py` grep empty, `infer_brain_setting_from_legacy_model_code` removed). Remaining hits on `origin/dev` call sites (`agent.py`, `api_admin.py`, `AdminAgentPrompts.tsx`) are unchanged in this three-dot diff and are expected under sequencing option A.  
  **@susan:** Keep treating shared AC 6 bullets as **ftr gates** after #2/#3, or narrow the Linear AC wording to match option A?  
  **Default:** Leave Linear AC as-is; do not reopen AST-1947 — validate full AC 6 on `ftr` after AST-1948 and the UI child merge.

### advisory
- **sibling test carry:** `tests/component/utils/test_config.py`, `tests/component/external/test_llm_compat.py`, `docs/test-bible/utils/config.md`, `docs/test-bible/external/llm_compat.md`, fixture swap `ast1937` → `ast1946_openrouter_brief.txt` — expected Betty `merge-tests` on this sub; not product scope bleed.
- **Import / app boot:** `src.data.database` and sibling component tests (`test_agent.py`, `test_api_admin.py`, `test_repo_admin_json.py`) remain broken until AST-1948 — documented in plan **Sequencing gap**; spawn prompt confirms this is expected.
- **Tip commit:** `0d5db0f6f` is `merge-tests(AST-1947)` atop Katherine’s two code stages; product delta vs `origin/dev` is `config.py`, seed, AST-756 fixture, and test/bible only — no `llm_compat.py`, `database.py`, `agent.py`, or admin/UI paths.

## What's solid
- **Plan fidelity:** 95-row `OPENROUTER_MODEL_TABLE`, quantization → single brain size, `_openrouter_pin` with `quantizations`, `AGENT_MODE_CONFIG` + required `mode` on `resolve_model_brain`, stored tiers without thinking/temperature, `kimi-k2.6-openrouter` removed, repo-JSON column `mode`, seed/fixture modes — all match the issue doc stages.
- **stat.logging.debug:** No new `logger.*` in `config.py`; `llm_compat.py` untouched — existing ungated `logger.debug` on `api_kwargs` / response still carries resolver-derived thinking, temperature, and pin (no `debug=` parameter added).
- **Spot checks on workspace tree:** `validate_llm_provider_environment()` passes; `len(LLM_MODEL_CONFIG)==98`; stored-tier scan finds no `thinking` / `thinking_params` / `default_temperature`; mode wiring spots (glm Creative, mythomax cap 3686, invalid `Wild` → `ValueError`) behave as specified.

## Recommended actions (downstream — not Radia)
- Chuckles: append this artifact to the issue doc, commit `docs(AST-1947): Radia review — clean`, push, post slim upshot `--as radia`, move **Review Posted** → datt **PROCEED** path (no fix-now).
- **resolve-child:** No canon fix-now; optional frame-diff ticks above are **ftr** checklist items, not this sub’s resolve work unless Susan narrows AC 6 in Linear.
- After AST-1948 merges to `ftr`: run full AC 6/8/9 greps and admin models count before parent UAT.

context_tokens≈28000
```

## Resolution

- **Date:** 2026-10-03. **Reviewed tip:** `0d5db0f6f` (review commit `e15f115cf`). No product change in resolve.
- **Fix-now:** none.
- **Discuss (shared AC 6 greps):** no Susan answer in thread, so Radia's `Default:` applies. The Linear AC text stays as written and AST-1947 is not reopened. The whole-`src/` AC 6 greps, the AC 8 `GET /api/admin/agents/models` = 98 count, and the AC 9 mode-literal grep run on `ftr/AST-1946-big-brain-openrouter` after AST-1948 and the UI child merge. Susan can reverse this by narrowing AC 6 in Linear.
- **Frame diff rows:** left unchecked on purpose. They are ftr gates under option A ([AST-1951](https://linear.app/astralcareermatch/issue/AST-1951)) and cannot be validated on this sub. The config halves of AC 6 and AC 8 hold on this tip, per § Review.
- **Advisory:** nothing to act on. The sibling test carry and the `src.data.database` import break until AST-1948 are both expected under § Sequencing gap.
