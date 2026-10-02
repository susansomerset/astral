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
