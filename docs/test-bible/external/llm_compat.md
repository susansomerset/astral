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
