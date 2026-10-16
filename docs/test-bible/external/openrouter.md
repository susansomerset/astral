# OpenRouter

**Test module:** `tests/component/external/test_openrouter.py`

`src/external/openrouter.py` — OpenRouter host discovery (AST-1959): `probe_host` (one probe request built from the real call's kwargs) and `get_batch_host` (process-global single-flight host map keyed on batch id + request args minus `messages` / `system`; never evicted). `send` / `record_probe` are fakes in this module; the `send_to_llm_compat` wiring lives in [`llm_compat.md`](llm_compat.md) § AST-1959. Generation-stats lookup (AST-1964): `get_generation_stats(generation_id, api_key)` — `httpx.get` is stubbed in this module; the background reconcile that calls it is AST-1966's ([`../core/timesheets.md`](../core/timesheets.md)).

### AST-1959 · AST-1954 (per-batch probe and host lock)

**Primary manifest:** [`llm_compat.md`](llm_compat.md) § AST-1959.

Every test clears `openrouter._hosts` (autouse `_fresh_host_map`) — the map is module state and survives across tests otherwise.

| Area | Source | Component tests |
| --- | --- | --- |
| New — probe = real kwargs with content swapped for `LLM_PROBE_MESSAGE`, `system` dropped, no `cache_control`; max_tokens / temperature / effort / provider untouched; caller kwargs not mutated; probe recorded | `probe_host` | `TestAst1959ProbeHost::test_probe_swaps_content_drops_system_keeps_everything_else` |
| New — no `provider` (None / "") raises after the probe is recorded | `probe_host` | `…::test_no_provider_raises_after_recording` (2) |
| New — send error propagates, nothing recorded | `probe_host` | `…::test_send_error_propagates_and_records_nothing` |
| New — 4 concurrent first callers → one `send`, all `(host, None)` | `get_batch_host` | `TestAst1959BatchHostMap::test_concurrent_first_callers_share_one_probe` |
| New — later caller hits the map, no send | `get_batch_host` | `…::test_later_caller_hits_the_map_without_sending` |
| New — probe exception / no provider → remembered `(None, "Host probe failed: …")`, no second probe | `get_batch_host` | `…::test_failed_probe_is_remembered_for_the_key` (2) |
| New — key ignores content + system; new settings or new batch id → fresh probe | `_batch_key` | `…::test_key_ignores_content_and_system_not_settings_or_batch` |
| New — cancelled owner releases waiters with `probe cancelled` failure | `get_batch_host` | `…::test_cancelled_owner_releases_waiters_with_failure` |
| New — waiter on another thread / event loop gets the owner's host, one send | `get_batch_host` | `…::test_waiter_on_another_thread_and_loop_gets_the_owners_host` |

Branch coverage: `--cov-branch` over this module alone reports 100% (46 stmts, 8 branches). Not added to `LOCKED_AT_100` (not requested by the ticket).

**Integration:** none (no `tests/integration/` scenario reaches `llm_compat` or OpenRouter).

### AST-2098 · AST-2099 (hollow probe error text)

**Primary manifest:** [`../core/dispatcher.md`](../core/dispatcher.md) § AST-2098. Contract: when the probe response names no `provider`, `probe_host` raises `ValueError("Probe response named no provider: <detail>")` where `<detail>` is `normalize_provider_error` over the response's `error` attr if present, else the whole response, else `"empty body"` (a `None` response). The probe is still recorded first.

| Area | Source | Component tests |
| --- | --- | --- |
| Revised (AST-2098 message contract) — no-provider case remembered as `"Host probe failed: Probe response named no provider: namespace(provider=None, id='probe_resp')"` | `get_batch_host` | `TestAst1959BatchHostMap::test_failed_probe_is_remembered_for_the_key[send1-…]` |
| New — `error` attr present → message carries OpenRouter's error text; probe recorded once | `probe_host` | `TestAst2098ProbeErrorText::test_hollow_probe_names_provider_error_body` |
| New — `None` response → `"… named no provider: empty body"`; `None` recorded once | `probe_host` | `…::test_hollow_probe_with_no_body_says_empty_body` |
| Revised (drift, not AST-2098) — probe copy gains `provider.zdr = True`; caller's provider has no `zdr` (product `0376f3f8c`; the test update was lost in a later tests resync) | `_probe_request_kwargs` | `TestAst1959ProbeHost::test_probe_swaps_content_drops_system_keeps_everything_else` |

**Integration:** none.

### AST-1964 (retired by AST-2218 — `get_generation_stats` → `get_receipt`) · AST-1963 (generation-stats lookup)

**Primary manifest:** [`../utils/config.md`](../utils/config.md) § AST-1964. `get_generation_stats(generation_id, api_key)` → `GET https://openrouter.ai/api/v1/generation?id=…` with bearer key and `provider_call_http_timeout_seconds()`. Success: `{"success": True, "total_cost", "native_tokens_prompt", "native_tokens_completion", "native_tokens_cached", "native_tokens_reasoning", "provider_name"}` (OpenRouter field names verbatim; only `total_cost` required, the rest pass through as sent). Failure: `{"success": False, "error"}` — no cost key, never raises. Retries are the caller's (AST-1966).

`_Get` stubs `openrouter.httpx.get` (the AC's "stubbed lookup") and records each call.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 2 stubbed 200 → billed values verbatim; request = endpoint, `id` param, `Bearer <key>`, provider timeout | `get_generation_stats` | `TestAst1964GenerationStats::test_200_returns_billed_values` |
| New — AC 2 stub body exactly (`total_cost` / `native_tokens_cached` / `provider_name` only) → missing native counts come back `None` | `get_generation_stats` | `…::test_200_with_only_cost_passes_missing_fields_as_none` |
| New — AC 2 404 / 500 / `httpx.ReadTimeout` / not ready (`total_cost` null, `data` null, body null) → error result, keys exactly `{success, error}` | `get_generation_stats` | `…::test_failure_returns_error_and_no_cost` (6) |
| New — integration-mode guard raise → error result, no HTTP | `get_generation_stats` | `…::test_integration_guard_becomes_error_without_http` |
| New — `stat.logging.debug` request + response lines (generation id) on success and on exception; key never in any record | `get_generation_stats` | `…::test_debug_request_and_response_never_the_key` (2) |

Branch coverage: `--cov-branch` over this module alone reports 100% (65 stmts, 12 branches). Not added to `LOCKED_AT_100` (not requested by the ticket).

**Integration:** none.

### AST-2218 · AST-2215 (billed `get_receipt`)

Parent AC **5** OpenRouter half. `get_receipt(ids, key)` returns one dict per id with exactly `TIMESHEET_RECEIPT_FIELDS`; 200 + `total_cost` fills `platform_cost`; 404 / transport → `completion_status="error"` + null cost; null `total_cost` → `not_ready`. Never raises. `get_generation_stats` / `get_generation_record` removed.

| Area | Source | Component tests |
| --- | --- | --- |
| New — two ids (200 + 404), shared key set, billed vs error | `get_receipt` | `TestAst2218GetReceipt::test_two_ids_200_and_404_shared_shape` |
| New — null total_cost → not_ready | `get_receipt` | `…::test_not_ready_null_cost` |
| New — integration guard → error, no HTTP | `get_receipt` | `…::test_integration_guard_no_http` |
| New — timeout never raises | `get_receipt` | `…::test_never_raises_on_timeout` |
| Broken / obsolete | `TestAst1964GenerationStats` | retired with `get_generation_stats` |

**Primary manifest:** [`../core/timesheets.md`](../core/timesheets.md) § AST-2218. Probe map coverage unchanged (`TestAst1959*` / `TestAst2098*`).
