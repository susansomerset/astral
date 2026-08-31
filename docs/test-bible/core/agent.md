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

**`do_task`** SUCCESS-path lenient capture of **`vector_reviews`** on rubric-backed tasks: clean parse → **`vector_feedback`** rows **and** **FEEDBACK** block (AST-862); unparseable → **`FEEDBACK`** agent_data block only. Parse failures never fail the run.

| Area | Source | Component tests |
| --- | --- | --- |
| `agent_performance.status` normalization | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_agent_performance_status_normalizes_dict_and_string` |
| Owner task + candidate resolution | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_rubric_feedback_owner_and_candidate_resolves_from_cd_and_ctx` |
| Clean parse → vector_feedback rows + FEEDBACK block | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_clean_parse_inserts_vector_feedback_rows` |
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

### AST-862 · AST-378 (UAT fix)

**`_capture_rubric_vector_feedback`** clean-parse SUCCESS path appends **FEEDBACK** block to **`prompt_blocks`** (via **`store_feedback_block` / `format_vector_reviews_raw`**) after **`insert_vector_feedback_rows`** — so **`agent_data`** / Performance Monitor / FEEDBACK tab can inspect **`vector_reviews`** alongside **`vector_feedback`** rows. Unparseable path unchanged (AST-724).

| Area | Source | Component tests |
| --- | --- | --- |
| Clean parse → FEEDBACK ref + agent_data row | `src/core/agent.py` | `TestAst862CleanParseFeedbackBlock::test_clean_parse_feedback_block_has_vector_reviews_json` |
| FEEDBACK store failure is non-fatal | `src/core/agent.py` | `TestAst862CleanParseFeedbackBlock::test_store_feedback_block_failure_still_inserts_vector_feedback_rows` |
| AST-724 clean-parse regression (rows + FEEDBACK) | `src/core/agent.py` | `TestAst724VectorFeedbackCapture::test_clean_parse_inserts_vector_feedback_rows` |

**AST-862** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst862CleanParseFeedbackBlock \
  tests/component/core/test_agent.py::TestAst724VectorFeedbackCapture::test_clean_parse_inserts_vector_feedback_rows \
  -q
```

---

### AST-848 · AST-847

**AST-848:** Synchronous **`run_next`** chain ownership moves into **`do_task`**: after each successful hop, write runtime DB label **`{trigger_state}.{completed_task_key}`** via **`write_job_dispatch_hop_label`**; recurse via existing **`run_next`**; terminal graduation to config successor (**`BUILD_ARTIFACTS` → `CANDIDATE_REVIEW`**) in the same invocation when **`dispatch_chain_graduate_on_terminal`** is true and the last hop has empty **`run_next`**. Retires AST-803 consult **`_chain_graduate_to_candidate_review`**, persist gate, and **`chain_incomplete`** flag. Dispatch claim for runtime labels is sibling **AST-849**.

| # | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Hop label helpers + batch claim predicate | `src/utils/config.py` | **`TestAst848DispatchHopLabels`** |
| 2 | Runtime hop write + chain graduation | `src/core/tracker.py` | **`TestAst848DispatchChainTracker`** |
| 3 | Per-hop DB write + terminal graduation + hard failure | `src/core/agent.py` | **`TestAst848DispatchChainDoTask`** |

**Regression (required):** **AST-597** mid-chain hydration without per-hop compound transitions; **AST-1111** config shadow absence (**`TestAst1111JobArtifactEntryShadowDeleted`**). Consult/dispatch claim wiring is sibling **AST-849**.

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

**Regression (required):** **AST-848** **`TestAst848DispatchChainDoTask`**; **AST-1111** **`TestAst1111JobArtifactEntryShadowDeleted`**; **AST-534** dispatch-key honesty (non-chain **`grade_do`** row in **`TestAst534DispatchTaskKeyHonesty::test_consult_do_routes_via_dispatch_task_key_not_state_map`**).

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
  tests/component/utils/test_config.py::TestAst1111JobArtifactEntryShadowDeleted \
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

---

### AST-880 · AST-879

**`grades_encoded_vet_meta`:** **`_decode_payload`** branch returns **`results[]`** with **`hit_index` / `grade` / `website` / `confidence`** — LT vector segment, website required on every grade including F; illegal grade or empty website raises **`ValueError`**.

| Area | Source | Component tests |
| --- | --- | --- |
| LT segment decode + validation | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst880GradesEncodedVetMetaDecode` |

**AST-880** narrowed run:

```bash
.venv/bin/python -m pytest tests/component/core/test_agent.py::TestAst880GradesEncodedVetMetaDecode -q
```

### AST-1190 · AST-1164

**`do_task`:** coerce blank provider `error=` to a non-empty string on the `provider call failed` log/return; **`debug=True`** detail when **`is_provider_empty_response`**. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1190.

| Area | Source | Component tests |
| --- | --- | --- |
| Blank-error coerce + empty-response debug | `src/core/agent.py` | **`TestAst1190DoTaskEmptyProviderError`** |

### AST-1191 · AST-1164

**Dispatch-chain provider hop failure:** `_apply_dispatch_chain_hop_failure` — non-balance provider failures apply `error_state` then `release_job_dispatch_claim`; balance refusal holds state but still releases claim; `_close_hop_ledger` returns outcome on every exit. **`debug=True`:** found (duration/stop/tokens/`failure_class`, `n/a` not silent 0) + recorded (error / error_state|held / batch_released). Hop-label-false non-job (or no index) → `_HOP_FAILURE_NOOP`; hop-label-false **job** + `provider_failed` claim release is **AST-1298**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hop failure apply + claim release + debug | `src/core/agent.py` | **`TestAst1191ArtifactHopFailureRelease`** |
| Hard-string path still transitions (release added) | `src/core/agent.py` | **`TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts`** |

**AST-1191** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts \
  -q
```

### AST-1298 · AST-1280

**Parent:** [AST-1280 — Connection error on dispatch task did not clear the batch_id](https://linear.app/astralcareermatch/issue/AST-1280/connection-error-on-dispatch-task-did-not-clear-the-batch-id). **Publish:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`.

Close orphaned job `batch_id` after provider Connection-style failure on hop-label-true BUILD_ARTIFACTS dispatch: helper `try`/`finally` still releases when `transition_job_state` raises non-`ValueError`; consult `_run_dispatch_chain_job_batch` releases when `do_task` raises; hop-label-false job+`provider_failed` defense-in-depth release (no error_state). No new debug contract strings; `debug=True` keeps recorded `batch_released=true`.

| Area | Source | Component tests |
| --- | --- | --- |
| Transition non-`ValueError` still releases | `src/core/agent.py` | **`TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases`** |
| `draft_job_resume` Connection error → `ERROR_BUILD_ARTIFACTS` + release + debug | `src/core/agent.py` | **`TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors`** |
| Hop-label-false job release (revised AST-1191 noop) | `src/core/agent.py` | **`TestAst1191ArtifactHopFailureRelease::test_apply_hop_label_false_job_provider_failed_releases`** |
| Consult `do_task` raise → claim release | `src/core/consult.py` | **`TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_do_task_raise_releases_claim`** |
| Regression: structured `success=False` still releases | `src/core/consult.py` | **`TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_failure_releases_claim`** |
| Regression: AST-1191 hop-failure suite | `src/core/agent.py` | **`TestAst1191ArtifactHopFailureRelease`** |

**Broken / obsolete:** **`TestAst1191ArtifactHopFailureRelease::test_apply_non_dispatch_chain_returns_noop`** — replaced by hop-label-false job release + non-job noop (product defense-in-depth).

**Integration:** none revised (no existing scenario asserted orphaned Connection-error claim clear).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease \
  tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_do_task_raise_releases_claim \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_dispatch_chain_batch_failure_releases_claim \
  -q
```

### AST-903 · AST-900 (UAT fix)

**AST-903:** Craft rubric JSON truncation (`Unterminated string` mid-`criteria[].content`) — `do_task` floors **`max_tokens`** to **`CRAFT_RUBRIC_MAX_TOKENS`** (32000) for **`CRAFT_RUBRIC_UI_TASK_KEYS`**; DeepSeek/Anthropic hard-fail JSON when **`stop_reason == max_tokens`** (no heal-into-partial-success). UI/prompts/consult batches out of scope.

| Area | Source | Component tests |
| --- | --- | --- |
| Token floor in `do_task` | `src/core/agent.py` | **`TestAst903CraftRubricMaxTokensFloor`** |
| Config floor literal | `src/utils/config.py` | **`TestAst903CraftRubricMaxTokens`** (`test_config.py`) |
| JSON max_tokens hard-fail | `src/external/deepseek.py`, `src/external/anthropic.py` | **`TestAst903JsonMaxTokensHardFail`** (each provider module) |

**AST-903** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor \
  tests/component/utils/test_config.py::TestAst903CraftRubricMaxTokens \
  tests/component/external/test_deepseek.py::TestAst903JsonMaxTokensHardFail \
  tests/component/external/test_anthropic.py::TestAst903JsonMaxTokensHardFail
```

### AST-1380 / AST-1383 · AST-1379 (fix + gap)

**AST-1380** Decision A: for `CRAFT_RUBRIC_UI_TASK_KEYS` on DeepSeek, `do_task` forces `tier_meta.thinking=False` / `reasoning_effort=None` (Big thinking otherwise shares the craft `max_tokens` floor and starves mid-`criteria[].content`) while keeping the AST-903 floor. Provider-failure RESPONSE rows use `_provider_failure_audit_body` (`Provider failed …` / optional `(failure_class)` + `--- model response ---`) so a truncated success-shaped envelope cannot look like a finished hop. Gap **AST-1383** lands this bible + component coverage (product stays on AST-1380). **AST-1391:** that craft DeepSeek Big hop still forces thinking off; `max_tokens` is now the DeepSeek Big floor (not `CRAFT_RUBRIC_MAX_TOKENS`).

| Area | Source | Component tests |
| --- | --- | --- |
| Craft DeepSeek Big thinking-off + floor | `src/core/agent.py` | **`TestAst1380CraftRubricThinkingOffAndFailureBanner::test_craft_get_rubric_deepseek_big_forces_thinking_false`** |
| Non-craft Big keeps thinking | `src/core/agent.py` | **`TestAst1380CraftRubricThinkingOffAndFailureBanner::test_non_craft_deepseek_big_keeps_thinking`** |
| Provider-failure RESPONSE banner | `src/core/agent.py` | **`TestAst1380CraftRubricThinkingOffAndFailureBanner::test_provider_failure_response_banner_prefixes_success_shaped_envelope`** |

**AST-1383** narrowed run (repro = thinking-off + banner nodes):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1380CraftRubricThinkingOffAndFailureBanner \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor
```

### AST-1391 · AST-1390 (DeepSeek Big output floor)

**AST-1391:** DeepSeek **Big** `do_task` hops send `max_tokens` of at least **384000** (named `tier_map["deepseek"][BRAIN_BIG]["max_tokens"]`, applied via `deepseek_brain_max_tokens_floor` after the craft 32000 floor). Agent-row values above 384000 still win (floor, not cap). Little / Medium DeepSeek hops and Anthropic Big are unchanged. Craft DeepSeek Big still disables thinking (AST-1380 Decision A). Admin `run_adhoc` / `_resolve_adhoc` out of scope. Config helper + SKU-default guard: **`docs/test-bible/utils/config.md`** § AST-1391.

| Area | Source | Component tests |
| --- | --- | --- |
| DeepSeek Big floor over low agent-row | `src/core/agent.py` | **`TestAst1391DeepseekBigOutputFloor::test_deepseek_big_floors_low_agent_row`** |
| Agent-row above floor wins | same | **`TestAst1391DeepseekBigOutputFloor::test_deepseek_big_agent_row_above_floor_wins`** |
| Medium / Little unchanged | same | **`test_deepseek_medium_keeps_agent_row`**, **`test_deepseek_little_keeps_agent_row`** |
| Anthropic Big not 384000 | same | **`test_anthropic_big_does_not_use_deepseek_floor`** |
| `debug=True` max_tokens line | same | **`test_debug_true_max_tokens_line_shows_floor`** |
| Craft thinking-off still holds; tokens now Big floor | same | **`TestAst1391DeepseekBigOutputFloor::test_craft_deepseek_big_thinking_off_uses_big_floor`**; **`TestAst1380CraftRubricThinkingOffAndFailureBanner::test_craft_get_rubric_deepseek_big_forces_thinking_false`** (revised assertion) |
| Named 384000 + helper None on Little/Medium | `src/utils/config.py` | **`TestAst1391DeepseekBigMaxTokensFloor`** (`test_config.py`) |

**Broken / obsolete this pass:** `test_craft_get_rubric_deepseek_big_forces_thinking_false` asserted `max_tokens == CRAFT_RUBRIC_MAX_TOKENS` (32000); DeepSeek Big craft now sends the Big floor (AC6).

**Integration:** no existing scenario asserts `do_task` `max_tokens` / DeepSeek Big hops — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1391DeepseekBigOutputFloor \
  tests/component/core/test_agent.py::TestAst1380CraftRubricThinkingOffAndFailureBanner::test_craft_get_rubric_deepseek_big_forces_thinking_false \
  tests/component/utils/test_config.py::TestAst1391DeepseekBigMaxTokensFloor \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor \
  -q
```

### AST-1393 · AST-1392 (serialize Ad Hoc success body)

**Parent:** [AST-1392](https://linear.app/astralcareermatch/issue/AST-1392). **Publish:** `origin/sub/AST-1392/AST-1393-serialize-ad-hoc-success-body-to-text`.

Workbench Test success path stringifies the extracted body via **`_caller_response_blob`** before **`_store_response_block`**: dict/list → compact JSON text; already-`str` unchanged; empty `{}` / `[]` store as `"{}"` / `"[]"` (not `""`). Envelope still extracts **`agent_payload`** when present. Style D found type/shape → recorded text when `debug=True`; quiet when `debug=False`. Does **not** own Admin HTTP/React (sibling #2) or `do_task` schema coerce. Data layer still raises on non-text.

| Area | Source | Component tests |
| --- | --- | --- |
| Object payload JSON text + ledger COMPLETED | `src/core/agent.py` (`run_adhoc_workbench_test`) | **`TestAst1393SerializeAdhocSuccessBody::test_success_stores_serialized_text`** (`object-payload`) |
| Empty dict/list, list payload, plain text, dict without payload key | same | **`test_success_stores_serialized_text`** (remaining ids) |
| String payload regression | same | **`TestAst515AdhocWorkbenchLedger::test_success_completes_ledger_and_stores_blocks`**; **`test_success_stores_serialized_text`** (`str-payload`) |
| Style D found→recorded (dict/list/str/none/other) | same | **`test_debug_true_style_d_found_to_recorded`** |
| `debug=False` adds no serialize lines | same | **`test_debug_false_adds_no_serialize_lines`** |
| Failure path unchanged | same | **`TestAst515AdhocWorkbenchLedger::test_failure_marks_ledger_failed_and_stores_failure_response`** |

**Broken / obsolete this pass:** none — existing string-payload AST-515 assertion (`_store_response_block` arg `[3] == "ok"`) still holds.

**Integration:** no existing scenario asserts Ad Hoc workbench RESPONSE stringify — no revision; do not invent new integration coverage.

## QA test manifest

1. Existing string-payload ledger + store: `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`
2. Object/list/plain-text stringify + debug Style D: `tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody`

**AST-1393** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1393SerializeAdhocSuccessBody \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-977 · AST-974

`agent_data` dedupe write/read debug in **`agent.py`**: `_store_prompt_blocks` / `_store_response_block` emit `agent_data_write` found/recorded when `debug=True`; `_block_text_by_type` emits `agent_data_read` resolve/direct; quiet when `debug=False`. Data-layer contract: **`docs/test-bible/data/database/agent_data.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Write trail (`debug=True`) | `src/core/agent.py` | `TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome` |
| Quiet when `debug=False` | `src/core/agent.py` | `TestAst977AgentDataDedupeDebug::test_store_response_debug_false_is_quiet` |
| Read trail resolve mode | `src/core/agent.py` | `TestAst977AgentDataDedupeDebug::test_block_text_by_type_debug_emits_read_mode` |

### AST-981 · AST-975

**Scope:** Stop core audit writes to the standalone `agent_responses` **table**. `_store_agent_response` / `add_agent_response_entry` removed; `do_task` persists `agent_data` (`save_agent_data`); entity JSON append was sibling scope. Schema drop / docs / column retirement: AST-982 / AST-983 / **AST-984**.

| Area | Source | Component tests |
| --- | --- | --- |
| Retired audit symbols absent | `src/core/agent.py` | `TestAst981StandaloneTableAuditRetired::test_agent_module_has_no_standalone_table_helpers` |
| Success path: agent_data + entity append only | same | `TestAst981StandaloneTableAuditRetired::test_do_task_success_persists_agent_data_and_entity_append_only` |
| Failure path still stores agent_data | same | `TestDoTask::test_returns_api_failure_and_stores_agent_data` |

**Obsolete revised:** removed `test_store_agent_response_skips_or_records`; dropped all `add_agent_response_entry` monkeypatches / `stub_agent_storage["audit"]` (setattr raises once the import is gone).

**AST-981** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  tests/component/core/test_agent.py::TestDoTask::test_returns_api_failure_and_stores_agent_data \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst726AppendAgentResponseUpsert \
  tests/component/scripts/test_migrate_agent_data.py::TestAst981MigrateAgentDataRetired \
  -q
```

### AST-984 · AST-975

**Scope:** No `append_agent_response`; RESPONSE rows tagged with `entity_id`; hop/hydrate via `list_entity_latest_agent_refs`. AST-1429 stamps the same `entity_id` on prompt rows when index is known (AST-1431 tests).

| Area | Source | Component tests |
| --- | --- | --- |
| No append symbol; RESPONSE save carries `entity_id` | `src/core/agent.py` | `TestAst984EntityColumnRetired::test_do_task_success_tags_response_entity_id` |
| Prompt-row `entity_id` stamp (SYSTEM / CACHE_* / TASK / NO_CACHE) when index is known | `src/core/agent.py` | `TestAst984EntityColumnRetired::test_do_task_success_tags_prompt_entity_id`; `test_store_prompt_blocks_stamps_entity_id_when_known`; `TestAst515AdhocWorkbenchLedger` call-site |
| Hop skips failure prefix / prefers anchor batch | same | hop tests in `TestAst597*` / `TestAst769*` (list API mocks) |

**AST-984** narrowed run: see `docs/test-bible/data/database/agent_responses.md` (§ AST-984).

### AST-1431 · AST-1423

**Scope:** Gap from AST-1429 `[board-betty] TESTS: REVISE` — `do_task` / `_store_prompt_blocks` / Ad Hoc Test stamp `entity_id` on prompt rows, not only RESPONSE.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt saves share RESPONSE `entity_id` | `src/core/agent.py` | `TestAst984EntityColumnRetired::test_do_task_success_tags_prompt_entity_id` |
| Helper kwarg on / omitted | same | `TestAst984EntityColumnRetired::test_store_prompt_blocks_stamps_entity_id_when_known` |
| Ad Hoc call-site forwards `entity_id` | same | `TestAst515AdhocWorkbenchLedger` success + failure |

**AST-1431** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst984EntityColumnRetired::test_do_task_success_tags_prompt_entity_id \
  tests/component/core/test_agent.py::TestAst984EntityColumnRetired::test_store_prompt_blocks_stamps_entity_id_when_known \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  -q
```

### AST-1486 · AST-1423

**Scope:** Gap from AST-1486 `[board-betty] TESTS: REVISE` — `store_feedback_block` / FEEDBACK rows stamp `entity_id` when index is known (AST-724/862 only asserted block presence).

| Area | Source | Component tests |
| --- | --- | --- |
| Capture path stamps FEEDBACK `entity_id` | `src/core/agent.py` → `store_feedback_block` | `TestAst1486FeedbackEntityIdStamp::test_capture_feedback_block_stamps_entity_id_when_index_known` |
| Omitted index → null | same | `TestAst1486FeedbackEntityIdStamp::test_capture_feedback_block_entity_id_null_when_index_omitted` |
| Direct `store_feedback_block` writer | `src/data/database.py` | `TestAst1486FeedbackEntityIdStamp::test_store_feedback_block_stamps_entity_id_when_index_known` |

**AST-1486** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1486FeedbackEntityIdStamp \
  -q
```

---

### AST-1005 · AST-994

**AST-1005 (UAT bug):** `_validate_response_schema` validates `items_schema` list elements via `_validate_schema_object_fields` (plain object field checks) — not recursive envelope validation — so experience job objects get path-prefixed field errors (`experience[i]: …`) instead of misleading envelope/`candidate_name` fallout. Promote path: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| items_schema object-field validation | `src/core/agent.py` | **`TestAst1005ItemsSchemaObjectValidation`**; reuse **`TestResponseSchemaBranches`** |

**Broken / obsolete this pass:** `TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema` fixture updated to include required criteria `code` (items_schema now correctly enforces object fields).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1005ItemsSchemaObjectValidation \
  tests/component/core/test_agent.py::TestResponseSchemaBranches \
  -q
```

---

### AST-1037 · AST-1036

**AST-1037:** Ruth `simple_resume_parse` task — shared `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` with Judith `craft_resume_base`; `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` frozenset gates `normalize_craft_resume_base_agent_payload` in `do_task` (both sync validation sites). Repo `agent_task` seed + AST-756 fixture sync. Admin session wire = sibling **AST-1038**. Config: **`docs/test-bible/utils/config.md`**. Catalog: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Normalize gate membership | `src/core/agent.py` | **`TestAst1037NormalizeGateMembership`** |

**Broken / obsolete:** AST-786 catalog frozenset — `preamble_validate_response` → `simple_resume_parse` on this tip’s origin/dev base (parallel AST-1015 row not on base).

**Integration:** no existing scenario asserts session-parse task key — no revision; do not invent new integration coverage.

**AST-1037** narrowed run (agent slice):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1037NormalizeGateMembership \
  -q
```


### AST-1072 · AST-1046

**Parent:** [AST-1046 — Contact Estelle conversational envelope](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope). **Publish:** `origin/sub/AST-1046/AST-1072-conversational-agent-envelope`.

`do_task` CHAT contract for `contact_estelle_turn`: ternary `agent_performance.status` (`success` | `failure` | `concern`); concern requires non-empty `admin_aside` and is **not** `Agent failure`; preserve `agent_performance` + `conversational_outcome` on result; `conversational_turn_from_do_task_result` helper; brain override from `CONTACT_ESTELLE_CONFIG` Medium (Estelle agent row stays Big for upshot); Style D debug index/detail when `debug=True`. Config: **`docs/test-bible/utils/config.md`**. Catalog: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validate + helper + do_task preserve / brain / debug | `src/core/agent.py` | **`TestAst1072ConversationalEnvelope`** |

**Broken / obsolete:** none for agent paths — non-CHAT binary failure path unchanged.

**Integration:** no existing scenario asserts conversational envelope — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1072ConversationalEnvelope \
  -q
```

### AST-1076 · AST-1058 (UAT)

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`.

`_store_response_block` assigns `result = save_agent_data(...)` so debug `result.get("outcome")` does not NameError (mirrors prompt `_save`).

| Area | Source | Component tests |
| --- | --- | --- |
| RESPONSE debug result bind | `src/core/agent.py` | **`TestAst1076StoreResponseDebugResult`** (also covered by **`TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome`**) |

**Broken / obsolete:** none — bugfix for existing debug path.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1076StoreResponseDebugResult \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome \
  -q
```

### AST-1083 · AST-952 (UAT)

**Parent:** [AST-952 — Candidate profile preamble to intake](https://linear.app/astralcareermatch/issue/AST-952). **Publish:** `origin/sub/AST-952/AST-1083-uat-store-response-block-nameerror`.

Same `_store_response_block` / `debug=True` `result` bind as **AST-1076** (intake initiate path on Candidate Intake). Existing suites already assert the Correct outcome — no new cases.

| Area | Source | Component tests |
| --- | --- | --- |
| RESPONSE debug result bind | `src/core/agent.py` | **`TestAst1076StoreResponseDebugResult`** + **`TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1076StoreResponseDebugResult \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome \
  -q
```

### AST-1099 · AST-1091

**Parent:** [AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1099-pin-agent-data-id`.

After successful RESPONSE store for `finalize_job_resume` / `finalize_cover_letter` / `propose_application_responses`, `do_task` pins the RESPONSE `agent_data_id` into `job_data.artifacts` **before** `run_next` (mid-chain + terminal). Failed hops do not pin. Terminal body-copy via `persist_job_artifact_from_parsed` removed for finalize hops. Sibling `resume_content` copy after the resume pin is **AST-1430**. Config map: **`docs/test-bible/utils/config.md`**. Tracker helper: **`docs/test-bible/core/tracker.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Mid-chain / terminal pin + no `persist_job_artifact_from_parsed` | `src/core/agent.py` | **`TestAst1099DoTaskArtifactPin`** |

**Broken / obsolete:** terminal `persist_job_artifact_from_parsed` for finalize hops (still unused). Cover / `proposed_answers` stay pin-only. Resume sibling blob copy is **AST-1430**.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin \
  -q
```

### AST-1430 · AST-1422

**Parent:** [AST-1422](https://linear.app/astralcareermatch/issue/AST-1422/finalize-job-resume-isnt-getting-parsed-into-the-job-resume-renderer). **Publish:** `origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin`. Product fix: **AST-1428**.

After a successful `finalize_job_resume` pin, `do_task` calls `persist_finalize_job_resume_content(index, parsed)` (best-effort; does not revive `persist_job_artifact_from_parsed`). Pin string stays. PUT keep-pin: **`docs/test-bible/ui/api/api_jobs.md`** § AST-1430.

| Area | Source | Component tests |
| --- | --- | --- |
| Sibling copy after pin | `src/core/agent.py` | **`TestAst1430DoTaskResumeContentCopy::test_finalize_copies_resume_content_keeps_pin`** |

**Broken / obsolete:** none on the pin suite — `TestAst1099DoTaskArtifactPin` still asserts `persist_job_artifact_from_parsed` unused.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1430DoTaskResumeContentCopy \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_resume_content_keeps_pin \
  -q
```

### AST-1271 · AST-1268

**Parent:** [AST-1268 — draft_job_resume response schema is wrong](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong). **Publish:** `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop`.

On successful `do_task("draft_job_resume")`, best-effort `persist_draft_job_resume_deviations(index, parsed)` (does not fail the hop). Tracker extract/save + resume-body skip: **`docs/test-bible/core/tracker.md`** § AST-1271.

| Area | Source | Component tests |
| --- | --- | --- |
| Success persist / validation skip | `src/core/agent.py` | **`TestAst1271DoTaskDeviationsPersist`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1271DoTaskDeviationsPersist \
  -q
```

### AST-1507 · AST-1460

**Parent:** [AST-1460 — Advise resume needs a coded list for clear adherence](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list`.

On successful `do_task("advise_job_resume")`, validate coded RESUME BRIEF text (post-unwrap) then best-effort `persist_advise_job_resume_coded_advice(index, parsed)`; validation failure fails hop before persist. Tracker extract/save: **`docs/test-bible/core/tracker.md`** § AST-1507. Parse/validate: **`docs/test-bible/core/candidate.md`** § AST-1507.

| Area | Source | Component tests |
| --- | --- | --- |
| Validate gate + success persist / failure skip | `src/core/agent.py` | **`TestAst1507DoTaskResumeAdvicePersist`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1507DoTaskResumeAdvicePersist \
  -q
```

### AST-1514 · AST-1460 (bug-repro)

**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1514-advise-resume-brief-validation`.

`do_task("advise_job_resume")` must validate + persist when post-unwrap `parsed` is a JSON-string or dict with config `resume_advice_json_key` (`resume_brief`). Primary parse/validate: **`docs/test-bible/core/candidate.md`** § AST-1514.

| Area | Source | Component tests |
| --- | --- | --- |
| JSON-string / dict success + persist | `src/core/agent.py` | **`TestAst1514DoTaskResumeBriefJsonPersist`** (bug-repro) |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1514DoTaskResumeBriefJsonPersist \
  -q
```

### AST-1508 · AST-1460

**Parent:** [AST-1460 — Advise resume needs a coded list for clear adherence](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1508-judith-per-code-advice-adherence`.

On successful `do_task("draft_job_resume")`, validate per-code **`advice_adherence`** against **`get_job_resume_advice_codes`** (post resume whitelist) then best-effort **`persist_draft_job_resume_advice_adherence`**. Replaces **AST-1271** deviations persist. Tracker extract/save: **`docs/test-bible/core/tracker.md`** § AST-1508. Parse/validate: **`docs/test-bible/core/candidate.md`** § AST-1508.

| Area | Source | Component tests |
| --- | --- | --- |
| Validate gate + success persist / failure skip | `src/core/agent.py` | **`TestAst1508DoTaskAdviceAdherencePersist`** |

**Broken / obsolete:** **`TestAst1271DoTaskDeviationsPersist`** — retired; stub asserts persist helper removed.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1508DoTaskAdviceAdherencePersist \
  -q
```

### AST-1523 · AST-1460

**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence`.

Draft success persists freeform **`notes`**; advise accepts freeform RESUME BRIEF (no coded validate/persist). Primary: **`docs/test-bible/core/candidate.md`** § AST-1523.

| Area | Source | Component tests |
| --- | --- | --- |
| Notes persist + freeform advise | `src/core/agent.py` | **`TestAst1523DoTaskNotesPersist`**, **`TestAst1523AdviseFreeformSuccess`**, **`TestAst1523EpicAgentHooksRemoved`** |

**Broken / obsolete:** **`TestAst1507DoTaskResumeAdvicePersist`**, **`TestAst1508DoTaskAdviceAdherencePersist`** — retired.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1523DoTaskNotesPersist \
  tests/component/core/test_agent.py::TestAst1523AdviseFreeformSuccess \
  tests/component/core/test_agent.py::TestAst1523EpicAgentHooksRemoved \
  -q
```

### AST-1252 · AST-1243

**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain). **Publish:** `origin/sub/AST-1243/AST-1252-artifacts-dispatch-chain`.

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-1252. `do_task` persists candidate craft hops when `ctx.persist_candidate_craft_hops` is set.

| Area | Source | Component tests |
| --- | --- | --- |
| Persist hook | `src/core/agent.py` | **`TestAst1252PersistCandidateCraftHops`** |


### AST-1264 · AST-1243

**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain). **Publish:** `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next`.

Restore `run_next` succession after `craft_get_rubric` on `persist_candidate_craft_hops`: re-inject live `CALLER_*` into recurse ctx; skip / fail-open child hydration when live CALLER present; Style D detail when succession stops after persist. Migration neuter: **`docs/test-bible/data/database/agent_tasks.md`** § AST-1264.

| Area | Source | Component tests |
| --- | --- | --- |
| CALLER reinject + hydrate skip/hard-fail | `src/core/agent.py` | **`TestAst1264CandidateCraftSuccession`** |

**Broken / obsolete:** AST-1113 migration “corrects wrong links” asserts (now no-op).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession \
  tests/component/data/database/test_agent_tasks.py::TestAst1113CraftRunNextChainMigration \
  -q
```

### AST-1112 · AST-1109

**Parent:** [AST-1109 — Hard-coded daisy chain in config.py](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy). **Publish:** `origin/sub/AST-1109/AST-1112-anomaly-resume-hop-task-keys`.

Primary config map: **`docs/test-bible/utils/config.md`** AST-1112. Agent surface: `_resume_artifact_parent_hop_key` deleted; `_parent_hop_task_key_for_child` is sole parent resolver (ambiguous parents → `None`); hydrate/debug no longer consult `resume_artifact_hop_task_keys`.

| Area | Source | Component tests |
| --- | --- | --- |
| Parent via `run_next` | `src/core/agent.py` | **`TestAst597MidChainResumeHydrationAndTransitions::test_parent_hop_task_key_*`** |
| Hydrate entry chain context | `src/core/agent.py` | revised **`test_hydrate_resume_entry_chain_context_*`** |

**Broken / obsolete (Betty revision):** **`test_resume_artifact_parent_hop_key_*`**.

**AST-1112** agent slice (full narrowed run in config bible):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  -q
```

### AST-1144 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`.

Regression: `_validate_response_schema` accepts realistic `parse_meteorite_email` html_links payload with `jobs[].metadata` as dict; rejects str (pre-fix contract). Schema source: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Dict metadata validates / str rejected | `src/core/agent.py` | **`TestAst1144ParseMeteoriteEmailMetadataDict`** (retired — see **AST-1529**) |

**Broken / obsolete (AST-1529):** class replaced by **`TestAst1529StageMeteoriteSchemaValidate`** — `TASK_CONFIG["meteorite_email"]` parse schema removed.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1529StageMeteoriteSchemaValidate \
  -q
```

### AST-1192 · AST-1163

**Parent:** [AST-1163 — Issues while running anticipate_scan](https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan). **Publish:** `origin/sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names`.

Artifact hop `do_task` + Manage Tasks `preview_task_prompt` feed `build_candidate_token_view` (name columns + library blobs) so `{$FIRST_NAME}` / `{$LAST_NAME}` resolve on `anticipate_scan` / shared hops. Dispatch rafts load the full candidate row by `astral_candidate_id`. Style D found/recorded for name-token outcomes when `debug=True`. Boundaries: ANALYSIS match parity (**AST-1193**); provider blank/timeout (**AST-1164**).

| Area | Source | Component tests |
| --- | --- | --- |
| `_token_view_for_do_task` branches + `do_task` name resolve + Style D | `src/core/agent.py` | **`TestAst1192TokenViewForDoTask`** |
| `preview_task_prompt` columns → name tokens | `src/core/candidate.py` | **`TestPreviewTaskPrompt::test_preview_resolves_names_from_columns_not_blob`** |

**Broken / obsolete:** none — additive cutover at resolve boundary; `_candidate_data_for_job` blob consumers unchanged.

**Integration:** no existing scenario asserts artifact-hop name-token wiring — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1192TokenViewForDoTask \
  tests/component/core/test_candidate.py::TestPreviewTaskPrompt::test_preview_resolves_names_from_columns_not_blob \
  -q
```


### AST-1212 · AST-1182

**Parent:** [AST-1182 — Rename task to meteorite_email + AI payload as visible text/links](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks). **Publish:** `origin/sub/AST-1182/AST-1212-rename-parse-meteorite-email-to-meteorite-email`.

`_validate_response_schema` regression for Ruth html_links payload now keys **`meteorite_email`** (was `parse_meteorite_email`). Schema source: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Dict metadata validates / str rejected | `src/core/agent.py` | revised **`TestAst1144ParseMeteoriteEmailMetadataDict`** |

**Broken / obsolete:** AST-1144 skipif + schema lookups on `TASK_CONFIG["parse_meteorite_email"]`.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  -q
```

### AST-1221 · AST-1184

**Parent:** [AST-1184 — Task config aliases via master_task_key](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key). **Publish:** `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`.

`_resolve_task_prompts` fetches `agent_task` / `agent` via `resolve_task_key_for_content` (alias → master); caller `task_key` stays identity for orchestration. `_is_strict_encoded_batch_consult` wraps resolve for both strict-envelope gate sites. Style D alias→master detail when `debug=True`. Consult / config / dispatcher: sibling bible files under this ticket.

| Area | Source | Component tests |
| --- | --- | --- |
| Prompt fetch master + strict membership | `src/core/agent.py` | **`TestAst1221RuntimeAliasAgent`** |

**Broken / obsolete:** none for agent paths — additive resolve at prompt choke point.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1221RuntimeAliasAgent \
  -q
```

### AST-1293 · AST-1289

**Parent:** [AST-1289 — Handling datatype issues in responses](https://linear.app/astralcareermatch/issue/AST-1289/handling-datatype-issues-in-responses). **Publish:** `origin/sub/AST-1289/AST-1293-soft-coerce-numeric-schema-strings`.

Pre-validate soft-coerce on shared `do_task` path: `_coerce_schema_str_fields_from_list` joins list→str (unchanged) and now int→str (`type(val) is int`, bool excluded) including nested `items_schema` (e.g. `jobs[].astral_job_id`). Style D found→recorded only when `debug=True`. Schema field types in `TASK_CONFIG` stay `str`.

| Area | Source | Component tests |
| --- | --- | --- |
| Nested int slot echo + validate; list regression; bool/dict/float hard-fail; Style D gate; config type | `src/core/agent.py` | **`TestAst1293SoftCoerceNumericSchemaStrings`** |
| Existing list→str habit | `src/core/agent.py` | **`TestResponseSchemaBranches::test_coerce_schema_str_list_to_newlines_before_validate`** |

**Broken / obsolete:** none — additive coerce gate; validator type checks unchanged (ints never reach them on the happy path).

**Integration:** no existing scenario asserts integer slot-id rejection — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1293SoftCoerceNumericSchemaStrings \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_coerce_schema_str_list_to_newlines_before_validate \
  -q
```

### AST-1355 · AST-1316 (gap — agent-story tests after AST-1354)

**Parent:** [AST-1316](https://linear.app/astralcareermatch/issue/AST-1316/cant-find-agent-data-for-proposed-application-responses). **Sibling product:** AST-1354 (`get_entity_agent_story` → `agent.py`; metadata-only list; per-id soft-fail). **Publish:** `origin/sub/AST-1316/AST-1355-gap-agent-story-tests`.

Retarget entity-story coverage from roster → agent; add dangling `propose_application_responses` TASK sibling → partial story / no `logger.exception` stack (**[bug-repro]**).

| Area | Source | Component tests |
| --- | --- | --- |
| Story ownership + enrich / AST-520 label | `src/core/agent.py` (`get_entity_agent_story`) | **`TestEntityAgentStory`** |
| Duplicate block labels / scored filter | same + `_filter_response_block` | **`TestEntityAgentStoryBranches`**, **`TestFilterResponseBlock`** |
| Soft-fail list / per-id resolve (AST-1274/1354) | same | **`TestAst1274AgentStorySoftFail`** |
| Dangling TASK sibling → partial story, warning only | same | **`TestAst1354AgentStoryDanglingTaskSibling::test_partial_story_no_exception_stack`** (**[bug-repro]**) |
| Company `vector_grades` (AST-726) | same | **`TestEntityAgentStory::test_company_prefilter_vector_grades_from_company_data`** |

**Broken / obsolete:** roster `TestEntityAgentStory*` / `TestAst1274AgentStorySoftFail` / `TestFilterResponseBlock` / story method on `TestAst726LatestOnlyRosterStory` — deleted; bible rows retargeted here + `docs/test-bible/core/roster.md` / `frontend/components.md`.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestEntityAgentStory \
  tests/component/core/test_agent.py::TestFilterResponseBlock \
  tests/component/core/test_agent.py::TestEntityAgentStoryBranches \
  tests/component/core/test_agent.py::TestAst1274AgentStorySoftFail \
  tests/component/core/test_agent.py::TestAst1354AgentStoryDanglingTaskSibling \
  -q
```

### AST-1448 · AST-1442 (persist prompt before provider)

**Parent:** [AST-1442](https://linear.app/astralcareermatch/issue/AST-1442). **Publish:** `origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`.

Stored `do_task` and Ad Hoc workbench Test commit prompt segments via `_store_prompt_blocks` **before** `send_to_anthropic` / `run_adhoc`. `_store_response_block` stays after return. Persist failure is swallowed. `store_agent_data=False` and bare `run_adhoc` write no `agent_data`. Latest-per-task stays RESPONSE-gated. Debug found/recorded for prompt persist happens before the provider await; quiet when `debug=False`.

| Area | Source | Component tests |
| --- | --- | --- |
| `do_task` prompt-before-await + RESPONSE after | `src/core/agent.py` | **`tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider`** |
| Kill mid-call + later batch isolation | same | **`test_do_task_provider_raise_keeps_prompt_omits_response`**, **`test_do_task_later_success_does_not_rewrite_interrupted_batch_prompts`** |
| Storage-off / persist failure / debug | same | **`test_do_task_storage_off_skips_prompt_and_response`**, **`test_do_task_prompt_persist_failure_still_calls_provider`**, **`test_do_task_debug_emits_prompt_found_recorded_before_provider`**, **`test_do_task_debug_false_skips_persist_contract_lines`** |
| Workbench Test sequencing; bare `run_adhoc` | same | **`test_workbench_stores_prompt_before_run_adhoc`**, **`test_workbench_raise_keeps_prompt_omits_response`**, **`test_bare_run_adhoc_does_not_store_agent_data`** |
| Prompt-only batch is not latest story | `src/data/database.py` | **`test_prompt_only_batch_is_not_latest_ref`**; existing **`tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired::test_list_latest_per_task_key`** |
| Existing store-once + ledger | `src/core/agent.py` | **`TestDoTask::test_returns_api_failure_and_stores_agent_data`**, **`TestAst515AdhocWorkbenchLedger`**, **`TestDoTaskStorageFailures`** |

**Broken / obsolete:** none — `_store_prompt_blocks` still runs once; order moved before the await. Count-only tests still hold.

**Integration:** no existing scenario asserts in-flight `agent_data` vs provider await — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired::test_list_latest_per_task_key \
  -q
```

### AST-1451 · AST-1439 (Ad Hoc import list and load payload)

**Parent:** [AST-1439](https://linear.app/astralcareermatch/issue/AST-1439). **Publish:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload`.

Read path only: `list_agent_data_batches` / `list_agent_data_runs` (one row per `batch_id`, newest first, includes `adhoc-*`); `GET /api/admin/adhoc/runs` `@require_admin`; Style D found→recorded on the list when `debug=True`; one leading `adhoc-` strip in `run_adhoc_workbench_test` so ledger stays `adhoc-<task_key>`. Load body is existing `GET /api/agent_data/<batch_id>` (unchanged). Picker chrome: sibling AST-1452. **Filter/cap (candidate + task_key + config limit):** superseded by **AST-1534** — unfiltered full-history list retired.

| Area | Source | Component tests |
| --- | --- | --- |
| One row per batch; newest first; adhoc + production; no `block_data` | `src/data/database.py` (`list_agent_data_batches`) | **`TestAst1451ListAgentDataBatches`** |
| Core list + debug gate | `src/core/agent.py` (`list_agent_data_runs`) | **`TestAst1451ListAgentDataRuns`** |
| Catalog key still `adhoc-<task_key>` | same (`run_adhoc_workbench_test`) | existing **`TestAst515AdhocWorkbenchLedger`** |
| Prefixed workbench key does not double `adhoc-`; `TASK_CONFIG` uses stripped key | same | **`TestAst515AdhocWorkbenchLedger::test_prefixed_workbench_key_does_not_double_adhoc`** |
| Admin list JSON + auth + `ui_llm_debug` | `src/ui/api/api_admin.py` (`adhoc_runs`) | **`TestAst1451AdhocRuns`** |
| Load payload (existing GET) | `src/ui/api/api_system.py` | existing **`TestSystemAuthRoutes::test_agent_data_returns_rows`** |

**Broken / obsolete this pass:** none originally — **AST-1534** revises list mocks/asserts for filter kwargs (see § AST-1534).

**Integration:** no existing scenario covers admin Ad Hoc list/load — v1 harness is system+candidate only. Do not invent new integration coverage.

## QA test manifest

1. Data list: `tests/component/data/database/test_agent_data.py::TestAst1451ListAgentDataBatches`
2. Core list debug: `tests/component/core/test_agent.py::TestAst1451ListAgentDataRuns`
3. Ledger prefix (existing + new): `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`
4. Admin GET: `tests/component/ui/api/test_api_admin.py::TestAst1451AdhocRuns`
5. Load GET (existing): `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_agent_data_returns_rows`

**AST-1451** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py::TestAst1451ListAgentDataBatches \
  tests/component/core/test_agent.py::TestAst1451ListAgentDataRuns \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/ui/api/test_api_admin.py::TestAst1451AdhocRuns \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_agent_data_returns_rows \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1513 · AST-1510

**Parent:** [AST-1510 — meteorite_grade_do incomplete grade set (duplicate Do rubric TP codes)](https://linear.app/astralcareermatch/issue/AST-1510). **Publish:** `origin/sub/AST-1510/AST-1513-reject-duplicate-do-rubric-codes`.

Board REVISE (optional Step 4): `_decode_payload` should fail fast when the same two-char vector code appears twice on one encoded line (`…|TPB4|TPB4`). Contingent on make-fix landing Step 4.

| Area | Source | Component tests |
| --- | --- | --- |
| Duplicate segment guard on encoded line | `src/core/agent.py` (`_decode_payload`) | **`TestAst1513DuplicateRubricCodes::test_decode_rejects_duplicate_tp_segments_on_one_line`** (**[bug-repro]**, Step 4 optional) |

**Broken / obsolete:** none — additive guard on duplicate segments only.

**Integration:** none.

## QA test manifest

1. Decode duplicate guard (bug-repro, Step 4 optional): `tests/component/core/test_agent.py::TestAst1513DuplicateRubricCodes::test_decode_rejects_duplicate_tp_segments_on_one_line`

**Pass criterion:** red pre-fix; green if make-fix lands Step 4 (skip/xfail acceptable if engineer omits optional decode guard).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1513DuplicateRubricCodes \
  -q
```


---

### AST-1529 · AST-1527

**Parent:** [AST-1527 — Generalize Meteorite Ingress Point](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point). **Publish:** `origin/sub/AST-1527/AST-1529-stage-meteorite-catalog-config`.

`_validate_response_schema` for `stage_meteorite`: closed `outcome` enum + `jobs` list; unknown outcomes rejected. Supersedes AST-1144 / AST-1212 parse `metadata` / `parse_mode` validation. Schema SSOT: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Landable / skip / unknown outcome | `src/core/agent.py` | **`TestAst1529StageMeteoriteSchemaValidate`** |

**Broken / obsolete:** **`TestAst1144ParseMeteoriteEmailMetadataDict`** — rewritten as **`TestAst1529StageMeteoriteSchemaValidate`**.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1529StageMeteoriteSchemaValidate \
  -q
```


### AST-1534 · AST-1532 (Scoped adhoc runs list API)

**Parent:** [AST-1532](https://linear.app/astralcareermatch/issue/AST-1532). **Publish:** `origin/sub/AST-1532/AST-1534-scoped-adhoc-runs-list-api`.

Backend scoped import list: `UI_CONFIG` cap (10) + picker visible rows (5); `list_agent_data_batches` joins `dispatch_ledger` for `candidate_id`, optional `task_key` with one leading `adhoc-` strip equivalence, `ORDER BY created_at DESC` + `limit`; `list_agent_data_runs` forwards kwargs and Style D debug only on returned rows; `GET /api/admin/adhoc/runs` reads `candidate_id`/`task_key`, uses config limit (ignores client `limit`). React chrome: **AST-1535**.

| Area | Source | Component tests |
| --- | --- | --- |
| Config literals | `src/utils/config.py` (`UI_CONFIG`) | **`TestAst1534AdhocImportConfigKeys`** |
| Blank candidate → `[]`; scoped newest-first; no `block_data` | `src/data/database.py` | revised **`TestAst1451ListAgentDataBatches`** |
| Candidate scope + ledgerless exclude; `adhoc-` task equiv; empty task; limit | same | **`TestAst1534ScopedListAgentDataBatches`** |
| Core Style D debug gate | `src/core/agent.py` | revised **`TestAst1451ListAgentDataRuns`** |
| Forwards kwargs; debug only on returned set | same | **`TestAst1534ListAgentDataRunsFilters`** |
| Admin auth + debug forward | `src/ui/api/api_admin.py` | revised **`TestAst1451AdhocRuns`** |
| Query params + config cap; blank → none; ignore client limit | same | **`TestAst1534AdhocRunsScoped`** |

**Broken / obsolete this pass:** AST-1451 unfiltered/no-cap list assumptions — revised in place (blank candidate, kwargs-accepting mocks).

**Integration:** no existing scenario covers admin Ad Hoc list — do not invent.

## QA test manifest

1. Config keys: `tests/component/utils/test_config.py::TestAst1534AdhocImportConfigKeys`
2. Data scoped list: `tests/component/data/database/test_agent_data.py::TestAst1451ListAgentDataBatches`
3. Data filter/limit: `tests/component/data/database/test_agent_data.py::TestAst1534ScopedListAgentDataBatches`
4. Core debug + kwargs: `tests/component/core/test_agent.py::TestAst1451ListAgentDataRuns`
5. Core filter forward: `tests/component/core/test_agent.py::TestAst1534ListAgentDataRunsFilters`
6. Admin auth: `tests/component/ui/api/test_api_admin.py::TestAst1451AdhocRuns`
7. Admin scoped GET: `tests/component/ui/api/test_api_admin.py::TestAst1534AdhocRunsScoped`

**AST-1534** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1534AdhocImportConfigKeys \
  tests/component/data/database/test_agent_data.py::TestAst1451ListAgentDataBatches \
  tests/component/data/database/test_agent_data.py::TestAst1534ScopedListAgentDataBatches \
  tests/component/core/test_agent.py::TestAst1451ListAgentDataRuns \
  tests/component/core/test_agent.py::TestAst1534ListAgentDataRunsFilters \
  tests/component/ui/api/test_api_admin.py::TestAst1451AdhocRuns \
  tests/component/ui/api/test_api_admin.py::TestAst1534AdhocRunsScoped \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1550 · AST-1541

**Parent:** [AST-1541](https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal). **Publish:** `origin/sub/AST-1541/AST-1550-discussion-tab-config-story-task-name`.

`get_entity_agent_story` attaches `task_name` from the live `agent_task` row when non-empty; omits the key when blank/missing (UI falls back to `task_key`). Additive — Agent Story tabs unchanged. Config hop walk + manifest sections: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_system.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Attach / omit `task_name` | `src/core/agent.py` (`get_entity_agent_story`) | **`TestAst1550AgentStoryTaskName`** |

**Broken / obsolete:** none — additive field; existing **`TestEntityAgentStory`** still holds.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1550AgentStoryTaskName \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

