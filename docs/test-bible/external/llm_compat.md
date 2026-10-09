# LLM Compat

**Test module:** `tests/component/external/test_llm_compat.py`

`src/external/llm_compat.py` — `send_to_llm_compat`, the one client for every `anthropic_compat` server in `LLM_SERVER_CONFIG` (AST-1851). Outbound body is intercepted at a stubbed `_get_client` → `messages.create`; no network.

### AST-1877 · AST-1851 (model/server catalog + shared compat client)

**Primary manifest:** **`docs/test-bible/utils/config.md`** § AST-1877.

| Area | Source | Component tests |
| --- | --- | --- |
| AC 9 — request extras in body; shipped OpenRouter no `provider.zdr` | `send_to_llm_compat` | `TestAst1877RequestExtras` |
| Thinking on/off body, temperature, system, extras merge order | `send_to_llm_compat` | `TestAst1877OutboundBody` |
| Non-compat / unknown server, empty SKU / key raise before request | `send_to_llm_compat` | `TestAst1877Guards` |
| Bearer → `auth_token`, x-api-key → `api_key` (single credential) | `_get_client` | `TestAst1877GetClient` |
| Result + timesheet contract (`provider=server_id`, `model_code=sku`), JSON, `max_tokens` truncation, hollow, parse error, create exception | `send_to_llm_compat` | `TestAst1877ResultContract` |
| Per-server slot cap + 429 backoff | `_create` | `TestAst1877ServerConcurrency` |

**Integration:** none.

### AST-1938 · AST-1937 (tier `request_extras` — OpenRouter provider pin)

**Primary manifest:** **`docs/test-bible/utils/config.md`** § AST-1938.

`extra_body` = thinking body + server `request_extras` + tier `request_extras`; the tier wins on key collision. Shipped OpenRouter tiers all carry a `provider` pin, so the AST-1877 Kimi-OpenRouter body assertions now include `{"provider": {"order": ["siliconflow"], "allow_fallbacks": false}}`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 5 shortlist Little / Medium pin DeepInfra only, fallbacks off; Kimi-OpenRouter (Little, Big) SiliconFlow only; gemma-4-31b quantization filter; direct Kimi / DeepSeek carry no `provider`; no non-openrouter catalog tier carries a pin (Claude rides `send_to_anthropic`, which never receives a tier); tier beats server on collision | `send_to_llm_compat` | `TestAst1938ProviderPin` |
| Revised — body now includes the SiliconFlow pin | `send_to_llm_compat` | `TestAst1877OutboundBody::test_thinking_off_sends_server_off_params_and_temperature` · `::test_thinking_on_sends_tier_params_and_omits_temperature` |
| Revised — AC 9 server extras checked on an unpinned tier copy (the shipped pin would win on `provider`); shipped body's `provider` is the pin and still has no `zdr` | `send_to_llm_compat` | `TestAst1877RequestExtras::test_configured_request_extra_appears_in_outbound_body` · `::test_shipped_openrouter_body_carries_no_zdr` |

**Integration:** none.

### AST-1947 · AST-1946 (mode-resolved tiers on the wire)

**Primary manifest:** **`docs/test-bible/utils/config.md`** § AST-1947.

`src/external/llm_compat.py` is unchanged. Stored sizes no longer carry `thinking`, so every test tier now comes from `cfg.resolve_model_brain(model, size, mode)["tier"]` (`_tier` / `_send_model` default Deterministic). `kimi-k2.6-openrouter` is retired: the default send is `moonshotai/kimi-k2.6` Little, pinned `{"order": ["inceptron"], "allow_fallbacks": false, "quantizations": ["int4"]}` (`KIMI_OR_PIN`). Every OpenRouter pin now carries `quantizations`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — Creative on a non-reasoning host (phi-4 Big) sends thinking-off params + temperature 0.6 ("think, else 0.6") | `send_to_llm_compat` | `TestAst1877OutboundBody::test_creative_on_non_thinking_host_sends_temperature` |
| Revised — Deterministic tier → thinking off + 0.2 on the wire; Creative on a reasoning host → adaptive thinking, temperature dropped; direct Kimi Big Creative → `enabled` payload before extras | `send_to_llm_compat` | `TestAst1877OutboundBody::test_thinking_off_sends_server_off_params_and_temperature` · `::test_thinking_on_sends_tier_params_and_omits_temperature` · `::test_extras_merge_after_thinking_body` |
| Revised — catalog pin with quantization in both modes (qwen3-32b Medium, fp8); Kimi on OpenRouter → Inceptron int4 in both modes; gemma-4-31b `fp4`; direct Kimi / DeepSeek carry no `provider` in either mode; tier beats server | `send_to_llm_compat` | `TestAst1938ProviderPin::test_catalog_deterministic_pins_host_quant_fallbacks_off` · `::test_catalog_creative_keeps_thinking_and_pin` · `::test_kimi_on_openrouter_names_only_inceptron` · `::test_quantization_filter_rides_with_pin` · `::test_direct_compat_servers_carry_no_provider` · `::test_tier_extras_win_over_server_extras` |
| Revised — default send / unpinned copy / zdr check retargeted to `moonshotai/kimi-k2.6` | `send_to_llm_compat` | `TestAst1877RequestExtras` (both nodes) |
| Retired (renamed above) | — | `TestAst1938ProviderPin::test_shortlist_little_pins_brief_provider_fallbacks_off` · `::test_shortlist_medium_keeps_thinking_and_pin` · `::test_kimi_openrouter_names_only_siliconflow` |

**Integration:** none.

> **AST-1956:** the AST-1938 / AST-1947 rows above (host pin, thinking-from-tier, mode temperature) describe a wire that no longer exists. See § AST-1956.

### AST-1956 · AST-1953 (send the agent's settings on the wire)

**Primary manifest:** **`docs/test-bible/core/agent.md`** § AST-1956.

`send_to_llm_compat` builds `extra_body = {**_effort_body(tier["reasoning_effort"]), **server["request_extras"], "provider": tier["provider"]}`; `provider` only when set, and the agent's object wins over a server extra. `_effort_body` (from `anthropic.py`): empty → `{}`, `"none"` → `{"thinking": {"type": "disabled"}}`, anything else → `{"output_config": {"effort": v}}`, no vocabulary. `temperature` is sent only when not `None` (0.0 is a value). No host pin, no `thinking_off_params`, no model lookup. Test tiers come from `cfg.resolve_agent_settings(model_id, settings)["tier"]` (`_tier(model_id="moonshotai/kimi-k2.6", **settings)`); the default send is `_tier(provider_allow_fallbacks=True)`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 1 provider object built from the agent row reaches `extra_body` as is | `send_to_llm_compat` | `TestAst1956SettingsOnTheWire::test_ac1_provider_object_from_the_agent_row` |
| New — AC 2 empty settings: no `temperature`, `extra_body == {}` | `send_to_llm_compat` | `::test_ac2_empty_settings_send_nothing` |
| New — AC 3 temperature / effort exactly as set (incl. 0.0 and `ultra`) | `send_to_llm_compat`, `_effort_body` | `::test_ac3_temperature_and_effort_exactly_as_set` (5) |
| New — AC 3 no gating on models that could not think (phi-4 on OpenRouter, deepseek-v4-pro) | `send_to_llm_compat` | `::test_ac3_no_gating_on_models_that_could_not_think` (2) |
| New — direct servers (kimi-k2.6, deepseek-v4-flash) get no `provider` object | `send_to_llm_compat` | `::test_direct_servers_get_no_provider_object` (2) |
| New — AC 4 a 400 rejection is `success: False` with the message, no `failure_class` | `send_to_llm_compat` | `::test_ac4_rejected_setting_is_a_plain_failure` |
| Revised — body shape with temperature + system; server extras merge after the effort body; agent `provider` wins over a server extra | `send_to_llm_compat` | `TestAst1877OutboundBody::test_body_shape_with_temperature_and_system` · `::test_server_extras_merge_after_effort_body` · `::test_agent_provider_wins_over_server_extra` |
| Revised — AC 9 server extras / shipped no-`zdr` checked on settings tiers | `send_to_llm_compat` | `TestAst1877RequestExtras` |

**Broken / obsolete:** `TestAst1938ProviderPin` (7, incl. `test_non_openrouter_catalog_tiers_carry_no_pin`) retired — host pins are gone. `TestAst1877OutboundBody::test_thinking_off_sends_server_off_params_and_temperature` · `::test_thinking_on_sends_tier_params_and_omits_temperature` · `::test_creative_on_non_thinking_host_sends_temperature` · `::test_extras_merge_after_thinking_body` retired / replaced by the revised rows above.

**Integration:** none.

### AST-1959 · AST-1954 (per-batch probe and host lock on the OpenRouter path)

**Primary manifest** (this file). Siblings: [`openrouter.md`](openrouter.md) (probe + host map), [`../utils/config.md`](../utils/config.md) § AST-1959 (`probe` flag, `LLM_PROBE_MESSAGE`, startup check), [`../utils/logging_batch.md`](../utils/logging_batch.md) § AST-1959 (`host=` on the INFO line).

On a `probe: True` server (OpenRouter only) with `log_batch_id` set, `send_to_llm_compat` asks `get_batch_host` for the batch key before the real call: success → `extra_body.provider = {**agent provider, "only": [host]}` (new dicts); remembered failure → `{"success": False, "error": "Host probe failed: …", "host": <label>}` with no request. Probe cost goes through `record_timesheet`. Every result carries `host` (response `provider`, else server label); the healthy summary passes `host=`. `_HostClient` (subclass of `_RecordingClient`) sets `provider` on responses and can raise on the probe only; `_is_probe` matches on the probe message content. `TestAst1959ProbeHostLock` clears `openrouter._hosts` per test and sets `log_batch_id` via the `batch` fixture.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 1 one awaited + three concurrent → 5 requests, first is the only probe | `send_to_llm_compat` | `TestAst1959ProbeHostLock::test_ac1_one_probe_per_batch_key_before_first_real_call` |
| New — AC 1 four concurrent first callers → 5 requests, one probe, probe first | `send_to_llm_compat` | `…::test_ac1_concurrent_first_callers_wait_on_one_probe` |
| New — AC 2 probe = real call minus content / system / host lock; no `cache_control`; agent's own `only` rides on the probe, host replaces it on the real call | `send_to_llm_compat` | `…::test_ac2_probe_matches_real_call_and_carries_no_cache` (2) |
| New — AC 3 later requests `provider == {quantizations: [bf16], allow_fallbacks: True, only: [DeepInfra]}`; agent tier dict not mutated | `send_to_llm_compat` | `…::test_ac3_warm_and_gather_locked_to_probe_host` |
| New — AC 4 probe 429 → no real request, all four calls `success: False`, `Host probe failed:`, host = label (**AST-2010** revised: 6 probe attempts, sleep patched, all four tagged `provider_rate_limit`) | `send_to_llm_compat` | `…::test_ac4_failed_probe_fails_the_batch_with_no_fallback` |
| New — AC 5 kimi / deepseek in a batch, openrouter with no batch id → no probe, no `only`, host = server label | `send_to_llm_compat` | `…::test_ac5_no_probe_outside_scope` (3) |
| New — AC 6 `host == "DeepInfra"` on result; one INFO line with `host=DeepInfra` | `send_to_llm_compat` | `…::test_ac6_host_on_result_and_info_line` |
| New — probe row then real row on the timesheet (same server + batch); probe row success / no note | `_record_probe` | `…::test_probe_cost_lands_on_the_timesheet` |
| New — a raising `record_timesheet` never fails the probe | `_record_probe` | `…::test_probe_timesheet_failure_never_fails_the_probe` |
| Revised — result keys gain `host`; no response `provider` → `"OpenRouter"` label | `send_to_llm_compat` | `TestAst1877ResultContract::test_success_shape_and_timesheet_kwargs` |
| Extended — create exception result carries `host` = label | `send_to_llm_compat` | `TestAst1877ResultContract::test_create_exception_returns_failure_dict` |

**Broken / obsolete:** `TestAst1877ResultContract::test_success_shape_and_timesheet_kwargs` (exact key set) — revised above. Existing sends set no `log_batch_id`, so no prior test reaches the probe.

**Integration:** none (no `tests/integration/` scenario reaches `llm_compat`, OpenRouter, or `log_batch_id`).

## QA test manifest

1. **Component (narrowed — must be all green, 157 on the publish tip):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_openrouter.py \
  tests/component/external/test_llm_compat.py \
  tests/component/utils/test_logging_batch.py \
  tests/component/utils/test_config.py::TestAst1877LlmCatalogConfig \
  tests/component/utils/test_config.py::TestAst1959ServerProbeFlag \
  tests/component/external/test_anthropic.py \
  tests/component/core/test_agent_ast1879.py \
  --deselect tests/component/external/test_anthropic.py::TestAst1190EmptyUnusableProviderResponse::test_hollow_stop_question_zero_tokens_fails_closed
```

`test_anthropic.py` / `test_agent_ast1879.py` are regression only (`anthropic.py` calls `log_llm_batch_summary` without `host`; agent routes to `send_to_llm_compat`). The deselected AST-1190 node asserts an ERROR record that AST-1839 made WARNING. It fails the same way with `origin/dev` product and is outside this ticket (same deselect as § AST-1877 in `utils/config.md`).

2. **AC 5 greps (expect no output):**

```bash
rg -n '"openrouter"' src/external/
git diff origin/dev...HEAD --stat -- src/core/dispatcher.py
```

3. **Whole file (informational — expected reds only):** `.venv/bin/python -m pytest tests/component/utils/test_config.py -q --tb=line` gives exactly the 21 pre-existing reds listed in [`../utils/config.md`](../utils/config.md) § AST-1947 item 2, which fail the same way with `origin/dev` product. Any other failure is real.

**Pass criterion:** item 1 green, item 2 empty, item 3 limited to those 21. Not the zero-arg harness.

### AST-1966 · AST-1963 (unpriced calls still get a timesheet row)

**Primary manifest:** [`../core/timesheets.md`](../core/timesheets.md) § AST-1966. `_timesheet_kwargs_for` always returns row kwargs: `calculate_cost_components_from_counts` raising → `calc_cost_*` all `0.0` (`CALC_COST_KEYS`) + one `logger.exception` ("timesheet catalog price"); `usage_to_token_counts` raising → counts 0 + one `logger.exception` ("timesheet token counts").

**Reach of the token-count fallback:** the main call path reads `usage_to_token_counts(response.usage)` itself before calling the helper (unchanged from `origin/ftr`), so an unreadable usage on the real call still fails the call with no row. The fallback is live only on the probe row (`_record_probe` calls the helper directly). Not an AC gap (AC 3 covers pricing); noted so the manifest does not overclaim. The `if kw is not None` / `if _timesheet_kwargs is not None` guards around `record_timesheet` are now always true.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 3 (llm_compat half): pricing raises → call succeeds, `record_timesheet` once, `calc_cost_*` all 0, usage counts (50 / 100 / 25 / 5), one ERROR with traceback | `_timesheet_kwargs_for` | `TestAst1966UnpricedRowRecorded::test_pricing_raises_row_recorded_with_zero_cost_and_counts` |
| New — probe response usage unreadable → probe row with zero tokens + zero cost, one ERROR; real call row normal | `_timesheet_kwargs_for` via `_record_probe` | `…::test_probe_token_counts_raise_row_recorded_with_zero_tokens` |
| New — failure path (unparseable JSON) + unpriced → one `failure` row, zero cost | `_timesheet_kwargs_for` | `…::test_failure_path_unpriced_row_still_recorded` |
| Kept — clean pricing row unchanged | — | `TestAst1877ResultContract::test_success_shape_and_timesheet_kwargs` |

No coverage regression: the AST-1966 hunk (helper try/except pair) is fully covered; the only new uncovered arc is `_record_probe`'s `kw is None` exit (now unreachable).

**Integration:** none.

### AST-2010 · AST-2009 (qa-fix bug-repro — OpenRouter 429 retry; exhausted 429 stops the batch)

**Parent:** [AST-2009](https://linear.app/astralcareermatch/issue/AST-2009) (orphaned-bug mini-parent). Fix child **AST-2010** (`origin/sub/AST-2009/AST-2010-openrouter-429-retry`); plan `docs/features/agent/ast-1877-model-server-catalog-compat-client.md` § Bug: AST-2010. Tests land on the fix child itself (no gap sibling). Contract: OpenRouter `concurrency = {"rate_limit_retries": 5, "backoff_base_seconds": 2.0, "exhausted_stops_batch": True}`. `_create` treats `max_concurrent` / `backoff_max_seconds` as optional (no slot, no ceiling when absent). Delay is `base · 2^attempt · uniform(0.5, 1.0)`. Only servers with `exhausted_stops_batch` tag an exhausted 429 `failure_class = "provider_rate_limit"`, on both the call path and the host-probe path. Balance still wins a tie. DeepSeek (4 retries, no opt-in) and Kimi (no block) stay untagged. The tag is forwarded by consult/roster; the dispatcher then stops the batch and the ledger finishes **FAILED**.

**Repro-first:** red at publish tip `c08219c32` (pre-fix) for the root-cause reasons. `_create` raises `KeyError: 'max_concurrent'` on a retry-only block. OpenRouter makes 1 call with no tag. The classifier and predicate are absent. Consult and roster drop `failure_class`. The dispatcher sends 2 × 3 = 6 and finishes COMPLETED. Green is `test-fix`'s to confirm after `make-fix`.

| Area | Source | Component tests |
| --- | --- | --- |
| Retry-only block: 6 calls, sleeps `[2, 4, 8, 16, 32]` (no ceiling), no `_slots` entry | `_create` | **`tests/component/external/test_llm_compat.py::TestAst2010OpenRouterRateLimit::test_retry_only_block_doubles_with_no_cap_or_ceiling`** (**bug-repro**) |
| Jitter kept: `uniform(0.5, 1.0)` per retry | `_create` | **`::TestAst2010OpenRouterRateLimit::test_retry_only_block_keeps_jitter`** |
| OpenRouter exhausted 429 (AST-2009 body): 6 calls, 5 sleeps, `failure_class == "provider_rate_limit"` | `send_to_llm_compat` | **`::TestAst2010OpenRouterRateLimit::test_openrouter_exhausted_429_is_tagged`** (**bug-repro**) |
| DeepSeek exhausted 429 → 5 calls, untagged; Kimi → 1 call, untagged (guard, green both) | `send_to_llm_compat` | **`::TestAst2010OpenRouterRateLimit::test_exhausted_429_untagged_without_opt_in`** |
| 429 carrying a balance substring → `provider_balance_refusal` (guard, green both) | `send_to_llm_compat` | **`::TestAst2010OpenRouterRateLimit::test_balance_wins_over_rate_limit`** |
| Probe 429 → 6 probe attempts, every caller tagged (real SDK str: the probe classifies a string) | probe branch | **`::TestAst1959ProbeHostLock::test_ac4_failed_probe_fails_the_batch_with_no_fallback`** (revised) |
| Classifier (status / `response.status_code` / substring on exception **or** string) + predicate | `llm_external` | **`tests/component/utils/test_llm_external.py::TestAst2010ProviderRateLimit`** |
| OpenRouter block, DeepSeek block unchanged + only OpenRouter opted in, `PROVIDER_RATE_LIMIT` registry | `config.py` | **`tests/component/utils/test_config.py::TestAst2010OpenRouterRetryConfig`** |
| Tag forwarded on every failure return (routing / counts unchanged; untagged stays untagged) | `consult.py` | **`tests/component/core/test_consult.py::TestAst2010RateLimitForwarding`** — see `core/consult.md` § AST-2010 |
| Tag forwarded on select / JOBS_FOUND / prefilter batch | `roster.py` | **`tests/component/core/test_roster.py::TestAst2010RateLimitForwarding`** — see `core/roster.md` § AST-2010 |
| Batch stop at all three call sites, loop stop, ledger FAILED | `dispatcher.py` | **`tests/component/core/test_dispatcher.py::TestAst2010ProviderRateLimitOutage`** — see `core/dispatcher.md` § AST-2010 |

**Kept:** `TestAst1877ServerConcurrency` (full four-key block, unchanged behavior).

**Pre-existing drift (not AST-2010, left as-is):** at `c08219c32` the six touched modules carry the same ~105-node failure set with and without this pass's tests (zero new failures besides the 31 intended reds).

**Integration:** none — do not invent.

## QA test manifest

1. **AST-2010 nodes** (**[bug-repro]** red pre-fix, green expected after `make-fix`):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_llm_compat.py::TestAst2010OpenRouterRateLimit \
  tests/component/external/test_llm_compat.py::TestAst1959ProbeHostLock \
  tests/component/external/test_llm_compat.py::TestAst1877ServerConcurrency \
  tests/component/utils/test_llm_external.py::TestAst2010ProviderRateLimit \
  tests/component/utils/test_llm_external.py::TestAst897ProviderBalanceRefusal \
  tests/component/utils/test_config.py::TestAst2010OpenRouterRetryConfig \
  tests/component/core/test_consult.py::TestAst2010RateLimitForwarding \
  tests/component/core/test_consult.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_roster.py::TestAst2010RateLimitForwarding \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_roster.py::TestAst1867BalanceHeldCounting \
  tests/component/core/test_dispatcher.py::TestAst2010ProviderRateLimitOutage \
  tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage \
  -q
```

Expect **all passed** with the AST-2010 fix. The AST-897 / AST-1867 / AST-1877 / AST-1959 classes are the "What must still hold" regressions (balance still INTERRUPTED + held; DeepSeek capped backoff unchanged).

2. **No-regression:** the six touched test modules' failure set must not grow beyond the pre-existing drift above (compare against `c08219c32`).

**Bible shasum (after publish):** `git show origin/sub/AST-2009/AST-2010-openrouter-429-retry:docs/test-bible/external/llm_compat.md | shasum`

### AST-2098 · AST-2099 (failed host probe tagged `provider_probe_failure`; missing usage reads zero)

**Primary manifest:** [`../core/dispatcher.md`](../core/dispatcher.md) § AST-2098. Contract: on a probe server inside a batch, any probe error that is not an exhausted 429 on a `stops_batch` server is tagged `failure_class = "provider_probe_failure"` (no fallback, nothing sent; waiters share the cached error so every caller is tagged alike). An exhausted 429 keeps AST-2010's `provider_rate_limit`. `usage=None` reads as zero tokens (`usage_to_token_counts`), so the hollow probe's timesheet row is written without AST-1966's ERROR traceback, and a hollow real call still takes AST-1190's `provider_empty_response`.

| Area | Source | Component tests |
| --- | --- | --- |
| AST-2016 hollow probe (no provider, no usage, error body): probe only, `failure_class == "provider_probe_failure"`, error names the body, host `OpenRouter`, one zero-token timesheet row, no ERROR record | probe branch + `_timesheet_kwargs_for` | **`tests/component/external/test_llm_compat.py::TestAst2098ProbeFailureTagged::test_hollow_probe_tagged_held_no_traceback`** |
| Non-429 probe exception → one probe, all four callers tagged | probe branch | **`::TestAst2098ProbeFailureTagged::test_non_429_probe_exception_tags_every_caller`** |
| Hollow real call on a non-probe server (`kimi`) → `provider_empty_response`, no ERROR record | main call path | **`::TestAst2098ProbeFailureTagged::test_hollow_real_call_is_empty_response_without_traceback`** |
| Exhausted 429 on the probe stays `provider_rate_limit` (AC 4 guard) | probe branch | **`::TestAst1959ProbeHostLock::test_ac4_failed_probe_fails_the_batch_with_no_fallback`** (unchanged) |

**Integration:** none — do not invent.
