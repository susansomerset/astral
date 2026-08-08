# Tracker

**Test module:** `tests/component/core/test_tracker.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/tracker.py` | `tests/component/core/test_tracker.py` | yes |

---

### AST-419 · AST-379 (historical — SUNSET AST-757)

**RETIRED (AST-757):** Board-sourced qualify/evaluate pipeline removed with boards channel. No active manifest. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

---

### AST-595 · AST-596 · AST-597 · AST-593

**AST-593 (parent):** Mid-chain artifact resume — replace flat **`BUILD_ARTIFACTS`** with compound **`BUILD_ARTIFACTS.<task_key>`** per resume hop; explicit **`hop_task_keys`** order in **`BUILD_CONFIG`**; **Generate Artifacts** / **approve_artifacts** → first compound state (**`BUILD_ARTIFACTS.anticipate_scan`** v1). Per-hop success transitions (**AST-597**) and **`agent_data`** caller hydration are siblings — manifest rows below split registry/entry, claim/release, and transition/hydration.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-595** | Compound **`JOB_STATES`** + helpers; **`RECOMMENDED_JOB_STATES`** / UI manifest; dispatch **`trigger_state`** per hop; generate/cancel/approve entry | `src/utils/config.py`, `src/core/tracker.py`, `src/ui/api/api_jobs.py` | `tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates`; `tests/component/utils/test_config.py::TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like`; `tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged`; `tests/component/utils/test_config.py::TestBuildStateUiManifest::{test_ast522_recommended_manifest_sections_and_phase_columns,test_ast562_recommended_primary_actions_by_state,test_ast562_recommended_prior_states_allow_cancel_from_build}`; `tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort`; `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::{test_start_artifact_build_from_recommended,test_cancel_from_mid_hop_compound_state,test_cancel_rejects_wrong_state}`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::{test_list_recommended_and_default,test_approve_artifacts_from_recommended,test_approve_artifacts_wrong_state_returns_409,test_approve_artifacts_missing_job_returns_404}`; `tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::{test_generate_artifacts_happy_path,test_cancel_artifact_build_happy_path,test_cancel_artifact_build_409_wrong_state}` |
| **AST-596** | Mid-chain dispatch claim: resume hop **`task_key`** must match compound **`trigger_state`**; hop failure **`release_job_dispatch_claim`** (no **`BUILD_FAILED`**, no resume wipe) | `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/tracker.py` | `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::{test_routes_build_artifacts_to_artifact_entry_batch,test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job,test_artifact_entry_batch_errors_skip_cover_letter,test_artifact_entry_batch_empty_persist_releases_claim}`; `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty::{test_anticipate_scan_entry_skips_contemplate_job_and_cover_letter,test_build_artifacts_state_does_not_imply_contemplate_job_without_dispatch_key,test_mid_chain_compound_trigger_claims_matching_entry,test_dispatch_row_mismatch_skips_artifact_entry}`; `tests/component/core/test_consult.py::TestAst596MidChainDispatchClaimRelease::test_release_job_dispatch_claim_delegates_to_database`; `tests/component/core/test_dispatcher.py::TestRunUnified::{test_ast534_forwards_dispatch_task_key_to_consult,test_ast596_resume_hop_mismatch_skips_claim}` |
| **AST-597** | Per-hop **`BUILD_ARTIFACTS.<task_key>`** transition after successful resume hop; mid-chain entry hydrates **`{$CALLER_*}`** from stored **`agent_data`** (no upstream LLM re-run); Style D **`caller_source`** debug on resume hops | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job` (terminal **`CANDIDATE_REVIEW`** regression) |

**AST-595** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates \
  tests/component/utils/test_config.py::TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like \
  tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_primary_actions_by_state \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_prior_states_allow_cancel_from_build \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_start_artifact_build_from_recommended \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_from_mid_hop_compound_state \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_rejects_wrong_state \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404 \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_generate_artifacts_happy_path \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_happy_path \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_409_wrong_state
```

**AST-596** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst596MidChainDispatchClaimRelease \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast596_resume_hop_mismatch_skips_claim
```

**AST-597** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job
```

---

### AST-732 · AST-728

**`ingest_jobs`** and **`ingest_board_listings`** increment **`duplicates`** (not **`new`**) when **`database.save_job`** returns **`False`** on identity duplicate insert bounce. Pre-insert listing dedup unchanged. Facade **`tracker.save_job`** passthrough bool.

| Area | Source | Component tests |
| --- | --- | --- |
| Ingest count wiring | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestIngestJobs::test_counts_identity_duplicate_bounce_from_save_job`, `TestIngestBoardListings::test_counts_identity_duplicate_bounce_from_save_job` |

See **`docs/test-bible/data/database/jobs.md`** for index + **`save_job`** bounce tests.

### AST-733 · AST-728

**`initialize_job`** returns **`False`** when another row already owns the complete **`(company, job_title, company_job_id)`** triple — current row deleted, canonical row untouched. Incomplete triples skip collision check. IntegrityError fallback deletes current row when **AST-732** index catches a race.

| Area | Source | Component tests |
| --- | --- | --- |
| Collision delete + bool return | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestAst733InitializeJobCollision` |

**AST-733** narrowed run (tracker slice):

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_tracker.py::TestAst733InitializeJobCollision \
  tests/component/core/test_tracker.py::TestInitializeJob \
  -q
```

---

### AST-848 · AST-847

**Runtime dispatch hop labels** — **`write_job_dispatch_hop_label`** writes **`{trigger}.{task_key}`** to **`job.state`** without **`JOB_STATES`** registry validation; **`graduate_job_from_dispatch_chain`** transitions to config successor when predecessor is bare trigger, runtime hop label, or legacy compound hop.

| Area | Source | Component tests |
| --- | --- | --- |
| Hop label write | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestAst848DispatchChainTracker::test_write_job_dispatch_hop_label` |
| Chain graduation | `src/core/tracker.py` | `::test_graduate_from_runtime_hop_label`, `::test_graduate_rejects_unrelated_from_state` |

Primary manifest: **`docs/test-bible/core/agent.md`** AST-848.

---

### AST-765 · AST-757 (SUNSET — documentation)

**RETIRED (AST-757):** Boards channel removed from product (**AST-765**) and schema (**AST-766**). No active boards manifest obligations. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.

---

### AST-828 · AST-752 (UAT bug)

**`get_new_job_batch`** accepts legacy compound holding states **`BUILD_ARTIFACTS.<hop>`** at claim validation only — **`is_valid_job_batch_claim_state`** in config; **`transition_job_state`** still uses flat **`JOB_STATES`** registry. Fixes **`draft_cover_letter`** dispatch rows targeting **`BUILD_ARTIFACTS.finalize_job_resume`** without **`ValueError`** before claim.

| Area | Source | Component tests |
| --- | --- | --- |
| Claim-state helper | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst828JobBatchClaimStateValidation` |
| Batch claim API | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestBatchApi::{test_compound_build_artifacts_hop_claimable_without_value_error,test_invalid_compound_suffix_still_rejects,test_states_list_accepts_legacy_compound_hop}` |

**AST-828** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_config.py::TestAst828JobBatchClaimStateValidation \
  tests/component/core/test_tracker.py::TestBatchApi::test_compound_build_artifacts_hop_claimable_without_value_error \
  tests/component/core/test_tracker.py::TestBatchApi::test_invalid_compound_suffix_still_rejects \
  tests/component/core/test_tracker.py::TestBatchApi::test_states_list_accepts_legacy_compound_hop \
  -q
```


---

### AST-997 · AST-994

**AST-997:** Tracker `_resume_payload_body` / match / persist gates treat non-empty experience job arrays as body content (alongside strings). Primary pin/validate coverage: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Persist + match gates for job arrays | `src/core/tracker.py` | **`TestAst997ExperienceJobArrayPersist`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst997ExperienceJobArrayPersist \
  -q
```

---

### AST-1270 · AST-1268

**Parent:** [AST-1268 — draft_job_resume response schema is wrong](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong). **Publish:** `origin/sub/AST-1268/AST-1270-nested-draft-job-resume-contract`.

`_resume_payload_body` prefers nested **`agent_payload.resume`** when present so envelope keys (`deviations`, nest key) never appear as section content. Primary normalize/validate/prompt coverage: **`docs/test-bible/core/candidate.md`** § AST-1270.

| Area | Source | Component tests |
| --- | --- | --- |
| Nested body prefer + deviations excluded | `src/core/tracker.py` | **`TestAst1270NestedResumePayloadBody`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1270NestedResumePayloadBody \
  -q
```

---

### AST-1099 · AST-1091

**Parent:** [AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1099-pin-agent-data-id`.

`pin_job_artifact_agent_data_id` merges a non-empty RESPONSE `agent_data_id` into `job_data.artifacts[<slot>]` (pointer only). Blank/missing id or job/key skips write (coat-check). Style D `artifact_pin … recorded|skipped` when `debug=True`. Cancel clear removes pin slots via `JOB_BUILD_ARTIFACT_CLEAR_KEYS`.

| Area | Source | Component tests |
| --- | --- | --- |
| Pin helper + never-store-empty + debug | `src/core/tracker.py` | **`TestAst1099PinJobArtifactAgentDataId`** |
| Cancel clears pin slots | `src/core/tracker.py` | **`TestAst1099PinJobArtifactAgentDataId::test_clear_job_build_artifacts_removes_pin_slots`** |

**Broken / obsolete:** none — `persist_job_artifact_from_parsed` remains for manual/API callers; `do_task` no longer body-copies finalize hops (see **`docs/test-bible/core/agent.md`**).

**Integration:** none — do not invent new integration coverage (JAR resolve = AST-1100).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1099PinJobArtifactAgentDataId \
  -q
```


---

### AST-1100 · AST-1091

**Parent:** [AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

`resolve_job_artifact_agent_data_body` loads RESPONSE `block_data` by pin id (coat-check empty/missing). `hydrate_job_artifacts_for_display` shallow-copies artifacts and replaces pin-slot strings with resolved bodies (no `save_job_data`). Pin write = **AST-1099**.

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve + hydrate overlay | `src/core/tracker.py` | **`TestAst1100ResolveHydrateJobArtifactPins`** |

**Broken / obsolete:** none on tracker pin-write suites.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins \
  -q
```

---

### AST-1116 · AST-1091 (UAT)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs`.

`hydrate_job_artifacts_for_display` normalizes `cover_letter` dict values via `normalize_cover_letter_artifact` (Subject/Letter/signature) after pin resolve — overlay only. Field defs: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hydrate cover normalize | `src/core/tracker.py` | **`TestAst1116HydrateCoverLetterNormalize`** (+ revised **`TestAst1100ResolveHydrateJobArtifactPins::test_hydrate_replaces_pin_strings_leaves_legacy_dicts`**) |

**Broken / obsolete:** AST-1100 hydrate assert that a partial `{"Subject": "keep"}` stays un-normalized — superseded by AST-1116 spine normalize.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1116HydrateCoverLetterNormalize \
  tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins \
  -q
```
