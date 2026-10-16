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

### AST-1988 · AST-1987 (bug-repro — log_candidate_id set/clear at batch openers)

**Tests landed under gap sibling AST-1991.** Supersedes the AST-1598 line "No dispatcher set sites in this child" for current behavior (that text stays as history). Every candidate-owned batch opener sets `log_candidate_id` right after `log_batch_id` and clears it at the same teardown; meteorite's `_hold_log_batch(batch_id, candidate_id)` returns a `(batch_token, candidate_token)` pair, or `None` under a parent batch. Each opener test pins both vars to `None` with tokens, records `(batch, candidate)` from inside the mocked inner call, and asserts both `None` afterward. Railway JSON keys: [`debug_logging.md`](debug_logging.md) § AST-1988.

**AC 3 composition:** these tests prove the contextvar is set during candidate-owned runs; **`TestAst1598LogCandidateId`** above already proves a set contextvar lands in `app_log.candidate_id` on flush. No duplicate DB-flush test.

| Area | Source | Component tests |
| --- | --- | --- |
| Unified entity run stamps + clears | `src/core/dispatcher.py` | **`tests/component/core/test_dispatcher.py::TestDispatchOne::test_ast1988_unified_run_stamps_candidate_with_batch_and_clears`** (**bug-repro**) |
| Failed run still clears | same | **`…::TestDispatchOne::test_ast1988_failed_run_still_clears_candidate`** |
| run_next chain → neither stamped at dispatch level | same | **`…::TestDispatchOne::test_ast1988_run_next_chain_leaves_candidate_unset_like_batch`** |
| Hop open stamps per hop, close clears | `src/core/agent.py` | **`tests/component/core/test_agent.py::TestAst531RunNextHopLedger::test_ast1988_hop_open_stamps_candidate_and_close_clears`** |
| Workbench stamps + clears | same | **`…::TestAst515AdhocWorkbenchLedger::test_ast1988_workbench_stamps_candidate_and_clears`** |
| Workbench raise still clears | same | **`…::TestAst515AdhocWorkbenchLedger::test_ast1988_workbench_raise_still_clears_candidate`** |
| UI generate stamps + clears | `src/core/candidate.py` | **`tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration::test_ast1988_ui_generate_stamps_candidate_and_clears`** |
| "session" sentinel stays unstamped | same | **`…::TestAst986SessionResumeParse::test_ast1988_session_sentinel_batch_stays_unstamped`** |
| `_hold_log_batch` token pair | `src/core/meteorite.py` | **`tests/component/core/test_meteorite.py::TestAst1988HoldLogBatchPairing::test_hold_sets_both_and_returns_token_pair`** (**bug-repro**) |
| No-op under parent batch | same | **`…::TestAst1988HoldLogBatchPairing::test_hold_noop_under_parent_batch`** |
| Blank candidate → `None` | same | **`…::TestAst1988HoldLogBatchPairing::test_hold_blank_candidate_stamps_none`** |
| `_classify_stage_blob` stamps + two-token reset | same | **`…::TestAst1988HoldLogBatchPairing::test_classify_stage_blob_stamps_and_releases`** |

**Broken / obsolete:** none (add-only).

**Integration:** none.

### AST-1846 · AST-1828 (bug-repro — provider error line is WARNING)

**Primary manifest:** **`docs/test-bible/core/roster.md`** § AST-1846. AST-1839: `log_llm_batch_summary` with `error is not None` logs at **WARNING** (the batch caller decides ERROR via `_log_fail_dest`); blank error still uses the error shape, never the healthy INFO line.

| Area | Source | Component tests |
| --- | --- | --- |
| Provider error → WARNING, no ERROR record | `src/utils/logging.py` | **`TestAst1846ProviderErrorLevel::test_provider_error_logs_warning_not_error`** (**bug-repro**) |
| Flipped (blank error → WARNING) | same | `TestLogLlmBatchSummary::test_empty_error_string_uses_error_path_not_healthy_summary` |

### AST-1959 · AST-1954 (served host on the INFO line)

**Primary manifest:** [`../external/llm_compat.md`](../external/llm_compat.md) § AST-1959. `log_llm_batch_summary` gains keyword-only `host`; when truthy the INFO line reads `LLM <provider> host=<host> task=…`, still one line per call. `None` / `""` leave the line byte-for-byte as before (so `anthropic.py` callers are unchanged). The WARNING branch ignores `host`.

| Area | Source | Component tests |
| --- | --- | --- |
| New — exact INFO message with `host=DeepInfra`; `None` / `""` → today's exact message; one record | `src/utils/logging.py` | `TestAst1959ServedHostOnInfoLine::test_host_segment_on_single_info_line` (3) |

**Broken / obsolete:** none — existing `"LLM deepseek"` substring assertions still hold.

**Integration:** none.
