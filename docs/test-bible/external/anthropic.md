# Anthropic

**Test module:** `tests/component/external/test_anthropic.py`

> **AST-1880:** `src/external/deepseek.py` and `tests/component/external/test_deepseek.py` are deleted. DeepSeek goes through `llm_compat` (see [`llm_compat.md`](llm_compat.md)). Manifests below that cite `test_deepseek.py` are frozen historical records: drop those nodes when re-running.

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/anthropic.py` | `tests/component/external/test_anthropic.py` | yes |

---

### AST-620 · AST-546

**AST-546 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/external/anthropic.py`** and **`src/external/deepseek.py`** — shared debug helper (now **`emit_llm_call_debug`** in **`src/utils/llm_external.py`** per **AST-687**), Style D index + **`|`** detail lines (model, task key, timing, tokens, truncated response preview via **`debug_detail_block`**); retire hand-rolled **`[DEBUG]`** blocks. **`log_llm_batch_summary`** and non-debug INFO/ERROR timing lines unchanged when **`debug=False`**. Attribution locks: **`docs/test-bible/utils/llm_external.md`** (**AST-687**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-620** | Contract debug on success, API error, and outer exception paths for Anthropic + DeepSeek send wrappers | `src/external/anthropic.py`, `src/external/deepseek.py` | **`tests/component/external/test_anthropic.py`** (full file); **`tests/component/external/test_deepseek.py`**; **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-620** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/external/test_anthropic.py tests/component/external/test_deepseek.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/external/test_anthropic.py
```

### AST-903 · AST-900 (UAT fix)

JSON **`stop_reason == max_tokens`** hard-fail (no heal). Primary manifest: **`docs/test-bible/core/agent.md`** § AST-903.

| Area | Source | Component tests |
| --- | --- | --- |
| Fail-closed truncation | `src/external/anthropic.py` | **`TestAst903JsonMaxTokensHardFail`** |


### AST-1189 · AST-1164

Per-call wall budget + `provider_call_timeout` tagging. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1189.

| Area | Source | Component tests |
| --- | --- | --- |
| Timeout tagging | `src/external/anthropic.py` | **`TestAst1189ProviderCallBudgetTimeout`** |

### AST-1190 · AST-1164

Hollow / unusable response fail-closed + blank exception `error=` normalize. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1190.

| Area | Source | Component tests |
| --- | --- | --- |
| Hollow + blank TimeoutError | `src/external/anthropic.py` | **`TestAst1190EmptyUnusableProviderResponse`** |

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `send_to_anthropic` success + `debug=True` (formats, web search) | **`TestSendToAnthropic::test_text_json_and_python_success`** |
| `send_to_anthropic` API failure / invalid format | **`test_api_failure_returns_error_payload`**, **`test_invalid_response_format_raises`** |
| `send_to_deepseek` success + timesheet buckets | **`TestSendToDeepseekTimesheetMapping::test_record_timesheet_kwargs_match_deepseek_buckets`** |
| `_parse_api_response` (unchanged) | **`TestDeepseekParseApiResponse`** |
| `do_task` → DeepSeek provider wiring | **`TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta`** (**§7.13zd**) |

### AST-1956 · AST-1953 (send the agent's settings on the wire)

**Primary manifest:** **`docs/test-bible/core/agent.md`** § AST-1956. Compat side: [`llm_compat.md`](llm_compat.md) § AST-1956.

`send_to_anthropic` takes `reasoning_effort`. New `_effort_body(effort)`: empty → `{}`, `"none"` → `{"thinking": {"type": "disabled"}}`, anything else → `{"output_config": {"effort": v}}`, sent via `extra_body` (no SDK vocabulary). `temperature` is sent only when not `None`. Tests record the `messages.create` kwargs through `_recording` around `fake_anthropic_client`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 2 empty settings: no `temperature`, no effort body | `send_to_anthropic` | **`TestAst1956SettingsOnTheWire::test_empty_settings_send_nothing`** |
| New — AC 3 temperature / effort exactly as set (incl. 0.0, `none`, free-form values) | `send_to_anthropic`, `_effort_body` | **`::test_ac3_temperature_and_effort_exactly_as_set`** (6) |
| New — AC 4 a 400 rejection is a plain `success: False` | `send_to_anthropic` | **`::test_ac4_rejected_setting_is_a_plain_failure`** |

**Broken / obsolete:** none. **Integration:** none.
