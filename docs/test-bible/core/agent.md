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

---

### AST-816 · AST-378 (UAT fix)

**`_capture_rubric_vector_feedback`** uses UUID-backed **`expected_codes`**, **`parse_vector_reviews_diagnostic`**, JSON-string **`vector_reviews`**, and debug hydration lines on SUCCESS/failure.

| Area | Source | Component tests |
| --- | --- | --- |
| JSON-string envelope capture | `src/core/agent.py` | `TestAst816VectorFeedbackCapture::test_json_string_vector_reviews_persists_rows` |
| Debug diagnostic on parse failure | `src/core/agent.py` | `TestAst816VectorFeedbackCapture::test_debug_emits_diagnostic_on_parse_failure` |

**AST-816** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst816VectorFeedbackCapture \
  -q
```

Parse helpers: **`docs/test-bible/utils/rubric_feedback.md`**. FEEDBACK modal ledger **`candidate_id`**: **`docs/test-bible/frontend/pages.md`**.

---

### AST-820 · AST-378 (UAT fix)

**`_capture_rubric_vector_feedback`** and **`do_task`** emit debug-only pipeline trace + explicit skip reasons when **`debug=True`** (empty **`batch_id`**, empty rubric UUID map, missing owner/candidate).

| Area | Source | Component tests |
| --- | --- | --- |
| Early-return skip debug | `src/core/agent.py` | `TestAst820VectorFeedbackDebugTrace::test_debug_skip_empty_batch_id`, `test_debug_skip_empty_expected_codes` |
| Pipeline trace on capture | `src/core/agent.py` | `TestAst820VectorFeedbackDebugTrace::test_debug_emits_pipeline_trace_on_capture_start` |
| `do_task` skip when no candidate | `src/core/agent.py` | `TestAst820VectorFeedbackDebugTrace::test_do_task_debug_skip_when_candidate_id_missing` |

**AST-820** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst820VectorFeedbackDebugTrace \
  -q
```

Trace builder: **`docs/test-bible/utils/rubric_feedback.md`**.

---

### AST-860 · AST-378 (UAT fix)

**`_normalize_rubric_envelope_for_capture`**, **`expected_codes = criteria_codes ∩ uuid_codes`**, and **`do_task`** silent-skip debug when **`agent_performance`** missing after normalize — closes **`grade_get`** batch capture/hydrate gap (post AST-859 RACOVK).

| Area | Source | Component tests |
| --- | --- | --- |
| Envelope normalize (status + top-level reviews) | `src/core/agent.py` | `TestAst860NormalizeRubricEnvelope` |
| RACOVK capture + criteria/uuid debug | `src/core/agent.py` | `TestAst860GradeGetVectorFeedbackCapture` |

**AST-860** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst860NormalizeRubricEnvelope \
  tests/component/core/test_agent.py::TestAst860GradeGetVectorFeedbackCapture \
  -q
```

Batch **`astral_candidate_id`** wiring: **`docs/test-bible/core/consult.md`**.

---

### AST-848 · AST-847

**AST-848:** Synchronous **`run_next`** chain ownership moves into **`do_task`**: after each successful hop, write runtime DB label **`{trigger_state}.{completed_task_key}`** via **`write_job_dispatch_hop_label`**; recurse via existing **`run_next`**; terminal graduation to config successor (**`BUILD_ARTIFACTS` → `CANDIDATE_REVIEW`**) in the same invocation when **`dispatch_chain_graduate_on_terminal`** is true and the last hop has empty **`run_next`**. Retires AST-803 consult **`_chain_graduate_to_candidate_review`**, persist gate, and **`chain_incomplete`** flag. Dispatch claim for runtime labels is sibling **AST-849**.

| # | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Hop label helpers + batch claim predicate | `src/utils/config.py` | **`TestAst848DispatchHopLabels`** |
| 2 | Runtime hop write + chain graduation | `src/core/tracker.py` | **`TestAst848DispatchChainTracker`** |
| 3 | Per-hop DB write + terminal graduation + hard failure | `src/core/agent.py` | **`TestAst848DispatchChainDoTask`** |

**Regression (required):** **AST-597** mid-chain hydration without per-hop compound transitions; **AST-844** hop registry (**`TestAst844BuildArtifactsChainTaskKeys`**). Consult/dispatch claim wiring is sibling **AST-849**.

**AST-848** narrowed run (agent + config + tracker slice):

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/core/test_tracker.py::TestAst848DispatchChainTracker \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-849 · AST-847

**AST-849:** Retires consult chain wrapper (**`do_chain_for_job`**, **`_run_build_artifacts_chain_batch`**, all **`_chain_*`** helpers). **`_run_dispatch_chain_job_batch`** invokes **`do_task`** only with **`dispatch_chain_row_matches_job`** gate. Generic **`dispatch_chain_claim_states_for_row`** + **`dispatch_chain_row_matches_job`** drive dispatcher claim/count filter and admin row validation. Depends on **AST-848** **`do_task`** ctx contract.

| # | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Chain claim states + row match helpers | `src/utils/config.py` | **`TestAst849DispatchChainClaimStates`** |
| 2 | Post-claim entity filter | `src/core/dispatcher.py` | **`TestRunUnified::{test_ast534_forwards_dispatch_task_key_to_consult,test_ast849_post_claim_filter_skips_row_mismatch}`** |
| 3 | **`_run_dispatch_chain_job_batch`** → **`do_task`** | `src/core/consult.py` | **`TestAst371ResumeArtifactDispatch`**, **`TestAst534DispatchTaskKeyHonesty`** |
| 4 | Admin hop-label row validation | `src/ui/api/api_admin.py` | **`TestAst773UpdateDispatchTaskTaskKey::test_dispatch_chain_hop_label_must_match_task_key`** |

**Broken / obsolete (Betty revision):** **`TestAst803ChainGraduation`**, **`TestAst803ChainHelpers`**, **`_run_build_artifacts_chain_batch`** / **`do_chain_for_job`** / **`_run_craft_job_cover_letter_batch`** consult tests; **`test_ast596_resume_hop_mismatch_skips_claim`** (pre-claim guard removed — post-claim filter in item 2).

**Regression (required):** **AST-848** **`TestAst848DispatchChainDoTask`**; **AST-844** **`TestAst844BuildArtifactsChainTaskKeys`**; **AST-534** dispatch-key honesty (non-chain **`grade_do`** row in **`TestAst534DispatchTaskKeyHonesty::test_consult_do_routes_via_dispatch_task_key_not_state_map`**).

**AST-849** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestRunConsultTask::test_routes_candidate_review_cover_letter_unhandled_returns_zero \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast849_post_claim_filter_skips_row_mismatch \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask \
  tests/component/ui/api/test_api_admin.py::TestAst773UpdateDispatchTaskTaskKey::test_dispatch_chain_hop_label_must_match_task_key \
  tests/component/utils/test_config.py::TestAst844BuildArtifactsChainTaskKeys \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-855 · AST-852

**Scope:** Dispatch-chain hop success debug aligns Style D index/total when `_dispatch_chain_hop_total` is unset on ctx — fixes multi-hop BUILD_ARTIFACTS crash (`index 2/1`) on `_write_dispatch_hop_label_on_success`. Shared `_dispatch_chain_hop_debug_counts` helper with `_resume_hop_debug_index`.

| Area | Source | Component tests |
| --- | --- | --- |
| Hop debug index/total helper | `src/core/agent.py` | `TestAst855DispatchChainHopDebug::test_dispatch_chain_hop_debug_counts_expands_unset_total`, `::test_dispatch_chain_hop_debug_counts_preserves_explicit_total` |
| Second-hop success path (`contemplate_job`) | `src/core/agent.py` | `TestAst855DispatchChainHopDebug::test_contemplate_job_hop_ok_debug_valid_index_total_on_second_hop` |

**Regression (required):** **AST-848** **`TestAst848DispatchChainDoTask`** (full class).

**AST-855** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst855DispatchChainHopDebug \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
