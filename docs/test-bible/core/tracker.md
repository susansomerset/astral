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

### AST-1271 · AST-1268

**Parent:** [AST-1268 — draft_job_resume response schema is wrong](https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong). **Publish:** `origin/sub/AST-1268/AST-1271-deviations-metadata-retention-on-draft-hop`.

Persist `deviations` under `job_data.artifacts.deviations` (sibling of `resume_content`); `_resume_payload_body` skips nest + `payload_metadata_keys` even when string-typed; cancel clears via `JOB_BUILD_ARTIFACT_CLEAR_KEYS`. Live hop path: **`docs/test-bible/core/agent.md`** § AST-1271. Config slot: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Extract / save / body skip / persist + clear | `src/core/tracker.py` | **`TestAst1271DeviationsMetadataRetention`**; reuse **`TestAst1270NestedResumePayloadBody`** |

**Integration:** none — do not invent coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1271DeviationsMetadataRetention \
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

`resolve_job_artifact_agent_data_body` loads RESPONSE `block_data` by pin id (coat-check empty/missing). `hydrate_job_artifacts_for_display` shallow-copies artifacts; **AST-1548:** operator `job_resume` / `cover_letter` use job body only (no pin→`agent_data`); `proposed_answers` still pin-resolves. Pin write = **AST-1099** (propose only after AST-1548).

| Area | Source | Component tests |
| --- | --- | --- |
| Resolve + hydrate overlay | `src/core/tracker.py` | **`TestAst1100ResolveHydrateJobArtifactPins`** |

**Broken / obsolete:** hydrate asserts that replace `job_resume`/`cover_letter` pin strings via resolve — AST-1554.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins \
  -q
```

---

### AST-1116 · AST-1091 (UAT)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1116-cover-letter-field-defs`.

`hydrate_job_artifacts_for_display` normalizes `cover_letter` **dict** values via `normalize_cover_letter_artifact` (Subject/Letter/signature) — overlay only. **AST-1548:** pin strings on cover are not resolved for operator hydrate. Field defs: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Hydrate cover normalize | `src/core/tracker.py` | **`TestAst1116HydrateCoverLetterNormalize`** (+ revised **`TestAst1100ResolveHydrateJobArtifactPins`**) |

**Broken / obsolete:** AST-1100 hydrate assert that a partial `{"Subject": "keep"}` stays un-normalized — superseded by AST-1116 spine normalize; pin-resolve cover node — AST-1554.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1116HydrateCoverLetterNormalize \
  tests/component/core/test_tracker.py::TestAst1100ResolveHydrateJobArtifactPins \
  -q
```

---

### AST-1504 · AST-1491 (gap — cover letter hydrate display)

**Parent:** [AST-1491](https://linear.app/astralcareermatch/issue/AST-1491/cover-letter-content-does-not-appear-for-editing). **Publish:** `origin/sub/AST-1491/AST-1504-gap-cover-letter-hydrate-tests`. Product fix: **AST-1499**.

Originally pin-resolve cover gaps. **AST-1548/1554:** same behaviors asserted on **job cover dicts**; pin strings stay unresolved on operator hydrate.

| Area | Source | Component tests |
| --- | --- | --- |
| Nested unwrap / empty spine / pin leave | `src/core/tracker.py` | **`TestAst1504CoverLetterHydrateDisplayGaps`** |

**Broken / obsolete:** resolve-on-hydrate cover pin nodes — flipped in AST-1554.

**Integration:** none — do not invent.

## QA test manifest

1. Cover dict unwrap + empty-spine gate + pin leave: `tests/component/core/test_tracker.py::TestAst1504CoverLetterHydrateDisplayGaps`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1504CoverLetterHydrateDisplayGaps \
  -q
```

### AST-1554 · AST-1547 (gap — body replica persist + hydrate)

**Parent:** [AST-1547](https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record). Product: **AST-1548**.

Historical dual-write into `job_data.artifacts`. **AST-1556:** SoT moves to `artifacts` table — helpers rewritten to assert `save_artifact` / no job_data body keys.

| Area | Source | Component tests |
| --- | --- | --- |
| Persist table write + cover + coat-check | `src/core/tracker.py` | **`TestAst1554BodyReplicaPersistHelpers`** (+ hydrate suites above) |

**Broken / obsolete:** dual-write `job_resume`+`resume_content` into `job_data` — AST-1556.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1554BodyReplicaPersistHelpers \
  -q
```

### AST-1556 · AST-1547 (bug-repro — artifacts table SoT)

**Parent:** [AST-1547](https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record). **Publish:** `origin/sub/AST-1547/AST-1556-job-artifacts-in-artifacts-table`.

Editable `job_resume` / `cover_letter` persist via `database.save_artifact("job", …)`; hydrate overlays `get_current_artifact`; cancel retires table currents. Not `job_data.artifacts.*` as SoT.

| Area | Source | Component tests |
| --- | --- | --- |
| Table save / hydrate / cancel-retire | `src/core/tracker.py` | **`TestAst1556JobArtifactsTableSoT`** (bug-repro) |

**Broken / obsolete:** AST-1554 job_data dual-write asserts.

**Integration:** none — do not invent.

## QA test manifest

1. Bug-repro (table SoT save + hydrate overlay + cancel retire): `tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT`
   - Primary red-first: `::test_save_job_resume_body_writes_artifacts_table_not_job_data`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT \
  tests/component/core/test_tracker.py::TestAst1554BodyReplicaPersistHelpers \
  -q
```

**Pass criterion:** red on pre-AST-1556 product (job_data dual-write); green after make-fix table writers — `test-fix` verifies the flip.

---

### AST-1420 · AST-1419

**Parent:** [AST-1419 — Create a Copy button on the Job Modal](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal). **Publish:** `origin/sub/AST-1419/AST-1420-job-copy-snapshot-payload`.

`assemble_job_copy_snapshot` returns `{job, agent_data}`: stored job (artifact pins stay ids; no hydrate / flatten / agent_story); `agent_data` keyed by every id from the stored-record walk ∪ `list_entity_latest_agent_refs`, each hop’s `blocks` iterated from `BLOCK_TYPES` with pointer-resolved `block_data`. Missing job → `None`. Route: **`docs/test-bible/ui/api/api_jobs.md`**. Copy chrome: AST-1421.

| Area | Source | Component tests |
| --- | --- | --- |
| Assembler + pointer content + BLOCK_TYPES + debug | `src/core/tracker.py` | **`TestAst1420AssembleJobCopySnapshot`** |
| Authenticated copy route | `src/ui/api/api_jobs.py` | **`TestAst1420CopySnapshotRoute`** |

**Broken / obsolete:** none — additive; existing `GET /api/jobs/<id>` detail hydrate suites still hold.

**Integration:** no existing jobs-pipeline scenario in `tests/integration/` — no revision (do not invent).

## QA test manifest

1. Assembler (pins stay ids, hop union, pointer `block_data`, skip/error paths, debug): `tests/component/core/test_tracker.py::TestAst1420AssembleJobCopySnapshot`
2. `GET /api/jobs/<id>/copy` (401 / 404 / 200 no-hydrate / 500 / debug query): `tests/component/ui/api/test_api_jobs.py::TestAst1420CopySnapshotRoute`

**AST-1420** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1420AssembleJobCopySnapshot \
  tests/component/ui/api/test_api_jobs.py::TestAst1420CopySnapshotRoute \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1453 · AST-1446

**Parent:** [AST-1446 — When a job is in a Skipped state, make all fields editable](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable). **Publish:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits`.

`legal_job_successor_states` lists `JOB_STATES` keys `transition_job_state` would accept from `from_state` (excludes self; includes unrestricted `prior_states is None`). `persist_skipped_job_edits` gates on `SKIPPED_STATES`, writes title/link/`job_description` before optional `transition_job_state`, allows empty JD, rejects empty title/link. API wrap: **`docs/test-bible/ui/api/api_jobs.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Successor list + persist | `src/core/tracker.py` | **`TestAst1453LegalJobSuccessorStates`**, **`TestAst1453PersistSkippedJobEdits`** |

**Broken / obsolete:** none.

**Integration:** none.

## QA test manifest

1. `tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates`
2. `tests/component/core/test_tracker.py::TestAst1453PersistSkippedJobEdits`
3. `tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut` (API)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates \
  tests/component/core/test_tracker.py::TestAst1453PersistSkippedJobEdits \
  tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1507 · AST-1460

**Parent:** [AST-1460 — Advise resume needs a coded list for clear adherence](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1507-estelle-coded-resume-advice-list`.

Extract/save coded advice list under `job_data.artifacts.resume_advice` (sibling metadata — not resume body); `clear_job_build_artifacts` drops slot via `JOB_BUILD_ARTIFACT_CLEAR_KEYS`. Parse/validate: **`docs/test-bible/core/candidate.md`** § AST-1507. Config slot: **`docs/test-bible/utils/config.md`** § AST-1507. Live hop path: **`docs/test-bible/core/agent.md`** § AST-1507.

| Area | Source | Component tests |
| --- | --- | --- |
| Extract/save/cancel clear | `src/core/tracker.py` | **`TestAst1507ResumeAdviceMetadataRetention`** |

**Broken / obsolete:** none — `_resume_payload_body` already skips draft metadata keys only; advise is text → artifacts path.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1507ResumeAdviceMetadataRetention \
  -q
```

---

### AST-1508 · AST-1460

**Parent:** [AST-1460 — Advise resume needs a coded list for clear adherence](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1508-judith-per-code-advice-adherence`.

Extract/save per-code **`advice_adherence`** under `job_data.artifacts.advice_adherence`; **`get_job_resume_advice_codes`** reads expected codes from **`resume_advice`** artifact (**AST-1507**); `_resume_payload_body` skips adherence metadata; cancel clears via `JOB_BUILD_ARTIFACT_CLEAR_KEYS`. Replaces **AST-1271** deviations helpers. Parse/validate: **`docs/test-bible/core/candidate.md`** § AST-1508. Config slot: **`docs/test-bible/utils/config.md`** § AST-1508. Live hop path: **`docs/test-bible/core/agent.md`** § AST-1508.

| Area | Source | Component tests |
| --- | --- | --- |
| Extract/save/body skip/persist/clear + code load | `src/core/tracker.py` | **`TestAst1508AdviceAdherenceMetadataRetention`**; revised **`TestAst1270NestedResumePayloadBody`** |

**Broken / obsolete:** **`TestAst1271DeviationsMetadataRetention`** — retired; stub asserts deviations helpers removed.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1508AdviceAdherenceMetadataRetention \
  tests/component/core/test_tracker.py::TestAst1270NestedResumePayloadBody \
  -q
```

### AST-1518 · AST-1414

**Parent:** [AST-1414 — Estelle needs to be able to use our endpoints](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints). **Publish:** `origin/sub/AST-1414/AST-1518-job-company-candidate-contact-task-reads`.

Four `contact_task_*` read handlers + `get_job_by_pattern`: candidate-scoped pattern match; company→`candidate_id` ownership; hydrate via `get_entity_agent_story` (no coat-check/gazer). Markup/dispatch: **`docs/test-bible/core/contact.md`** (AST-1515).

| Area | Source | Component tests |
| --- | --- | --- |
| Pattern / job / company / candidate reads + Style D | `src/core/tracker.py` | **`TestAst1518ContactTaskReads`** |

**Broken / obsolete:** AST-1515 `handler_unavailable` / turn fixtures — retargeted from `gazer_scrape` and `get_job_data` to `create_contact_meteorite` (gazer lands AST-1516; reads land this ticket; meteorite create AST-1517). **AST-1517:** all handlers resolve; AST-1515 fixtures mock `_resolve_contact_task_handler` → `None`. `[qa-handoff]` return: `test_dispatch_handler_unavailable_for_listed_key` must not pin `gazer_scrape`.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1518ContactTaskReads \
  tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  -q
```

---

### AST-1523 · AST-1460

**Parent:** [AST-1460](https://linear.app/astralcareermatch/issue/AST-1460/advise-resume-needs-a-coded-list-for-clear-adherence). **Publish:** `origin/sub/AST-1460/AST-1523-revert-hard-coded-advice-adherence`.

Freeform **`notes`** extract/save/cancel clear (AST-1271 shape, renamed); epic **`resume_advice`** / **`advice_adherence`** helpers removed. Primary: **`docs/test-bible/core/candidate.md`** § AST-1523.

| Area | Source | Component tests |
| --- | --- | --- |
| Notes extract/persist/clear + body skip | `src/core/tracker.py` | **`TestAst1523NotesMetadataRetention`**; revised **`TestAst1270NestedResumePayloadBody`**; **`TestAst1523EpicHelpersRemoved`** |

**Broken / obsolete:** **`TestAst1507ResumeAdviceMetadataRetention`**, **`TestAst1508AdviceAdherenceMetadataRetention`** — retired.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1523NotesMetadataRetention \
  tests/component/core/test_tracker.py::TestAst1270NestedResumePayloadBody \
  tests/component/core/test_tracker.py::TestAst1523EpicHelpersRemoved \
  -q
```


---

### AST-1592 · AST-1588

**Parent:** [AST-1588 — Support job.artifacts.job_resume and job.artifacts.cover_letter as artifacts](https://linear.app/astralcareermatch/issue/AST-1588/support-jobartifactsjob-resume-and-jobartifactscover-letteras). **Publish:** `origin/sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation`.

Tracker generic `save_job_artifact` / `get_job_current` (entity id + catalog key); `job.artifacts.job_resume` writes always auto-cite the owning candidate’s current `base_resume` `artifact_uuid` (or `[]`); cover/other keys pass `source_artifact_ids` through. Hydrate / has-body / from-parsed / agent finalize land via those generics. Type-specific public `save_job_artifact_job_resume_body` / `save_job_artifact_cover_letter` / `persist_finalize_*` removed. API + agent: **`docs/test-bible/ui/api/api_jobs.md`**, **`docs/test-bible/core/agent.md`**. Builder/UI inventory → **AST-1593**.

| Area | Source | Component tests |
| --- | --- | --- |
| Public API + type-specific names gone | `src/core/tracker.py` | **`TestAst1592TrackerCatalogWriteReadCitation::test_type_specific_public_saves_removed`** |
| get_job_current hit/miss/key validation | `src/core/tracker.py` | **`TestAst1592TrackerCatalogWriteReadCitation::test_get_job_current_hit_miss_and_key_validation`** |
| job_resume cites base_resume (ignores caller sources) | `src/core/tracker.py` | **`TestAst1592TrackerCatalogWriteReadCitation::test_job_resume_cites_current_base_resume_uuid`** |
| job_resume empty sources when no base | `src/core/tracker.py` | **`TestAst1592TrackerCatalogWriteReadCitation::test_job_resume_empty_sources_when_no_base_resume`** |
| cover_letter passes caller sources | `src/core/tracker.py` | **`TestAst1592TrackerCatalogWriteReadCitation::test_cover_letter_passes_caller_sources`** |
| Catalog write still table SoT (1554/1556 revised) | `src/core/tracker.py` | **`TestAst1554BodyReplicaPersistHelpers`**, **`TestAst1556JobArtifactsTableSoT`** |

**Broken / obsolete this pass:** calls to deleted `save_job_artifact_job_resume_body` / `save_job_artifact_cover_letter` / `persist_finalize_*` in AST-1554/1556 + cover normalize + from-parsed suites — revised to `save_job_artifact` / `prepare_job_replica_body`. Hydrate overlay still asserts `get_current_artifact` via `get_job_current`.

**Integration:** none — no existing scenario asserts job catalog write/citation.

## QA test manifest (AST-1592)

1. Tracker catalog + citation: `tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation`
2. Revised table-SoT helpers: `tests/component/core/test_tracker.py::TestAst1554BodyReplicaPersistHelpers`
3. Revised bug-repro SoT: `tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT`
4. API PUT catalog keys: `tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_persists_via_tracker_body_helper` + cover PUT in same module
5. Agent finalize → save_job_artifact: `tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin` + `TestAst1554DoTaskBodyReplica`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1592TrackerCatalogWriteReadCitation \
  tests/component/core/test_tracker.py::TestAst1554BodyReplicaPersistHelpers \
  tests/component/core/test_tracker.py::TestAst1556JobArtifactsTableSoT \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_persists_via_tracker_body_helper \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_cover_letter_persists_via_tracker \
  tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin \
  tests/component/core/test_agent.py::TestAst1554DoTaskBodyReplica \
  -q
```

**Pass criterion:** pytest green on lines 1–5 — not zero-arg harness / branch-lock gate.

**Bible path shasum:** `docs/test-bible/core/tracker.md` (fill after publish)
