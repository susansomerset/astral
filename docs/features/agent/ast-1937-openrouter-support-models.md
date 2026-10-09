# AST-1937 — OpenRouter Support Models

<!-- linear-archive: AST-1937 archived 2026-10-08 -->

## Linear archive (AST-1937)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1937/openrouter-support-models  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

[AST-1851](https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work) (now on `dev`) gave every agent a catalog **model** + model-scoped **brain size**, with `LLM_MODEL_CONFIG` mapping each model to its server and promising "adding a model is a config edit only." Today the catalog has exactly one OpenRouter model (`kimi-k2.6-openrouter`). Susan wants the full OpenRouter shortlist below selectable in Manage Agents so she can trial models on content generation without each one becoming its own ticket. The outcome: every model in the brief is a pickable catalog model served by the `openrouter` server, pinned to the upstream provider whose price is in the brief so the timesheet ledger is right, with brain sizes and output defaults that won't make the vendor reject the call. Susan also confirmed that the **agent row is the one and only model source**: the task-level model picker added to the Manage Task modal by [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) was requested in error and comes out.

## Functional scope

1. **OpenRouter models in the catalog.** Every model slug in the brief's table (76) is a catalog model on the `openrouter` server, selectable in Manage Agents with no UI or route change (Manage Agents already renders whatever the catalog holds). The vendor SKU sent on the wire is the OpenRouter slug. `moonshotai/kimi-k2.6` is already catalogued as `kimi-k2.6-openrouter`, so that entry is kept rather than duplicated (see item 4).
2. **Brain sizes per model (Susan: Little + Medium; these are intentionally low-quantization models).**
   * Each new model offers **Little** (thinking off).
   * Models that support reasoning also offer **Medium** (thinking on, same adaptive thinking payload as `kimi-k2.6-openrouter`'s thinking tier).
   * No new model offers Big.
   * Which models count as reasoning-capable is decided once at build time from OpenRouter's model listing and written into the table. No runtime lookup.
3. **Pricing from the brief.** Each model's catalog pricing is the brief's IN / OUT / CACHE $ per million tokens (input / output / cache read). Cache write is 0 and cache minimum is 0, matching the existing OpenRouter entry. Timesheet cost for a run on one of these models is computed from these numbers by the existing ledger path.
4. **Upstream provider pin (Susan: definitely pin).**
   * Each model's requests go only to the upstream provider named in the brief's PROVIDER column (OpenRouter `provider` routing, fallbacks off), so the catalog price and limits match what is actually billed.
   * `kimi-k2.6-openrouter` moves to the same treatment: pinned to SiliconFlow and repriced to the brief's 0.77 / 3.4 / 0.14.
   * Its existing Little / Big brain sizes stay as they are, because agent rows may already reference them.
5. **Defaults that fit (Susan: temperature 1 for both; 16k / 32k capped).**
   * **Temperature:** every new brain size defaults to temperature 1.0.
   * **Output budget:** `default_max_tokens` defaults to 16,000 (Little) or 32,000 (Medium), capped at the pinned provider's max output for that model. Five models get a lower Little default: `anthracite-org/magnum-v4-72b`, `gryphe/mythomax-l2-13b`, `tencent/hy-mt2-30b-a3b`, `tencent/hy-mt2-7b`, `undi95/remm-slerp-l2-13b`.
   * Agent rows can still override both.
6. **Agent row is the only model source.** The Manage Task modal no longer offers Model or Brain size selects, and saving a task never writes the agent row. The task list's read-only Model column stays: it already reflects the task's agent. Model and brain size are edited only in Manage Agents.

**Not in scope:**

* The brief's CTX and UP1D columns are not stored. CTX only informs the output defaults in item 5, and uptime is a point-in-time snapshot.
* ZDR enforcement (still future scope per [AST-1851](https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work)).
* Admin UI grouping/sorting of the now \~80-entry model list.
* Re-pointing any existing agent row onto a new model (Susan does that in Manage Agents).

## Component scope

* `src/utils/config.py`: **modified**.
  * **New:** a compact OpenRouter model table (one row per brief slug) plus a small builder that expands each row into `LLM_MODEL_CONFIG` entries in the existing catalog shape.
  * **New:** a per-brain-size request-extras field for the provider pin.
  * **Modified:** the `kimi-k2.6-openrouter` entry gets its pin and new price, and catalog startup validation is extended to cover the new field.
* `src/external/llm_compat.py`: **modified**. Merges the brain size's own request extras into the outbound body next to the server's request extras.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`: **modified**. Removes the Manage Task modal's Model / Brain size selects and the agent write on save.
* `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`: **modified**. The [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) bug-repro cases for the modal selects are retired or inverted (Betty, `qa-child`).
* `docs/test-bible/frontend/pages.md`: **modified**. The [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) Manage Task model-select entries are retired (Betty, `qa-child`).

## Technical scope

* `src/utils/config.py`:
  * **New table:** a new compact OpenRouter model table, keyed by slug, carrying each row's pricing, upstream provider, reasoning flag, and the pinned provider's max output tokens. These are literal snapshot values, with a one-line source/date comment like the existing pricing blocks.
  * **New builder:** a new builder function merges the table into `LLM_MODEL_CONFIG` after the hand-written entries. For each row it creates a model entry: server `openrouter`, label from the slug, Little (thinking off) and, when reasoning-capable, Medium (thinking on), temperature 1.0, capped output defaults, and one pricing row keyed by the slug. It skips any slug already priced on `openrouter` (today only `moonshotai/kimi-k2.6`), so `get_sku_pricing` never sees a duplicate.
  * **Modified tier schema:** each brain-size row gains an optional `request_extras` field (default empty) holding the provider pin.
  * **Modified** `kimi-k2.6-openrouter` **entry:** both of its brain sizes carry the SiliconFlow pin, and its pricing row changes to 0.77 / 3.4 / 0.14 / cache-write 0. Other hand-written entries are unchanged in behaviour.
  * **Modified validation:** `validate_llm_provider_environment` additionally checks that `request_extras` is a dict on every brain size and that every catalog SKU resolves through `get_sku_pricing` without ambiguity.
  * **Table shape is the builder's call:** row layout, field names, provider-slug spelling (OpenRouter's routing ids), and exact function names are `plan-child`'s.
* `src/external/llm_compat.py`: the modified send function builds its `extra_body` from thinking payload + server `request_extras` + tier `request_extras`. The tier's extras win on key collision. The existing ungated call/response debug lines keep logging the full body, so the pin shows up in them.
* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`:
  * **Removed:** the model-catalog fetch, the agent model/brain load, the model-change handler, the Model and Brain size selects with their "Applies to agent" note, and the post-save agent `PUT`. Plus the related state, types, and helper that only those used.
  * **Unchanged:** the Agent select, the task save, and the list's read-only Model column.
* `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`: the modified [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) modal-select cases are removed or replaced by an assertion that the modal has no Model / Brain size select and that save issues no agent `PUT`.
* `docs/test-bible/frontend/pages.md`: the modified Manage Task entries drop the [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) model-select rows.

## Architectural definition

* **Patterns to reuse:** `no established pattern applies`. No active `patt.*` covers the LLM catalog or this admin page: AST-1851's *Model → server catalog routing* was proposed there but never registered as an id. This epic follows that catalog's existing shape (`LLM_SERVER_CONFIG` / `LLM_MODEL_CONFIG` / `resolve_model_brain`) without changing it, beyond the optional tier `request_extras` field.
* **New patterns proposed:** `none`. Generating catalog entries from a compact table is local to this block. It doesn't create a reusable cross-module shape.
* **Applicable statutes:**
  * `stat.logging.debug` ([file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)): applies to the `llm_compat.py` change. The ungated `logger.debug` call/response lines must keep emitting the full request body (now including the tier extras). No `debug=` parameter.
  * No other active statute applies. The `config.config-source-of-truth` / `no-hardcoded-sets` / `ui-config-driven-business-logic` rules are still draft, so they are not cited as law here. The design still keeps every slug inside `config.py` (AC 6).

## Acceptance criteria

All `python -c` checks run from the repo root on the shipped tree.

1. **Every brief slug is catalogued on OpenRouter.**
   * **Check:** a script reading the 76 slugs from this ticket's Original brief table prints `[]` for `[s for s in slugs if not any(t["sku"] == s for m in LLM_MODEL_CONFIG.values() if m["server"] == "openrouter" for t in m["brain_sizes"].values())]`.
   * **Fails if:** any slug is printed.
2. **Pricing matches the brief.**
   * **Check:** for every one of the 76 slugs (including `moonshotai/kimi-k2.6`), `get_sku_pricing(slug, "openrouter")` has `cpm_input` / `cpm_output` / `cpm_cache_read` equal to the brief's IN / OUT / CACHE, and `cpm_cache_write == 0`. The script prints mismatches.
   * **Fails if:** any mismatch is printed, or any lookup raises (unknown or ambiguous SKU).
3. **Brain sizes per model.**
   * **Check:** `model_brain_sizes(<id>)` is `('Little', 'Medium')` for every new model the table flags reasoning-capable and `('Little',)` for every other new model. `model_brain_sizes('kimi-k2.6-openrouter')` stays `('Little', 'Big')`.
   * **Spot checks:** `gryphe/mythomax-l2-13b` → `('Little',)`; `qwen/qwen3-32b` → `('Little', 'Medium')`.
   * **Fails if:** any other tuple appears, or any new model offers `Big`.
4. **Saving an agent respects model-scoped sizes.**
   * **Check (component test):**
     * `PUT /api/admin/agents/<id>` with a new OpenRouter model + `Little` → re-GET returns both.
     * The same request with `gryphe/mythomax-l2-13b` + `Medium` → 400.
     * The same request with `qwen/qwen3-32b` + `Big` → 400.
   * **Fails if:** either 400 case saves, or the valid case doesn't persist.
5. **Provider pin on the wire.**
   * **Check (component test, stubbed** `_get_client`**):**
     * A Little call on `qwen/qwen3-32b` sends `extra_body["provider"]` naming only the brief's provider (DeepInfra) with fallbacks off.
     * A `kimi-k2.6-openrouter` call names only SiliconFlow.
     * A Kimi-direct call and a Claude-catalog call carry no `provider` key.
   * **Fails if:** a pin is missing or wrong on an OpenRouter call, or leaks onto another server.
6. **No slug outside config.**
   * **Check:** `rg -n "qwen/|z-ai/|meta-llama/|mistralai/|bytedance-seed/|nousresearch/|thedrummer/|undi95/|gryphe/|anthracite-org/|sao10k/|tencent/|xiaomi/|stepfun/|morph/|nvidia/|google/gemma|openai/gpt-oss|deepseek/deepseek" src/ --glob '!src/utils/config.py'` returns nothing.
   * **Fails if:** any hit (a per-model literal leaked into code).
7. **Defaults fit.**
   * **Check:** for every new model and brain size, `default_temperature == 1.0` and `default_max_tokens == min(16000 Little | 32000 Medium, <table max output for that slug>)`. The script prints violators.
   * **Fails if:** any violator is printed.
8. **Catalog boots and lists.**
   * **Check:**
     * `python -c "from src.utils.config import validate_llm_provider_environment as v; v()"` returns without raising.
     * `GET /api/admin/agents/models` returns 4 + 75 = 79 model ids.
   * **Fails if:** `v()` raises, or the count isn't 79 (a skipped or duplicated slug).
9. **No task-level model picker.**
   * **Check:**
     * `rg -n "agents/models|editModelId|editBrainSetting|loadAgentModel|Brain size" src/ui/frontend/src/pages/AdminTaskPrompts.tsx` returns nothing.
     * A component test opens the Manage Task modal and finds no Model or Brain size select.
     * Saving the task issues only the task update, with no request to `/api/admin/agents/<id>`.
     * The task list still shows the read-only Model column.
   * **Fails if:** any grep hit, a select renders, an agent `PUT` goes out, or the Model column disappears.

## Open questions

None.

## Proposed child tickets

#### 1: **OpenRouter model shortlist in the catalog - Katherine**

Adds every brief slug as a selectable OpenRouter catalog model, with the brief's pricing, Little / Medium brain sizes, temperature-1 and capped output defaults, and the per-model upstream provider pin carried through the compat client. Also moves `kimi-k2.6-openrouter` onto its SiliconFlow pin and price. Nothing in routing, DB, or the admin UI changes, because they already read the catalog. Does **not** touch the Manage Task modal (#2).
**Citations:** `stat.logging.debug` (the compat client's call/response debug lines keep logging the full body, pin included).
**Scope:**

* `src/utils/config.py` (**modified**):
  * **New table:** a new compact OpenRouter model table, keyed by slug, carrying each row's pricing, upstream provider, reasoning flag, and the pinned provider's max output tokens. These are literal snapshot values, with a one-line source/date comment like the existing pricing blocks.
  * **New builder:** a new builder function merges the table into `LLM_MODEL_CONFIG` after the hand-written entries. For each row it creates a model entry: server `openrouter`, label from the slug, Little (thinking off) and, when reasoning-capable, Medium (thinking on), temperature 1.0, capped output defaults, and one pricing row keyed by the slug. It skips any slug already priced on `openrouter` (today only `moonshotai/kimi-k2.6`), so `get_sku_pricing` never sees a duplicate.
  * **Modified tier schema:** each brain-size row gains an optional `request_extras` field (default empty) holding the provider pin.
  * **Modified** `kimi-k2.6-openrouter` **entry:** both of its brain sizes carry the SiliconFlow pin, and its pricing row changes to 0.77 / 3.4 / 0.14 / cache-write 0. Other hand-written entries are unchanged in behaviour.
  * **Modified validation:** `validate_llm_provider_environment` additionally checks that `request_extras` is a dict on every brain size and that every catalog SKU resolves through `get_sku_pricing` without ambiguity.
  * **Table shape is the builder's call:** row layout, field names, provider-slug spelling (OpenRouter's routing ids), and exact function names are `plan-child`'s.
* `src/external/llm_compat.py` (**modified**): the modified send function builds its `extra_body` from thinking payload + server `request_extras` + tier `request_extras`. The tier's extras win on key collision. The existing ungated call/response debug lines keep logging the full body, so the pin shows up in them.

Estimate: 3

#### 2: **Remove the Manage Task model picker - Ada**

Makes the agent row the only model source in the UI. The Manage Task modal drops the Model / Brain size selects that [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) added, and saving a task no longer writes the agent. The list's read-only Model column stays. Runs in parallel with #1, and does **not** touch the catalog or compat client (#1).
**Citations:** none. Frontend-only removal, and no active pattern or statute governs this page.
**Scope:**

* `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`:
  * **Removed:** the model-catalog fetch, the agent model/brain load, the model-change handler, the Model and Brain size selects with their "Applies to agent" note, and the post-save agent `PUT`. Plus the related state, types, and helper that only those used.
  * **Unchanged:** the Agent select, the task save, and the list's read-only Model column.
* `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`: the modified [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) modal-select cases are removed or replaced by an assertion that the modal has no Model / Brain size select and that save issues no agent `PUT`.
* `docs/test-bible/frontend/pages.md`: the modified Manage Task entries drop the [AST-1909](https://linear.app/astralcareermatch/issue/AST-1909/manage-task-modal-no-model-dropdown-of-config-driven-model-keys) model-select rows.

Estimate: 1

**New patterns:** none.

**Monolith check:** 6 functional items, 2 children. Items 1–5 are properties of the same catalog table rows plus the compat-client merge that carries their pin, so they stay one slice (#1). Item 6 is an independent UI removal (#2).

**Scope partition check:**

* **#1:** `config.py`, `llm_compat.py`, and their Technical scope items.
* **#2:** `AdminTaskPrompts.tsx` and its test and bible rows.
* No file is claimed twice and none is unclaimed.

---

## Original brief

```
MODEL                                      PROVIDER       IN$/M  OUT$/M  CACHE$/M  CTX      UP1D
anthracite-org/magnum-v4-72b               Mancer 2       2.5    5       0         32768    99
bytedance-seed/seed-1.6                    Seed           0.25   2       0         262144   100
bytedance-seed/seed-1.6-flash              Seed           0.08   0.3     0         262144   99
bytedance-seed/seed-2-1-turbo              Seed           0.5    2.5     0         262144   99
bytedance-seed/seed-2.0-code               Seed           0.5    3       0         262144   100
bytedance-seed/seed-2.0-lite               Seed           0.25   2       0         262144   99
bytedance-seed/seed-2.0-mini               Seed           0.1    0.4     0         262144   99
deepseek/deepseek-chat-v3-0324             SiliconFlow    0.25   1       0         163840   98
deepseek/deepseek-chat-v3.1                SiliconFlow    0.27   1       0         163840   97
deepseek/deepseek-r1-0528                  SiliconFlow    0.5    2.18    0         163840   99
deepseek/deepseek-v3.1-terminus            SiliconFlow    0.27   1       0         163840   98
deepseek/deepseek-v3.2                     SiliconFlow    0.26   0.42    0.14      163840   96
deepseek/deepseek-v3.2-exp                 SiliconFlow    0.27   0.41    0         163840   99
deepseek/deepseek-v4-flash                 OpenInference  0      1.6     0         1048576  99
deepseek/deepseek-v4-flash-0731            OpenInference  0      1.6     0         1048576  99
deepseek/deepseek-v4-flash-vision-exp      DeepInfra      0.22   0.65    0.01      1048576  99
deepseek/deepseek-v4-pro                   DeepInfra      1.3    2.6     0.1       1048576  99
deepseek/deepseek-v4-pro-0813              NextBit        1.06   3.17    0.04      1048576  99
deepseek/deepseek-v4.1-flash               Morph          0.02   0.38    0.01      1048576  99
google/gemma-3-27b-it                      DeepInfra      0.08   0.16    0         131072   99
google/gemma-4-26b-a4b-it                  DeepInfra      0.07   0.34    0         262144   99
google/gemma-4-31b-it                      DeepInfra      0.15   0.4     0         262144   97
gryphe/mythomax-l2-13b                     Mancer 2       0.35   0.6     0         8192     99
meta-llama/llama-3.1-70b-instruct          DeepInfra      0.4    0.4     0         131072   97
meta-llama/llama-3.3-70b-instruct          DeepInfra      0.1    0.32    0         131072   98
meta-llama/llama-4-maverick                Novita         0.27   0.85    0         1048576  99
meta-llama/llama-4-scout                   DeepInfra      0.1    0.3     0         327680   99
mistralai/mistral-nemo                     DekaLLM        0.02   0.03    0         131072   99
mistralai/mistral-small-24b-instruct-2501  DeepInfra      0.05   0.08    0         32768    99
mistralai/mistral-small-3.2-24b-instruct   DeepInfra      0.08   0.2     0         128000   99
moonshotai/kimi-k2-0905                    Novita         0.6    2.5     0         262144   99
moonshotai/kimi-k2.6                       SiliconFlow    0.77   3.4     0.14      262144   99
moonshotai/kimi-k3                         Morph          1.35   11.36   0.29      1048576  99
morph/morph-v3-large                       Morph          0.9    1.9     0         262144   100
nousresearch/hermes-3-llama-3.1-405b       DeepInfra      1      1       0         131072   99
nousresearch/hermes-3-llama-3.1-70b        DeepInfra      0.7    0.7     0         131072   100
nvidia/nemotron-3-nano-30b-a3b             Crusoe         0.05   0.2     0.03      262144   99
nvidia/nemotron-3-super-120b-a12b          DekaLLM        0.08   0.45    0         262144   97
openai/gpt-oss-120b                        Mancer 2       0.05   0.28    0         131072   98
openai/gpt-oss-20b                         SiliconFlow    0.04   0.18    0         131072   97
qwen/qwen-2.5-72b-instruct                 DeepInfra      0.36   0.4     0         32768    96
qwen/qwen2.5-vl-72b-instruct               Parasail       0.8    1       0.4       128000   99
qwen/qwen3-14b                             DeepInfra      0.12   0.24    0         40960    96
qwen/qwen3-235b-a22b-2507                  Novita         0.09   0.58    0         131072   96
qwen/qwen3-30b-a3b                         DeepInfra      0.12   0.5     0         40960    99
qwen/qwen3-30b-a3b-instruct-2507           SiliconFlow    0.09   0.3     0         262144   99
qwen/qwen3-32b                             DeepInfra      0.08   0.28    0         40960    99
qwen/qwen3-coder-30b-a3b-instruct          SiliconFlow    0.07   0.28    0         262144   98
qwen/qwen3-next-80b-a3b-instruct           DeepInfra      0.09   1.1     0         262144   99
qwen/qwen3-vl-235b-a22b-instruct           DeepInfra      0.2    0.88    0.11      262144   98
qwen/qwen3-vl-30b-a3b-instruct             DeepInfra      0.15   0.6     0         262144   99
qwen/qwen3.5-27b                           SiliconFlow    0.25   2       0         262144   98
qwen/qwen3.5-35b-a3b                       DeepInfra      0.14   1       0.05      262144   99
qwen/qwen3.5-397b-a17b                     DeepInfra      0.45   3       0.22      262144   96
qwen/qwen3.5-9b                            SiliconFlow    0.1    0.15    0         262144   98
qwen/qwen3.6-27b                           SiliconFlow    0.3    3.2     0         262144   96
qwen/qwen3.6-35b-a3b                       AkashML        0.1    0.9     0.05      262144   99
qwen/qwen3.8-2.4t-a95b                     SiliconFlow    2      6       0.25      1048576  99
qwen/qwen3.8-27b                           Ionstream      0.09   2.2     0.09      262144   98
sao10k/l3.1-euryale-70b                    DeepInfra      0.85   0.85    0         131072   99
stepfun/step-3.7-flash                     Novita         0.2    1.15    0.04      262144   99
tencent/hunyuan-a13b-instruct              SiliconFlow    0.14   0.57    0         131072   100
tencent/hy-mt2-30b-a3b                     Tencent        0.07   0.3     0         8192     100
tencent/hy-mt2-7b                          Tencent        0.07   0.3     0         8192     100
tencent/hy4-preview                        DeepInfra      0.83   2.5     0.04      1048576  97
thedrummer/skyfall-36b-v2                  Parasail       0.55   0.8     0.25      32768    100
undi95/remm-slerp-l2-13b                   Mancer 2       0.35   0.65    0         6144     99
xiaomi/mimo-v2.5                           Venice         0.4    2       0.08      1000000  99
xiaomi/mimo-v2.6-flash                     DeepInfra      0.14   0.28    0         1048576  98
xiaomi/mimo-v2.6-pro                       DeepInfra      0.43   0.87    0         1048576  99
z-ai/glm-4.7-flash                         Venice         0.06   0.4     0.01      128000   98
z-ai/glm-5                                 Venice         1      3.2     0.2       198000   99
z-ai/glm-5.1                               Nebius         1.4    4.4     0         202752   97
z-ai/glm-5.2                               Morph          0.25   3.07    0.2       1048576  98
z-ai/glm-5.3                               Morph          0.19   2.99    0.15      1048576  99
z-ai/glm-5.3-flash                         Near AI        0.11   0.35    0.02      1048576  95
```

Please support these 76 models through OpenRouter.

### Comments

#### chuckles — 2026-10-02T18:14:16.212Z
AST-1939 drone collision — Betty's shared session `12ade1a8` was resumed for AST-1939 while the AST-1938 qa-child run (ebc576fc) was still live; `datt_trace` call-wait did not detect busy, so both ran concurrently in `astral-tests`. The AST-1939 pass stashed AST-1938 WIP as `stash@{0}`; Chuckles restored all three files (`test_llm_compat.py`, `test_config.py` hunk, `fixtures/ast1937_openrouter_brief.txt`) to the working tree unstaged — stash kept as backup, drop once AST-1938 qa-child publishes. Separately, Betty notes `origin/tests` carries a stale `docs/uat-fixtures/AST-756/expected-agent_task.json` (missing AST-1910's change on dev).

#### chuckles — 2026-10-02T17:40:38.946Z
@susan

1. The brief says 77 models, but the table has 76 rows, and one of them (`moonshotai/kimi-k2.6`) is already in the catalog. Is a row missing from the table, or is 76 the real list?
2. **Brain sizes.** I recommend Little (thinking off) for every model, plus Big (thinking on) only for the 48 of 76 that OpenRouter lists as reasoning-capable, snapshotted into the table at build. The alternatives are Little-only for every model, or Little + Big for all (non-reasoning models may reject or ignore the thinking payload). Which one?
3. **Pin the upstream provider?** The brief's prices and contexts are per provider (for example `qwen/qwen3-32b` is 40,960 ctx on DeepInfra versus 131,072 on OpenRouter's model listing). Unpinned, OpenRouter routes freely and the ledger price is only an estimate.
   * **My recommendation:** pin each model to the brief's PROVIDER with no fallback.
   * **Follow-up for `kimi-k2.6-openrouter`:** should it move to the brief's SiliconFlow pin + price (0.77 / 3.4 / 0.14), or stay on Moonshot list price (0.95 / 4.00 / 0.16) unpinned?
4. **Default temperature and output budget.** My recommendation:
   * **Temperature:** 0.6 with thinking off and 1.0 with thinking on, same as the Kimi entries.
   * **Output budget:** `default_max_tokens` = 16,000 for Little and 32,000 for Big, each capped at the pinned provider's max output. That cap gives five models (magnum-v4-72b, mythomax-l2-13b, hy-mt2-30b-a3b, hy-mt2-7b, remm-slerp-l2-13b) a 3.7k–5.5k default.
   * Agent rows can still override both. OK, or do you want different numbers?

---

_Implementation detail may live in git history on `origin/dev`._
