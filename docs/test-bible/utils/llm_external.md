# LLM External (utils)

**Test module:** `tests/component/utils/test_llm_external.py`

**Source:** `src/utils/llm_external.py` — shared **`extract_api_response_text`** and **`emit_llm_call_debug`** for Anthropic- and DeepSeek-compatible external clients (**AST-687**); **`logger_name`** pins AST-538 debug lines to the caller external module; **`classify_provider_balance_refusal`** / **`is_provider_balance_refusal`** (**AST-897**).

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

---

### AST-897 · AST-896

**Scope:** Recognize LLM provider balance/credit refusals (`PROVIDER_BALANCE_REFUSAL` + classifiers in **`llm_external`**); tag **`failure_class`** on Anthropic/DeepSeek exception returns; gate consult/roster fail→error/retry transitions so job/company **state is held**; **`do_task`** debug detail when tagged.

| Area | Source | Component tests |
| --- | --- | --- |
| Config block | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst897ProviderBalanceRefusalConfig` |
| Classify / predicate | `src/utils/llm_external.py` | `tests/component/utils/test_llm_external.py::TestAst897ProviderBalanceRefusal` |
| Anthropic tagging | `src/external/anthropic.py` | `tests/component/external/test_anthropic.py::TestAst897BalanceRefusalTagging` |
| DeepSeek tagging | `src/external/deepseek.py` | `tests/component/external/test_deepseek.py::TestAst897BalanceRefusalTagging` |
| `do_task` debug hold detail | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst897DoTaskBalanceDebug` |
| Consult hold (verdict / batch / upshot) | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst897HoldStateOnBalanceRefusal` |
| Roster hold (prefilter / batch / select / JOBS_FOUND wrapper) | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal` |
| JOBS_FOUND ordinary error still → locate `error_state` | `src/core/roster.py` | `::test_run_company_task_jobs_found_error_moves_locate_error_state` |

**Broken / obsolete:** none — existing fail→transition cases remain; balance path is additive.

**Return pass (resolve `[qa-handoff]`):** cover `run_company_task("JOBS_FOUND")` outer gate so `state_held` / `failure_class=provider_balance_refusal` does **not** call `transition_company_state` (Radia fix-now @ `4153885`).

**AST-897** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst897ProviderBalanceRefusalConfig \
  tests/component/utils/test_llm_external.py::TestAst897ProviderBalanceRefusal \
  tests/component/external/test_anthropic.py::TestAst897BalanceRefusalTagging \
  tests/component/external/test_deepseek.py::TestAst897BalanceRefusalTagging \
  tests/component/core/test_agent.py::TestAst897DoTaskBalanceDebug \
  tests/component/core/test_consult.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_roster.py::test_run_company_task_jobs_found_error_moves_locate_error_state \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
