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
| `do_task` skip when no candidate | `src/core/agent.py` | **AST-1639 revised:** `TestAst820VectorFeedbackDebugTrace::test_do_task_fail_closed_when_candidate_id_missing` (blank id raises before send; old skip-feedback path obsolete) |

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

**Scope:** Dispatch-chain hop success increments `_dispatch_chain_hop_index` on ctx (fixes multi-hop BUILD_ARTIFACTS `index 2/1`). Style D helpers `_dispatch_chain_hop_debug_counts` / `_resume_hop_debug_index` are gone.

| Area | Source | Component tests |
| --- | --- | --- |
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

**`do_task`:** coerce blank provider `error=` to a non-empty string on the return; agent does **not** emit a second `logger.error` (provider `log_llm_batch_summary(..., error=)` is the hop error line). When `log_batch_id` is unset, warning `{task_key} skipped — provider failed`. **`debug=True`** detail when **`is_provider_empty_response`**. Primary manifest: **`docs/test-bible/utils/llm_external.md`** § AST-1190.

| Area | Source | Component tests |
| --- | --- | --- |
| Blank-error coerce + empty-response debug | `src/core/agent.py` | **`TestAst1190DoTaskEmptyProviderError`** |

### AST-1191 · AST-1164

**Dispatch-chain provider hop failure:** `_apply_dispatch_chain_hop_failure` — provider failures (balance or otherwise) hold state — no `error_state` — and release the claim; only `Job not found` / `Missing candidate_data` apply `error_state` then release (**AST-1941**, supersedes the AST-1191 provider → `error_state` rule); `_close_hop_ledger` returns outcome on every exit. **`debug=True`:** found (duration/stop/tokens/`failure_class`, `n/a` not silent 0) + recorded (error / error_state|held / batch_released). Hop-label-false non-job (or no index) → `_HOP_FAILURE_NOOP`; hop-label-false **job** + `provider_failed` claim release is **AST-1298**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hop failure apply (provider → held state) + claim release + debug | `src/core/agent.py` | **`TestAst1191ArtifactHopFailureRelease`** |
| Bug repro: provider failure holds state (AST-1941 / AST-1942) | `src/core/agent.py` | **`TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_holds_state_and_releases`** |
| Hard-string path still transitions (release added) | `src/core/agent.py` | **`TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts`** |

**AST-1191** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst1191ArtifactHopFailureRelease \
  tests/component/core/test_agent.py::TestAst848DispatchChainDoTask::test_hard_failure_transitions_error_build_artifacts \
  -q
```

**AST-1942 manifest (`[bug-repro]`, parent AST-1940):** repro node `TestAst1191ArtifactHopFailureRelease::test_apply_provider_failed_holds_state_and_releases` — red on `origin/dev` `src/core/agent.py` (provider clause transitions → `assert_not_called` fails), green on the AST-1941 tip. Run the narrowed command above plus `tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease`; all green. `test_agent.py` + `test_llm_external.py` failures must equal the 40 pre-existing ftr-baseline nodes (none in these classes).

### AST-1298 · AST-1280

**Parent:** [AST-1280 — Connection error on dispatch task did not clear the batch_id](https://linear.app/astralcareermatch/issue/AST-1280/connection-error-on-dispatch-task-did-not-clear-the-batch-id). **Publish:** `origin/sub/AST-1280/AST-1298-release-orphaned-job-claim-after-provider-connection-error`.

Close orphaned job `batch_id` after provider Connection-style failure on hop-label-true BUILD_ARTIFACTS dispatch: helper `try`/`finally` still releases when `transition_job_state` raises non-`ValueError` (reachable on hard strings only since AST-1941); consult `_run_dispatch_chain_job_batch` releases when `do_task` raises; hop-label-false job+`provider_failed` defense-in-depth release (no error_state). No new debug contract strings; `debug=True` keeps recorded `batch_released=true`.

| Area | Source | Component tests |
| --- | --- | --- |
| Transition non-`ValueError` (hard string `Job not found`) still releases | `src/core/agent.py` | **`TestAst1298OrphanedJobClaimRelease::test_apply_transition_non_value_error_still_releases`** |
| `draft_job_resume` Connection error → held state (no transition) + release + debug (AST-1941) | `src/core/agent.py` | **`TestAst1298OrphanedJobClaimRelease::test_do_task_draft_job_resume_connection_error_releases_and_errors`** |
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
| `debug=True` does not put `[DEBUG] do_task` on info | same | **`test_debug_true_max_tokens_line_shows_floor`** |
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

Workbench Test success path stringifies the extracted body via **`_caller_response_blob`** before **`_store_response_block`**: dict/list → compact JSON text; already-`str` unchanged; empty `{}` / `[]` store as `"{}"` / `"[]"` (not `""`). Envelope still extracts **`agent_payload`** when present. Does **not** own Admin HTTP/React (sibling #2) or `do_task` schema coerce. Data layer still raises on non-text.

| Area | Source | Component tests |
| --- | --- | --- |
| Object payload JSON text + ledger COMPLETED | `src/core/agent.py` (`run_adhoc_workbench_test`) | **`TestAst1393SerializeAdhocSuccessBody::test_success_stores_serialized_text`** (`object-payload`) |
| Empty dict/list, list payload, plain text, dict without payload key | same | **`test_success_stores_serialized_text`** (remaining ids) |
| String payload regression | same | **`TestAst515AdhocWorkbenchLedger::test_success_completes_ledger_and_stores_blocks`**; **`test_success_stores_serialized_text`** (`str-payload`) |
| Serialize still holds under `debug=True` / `debug=False` | same | **`test_debug_true_style_d_found_to_recorded`**, **`test_debug_false_adds_no_serialize_lines`** |
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

Originally pinned RESPONSE `agent_data_id` for finalize + propose hops. **AST-1548 / AST-1554:** finalize hops write **body replicas** instead; only `propose_application_responses` → `proposed_answers` still pins. Failed hops do not pin/replica. Config maps: **`docs/test-bible/utils/config.md`**. Tracker helpers: **`docs/test-bible/core/tracker.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Finalize body replica + propose pin only | `src/core/agent.py` | **`TestAst1099DoTaskArtifactPin`** |

**Broken / obsolete:** pin asserts for `finalize_job_resume` / `finalize_cover_letter` — superseded by AST-1548 body replica (see **AST-1554**).

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin \
  -q
```

### AST-1430 · AST-1422

**Parent:** [AST-1422](https://linear.app/astralcareermatch/issue/AST-1422/finalize-job-resume-isnt-getting-parsed-into-the-job-resume-renderer). **Publish:** `origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin`. Product fix: **AST-1428**.

Historical keep-pin + sibling-`resume_content` copy. **Broken / obsolete under AST-1548/AST-1554:** `test_finalize_copies_resume_content_keeps_pin` — replaced by body-on-`job_resume` nodes below.

### AST-1554 · AST-1547 (gap — body replica tests)

**Parent:** [AST-1547](https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record). Product fix: **AST-1548**. **Publish:** `origin/sub/AST-1547/AST-1554-gap-job-resume-body-replica-tests`.

After successful RESPONSE store, `do_task` calls `persist_finalize_job_resume_content` / `persist_finalize_cover_letter_content` for finalize hops (no `pin_job_artifact_agent_data_id` on those slots). PUT dual-write: **`docs/test-bible/ui/api/api_jobs.md`**. Hydrate / persist helpers: **`docs/test-bible/core/tracker.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Resume + cover body replica, no pin | `src/core/agent.py` | **`TestAst1554DoTaskBodyReplica`** (+ revised **`TestAst1099DoTaskArtifactPin`**) |

**Broken / obsolete:** AST-1430 keep-pin copy node; AST-1099 finalize pin asserts.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1554DoTaskBodyReplica \
  tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_dual_writes_job_resume_body \
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

Retarget entity-story coverage from roster → agent; add dangling `propose_application_responses` TASK sibling → partial story / no raise to the caller (**[bug-repro]**). Thrown resolve failures log `logger.exception` then continue.

| Area | Source | Component tests |
| --- | --- | --- |
| Story ownership + enrich / AST-520 label | `src/core/agent.py` (`get_entity_agent_story`) | **`TestEntityAgentStory`** |
| Duplicate block labels / entity slice | same + `_slice_entity_block` (was `_filter_response_block`, AST-2030) | **`TestEntityAgentStoryBranches`**, **`TestSliceEntityBlock`** |
| Soft-fail list / per-id resolve (AST-1274/1354) | same | **`TestAst1274AgentStorySoftFail`** |
| Dangling TASK sibling → partial story, exception log then continue | same | **`TestAst1354AgentStoryDanglingTaskSibling::test_partial_story_does_not_raise`** (**[bug-repro]**) |
| Company `vector_grades` (AST-726) | same | **`TestEntityAgentStory::test_company_prefilter_vector_grades_from_company_data`** |

**Broken / obsolete:** roster `TestEntityAgentStory*` / `TestAst1274AgentStorySoftFail` / `TestFilterResponseBlock` / story method on `TestAst726LatestOnlyRosterStory` — deleted; bible rows retargeted here + `docs/test-bible/core/roster.md` / `frontend/components.md`.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestEntityAgentStory \
  tests/component/core/test_agent.py::TestSliceEntityBlock \
  tests/component/core/test_agent.py::TestEntityAgentStoryBranches \
  tests/component/core/test_agent.py::TestAst1274AgentStorySoftFail \
  tests/component/core/test_agent.py::TestAst1354AgentStoryDanglingTaskSibling \
  -q
```

### AST-1448 · AST-1442 (persist prompt before provider)

**Parent:** [AST-1442](https://linear.app/astralcareermatch/issue/AST-1442). **Publish:** `origin/sub/AST-1442/AST-1448-persist-prompt-before-provider`.

Stored `do_task` and Ad Hoc workbench Test commit prompt segments via `_store_prompt_blocks` **before** `send_to_anthropic` / `run_adhoc`. `_store_response_block` stays after return. Persist failure is swallowed (`logger.exception`, hop continues). `store_agent_data=False` and bare `run_adhoc` write no `agent_data`. Latest-per-task stays RESPONSE-gated.

| Area | Source | Component tests |
| --- | --- | --- |
| `do_task` prompt-before-await + RESPONSE after | `src/core/agent.py` | **`tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider`** |
| Kill mid-call + later batch isolation | same | **`test_do_task_provider_raise_keeps_prompt_omits_response`**, **`test_do_task_later_success_does_not_rewrite_interrupted_batch_prompts`** |
| Storage-off / persist failure | same | **`test_do_task_storage_off_skips_prompt_and_response`**, **`test_do_task_prompt_persist_failure_still_calls_provider`** |
| Workbench Test sequencing; bare `run_adhoc` | same | **`test_workbench_stores_prompt_before_run_adhoc`**, **`test_workbench_raise_keeps_prompt_omits_response`**, **`test_bare_run_adhoc_does_not_store_agent_data`** |
| Prompt-only batch is not latest story | `src/data/database.py` | **`test_prompt_only_batch_is_not_latest_ref`**; existing **`tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired::test_list_latest_per_task_key`** |
| Existing store-once + ledger | `src/core/agent.py` | **`TestDoTask::test_returns_api_failure_and_stores_agent_data`**, **`TestAst515AdhocWorkbenchLedger`**, **`TestDoTaskStorageFailures`** |
| Store off the event loop (AST-1842 / AST-1843) | `src/core/agent.py` (`do_task` → `asyncio.to_thread(_store_*)`) | **`tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop::test_slow_save_agent_data_does_not_block_loop`** — `[bug-repro]`: 0.3s blocking `save_agent_data`, heartbeat max gap < 0.2s; pre-fix `origin/dev` gap ≈ 1.5s (5 stores on the loop) |

**Broken / obsolete:** none — `_store_prompt_blocks` still runs once; order moved before the await. Count-only tests still hold.

**Known pre-existing reds (not AST-1842, red on `origin/dev` too):** `test_do_task_debug_emits_prompt_found_recorded_before_provider`, `test_prompt_only_batch_is_not_latest_ref`, `test_bare_run_adhoc_does_not_store_agent_data`.

**Integration:** no existing scenario asserts in-flight `agent_data` vs provider await — no revision; do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1842DoTaskStoreOffLoop \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired::test_list_latest_per_task_key \
  -q
```

### AST-1451 · AST-1439 (Ad Hoc import list and load payload)

**Parent:** [AST-1439](https://linear.app/astralcareermatch/issue/AST-1439). **Publish:** `origin/sub/AST-1439/AST-1451-ad-hoc-import-list-and-load-payload`.

Read path only: `list_agent_data_batches` / `list_agent_data_runs` (one row per `batch_id`, newest first, includes `adhoc-*`); `GET /api/admin/adhoc/runs` `@require_admin`; one leading `adhoc-` strip in `run_adhoc_workbench_test` so ledger stays `adhoc-<task_key>`. Load body is existing `GET /api/agent_data/<batch_id>` (unchanged). Picker chrome: sibling AST-1452. **Filter/cap (candidate + task_key + config limit):** superseded by **AST-1534** — unfiltered full-history list retired.

| Area | Source | Component tests |
| --- | --- | --- |
| One row per batch; newest first; adhoc + production; no `block_data` | `src/data/database.py` (`list_agent_data_batches`) | **`TestAst1451ListAgentDataBatches`** |
| Core list returns data rows | `src/core/agent.py` (`list_agent_data_runs`) | **`TestAst1451ListAgentDataRuns`** |
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

---

### AST-1576 · AST-1569

**Publish:** `origin/sub/AST-1569/AST-1576-generic-save-candidate-data`.

`do_task` persist_candidate_craft_hops: when `TASK_CONFIG[task_key]["artifact_key"]` is set, land via `save_candidate_data` (library structure + operative body); else `_persist_craft_dispatch_success`. Primary: **`docs/test-bible/core/candidate.md`** § AST-1576.

| Area | Source | Component tests |
| --- | --- | --- |
| Operative persist (not helper) | `src/core/agent.py` | **`TestAst1576CraftPersistOperative`** |
| Source hook + rubric helper still live | same | revised **`TestAst1252PersistCandidateCraftHops`** |

**Broken / obsolete:** none in agent besides source-hook expansion.

**Integration:** none.


---

### AST-1592 · AST-1588

**Publish:** `origin/sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation`.

`do_task` finalize hops call `_prepare_job_replica_body` + `save_job_artifact` driven by `TASK_CONFIG.artifact_key` (**AST-1603**; body-replica map retired under **AST-1602**). Tracker generics: **`docs/test-bible/core/tracker.md`** § AST-1592 / AST-1603.

| Area | Source | Component tests |
| --- | --- | --- |
| Finalize resume/cover → catalog write | `src/core/agent.py` | **`TestAst1099DoTaskArtifactPin`**, **`TestAst1554DoTaskBodyReplica`** (revised) |

**Broken / obsolete this pass:** spies on `persist_finalize_job_resume_content` / `persist_finalize_cover_letter_content` — retargeted to `save_job_artifact` (+ prepare mock for resume match).


### AST-1600 · AST-1588 (bug)

**Publish:** `origin/sub/AST-1588/AST-1600-job-resume-cover-not-persisting`.

Finalize body replica must land without `resp_id` (RESPONSE store failure must not skip catalog write). Tracker/data `candidate_id` land covered in **`docs/test-bible/core/tracker.md`** / **`docs/test-bible/data/database/artifacts.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Body replica lands when RESPONSE store fails | `src/core/agent.py` | **`[bug-repro]`** `TestAst1600DoTaskBodyReplicaLand::test_bug_repro_body_replica_lands_when_response_store_fails` |

**Broken / obsolete this pass:** `TestAst1099DoTaskArtifactPin::test_debug_skip_replica_when_store_fails` (deleted — assumed store_failed skips replica).

**Integration:** none.

## QA test manifest (AST-1600)

1. **[bug-repro]** agent land without resp_id: `tests/component/core/test_agent.py::TestAst1600DoTaskBodyReplicaLand`
2. **[bug-repro]** tracker cid prefer + pass-through: `tests/component/core/test_tracker.py::TestAst1600TrackerCandidateIdLand`
3. **[bug-repro]** data job-column resolve: `tests/component/data/database/test_artifacts.py::TestAst1600JobArtifactCandidateIdResolve`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1600DoTaskBodyReplicaLand \
  tests/component/core/test_tracker.py::TestAst1600TrackerCandidateIdLand \
  tests/component/data/database/test_artifacts.py::TestAst1600JobArtifactCandidateIdResolve \
  -q
```

**Pass criterion (test-fix):** [bug-repro] flips red→green after make-fix — not zero-arg harness / branch-lock gate.

### AST-1603 · AST-1601

**Parent:** [AST-1601 — Rip out job-specific artifact pin helpers; match candidate catalog pattern](https://linear.app/astralcareermatch/issue/AST-1601). **Publish:** `origin/sub/AST-1601/AST-1603-agent-tracker-land-via-task-config-artifact-key`.

`do_task` job catalog land reads `TASK_CONFIG[task].artifact_key` (entity_type job) → `_prepare_job_replica_body` + `save_job_artifact`. `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` import/branch gone. Proposed_answers pin path unchanged. Tracker pin/prepare: **`docs/test-bible/core/tracker.md`** § AST-1603. Config authority: **`docs/test-bible/utils/config.md`** § AST-1602.

| Area | Source | Component tests |
| --- | --- | --- |
| Catalog land via artifact_key; no body-replica map | `src/core/agent.py` | **`TestAst1603DoTaskCatalogLandViaArtifactKey`** |
| Revised prepare mock path (private) | same | **`TestAst1099DoTaskArtifactPin`**, **`TestAst1554DoTaskBodyReplica`**, **`TestAst1600DoTaskBodyReplicaLand`** |

**Broken / obsolete this pass:** monkeypatch / import of public `prepare_job_replica_body`; any assert that `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` still drives land; `save_job_artifact` stubs with `_candidate_id_for_job → None` (AST-1600 requires cid — revised stubs in 1554/1556/1592).

**Integration:** none — no existing scenario asserts body-replica map vs TASK_CONFIG.artifact_key land; do not invent new integration coverage.

### AST-1613 · AST-1610 (bug) — docs-acceptance

**Publish:** `origin/sub/AST-1610/AST-1613-fix-job-artifacts-prepare-empty`.

Catalog-land coerce for text-format finalize `parsed` (string JSON → dict before prepare) is product on this ticket. **No new tests on AST-1613** — `[bug-repro]` string-JSON prepare/land coverage is sibling gap **AST-1614**. Tracker note: **`docs/test-bible/core/tracker.md`** § AST-1613.

**Integration:** none.

### AST-1614 · AST-1610 (gap)

**Publish:** `origin/sub/AST-1610/AST-1614-gap-string-json-prepare-land-repro`.

`do_task` finalize with string `parsed_response` (text-format) must coerce and call `save_job_artifact` via real `_prepare_job_replica_body` (no prepare mock). Tracker prepare: **`docs/test-bible/core/tracker.md`** § AST-1614.

| Area | Source | Component tests |
| --- | --- | --- |
| String parsed → save_job_artifact | `src/core/agent.py` | **`[bug-repro]`** `TestAst1614DoTaskStringParsedCatalogLand::test_bug_repro_finalize_string_parsed_lands_save_job_artifact` |
| Tracker string prepare | `src/core/tracker.py` | **`TestAst1614StringJsonPrepare`** (see tracker.md) |

**Broken / obsolete this pass:** none — additive; AST-1603 prepare-mock suites stay as dict-path coverage.

**Integration:** none.

## QA test manifest (AST-1614)

1. **[bug-repro]** tracker string prepare: `tests/component/core/test_tracker.py::TestAst1614StringJsonPrepare`
2. **[bug-repro]** agent string land: `tests/component/core/test_agent.py::TestAst1614DoTaskStringParsedCatalogLand`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1614StringJsonPrepare \
  tests/component/core/test_agent.py::TestAst1614DoTaskStringParsedCatalogLand \
  -q
```

**Pass criterion (test-fix):** [bug-repro] green with AST-1613 coerce on tip — not zero-arg harness / branch-lock gate.

## QA test manifest

1. Primary catalog land: `tests/component/core/test_agent.py::TestAst1603DoTaskCatalogLandViaArtifactKey`
2. Revised finalize mid-chain / propose pin: `tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin`
3. Revised body replica nodes: `tests/component/core/test_agent.py::TestAst1554DoTaskBodyReplica`
4. Revised store-fail land: `tests/component/core/test_agent.py::TestAst1600DoTaskBodyReplicaLand`
5. Tracker pin keys + private prepare: `tests/component/core/test_tracker.py::TestAst1603TrackerPinKeysAndPrivatePrepare`
6. Revised prepare coat-check helpers: `tests/component/core/test_tracker.py::TestAst1554BodyReplicaPersistHelpers`
7. Revised catalog write/read citation: `tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation`
8. Revised table-SoT saves (candidate_id stub): `tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT::test_save_job_resume_body_writes_artifacts_table_not_job_data` + `test_save_cover_letter_writes_artifacts_table_not_job_data`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1603DoTaskCatalogLandViaArtifactKey \
  tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin \
  tests/component/core/test_agent.py::TestAst1554DoTaskBodyReplica \
  tests/component/core/test_agent.py::TestAst1600DoTaskBodyReplicaLand \
  tests/component/core/test_tracker.py::TestAst1603TrackerPinKeysAndPrivatePrepare \
  tests/component/core/test_tracker.py::TestAst1554BodyReplicaPersistHelpers \
  tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation \
  tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT::test_save_job_resume_body_writes_artifacts_table_not_job_data \
  tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT::test_save_cover_letter_writes_artifacts_table_not_job_data \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/agent.md` — *(filled after publish)*
- `docs/test-bible/core/tracker.md` — *(filled after publish)*

### AST-1639 · AST-1638 (candidate-id system-prompt prefix)

**Publish:** `origin/sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix`.

Shared assembly prepends `[astral-<id>]` as the first bytes of the first system text block (no separator before body); `do_task` / `run_adhoc` / `preview_prompt` / stored SYSTEM rows share that shape; blank/missing candidate id fails closed before provider send. No DeepSeek `user_id` / Anthropic metadata isolation; no second prefix outside `agent.py`.

| Area | Source | Component tests |
| --- | --- | --- |
| Helper + assemble lead + cache/user clean | `src/core/agent.py` | `TestAst1639CandidateIdSystemPrefix` (helper / assemble / preview / fail-closed) |
| Provider-agnostic wire prefix | `src/core/agent.py` | `TestAst1639CandidateIdSystemPrefix::test_do_task_anthropic_and_deepseek_both_get_prefix` |
| Fail-closed do_task | `src/core/agent.py` | `TestAst820VectorFeedbackDebugTrace::test_do_task_fail_closed_when_candidate_id_missing` |
| Legacy assemble / preview / adhoc ctx | `src/core/agent.py` | Revised: `TestPromptHelpers::test_builds_context_and_assembles_blocks`, `TestAssembleBlocks`, `TestAgentDataHelpers::test_preview_prompt_resolves_blocks`, `TestRunAdhoc`, do_task ctx helpers (`_draft_job_resume_ctx`, `_rubric_evaluate_jd_ctx`, …) now carry top-level `astral_candidate_id` |

**Broken / obsolete this pass:** `test_do_task_debug_skip_when_candidate_id_missing` (silent skip of vector-feedback capture when id missing) — replaced by fail-closed raise before send. All other do_task/assemble/preview/adhoc call sites that omitted top-level `astral_candidate_id` revised to supply one (product now requires it at assembly).

**Integration:** none (no existing integration scenario asserts un-prefixed system text).

## QA test manifest (AST-1639)

1. New prefix suite: `tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix`
2. Fail-closed revision: `tests/component/core/test_agent.py::TestAst820VectorFeedbackDebugTrace::test_do_task_fail_closed_when_candidate_id_missing`
3. Revised assemble / preview / adhoc smoke: `TestPromptHelpers::test_builds_context_and_assembles_blocks`, `TestAssembleBlocks::test_builds_cached_and_minimal_blocks`, `TestAgentDataHelpers::test_preview_prompt_resolves_blocks`, `TestRunAdhoc`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix \
  tests/component/core/test_agent.py::TestAst820VectorFeedbackDebugTrace::test_do_task_fail_closed_when_candidate_id_missing \
  tests/component/core/test_agent.py::TestPromptHelpers::test_builds_context_and_assembles_blocks \
  tests/component/core/test_agent.py::TestAssembleBlocks::test_builds_cached_and_minimal_blocks \
  tests/component/core/test_agent.py::TestAgentDataHelpers::test_preview_prompt_resolves_blocks \
  tests/component/core/test_agent.py::TestRunAdhoc \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (after publish):** `git show origin/sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix:docs/test-bible/core/agent.md | shasum`

### AST-1992 · AST-1985 (gap — candidate-prefix idempotence; product AST-1990)

**Parent:** [AST-1985](https://linear.app/astralcareermatch/issue/AST-1985) (orphaned mini-parent). **Publish:** `origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests`. **Gap from** `[board-betty] TESTS: REVISE` on **AST-1990** — product fix (`_system_text_with_candidate_prefix` strips any leading `[astral-…]` run, then prepends one `[astral-<cid>]`) is **AST-1990** (`origin/sub/AST-1985/AST-1990-candidate-prefix-dedupe`); this ticket is test tree + bible only.

| Area | Source | Component tests |
| --- | --- | --- |
| Already-prefixed / 5× stacked (AST-1985 sample) collapse to one marker | `src/core/agent.py` | `TestAst1639CandidateIdSystemPrefix::test_helper_already_prefixed_input_keeps_one_marker`, `::test_helper_five_stacked_markers_collapse_to_one` |
| Other-id leading marker replaced by current cid (Susan-approved any-id strip) | same | `::test_helper_other_id_leading_marker_replaced_by_current_cid` |
| Byte-zero run only — leading whitespace / mid-body markers untouched | same | `::test_helper_non_leading_marker_left_in_body` (green pre- and post-fix guard) |
| Fail closed with marker already in body | same | `::test_helper_blank_id_raises_even_when_body_already_prefixed` (green pre- and post-fix guard) |
| AC3 parity on re-fed text (wire + runtime system) | same | `::test_assemble_already_prefixed_system_keeps_one_marker` |

**Broken / obsolete:** none — un-prefixed output unchanged; existing AST-1639 nodes stay green. Monkeypatched helper stubs elsewhere in `test_agent.py` don't assert stacking.

**Integration:** none.

**Sequencing deviation (gap child):** product not on ftr yet. `[bug-repro]` proven both ways — **RED on pre-fix tree** (4 nodes: already-prefixed, 5× stacked, other-id, assemble parity; stacked-marker assertion diffs) and **GREEN with AST-1990 plan `## Proposed change` overlaid** on `src/core/agent.py` (scratch, restored, not committed).

## QA test manifest (AST-1992)

1. `[bug-repro]` nodes (must flip red→green under `test-fix` once AST-1990 lands): `test_helper_already_prefixed_input_keeps_one_marker`, `test_helper_five_stacked_markers_collapse_to_one`, `test_helper_other_id_leading_marker_replaced_by_current_cid`, `test_assemble_already_prefixed_system_keeps_one_marker`
2. Guards + existing AST-1639 suite stay green: full `TestAst1639CandidateIdSystemPrefix`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix \
  -q
```

**Pass criterion:** pytest green on the class (13 nodes) with AST-1990 product merged — not zero-arg harness / branch-lock gate.

**Bible shasum (after publish):** `git show origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests:docs/test-bible/core/agent.md | shasum`

### AST-1679 · AST-1677

**Parent:** [AST-1677](https://linear.app/astralcareermatch/issue/AST-1677). **Publish:** `origin/sub/AST-1677/AST-1679-operative-save-hydrate-blob-retirement`.

`do_task` persist_candidate_craft_hops (inline): when `artifact_key` set, land structure via `candidate.artifacts.resume_structure` then body via catalog key (no library dict-path for structure). Primary candidate: **`docs/test-bible/core/candidate.md`** § AST-1679.

| Area | Source | Component tests |
| --- | --- | --- |
| Craft-persist dual operative keys | `src/core/agent.py` | revised **`TestAst1576CraftPersistOperative`** |
| Source gate (catalog key, no library dict) | same | **`TestAst1679CraftPersistResumeStructureOperative`** |

**Broken / obsolete:** AST-1576 expected a library dict-path save for structure — revised to operative str-path.

**Integration:** none.

## QA test manifest

See **`docs/test-bible/core/candidate.md`** § AST-1679 (shared numbered list).

**Bible shasum (publish tip):**
- `docs/test-bible/core/agent.md` — *(filled after publish)*

### AST-1683 · AST-1681 (Contact-shaped BASE_RESUME current-read — test gap for AST-1682)

**Parent:** [AST-1681](https://linear.app/astralcareermatch/issue/AST-1681). **Sibling product fix:** AST-1682. **Publish:** `origin/sub/AST-1681/AST-1683-cover-contact-base-resume-current-read`.

Board REVISE (copied from AST-1682): Contact-shaped `do_task(index=cid, ctx=None)` / library blob without `_astral_candidate_id` → `{$BASE_RESUME}` current-read not exercised (AST-1587/607/1192 only cover pre-stamped cid or name tokens). Product cid-threading lives on AST-1682; this child lands the repro-first gate only.

| Area | Source | Component tests |
| --- | --- | --- |
| Contact-shaped index=cid, ctx=None → `{$BASE_RESUME}` current-read | `src/core/agent.py` (`_token_view_for_do_task` / `do_task`) | **`TestAst1683ContactBaseResumeCurrentRead::test_do_task_index_cid_ctx_none_resolves_base_resume`** |

**Broken / obsolete:** none — additive repro; AST-1192 name-token suite unchanged.

**Integration:** none.

## QA test manifest (AST-1683)

1. Bug-repro (red pre AST-1682 cid threading; green after): `tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead::test_do_task_index_cid_ctx_none_resolves_base_resume`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead::test_do_task_index_cid_ctx_none_resolves_base_resume \
  -q
```

**Pass criterion:** pytest green on the repro node once AST-1682 make-fix lands — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/agent.md` — *(filled after publish)*

### AST-1698 · AST-1579

**Parent:** [AST-1579 — Capture deduped source-artifact-id array](https://linear.app/astralcareermatch/issue/AST-1579). **Publish:** `origin/sub/AST-1579/AST-1698-prompt-token-source-pin-harvest-helper`.

Prompt-time source-pin harvest: parse `{$TOKEN}` via `_TOKEN_RE` / `TOKEN_SOURCES.source_type == "artifact"`, resolve current `artifact_uuid` per catalog key, dedupe, attach `source_artifact_ids` on `do_task` result. No job_data siblings / save-signature threading (siblings AST-1699 / AST-1700). Config parse: **`docs/test-bible/utils/config.md`** § AST-1698. Candidate UUID helper: **`docs/test-bible/core/candidate.md`** § AST-1698.

| Area | Source | Component tests |
| --- | --- | --- |
| Harvest entry (AC1 dedupe + miss/empty cid) | `src/core/agent.py` | **`TestAst1698HarvestSourceArtifactIds`** |
| `do_task` attaches `source_artifact_ids` | same | **`TestAst1698HarvestSourceArtifactIds::test_do_task_attaches_source_artifact_ids`** |
| Config key parse (no pinnable allowlist) | `src/utils/config.py` | **`TestAst1698ListArtifactKeysInPromptTexts`** |
| Current uuid-by-key | `src/core/candidate.py` | **`TestAst1698GetCandidateCurrentArtifactUuid`** |

**Broken / obsolete this pass:** none — additive helpers; existing TOKEN_SOURCES / get_candidate_current suites unchanged.

**Integration:** none — no existing scenario asserts `source_artifact_ids` / harvest; do not invent.

## QA test manifest

1. Harvest AC1 + miss/empty + non-artifact skip: `tests/component/core/test_agent.py::TestAst1698HarvestSourceArtifactIds`
2. Config parse/dedupe: `tests/component/utils/test_config.py::TestAst1698ListArtifactKeysInPromptTexts`
3. Candidate uuid helper: `tests/component/core/test_candidate.py::TestAst1698GetCandidateCurrentArtifactUuid`
4. AC2 (catalog reuse, no parallel allowlist): `rg -n 'list_artifact_keys_in_prompt_texts|harvest_source_artifact_ids|get_artifact_key_for_token|_TOKEN_RE' src/utils/config.py src/core/agent.py` — expect helpers; fail if a new frozenset/tuple of pinnable token names appears beside harvest.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1698HarvestSourceArtifactIds \
  tests/component/utils/test_config.py::TestAst1698ListArtifactKeysInPromptTexts \
  tests/component/core/test_candidate.py::TestAst1698GetCandidateCurrentArtifactUuid \
  -q
```

**Pass criterion:** pytest green on manifest lines 1–3 + AC2 grep — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/agent.md` — *(filled after publish)*
- `docs/test-bible/utils/config.md` — *(filled after publish)*
- `docs/test-bible/core/candidate.md` — *(filled after publish)*

### AST-1700 · AST-1579

**Parent:** [AST-1579 — Capture deduped source-artifact-id array](https://linear.app/astralcareermatch/issue/AST-1579). **Publish:** `origin/sub/AST-1579/AST-1700-thread-harvest-generative-artifact-writes`.

Thread AST-1698 harvest into generative lands: `do_task` passes `list(source_artifact_ids)` into non-`job_resume` / all `save_job_artifact` call sites and operative str-path `save_candidate_data` (dict-path structure merge left without sources). Tracker job_resume auto-cite unchanged (no tracker edit). Draft traceability Implementation alignment. Candidate optional sources: **`docs/test-bible/core/candidate.md`** § AST-1700. Existing job_resume ignore: **`docs/test-bible/core/tracker.md`** § AST-1592.

| Area | Source | Component tests |
| --- | --- | --- |
| Craft str-path land passes harvest | `src/core/agent.py` | **`TestAst1700ThreadHarvestGenerativeLands::test_craft_str_path_passes_harvest_not_dict_path`** |
| Cover-letter catalog land passes harvest | same | **`TestAst1700ThreadHarvestGenerativeLands::test_cover_letter_land_passes_harvest`** |
| Job-resume land still passes list (tracker ignores) | same | **`TestAst1700ThreadHarvestGenerativeLands::test_job_resume_land_still_passes_harvest_list`** |
| Candidate str-path optional sources | `src/core/candidate.py` | **`TestAst1700SaveCandidateDataSourceArtifactIds`** |
| Job_resume auto-cite ignore (AC6) | `src/core/tracker.py` | **`TestAst1592TrackerCatalogWriteReadCitation`** (existing) |

**Broken / obsolete this pass:** none — kwargs additive; AST-1603 / AST-1576 spies still match on positional args.

**Integration:** none — no existing scenario asserts generative `source_artifact_ids` pass-through; do not invent.

## QA test manifest

1. Agent generative lands: `tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands`
2. Candidate optional sources: `tests/component/core/test_candidate.py::TestAst1700SaveCandidateDataSourceArtifactIds`
3. AC6 existing tracker auto-cite: `tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation::test_job_resume_cites_current_base_resume_uuid` · `test_job_resume_empty_sources_when_no_base_resume` · `test_cover_letter_passes_caller_sources`
4. AC7 docs-acceptance (draft stays draft + Implementation names AST-1698/AST-1700): `rg -n 'AST-1698|AST-1700|status:' canon/directives/draft/patt.artifact.traceability.md` — expect Implementation harvest/land wording; file remains under `draft/`; no agent/task lineage columns as live product.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands \
  tests/component/core/test_candidate.py::TestAst1700SaveCandidateDataSourceArtifactIds \
  tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation::test_job_resume_cites_current_base_resume_uuid \
  tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation::test_job_resume_empty_sources_when_no_base_resume \
  tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation::test_cover_letter_passes_caller_sources \
  -q
```

**Pass criterion:** pytest green on lines 1–3 + AC7 grep — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**
- `docs/test-bible/core/agent.md` — *(filled after publish)*
- `docs/test-bible/core/candidate.md` — *(filled after publish)*

### AST-1846 · AST-1828 (bug-repro — `agent_failure` flag on rubric envelope failure)

**Primary manifest:** **`docs/test-bible/core/roster.md`** § AST-1846. AST-1839: `do_task` on a rubric-encoded task whose envelope reports `agent_performance.status == "failure"` returns `{"success": False, "agent_failure": True, "error": "Agent failure: <note>"}` so prefilter can route the envelope first strike to WFR.

| Area | Source | Component tests |
| --- | --- | --- |
| Envelope failure sets `agent_failure` | `src/core/agent.py` (`do_task`) | **`TestAst1846DoTaskAgentFailureFlag::test_rubric_envelope_failure_sets_agent_failure`** (**bug-repro**) |
| Note fallback: top-level `failure_note` → default text | same | **`…::test_failure_note_fallbacks`** (branch lock, 2 params) |
| Response-block store exception swallowed | same | **`…::test_failure_response_store_exception_is_swallowed`** (branch lock) |
| Non-rubric task never sets the flag | same | **`…::test_non_rubric_task_does_not_set_agent_failure`** (guard — green at base and tip) |

**Integration:** none.

### AST-1879 · AST-1851 (route agent calls by model → server)

`do_task` resolves the agent row's `model_id` + `brain_setting` through `resolve_model_brain` (server, SKU, tier). It sends **only** the candidate's key for that server: `ctx["candidate_api_keys"]` when present, otherwise the map loaded by candidate id. There is no env key and no other platform's key. Dispatch goes by server `protocol` (`send_to_anthropic` vs `send_to_llm_compat`). With no key for the server, the call returns a failure envelope naming the server, sends no request and writes no prompt rows. The conversational brain override is gone. `run_adhoc` / `run_adhoc_workbench_test` take `server_id` / `tier` / `candidate_api_keys`. Pointers: dispatcher key gate ([`dispatcher.md`](dispatcher.md)), Estelle turn ctx ([`contact.md`](contact.md)), classify hand-off ([`meteorite.md`](meteorite.md)).

| Area | Source | Component tests |
| --- | --- | --- |
| New — `_candidate_server_key` (ctx map wins; DB load by id; explicit `{}` honoured; blank/no id → None) | `src/core/agent.py` | `test_agent_ast1879.py::TestAst1879CandidateServerKey` |
| New — `_agent_llm_route`, `task_llm_server_id`, `_missing_server_key_result` | same | `…::TestAst1879RouteHelpers` |
| AST-1944 — `task_llm_server_id_or_none`: `telescope` / empty / blank `agent_id` / no row → `None`; LLM row → catalog server; unknown real agent and real agent without `model_id` re-raise; `stage_email_meteorite` mailbox fold resolves the legacy `parse_meteorite_email` agent's server, and returns `None` when there is no legacy agent. Data layer patched (`get_agent_task` / `get_agent`); strict `_resolve_task_prompts` runs for real | same | `…::TestAst1944TaskLlmServerIdOrNone` (9; AST-1945) |
| New — `_send_to_server` protocol dispatch (anthropic SKU + override key; compat server/SKU/tier/key; `record_timesheet_entry`) | same | `…::TestAst1879SendToServer` |
| AC 7 — right key, no fallback (intercept at `llm_compat._get_client` / `anthropic.Anthropic`; env key never used; four missing-key cases name the server, zero client calls, no prompt storage, warning line) | `do_task` | `…::TestAst1879RightKeyNoFallback` |
| AC 8 — Kimi-routed Estelle task writes a catalog-priced `agent_timesheets` row | `do_task` → `send_to_llm_compat` → `record_timesheet_entry` | `…::TestAst1879KimiLedgerRow` |
| AC 9 / 10 — contact turn at `contact_recruiter_estelle` seed model + brain on the candidate's kimi key; `agent.py` free of `default_brain_setting` / legacy provider symbols | `do_task` | `…::TestAst1879EstelleTurnRoute` |
| AC 7 — `run_adhoc` routes by server; missing key → failure naming server, no request | `run_adhoc` | `test_agent.py::TestRunAdhoc` (revised + 3 new) |
| Workbench wrapper forwards route + key map | `run_adhoc_workbench_test` | `test_agent.py::TestAst515AdhocWorkbenchLedger::test_forwards_server_route_and_key_map_to_run_adhoc` |
| Revised — catalog route replaces `get_active_llm_provider` / `send_to_deepseek` / `resolve_brain_setting_to_*` stubs | `do_task` | `test_agent.py::TestAst492BrainSettingDoTask` (DeepSeek-tier test → compat route; unknown-provider / vendor-model tests → parametrized broken-model-config raise), `TestAst1380…` (Big thinking cases on Kimi Big — catalog DeepSeek Big is thinking-off), `TestAst1391DeepseekBigOutputFloor` (floor from tier `max_tokens_floor`), `TestAst1072ConversationalEnvelope::test_do_task_concern_preserves_outcome_at_agent_rows_own_brain` (AC 9: no Medium override), `TestAst1639…`, `TestAst1846…`, `TestAst1298…`, `TestDoTask::test_rejects_unknown_or_misconfigured_tasks` (model_id checked first) |
| Revised — fixtures | `test_agent.py` | `_agent_rows(model_id="claude")`; autouse `_candidate_server_key_stub` (this file tests past the gate; key selection lives in `test_agent_ast1879.py`); `test_agent_ast1448.py` `_patch_prompts` stubs the key, bare `run_adhoc` passes a route |
| Retired | — | `test_send_to_deepseek_receives_vendor_model_and_tier_meta`, `test_do_task_deepseek_raises_when_vendor_model_not_in_pricing`, `test_do_task_raises_on_unknown_llm_provider`, `TestRunAdhoc::test_with_tier_meta_sends_via_deepseek`, `test_non_craft_deepseek_big_keeps_thinking`, `test_do_task_concern_preserves_outcome_and_uses_medium_brain`: each is replaced by the catalog-route case named above |

**AC 8 gap (flagged to Susan):** `agent_timesheets` has **no `provider` column**. The server id is only `_add_timesheet_entry`'s `provider` argument (SKU-on-server validation, plus the `anthropic_timesheets` mirror switch). So the test asserts: insert called with `provider="kimi"`, SKU `kimi-k2.6` (priced only on `kimi`), token columns, the per-type catalog cost sum, and no anthropic mirror. It cannot assert a stored provider. Adding a column is `database.py`, which is outside AST-1879's scope.

**Handed to #4 (AST-1880):** `tests/component/core/conftest.py` `_core_default_anthropic_llm_provider` patches `cfg.get_active_llm_provider` without `raising=False`. That breaks when #4 deletes the symbol. Its agent-module loop is now a no-op (`hasattr` guard).

**Integration:** none.

## QA test manifest (AST-1879)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast1879.py \
  tests/component/core/test_agent.py::TestDoTask::test_rejects_unknown_or_misconfigured_tasks \
  tests/component/core/test_agent.py::TestDoTask::test_returns_api_failure_and_stores_agent_data \
  tests/component/core/test_agent.py::TestDoTask::test_do_task_stores_agent_data_for_craft_null_entity_type \
  tests/component/core/test_agent.py::TestDoTask::test_decodes_top_level_json_string_encoded_payload \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object \
  tests/component/core/test_agent.py::TestDoTask::test_chains_run_next_when_configured \
  tests/component/core/test_agent.py::TestDoTask::test_chain_entry_log \
  tests/component/core/test_agent.py::TestDoTask::test_hop_boundary_log_on_run_next \
  tests/component/core/test_agent.py::TestDoTask::test_debug_flag_passed_to_child \
  tests/component/core/test_agent.py::TestDoTask::test_ignores_invalid_run_next \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/core/test_agent.py::TestRunAdhoc \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1190DoTaskEmptyProviderError \
  tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor \
  tests/component/core/test_agent.py::TestAst1380CraftRubricThinkingOffAndFailureBanner \
  tests/component/core/test_agent.py::TestAst1072ConversationalEnvelope \
  tests/component/core/test_agent.py::TestAst1576CraftPersistOperative \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_skips_hydrate_when_live_caller \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_hydrate_hard_fails_without_live_caller \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_reinjects_caller_on_recurse \
  tests/component/core/test_agent.py::TestAst1391DeepseekBigOutputFloor \
  tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix \
  tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead \
  tests/component/core/test_agent.py::TestAst1698HarvestSourceArtifactIds \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands::test_cover_letter_land_passes_harvest \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands::test_job_resume_land_still_passes_harvest_list \
  tests/component/core/test_agent.py::TestAst1846DoTaskAgentFailureFlag \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_stores_prompt_before_provider_and_response_after \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_provider_raise_keeps_prompt_omits_response \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_storage_off_skips_prompt_and_response \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_prompt_persist_failure_still_calls_provider \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_debug_false_skips_persist_contract_lines \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_later_success_does_not_rewrite_interrupted_batch_prompts \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_workbench_stores_prompt_before_run_adhoc \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_workbench_raise_keeps_prompt_omits_response \
  tests/component/core/test_dispatcher.py::TestDispatchOne \
  tests/component/core/test_dispatcher.py::TestAst1847TimeoutPartialCounts \
  tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage \
  tests/component/core/test_dispatcher.py::TestAst1829ScheduledSweep \
  tests/component/core/test_contact.py::TestAst1879EstelleTurnCandidateCtx \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_listen_off_skips_do_task \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_success_posts_prefixed_reply \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_failure_does_not_post \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_skill_calls_run_for_resolved_candidate \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_handle_slack_event_attaches_estelle_turn \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  tests/component/core/test_contact.py::TestAst1561ContactPasteRouting \
  tests/component/core/test_contact.py::TestAst1585ContactPinnedBaseResume \
  tests/component/core/test_meteorite.py::TestAst1879ClassifyKeyMapHandOff \
  -q
```

**Pass criterion:** narrowed run green (169 passed), not the zero-arg harness. Every new `test_agent_ast1879.py` node is red on the `origin/ftr/AST-1851-support-openrouter-api-models` product (22/22). The full `tests/component` failure set on this tip has zero new entries against the same tree with `ftr` product (153 moved nodes back to green). Pre-existing reds in touched classes are left out of the manifest: `TestDoTask::{test_rejects_json_schema_and_confidence_failures, test_rejects_grade_vector_mismatch, test_decodes_encoded_payload_and_stores_success, test_returns_decode_and_post_decode_validation_errors, test_mid_chain_empty_caller_skips_api}`, `TestAst1264…::test_do_task_source_has_caller_reinject_and_hydrate_gates`, `TestAst1700…::test_craft_str_path_passes_harvest_not_dict_path`, `TestAst1448…::{test_do_task_debug_emits_prompt_found_recorded_before_provider, test_prompt_only_batch_is_not_latest_ref, test_bare_run_adhoc_does_not_store_agent_data}`, `TestAst841DispatchTerminalLogging` (2), `TestAst1073…::{test_concern_posts_and_logs_aside, test_debug_style_d_index_and_detail}`. LOCKED_AT_100: no line changed by AST-1879 in `agent.py` / `dispatcher.py` is uncovered.

> **AST-1948:** The manifest above calls `resolve_model_brain` with two arguments and puts `temperature` on agent rows. Both are gone (§ AST-1948 below). Do not re-run it as written.

### AST-1948 · AST-1946 (agent mode persisted and applied; temperature and model_code retired from the agent row)

The agent row now carries `mode` (`Deterministic` | `Creative`), and the mode decides thinking and temperature. `_agent_llm_route` passes the row's mode into `resolve_model_brain`. A blank or missing mode raises `Agent '<id>' has no mode configured.`, and an unknown mode raises `Invalid mode '<x>'`. There is no fallback. `do_task` sends `temperature = tier["temperature"]` (0.2 / 0.6 from `AGENT_MODE_CONFIG`). The row has no `temperature` or `model_code` column any more. Data layer: [`../data/database/agents.md`](../data/database/agents.md) § AST-1948. Admin routes: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1948. Repo JSON: [`repo_admin_json.md`](repo_admin_json.md) § AST-1948. Catalog / resolver: [`../utils/config.md`](../utils/config.md) § AST-1947.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 5 wire cases through `do_task`, with `send_to_llm_compat` / `send_to_anthropic` stubbed. The six compat cases (glm-4.6 Little Creative / Deterministic, phi-4 Big Creative, kimi-k2.6 Little Creative / Big Deterministic, deepseek-v4 Big Creative) check server, SKU, the `temperature` kwarg, `tier.thinking` / `thinking_params`, and the deepseek Big `max_tokens` floor of at least 384000. The Anthropic case is claude Medium Deterministic → `claude-sonnet-4-6` at 0.2 | `src/core/agent.py` (`_agent_llm_route`, `do_task`) | `test_agent.py::TestAst1948ModeOnTheWire` (7) |
| New — mode-less (`None` / `""` / `"  "`) and unknown-mode routes raise | `_agent_llm_route` | `test_agent_ast1879.py::TestAst1879RouteHelpers::test_agent_llm_route_raises_without_mode` (3) · `::test_agent_llm_route_rejects_unknown_mode` |
| New — broken-config raise also covers `mode: None` and `mode: "Wild"`, with no client call | `do_task` | `test_agent.py::TestAst492BrainSettingDoTask::test_do_task_raises_on_broken_agent_model_config` (+2 params) |
| Revised — fixtures carry `mode` and drop `temperature`. Resolver calls take a mode: Deterministic by default, and Creative where the old case was a Kimi Big thinking case | `test_agent.py` `_agent_rows(mode=…)`, `_DEEPSEEK_BIG_FLOOR`; `test_agent_ast1879.py` `_seeded_rows`, `_REAL`; `test_agent_ast1448.py` | `TestAst1380CraftRubricThinkingOffAndFailureBanner` (Kimi Big Creative), `TestAst1072ConversationalEnvelope`, `TestAst1391DeepseekBigOutputFloor`, `TestAst1879…` |
| Revised — `kimi-k2.6-openrouter` → `moonshotai/kimi-k2.6` (retired by AST-1947) | `test_agent_ast1879.py` | `TestAst1879SendToServer` compat parametrize · `TestAst1879RightKeyNoFallback` missing-key param |
| Revised — the Estelle turn routes with the seed row's mode (Deterministic) and sends the tier temperature 0.2 | `do_task` | `TestAst1879EstelleTurnRoute` |

**Broken / obsolete:** none retired. Every test that broke was repaired in place.

**Pre-existing test-order leak (not AST-1948, flagged):** if `test_agent_ast1879.py` runs before `TestDoTask` run-next / `TestAst1264…` nodes in one session, those fail with `no such table: agent_timesheets`. The same pair fails the same way on pre-epic `ae494c618`. The manifest below runs `test_agent_ast1879.py` last. The fixture fix is a separate ticket.

**Integration:** none (no `tests/integration/` scenario reads the agent row's mode or temperature).

## QA test manifest (AST-1948)

1. **Component (narrowed — must be all green, run in this order):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestDoTask::test_rejects_unknown_or_misconfigured_tasks \
  tests/component/core/test_agent.py::TestDoTask::test_returns_api_failure_and_stores_agent_data \
  tests/component/core/test_agent.py::TestDoTask::test_do_task_stores_agent_data_for_craft_null_entity_type \
  tests/component/core/test_agent.py::TestDoTask::test_decodes_top_level_json_string_encoded_payload \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object \
  tests/component/core/test_agent.py::TestDoTask::test_chains_run_next_when_configured \
  tests/component/core/test_agent.py::TestDoTask::test_chain_entry_log \
  tests/component/core/test_agent.py::TestDoTask::test_hop_boundary_log_on_run_next \
  tests/component/core/test_agent.py::TestDoTask::test_debug_flag_passed_to_child \
  tests/component/core/test_agent.py::TestDoTask::test_ignores_invalid_run_next \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/core/test_agent.py::TestRunAdhoc \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1190DoTaskEmptyProviderError \
  tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor \
  tests/component/core/test_agent.py::TestAst1380CraftRubricThinkingOffAndFailureBanner \
  tests/component/core/test_agent.py::TestAst1072ConversationalEnvelope \
  tests/component/core/test_agent.py::TestAst1576CraftPersistOperative \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_skips_hydrate_when_live_caller \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_hydrate_hard_fails_without_live_caller \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_reinjects_caller_on_recurse \
  tests/component/core/test_agent.py::TestAst1391DeepseekBigOutputFloor \
  tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix \
  tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead \
  tests/component/core/test_agent.py::TestAst1698HarvestSourceArtifactIds \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands::test_cover_letter_land_passes_harvest \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands::test_job_resume_land_still_passes_harvest_list \
  tests/component/core/test_agent.py::TestAst1846DoTaskAgentFailureFlag \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_stores_prompt_before_provider_and_response_after \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_provider_raise_keeps_prompt_omits_response \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_storage_off_skips_prompt_and_response \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_prompt_persist_failure_still_calls_provider \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_debug_false_skips_persist_contract_lines \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_later_success_does_not_rewrite_interrupted_batch_prompts \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_workbench_stores_prompt_before_run_adhoc \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_workbench_raise_keeps_prompt_omits_response \
  tests/component/core/test_agent.py::TestAst1948ModeOnTheWire \
  tests/component/data/database/test_agents.py \
  tests/component/core/test_repo_admin_json.py::TestExportRepoAdminJsonToFiles \
  tests/component/core/test_repo_admin_json.py::TestAst783RepoAdminJsonDivergence \
  tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed::test_repo_rows_use_repo_columns_only \
  tests/component/core/test_repo_admin_json.py::TestAst1878AgentSeedModels \
  tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents \
  tests/component/ui/api/test_api_admin.py::TestEnrichTasks \
  tests/component/ui/api/test_api_admin.py::TestAst1880ResolveAdhocCatalogRoute \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_adhoc_entities_and_resolve \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_resolve_adhoc_candidate_and_preview_errors \
  tests/component/ui/api/test_api_admin.py::TestAst1411AdhocSevenSegment::test_resolve_preview_seven_segment_and_system_fallback \
  tests/component/core/test_agent_ast1879.py \
  -q
```

2. **Whole files (informational — pre-existing reds only):**

```bash
.venv/bin/python -m pytest tests/component/core/test_agent.py tests/component/core/test_agent_ast1448.py \
  tests/component/core/test_agent_ast1879.py tests/component/core/test_repo_admin_json.py \
  tests/component/data/database/test_agents.py tests/component/ui/api/test_api_admin.py -q --tb=line
```

Every failure here must also fail on pre-epic `ae494c618` with this test tree. That baseline covers the 43 core-agent reds, 18 `test_repo_admin_json.py` reds (catalog / fixture lockstep, `TestApplyRepoAdminJsonAtStartup` ×3, `TestAst1400…` craft pins) and 5 `test_api_admin.py` reds. `test_agents.py` is all green. Any other failure is real.

3. **AC 6 / AC 8 greps (all three empty on the publish tip):**

```bash
rg -n "default_temperature|brain_setting_for_anthropic_agent_key|admin_brain_setting_catalog|infer_brain_setting_from_legacy_model_code" src/ --glob '!src/ui/frontend/**'
rg -n "0\.6\b|0\.2\b" src/core/agent.py src/ui/api/api_admin.py src/data/database.py
rg -n "apodex/|bytedance/ui-tars|ibm-granite/|inclusionai/|meta/muse|microsoft/|minimax/|sao10k/l3|thedrummer/|z-ai/glm-4|moonshotai/kimi-k2\.[57]" src/ --glob '!src/utils/config.py'
```

**Pass criterion:** item 1 green (206 passed on the publish tip), item 2 reds limited to the baseline set, item 3 empty. Not the zero-arg harness. **AC 6 is composite on `ftr`** (Joan, validate-plan discuss). Once both subs merge, re-run item 3 plus [`../utils/config.md`](../utils/config.md) § AST-1947 manifest item 1 on `origin/ftr/AST-1946-big-brain-openrouter`. The `temperature` grep on `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` belongs to AST-1949, so leave it out here. Between this merge and AST-1949, an agent edit from the UI returns `400 mode is required`. That is by design (plan Stage 2 decision), not a bug.

> **AST-1956:** `mode` is gone from the agent row, and `TestAst1948ModeOnTheWire` is retired (§ AST-1956 below). Do not re-run the manifest above as written.

### AST-1956 · AST-1953 (send the agent's settings on the wire)

`_agent_llm_route` now calls `resolve_agent_settings(model_id, agent_row)` (AST-1955). The tier carries the row's `temperature`, `reasoning_effort` and the OpenRouter-only `provider` object exactly as stored. There is no mode, no brain size and no thinking-from-tier. The craft-rubric guard sets `tier["reasoning_effort"] = "none"` instead of thinking off. `_send_to_server` passes `reasoning_effort` to `send_to_anthropic`. The `Calling _send_to_server` debug line in `do_task`, and a new one in `run_adhoc` (`task_key=adhoc`), print `temp=%s, effort=%s` with what was actually sent (`temp=None` when the row's temperature is empty). Pre-SKU ids (`claude`, `deepseek-v4`) raise `Unknown LLM model`. Wire bodies: [`../external/llm_compat.md`](../external/llm_compat.md) § AST-1956 · [`../external/anthropic.md`](../external/anthropic.md) § AST-1956. Resolver: [`../utils/config.md`](../utils/config.md) § AST-1955.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 1 / AC 3 through `do_task`, `send_to_llm_compat` stubbed. gpt-oss-120b `bf16` → provider object; phi-4 temperature 0.3 + effort `high` with no gating; kimi-k2.6 effort `none`; deepseek-v4-pro `provider_only` on a direct server → `provider` None | `_agent_llm_route`, `do_task` | `test_agent.py::TestAst1956SettingsOnTheWire::test_compat_call_carries_row_settings` (4) |
| New — Anthropic leg gets the row's temperature and `reasoning_effort` | `_send_to_server` | `::test_anthropic_call_carries_temperature_and_effort` |
| New — AC 4: a 400 "Reasoning is mandatory…" from the compat client is `success: False` with the message in `error` and no `failure_class` | `do_task` → `send_to_llm_compat` | `::test_rejected_setting_is_an_ordinary_failure` |
| New — AC 5: `do_task` debug line shows `temp=` / `effort=` as sent (`temp=None` when empty) | `do_task` | `::test_debug_line_shows_what_was_sent` (2) |
| New — AC 5: `run_adhoc` forwards effort and logs the same line with `task_key=adhoc` | `run_adhoc` | `::test_run_adhoc_forwards_effort_and_logs_it` |
| New — pre-SKU ids raise | `_agent_llm_route` | `test_agent_ast1879.py::TestAst1879RouteHelpers::test_agent_llm_route_raises_on_pre_sku_model_id` (2) |
| Revised — route resolves catalog + row settings (moonshotai/kimi-k2.6, effort `ultra` passes through, provider `{"quantizations": ["int4"], "allow_fallbacks": false}`) | `_agent_llm_route` | `TestAst1879RouteHelpers::test_agent_llm_route_resolves_catalog` |
| Revised — Anthropic protocol carries effort (None / `high` / `none`) and temperature 0.3 | `_send_to_server` | `TestAst1879SendToServer::test_anthropic_protocol` (3) |
| Revised — Estelle turn sends the seed row's temperature 0.2 and `extra_body == {"thinking": {"type": "disabled"}}` | `do_task` | `TestAst1879EstelleTurnRoute` |
| Revised — craft rubric forces effort `none`; non-craft keeps the stored effort (`high`) | craft guard | `TestAst1380CraftRubricThinkingOffAndFailureBanner::test_craft_get_rubric_forces_effort_none` · `::test_non_craft_keeps_stored_effort` |
| Revised — parent AC 6 wire half: deepseek-v4-pro row `max_tokens: 384000` → sent as 384000; flash sends the row's 100. Catalog floor lifts a low row; a row above the floor wins; Opus keeps the row; craft effort `none` still uses the catalog floor | `do_task` `max_tokens` | `TestAst1391DeepseekBigOutputFloor::test_catalog_floor_lifts_low_agent_row` · `::test_agent_row_above_catalog_floor_wins` · `::test_deepseek_sends_row_max_tokens_as_stored` · `::test_anthropic_opus_keeps_agent_row` · `::test_debug_true_max_tokens_line_shows_floor` · `::test_craft_effort_none_uses_catalog_floor` |
| Revised — Anthropic routing by per-SKU id (claude-opus-4-6); broken-config params are `""`, `__no_such_model__`, `claude`, `deepseek-v4` | `do_task` | `TestAst492BrainSettingDoTask::test_send_to_anthropic_receives_row_per_sku_model` · `::test_do_task_raises_on_broken_agent_model_config` |
| Revised — fixtures carry plain settings (`_agent_rows(model_id=…, **settings)`, `_route(model_id, **settings)`, `_STUB_FLOOR`; ast1879 `_SEED_KEYS`, `_REAL` = deepseek-v4-pro; ast1448 tier from `resolve_agent_settings`). `brain_setting` / `deepseek-v4` / `claude` ids → per-SKU ids | `test_agent.py`, `test_agent_ast1879.py`, `test_agent_ast1448.py` | `TestRunAdhoc`, `TestAst1072ConversationalEnvelope`, concern test, `TestAst1879…` |
| Revised — needle test also forbids `resolve_model_brain` and `brain_setting` in `agent.py` | source scan | `TestAst1879…` needle test |
| Revised — non-LLM gate row uses `model_id: deepseek-v4-pro` (was red on the dev product too; green now) | `dispatcher.py` | `test_dispatcher.py::TestAst1944NonLlmGate::test_llm_key_without_server_key_still_skipped` |

**Broken / obsolete:** `TestAst1948ModeOnTheWire` (7) retired → `TestAst1956SettingsOnTheWire`. `test_agent_ast1879.py::TestAst1879RouteHelpers::test_agent_llm_route_raises_without_mode` (3) and `::test_agent_llm_route_rejects_unknown_mode` retired (no mode). Renamed in place: `test_send_to_anthropic_receives_resolved_key_for_big_tier`, `test_craft_get_rubric_deepseek_big_forces_thinking_false`, `test_non_craft_kimi_big_keeps_thinking`, and the `TestAst1391` deepseek Big / Medium / Little / anthropic-Big floor nodes (the size split no longer exists).

**Pre-existing reds:** whole-file runs of `tests/component/core` + `tests/component/external` on this tip show zero new failures against the same test tree on the `origin/tests` (dev) product. The 40 `test_agent.py` reds, 3 `test_agent_ast1448.py` reds and `test_anthropic.py::TestAst1190…` red are all baseline. `test_candidate.py` `TestAst901…` reds are order-dependent (green alone and at file level).

**LOCKED_AT_100:** `--cov-branch` reports no missing line or partial branch in any AST-1956 hunk of `agent.py`, `anthropic.py` or `llm_compat.py`. Mutants all caught: debug line printing a constant, a truthy temperature check (drops 0.0), the craft guard removed, server extras overriding the agent's `provider`.

**Integration:** none (no `tests/integration/` scenario reads agent settings, effort, temperature or provider).

## QA test manifest (AST-1956)

1. **Component (narrowed — must be all green, run in this order):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestDoTask::test_rejects_unknown_or_misconfigured_tasks \
  tests/component/core/test_agent.py::TestDoTask::test_returns_api_failure_and_stores_agent_data \
  tests/component/core/test_agent.py::TestDoTask::test_do_task_stores_agent_data_for_craft_null_entity_type \
  tests/component/core/test_agent.py::TestDoTask::test_decodes_top_level_json_string_encoded_payload \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object \
  tests/component/core/test_agent.py::TestDoTask::test_chains_run_next_when_configured \
  tests/component/core/test_agent.py::TestDoTask::test_chain_entry_log \
  tests/component/core/test_agent.py::TestDoTask::test_hop_boundary_log_on_run_next \
  tests/component/core/test_agent.py::TestDoTask::test_debug_flag_passed_to_child \
  tests/component/core/test_agent.py::TestDoTask::test_ignores_invalid_run_next \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/core/test_agent.py::TestRunAdhoc \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1190DoTaskEmptyProviderError \
  tests/component/core/test_agent.py::TestAst1298OrphanedJobClaimRelease \
  tests/component/core/test_agent.py::TestAst903CraftRubricMaxTokensFloor \
  tests/component/core/test_agent.py::TestAst1380CraftRubricThinkingOffAndFailureBanner \
  tests/component/core/test_agent.py::TestAst1072ConversationalEnvelope \
  tests/component/core/test_agent.py::TestAst1576CraftPersistOperative \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_skips_hydrate_when_live_caller \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_hydrate_hard_fails_without_live_caller \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession::test_persist_craft_reinjects_caller_on_recurse \
  tests/component/core/test_agent.py::TestAst1391DeepseekBigOutputFloor \
  tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix \
  tests/component/core/test_agent.py::TestAst1683ContactBaseResumeCurrentRead \
  tests/component/core/test_agent.py::TestAst1698HarvestSourceArtifactIds \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands::test_cover_letter_land_passes_harvest \
  tests/component/core/test_agent.py::TestAst1700ThreadHarvestGenerativeLands::test_job_resume_land_still_passes_harvest_list \
  tests/component/core/test_agent.py::TestAst1846DoTaskAgentFailureFlag \
  tests/component/core/test_agent.py::TestAst1956SettingsOnTheWire \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_stores_prompt_before_provider_and_response_after \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_provider_raise_keeps_prompt_omits_response \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_storage_off_skips_prompt_and_response \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_prompt_persist_failure_still_calls_provider \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_debug_false_skips_persist_contract_lines \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_do_task_later_success_does_not_rewrite_interrupted_batch_prompts \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_workbench_stores_prompt_before_run_adhoc \
  tests/component/core/test_agent_ast1448.py::TestAst1448PersistPromptBeforeProvider::test_workbench_raise_keeps_prompt_omits_response \
  tests/component/core/test_dispatcher.py::TestAst1944NonLlmGate \
  tests/component/external/test_llm_compat.py \
  tests/component/external/test_anthropic.py::TestSendToAnthropic \
  tests/component/external/test_anthropic.py::TestAst1956SettingsOnTheWire \
  tests/component/core/test_agent_ast1879.py \
  -q
```

2. **Whole files (informational — pre-existing reds only):**

```bash
.venv/bin/python -m pytest tests/component/core tests/component/external -q --tb=line
```

Every failure here must also fail with this test tree on the `origin/tests` (dev) product. Any other failure is real. `tests/component/ui/api/` is left out: `api_admin.py` still imports `resolve_model_brain` until AST-1957, so it does not collect on this sub alone.

3. **AC 4 / parent AC 5 greps (both empty on the publish tip):**

```bash
rg -n "config_error|configuration_error" src/
rg -n "_openrouter_pin|AGENT_MODE|OPENROUTER_QUANT_BRAIN_SIZE|resolve_model_brain|validate_agent_mode|brain_setting|brain_sizes|can_think|thinking_params" src/core/agent.py src/external/llm_compat.py src/external/anthropic.py
```

**Pass criterion:** item 1 green (185 passed on the publish tip), item 2 reds limited to the baseline set, item 3 empty. Not the zero-arg harness.

### AST-1960 · AST-1954 (served host on the dispatch ledger)

**Primary manifest** (this file). Siblings: [`../data/database/dispatch_ledger.md`](../data/database/dispatch_ledger.md) § AST-1960 (`host` column); AST-1959's `host` on the compat result is [`../external/llm_compat.md`](../external/llm_compat.md) § AST-1959.

After `_send_to_server`, `do_task` writes `host` to the `dispatch_ledger` row for `log_batch_id.get()` (a dispatcher batch, or the hop row `_open_run_next_hop_ledger` set), via `asyncio.to_thread(database.update_dispatch_ledger, id, host=…)`. It writes only when a batch id is set **and** `result["success"]`. The value is `result["host"]`, else `get_llm_server(server_id)["label"]` (Anthropic-direct results carry no host). A raising ledger write is logged (`logger.exception`, "Ledger host write failed for batch …") and the call still succeeds. `TestAst1960LedgerHost` runs on `sqlite_in_memory` with a saved ledger row and stubs both send functions at `agent_mod`. Its `ledger` fixture snapshots the core conftest `_SCHEMA_FLAGS` through `monkeypatch` (`raising=False`) before requesting `sqlite_in_memory`. That fixture sets the flags with plain `setattr` and never restores them, so without the snapshot every later `do_task` test in the run skips schema-ensure against the harness DB and fails "no such table" on a fresh `data/` (24 reds in this manifest on a new worktree).

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 1 OpenRouter-routed success with `host: "DeepInfra"` → `get_dispatch_ledger(id)["host"] == "DeepInfra"` | `do_task` | `TestAst1960LedgerHost::test_ac1_compat_result_host_lands_on_ledger_row` |
| New — AC 1 Anthropic-direct success, no `host` key → row host = `LLM_SERVER_CONFIG["anthropic"]["label"]` (`"Anthropic"`) | `do_task` | `…::test_ac1_anthropic_direct_records_server_label` |
| New — failed call (carries the server label) does not overwrite a host already on the row | `do_task` | `…::test_failed_call_keeps_the_real_host` |
| New — no `log_batch_id` → no ledger write | `do_task` | `…::test_no_batch_id_writes_nothing` |
| New — ledger write raises → call still `success: True`, failure logged | `do_task` | `…::test_ledger_write_failure_never_fails_the_call` |
| Revised — two-hop chain: each hop's host write (`(hop_id, {"host": "Anthropic"})`) lands on its own hop row before that hop's finalize; finalize updates still 2 × `COMPLETED` | `do_task` / hop ledger | `TestAst531RunNextHopLedger::test_two_hop_chain_creates_distinct_ledger_rows` |

**Broken / obsolete:** `TestAst531RunNextHopLedger::test_two_hop_chain_creates_distinct_ledger_rows` (`len(updates) == 2`) — revised above. No other test counts `update_dispatch_ledger` calls.

**Note:** existing `test_agent.py` tests that run a successful `do_task` under the `batch-1` token (no temp DB) now also send the host `UPDATE` to the harness DB (`ASTRAL_DB_DIR`, default `data/`). It matches no row, so nothing changes; left as is.

`LOCKED_AT_100`: `--cov-branch` over `TestAst1960LedgerHost` reports no missing line or partial branch in the AST-1960 hunk of `agent.py`.

**Integration:** none (no `tests/integration/` scenario calls `do_task` or reads the ledger; the conftest only resets `_dispatch_ledger_schema_ensured`).

## QA test manifest (AST-1960)

1. **Component (narrowed — must be all green, 67 on the publish tip):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1960LedgerHost \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/core/test_agent.py::TestAst1846DoTaskAgentFailureFlag \
  tests/component/core/test_agent.py::TestAst1956SettingsOnTheWire \
  tests/component/core/test_agent_ast1879.py \
  tests/component/data/database/test_dispatch_ledger.py \
  -q
```

2. **Whole files (informational — pre-existing reds only):**

```bash
.venv/bin/python -m pytest tests/component/core/test_agent.py tests/component/core/test_dispatcher.py -q --tb=line
```

Expect 40 reds in `test_agent.py` and 12 in `test_dispatcher.py`. Each one fails identically with this test tree on `origin/ftr/AST-1954-host-probe` product (no AST-1960). Causes: resume-section message drift, `KeyError: 'company_id'` / `'jobs'`, `empty agent_payload` wording, and others. Any other failure is real.

3. **Boundary gate (expect no output):** `git diff origin/ftr/AST-1954-host-probe...HEAD --stat -- src/core/dispatcher.py src/external/ src/utils/`

**Pass criterion:** item 1 green, item 2 limited to the baseline reds, item 3 empty. Not the zero-arg harness.

### AST-2001 · AST-1884 (bug-repro — AST-1996 decode-line isolation, agent side)

Test gap for **AST-1996** (`96bc0471d`): `_decode_payload` records grades-only trailing content (a token failing `_GRADE_SEG`, e.g. `DEC35`) in `decode_failures` (`astral_job_id`, `pos`, `reason` — reason text identical to the old `ValueError`) and skips that line; clean lines in the same payload still decode. Key present **only** when a line failed. `_meta` / `_notes` output types keep the tail as meta/notes (never a decode failure). Bad position, duplicate code (**AST-1513**) and the vet branch still raise for the whole payload; an X segment with nonzero confidence is a per-line `decode_failures` entry (since `f8d3f9a12`); a letter with confidence 0 is normalised to 1 (**AST-2053**, see AST-2057). Routing / batch side: **`core/consult.md`** (**AST-2001**).

| Area | Source | Component tests |
| --- | --- | --- |
| Trailing content → `decode_failures` entry, `jobs == []` (flipped from raise; bad-position raise kept; `0|CRX2` → X-branch `decode_failures` entry) | `src/core/agent.py` (`_decode_payload`) | **`TestDecodePayload::test_rejects_bad_positions_and_records_trailing_meta`** (**bug-repro**) |
| Repro A — malformed line 0 isolated, line 1 decodes (`DE/C/3`, `EC/C/3`, `OR/X/0`) | same | **`…::test_ast1996_malformed_line_isolated_clean_line_decodes`** (**bug-repro**) |
| Clean payload has no `decode_failures` key | same | **`…::test_ast1996_clean_payload_has_no_decode_failures_key`** (guard) |
| `grades_encoded_notes` tail stays `notes`, no `decode_failures` | same | **`…::test_ast1996_notes_type_tail_is_not_a_decode_failure`** (guard) |

**Integration:** none.

### AST-2057 · AST-2045 (bug-repro — AST-2053 letter-confidence-0 normalisation)

Test gap for **AST-2053** (`2d1b73da1`): in `_decode_payload`'s non-vet encoded loop, a letter segment with confidence `0` (`{A-F}0`) decodes as the same letter with confidence `1` (no signal) — no `decode_failures` entry. Unchanged: X with nonzero confidence → `decode_failures`; letter confidence 6–9 fails `_GRADE_SEG` → trailing-content `decode_failures`; vet branch (`grades_encoded_vet_meta`) still raises on `LT{letter}0`. Statute: `astral.agent.confidence-bounds`.

| Area | Source | Component tests |
| --- | --- | --- |
| `CFC0`/`SSC0`/`TCC0` line decodes as conf 1, both entities in `jobs`, no `decode_failures` key | `src/core/agent.py` (`_decode_payload`) | **`TestDecodePayload::test_ast2053_letter_conf0_normalised_to_conf1`** (**bug-repro**) |
| `0\|CRA7` trailing failure; `_notes` `CRF0` → `F/1` with notes kept; vet `LTA0` raises | same | **`…::test_ast2053_normalisation_boundaries`** (guard) |
| `0\|CRA0` → `A/1` grade row (flipped from raise) | same | **`TestDecodeAndAuditBranches::test_skips_non_dict_payload_rows_and_invalid_confidence`** |
| `0\|CRX2` → X-branch `decode_failures` entry (flipped from raise) | same | **`TestDecodePayload::test_rejects_bad_positions_and_records_trailing_meta`** |

**Integration:** none.

**QA test manifest (test-fix):**

1. **[bug-repro]** `tests/component/core/test_agent.py::TestDecodePayload::test_ast2053_letter_conf0_normalised_to_conf1`.
2. Decode classes: `pytest tests/component/core/test_agent.py -k "TestDecodePayload or TestDecodeAndAuditBranches"` → **12 passed, 0 failed**.
3. `git diff origin/ftr/AST-2045-letter-conf0-normalize -- src/` empty (test-tree only).

**Red/green record (qa-fix, test-gap sibling — product fix already on ftr):**

- **Red** — pre-fix `src/core/agent.py` from `06df211db` (byte-identical to `055c53c2a`), swapped in temporarily: repro fails `['job-1'] == ['job-0', 'job-1']` (`CFC0` line went to `decode_failures`); `test_ast2053_normalisation_boundaries` fails at `_notes` `CRF0` (`IndexError`, no job row); `0|CRA0` rewrite fails (got `decode_failures` "non-X grade requires confidence 1-5, got 0"). 3 failed / 9 passed across the two decode classes.
- **Green** — ftr tip `3d51b06c7` (AST-2053 `2d1b73da1` merged): 12 passed.
- **Out of scope:** `TestDoTask::test_returns_decode_and_post_decode_validation_errors` is red on **both** trees at its first assert (`'empty agent_payload' in 'Agent failure: nope'` — failure-envelope drift, one of the pre-existing `test_agent.py` reds per AST-2057 Boundaries); its `0|CRX2` assert is never reached.

### AST-2090 · AST-2015 (bug-repro — AST-2089 salvaged_response on rubric envelope failure, agent side)

Test gap for **AST-2089** (`f3897829d`). In `do_task`'s AST-1839 branch (rubric-encoded, envelope `status == "failure"`), when `ctx.batch_entities` is present, the payload goes through the success-path bar (`_normalize_rubric_task_response` → `_coerce_schema_str_fields_from_list` → `_validate_response_schema` → `_validate_grade_confidence_in_payload`). If that yields ≥1 job / company it is returned as `salvaged_response`; otherwise `salvaged_response` is `None`. The failure result is otherwise unchanged (`success False`, `agent_failure True`, `parsed_response None`, `error "Agent failure: <note>"` — **AST-1846** rows above still hold). Consumer: **`core/consult.md`** (**AST-2090**).

| Area | Source | Component tests |
| --- | --- | --- |
| Clean lines salvaged (empty job-ID slot → `company_job_id None`, title/link in place); AST-1846 fields unchanged | `src/core/agent.py` (`do_task`) | **`TestAst2089DoTaskSalvagedResponse::test_envelope_failure_salvages_clean_lines`** (**bug-repro**) |
| Empty / letter-pipe garbage / bad-confidence-only payload → `None` | same | **`…::test_no_salvage_without_a_clean_line`** (guard, 3 params) |
| Schema-invalid decode → `None` | same | **`…::test_no_salvage_when_schema_invalid`** (guard) |
| No `batch_entities` → `None` | same | **`…::test_no_salvage_without_batch_entities`** (guard) |

**Integration:** none.

**Red/green record (qa-fix, test-gap sibling — product fix already on ftr):** red with pre-fix `22ff5e47a` `src/core/agent.py` + `src/core/consult.py` overlaid (scratch worktree) — repro fails `assert None == {'jobs': …}` (no `salvaged_response`); guards pass. Green on ftr tip `e8119b1da`. Run command and consult half: **`core/consult.md`** § AST-2090.

### AST-2006 · AST-2000 (bug — runtime empty-token guard)

**Parent:** [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986) (orphaned mini-parent). **Product:** [AST-2000](https://linear.app/astralcareermatch/issue/AST-2000); canon carve-out [AST-2005](https://linear.app/astralcareermatch/issue/AST-2005) (`patt.task.dispatch-retry`). **Publish:** `origin/sub/AST-1986/AST-2006-empty-token-guard-tests`. `do_task` resolves every segment with an `empty_tokens` collector; any blank recognized token in a segment that is actually sent → no provider call, no hop ledger, one ERROR (`<index> | <task> skipped — empty tokens …`), result carries `empty_tokens` + `empty_token_task` (the failing hop's key on a mid-chain hop). Agent content counts only when a segment references `{$SELECTED_AGENT}`; intake-snapshot-replaced segments are dropped. AST-530 `_mid_chain_empty_caller_tokens` is folded into this guard. Siblings: config collector **`utils/config.md`**, routing **`core/consult.md`** / **`core/roster.md`** / **`core/candidate.md`** / **`core/intake.md`**, probe **`ui/api/api_admin.md`** (all § AST-2006).

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** entry hop blank `{$DEAL_BREAKERS}` → provider not called; `empty_tokens == ["DEAL_BREAKERS"]`, `empty_token_task`; one ERROR; no `resolved to empty` WARNING | `do_task` guard | **`TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent`** |
| Populated prompt → sent once, no `empty_tokens` key | same | **`…::test_populated_prompt_is_sent_without_empty_tokens`** |
| Whitespace-only value is empty | same | **`…::test_whitespace_only_value_counts_as_empty`** |
| `{$SELECTED_AGENT}` rule (no reference → sent; reference → guarded) | same | **`…::test_blank_agent_content_ignored_without_selected_agent_reference`** · **`…::test_blank_agent_content_guarded_when_selected_agent_referenced`** |
| Intake snapshot drops replaced segment (control: no snapshot → guarded) | same | **`…::test_intake_snapshot_replaced_segment_not_guarded`** (2 params) |
| Mid-chain blank `{$CALLER_SYSTEM}` → `empty_tokens`, `empty_token_task` = hop key, one ERROR | same | **`TestDoTask::test_mid_chain_empty_caller_skips_api`** (rewritten in place) |

Fixtures: module helper `_ast2006_guard_ctx` (candidate row with name columns → token view from ctx, no DB); class-local `_rows` / `_ctx` patch `candidate.get_candidate` + `company_search_terms_joined_text` so sent prompts need no DB. Shared `_agent_rows` unchanged (token-free).

**Broken / obsolete:** `TestDoTask::test_mid_chain_empty_caller_skips_api` — pinned AST-530 contract (`"CALLER_SYSTEM" in error`) and was already red on its unstubbed caller hydration (`job not found: job-1`). Rewritten in place: stubs `_hydrate_caller_chain_context` (AST-1264 seam), asserts the AST-2000 result fields + single ERROR.

**Red / green:** `[bug-repro]` red on `origin/dev` `65e23b71b` (provider called with `[astral-cand-1]Deal breakers: `), green on `origin/ftr/AST-1986-runtime-empty-token-error`. 29 of the 39 new/rewritten nodes are red on dev; the 10 dev-green are controls / unchanged behavior. Clean detached worktrees, temp `ASTRAL_DB_DIR`.

**Pre-existing failures (not AST-2006):** hermetic full `tests/component` run on the ftr product: 359 failing nodes without this pass, 357 with it — zero new; fixed = the rewritten mid-chain test plus `TestIntakeSessionFlow::test_background_initiate_failure_writes_assistant_error` (not touched — timing-dependent, not claimed). Five collection errors (`test_meteorite_email.py`, `test_page_intake.py`, `test_surfer.py`, `database/test_meteorites.py`, `database/test_surfer_batches.py`) are pre-existing. Out of scope.

**Integration:** none — no `tests/integration/` scenario exercises `do_task` prompt assembly or empty-token routing.

## QA test manifest — AST-2006

1. **New + rewritten pytest (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst2006DoTaskEmptyTokenGuard \
  tests/component/core/test_agent.py::TestDoTask::test_mid_chain_empty_caller_skips_api \
  tests/component/utils/test_config.py::TestAst2006ResolveTokensEmptyCollector \
  tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts \
  tests/component/core/test_consult.py::TestAst2006EmptyTokenRouting \
  tests/component/core/test_roster.py::TestAst2006EmptyTokenCompanyTerminals \
  tests/component/core/test_candidate.py::TestAst2006RequestedArtifactsEmptyTokens \
  tests/component/core/test_intake.py::TestAst2006IntakeEmptyTokenLedger \
  tests/component/ui/api/test_api_admin.py::TestAst2006EnrichTasksProbeSilent \
  -q
```

2. **[bug-repro] flip:** `tests/component/core/test_agent.py::TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent` — red on `origin/dev`, green on ftr.

### AST-2008 · AST-2007 (do_task ledger call outcome)

Post-call ledger write runs on every call with a batch id: `llm_call_seconds` (timesheet duration) + `llm_failure_class` (NULL on success, `failure_class` or `provider_failed` on failure); `host` still success-only (AST-1960). **Revised:** `TestAst1960LedgerHost::test_ledger_write_failure_never_fails_the_call` (parametrized ok/failed; message names "call outcome"). **New:** `…::test_ast2008_success_writes_duration_and_null_class`, `…::test_ast2008_timeout_writes_outcome_and_keeps_host`, `…::test_ast2008_failed_call_kwargs_carry_no_host`, `…::test_ast2008_last_call_wins_and_unclassified_is_provider_failed` (Decision A). Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-2008.

### AST-2029 · AST-2028 (store agent data with real entity ids)

**Parent:** [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028). **Publish:** `origin/sub/AST-2028/AST-2029-store-agent-data-with-entity-ids`. `do_task` builds `_store_ids` once from `ctx["batch_entities"]` (`company_id` for company tasks, else `astral_job_id`; all-or-nothing, D3) and passes `entity_ids=` to `_store_prompt_blocks` (hydrates the **live** `NO_CACHE` row only, D4) and every `_store_response_block` call (hydrated text is also the hash input). Wire blocks are built from unhydrated text. Helpers: **`utils/formatting.md`** § AST-2029.

| Area | Source | Component tests |
| --- | --- | --- |
| Live NO_CACHE hydrated, prompt-text NO_CACHE not (seven-segment + legacy); no ids → positional | `src/core/agent.py` (`_store_prompt_blocks`) | **`tests/component/core/test_agent_ast2029.py::TestAst2029StorePromptBlocks`** |
| RESPONSE hydrated + id hash over hydrated text; no ids → unchanged | same (`_store_response_block`) | **`…::TestAst2029StoreResponseBlock`** |
| AC1 stored ids / wire positional · AC2 `[index=NNN]` · AC3 failed RESPONSE · company ids · D3 partial/non-dict/empty · success split by id | same (`do_task`) | **`…::TestAst2029DoTaskStoresIds`** |

**Broken / obsolete:** none — existing store fakes take `**kwargs`; no exact-kwarg assertion on the store mocks.

**Red / green:** 26 of 31 new nodes red on `origin/dev` `0e81d63a8`; the 5 dev-green are the no-ids / D3 guards.

**Pre-existing failures (not AST-2029):** `tests/component/core/test_agent.py` + `test_formatting.py` have 45 failing nodes on both `origin/tests` (dev product) and the AST-2029 tip — identical list (resume-section validation text, `KeyError: 'company_id'` / `'jobs'` decode shapes, missing `config.CRAFT_RUBRIC_MAX_TOKENS` / `tracker.persist_advise_job_resume_coded_advice`, token-resolve drift). `test_agent_ast1448.py` has 3 pre-existing reds. Out of scope; manifest is narrowed to the new classes.

**Integration:** none — no `tests/integration/` scenario reads stored `agent_data` block text.

## QA test manifest — AST-2029

1. **New pytest (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast2029.py \
  tests/component/utils/test_formatting.py::TestAst2029HydrateEntityLabels \
  tests/component/utils/test_formatting.py::TestAst2029SplitEntitySegments \
  -q
```

2. **AC4 scope gate:** `git diff origin/dev...origin/sub/AST-2028/AST-2029-store-agent-data-with-entity-ids -- src/ui/api/ src/data/` is empty.

**Pass criterion:** item 1 green, item 2 empty. Not the zero-arg harness (pre-existing reds above).

### AST-2030 · AST-2028 (slice agent-data reads and agent story by entity)

**Parent:** [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028). **Publish:** `origin/sub/AST-2028/AST-2030-slice-agent-data-reads-by-entity`. New `_slice_entity_block(content, entity_id)` over `split_entity_segments` (AST-2029): `{}` → whole block, this id → its segment, other ids only → `None` (D1). `get_agent_data(entity_id=…)` slices `NO_CACHE` / `TASK` / `RESPONSE` and **drops** `None` rows; `SYSTEM` / `CACHE_*` pass through. `get_entity_agent_story` slices `NO_CACHE` / `RESPONSE` for **every** task when the entity has `astral_job_id` / `short_name` (candidates stay whole, D5); `None` → `""` (D2). `_filter_response_block` deleted (D3); `_extract_entity_segment` stays for `get_entity_response`.

| Area | Source | Component tests |
| --- | --- | --- |
| AC4 tagged slice · AC5 chunk-2 rows dropped · AC7 legacy whole · D6 shared prompt whole · CACHE/SYSTEM pass-through · no mutation | `src/core/agent.py` (`get_agent_data`) | **`tests/component/core/test_agent_ast2030.py::TestAst2030GetAgentDataSlice`** |
| AC6 unscored story slice · other chunk `""` · legacy whole · TASK unsliced · company by `short_name` · candidate whole | same (`get_entity_agent_story`) | **`…::TestAst2030AgentStorySlice`** |
| Helper three outcomes (retargeted) | same (`_slice_entity_block`) | **`tests/component/core/test_agent.py::TestSliceEntityBlock`** |

**Broken / obsolete (revised in place):**
- `TestFilterResponseBlock` (both methods) → renamed **`TestSliceEntityBlock`**, retargeted onto `_slice_entity_block`; id-less `jobs[]` now whole, other-id `jobs[]` now `None`.
- `TestAgentDataAccess::test_get_agent_data_keeps_row_when_segment_missing` → **`…_drops_row_when_segment_missing`** (AC5, JSON `jobs[]` shape).
- `TestEntitySegmentAccess::test_get_agent_data_keeps_rows_without_matching_segment` → **`…_drops_rows_without_matching_segment`** (AC5, tagged shape; SYSTEM kept).
- `TestEntityAgentStoryBranches::test_scored_response_without_job_id_keeps_content` → asserts the whole block (AC7 / D4; was `""`).
- AST-1355 table row + run line retargeted to `TestSliceEntityBlock`.

**Red / green:** all 8 revised/new behaviour nodes red on `origin/ftr/AST-2028-…` (pre-AST-2030); 9 guards green there.

**Pre-existing failures:** same 45 as § AST-2029 — unchanged by this ticket (failure list identical after revision).

**Integration:** none — no `tests/integration/` scenario calls `/api/agent_data` or the agent story.

## QA test manifest — AST-2030

1. **New + revised pytest (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast2030.py \
  tests/component/core/test_agent.py::TestSliceEntityBlock \
  tests/component/core/test_agent.py::TestAgentDataAccess \
  tests/component/core/test_agent.py::TestEntitySegmentAccess \
  tests/component/core/test_agent.py::TestEntityAgentStoryBranches \
  tests/component/core/test_agent_ast2029.py \
  -q
```

2. **AC8 scope gate:** `git diff origin/dev...origin/sub/AST-2028/AST-2030-slice-agent-data-reads-by-entity -- src/ui/api/ src/data/` is empty.
3. **Deleted helper gone:** `rg -n "_filter_response_block" src/ tests/` → no matches.

**Pass criterion:** item 1 green, items 2–3 empty. Not the zero-arg harness (pre-existing reds).

### AST-2052 · AST-2028 (bug — job run modal reads like one Each-mode call)

**Parent:** [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028). **Publish:** `origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout`. Plan: `docs/features/agent/ast-2030-slice-agent-data-reads-and-agent-story-by-entity.md` § Bug: AST-2052. `get_agent_data(entity_id=X)` returns live `NO_CACHE` / `RESPONSE` as an Each-mode call for X would have stored them (JSON `companies[]` / `jobs[]` filtered to X's item, compact `json.dumps`; tagged text = preamble before the first `[entity_id=` + X's segment) and omits blank rows. Story keeps the bare slice.

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** plan Repro fixture → envelope + preamble kept, blank `CACHE_C` omitted | `src/core/agent.py` (`get_agent_data`, `_entity_call_view`) | **`tests/component/core/test_agent_ast2052.py::TestAst2052EntityCallView::test_bug_repro_entity_read_is_one_each_mode_call`** |
| D2-2052 non-last entity keeps opener, not closing `"}` · `companies[]` with numeric id · blank rows (`None` / whitespace) omitted | same | **`…::TestAst2052EntityCallView`** (other three nodes) |
| Still holds: AC5 other chunk dropped + AC7 legacy whole · batch view byte-identical · story bare slice | same | **`…::TestAst2052StillHolds`** (green pre- and post-fix) |

**Broken / obsolete (rewritten):** `test_agent_ast2030.py::TestAst2030GetAgentDataSlice::test_ac4_ac5_ac7_entity_read` pinned a blank `TASK` row as `("TASK", "")`; the blank fixture row and its expectation are removed, so the test stays a pure AC4/AC5/AC7 check (blank-row omission lives in the AST-2052 class).

**Red / green:** 4 `TestAst2052EntityCallView` nodes red on the pre-fix tree (`135df3dee`) for the plan's root cause (bare segment / blank rows kept); `TestAst2052StillHolds` + rewritten AST-2030 test green there. All 22 nodes in item 1 green against the plan's Proposed change applied in a throwaway tree (not committed — `test-fix` confirms on the real fix).

## QA test manifest — AST-2052

1. **Repro + guards (required):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent_ast2052.py \
  tests/component/core/test_agent_ast2030.py \
  tests/component/core/test_agent.py::TestAgentDataAccess \
  tests/component/core/test_agent.py::TestEntitySegmentAccess \
  tests/component/core/test_agent.py::TestSliceEntityBlock \
  -q
```

2. **[bug-repro] flip:** `tests/component/core/test_agent_ast2052.py::TestAst2052EntityCallView::test_bug_repro_entity_read_is_one_each_mode_call` — red pre-fix, green after `make-fix`.
3. **Scope gate:** `git diff origin/dev...origin/sub/AST-2028/AST-2052-run-modal-each-mode-layout -- src/ui/api/ src/data/ src/ui/frontend/ src/utils/` shows no AST-2052 product change.
