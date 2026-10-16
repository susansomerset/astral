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

### AST-2179 · AST-2172 (forced-tool transport)

**Primary manifest** for AST-2179. Compat side: [`llm_compat.md`](llm_compat.md) § AST-2179. Extractors: [`../utils/llm_external.md`](../utils/llm_external.md) § AST-2179.

`send_to_anthropic(..., forced_tool={name, input_schema})` merges `_forced_tool_body` (exactly one tool + `tool_choice: {"type": "tool", "name": …}`) into the `messages.create` kwargs. The named tool's input is `parsed_response` whatever `response_format` says (`extract_tool_input`). A missing, other-named or non-object tool call goes down the existing parse-failure path (`success: False`, timesheet `failure`). `max_tokens` fails closed when `forced_tool` is set, even without `response_format="json"`. `forced_tool` + `enable_web_search` raises before any request. `getTimestampPrefix(structured=True)` reads `prompt_prefix_structured`. `_parse_json_response` no longer coerces encoded grade text into `{"agent_payload": …}`. Tests answer through a local `_BlocksClient` (records kwargs, returns arbitrary content blocks), so there are no live provider calls.

| Area | Source | Component tests |
| --- | --- | --- |
| New — `_forced_tool_body` shape | `_forced_tool_body` | **`TestAst2179ForcedToolTransport::test_forced_tool_body_is_one_tool_and_a_named_choice`** |
| New — AC 3 kwargs carry exactly one tool + forcing `tool_choice`; neither key without `forced_tool` | `send_to_anthropic` | **`::test_ac3_request_carries_exactly_one_tool_and_forcing_choice`** · **`::test_ac3_no_tool_keys_without_forced_tool`** |
| New — AC 3 debug `Calling messages.create` line carries the tool kwargs; `Response from messages.create` logged | `send_to_anthropic` | **`::test_ac3_debug_logs_request_kwargs_and_response`** |
| New — `forced_tool` + web search refused, nothing sent | `send_to_anthropic` | **`::test_forced_tool_with_web_search_is_refused`** |
| New — tool input is `parsed_response` for `response_format` None / text / json (stray text block ignored); its `agent_performance` reaches the timesheet | `send_to_anthropic` | **`::test_tool_input_is_parsed_response_whatever_format`** (3) · **`::test_tool_input_agent_performance_reaches_timesheet`** |
| New — text-only / other tool / non-object input → failure + timesheet `failure` | `send_to_anthropic`, `extract_tool_input` | **`::test_missing_or_malformed_tool_call_is_a_failure`** (3) |
| New — `max_tokens` fails closed with `forced_tool` and no JSON format | `send_to_anthropic` | **`::test_max_tokens_fails_closed_even_without_json_format`** |
| New — `debug=True` on a tool-only reply: raw text is the tool input JSON, call succeeds | `send_to_anthropic`, `extract_api_response_text` | **`::test_debug_raw_text_falls_back_to_tool_input_json`** |
| New — structured prefix swaps the envelope sentence for `prompt_prefix_structured` | `getTimestampPrefix` | **`TestGetTimestampPrefix::test_structured_swaps_envelope_for_performance_rules`** |
| Revised — encoded-string coercion removed: a JSON string stays a string; bare encoded text is a parse failure | `_parse_json_response` | **`TestParseJsonResponse::test_top_level_json_string_is_not_wrapped`** · **`::test_bare_encoded_text_is_a_parse_failure`** |

**Broken / obsolete:** `TestParseJsonResponse::test_wraps_top_level_json_string_encoded_grades` and `::test_wraps_bare_encoded_text_without_json` asserted the removed coercion. Both are replaced by the revised rows above.

**Masked:** none new. `TestAst1190EmptyUnusableProviderResponse::test_hollow_stop_question_zero_tokens_fails_closed` was already red before this build and is unchanged by it.

**Repro:** all 35 new / revised nodes in this manifest are red on the pre-build product files (`051dce84c`) and green on the build tip. `TestAst2179ForcedToolTransport::test_ac4_openrouter_without_forced_tool_is_unchanged` (compat) and the two new negative `extract_api_response_text` cases are green on both by design: they guard behaviour that must survive.

**Integration:** none. No `tests/integration/` scenario touches `_parse_json_response`, tool kwargs or `require_parameters`.

**AST-2179 QA test manifest:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_anthropic.py::TestAst2179ForcedToolTransport \
  tests/component/external/test_anthropic.py::TestGetTimestampPrefix \
  tests/component/external/test_anthropic.py::TestParseJsonResponse \
  tests/component/external/test_llm_compat.py::TestAst2179ForcedToolTransport \
  tests/component/utils/test_llm_external.py::TestExtractApiResponseText \
  tests/component/utils/test_llm_external.py::TestExtractToolInput
```

**Regression (no new reds):** `tests/component/external/test_anthropic.py`, `test_llm_compat.py`, `test_openrouter.py`, `tests/component/utils/test_llm_external.py`, `tests/component/utils/test_formatting.py`, `tests/component/core/test_agent.py`, `test_agent_ast1448.py`, `test_agent_ast1879.py`. The 52 failures that were already red before the build (mostly `test_agent.py` decode / `do_task` cases) are identical on the tip.

**Pass criterion:** pytest green on the manifest lines, not the zero-arg harness or branch-lock gate.

### AST-2217 · AST-2215 (zero-stub `get_receipt` + call-time attribution)

Parent AC **5** stub half + AC **8** Anthropic recorded-row attribution. `get_receipt` returns one dict per id with exactly `TIMESHEET_RECEIPT_FIELDS`; `platform_cost` always `None`; no HTTP. `send_to_anthropic` stamps `request_type` / `entity_*` / `call_start`/`call_stop` / response size into `record_timesheet` kwargs.

| Area | Source | Component tests |
| --- | --- | --- |
| New — stub receipt shape + null platform cost | `get_receipt` | `TestAst2217ReceiptStubAndAttribution::test_get_receipt_zero_stub_shape_and_null_cost` |
| New — recorded call carries attribution + timing | `send_to_anthropic` | `…::test_recorded_call_carries_attribution` |

**Primary manifest:** [`../data/database/timesheets.md`](../data/database/timesheets.md) § AST-2217. **Integration:** none.
