<!-- linear-archive: AST-1938 archived 2026-10-08 -->

## Linear archive (AST-1938)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1938/openrouter-model-shortlist-in-the-catalog-openrouter-support-models  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / 3  
**Parent:** AST-1937 — OpenRouter Support Models  
**Blocked by / blocks / related:** parent: AST-1937

### Description

## What this implements

Adds every brief slug as a selectable OpenRouter catalog model, with the brief's pricing, Little / Medium brain sizes, temperature-1 and capped output defaults, and the per-model upstream provider pin carried through the compat client. Also moves `kimi-k2.6-openrouter` onto its SiliconFlow pin and price. Nothing in routing, DB, or the admin UI changes, because they already read the catalog. Does **not** touch the Manage Task modal (#2).

## Citations

`stat.logging.debug` (the compat client's call/response debug lines keep logging the full body, pin included).

## Scope

* `src/utils/config.py` (**modified**):
  * **New table:** a new compact OpenRouter model table, keyed by slug, carrying each row's pricing, upstream provider, reasoning flag, and the pinned provider's max output tokens. These are literal snapshot values, with a one-line source/date comment like the existing pricing blocks.
  * **New builder:** a new builder function merges the table into `LLM_MODEL_CONFIG` after the hand-written entries. For each row it creates a model entry: server `openrouter`, label from the slug, Little (thinking off) and, when reasoning-capable, Medium (thinking on), temperature 1.0, capped output defaults, and one pricing row keyed by the slug. It skips any slug already priced on `openrouter` (today only `moonshotai/kimi-k2.6`), so `get_sku_pricing` never sees a duplicate.
  * **Modified tier schema:** each brain-size row gains an optional `request_extras` field (default empty) holding the provider pin.
  * **Modified** `kimi-k2.6-openrouter` **entry:** both of its brain sizes carry the SiliconFlow pin, and its pricing row changes to 0.77 / 3.4 / 0.14 / cache-write 0. Other hand-written entries are unchanged in behaviour.
  * **Modified validation:** `validate_llm_provider_environment` additionally checks that `request_extras` is a dict on every brain size and that every catalog SKU resolves through `get_sku_pricing` without ambiguity.
  * **Table shape is the builder's call:** row layout, field names, provider-slug spelling (OpenRouter's routing ids), and exact function names are `plan-child`'s.
* `src/external/llm_compat.py` (**modified**): the modified send function builds its `extra_body` from thinking payload + server `request_extras` + tier `request_extras`. The tier's extras win on key collision. The existing ungated call/response debug lines keep logging the full body, so the pin shows up in them.

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

## Boundaries

Does **not** touch the Manage Task modal, its tests, or bible rows (sibling #2 — Remove the Manage Task model picker). No routing, DB, admin route, or UI change.

## Notes for planning

Citations: `stat.logging.debug`. Pinned provider max-output and reasoning flags are build-time snapshots from OpenRouter (model listing / per-model endpoints) written as literals with a source/date comment. Susan decisions (parent Description): 76 models; Little + Medium (no Big on new models); pin provider, fallbacks off; kimi-k2.6-openrouter → SiliconFlow pin + 0.77/3.4/0.14, keeps Little/Big; temperature 1.0; 16k/32k capped.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1937-openrouter-support-models`, child `sub/AST-1937/AST-1938-openrouter-model-shortlist`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-02T18:20:57.725Z
[code-rubric] PROCEED (Commit: efab2e87c) OpenRouter catalog; rollup note

#### betty — 2026-10-02T18:17:07.097Z
`origin/sub/AST-1937/AST-1938-openrouter-model-shortlist` @ `099978e56` · manifest in config.md bible

#### joan — 2026-10-02T18:04:31.076Z
[plan-rubric] PROCEED (Commit: 57d2ef49c) OpenRouter catalog plan clean — context_tokens≈52000

#### katherine — 2026-10-02T18:02:19.411Z
`origin/sub/AST-1937/AST-1938-openrouter-model-shortlist` @ `57d2ef49c` · plan ready, 79 models

---

# AST-1938 — OpenRouter model shortlist in the catalog

- **Parent:** [AST-1937 — OpenRouter Support Models](https://linear.app/astralcareermatch/issue/AST-1937)
- **Ticket:** [AST-1938](https://linear.app/astralcareermatch/issue/AST-1938)
- **Publish ref:** `origin/sub/AST-1937/AST-1938-openrouter-model-shortlist`
- **Canon Scope:** `stat.logging.debug`. No pattern applies (parent § Architectural definition: `no established pattern applies`).

This ticket makes all 76 models from Susan's OpenRouter brief pickable in Manage Agents. They are served by the existing `openrouter` server and pinned to the upstream provider whose price is in the brief, so the timesheet ledger matches what OpenRouter bills. A compact table in `config.py` holds one row per brief slug: price, provider routing slug, reasoning flag, and the pinned provider's max output. A builder expands each row into a normal `LLM_MODEL_CONFIG` entry after the hand-written entries. Every new model offers Little. Reasoning-capable models also offer Medium. Defaults are temperature 1.0 and an output budget of 16k (Little) or 32k (Medium), each capped at the provider's max output. Brain-size rows gain an optional `request_extras` dict that carries the OpenRouter `provider` pin, and `llm_compat` merges it into `extra_body` after the server extras. The hand-written `kimi-k2.6-openrouter` entry gets the SiliconFlow pin and the brief's price, and keeps Little / Big. Routing, DB, admin routes, and the UI already read the catalog, so none of them change. The Manage Task modal is sibling AST-1939 and is out of scope here.

## Scope gate

Every row in **Files Changed** is named in this ticket's `## Scope`. Every stage is the kind of change Scope describes for that file.

- `src/utils/config.py`: new table, new builder, optional tier `request_extras`, the `kimi-k2.6-openrouter` pin and price, and the extended `validate_llm_provider_environment`. The small `_openrouter_pin` helper and the `OPENROUTER_TIER_DEFAULTS` / `OPENROUTER_PIN_QUANTIZATIONS` constants are parts of the table and builder (Scope: "Table shape is the builder's call … exact function names are plan-child's"). The config header inventory line is documentation for the new table.
- `src/external/llm_compat.py`: the `extra_body` merge only. The existing `logger.debug("Calling messages.create: …", api_kwargs)` line is not touched, so it keeps logging the full body including the pin (`stat.logging.debug`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Header inventory line. New `OPENROUTER_MODEL_TABLE`, `OPENROUTER_PIN_QUANTIZATIONS`, `OPENROUTER_TIER_DEFAULTS`, and `_openrouter_pin()` before `LLM_MODEL_CONFIG`. `LLM_MODEL_CONFIG` schema comment gains `request_extras`. `kimi-k2.6-openrouter` pin and price. New `_build_openrouter_models()` plus its module-level call after `LLM_MODEL_CONFIG`. Two new checks in `validate_llm_provider_environment`. | utils |
| `src/external/llm_compat.py` | `extra_body` = thinking body + server `request_extras` + tier `request_extras` (tier wins) | external |

No other file is touched. No `tests/` or bible edits. Betty owns those (see **Tests expected to move**).

## Snapshot source (for reviewers)

Prices, including CACHE, are copied verbatim from the brief (parent § Original brief), as AC 2 requires. Provider routing slug, reasoning flag, and max output come from `GET https://openrouter.ai/api/v1/models/<slug>/endpoints`, snapshotted 2026-10-02. For each slug I used the endpoint whose `provider_name` equals the brief's PROVIDER:

- **Provider routing slug:** the part of the endpoint `tag` before `/`. Examples: `Mancer 2` → `mancer`, `Near AI` → `near-ai`, `OpenInference` → `open-inference`. OpenRouter's provider-routing docs say a base slug matches every endpoint that provider hosts for the model.
- **Reasoning:** `"reasoning" in supported_parameters`. The model listing (`/api/v1/models`) agrees with the pinned endpoint for all 76 slugs.
- **Max output:** the endpoint's `max_completion_tokens`.

Live endpoint prices differ from the brief by rounding on most rows, and by more on a few (for example `moonshotai/kimi-k3` input is 0.5 live vs 1.35 in the brief). The brief governs (AC 2), so this plan does not reconcile them.

---

## Stage 1: Catalog table, builder, tier `request_extras`, Kimi pin, validation (`config.py`)

**Done when:** `python -c "from src.utils.config import validate_llm_provider_environment as v, LLM_MODEL_CONFIG as C; v(); print(len(C))"` prints `79`. `LLM_MODEL_CONFIG["qwen/qwen3-32b"]["brain_sizes"]["Little"]["request_extras"] == {"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}`. `get_sku_pricing("moonshotai/kimi-k2.6", "openrouter")["cpm_input"] == 0.77`.

1. **Header inventory** (top-of-file docstring, `Config sections:`). Directly after the `LLM_MODEL_CONFIG  — …` line, insert:

   ```
     OPENROUTER_MODEL_TABLE — OpenRouter shortlist rows expanded into LLM_MODEL_CONFIG (price, provider pin, reasoning, max output) (AST-1938)
   ```

2. **New block** between `ALLOWED_TIMESHEET_PROVIDERS = tuple(LLM_SERVER_CONFIG)` and the `# LLM_MODEL_CONFIG — what an agent row picks` comment banner. Insert exactly this, with the table rows from **Appendix A** in the order shown there:

   ```python
   # ---------------------------------------------------------------------------
   # OPENROUTER_MODEL_TABLE — OpenRouter shortlist (AST-1937 brief). slug → (cpm_input, cpm_output,
   #   cpm_cache_read, provider routing slug, reasoning-capable, pinned provider max output tokens).
   # Prices: Susan's brief (AST-1937, 2026-10). Provider slug / reasoning / max output:
   #   https://openrouter.ai/api/v1/models/<slug>/endpoints snapshot 2026-10-02 (brief's PROVIDER endpoint).
   # _build_openrouter_models() turns each row into an LLM_MODEL_CONFIG entry (model id = slug), skipping
   # slugs a hand-written entry already prices on openrouter.
   # ---------------------------------------------------------------------------
   OPENROUTER_MODEL_TABLE = {
       <Appendix A rows>
   }
   # Slug → extra OpenRouter quantization filter, for when the pinned provider hosts more than one
   # endpoint for the model and the brief's price is only one of them (DeepInfra turbo/fp4 vs fp8).
   OPENROUTER_PIN_QUANTIZATIONS = {
       "google/gemma-4-31b-it": ("fp8",),
   }
   # Brain sizes a table row expands into. Medium only when the row is reasoning-capable; no Big.
   # default_max_tokens = min(max_tokens_cap, row's pinned max output).
   OPENROUTER_TIER_DEFAULTS = {
       BRAIN_LITTLE: {"thinking": False, "thinking_params": {}, "default_temperature": 1.0, "max_tokens_cap": 16000},
       BRAIN_MEDIUM: {
           "thinking": True,
           "thinking_params": {"thinking": {"type": "adaptive"}},
           "default_temperature": 1.0,
           "max_tokens_cap": 32000,
       },
   }


   def _openrouter_pin(slug: str) -> Dict[str, Any]:
       """Tier request_extras pinning a table slug to its upstream provider, fallbacks off."""
       pin: Dict[str, Any] = {"order": [OPENROUTER_MODEL_TABLE[slug][3]], "allow_fallbacks": False}
       if slug in OPENROUTER_PIN_QUANTIZATIONS:
           pin["quantizations"] = list(OPENROUTER_PIN_QUANTIZATIONS[slug])
       return {"provider": pin}
   ```

   ⚠️ **Decision:** the pin is `{"provider": {"order": [<slug>], "allow_fallbacks": False}}`. This is the "disable fallbacks" shape in OpenRouter's provider-routing docs: the request goes to the named provider or fails. It satisfies AC 5 ("naming only the brief's provider … with fallbacks off").

   ⚠️ **Decision:** routing slugs are **base** slugs (`deepinfra`, not the endpoint `tag` such as `deepinfra/fp8`). The docs only confirm suffixed slugs for real variants like `/turbo` or regions, not for the quantization part of `tag`. `google/gemma-4-31b-it` is the only brief slug whose pinned provider has two endpoints (DeepInfra `turbo` fp4 at 0.09/0.34/0.05 and default fp8 at 0.15/0.4, which is the brief price). It uses the documented `quantizations: ["fp8"]` filter so the billed endpoint matches the catalog price.

3. **`LLM_MODEL_CONFIG` schema comment.** In the comment banner above `LLM_MODEL_CONFIG = {`, directly after the line `#     default_temperature / default_max_tokens — used when the agent row leaves them null`, insert:

   ```
   #     request_extras      — optional dict (default {}): body fields for this size only, merged after the
   #                           server's request_extras (size wins). OpenRouter provider pin (AST-1938).
   ```

4. **`kimi-k2.6-openrouter` entry.**
   - In **both** `BRAIN_LITTLE` and `BRAIN_BIG` dicts, add `"request_extras": _openrouter_pin("moonshotai/kimi-k2.6"),` as the last key, after `"default_max_tokens"`. Change nothing else in those dicts: Little keeps 0.6 / 16000, Big keeps adaptive thinking, 1.0 / 32000.
   - Replace the comment `# OpenRouter bills per upstream host; catalog uses Moonshot list price (conservative).` with `# Pinned to SiliconFlow (AST-1938); brief price 2026-10 — that host's OpenRouter rate.`
   - In its `"moonshotai/kimi-k2.6"` pricing row, set `"cpm_input": 0.77`, `"cpm_output": 3.4`, `"cpm_cache_read": 0.14`. `cpm_cache_write` stays `0.0`, `cache_min_tokens` stays `0`, `model_label` is unchanged.

5. **New builder** directly after the closing `}` of `LLM_MODEL_CONFIG` and before `def get_llm_server`:

   ```python
   def _build_openrouter_models() -> None:
       """Append one LLM_MODEL_CONFIG entry per OPENROUTER_MODEL_TABLE row (AST-1938). Model id, label,
       SKU and pricing key are all the slug; slugs a hand-written entry already prices on openrouter
       are skipped so get_sku_pricing never sees a duplicate."""
       priced = {sku for m in LLM_MODEL_CONFIG.values() if m["server"] == "openrouter" for sku in m["pricing"]}
       for slug, (cpm_in, cpm_out, cpm_cache, _provider, reasoning, max_out) in OPENROUTER_MODEL_TABLE.items():
           if slug in priced:
               continue
           sizes = (BRAIN_LITTLE, BRAIN_MEDIUM) if reasoning else (BRAIN_LITTLE,)
           LLM_MODEL_CONFIG[slug] = {
               "label": slug,
               "server": "openrouter",
               "brain_sizes": {
                   bs: {
                       "sku": slug,
                       "thinking": OPENROUTER_TIER_DEFAULTS[bs]["thinking"],
                       "thinking_params": OPENROUTER_TIER_DEFAULTS[bs]["thinking_params"],
                       "max_tokens_floor": None,
                       "default_temperature": OPENROUTER_TIER_DEFAULTS[bs]["default_temperature"],
                       # Capped at the pinned provider's max output so the vendor never rejects the default.
                       "default_max_tokens": min(OPENROUTER_TIER_DEFAULTS[bs]["max_tokens_cap"], max_out),
                       "request_extras": _openrouter_pin(slug),
                   }
                   for bs in sizes
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


   _build_openrouter_models()
   ```

   ⚠️ **Decision:** the model id **and** label are the bare slug, for example `qwen/qwen3-32b`. AC 3 and AC 4 use slugs as model ids (`model_brain_sizes("gryphe/mythomax-l2-13b")`). The slug is also the name Susan sees in her brief and on OpenRouter, so no prettified label is derived.

   ⚠️ **Decision:** the cap uses each row's **pinned-provider** max output, as Technical scope and AC 7 require. On the 2026-10-02 snapshot that lowers the Little default below 16000 for **seven** models, not the five the parent's functional scope item 5 lists. The five are `anthracite-org/magnum-v4-72b` (4096), `gryphe/mythomax-l2-13b` (7372), `tencent/hy-mt2-30b-a3b` (4096), `tencent/hy-mt2-7b` (4096), and `undi95/remm-slerp-l2-13b` (5529). The other two are `meta-llama/llama-4-maverick` (Novita, 8192) and `openai/gpt-oss-20b` (SiliconFlow, 8192, and its Medium is also 8192). The model listing's `top_provider` shows 16384 / 32768 for those two, but that is not the pinned host. A 16000 default there would be rejected by the pinned provider. AC 7's formula governs, so the builder applies it uniformly and no per-model list exists.

6. **`validate_llm_provider_environment`.** Inside the `for bs, tier in m["brain_sizes"].items():` loop, after the existing `if tier["sku"] not in m["pricing"]: raise …` statement, add:

   ```python
               if not isinstance(tier.get("request_extras", {}), dict):
                   raise ValueError(f"LLM model {mid!r} {bs}: request_extras must be a dict")
               # Raises on an unknown or ambiguous SKU for this server (AST-1938).
               get_sku_pricing(tier["sku"], m["server"])
   ```

   ⚠️ **Decision:** the ambiguity check is server-scoped (`server_id=m["server"]`). That is how runtime pricing calls it (`llm_compat` → `calculate_cost_components_from_counts(..., server_id=server_id)`) and how AC 2 asserts. The same SKU on two different servers stays legal, as `get_sku_pricing`'s design already allows.

   Hand-written tiers other than `kimi-k2.6-openrouter` do **not** gain a `request_extras` key. It is optional, and both readers (step 6 and Stage 2) default it to `{}`.

**Stage commit:** `code(AST-1938): OpenRouter shortlist table + builder, tier request_extras, Kimi SiliconFlow pin`

---

## Stage 2: Tier extras on the wire (`llm_compat.py`)

**Done when:** a stubbed `_get_client` call on `qwen/qwen3-32b` Little sends `extra_body == {"thinking": {"type": "disabled"}, "provider": {"order": ["deepinfra"], "allow_fallbacks": False}}`. A `kimi-k2.6` (Kimi direct) call's `extra_body` has no `provider` key. The `Calling messages.create` debug line still prints the full `api_kwargs`.

1. In `send_to_llm_compat`, replace these two lines:

   ```python
           # Thinking + server extras are vendor body fields taken verbatim from config.
           api_kwargs["extra_body"] = {**thinking_body, **server["request_extras"]}
   ```

   with:

   ```python
           # Thinking + server extras + brain-size extras (OpenRouter provider pin) are vendor body fields
           # taken verbatim from config; later wins on key collision, so the size's extras beat the server's.
           api_kwargs["extra_body"] = {**thinking_body, **server["request_extras"], **tier.get("request_extras", {})}
   ```

2. Do **not** edit `logger.debug("Calling messages.create: server=%s %s", server_id, api_kwargs)` or `logger.debug("Response from messages.create: %s", response)`. They stay ungated, untruncated, and log the full body including the pin (`stat.logging.debug`).

**Stage commit:** `code(AST-1938): llm_compat merges tier request_extras into extra_body`

---

## Verification (build-child §7, before each commit)

- `python -m py_compile src/utils/config.py src/external/llm_compat.py`
- `ruff check src/utils/config.py src/external/llm_compat.py` (if `ruff` is not installed, `python -m pyflakes` on the same files)
- After Stage 1, run the AC 1/2/3/7/8 checks from the ticket as `python -c` scripts. The 76 slugs and brief prices come from parent § Original brief. Expected results: `[]` for AC 1, no mismatches for AC 2, 47 models at `('Little', 'Medium')` and 28 at `('Little',)` for AC 3, no violators for AC 7, and 79 for AC 8.
- AC 6 grep (`rg … src/ --glob '!src/utils/config.py'`) returns nothing. Baseline on this branch is already empty.

## Tests expected to move (Betty, `qa-child`)

Not edited here (test tree is off-limits to engineers). Listed so the manifest can account for them:

- `tests/component/external/test_llm_compat.py`:
  - About line 100: a `kimi-k2.6-openrouter` Little call asserts `extra_body == thinking_off_params`. It now also carries the SiliconFlow `provider` pin.
  - About line 108: the Big call asserts `extra_body == {"thinking": {"type": "adaptive"}}`. It now also carries the pin.
  - About line 81: the server `request_extras` `provider` override on openrouter. The tier pin now wins on the `provider` key, by design.
- `tests/component/utils/test_config.py` near line 7093 still holds, because the server-level `request_extras` stays `{}`.
- `tests/component/ui/api/test_api_admin.py:40` (catalog order equals `LLM_MODEL_CONFIG` order) should still hold with 79 entries.
- New coverage the ticket's ACs call for: AC 4 (agent PUT with model-scoped sizes) and AC 5 (pin on the wire).

## Estimate

Confirm Chuckles estimate: 3 — agree

---

## Appendix A — `OPENROUTER_MODEL_TABLE` rows (paste verbatim, 4-space indent, in this order)

```python
    "anthracite-org/magnum-v4-72b": (2.5, 5.0, 0.0, "mancer", False, 4096),
    "bytedance-seed/seed-1.6": (0.25, 2.0, 0.0, "seed", True, 32768),
    "bytedance-seed/seed-1.6-flash": (0.08, 0.3, 0.0, "seed", True, 32768),
    "bytedance-seed/seed-2-1-turbo": (0.5, 2.5, 0.0, "seed", True, 235929),
    "bytedance-seed/seed-2.0-code": (0.5, 3.0, 0.0, "seed", True, 131072),
    "bytedance-seed/seed-2.0-lite": (0.25, 2.0, 0.0, "seed", True, 131072),
    "bytedance-seed/seed-2.0-mini": (0.1, 0.4, 0.0, "seed", True, 131072),
    "deepseek/deepseek-chat-v3-0324": (0.25, 1.0, 0.0, "siliconflow", False, 147456),
    "deepseek/deepseek-chat-v3.1": (0.27, 1.0, 0.0, "siliconflow", True, 147456),
    "deepseek/deepseek-r1-0528": (0.5, 2.18, 0.0, "siliconflow", True, 147456),
    "deepseek/deepseek-v3.1-terminus": (0.27, 1.0, 0.0, "siliconflow", True, 147456),
    "deepseek/deepseek-v3.2": (0.26, 0.42, 0.14, "siliconflow", True, 147456),
    "deepseek/deepseek-v3.2-exp": (0.27, 0.41, 0.0, "siliconflow", True, 147456),
    "deepseek/deepseek-v4-flash": (0.0, 1.6, 0.0, "open-inference", True, 943718),
    "deepseek/deepseek-v4-flash-0731": (0.0, 1.6, 0.0, "open-inference", True, 943718),
    "deepseek/deepseek-v4-flash-vision-exp": (0.22, 0.65, 0.01, "deepinfra", True, 262144),
    "deepseek/deepseek-v4-pro": (1.3, 2.6, 0.1, "deepinfra", True, 16384),
    "deepseek/deepseek-v4-pro-0813": (1.06, 3.17, 0.04, "nextbit", True, 943718),
    "deepseek/deepseek-v4.1-flash": (0.02, 0.38, 0.01, "morph", True, 943718),
    "google/gemma-3-27b-it": (0.08, 0.16, 0.0, "deepinfra", False, 16384),
    "google/gemma-4-26b-a4b-it": (0.07, 0.34, 0.0, "deepinfra", True, 16384),
    "google/gemma-4-31b-it": (0.15, 0.4, 0.0, "deepinfra", True, 16384),
    "gryphe/mythomax-l2-13b": (0.35, 0.6, 0.0, "mancer", False, 7372),
    "meta-llama/llama-3.1-70b-instruct": (0.4, 0.4, 0.0, "deepinfra", False, 16384),
    "meta-llama/llama-3.3-70b-instruct": (0.1, 0.32, 0.0, "deepinfra", False, 16384),
    "meta-llama/llama-4-maverick": (0.27, 0.85, 0.0, "novita", False, 8192),
    "meta-llama/llama-4-scout": (0.1, 0.3, 0.0, "deepinfra", False, 16384),
    "mistralai/mistral-nemo": (0.02, 0.03, 0.0, "dekallm", False, 104857),
    "mistralai/mistral-small-24b-instruct-2501": (0.05, 0.08, 0.0, "deepinfra", False, 16384),
    "mistralai/mistral-small-3.2-24b-instruct": (0.08, 0.2, 0.0, "deepinfra", False, 16384),
    "moonshotai/kimi-k2-0905": (0.6, 2.5, 0.0, "novita", False, 98304),
    "moonshotai/kimi-k2.6": (0.77, 3.4, 0.14, "siliconflow", True, 235929),  # priced + kept Little/Big by hand-written kimi-k2.6-openrouter (builder skips); pin reads this row
    "moonshotai/kimi-k3": (1.35, 11.36, 0.29, "morph", True, 943718),
    "morph/morph-v3-large": (0.9, 1.9, 0.0, "morph", False, 131072),
    "nousresearch/hermes-3-llama-3.1-405b": (1.0, 1.0, 0.0, "deepinfra", False, 16384),
    "nousresearch/hermes-3-llama-3.1-70b": (0.7, 0.7, 0.0, "deepinfra", False, 16384),
    "nvidia/nemotron-3-nano-30b-a3b": (0.05, 0.2, 0.03, "crusoe", True, 235929),
    "nvidia/nemotron-3-super-120b-a12b": (0.08, 0.45, 0.0, "dekallm", True, 235929),
    "openai/gpt-oss-120b": (0.05, 0.28, 0.0, "mancer", True, 117964),
    "openai/gpt-oss-20b": (0.04, 0.18, 0.0, "siliconflow", True, 8192),
    "qwen/qwen-2.5-72b-instruct": (0.36, 0.4, 0.0, "deepinfra", False, 16384),
    "qwen/qwen2.5-vl-72b-instruct": (0.8, 1.0, 0.4, "parasail", False, 115200),
    "qwen/qwen3-14b": (0.12, 0.24, 0.0, "deepinfra", True, 16384),
    "qwen/qwen3-235b-a22b-2507": (0.09, 0.58, 0.0, "novita", False, 16384),
    "qwen/qwen3-30b-a3b": (0.12, 0.5, 0.0, "deepinfra", True, 16384),
    "qwen/qwen3-30b-a3b-instruct-2507": (0.09, 0.3, 0.0, "siliconflow", False, 235929),
    "qwen/qwen3-32b": (0.08, 0.28, 0.0, "deepinfra", True, 16384),
    "qwen/qwen3-coder-30b-a3b-instruct": (0.07, 0.28, 0.0, "siliconflow", False, 235929),
    "qwen/qwen3-next-80b-a3b-instruct": (0.09, 1.1, 0.0, "deepinfra", False, 16384),
    "qwen/qwen3-vl-235b-a22b-instruct": (0.2, 0.88, 0.11, "deepinfra", False, 16384),
    "qwen/qwen3-vl-30b-a3b-instruct": (0.15, 0.6, 0.0, "deepinfra", False, 16384),
    "qwen/qwen3.5-27b": (0.25, 2.0, 0.0, "siliconflow", True, 235929),
    "qwen/qwen3.5-35b-a3b": (0.14, 1.0, 0.05, "deepinfra", True, 81920),
    "qwen/qwen3.5-397b-a17b": (0.45, 3.0, 0.22, "deepinfra", True, 81920),
    "qwen/qwen3.5-9b": (0.1, 0.15, 0.0, "siliconflow", True, 235929),
    "qwen/qwen3.6-27b": (0.3, 3.2, 0.0, "siliconflow", True, 235929),
    "qwen/qwen3.6-35b-a3b": (0.1, 0.9, 0.05, "akashml", True, 235929),
    "qwen/qwen3.8-2.4t-a95b": (2.0, 6.0, 0.25, "siliconflow", True, 131072),
    "qwen/qwen3.8-27b": (0.09, 2.2, 0.09, "ionstream", True, 65536),
    "sao10k/l3.1-euryale-70b": (0.85, 0.85, 0.0, "deepinfra", False, 16384),
    "stepfun/step-3.7-flash": (0.2, 1.15, 0.04, "novita", True, 256000),
    "tencent/hunyuan-a13b-instruct": (0.14, 0.57, 0.0, "siliconflow", True, 117964),
    "tencent/hy-mt2-30b-a3b": (0.07, 0.3, 0.0, "tencent", False, 4096),
    "tencent/hy-mt2-7b": (0.07, 0.3, 0.0, "tencent", False, 4096),
    "tencent/hy4-preview": (0.83, 2.5, 0.04, "deepinfra", True, 131072),
    "thedrummer/skyfall-36b-v2": (0.55, 0.8, 0.25, "parasail", False, 29491),
    "undi95/remm-slerp-l2-13b": (0.35, 0.65, 0.0, "mancer", False, 5529),
    "xiaomi/mimo-v2.5": (0.4, 2.0, 0.08, "venice", True, 65536),
    "xiaomi/mimo-v2.6-flash": (0.14, 0.28, 0.0, "deepinfra", True, 943718),
    "xiaomi/mimo-v2.6-pro": (0.43, 0.87, 0.0, "deepinfra", True, 943718),
    "z-ai/glm-4.7-flash": (0.06, 0.4, 0.01, "venice", True, 16384),
    "z-ai/glm-5": (1.0, 3.2, 0.2, "venice", True, 32000),
    "z-ai/glm-5.1": (1.4, 4.4, 0.0, "nebius", True, 182476),
    "z-ai/glm-5.2": (0.25, 3.07, 0.2, "morph", True, 943718),
    "z-ai/glm-5.3": (0.19, 2.99, 0.15, "morph", True, 943718),
    "z-ai/glm-5.3-flash": (0.11, 0.35, 0.02, "near-ai", True, 943718),
```


## Joan validate

[plan-rubric]
**Ticket:** AST-1938
**Overall:** APPROVED
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (tree `canon/` at publish tip; no `docs/canon-index.md` on ref — `stat.logging.debug` read from `canon/directives/active/` on same tip)
**Publish ref:** `57d2ef49cb3a65c4d0d058a0776c708b9de55b7c`

## Canon scores

stat.logging.debug | A | | Stage 2: leaves both `Calling messages.create` / `Response from messages.create` debug lines ungated and full-body; Scope gate cites statute

## Traceability

1→S1 `_build_openrouter_models` + Verification AC1 | 2→Appendix A + S1 pricing + Verification AC2 | 3→S1 `OPENROUTER_TIER_DEFAULTS` / reasoning flag + Verification AC3 (47+28; kimi Little/Big hand entry) | 4→Tests expected (Betty `qa-child`); product is catalog-only — existing admin PUT path | 5→S2 tier `request_extras` merge + Betty `test_llm_compat` | 6→Verification `rg` AC6 | 7→S1 `min(cap, max_out)` + Verification AC7 | 8→S1 `validate_llm_provider_environment` + Verification AC8 | parent FS6 / AC re task modal→N/A (AST-1939)

## Findings

### discuss

- **Severity:** discuss
- **Location:** Stage 1 decision (seven vs five lower Little caps)
- **Finding:** Parent functional scope item 5 names five slugs with sub-16k Little defaults; the plan applies AC 7’s `min(16000, pinned max)` uniformly and documents two additional slugs (`meta-llama/llama-4-maverick`, `openai/gpt-oss-20b`) whose pinned-host max is 8192.
- **Recommendation:** No plan change — AC 7 on the child ticket governs; Susan already signed brief-priced caps in Notes. Keep the documented decision for UAT expectations.

### acceptable

- **Severity:** acceptable
- **Location:** **Tests expected to move**
- **Finding:** AC 4 and AC 5 component assertions are explicitly deferred to Betty (`qa-child`); engineer stages touch only `config.py` and `llm_compat.py`, matching child Scope and parent partition (#1 vs #2).
- **Recommendation:** None — standard epic handoff; manifest should list AC 4/5 rows from plan.

- **Severity:** acceptable
- **Location:** **Snapshot source**
- **Finding:** Live OpenRouter endpoint prices often differ from the brief; plan states brief wins (AC 2) and does not reconcile — correct for ledger intent.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** **Scope gate** / Boundaries
- **Finding:** Files Changed and stages stay inside ticket `## Scope`; no `AdminTaskPrompts`, tests, or bible edits; sibling AST-1939 boundary repeated in plan intro.
- **Recommendation:** None.

- **Severity:** acceptable
- **Location:** **Estimate**
- **Finding:** Plan confirms estimate 3; large Appendix A is data paste, not extra engineering surface beyond two staged commits and verification scripts.
- **Recommendation:** None.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: 57d2ef49c) OpenRouter catalog plan clean


## Review

- **Branch:** `origin/sub/AST-1937/AST-1938-openrouter-model-shortlist`
- **Build tip:** `422ba2c73` (stages: `e6036a3b5` shortlist table + builder, tier `request_extras`, Kimi SiliconFlow pin + price, validation · `422ba2c73` `llm_compat` merges tier `request_extras` into `extra_body`)
- **Build notes:** Built as planned, with one literal mismatch. Stage 2 step 1 quotes the comment and the `extra_body` line as adjacent, but `thinking_on` / `thinking_body` sit between them. Both lines were replaced in place with the planned text, and the lines between them are unchanged. Verified on the shipped tree: `validate_llm_provider_environment()` passes. AC 1 `[]`; AC 2 no mismatches; AC 3 47 × `('Little', 'Medium')` + 28 × `('Little',)`, `kimi-k2.6-openrouter` `('Little', 'Big')`; AC 6 grep empty; AC 7 no violators; 79 catalog models (AC 8). Stubbed-client smoke for AC 5: `qwen/qwen3-32b` Little/Medium → `provider.order == ["deepinfra"]`, `allow_fallbacks: False`. `kimi-k2.6-openrouter` Big → `["siliconflow"]`. `google/gemma-4-31b-it` adds `quantizations: ["fp8"]`. `kimi-k2.6` (Kimi direct) has no `provider` key. Lint: `py_compile` clean, `ruff --select F,E9` clean.
- **For qa-child:** see **Tests expected to move** above. AC 4 and AC 5 need new component coverage.


## Radia review

[code-rubric]
**Ticket:** AST-1938
**Publish ref:** `efab2e87ca0af8fc604166387256a932242f6311` (`origin/sub/AST-1937/AST-1938-openrouter-model-shortlist`)
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned) — Joan graded `stat.logging.debug` **A**; diff leaves `logger.debug("Calling messages.create: …", api_kwargs)` and the response line ungated, so the merged `extra_body` (including tier `request_extras` / provider pin) still logs in full.

## Frame diff

(none)

## Findings

### discuss

- **Severity:** discuss  
- **Location:** **Boundaries** vs three-dot diff  
- **Finding:** Ticket boundaries exclude the Manage Task modal (`AdminTaskPrompts.tsx`). The publish ref’s `origin/dev…origin/sub/AST-1937/AST-1938-openrouter-model-shortlist` diff includes the full AST-1939 modal removal (158-line hunk, identical to the AST-1939 sub), plus `docs/features/agent/ast-1939-remove-the-manage-task-model-picker.md` (with AST-1939 Radia artifact), from `sync(ftr)` / merged sibling history (`fb6a5e37e`, `69a946461`, etc.). AST-1938’s own product commits are `config.py` + `llm_compat.py` only.  
- **@susan:** For child sign-off, is it acceptable that AST-1938’s publish ref is an epic rollup (both children) rather than a single-child diff, or should subs be rebased/split so each child’s review diff is scope-pure before **User Testing**?  
- **Default:** Treat as pipeline rollup for parent UAT; attribute modal work to AST-1939 only in release notes; no AST-1938 `resolve-child` work on `AdminTaskPrompts.tsx`.

### advisory

- **Severity:** advisory  
- **Location:** `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx`, `docs/test-bible/frontend/pages.md`  
- **Finding:** Diff includes AST-1939 test/bible retire/invert plus AST-1938 coverage (`test_config.py`, `test_llm_compat.py`, `test_api_admin.py`, bibles). Expected after `merge-tests` / ftr sync on a shared parent; not AST-1938 product scope.

### fix-now

(none) — OpenRouter catalog work on tip matches plan stages and ticket ACs; engineer build notes and component tests cover AC 4–5 where Betty landed them.

## What's solid

- **`src/utils/config.py`:** 76-row `OPENROUTER_MODEL_TABLE`, `_build_openrouter_models()`, tier `request_extras` via `_openrouter_pin()`, Kimi OpenRouter pin + brief pricing, validation extended (`request_extras` dict + `get_sku_pricing` per tier). Local `validate_llm_provider_environment()` passes; **79** models total / **76** OpenRouter entries on tip.  
- **`src/external/llm_compat.py`:** `extra_body` merge order thinking → server → tier (tier wins); debug lines unchanged and still log full `api_kwargs`.  
- **Tests/bible:** AC 4 agent PUT size guards (`test_api_admin.py`), AC 5 wire pins (`test_llm_compat.py` describe), catalog/pricing/brief fixture (`test_config.py`, `ast1937_openrouter_brief.txt`), bibles updated.  
- **AC 6:** No brief slug literals under `src/` outside `config.py` on the shipped tree (spot-checked via `git grep` on publish ref, excluding tests/docs).  
- **Plan fidelity:** Stage 1–2 delivered; Stage 2 comment/`extra_body` ordering note in issue doc (thinking lines between comment and assignment) is cosmetic only.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1938): Radia review — findings` (discuss rollup note) or `— clean` if Susan accepts default; post slim upshot; **Review Posted**.  
- If scope-pure child diffs are required before UT: rebase AST-1938 sub to exclude AST-1939 product commits (downstream merge-child/ftr policy — not Radia product fix).  
- UAT: Manage Agents catalog count (~79), spot OpenRouter models + pins; Manage Task modal behavior is AST-1939, not this ticket.

context_tokens≈32000



## Resolution

2026-10-02. Resolved against Radia's review at `c25ee00c9`, which was CLEAN with no fix-now items.

- **Discuss (publish ref is an epic rollup):** Susan had not answered, so I took Radia's `Default:`. The AST-1939 Manage Task modal removal and its plan, tests, and bible appear in this sub's `origin/dev…` diff only because `sync(ftr)` brought the merged sibling in from `origin/ftr/AST-1937-openrouter-support-models`. That is pipeline rollup for parent UAT. The modal work is credited to AST-1939, and AST-1938 makes no change to `AdminTaskPrompts.tsx`. AST-1938's own product commits are still only `src/utils/config.py` and `src/external/llm_compat.py`. Susan can reverse this by asking for scope-pure child subs. That would be a merge-child / ftr policy change, not a product fix here.
- **Advisory (sibling tests and bible in diff):** no action. This is expected after `merge-tests` and the ftr sync on a shared parent.
- **Product changes in resolve:** none.
