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
