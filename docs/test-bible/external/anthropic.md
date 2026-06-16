# Anthropic

**Test module:** `tests/component/external/test_anthropic.py`

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

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `send_to_anthropic` success + `debug=True` (formats, web search) | **`TestSendToAnthropic::test_text_json_and_python_success`** |
| `send_to_anthropic` API failure / invalid format | **`test_api_failure_returns_error_payload`**, **`test_invalid_response_format_raises`** |
| `send_to_deepseek` success + timesheet buckets | **`TestSendToDeepseekTimesheetMapping::test_record_timesheet_kwargs_match_deepseek_buckets`** |
| `_parse_api_response` (unchanged) | **`TestDeepseekParseApiResponse`** |
| `do_task` → DeepSeek provider wiring | **`TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta`** (**§7.13zd**) |
