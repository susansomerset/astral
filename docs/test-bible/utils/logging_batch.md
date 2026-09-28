# Logging Batch

**Test module:** `tests/component/utils/test_logging_batch.py`

**Source:** `src/utils/logging.py` — **`log_llm_batch_summary`** (batch-scoped LLM INFO/ERROR lines for Execution History).

---

### AST-1190 · AST-1164

**`log_llm_batch_summary`:** when **`error is not None`** (including `""` / whitespace), emit ERROR with display `"(empty error)"` if blank — never the healthy `stop=? tokens in=0 out=0` INFO shape. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1190.

| Area | Source | Component tests |
| --- | --- | --- |
| Blank `error=` error path (level WARNING since AST-1839 — see § AST-1846) | `src/utils/logging.py` | `test_empty_error_string_uses_error_path_not_healthy_summary` |
| Omitted `error` keeps INFO | same | `test_omitted_error_still_logs_healthy_summary` |

---

### AST-1598 · AST-1594

`log_candidate_id` ContextVar (parallel to `log_batch_id`); `_DatabaseLogHandler.emit` buffers `candidate_id`; flush passes kwargs to `add_log_entry`. No dispatcher set sites in this child.

| Area | Source | Component tests |
| --- | --- | --- |
| Emit buffer stamp / unset → None | `src/utils/logging.py` | **`TestAst1598LogCandidateId::test_contextvar_stamps_emit_buffer_and_unset_is_null`** |

**Broken / obsolete this pass:** none for prior `log_llm_batch_summary` suite.

**Integration:** none.

### AST-1846 · AST-1828 (bug-repro — provider error line is WARNING)

**Primary manifest:** **`docs/test-bible/core/roster.md`** § AST-1846. AST-1839: `log_llm_batch_summary` with `error is not None` logs at **WARNING** (the batch caller decides ERROR via `_log_fail_dest`); blank error still uses the error shape, never the healthy INFO line.

| Area | Source | Component tests |
| --- | --- | --- |
| Provider error → WARNING, no ERROR record | `src/utils/logging.py` | **`TestAst1846ProviderErrorLevel::test_provider_error_logs_warning_not_error`** (**bug-repro**) |
| Flipped (blank error → WARNING) | same | `TestLogLlmBatchSummary::test_empty_error_string_uses_error_path_not_healthy_summary` |
