# AST-1953 — Refactor agent settings and ingest per-endpoint model options

<!-- linear-archive: AST-1953 archived 2026-10-08 -->

## Linear archive (AST-1953)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1953/refactor-agent-settings-and-ingest-per-endpoint-model-options  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Today an agent's LLM call is shaped by two proxies, `brain_setting` and `mode`. Since [AST-1946](https://linear.app/astralcareermatch/issue/AST-1946), `brain_setting` on an OpenRouter model means host quantization, and `mode` means thinking on/off plus a hard-coded temperature (Deterministic 0.2, Creative 0.6). Susan wants each agent row to carry the **real request settings**, stored as plain values and sent as-is, with nothing in code deriving or gating them.

**Scope (Susan, 2026-10-03):**

* "Just support the additional settings and then wire those settings into the call."
* "Code it loosely, because code-bound constraints are biting me." The settings are static, any model may take any setting, and a setting the endpoint rejects fails at runtime like any other failed call. Susan catches those in testing.
* No catalog ingest or polling.
* No pre-send guardrails.
* No pricing change.
* No served-host logging. Per-batch host pinning and fallback visibility are [AST-1954](https://linear.app/astralcareermatch/issue/AST-1954)'s.

**As-built facts (**`origin/dev` **@** `0eddf5214`**, 2026-10-03):**

* `config._openrouter_pin` pins every OpenRouter model to one host with fallbacks off (`order: [<host>]`, `allow_fallbacks: false`, `quantizations: [<quant>]`). `openai/gpt-oss-120b` is pinned to `dekallm` / `bf16`, which is why DekaLLM's 2026-10-03 429 stalled `anticipate_scan`. This ticket replaces that pin with the agent's own provider settings.
* The `temp=0.6` log line: `agent.do_task` logs the mode's temperature even when the call is thinking, and in that case `llm_compat` never sends it. This ticket logs what is actually sent.
* Both LLM clients speak the Anthropic Messages protocol. Effort is `output_config.effort`, and thinking-off is `thinking: {type: "disabled"}`.

## Functional scope

1. **Plain settings on every agent.** Each agent row carries these fields, all optional:
   * `quantization`: free text, for example `bf16`;
   * `temperature`: a number;
   * `reasoning_effort`: free text, for example `high` or `none`;
   * `provider_allow_fallbacks`: true/false, default true;
   * `provider_only` and `provider_ignore`: lists of provider slugs;
   * `provider_sort`: free text, for example `price`.

   Code validates nothing beyond type. There is no vocabulary list and no per-model check. `model_id` and the `max_tokens` override stay exactly as they are today.
2. **Settings go on the wire as-is.** When a setting is empty it is not sent.
   * `temperature` → `temperature`.
   * `reasoning_effort` → the Messages-protocol effort field. `none` means thinking disabled.
   * On OpenRouter, the provider object is built from the agent row:
     * `quantizations: [<quantization>]`;
     * `allow_fallbacks`;
     * `only`, `ignore` and `sort`.

   AST-1946's hard-coded host pin is removed. If an endpoint rejects a setting, the call fails and the entity takes the normal [`patt.task.dispatch-retry`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md>) path (`_RETRY`, then the configured error state). There is no special handling (Susan).
3. **Proxies retired (Susan: remove mode).** `brain_setting` and `mode` leave the agent row, the seed, the API, the Manage Agents form and the call path. Nothing derives a temperature or a thinking switch from a label. The catalog loses its mode table, its per-size layer and its "can think" / thinking-payload fields. The craft-rubric thinking-off guard ([AST-1380](<https://linear.app/astralcareermatch/issue/AST-1380>)) and the per-task max-token floors stay. They are task-level truncation guards.
4. **Direct models: one model id per SKU (Susan: "YEP").**
   * `claude` splits into `claude-haiku-4-5`, `claude-sonnet-4-6` and `claude-opus-4-6`.
   * `deepseek-v4` splits into `deepseek-v4-flash` and `deepseek-v4-pro`.
   * `kimi-k2.6` stays one id.

   The DeepSeek Big 384k output floor moves to the agent's own `max_tokens`. OpenRouter models stay the current 95 slugs, one model id each.
5. **Default output budget without mode.** When an agent leaves `max_tokens` empty:
   * an OpenRouter model defaults to 16,000, capped at the model's listed max output (today's Deterministic default);
   * a direct model defaults to its SKU's existing default.

   The agent's `max_tokens` override is unchanged.
6. **Truthful debug line.** The `Calling _send_to_server` debug line logs the temperature and effort actually sent.
7. **Manage Agents edits the settings.** The add/edit form has:
   * a text input for quantization;
   * a number input for temperature;
   * a text input for effort;
   * a checkbox for allow-fallbacks;
   * comma-separated text inputs for only and ignore;
   * a text input for sort.

   The list shows them. Brain-size and mode controls are removed. The model picker lists the model ids from Functional scope 4.
8. **Live agent rows move once.** A run-once operator migration does three things.
   * **Per-SKU model ids:**
     * `claude` Little/Medium/Big → Haiku/Sonnet/Opus;
     * `deepseek-v4` Little → flash, and Medium/Big → pro (Big also gets `max_tokens` at least 384,000);
     * `kimi-k2.6` Big with empty `max_tokens` → 32,000, keeping today's Big default.
   * **Starting settings:**
     * `temperature` = what the call sends today: 0.2 on Deterministic, 0.6 on Creative where the model can't think, empty where it thinks;
     * `reasoning_effort: none` where today's call sends thinking-off on a model that can think;
     * `provider_allow_fallbacks: true`;
     * everything else empty, including `quantization` (Susan: no derived quantization; she sets it per agent).
   * **Column drop:** it drops the `brain_setting` and `mode` columns after deriving from them.

   It supersedes AST-1950's run-once script, which imports the mode constants this ticket removes.

**Not in scope:**

* catalog ingest, endpoint snapshots, quantization lists;
* pre-send parameter or `max_tokens` guardrails;
* `provider.require_parameters`;
* pricing changes (Susan);
* served-provider / served-quantization logging and host pinning ([AST-1954](https://linear.app/astralcareermatch/issue/AST-1954));
* choosing each agent's model;
* prompt/persona changes;
* BYOK keys.

## Component scope

* `src/utils/config.py`: **modified**.
  * Per-SKU direct models, with the per-size layer gone.
  * The OpenRouter table loses the host and quantization pin columns.
  * Mode, pin and resolver constants are removed, and a settings resolver is added.
  * The agent repo-JSON column list is updated.
* `src/data/database.py`: **modified**. Agent table gains the setting columns. Save, update, repo-JSON apply and validation write them and stop requiring `brain_setting` / `mode`.
* `data/admin/agent.json`: **modified**. Seed rows carry the settings and per-SKU model ids, and lose `brain_setting` and `mode`.
* `docs/uat-fixtures/AST-756/expected-agent.json`: **modified**. Twin of `agent.json`.
* `src/core/agent.py`: **modified**. The route helper reads the agent's settings, and the debug line logs what is sent. `run_adhoc` gets the same.
* `src/external/llm_compat.py`: **modified**. Sends temperature, effort and the provider object from the settings.
* `src/external/anthropic.py`: **modified**. Sends the agent's effort when set, same field, no gating.
* `src/ui/api/api_admin.py`: **modified**.
  * Agent create/update take and return the settings and no longer require `brain_setting` / `mode`.
  * `GET /agents/models` drops brain sizes.
  * The adhoc/workbench routes use the new resolver.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`: **modified**. Settings inputs and columns. Brain-size and mode controls removed.
* `scripts/migrations/remap_agent_settings.py`: **new**. Run-once migration of live rows, dry run by default.
* `scripts/migrations/remap_openrouter_agents.py`: **deleted**. AST-1950's superseded script.
  * `tests/component/scripts/test_remap_openrouter_agents.py`: **deleted**.
  * `docs/test-bible/dev/remap_openrouter_agents.md`: **deleted**.
* Tests and bibles (**modified** or **new**, Betty in `qa-child`):
  * `tests/component/utils/test_config.py`
  * `tests/component/data/database/test_agents.py`
  * `tests/component/core/test_repo_admin_json.py`
  * `tests/component/core/test_agent.py`
  * `tests/component/external/test_llm_compat.py`
  * `tests/component/external/test_anthropic.py`
  * `tests/component/ui/api/test_api_admin.py`
  * `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`
  * `tests/component/scripts/test_remap_agent_settings.py` (**new**)
  * `docs/test-bible/utils/config.md`
  * `docs/test-bible/data/database/agents.md`
  * `docs/test-bible/core/agent.md`
  * `docs/test-bible/external/llm_compat.md`
  * `docs/test-bible/external/anthropic.md`
  * `docs/test-bible/ui/api/api_admin.md`
  * `docs/test-bible/frontend/pages.md`
  * `docs/test-bible/dev/remap_agent_settings.md` (**new**)

## Technical scope

* `src/utils/config.py`:
  * **Modified direct models:** `claude` and `deepseek-v4` become one model entry per SKU, each with its SKU, pricing row (unchanged), default output budget and floor. `kimi-k2.6` stays one entry with its Little default. The `brain_sizes` layer, `can_think` and `thinking_params` leave every model.
  * **Modified OpenRouter table and builder:** each of the 95 slugs keeps its price and max output. The host-slug, quantization and reasoning columns go, because nothing reads them once the pin and mode are gone. The listing default is min(16,000, max output).
  * **New settings resolver:** model id + agent settings → server, SKU, pricing, default output budget, the provider object (OpenRouter only, empty keys omitted), and the temperature/effort to send. It replaces `resolve_model_brain`.
  * **Modified repo-JSON column list for** `agent`**:** the settings in, `brain_setting` and `mode` out.
  * **Removed:** `AGENT_MODE_CONFIG`, the mode constants, `AGENT_MODES`, `validate_agent_mode`, `OPENROUTER_QUANT_BRAIN_SIZE`, `OPENROUTER_THINKING_PARAMS`, `_openrouter_pin`, `resolve_model_brain`, `model_brain_sizes`, `validate_brain_setting_for_model`, and the `brain_settings` / tier-map helpers left with no caller.
* `src/data/database.py`:
  * **Modified agent schema-ensure:** adds the setting columns. It does **not** drop `brain_setting` / `mode`, because the migration needs to read them first (DDL only, per AST-1497).
  * **Modified agent writes:** save, update allow-list, repo-JSON apply and repo-JSON validation write the settings (type checks only) and no longer read, require or validate `brain_setting` / `mode`.
  * **Modified public view:** returns the settings and not `brain_setting` / `mode`.
* `data/admin/agent.json`, `docs/uat-fixtures/AST-756/expected-agent.json`:
  * every row gains the settings, using the Functional scope 8 starting values (computed by hand for the 7 seed rows);
  * direct rows get per-SKU model ids;
  * every row loses `brain_setting` and `mode`.
* `src/core/agent.py`:
  * **Modified route helper:** calls the new resolver with the agent row.
  * **Modified call path (**`do_task`**,** `run_adhoc`**):** passes the resolved temperature/effort/provider object through. The craft-rubric guard still forces thinking off, and the floors still apply.
  * **Modified debug line:** logs the temperature and effort sent.
* `src/external/llm_compat.py`: **modified request assembly**.
  * Sends `temperature` when given.
  * Sends the effort in `output_config.effort`, or `thinking: {type: "disabled"}` for `none`.
  * Merges the provider object into the body.
  * The thinking-on/off-from-tier branch goes. The failure path is unchanged.
* `src/external/anthropic.py`: **modified** `send_to_anthropic`. Takes an optional effort and sends it the same way when given. The failure path is unchanged.
* `src/ui/api/api_admin.py`:
  * **Modified agent create/update:** take and return the settings (type checks only) and no longer require or accept `brain_setting` / `mode`.
  * **Modified** `GET /agents/models`**:** returns model id, label, server and default output budget, with no brain sizes.
  * **Modified adhoc/workbench resolvers:** use the new resolver.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`:
  * **Modified form:** the Functional scope 7 inputs, sent as the settings keys.
  * **Removed:** brain-size and mode controls, the `AGENT_MODES` constant and the size pre-fill.
  * **Modified list columns:** show the settings.
  * **Modified model types:** drop brain sizes.
* `scripts/migrations/remap_agent_settings.py`: a new CLI. By default it is a dry run that prints each row's planned change. `--apply` writes the Functional scope 8 values, then drops the `brain_setting` and `mode` columns. It carries a literal snapshot of which model ids could think on 2026-10-03, so it does not depend on removed config. It handles rows whose `mode` is null ([AST-1950](https://linear.app/astralcareermatch/issue/AST-1950/run-once-agent-remap-starting-modes-new-sizes-kimi-fold-support-big) never ran) by treating them as Big → Creative, else Deterministic. The docstring says: run **once per environment, right after deploy**.

## Architectural definition

* **Patterns to reuse:**
  * [`patt.task.dispatch-retry`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md>): an endpoint rejecting a setting is an ordinary failed call. The entity goes to `_RETRY`, then the configured error state, with no special case (Susan).
  * No other active pattern covers agent settings or operator migrations. The column change follows [AST-1878](https://linear.app/astralcareermatch/issue/AST-1878) / [AST-1948](https://linear.app/astralcareermatch/issue/AST-1948/agent-mode-persisted-and-applied-temperature-and-model-code-retired), and the migration follows the `scripts/migrations/` convention.
* **New patterns proposed:** `none`.
* **Applicable statutes:**
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>): the request body with the new settings stays visible in the compat/Anthropic clients' existing ungated debug logging. The `_send_to_server` debug line logs what is sent. No `debug=` parameter is added.
  * [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>): agent create/update keep the statute's one completing-route line.
  * The migration script is under `scripts/`, which is outside every directive's scope.

## Acceptance criteria

"Stubbed client" means the component-test stubs of the Anthropic SDK client used by `test_llm_compat.py`, `test_anthropic.py` and `test_agent.py`.

 1. **Provider object from the agent row.**
    * **Check (stubbed client):** an agent on `openai/gpt-oss-120b` with `quantization: "bf16"`, fallbacks true and nothing else sends `provider == {"quantizations": ["bf16"], "allow_fallbacks": true}` exactly. With `provider_only: ["crusoe"]`, `provider_sort: "price"` added, it also carries `only` and `sort`.
    * **Fails if:** any other key appears, or there is an `order` pin, or the body differs.
 2. **Empty settings send nothing.**
    * **Check (stubbed client):** an OpenRouter agent with every setting empty except fallbacks sends no `temperature`, no `output_config`, no `thinking`, and `provider == {"allow_fallbacks": true}`.
    * **Fails if:** any of those keys appears with a value the agent didn't set.
 3. **Temperature and effort exactly as set, no gating.**
    * **Check (stubbed client):**
      * `temperature: 0.3` → `temperature == 0.3`;
      * `reasoning_effort: "high"` → `output_config.effort == "high"`;
      * `reasoning_effort: "none"` → `thinking == {"type": "disabled"}`.
    * **Check:** a model whose old config said it couldn't think still sends `"high"` when set.
    * **Check:** the same on `claude-sonnet-4-6` via the Anthropic client.
    * **Fails if:** any value is dropped, changed or blocked in code.
 4. **A rejected setting is an ordinary failure.**
    * **Check (stubbed 400 "Reasoning is mandatory for this endpoint and cannot be disabled"):** `do_task` returns the normal failure result. No new failure class is introduced: `rg -n "config_error|configuration_error" src/` returns nothing.
    * **Fails if:** a special class or hold path appears.
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
 8. **Truthful debug line.**
    * **Check (component test):** for an agent with empty temperature, the `Calling _send_to_server` debug line shows `temp=None`.
    * **Fails if:** a number is logged.
 9. **Seed carries the settings.**
    * **Check:** every row in `data/admin/agent.json` has the seven settings keys and no `brain_setting` or `mode`, and direct rows use per-SKU ids. The AST-756 fixture matches field-for-field, and reverting the agent table from the seed succeeds.
    * **Fails if:** a key is missing or retired, the fixture drifts, or revert fails.
10. **Manage Agents edits the settings.**
    * **Check (frontend component test):** the edit form renders the seven settings inputs and saves them under the settings keys, with no `brain_setting` or `mode` in the body.
    * **Check:** `rg -n "brain_setting|AGENT_MODES|Deterministic|Creative" src/ui/frontend/src/pages/AdminAgentPrompts.tsx` returns nothing.
    * **Fails if:** any input is missing or a retired control remains.
11. **Migration moves live rows once.**
    * **Check (component test, temp DB with** `brain_setting` **/** `mode` **columns):** seed these rows:
      * `claude` Medium Deterministic;
      * `deepseek-v4` Big Creative;
      * `kimi-k2.6` Big Creative with empty `max_tokens`;
      * `z-ai/glm-4.6` Deterministic;
      * `microsoft/phi-4` Creative;
      * one row with null `mode`.

      A dry run writes nothing. `--apply` yields:
      * `claude-sonnet-4-6` with temperature 0.2 and empty effort (`claude` couldn't think);
      * `deepseek-v4-pro` with `max_tokens >= 384000`, temperature 0.6;
      * `kimi-k2.6` with `max_tokens` 32000, empty temperature;
      * `z-ai/glm-4.6` with temperature 0.2 and effort `none`;
      * `microsoft/phi-4` with temperature 0.6.

      Every row has fallbacks true and empty quantization, and `PRAGMA table_info(agent)` then lists no `brain_setting` or `mode`.
    * **Fails if:** the dry run writes, a row maps differently, or a column survives.

## Open questions

None.

## Proposed child tickets

#### 1!!: **Plain agent settings and per-SKU direct models - Katherine**

Adds the settings columns to the agent row and stops requiring `brain_setting` and `mode`. Splits direct models into one id per SKU. Removes the mode table, the host pin and the per-size layer from config, and adds the settings resolver. Does **not** touch the call path (#2), the admin routes and UI (#3), or live rows (#4).
**Citations:** `stat.logging.debug`.
**Scope:**

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

Estimate: 3

#### 2: **Send the agent's settings on the wire - Hedy**

Agent calls send temperature, effort and the provider object straight from the agent's settings, on both clients, with no gating. A rejected setting is an ordinary failure. The debug line shows what was sent. After #1. Does **not** touch admin routes or UI (#3).
**Citations:** `patt.task.dispatch-retry` (rejections take the normal retry path); `stat.logging.debug`.
**Scope:**

* `src/core/agent.py` (**modified**):
  * **Modified route helper:** calls the new resolver with the agent row.
  * **Modified call path (**`do_task`**,** `run_adhoc`**):** passes the resolved temperature/effort/provider object through. The craft-rubric guard still forces thinking off, and the floors still apply.
  * **Modified debug line:** logs the temperature and effort sent.
* `src/external/llm_compat.py` (**modified**): **modified request assembly**.
  * Sends `temperature` when given.
  * Sends the effort in `output_config.effort`, or `thinking: {type: "disabled"}` for `none`.
  * Merges the provider object into the body.
  * The thinking-on/off-from-tier branch goes. The failure path is unchanged.
* `src/external/anthropic.py` (**modified**): **modified** `send_to_anthropic`. Takes an optional effort and sends it the same way when given. The failure path is unchanged.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/core/test_agent.py`
  * `tests/component/external/test_llm_compat.py`
  * `tests/component/external/test_anthropic.py`
  * `docs/test-bible/core/agent.md`
  * `docs/test-bible/external/llm_compat.md`
  * `docs/test-bible/external/anthropic.md`

Estimate: 3

#### 3: **Manage Agents edits the plain settings - Ada**

The admin routes take and return the settings, and the models list drops brain sizes. The Manage Agents form gets plain inputs for each setting, and brain size and mode are removed. After #1. Does **not** touch the call path (#2).
**Citations:** `stat.logging.info.api`.
**Scope:**

* `src/ui/api/api_admin.py` (**modified**):
  * **Modified agent create/update:** take and return the settings (type checks only) and no longer require or accept `brain_setting` / `mode`.
  * **Modified** `GET /agents/models`**:** returns model id, label, server and default output budget, with no brain sizes.
  * **Modified adhoc/workbench resolvers:** use the new resolver.
* `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` (**modified**):
  * **Modified form:** the Functional scope 7 inputs, sent as the settings keys.
  * **Removed:** brain-size and mode controls, the `AGENT_MODES` constant and the size pre-fill.
  * **Modified list columns:** show the settings.
  * **Modified model types:** drop brain sizes.
* Tests and bibles (Betty in `qa-child`):
  * `tests/component/ui/api/test_api_admin.py`
  * `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`
  * `docs/test-bible/ui/api/api_admin.md`
  * `docs/test-bible/frontend/pages.md`

Estimate: 3

#### 4: **Run-once migration of live agent rows - Katherine**

Moves every live agent row to per-SKU ids and its starting settings, then drops `brain_setting` and `mode`. Retires AST-1950's superseded script with its test and bible. After #1, which provides the setting columns. Does **not** touch product code.
**Citations:** none. The script is under `scripts/`, outside every directive's scope.
**Scope:**

* `scripts/migrations/remap_agent_settings.py` (**new**): a new CLI. By default it is a dry run that prints each row's planned change. `--apply` writes the Functional scope 8 values, then drops the `brain_setting` and `mode` columns. It carries a literal snapshot of which model ids could think on 2026-10-03, so it does not depend on removed config. It handles rows whose `mode` is null ([AST-1950](https://linear.app/astralcareermatch/issue/AST-1950/run-once-agent-remap-starting-modes-new-sizes-kimi-fold-support-big) never ran) by treating them as Big → Creative, else Deterministic. The docstring says: run **once per environment, right after deploy**.
* `scripts/migrations/remap_openrouter_agents.py`, `tests/component/scripts/test_remap_openrouter_agents.py`, `docs/test-bible/dev/remap_openrouter_agents.md` (**deleted**).
* `tests/component/scripts/test_remap_agent_settings.py`, `docs/test-bible/dev/remap_agent_settings.md` (**new**, Betty in `qa-child`).

Estimate: 2

**New patterns:** none.

**Monolith check:** 8 functional items, 4 children.

* **#1:** items 1, 3, 4, 5 and 8's seed side.
* **#2:** items 2 and 6.
* **#3:** item 7.
* **#4:** item 8's live rows.

**Scope partition check:**

* **#1:** `config.py`, `database.py`, the seed file and the AST-756 fixture, plus their tests and bibles.
* **#2:** `agent.py`, `llm_compat.py` and `anthropic.py`, plus their tests and bibles.
* **#3:** `api_admin.py` and `AdminAgentPrompts.tsx`, plus their tests and bibles.
* **#4:** the new migration, the deleted [AST-1950](https://linear.app/astralcareermatch/issue/AST-1950/run-once-agent-remap-starting-modes-new-sizes-kimi-fold-support-big) script, and their tests and bibles.
* No file is claimed twice and none is unclaimed.

**Sequencing:** #1 removes config symbols that #2 and #3's files still import. The epic integrates on `ftr` and lands on `dev` whole, so that intermediate state never deploys. #4 runs in each environment right after that deploy. Until it runs, live agents send no temperature or effort, and rows still on the retired `claude` / `deepseek-v4` ids fail to resolve.

---

## Original brief

## Context

Agent model configuration currently carries `brain_setting` (Little/Medium/Big) and `mode` (Deterministic/Creative) as proxies for LLM settings. Those proxies no longer map to anything real: `college_intern_ruth` is `brain_setting: Big` on a 12B model, and `job_filter_lucy` is `Big` on a sparse MoE. Meanwhile the dispatcher sends no `provider` object at all, so routing falls through to OpenRouter's price-weighted default.

Two live consequences, both observed 2026-10-03:

1. **Rate-limit outage.** `anticipate_scan` failed with a 429 —

   `limit_source: upstream_provider_shared_pool`, `provider_name: DekaLLM`,  `is_byok: false`. Five agents now share `openai/gpt-oss-120b`, so one  provider's shared-pool limit stalls half the pipeline.
2. **Silent precision drift.** `openai/gpt-oss-120b` is served at **bf16** by

   DekaLLM, DeepInfra, AkashML and Crusoe, and at **fp4** by CoreWeave, Nebius,  Parasail and BaseTen. With no `quantizations` filter, each call lands on  whichever host is cheapest that second. Precision varies per request, with  nothing in the logs saying so.

Also: `_send_to_server` logs `temp=0.6` on a call whose agent record specifies no temperature. Something between the agent record and the request body is setting it. That needs to be found and made explicit.

---

## Problem

**P1 — Settings are not addressable.** There is no per-agent field for `temperature`, `reasoning_effort`, `quantization`, or provider policy. Behaviour is whatever the model defaults to, which differs per model and is undocumented for most.

**P2 — Routing is unconstrained.** No `provider` object means no failover strategy and no precision floor.

**P3 — Unsupported parameters fail silently.** OpenRouter *drops* parameters an endpoint does not support rather than erroring. A `temperature: 0.0` sent to a temp-pinned endpoint runs at the model's default with no error and no log line.

**P4 —** `max_tokens` **is a hidden routing filter.** OpenRouter only routes to providers that can return a response of the requested length, and `max_completion_tokens` varies \~30x across hosts of the same weights. `content_writer_judith` (380000) and `principal_recruiter_estelle` (384000) both exceed every endpoint that serves `moonshotai/kimi-k2-thinking` — Novita bf16 caps at 98,304 and Google at 235,929. Any value above 98,304 also routes *off* the only bf16 host.

**P5 — Model catalog ingest keeps only the cheapest endpoint per model.** The `our_models` ingest sorts by completion price and dedupes by `model_id`, which always keeps the most aggressively quantized host and discards every bf16 option. `moonshotai/kimi-k2.6` is served at bf16 by Crusoe; the catalog only ever showed the int4 Inceptron row. Same for `gemma-4-31b`, `qwen3.8-27b`, and `deepseek-v4-flash-0731`.

---

## Scope

### A. Agent record: explicit settings

Add to the agent model-settings record:

| field | type | notes |
| -- | -- | -- |
| `quantization` | enum, required | `bf16` / `fp16` / `fp8` / `fp4` / `int4` / `any` |
| `temperature` | float, nullable | null = send nothing, accept model default |
| `reasoning_effort` | string, nullable | null = send nothing |
| `provider_allow_fallbacks` | bool, default true |  |
| `provider_only` | string\[\], nullable | provider slugs; empty = any |
| `provider_ignore` | string\[\], nullable |  |
| `provider_sort` | enum, nullable | `price` / `throughput` / `latency` |

Retire `brain_setting`. Retire or redefine `mode` — if it stays, it must be a label with no effect on the request body, and the temperature it currently implies must move to the explicit field.

Dispatcher assembles:

```
"provider": {
  "quantizations": ["<quantization>"],
  "allow_fallbacks": <provider_allow_fallbacks>,
  "only": [...],        // omit when empty
  "ignore": [...],      // omit when empty
  "sort": "<...>"       // omit when null
}
```

### B. Model catalog ingest: one row per endpoint

Replace the model-per-row ingest with an endpoint-per-row ingest from `GET https://openrouter.ai/api/v1/endpoints/zdr` (public, no auth).

Primary key `(model_id, provider_name, quantization, tag)`. Carry at minimum:

* `tag` (e.g. `morph/fp8`, `crusoe/bf16`) — host + precision identifier
* `supported_parameters[]` — the authoritative list of settable knobs
* `max_completion_tokens`, `context_length`
* `pricing.prompt`, `pricing.completion`, `pricing.input_cache_read`
* `uptime_last_1d`, `uptime_last_30m`
* `quantization` verbatim, including the literal string `unknown`

`unknown` means undisclosed, **not** full precision. Do not coerce it.

### C. Guardrails

**C1 — Parameter assertion at dispatch.** Before sending, intersect the request's parameter set with the eligible endpoints' `supported_parameters`. On mismatch, fail loudly with the dropped parameter named. Do not send a setting that will be discarded.

**C2 —** `max_tokens` **validation.** Reject or clamp (with a warning) any `max_tokens` exceeding the minimum `max_completion_tokens` across the agent's eligible endpoint set, and surface which endpoints it excludes.

**C3 — Record what actually served the call.** Log `provider` and quantization from the response body on every call, alongside `usage.completion_tokens` and `usage.completion_tokens_details.reasoning_tokens`. Without this, precision drift and reasoning spend are both invisible.

---

## Acceptance criteria

**Given** an agent configured `quantization: bf16` on a model served at both bf16 and fp4, **when** the dispatcher sends a request, **then** the request body contains `provider.quantizations: ["bf16"]` **and** the response's logged serving quantization is bf16.

**Given** an agent whose pinned provider returns 429, **when** `provider_allow_fallbacks` is true and other bf16 hosts exist, **then** the request succeeds on a different host at the same quantization **and** the substitution is logged.

**Given** an agent configured `temperature: 0.0` on an endpoint whose `supported_parameters` omits `temperature`, **when** the dispatcher assembles the request, **then** it fails loudly naming the unsupported parameter rather than sending a request whose temperature will be silently discarded.

**Given** an agent configured `max_tokens: 380000` on a model whose eligible endpoints cap at 98,304, **when** the configuration is saved or the request assembled, **then** the value is rejected with the endpoint cap and the excluded endpoints named.

**Given** a model served by nine endpoints at four quantizations, **when** the catalog ingest runs, **then** nine rows exist **and** at least one row per available quantization is present **and** no row has been dropped by price-dedupe.

**Given** an agent configured `reasoning_effort: none` on an endpoint that rejects it, **when** the request is sent, **then** the 400 ("Reasoning is mandatory for this endpoint and cannot be disabled") is surfaced as a configuration error naming the agent, not retried as a transient failure.

---

## Out of scope

* Choosing which model each agent uses. Settings plumbing only.
* Prompt or persona changes.
* BYOK provider keys (separate ticket; worth doing, but provider routing across the bf16 set fixes the 429 without new accounts).

---

## Evidence / notes

Empirical findings from a 25-call effort sweep (`effort_analysis.txt`), which should inform validation rather than be rediscovered:

* `reasoning_effort: none` is **unavailable** on `z-ai/glm-5.3` and `openai/gpt-oss-120b`. Hard 400.
* Effort vocabularies are narrower than the parameter implies. GLM-5.3 returns identical token counts for `low`, `medium` and `high`. Values outside an endpoint's real set are coerced, not rejected.
* `max` is **non-monotonic** on `bytedance-seed/seed-2.0-mini` (1475 → 1080) and `ibm-granite/granite-4.2-8b` (2393 → 1370). Treat the effort field as a vocabulary, not an ordering.
* Reasoning tokens bill at the **output** rate and share the `max_tokens` budget with the answer. GLM-5.3 at `max` spent 172 output tokens to produce 7 tokens of answer. An effort setting with a tight `max_tokens` can return a 200 with an empty payload.
* `tencent/hy3` reports `reasoning_tokens: 0` while spending \~300 tokens per call. Cost cannot be attributed on that endpoint.
* Reasoning models forced to `none` emit their deliberation as **visible output** — seed returned 631 characters and granite 2,579 where the answer was 6. A model with no `reasoning` parameter at all has no such failure mode.

### Comments

#### chuckles — 2026-10-03T23:23:11.232Z
AST-1958 is blocked at merge-child: the plan commit already reached ftr through the shared-worktree leak into AST-1957, so validate-sub-log.sh reports missing plan(). It needs a validator decision from @susan (details on AST-1958).

#### chuckles — 2026-10-03T23:10:57.290Z
@susan AST-1956 held at Plan Approved (Hedy) — not spawning build-child: three engineers share one checkout in astral-AST-1953 with no worktree lock.
- Plan commits stacked across branches: sub/AST-1956 carries the AST-1957 and AST-1958 plan commits; sub/AST-1957 carries AST-1958's.
- 23:10: `code(AST-1958)` was committed onto sub/AST-1957 while Ada's build had it checked out, then reset away (shared worktree reflog). Ada and Katherine are both still building there.
- Need your call: serialize engineer builds per epic worktree, or give each child its own worktree, before Hedy builds.

#### chuckles — 2026-10-03T22:42:35.339Z
AST-1955 REVIEW — Joan needs plan discuss: AC6 stubbed-client check unmapped in plan.

#### chuckles — 2026-10-03T22:14:42.091Z
@susan — I've rescoped per your notes. There's no ingest or polling now, and the endpoint facts for the curated 95 slugs (every quantization each one's hosts serve) sit in `config.py`. I also folded in your answers: one model id per SKU, and mode retired. Remaining questions:

1. **Keep the C1/C2/C3 guardrails in this ticket?** They're in your brief's Scope C. I've kept them, backed by the config snapshot. Or should I ship settings + wiring only and move the guardrails to a follow-up?
2. **Quantization vocabulary.** I recommend OpenRouter's full list plus `any`, matched exactly. Should `unknown` (undisclosed precision) be selectable? I recommend no.
3. **Pricing once fallbacks are on.** (a) Price from the snapshot row of the endpoint that served the call. (b) Recommended: OpenRouter's `usage.cost` from the response. (c) Keep one static price per slug.
4. **Serving quantization isn't in any response.** Should I derive it from the snapshot (model + served provider + requested quantization)? I recommend yes.
5. **Configuration errors vs `patt.task.dispatch-retry`.** (a) Recommended: hold the entity in state, stop the batch and alert once, like balance refusal, with a pattern amendment. (b) `_RETRY` then ERROR.
6. **C1/C2 rules — confirm each:**
   - (i) `max_tokens` is exempt from C1 (C2 governs it).
   - (ii) A setting must be supported by every eligible endpoint.
   - (iii) `reasoning_effort` requires `reasoning`.
   - (iv) C2 rejects and never clamps.
   - (v) Should requests also send `provider.require_parameters: true`?
7. **Starting values for live agents.** Recommended: today's quantization, fallbacks on, today's temperature, and `reasoning_effort: none` where thinking is off today. gpt-oss-120b and glm-5.3 reject `none`. Should those start at null?

#### chuckles — 2026-10-03T21:55:48.619Z
@susan — open questions on the AST-1953 definition (my recommendation in each):

1. **Direct models without `brain_setting`.** Option (a), recommended: one model id per SKU (`claude-haiku-4-5` / `-sonnet-4-6` / `-opus-4-6`, `deepseek-v4-flash` / `-pro`, `kimi-k2.6`), with `quantization: any`, the DeepSeek 384k floor moved to the agent's `max_tokens`, and C1–C3 on OpenRouter only. Option (b): keep `brain_setting` for direct models only.
2. **`mode`: retire, or keep as a no-effect label?** I recommend retire. Thinking on/off becomes `reasoning_effort` (null = model default, `none` = off).
3. **Catalog home and refresh.** (a), recommended: a DB table refreshed by a Manage Agents button plus an operator CLI, with no schedule. (b): the same table, refreshed at startup or on a schedule. (c): a snapshot script that regenerates `config.py`. If the feed is down, should dispatch keep using the last stored catalog? I recommend yes.
4. **Catalog breadth.** Ingest all 335 ZDR models, or only the curated slugs? Either way, I recommend the model picker stays on the curated `config.py` list.
5. **Send `provider.zdr: true` on every OpenRouter request,** so routing can't land on a host outside the catalog? I recommend yes. AST-1946 left ZDR out of scope, so it's your call.
6. **Pricing once fallbacks are on.** (a), recommended: price each call from the catalog row of the endpoint that served it. (b): OpenRouter's `usage.cost`. (c): keep the static per-slug price.
7. **Quantization vocabulary.** I recommend OpenRouter's full list (`int4`, `int8`, `fp4`, `mxfp4`, `nvfp4`, `fp6`, `fp8`, `mxfp8`, `fp16`, `bf16`, `fp32`) plus `any`, matched exactly. Should `unknown` be selectable at all?
8. **Serving quantization isn't in any OpenRouter response.** I recommend deriving it from the catalog row for (model, served provider) filtered by the requested quantization. That's exact when the filter has a single value.
9. **Configuration errors vs `patt.task.dispatch-retry`** (whose rule is that every failure goes through `_RETRY`). (a), recommended: a configuration error joins the existing state-held path (like balance refusal): the entity stays in state, the batch stops, and one alert goes out; the pattern gets an amendment. (b): `_RETRY` then ERROR like any failure.
10. **C1/C2 rules — confirm each:**
    - (i) `max_tokens` is exempt from C1; C2 governs it.
    - (ii) A setting must be supported by every eligible endpoint.
    - (iii) `reasoning_effort` requires `reasoning` in `supported_parameters`.
    - (iv) C2 rejects and never clamps.
    - (v) Should requests also send `provider.require_parameters: true`?
11. **Starting values for live agents.** Recommended:
    - quantization = today's pinned host quantization (`any` on direct models);
    - fallbacks on, with no only/ignore/sort;
    - temperature = what the call sends today;
    - `reasoning_effort: none` where the call sends thinking-off today.

    gpt-oss-120b and glm-5.3 reject `none`. Should those agents start at null instead?
12. **"Pinned provider" in the 429 criterion.** There's no `order` field in the brief. I recommend no `order`; the served-provider log line records which host took each call. Or do you want a `provider_order` setting?

Also worth knowing: `dev` already pins each OpenRouter model to one host with fallbacks **off**. That pin is why DekaLLM's 429 stalled the pipeline. Details are under Purpose → As-built corrections in the Description.

---

_Implementation detail may live in git history on `origin/dev`._
