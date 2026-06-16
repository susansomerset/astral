# LLM External (utils)

**Test module:** `tests/component/utils/test_llm_external.py`

**Source:** `src/utils/llm_external.py` — shared **`extract_api_response_text`** and **`emit_llm_call_debug`** for Anthropic- and DeepSeek-compatible external clients (**AST-687**); **`logger_name`** pins AST-538 debug lines to the caller external module.

---

### AST-687

| Behavior | Sources | Manifest tests |
| --- | --- | --- |
| Last text block extraction; skip non-text blocks; **`logger_name`** on debug emit | `src/utils/llm_external.py`, `src/external/anthropic.py`, `src/external/deepseek.py` | **`tests/component/utils/test_llm_external.py`** (full file); **`tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module`**; regression **`tests/component/external/test_anthropic.py`** |

**AST-687** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_llm_external.py \
  tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module \
  tests/component/external/test_anthropic.py \
  -q
```
