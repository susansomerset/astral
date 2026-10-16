# AST-1946 — Support "Big" brain OpenRouter models

<!-- linear-archive: AST-1946 archived 2026-10-08 -->

## Linear archive (AST-1946)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1946/support-big-brain-openrouter-models  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-1937](https://linear.app/astralcareermatch/issue/AST-1937) put 76 OpenRouter models in the catalog, all on 8-bit hosts. Their "brain size" quietly meant thinking on/off and an output budget, while temperature lived on the agent row, in per-size defaults, and in legacy Anthropic defaults. Susan wants **the agent row to decide everything about a call**, in a few plain choices, so tasks can be organized by agent "with fewer switches to chase around":

* **Model code:** the exact model version. On OpenRouter it is the slug sent on the wire.
* **Brain size:** on OpenRouter models, the **quantization** of that model's host: Little = 4-bit, Medium = 8-bit, Big = 16-bit. On the direct models (Claude, Kimi-direct, DeepSeek-direct) it keeps choosing the SKU, as today.
* **Mode:** a new setting on every agent. **Deterministic** = thinking off, temperature 0.2. **Creative** = thinking on, or temperature 0.6 where the model can't think.

This ticket **supersedes every earlier thinking/temperature setting** and clears out the logic that would confuse it (Susan). The OpenRouter catalog is replaced wholesale by the 95-slug Original brief below. The direct models persist and keep working until a later sunset ticket.

## Functional scope

 1. **Brain size = quantization on OpenRouter models.** Each OpenRouter model offers exactly one brain size, the one its host's quantization maps to: int4/fp4 → `Little`, int8/fp8 → `Medium`, fp16/bf16 → `Big`. No Huge (Susan: none in the set). The size labels are the existing `Little` / `Medium` / `Big`.
 2. **The brief is the whole OpenRouter catalog (Susan: "completely replace").** The OpenRouter models are exactly the 95 slugs in the Original brief:
    * 45 are unchanged from AST-1938 (same host, same price).
    * 19 move host and/or price.
    * 31 are new.
    * 12 current models are removed: `anthracite-org/magnum-v4-72b`, `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-pro-0813`, `moonshotai/kimi-k3`, `morph/morph-v3-large`, `nousresearch/hermes-3-llama-3.1-405b`, `qwen/qwen2.5-vl-72b-instruct`, `qwen/qwen3.8-2.4t-a95b`, `sao10k/l3.1-euryale-70b`, `tencent/hy4-preview`, `z-ai/glm-5`, `z-ai/glm-5.1`.
    * Every brief row matches a live OpenRouter endpoint at exactly that host and quantization (2026-10-02 snapshot). That gives 19 Little, 55 Medium and 21 Big models; 57 of them can think.
 3. **Host pin and pricing from the brief.** Each OpenRouter model is pinned to the brief's PROVIDER at the brief's QUANT, with fallbacks off. It is priced at the brief's IN / OUT / CACHE (cache read) per million tokens, with cache write 0. Each slug has one host, so pricing stays one row per slug and the ledger path is unchanged.
 4. **Mode on every agent decides thinking and temperature, on every model.**
    * **Deterministic:** thinking off, temperature 0.2.
    * **Creative**, on a model that can think: thinking on. The compat client already sends no temperature when thinking is on.
    * **Creative**, on a model that can't think: thinking off, temperature 0.6.
    * **Which models can think:**
      * OpenRouter: per host, from the snapshot's reasoning flag; payload is the existing adaptive one.
      * `kimi-k2.6` direct: yes, with its existing `enabled` payload.
      * `claude`: no. The Anthropic client has no thinking parameter, so Creative = 0.6.
      * `deepseek-v4` direct: no. No thinking payload has ever been sent to it in this codebase, so Creative = 0.6.
 5. **Output budget.** On OpenRouter models the default output budget is 16,000 for Deterministic and 32,000 for Creative, capped at the host's max output (AST-1937's 16k / 32k rule, now keyed by mode). Direct models keep their per-size output defaults and DeepSeek Big's 384k floor. The agent row's `max_tokens` still overrides the default.
 6. **Direct models persist (Susan).** `claude`, `kimi-k2.6` and `deepseek-v4` keep their model codes, brain sizes, SKUs, pricing and output defaults/floors. Only their thinking and temperature now come from mode, per this ticket superseding earlier settings. For example, `content_writer_judith` (Kimi Big, Creative) still thinks. `job_analyst_grace` (DeepSeek Medium, Deterministic) runs at 0.2 instead of its stored 0.3.
 7. **Clear out the confusing settings (Susan).**
    * The agent row's **temperature** field is removed everywhere: database column, seed file, API, Manage Agents form and list.
    * The per-size **thinking / thinking payload / default temperature** fields are removed from every catalog tier. Each model instead carries one "can think" flag and its thinking payload.
    * The Anthropic catalog's per-model default temperatures and two dead legacy helpers go too.
    * The agent row's legacy `model_code` column is removed, because it duplicates `model_id` (Susan: "duplicative model indicators in the agent table"). So is the legacy fallback that guessed a brain size from it. `model_id` is the one model indicator.
    * **Kept:** the craft-rubric thinking-off guard ([AST-1380](<https://linear.app/astralcareermatch/issue/AST-1380>)) and the max-token floors. They are task-level correctness guards against truncated JSON, not agent settings.
 8. **Starting modes (Susan: "for now").** Every existing agent whose brain size is `Big` starts **Creative**; every other agent starts **Deterministic**. This applies to the seed file and the live database. In the seed file that makes `ats_expert_atlas`, `content_writer_judith` and `principal_recruiter_estelle` Creative and the other four Deterministic.
 9. **Manage Agents.** The add/edit form has a required Mode select (Deterministic / Creative) and no temperature input. The agents list shows a Mode column instead of Temp. Picking a brain size no longer pre-fills a temperature.
10. `kimi-k2.6-openrouter` **folds into the table.** The hand-written entry is retired, and its model code becomes the slug `moonshotai/kimi-k2.6`. Per the brief, that slug is Inceptron int4 at 0.43 / 2.45 / 0.12, so its size is `Little`.
11. **Existing agent rows remap once.** A run-once operator migration does three things:
    * Sets each agent's starting mode (item 8), using its brain size before any remap.
    * Moves every OpenRouter agent row to its slug's new size, and `kimi-k2.6-openrouter` rows to `moonshotai/kimi-k2.6`.
    * Lists rows on removed models and leaves them unchanged (Susan: don't worry about production rows on removed models).

**Not in scope:**

* Sunsetting the direct models.
* Adding thinking support to the Anthropic client or DeepSeek-direct.
* Huge / 32-bit.
* Per-task mode: mode lives on the agent (Susan).
* The brief's CTX and UP1D columns. ZDR enforcement. Grouping/sorting of the 98-entry model list.
* Timesheet `model_code`: that is the ledger's SKU column, not the agent's.
* The brief's first line ("add all these models with 'Big' brain, thinking on, temp 1") is superseded by Susan's later comments. It is kept verbatim in the Original brief.

## Component scope

* `src/utils/config.py`: **modified**.
  * The OpenRouter table becomes the brief's 95 rows, with a quantization-to-size builder.
  * New mode constants and a mode-aware resolver.
  * Tiers drop thinking/temperature fields, and each model gains "can think" + payload.
  * The agent repo-JSON columns gain `mode` and lose `temperature`.
  * `kimi-k2.6-openrouter` is retired into the table.
  * The Anthropic default temperatures and dead legacy helpers are removed.
* `data/admin/agent.json`: **modified**. Each row gains `mode` and loses `temperature`.
* `docs/uat-fixtures/AST-756/expected-agent.json`: **modified**. It is the twin of `agent.json` and gets the same change.
* `src/data/database.py`: **modified**. The agent table gains `mode` and drops `temperature` and `model_code`. Writes and repo-JSON apply require mode, the legacy size inference goes, and the public view returns `mode`.
* `src/core/agent.py`: **modified**. Calls take thinking and temperature from the mode-aware route only.
* `src/ui/api/api_admin.py`: **modified**. Agent create/update take `mode` (no `temperature`). The adhoc/workbench route uses the mode-aware route. The models endpoint drops per-size `default_temperature`.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`: **modified**. Adds the Mode select and Mode column, and removes the temperature input, the Temp column and the temperature pre-fill.
* `scripts/migrations/remap_openrouter_agents.py`: **new**. The run-once operator migration (dry-run by default), following the existing `scripts/migrations/` convention.
* Tests and bibles (**modified**, Betty in `qa-child`): `tests/component/utils/test_config.py`, `tests/component/external/test_llm_compat.py`, `tests/component/ui/api/test_api_admin.py`, `tests/component/core/test_agent.py`, `tests/component/core/test_repo_admin_json.py`, `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`, `docs/test-bible/utils/config.md`, `docs/test-bible/external/llm_compat.md`, `docs/test-bible/ui/api/api_admin.md`, `docs/test-bible/core/agent.md`, `docs/test-bible/frontend/pages.md`. Covers the AST-1938 sizes / pin / prices / count, agent `mode` replacing `temperature` and `model_code`, and the Manage Agents form.

`src/external/llm_compat.py` is **not** touched. It already sends either the thinking payload or the thinking-off params plus a temperature, from the tier it is given, and prices by SKU.

## Technical scope

* `src/utils/config.py`:
  * **New quantization-to-size map:** a small constant: int4/fp4 → Little, int8/fp8 → Medium, fp16/bf16 → Big.
  * **Modified OpenRouter table:** replaced by the brief's 95 rows. Each row holds IN / OUT / CACHE from the brief, the host routing slug, the host quantization, the reasoning flag and the host max output. The last three come from `GET https://openrouter.ai/api/v1/models/<slug>/endpoints`, matched on the brief's PROVIDER **and** QUANT (AST-1938's snapshot method). The 12 removed slugs leave the table. The row layout and field names are `plan-child`'s call.
  * **Modified builder:** each row becomes one model with one brain size, the row's quantization size. It records whether the host can think, its max output, and `request_extras` pinning `provider.order = [host]`, `allow_fallbacks = false` and `quantizations = [row quantization]`. The uniform quantization pin replaces the one-off `gemma-4-31b-it` constant (DeepInfra hosts that slug at two quantizations).
  * **New mode constants:** Deterministic = thinking off, temperature 0.2, OpenRouter output cap 16k. Creative = thinking on when the model can think, otherwise temperature 0.6, OpenRouter output cap 32k.
  * **Modified catalog shape:** brain-size tiers no longer carry `thinking`, `thinking_params` or `default_temperature`. Each model carries one "can think" flag plus its thinking payload: OpenRouter per host (adaptive), `kimi-k2.6` yes (`enabled`), `claude` and `deepseek-v4` no. SKUs, pricing, `default_max_tokens` and `max_tokens_floor` on direct models are unchanged.
  * **Modified resolver:** the model + brain-size resolver also takes the agent's mode and returns the tier a call uses. That tier's thinking flag and temperature come from the mode. It carries the thinking flag and payload under the keys `llm_compat` already reads, which is why `llm_compat.py` needs no change. On OpenRouter its output default comes from the mode cap (capped at host max); on direct models it is the size's existing default. Validation helpers reject an unknown mode.
  * **Modified repo-JSON config:** the agent table's column list gains `mode` and drops `temperature`.
  * **Removed:** the `kimi-k2.6-openrouter` entry (`moonshotai/kimi-k2.6` is built from its brief row), the `default_temperature` keys in `AGENT_CONFIG`, and the dead helpers `brain_setting_for_anthropic_agent_key` and `admin_brain_setting_catalog` (no callers; their route no longer exists). Also `infer_brain_setting_from_legacy_model_code`, whose only caller is the legacy fallback removed from `database.py`.
* `data/admin/agent.json` and `docs/uat-fixtures/AST-756/expected-agent.json`: each agent row gains `mode` (per Functional scope item 8) and loses `temperature`. No other field changes.
* `src/data/database.py`:
  * **Schema:** the modified agent schema-ensure adds a nullable `mode` TEXT column and drops the `temperature` and `model_code` columns when present (DDL only, per AST-1497).
  * **Writes:** the modified agent save, update allow-list, repo-JSON apply and repo-JSON validation write `mode`, reject a missing or unknown mode, and no longer accept `temperature`.
  * **Reads:** the modified brain-size coercion stops falling back to legacy `model_code` inference. The modified agent public view returns `mode` and no longer emits `model_code` (`resolved_model_key` stays). The table docstring is updated.
* `src/core/agent.py`: the modified LLM route helper passes the agent's mode to the resolver. The modified call path takes temperature and thinking from the resolved tier only; there is no agent-row temperature. The craft-rubric thinking-off guard and the max-tokens floors still apply on top, unchanged.
* `src/ui/api/api_admin.py`:
  * The modified agent create/update routes take a required `mode`, return 400 on a missing or unknown one, and no longer accept `temperature`.
  * The modified adhoc/workbench resolver passes mode through and takes temperature from the resolved tier.
  * The modified `GET /agents/models` response drops per-size `default_temperature`.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`: the modified add/edit form gains a required Mode select, sent as `mode`, and drops the temperature input and the temperature half of the size pre-fill. The modified agents list swaps the Temp column for a Mode column. The `Agent` / model types drop `temperature`, `model_code` and `default_temperature`.
* `scripts/migrations/remap_openrouter_agents.py`: a new CLI. By default it is a dry run that prints each planned change and each agent row on a removed model. With `--apply` it does two things:
  * Sets `mode` on every agent row that has none (Big → Creative, else Deterministic, judged on the row's brain size before remap).
  * Rewrites OpenRouter rows' `brain_setting` to the slug's new size, and moves `kimi-k2.6-openrouter` rows to `moonshotai/kimi-k2.6` / `Little`.

  Removed-model and direct-model rows keep their model and size. The old→new slug map is a literal snapshot table inside the script. It runs **once per environment, right after deploy**, and the docstring says so (same convention as `retarget_artifact_chain_trigger_state.py`).

## Architectural definition

* **Patterns to reuse:** `no established pattern applies`. No active `patt.*` covers the LLM catalog, agent settings or operator migrations. The work reshapes AST-1938's OpenRouter table + builder, changes the agent row and repo-JSON column config the same way `model_id` / `brain_setting` were added ([AST-1878](https://linear.app/astralcareermatch/issue/AST-1878)), and follows the repo's existing `scripts/migrations/` convention (not a registered pattern id).
* **New patterns proposed:** `none`.
* **Applicable statutes:**
  * `stat.logging.debug` ([file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)): every request now carries mode-derived thinking/temperature, and OpenRouter requests carry the quantization pin. The compat client's existing ungated call/response debug lines must keep logging the full body. No `debug=` parameter is added in `agent.py`, `api_admin.py`, `database.py` or `config.py`.
  * `stat.logging.info.api` ([file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>)): applies to the modified agent create/update routes in `api_admin.py`. Any completing-route info line keeps that statute's shape with `mode` in place of `temperature`. No new ad-hoc info logging.
  * No other active statute applies. The migration script lives under `scripts/`, outside every active statute's `src/**` paths. The `config.*` rules are still draft and are not cited as law; every slug, host, price and mode value still lives only in `config.py` (AC 12).

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
 5. **Mode drives every call on the wire.**
    * **Check (component tests, stubbed clients):**
      * OpenRouter:
        * Creative on `z-ai/glm-4.6` sends the adaptive thinking payload and no `temperature`.
        * Creative on `microsoft/phi-4` sends thinking-off params and `temperature == 0.6`.
        * Deterministic on `z-ai/glm-4.6` sends thinking-off params and `temperature == 0.2`.
        * All three carry the AC 4 pin.
      * Direct:
        * Creative on `kimi-k2.6` Little sends `{"thinking": {"type": "enabled"}}` and no `temperature`.
        * Deterministic on `kimi-k2.6` Big sends thinking-off params and `temperature == 0.2`.
        * Creative on `deepseek-v4` Big sends thinking-off params and `temperature == 0.6` with `max_tokens >= 384000`.
        * Deterministic on `claude` Medium sends `temperature == 0.2` to the Anthropic client with SKU `claude-sonnet-4-6`.
    * **Fails if:** any call's thinking, temperature, SKU or floor differs.
 6. **Output default by mode on OpenRouter.**
    * **Check:** the resolved OpenRouter tier's `default_max_tokens == min(16000 Deterministic | 32000 Creative, host max output)`. Spot checks: `gryphe/mythomax-l2-13b` Creative → 3686, `qwen/qwen3.5-27b` Creative → 32000, `qwen/qwen3.5-27b` Deterministic → 16000.
    * **Fails if:** any violator prints.
 7. **Direct models persist; no stray thinking/temperature settings.**
    * **Check:**
      * For `claude`, `kimi-k2.6` and `deepseek-v4`, model ids, brain-size tuples, tier SKUs, `default_max_tokens`, `max_tokens_floor` and pricing rows equal pre-epic `origin/dev` values.
      * No stored tier in `LLM_MODEL_CONFIG` has a `thinking`, `thinking_params` or `default_temperature` key. These appear only on the tier the resolver returns for a call.
      * `rg -n "default_temperature|brain_setting_for_anthropic_agent_key|admin_brain_setting_catalog|infer_brain_setting_from_legacy_model_code" src/` returns nothing.
      * `rg -n "temperature" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing.
    * **Fails if:** any direct value differs, a stored tier keeps one of those keys, or any hit.
 8. **Agent row: mode in; temperature and model_code out.**
    * **Check (component tests):**
      * After schema-ensure on a DB that had both columns, `PRAGMA table_info(agent)` lists `mode` and neither `temperature` nor `model_code`.
      * `PUT /api/admin/agents/<id>` with `mode: "Creative"` → re-GET returns `"Creative"` and has no `temperature` or `model_code` key.
      * Omitting `mode`, or sending `"Wild"`, → 400.
      * Reverting the agent table from `data/admin/agent.json` succeeds.
    * **Fails if:** a column or key survives, an invalid mode saves, a valid one doesn't persist, or revert fails.
 9. **Starting modes in the seed.**
    * **Check:** in `data/admin/agent.json`, exactly `ats_expert_atlas`, `content_writer_judith` and `principal_recruiter_estelle` are `Creative` and the other four are `Deterministic`. No row has `temperature`. `docs/uat-fixtures/AST-756/expected-agent.json` matches field-for-field.
    * **Fails if:** any row differs or the fixture drifts.
10. **Manage Agents.**
    * **Check (frontend component test):**
      * The edit form renders a Mode select with exactly Deterministic / Creative and sends `mode` on save, with no `temperature` in the body.
      * No temperature input renders for any model.
      * The list has a Mode column and no Temp column.
    * **Fails if:** any of those is missing or a temperature control remains.
11. `kimi-k2.6-openrouter` **retired; catalog boots.**
    * **Check:**
      * `"kimi-k2.6-openrouter" not in LLM_MODEL_CONFIG` and `rg -n "kimi-k2.6-openrouter" src/` returns nothing.
      * `validate_llm_provider_environment()` returns without raising.
      * `GET /api/admin/agents/models` returns **98** ids.
    * **Fails if:** any hit, `v()` raises, or the count isn't 98.
12. **No slug or mode literal outside config.**
    * **Check:**
      * `rg -n "apodex/|bytedance/ui-tars|ibm-granite/|inclusionai/|meta/muse|microsoft/|minimax/|sao10k/l3|thedrummer/|z-ai/glm-4|moonshotai/kimi-k2\.[57]" src/ --glob '!src/utils/config.py'` returns nothing.
      * `rg -n "0\.6\b|0\.2\b" src/core/agent.py src/ui/api/api_admin.py src/data/database.py` returns no mode temperature literal.
    * **Fails if:** any hit.
13. **Migration remaps once.**
    * **Check (component test on a temp DB, rows without** `mode`**):** seed `(qwen/qwen3-32b, Little)`, `(qwen/qwen3-32b, Medium)`, `(gryphe/mythomax-l2-13b, Little)`, `(kimi-k2.6-openrouter, Little)`, `(kimi-k2.6-openrouter, Big)`, `(morph/morph-v3-large, Little)`, `(claude, Big)` and `(deepseek-v4, Medium)`.
      * A dry run writes nothing and lists `morph/morph-v3-large` as removed.
      * `--apply` yields:
        * `(qwen/qwen3-32b, Medium, Deterministic)` for both qwen rows
        * `(gryphe/mythomax-l2-13b, Big, Deterministic)`
        * `(moonshotai/kimi-k2.6, Little, Deterministic)` and `(moonshotai/kimi-k2.6, Little, Creative)`
        * `(morph/morph-v3-large, Little, Deterministic)`
        * `(claude, Big, Creative)` and `(deepseek-v4, Medium, Deterministic)`
      * Every non-removed row then passes model + size + mode validation.
    * **Fails if:** the dry run writes, any row maps differently, or a non-removed row fails validation.

## Open questions

None.

## Proposed child tickets

#### 1!!: **Catalog by quantization, mode-aware resolver, settings cleanup - Katherine**

Replaces the OpenRouter catalog with the brief's 95 slugs, each with one quantization brain size, host pin and brief price, and retires `kimi-k2.6-openrouter` into the table. Adds the Deterministic / Creative mode and a resolver that turns model + size + mode into the tier a call uses. Strips the old per-size thinking/temperature fields, the Anthropic default temperatures and the dead legacy helpers. Updates the agent repo-JSON columns (`mode` in, `temperature` out) and the seed and fixture files. Does **not** touch the database, call paths, admin routes or UI (#2, #3) or the migration (#4). Katherine built AST-1938's table and builder.
**Citations:** `stat.logging.debug` (mode-derived thinking/temperature and the pin stay visible in the compat client's existing ungated debug body logging; no `debug=` parameter).
**Scope:**

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

Estimate: 5

#### 2!: **Agent mode persisted and applied; temperature and model_code retired from the agent row - Hedy**

Adds `mode` to the agent table and drops `temperature` and the duplicate `model_code`. Every agent write and repo-JSON apply requires a valid mode. Agent calls and the admin workbench take thinking and temperature only from #1's mode-aware route. After #1. Does **not** touch the UI (#3) or migrate rows (#4).
**Citations:** `stat.logging.debug` (no `debug=` parameter on the touched call paths); `stat.logging.info.api` (agent create/update routes keep the statute's info shape with `mode` in place of `temperature`).
**Scope:**

* `src/data/database.py` (**modified**):
  * **Schema:** the modified agent schema-ensure adds a nullable `mode` TEXT column and drops the `temperature` and `model_code` columns when present (DDL only, per AST-1497).
  * **Writes:** the modified agent save, update allow-list, repo-JSON apply and repo-JSON validation write `mode`, reject a missing or unknown mode, and no longer accept `temperature`.
  * **Reads:** the modified brain-size coercion stops falling back to legacy `model_code` inference. The modified agent public view returns `mode` and no longer emits `model_code` (`resolved_model_key` stays). The table docstring is updated.
* `src/core/agent.py` (**modified**): the modified LLM route helper passes the agent's mode to the resolver. The modified call path takes temperature and thinking from the resolved tier only; there is no agent-row temperature. The craft-rubric thinking-off guard and the max-tokens floors still apply on top, unchanged.
* `src/ui/api/api_admin.py` (**modified**):
  * The modified agent create/update routes take a required `mode`, return 400 on a missing or unknown one, and no longer accept `temperature`.
  * The modified adhoc/workbench resolver passes mode through and takes temperature from the resolved tier.
  * The modified `GET /agents/models` response drops per-size `default_temperature`.
* `tests/component/core/test_agent.py`, `tests/component/ui/api/test_api_admin.py`, `tests/component/core/test_repo_admin_json.py`, `docs/test-bible/core/agent.md`, `docs/test-bible/ui/api/api_admin.md` (**modified**, Betty in `qa-child`).

Estimate: 5

#### 3: **Mode select in Manage Agents; temperature controls removed - Ada**

Adds the required Mode select to the add/edit agent form and swaps the list's Temp column for Mode. Removes the temperature input and the temperature pre-fill on size change. After #2. Does **not** touch the backend.
**Citations:** none. Frontend-only change, and no active pattern or statute governs this page.
**Scope:**

* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` (**modified**): the modified add/edit form gains a required Mode select, sent as `mode`, and drops the temperature input and the temperature half of the size pre-fill. The modified agents list swaps the Temp column for a Mode column. The `Agent` / model types drop `temperature`, `model_code` and `default_temperature`.
* `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`, `docs/test-bible/frontend/pages.md` (**modified**, Betty in `qa-child`).

Estimate: 2

#### 4: **Run-once agent remap: starting modes, new sizes, Kimi fold - Katherine**

Ships the operator migration that gives every existing agent its starting mode and moves OpenRouter agent rows to their new sizes, including `kimi-k2.6-openrouter` → `moonshotai/kimi-k2.6`. Rows on removed models are only listed. After #1 and #2: the `mode` column must exist, and remapped rows must pass mode validation. Does **not** touch product code.
**Citations:** none. The script lives under `scripts/`, outside every active statute's `src/**` paths, and no active pattern covers operator migrations.
**Scope:**

* `scripts/migrations/remap_openrouter_agents.py` (**new**): a new CLI. By default it is a dry run that prints each planned change and each agent row on a removed model. With `--apply` it does two things:
  * Sets `mode` on every agent row that has none (Big → Creative, else Deterministic, judged on the row's brain size before remap).
  * Rewrites OpenRouter rows' `brain_setting` to the slug's new size, and moves `kimi-k2.6-openrouter` rows to `moonshotai/kimi-k2.6` / `Little`.

  Removed-model and direct-model rows keep their model and size. The old→new slug map is a literal snapshot table inside the script. It runs **once per environment, right after deploy**, and the docstring says so (same convention as `retarget_artifact_chain_trigger_state.py`).

Estimate: 2

**New patterns:** none.

**Monolith check:** 11 functional items, 4 children.

* **#1:** items 1–3, 4–5's constants, 7's catalog side, 8's seed file and 10.
* **#2:** 4–6 at runtime and 7's agent-row side.
* **#3:** item 9.
* **#4:** item 11 and 8's live rows.

**Scope partition check:**

* **#1:** `config.py`, `agent.json`, the AST-756 fixture, and config/compat tests.
* **#2:** `database.py`, `agent.py`, `api_admin.py`, and their tests.
* **#3:** `AdminAgentPrompts.tsx` and its test/bible.
* **#4:** `remap_openrouter_agents.py`.
* No file is claimed twice and none is unclaimed.

---

## Original brief

Please add all these models with "Big" brain, thinking on, temp 1.

```
MODEL                                      PROVIDER       QUANT  IN$/M  OUT$/M  CACHE$/M  CTX      UP1D
apodex/apodex-1.1-mini:free                Novita         bf16   0      0       0         262144   99
bytedance-seed/seed-1.6                    Seed           fp8    0.25   2       0         262144   100
bytedance-seed/seed-1.6-flash              Seed           fp8    0.08   0.3     0         262144   99
bytedance-seed/seed-2-1-turbo              Seed           fp8    0.5    2.5     0         262144   99
bytedance-seed/seed-2.0-code               Seed           fp8    0.5    3       0         262144   100
bytedance-seed/seed-2.0-lite               Seed           fp8    0.25   2       0         262144   99
bytedance-seed/seed-2.0-mini               Seed           fp8    0.1    0.4     0         262144   100
bytedance/ui-tars-1.5-7b                   Parasail       bf16   0.1    0.2     0.1       128000   100
deepseek/deepseek-chat                     DeepInfra      fp4    0.32   0.89    0         163840   95
deepseek/deepseek-chat-v3-0324             SiliconFlow    fp8    0.25   1       0         163840   99
deepseek/deepseek-chat-v3.1                DeepInfra      fp4    0.25   0.95    0.13      163840   99
deepseek/deepseek-r1-0528                  SiliconFlow    fp8    0.5    2.18    0         163840   99
deepseek/deepseek-v3.1-terminus            SiliconFlow    fp8    0.27   1       0         163840   98
deepseek/deepseek-v3.2                     SiliconFlow    fp8    0.26   0.42    0.14      163840   96
deepseek/deepseek-v3.2-exp                 SiliconFlow    fp8    0.27   0.41    0         163840   99
deepseek/deepseek-v4-flash                 OpenInference  fp8    0      1.22    0         1048576  99
deepseek/deepseek-v4-flash-0731            OpenInference  fp8    0.01   0.95    0         1048576  99
deepseek/deepseek-v4-flash-vision-exp      DeepInfra      fp8    0.22   0.65    0.01      1048576  99
deepseek/deepseek-v4.1-flash               OpenInference  fp4    0.02   0.68    0         1048576  98
google/gemma-2-27b-it                      NextBit        int4   0.65   0.65    0         8192     100
google/gemma-3-12b-it                      DeepInfra      bf16   0.05   0.15    0         131072   99
google/gemma-3-27b-it                      Parasail       fp8    0.08   0.45    0.04      131072   99
google/gemma-3-4b-it                       DeepInfra      bf16   0.05   0.1     0         131072   99
google/gemma-4-26b-a4b-it                  DeepInfra      fp8    0.07   0.34    0         262144   99
google/gemma-4-31b-it                      DeepInfra      fp4    0.09   0.34    0.05      262144   99
gryphe/mythomax-l2-13b                     Parasail       fp16   0.08   0.11    0         4096     99
ibm-granite/granite-4.2-8b                 CoreWeave      bf16   0.1    0.15    0.05      131072   100
inclusionai/ling-3.0-flash-fin             DeepInfra      fp4    0.06   0.18    0.01      262144   100
inclusionai/ling-3.0-flash-vl              DeepInfra      fp16   0.06   0.18    0.01      131072   99
meta-llama/llama-3.1-70b-instruct          DeepInfra      fp8    0.4    0.4     0         131072   99
meta-llama/llama-3.1-8b-instruct           CoreWeave      bf16   0.22   0.22    0.22      131072   100
meta-llama/llama-3.2-3b-instruct           Parasail       bf16   0.05   0.33    0         131072   99
meta-llama/llama-3.3-70b-instruct          DeepInfra      fp8    0.1    0.32    0         131072   98
meta-llama/llama-4-maverick                Novita         fp8    0.27   0.85    0         1048576  99
meta-llama/llama-4-scout                   DeepInfra      fp8    0.1    0.3     0         327680   99
meta/muse-glimmer-30b                      DeepInfra      bf16   0.3    1.2     0.04      131072   99
microsoft/phi-4                            DeepInfra      bf16   0.07   0.14    0         16384    100
minimax/minimax-m3                         CoreWeave      fp4    0.23   0.96    0.05      262144   98
mistralai/mistral-nemo                     DeepInfra      fp8    0.02   0.03    0         131072   99
mistralai/mistral-small-24b-instruct-2501  DeepInfra      fp8    0.05   0.08    0         32768    99
mistralai/mistral-small-3.2-24b-instruct   DeepInfra      fp8    0.08   0.2     0         128000   99
moonshotai/kimi-k2-0905                    Novita         fp8    0.6    2.5     0         262144   100
moonshotai/kimi-k2-thinking                Novita         bf16   0.6    2.5     0.15      262144   99
moonshotai/kimi-k2.5                       SiliconFlow    int4   0.45   2.25    0.07      262144   99
moonshotai/kimi-k2.6                       Inceptron      int4   0.43   2.45    0.12      262144   99
moonshotai/kimi-k2.7-code                  Inceptron      int4   0.67   3.35    0.18      262144   99
nousresearch/hermes-3-llama-3.1-70b        DeepInfra      fp8    0.7    0.7     0         131072   100
nvidia/nemotron-3-nano-30b-a3b             Crusoe         fp8    0.05   0.2     0.03      262144   99
nvidia/nemotron-3-super-120b-a12b          DekaLLM        fp8    0.08   0.45    0         262144   98
nvidia/nemotron-3-ultra-550b-a55b          DeepInfra      fp4    0.5    2.2     0.1       262144   99
nvidia/nemotron-3.5-lightning              DeepInfra      bf16   0.06   0.16    0.03      262144   99
openai/gpt-oss-120b                        DekaLLM        bf16   0.03   0.18    0.03      131072   99
openai/gpt-oss-20b                         AkashML        fp4    0.02   0.1     0         131072   99
qwen/qwen-2.5-72b-instruct                 DeepInfra      fp8    0.36   0.4     0         32768    97
qwen/qwen3-14b                             NextBit        int4   0.1    0.22    0         40960    99
qwen/qwen3-235b-a22b-2507                  Novita         fp8    0.09   0.58    0         131072   98
qwen/qwen3-30b-a3b                         DeepInfra      fp8    0.12   0.5     0         40960    99
qwen/qwen3-30b-a3b-instruct-2507           SiliconFlow    fp8    0.09   0.3     0         262144   99
qwen/qwen3-32b                             DeepInfra      fp8    0.08   0.28    0         40960    99
qwen/qwen3-coder                           DeepInfra      fp4    0.3    1       0.1       262144   97
qwen/qwen3-coder-30b-a3b-instruct          SiliconFlow    fp8    0.07   0.28    0         262144   98
qwen/qwen3-coder-next                      Parasail       bf16   0.12   0.8     0.07      262144   99
qwen/qwen3-next-80b-a3b-instruct           DeepInfra      fp8    0.09   1.1     0         262144   99
qwen/qwen3-vl-235b-a22b-instruct           DeepInfra      fp8    0.2    0.88    0.11      262144   97
qwen/qwen3-vl-30b-a3b-instruct             DeepInfra      fp8    0.15   0.6     0         262144   99
qwen/qwen3-vl-30b-a3b-thinking             SiliconFlow    fp8    0.29   1       0         262144   97
qwen/qwen3-vl-8b-instruct                  Parasail       bf16   0.25   0.75    0.12      262144   97
qwen/qwen3.5-27b                           SiliconFlow    fp8    0.25   2       0         262144   99
qwen/qwen3.5-35b-a3b                       DeepInfra      fp8    0.14   1       0.05      262144   99
qwen/qwen3.5-397b-a17b                     DeepInfra      fp8    0.45   3       0.22      262144   96
qwen/qwen3.5-9b                            DeepInfra      bf16   0.1    0.15    0         262144   99
qwen/qwen3.6-27b                           SiliconFlow    fp8    0.3    3.2     0         262144   97
qwen/qwen3.6-35b-a3b                       DeepInfra      fp8    0.1    0.95    0.1       262144   98
qwen/qwen3.8-27b                           Ionstream      fp8    0.09   2.2     0.09      262144   97
qwen/qwen3.8-27b:free                      ModelRun       fp4    0      0       0         262144   97
sao10k/l3-lunaris-8b                       Parasail       bf16   0.04   0.05    0         8192     99
sao10k/l3.3-euryale-70b                    NextBit        bf16   0.65   0.75    0         131072   96
stepfun/step-3.7-flash                     Novita         fp8    0.2    1.15    0.04      262144   99
tencent/hunyuan-a13b-instruct              SiliconFlow    fp8    0.14   0.57    0         131072   100
tencent/hy-mt2-30b-a3b                     Tencent        fp8    0.07   0.3     0         8192     100
tencent/hy-mt2-7b                          Tencent        fp8    0.07   0.3     0         8192     100
tencent/hy3                                DeepInfra      fp4    0.13   0.53    0.03      262144   99
thedrummer/cydonia-24b-v4.1                Parasail       bf16   0.3    0.5     0.15      131072   99
thedrummer/skyfall-36b-v2                  Parasail       fp8    0.55   0.8     0.25      32768    100
thedrummer/unslopnemo-12b                  Parasail       bf16   0.4    0.4     0         1024000  99
undi95/remm-slerp-l2-13b                   Mancer 2       fp8    0.35   0.65    0         6144     99
xiaomi/mimo-v2.5                           Venice         fp8    0.4    2       0.08      1000000  97
xiaomi/mimo-v2.6-flash                     InferenceNet   fp8    0.12   0.28    0.01      1048576  99
xiaomi/mimo-v2.6-pro                       DeepInfra      fp8    0.43   0.87    0         1048576  99
z-ai/glm-4.6                               Venice         fp4    0.43   1.75    0.08      198000   99
z-ai/glm-4.7                               DeepInfra      fp4    0.4    1.75    0.08      202752   97
z-ai/glm-4.7-flash                         Venice         fp8    0.06   0.4     0.01      128000   99
z-ai/glm-5.2                               Morph          fp8    0.17   3.07    0.2       1048576  98
z-ai/glm-5.3                               Morph          fp8    0.13   2.99    0.15      1048576  98
z-ai/glm-5.3-flash                         OpenInference  fp4    0.03   0.93    0.01      1048576  98
```

### Comments

#### chuckles — 2026-10-03T03:26:10.375Z
AST-1950 gated on AST-1952: Susan picks validator fix (A) or one-time merge override (B) for the false 'missing test' block.

#### chuckles — 2026-10-03T03:23:48.705Z
AST-1950 REVIEW — merge-child blocked: validate-sub-log false positive (test(AST-1950) already on ftr via AST-1949 merge-tests); recalling Betty on tests-line hygiene.

#### chuckles — 2026-10-03T01:56:46.719Z
AST-1947 REVIEW — gated on AST-1951: Susan picks A/B/C for the AST-1947/AST-1948 sequencing gap; AST-1948, AST-1949 and AST-1950 wait behind it.

#### chuckles — 2026-10-03T01:20:54.876Z
@susan Two questions are still open and block a clean definition. Reply "draft is fine" to accept both draft answers:

1. **Mode on direct models (Claude / Kimi-direct / DeepSeek):** draft = mode is stored on every agent but **does nothing** on direct models, so they run exactly as today. The alternative is that mode applies there too, which turns thinking on for Creative DeepSeek/Claude agents.
2. **Agent temperature on OpenRouter agents:** draft = mode **owns** temperature (0.2 / 0.6), so the agent's own temperature is ignored and hidden for OpenRouter models but still used for direct models. The alternative is that an explicit agent temperature overrides the mode.

#### chuckles — 2026-10-03T00:49:15.806Z
@susan

1. **Mode on direct models.** "Run exactly as today" and "mode on every agent" collide on Claude / Kimi-direct / DeepSeek. For example, `content_writer_judith` (Kimi-direct Big) starts Creative, and Creative would turn thinking on for DeepSeek Big and Claude, which run thinking-off today. The draft stores mode on every agent but has it **do nothing** on direct models until they're sunset. Confirm, or should mode apply to direct models too (changing how they run)?
2. **Agent temperature field on OpenRouter agents.** Your Deterministic / Creative rules fix the temperature (0.2 / 0.6). Today the seed agents carry explicit temperatures (0.3, and 0 on `principal_recruiter_estelle`) that would otherwise override the mode. The draft has mode **own** temperature on OpenRouter models: the agent's temperature is ignored there and its input is hidden in Manage Agents, but it is still used for direct models. Confirm, or should an explicit agent temperature still override the mode?

#### susan — 2026-10-03T00:46:36.280Z
1. Actually, no.  Let's set it at the agent record, still.  Our agents are cleanly organized that this won't cause confusion.
2. Two settings: Deterministic (not-thinking AND/OR temp 0.2) and Creative (thinking AND/OR temp 0.6 if thinking isn't supported)
3. All Big brain tasks are Creative, all others are Deterministic (for now)

#### chuckles — 2026-10-03T00:34:58.745Z
[check-linear] answered: yes, this fits in AST-1946. Each task (`agent_task` row) gets a required **mode**: **Deterministic** (temperature 0.2) or **Creative** (temperature 0.6), set in Manage Tasks. Today temperature lives only on the agent row plus the brain-size default, and `agent_task` has no temperature or mode field, so this adds one.

@susan The current definition doesn't include this yet, and the ticket is at **Todo**. Please move it back to **Discussion** and assign Chuckles so I redefine it before anyone assigns it for dispatch. Three calls I'll need:

1. **Precedence:** does task mode **replace** temperature entirely (retire the agent row's temperature field and the 1.0 brain-size default), or only apply when the agent row leaves temperature blank?
2. **Thinking sizes:** the compat client never sends a temperature when thinking is on (the vendors require their own value there), so mode has no effect on "(thinking)" sizes or on Kimi-direct Big. Is that OK, or should picking a mode force a thinking-off size?
3. **Existing tasks:** what mode should the current tasks start with: all **Deterministic**, all **Creative**, or a per-task list from you?

#### susan — 2026-10-03T00:34:20.412Z
@chuckles Please include in this epic the requirement to assign a mode for each task of either "Deterministic" or "Creative", where Deterministic means temp = 0.2, and Creative means temp = 0.6

#### susan — 2026-10-03T00:30:12.026Z
Don't worry about production models.  This list will completely replace those OpenRouter models.  Please persist the anthropic, deepseek and kimi direct models, and make sure they still run as they do today.  These are only for OpenRouter.

#### chuckles — 2026-10-03T00:27:28.478Z
@susan

1. **Agent rows on the 12 removed models.** If any agent in production points at one of them (e.g. `moonshotai/kimi-k3`, `z-ai/glm-5.1`), it can't be remapped automatically, because there is no same-model host in the new set. Which do you want?
   * **(a) Draft.** The migration lists those agents and leaves them. Manage Agents still shows them, with no model, so you can re-pick one. Until then their calls fail with "Unknown LLM model".
   * **(b) Keep the 12 in the catalog** at Medium on their current fp8 host until no agent uses them.
   * **(c) Name a fallback model** the migration moves them to.

#### susan — 2026-10-03T00:25:00.445Z
I've updated the original set for ALL the models to support, including 4, 8 and 16 bit.  Those are Little, Medium, and Big brains (skip Huge, I thought I saw a 32 in the list, but it was later filtered out.)

#### chuckles — 2026-10-02T23:15:30.397Z
@susan

1. **Hosts for the sizes your briefs don't name.** AST-1937 named the 8-bit hosts and this brief names the 16-bit ones. Nothing names a 4-bit or 32-bit host. On OpenRouter today, 26 of the 106 slugs have a 4-bit host, 6 of this brief's new slugs also have an 8-bit host, 7 AST-1937 slugs also have a 16-bit host, and none has a 32-bit host. Which do you want?
   * **(a) Briefs only (draft).** Little / Huge exist as sizes but no model offers them until you send a brief naming their hosts.
   * **(b) Auto-fill those 39 slots.** For each, take the cheapest OpenRouter endpoint at that quantization from the snapshot, priced at its live rate.
2. **Drop the two `voxtral` slugs?** They are audio-transcription only, with max output 0. The draft leaves them out.
3. **Big hosts' cache price and the thinking output cap.** This brief has no CACHE column, so the 16-bit hosts' cache read is priced 0 (it under-counts if a host bills cache reads). "(thinking)" sizes default to 32,000 output tokens, capped at the host's max. Some 16-bit hosts allow far more (e.g. `deepseek/deepseek-v4-flash-0731` on Morph: 943,718). Keep both?

#### chuckles — 2026-10-02T23:12:04.673Z
[check-linear] answered: locked in. Existing OpenRouter agent rows (fp8 hosts) remap to Medium: Little → `Medium`, Medium → `Medium (thinking)`. **Huge** (32-bit) ships now as a real size, plus `Huge (thinking)` where the host supports reasoning. With these, every open question in this thread is answered.

Discussion — to have me rewrite the definition around the quantization-as-brain-size refactor, assign to Chuckles (@susan)

#### susan — 2026-10-02T23:10:53.835Z
@chuckles Also, yes, remap to medium brain for the eight bit models, and add the huge size for 32.

#### chuckles — 2026-10-02T22:26:08.014Z
[check-linear] answered: agreed, thinking folds into the brain size. On OpenRouter codes, each quantization size comes in up to two options: plain (thinking off) and **"(thinking)"** (thinking on, adaptive payload). The list runs `Little`, `Little (thinking)`, `Medium`, `Medium (thinking)`, `Big`, `Big (thinking)`, `Huge`, `Huge (thinking)`. A model code offers a size only if it has a host at that quantization. It offers the "(thinking)" variant only if that host supports reasoning. So there's no per-model toggle to manage; the picker shows only valid options.

@susan Two left before I rewrite the definition:
1. **Existing OpenRouter agent rows** (all on fp8 hosts today): remap automatically, i.e. Little → `Medium` and Medium → `Medium (thinking)`?
2. **Huge (32-bit):** ship it now (1 slug has a host today), or define it and leave it empty until more hosts exist?

#### susan — 2026-10-02T22:25:46.508Z
Also, yes, remap to medium brain for the eight bit models, and add the huge size for 32. @Chuckles

#### susan — 2026-10-02T22:25:00.507Z
@chuckles let's just extend the rain sizes to include a parenthetical for thinking or nothing if thinking would be false so that we don't have to manage all the little fiddly flips and switches for every single model.

#### chuckles — 2026-10-02T22:22:50.952Z
[check-linear] answered: the direct vendors can't take a quantization setting, so they stay as they are. None of the direct APIs we call (Anthropic, Moonshot/Kimi, DeepSeek) has a quantization parameter; each serves its model at one fixed precision. So `claude`, `kimi-k2.6` and `deepseek-v4` keep today's brain-size meaning (size picks the SKU / thinking tier). Agent rows on them keep working unchanged, and they sunset later once the new scheme is tested and validated. The quantization-as-brain-size refactor applies only to OpenRouter model codes in this ticket.

@susan Still open before I rewrite the definition:
1. **Thinking on OpenRouter codes:** once size means quantization, thinking needs its own home. Should it be its own agent-row setting (on/off, default per model code), or fixed per model code?
2. **Existing OpenRouter agent rows** are all on fp8 hosts today. Remap them to Medium (8-bit) automatically?
3. **Huge (32-bit):** ship it now (only 1 slug has a 32-bit host today), or define it and leave it empty until hosts exist?

#### susan — 2026-10-02T22:22:03.202Z
@chuckles If we can use quantization settings for the original set of models that we are calling directly, then we should implement that here. If we do not, it is OK we can sunset those later, but I would like them to continue to work until we have the full solution tested and validated.

#### chuckles — 2026-10-02T22:19:34.552Z
[check-linear] answered: got it. Going forward, the **model code** picks the exact version (the SKU on the wire), and the **brain size** only picks the quantization (Little 4 / Medium 8 / Big 16 / Huge 32). I'll redefine AST-1946 as that catalog-wide refactor, including the existing content.

Today a brain-size row carries more than the SKU. It also decides thinking on/off, the thinking payload, the output floor (DeepSeek Big = 384k), and the default temperature / max tokens. For example, `claude` Little/Medium/Big = Haiku/Sonnet/Opus, and `kimi-k2.6` Little = thinking off, Big = thinking on. Once size stops choosing the version, those need a new home. Three calls:

1. **Thinking:** should it become its own agent-row setting (on/off, defaulting per model code), or a fixed property of each model code (e.g. a separate `kimi-k2.6-thinking` code)?
2. **Vendors with no quantization** (Claude, Kimi-direct, DeepSeek-direct): there, should brain size be **hidden / not applicable**, or kept with one fixed value (e.g. Big) so every agent row still has one?
3. **Existing agent rows:** confirm I should remap each row to the explicit model code its current size resolves to today (e.g. `claude` + Big → `claude-opus-4-6`). For OpenRouter rows, the size would then mean the fp8 host they are on now (Medium). Also: ship **Huge** now (only 1 slug has a 32-bit host today), or define it and leave it empty until hosts exist?

#### susan — 2026-10-02T22:18:54.210Z
@chuckles I know we'll need to ref factor the existing content and the meaning for the brain size and I think that's the right move. From now on it will need an explicit model code that specifies the version we're calling and the brain size does not affect what version it is, but rather what the quantization setting should be.

#### chuckles — 2026-10-02T22:17:16.568Z
[check-linear] answered: will do. I'll redefine AST-1946 so that, on OpenRouter models, the brain size is the quantization: **Little = 4-bit, Medium = 8-bit, Big = 16-bit, Huge = 32-bit**. Each size carries its own provider + quantization pin and its own price.

What that refactor brings with it, from the live OpenRouter endpoint lists (108 slugs across AST-1937 + this brief):

* **Coverage is uneven.** 26 slugs have a 4-bit host, 82 have 8-bit, 57 have 16-bit, and **only 1 has 32-bit**. 56 slugs also have at least one host that reports `unknown` quantization, which can't map to a size. A slug offers only the sizes it has a host for. So Huge would be nearly empty today.
* **"Huge" is a new fourth brain size.** It touches the global brain-size list, per-model validation, the admin brain picker, and agent-row validation, not just OpenRouter rows.
* **Price per brain size becomes mandatory** (Open question 1 option (c)): each size is a different host at a different rate. The ledger (`database.py` timesheets/backfill, `cost_calculator.py`) moves from one price per slug to one price per slug + size.
* **Existing agent rows shift meaning.** Any agent on an OpenRouter Little/Medium today is on an fp8 host. Under the new rule fp8 is Medium, so OpenRouter Little rows would move to a 4-bit host or lose their size.
* **Non-OpenRouter models keep the old meaning.** On Claude, Kimi-direct and DeepSeek, brain size still picks a SKU/thinking tier, because those vendors expose no quantization. So the rule is OpenRouter-only.

@susan Two calls before I rewrite the definition:
1. **Huge:** ship it as a real fourth size now (1 slug today), or define the 32-bit rule and leave Huge out until more hosts exist?
2. **OpenRouter Little/Medium rows already on agents (fp8 hosts):** remap them automatically to the new size (fp8 → Medium), or leave existing agent rows alone and apply the new meaning only going forward?

#### susan — 2026-10-02T22:16:21.780Z
@chuckles let's actually ref factor to allow for a quantization to be the brain size of little medium, big and huge for 4,8,16 and 32 respectively.

#### chuckles — 2026-10-02T22:14:53.123Z
[check-linear] answered: yes, quantization can be set at the time of the prompt, but only together with a price per brain size.

* **How it works:** OpenRouter takes a per-request `provider.quantizations` filter (e.g. `["fp4","fp8"]` or `["fp16","bf16"]`). The catalog already sends one: AST-1938 pins `google/gemma-4-31b-it` to `fp8` this way. So each brain size can carry its own quantization in the `request_extras` it already has.
* **Why the slugs duplicate:** all 18 overlapping slugs are pinned today to an **fp8** host (AST-1938's low-quant list). This brief names a **bf16/fp16** host for every one of them. Each of the 18 has both a low-quant and a full-precision endpoint on OpenRouter, so "Little/Medium = 4/8, Big = 16+" is routable for all of them.
* **The catch:** a quantization is a property of an endpoint, and each host serves one. So Big at 16+ means a different host, at a different price, from Little/Medium on the same slug. Example: `moonshotai/kimi-k3` is Morph fp8 at 1.35 / 11.36 vs DeepInfra bf16 at 2.85 / 14.25. The ledger prices one rate per slug today, so this is Open question 1's option **(c)**: pricing moves to per brain size, which touches `database.py` timesheets/backfill and `cost_calculator.py` along with `config.py`.
* **Proposed shape:** each brain size carries its own pin (provider + quantization filter) and its own price. Little/Medium keep their AST-1938 fp8 host. Big uses this brief's 16+ host. The alternative is a quantization filter alone with no provider pin, letting OpenRouter pick any 16+ host. That leaves the price unknown at call time, so the ledger can't be trusted. I don't recommend it.

@susan Want me to redefine AST-1946 around (c) with per-brain-size pin + price? That likely means 2 children: per-size pricing in the ledger first, then the Big rows.

#### susan — 2026-10-02T22:13:51.065Z
@chuckles Check to see if quantization can be set at the time of the prompt, that's why those slugs are duplicate.  If so, let's add that feature to the model listing, so that Big is 16+ and little/medium are 4/8.

#### chuckles — 2026-10-02T22:11:00.780Z
@susan

1. **The 18 slugs already in the catalog are pinned to a different host than this brief names, and most at a different price.** Examples: `moonshotai/kimi-k3` is Morph 1.35 / 11.36 today vs DeepInfra 2.85 / 14.25 here. `qwen/qwen3.8-27b` is IonStream 0.09 / 2.2 vs Cerebras 0.99 / 1.49. `gryphe/mythomax-l2-13b` is Mancer 0.35 / 0.6 vs Parasail 0.08 / 0.11. Pricing is keyed by slug on `openrouter` (`get_sku_pricing` and timesheet `model_code`), so one slug can't carry two prices today. Which do you want?
   * **(a) Re-pin the whole slug to this brief's host and price.** Little/Medium move with it, and Big is added. Smallest change. This is what the draft assumes.
   * **(b) Big rides the existing AST-1938 host and price.** This brief's PROVIDER / IN / OUT are ignored for those 18.
   * **(c) Big keeps its own host and price, separate from Little/Medium.** Needs pricing per brain size instead of per slug. That's a bigger epic touching `database.py` timesheets/backfill and `cost_calculator.py`.
2. **24 of the 48 can't reason on the pinned host**, so "thinking on" has nothing to switch. Examples: `microsoft/phi-4`, `meta-llama/llama-3.3-70b-instruct`, `sao10k/l3.3-euryale-70b`, `qwen/qwen3-coder-next`. Should their Big **(a)** exist with thinking off, i.e. temperature 1 and the bigger output default (draft assumes this), **(b)** be left out so those slugs get no Big, or **(c)** send thinking anyway and accept that the vendor may reject or ignore it?
3. **New slugs: Big only?** The draft gives the 30 new slugs **Big only**. Or should they also get Little (and Medium when reasoning-capable) like the AST-1938 builder does?
4. **Drop the two `voxtral` slugs?** They are audio-transcription models with max output 0, so the messages API can't run them. The draft leaves them out. Also, `meta-llama/llama-guard-4-12b` and `nvidia/nemotron-3.5-content-safety` are safety classifiers, and `bytedance/ui-tars-1.5-7b` caps output at 2,048. They are included as listed. OK?
5. **Big output default and cache price.** The draft uses 32,000 capped at the host's max output, matching Kimi's Big. Some hosts allow far more (e.g. `deepseek/deepseek-v4-flash-0731` on Morph: 943,718). Do you want a higher Big cap? The brief also has no CACHE column, so cache read is priced 0. That under-counts cost for any host that bills cache reads. Is that OK?

---

_Implementation detail may live in git history on `origin/dev`._
