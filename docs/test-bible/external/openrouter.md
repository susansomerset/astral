# OpenRouter

**Test module:** `tests/component/external/test_openrouter.py`

`src/external/openrouter.py` — OpenRouter host discovery (AST-1959): `probe_host` (one probe request built from the real call's kwargs) and `get_batch_host` (process-global single-flight host map keyed on batch id + request args minus `messages` / `system`; never evicted). `send` / `record_probe` are fakes in this module; the `send_to_llm_compat` wiring lives in [`llm_compat.md`](llm_compat.md) § AST-1959.

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
