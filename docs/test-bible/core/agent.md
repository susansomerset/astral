# Agent

**Test module:** `tests/component/core/test_agent.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/agent.py` | `tests/component/core/test_agent.py` | yes |

---

### AST-455 · AST-453

Hop-to-hop **`chain_context`** uses **`CALLER_SYSTEM`**, **`CALLER_CACHE_A`**–**`D`**, **`CALLER_RESPONSE`** only ( **`{$CACHE_BLOCK_*}`** retired from **`TOKEN_SOURCES`** — literals pass through unresolved). **`do_task`** / **`preview_prompt`** assemble ≤5 ephemeral **`system`** blocks from resolved system + cache A–D; **`send_to_anthropic`** payloads store distinct **`CACHE_B`**/**`C`**/**`D`** **`agent_data`** rows when exercised.

| Area | Source | Component tests |
| --- | --- | --- |
| Assembly + caller hop dict | `src/core/agent.py` (`_assemble_blocks_seven_segment`, `_chain_tokens_for_next_hop`) | `tests/component/core/test_agent.py` (`TestAst455SevenSegmentAssembly`, `TestChainContext`, `TestPromptHelpers`) |
| **`TOKEN_SOURCES` / Manage Tasks picker** | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestManageTasksTokenPickerLookup`**, **`CALLER_*`**, **`get_manage_tasks_chain_tokens`**) |
| Admin chain token list endpoint | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (`test_list_tasks_and_tokens` — meta + chain **exactly** `get_tokens()` / `get_manage_tasks_chain_tokens()`) |

---

### AST-618 · AST-541

**AST-541 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/agent.py`** **`do_task`** orchestration — generalized entry header (task key, batch id, index) before external LLM call; token overlay / job-context detail; assembly **`llm_params`** + block counts; truncated response payload via **`debug_detail_block`**; **`run_next`** hop boundary detail; retire hand-rolled **`[DEBUG]`** in touched blocks. **No Betty log-string tests** (parent + child explicit); Radia enforces instrumentation on review. **AST-597** resume-hop index lines generalized to all tasks via **`_do_task_debug_entry`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-618** | Contract debug across `do_task` entry/exit, token overlay, assembly, response payload, `run_next` boundary | `src/core/agent.py` | **`tests/component/core/test_agent.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-618** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_agent.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py
```

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `do_task` entry header + batch/index detail | **`TestDoTask::test_debug_flag_passed_to_child`**; **`TestAst597MidChainResumeHydrationAndTransitions::test_resume_hop_debug_logs_agent_data_source_on_mid_chain_entry`** |
| Token overlay / caller hydration | **`test_resume_hop_debug_logs_agent_data_source_on_mid_chain_entry`** (asserts `caller_source` / `caller_hydration`, not golden index lines) |
| `run_next` hop boundary INFO (unchanged §1.5.1) | **`TestDoTask::test_hop_boundary_log_on_run_next`**; **`TestDoTask::test_chain_entry_log`** |
| Per-hop ledger + chain skip | **`TestAst531RunNextHopLedger`**; **`TestDoTask::test_mid_chain_empty_caller_skips_api`** |
| `debug=False` unchanged | **`TestDoTask`** paths without **`debug=True`**; full-file branch lock |

---

### AST-676 · AST-655

**`_validate_response_schema`:** int **`min`** / **`max`** bounds; reject **`bool`** masquerading as int. Nested **`criteria`** list items use shared craft rubric schema from **`config.py`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Int bounds + bool guard | `src/core/agent.py` | **`TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection`** |
| Craft rubric criteria validation | `src/core/agent.py` | **`TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema`** |

Config registry tests: **`TestAst676CraftRubricSchema`** in **`docs/test-bible/utils/config.md`** (**AST-676**).

---

### AST-697 · AST-696

**`stringify_response_schema("prefilter_company")`** emits bracket **link_set** example **`000|ERC2|MEA3|PGA2|[13]|[3,6,19]`**; **`output_types["grades_encoded_prefilter_links"].payload_instructions`** documents positional bracket tails as canonical with **`JOB:`** / **`CULT:`** alternates retained (**AST-603**).

| Area | Source | Component tests |
| --- | --- | --- |
| Schema example envelope | `src/utils/config.py` (`stringify_response_schema`) | `tests/component/utils/test_config.py::TestStringifyResponseSchema::test_prefilter_company_schema_shows_bracket_link_set_tails` |
| Output type registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded` |

See **`docs/test-bible/core/consult.md`** (**AST-697**) for decode-path manifest rows.

---

### AST-698 · AST-696

**UAT fix:** **`do_task`** emits **`raw_response`** contract lines for any non-empty API body when **`debug=True`** (retired **>50 lines** gate); encoded tasks log **`encoded_payload`** via **`debug_detail`** / **`debug_detail_block`** instead of **`[DEBUG] logger.info`**. Roster **`prefilter_company`** accepts **`debug`** and forwards it from **`run_company_task`** on **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Short-body **`raw_response`** under debug | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst698DoTaskDebugRawResponse::test_short_raw_response_emits_under_debug_contract` |
| Encoded payload contract (no legacy **`literal encoded agent_payload`**) | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst698DoTaskDebugRawResponse::test_encoded_payload_uses_contract_helpers_not_legacy_info` |
| **`debug=False`** unchanged | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst698DoTaskDebugRawResponse::test_debug_false_skips_raw_response_contract_lines` |

**AST-698** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst698DoTaskDebugRawResponse \
  tests/component/core/test_roster.py::TestAst698PrefilterDebugPassthrough \
  -q
```

Roster passthrough manifest: **`docs/test-bible/core/roster.md`** (**AST-698**).

---

### AST-724 · AST-378

**`do_task`** SUCCESS-path lenient capture of **`vector_reviews`** on rubric-backed tasks: clean parse → **`vector_feedback`** rows; unparseable → **`FEEDBACK`** agent_data block only. Parse failures never fail the run.

| Area | Source | Component tests |
| --- | --- | --- |
| `agent_performance.status` normalization | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_agent_performance_status_normalizes_dict_and_string` |
| Owner task + candidate resolution | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_rubric_feedback_owner_and_candidate_resolves_from_cd_and_ctx` |
| Clean parse → vector_feedback rows | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_clean_parse_inserts_vector_feedback_rows` |
| Unparseable → FEEDBACK block | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_unparseable_stores_feedback_block_not_rows` |
| Non-success skips capture | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_non_success_skips_capture` |

**AST-724** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture \
  -q
```

Parse helpers: **`docs/test-bible/utils/rubric_feedback.md`**. Data layer: **`docs/test-bible/data/database/rubric_vectors.md`**.

---

### AST-769 · AST-752

**General caller hydration:** `do_task` entry loads `{$CALLER_*}` from persisted `agent_data` on job / company / candidate entities (batch-anchored via `state_history` or `log_batch_id`); `run_next` child dispatch strips in-memory `CALLER_*` and re-hydrates from storage. Refactors AST-597 resume helpers onto `_hydrate_caller_chain_context` / `_hop_agent_ref_for_parent` (retires `_latest_job_hop_agent_ref`).

| Area | Source | Component tests |
| --- | --- | --- |
| Batch anchor + hop ref lookup | `src/core/agent.py` | **`TestAst769GeneralCallerHydration::test_anchor_batch_id_from_state_history_uses_current_state_row`**; **`test_hop_agent_ref_for_parent_prefers_anchor_batch_over_newer_ref`**; **`test_hop_agent_ref_for_parent_skips_failed_response_rows`** (AST-597 class) |
| Non-caller chain keys preserved | `src/core/agent.py` | **`TestAst769GeneralCallerHydration::test_merge_hydrated_caller_context_preserves_non_caller_keys`** |
| Roster mid-chain entry (company) | `src/core/agent.py` | **`TestAst769GeneralCallerHydration::test_do_task_parse_job_list_hydrates_caller_from_company_agent_data`** |
| Non-roster job hop (cover letter) | `src/core/agent.py` | **`TestAst769GeneralCallerHydration::test_do_task_job_cover_letter_hydrates_from_stored_parent_hop`** |
| Hydration miss — no LLM | `src/core/agent.py` | **`TestAst769GeneralCallerHydration::test_do_task_hydration_miss_returns_error_without_llm`** |
| Style D debug | `src/core/agent.py` | **`TestAst769GeneralCallerHydration::test_do_task_hydrated_hop_debug_logs_agent_data`** |
| AST-597 resume regression | `src/core/agent.py` | **`TestAst597MidChainResumeHydrationAndTransitions`** (full class) |
| Daisy-chain regression | `src/core/agent.py` | **`TestAst469ResolveRunNextLive`**; **`TestChainContext`** |

**AST-769** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst769GeneralCallerHydration \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  tests/component/core/test_agent.py::TestAst469ResolveRunNextLive \
  tests/component/core/test_agent.py::TestChainContext \
  -q
```

**Note:** Candidate entities lack `state_history` batch anchoring today — hydration falls back to latest successful parent ref per `task_key` (documented in plan Stage 1).

---

### AST-809 · AST-378 (UAT fix)

**`_capture_rubric_vector_feedback`** requires truthy **`batch_id`** before insert; passes **`batch_size`** and **`completed_at`** into **`insert_vector_feedback_rows`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Skip when batch_id missing | `src/core/agent.py` | `TestAst809VectorFeedbackBatchMetadata::test_capture_skips_insert_when_batch_id_missing` |
| Metadata on SUCCESS capture | `src/core/agent.py` | `TestAst809VectorFeedbackBatchMetadata::test_capture_persists_batch_metadata_on_rows` |
