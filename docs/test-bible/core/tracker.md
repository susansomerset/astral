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

`legal_job_successor_states` lists every `JOB_STATES` key except `from_state`, registry order, no `prior_states` filter (**AST-1811** operator override — was prior-filtered pre-1811; see § AST-1812). `persist_skipped_job_edits` gates on `SKIPPED_STATES`, writes title/link/`job_description` before optional `transition_job_state`, allows empty JD, rejects empty title/link. API wrap: **`docs/test-bible/ui/api/api_jobs.md`**.

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

### AST-1812 · AST-1809 (gap — skipped-job any-state override)

**Parent:** [AST-1809](https://linear.app/astralcareermatch/issue/AST-1809). **Sibling product:** AST-1811 (`sub/AST-1809/AST-1811-skipped-any-state`). **Publish:** `origin/sub/AST-1809/AST-1812-skipped-any-state-tests`.

Skipped-edit path is an operator override: successors = every `JOB_STATES` key except current; `persist_skipped_job_edits` rejects non-`JOB_STATES` targets (implicit `*_RETRY`, runtime hop labels) with "not in allowed list" before any hop, then calls `transition_job_state(..., enforce_prior_states=False)`. `transition_job_state` default (and explicit `True`) still enforces `prior_states`; `False` waives priors only — registration still checked; history + `state_changed_at` still written.

| Area | Source | Component tests |
| --- | --- | --- |
| Successor list | `src/core/tracker.py` | **`[bug-repro]`** `TestAst1453LegalJobSuccessorStates::test_ast1811_bug_repro_real_registry_candidate_skipped`, `::test_every_key_except_self_ignores_prior_states` |
| Persist hop | `src/core/tracker.py` | **`[bug-repro]`** `TestAst1453PersistSkippedJobEdits::test_ast1811_bug_repro_any_job_state_key_bypasses_prior`, `::test_writes_title_link_jd_then_transition` (asserts `enforce_prior_states=False`), `::test_field_writes_before_unregistered_target_rejected` (was `…_illegal_transition_propagates`) |
| `enforce_prior_states` flag | `src/core/tracker.py` | `TestTransitionJobState::test_ast1811_enforce_prior_states_false_skips_prior_check`, `::test_ast1811_enforce_prior_states_false_still_checks_registration`; default enforcement stays `::test_rejects_invalid_prior_state` |

**Broken / obsolete (rewritten this pass):** prior-filtered successor assertion; transition mock without the keyword-only flag; "illegal hop" premise → unregistered-target premise (core + API `test_put_unregistered_state_409`).

**Pre-existing unrelated reds** in `test_tracker.py` / `test_api_jobs.py` on `origin/dev` (e.g. `company.candidate_id` schema drift, `TestAst562*`, `TestInitializeJob`) — not this ticket; run the narrowed manifest, not whole files.

## QA test manifest

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestTransitionJobState \
  tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates \
  tests/component/core/test_tracker.py::TestAst1453PersistSkippedJobEdits \
  tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut \
  -q
```

**Pass criterion:** pytest green on manifest lines (8 AST-1811 nodes red pre-fix → green post-fix) — not zero-arg harness / branch-lock gate.

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

**Broken / obsolete this pass:** calls to deleted `save_job_artifact_job_resume_body` / `save_job_artifact_cover_letter` / `persist_finalize_*` in AST-1554/1556 + cover normalize + from-parsed suites — revised to `save_job_artifact` / `_prepare_job_replica_body` (**AST-1603** privatized prepare). Hydrate overlay still asserts `get_current_artifact` via `get_job_current`.

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

---

### AST-1600 · AST-1588 (bug)

**Publish:** `origin/sub/AST-1588/AST-1600-job-resume-cover-not-persisting`.

`_candidate_id_for_job` prefers denormalized `job.candidate_id`; `save_job_artifact` passes `candidate_id=` into `database.save_artifact`. Agent land: **`docs/test-bible/core/agent.md`** § AST-1600.

| Area | Source | Component tests |
| --- | --- | --- |
| Prefer job.candidate_id | `src/core/tracker.py` | **`[bug-repro]`** `TestAst1600TrackerCandidateIdLand::test_bug_repro_candidate_id_for_job_prefers_job_column` |
| Pass candidate_id into save_artifact | `src/core/tracker.py` | **`[bug-repro]`** `…::test_bug_repro_save_job_artifact_passes_candidate_id` |

**Broken / obsolete this pass:** AST-1592 `save_artifact` mocks revised to accept `candidate_id=` (would TypeError once make-fix lands).

**Integration:** none.

### AST-1603 · AST-1601

**Parent:** [AST-1601](https://linear.app/astralcareermatch/issue/AST-1601). **Publish:** `origin/sub/AST-1601/AST-1603-agent-tracker-land-via-task-config-artifact-key`.

`prepare_job_replica_body` → private `_prepare_job_replica_body`. `_JOB_ARTIFACT_PIN_KEYS` = `("proposed_answers",)` only. Hydrate still overlays `job_resume` / `cover_letter` via `get_job_current`. Agent land: **`docs/test-bible/core/agent.md`** § AST-1603.

| Area | Source | Component tests |
| --- | --- | --- |
| Pin keys + private prepare + hydrate overlay | `src/core/tracker.py` | **`TestAst1603TrackerPinKeysAndPrivatePrepare`** |
| Revised prepare coat-check calls | same | **`TestAst1554BodyReplicaPersistHelpers`** |
| Revised public-API assert (prepare private) | same | **`TestAst1592TrackerCatalogWriteReadCitation::test_type_specific_public_saves_removed`** |

**Broken / obsolete this pass:** public `prepare_job_replica_body` hasattr / call sites; pin-key lists including `job_resume` / `cover_letter`.

**Integration:** none.

### AST-1613 · AST-1610 (bug) — docs-acceptance

**Publish:** `origin/sub/AST-1610/AST-1613-fix-job-artifacts-prepare-empty`.

Product coerce (`_coerce_job_replica_parsed` + prepare/land string→dict) lands on this ticket. **No new tests on AST-1613** — string-JSON prepare/land `[bug-repro]` lives on sibling gap **AST-1614**. Existing AST-1603 suites still inject dict `parsed` / mock prepare and do not exercise the text-format path.

**Integration:** none.

### AST-1614 · AST-1610 (gap)

**Publish:** `origin/sub/AST-1610/AST-1614-gap-string-json-prepare-land-repro`.

String-JSON prepare/land repro for AST-1613 coerce. Agent land: **`docs/test-bible/core/agent.md`** § AST-1614.

| Area | Source | Component tests |
| --- | --- | --- |
| Finalize-shaped string → prepare body | `src/core/tracker.py` | **`[bug-repro]`** `TestAst1614StringJsonPrepare::test_bug_repro_prepare_lands_finalize_shaped_string_json` |
| Non-JSON string still prepare_empty | same | **`TestAst1614StringJsonPrepare::test_bug_repro_prepare_empty_on_non_json_string`** |
| Cover-letter string JSON path | same | **`TestAst1614StringJsonPrepare::test_bug_repro_prepare_lands_cover_letter_string_json`** |

**Broken / obsolete this pass:** none — additive coverage; AST-1603 dict/mock suites unchanged.

**Integration:** none.

## QA test manifest

See **`docs/test-bible/core/agent.md`** § AST-1614 (shared agent+tracker manifest).

**Bible shasum (publish tip):** filled with agent.md after publish.

### AST-1680 · AST-1677

**Parent:** [AST-1677](https://linear.app/astralcareermatch/issue/AST-1677). **Publish:** `origin/sub/AST-1677/AST-1680-job-drafting-interface-rewires`.

Job-resume prepare/filter paths hydrate operative structure onto a working `cd` copy when `candidate_id_for_current_read` is known, then `resolve_resume_structure` / filter — table current wins when the library blob is empty/missing. Sites: `_prepare_job_resume_content`, `parsed_matches_resume_content_shape`, `parsed_matches_job_resume_content`, `job_has_persisted_resume_body`, `persist_job_artifact_from_parsed` resume branch. Consult catalog: **`docs/test-bible/core/consult.md`** § AST-1680.

| Area | Source | Component tests |
| --- | --- | --- |
| hydrate→prepare/filter (table-only + no-cid skip) | `src/core/tracker.py` | **`TestAst1680JobResumeHydrateBeforeResolve`** |

**Broken / obsolete this pass:** none — AST-518 prepare still seeds a library blob without cid.

**Integration:** none.

## QA test manifest

See **`docs/test-bible/core/consult.md`** § AST-1680 (shared numbered list).

**Bible shasum (publish tip):**
- `docs/test-bible/core/tracker.md` — *(filled after publish)*

### AST-1702 · AST-1640

**Parent:** [AST-1640 — Job source_entity parent](https://linear.app/astralcareermatch/issue/AST-1640). **Publish:** `origin/sub/AST-1640/AST-1702-tracker-land-parent-writes-link-inherit-bot-block-jd-append`.

`save_meteorite_job(meteorite_id=…)` creates under `source=meteorite` + `source_entity_id`; company/gazed match supersedes in-place (same `astral_job_id`, keep `company_id`, append history); never clobber existing meteorite parent. Land surfaces: **`docs/test-bible/core/meteorite.md`** § AST-1702.

| Area | Source | Component tests |
| --- | --- | --- |
| Create + company→meteorite supersede | `src/core/tracker.py` | **`TestAst1702SourceEntityLand::test_save_meteorite_job_create_and_gazed_supersede`** |
| Never clobber meteorite parent | `src/core/tracker.py` | **`…::test_save_meteorite_job_never_clobbers_meteorite_parent`** |
| Tracker Style D on land debug | `src/core/tracker.py` | **`TestAst1470LandMeteorite::test_debug_true_emits_tracker_style_d_false_silent`** |

**Broken / obsolete:** required `company=` parent arg on `save_meteorite_job`.

**Integration:** none.

## QA test manifest

See **`docs/test-bible/core/meteorite.md`** § AST-1702 (shared numbered list).

**Bible shasum (publish tip):**
- `docs/test-bible/core/tracker.md` — *(filled after publish)*

### AST-1704 · AST-1640

**Parent:** [AST-1640 — Job source_entity parent](https://linear.app/astralcareermatch/issue/AST-1640). **Publish:** `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`.

Gazed `ingest_jobs` writes `source=company`, `source_entity_id` + `company_id` to employer short_name. Primary manifest: **`docs/test-bible/core/consult.md`** § AST-1704.

| Area | Source | Component tests |
| --- | --- | --- |
| Ingest company parent fields | `src/core/tracker.py` | **`TestIngestJobs::test_counts_new_and_duplicate_rows`** (extended) |

**Broken / obsolete this pass:** none.

**Integration:** none.


### AST-1807 · AST-1805 (implicit _RETRY substate)

**Parent:** [AST-1804](https://linear.app/astralcareermatch/issue/AST-1804). **Publish:** `origin/sub/AST-1804/AST-1807-implicit-retry-tests`. Product: **AST-1805** (`{base}_RETRY` validates through its registered base; retry priors derived by `state_prior_states`). Probe retries are never registry keys, so these stay green through **AST-1806**'s purge. Unregistered base (`NOPE_RETRY`) is still rejected everywhere.

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** `PASSED_GET → PASSED_GET_RETRY` saves (pre-fix: `not in allowed list`) | `src/core/tracker.py` `transition_job_state` | **`TestTransitionJobState::test_ast1807_bug_repro_base_to_implicit_retry`** |
| Derived priors gate `PASSED_DO → PASSED_GET_RETRY` | same | **`…::test_ast1807_derived_priors_still_gate_retry`** |
| `NOPE_RETRY` rejected, message preserved | same | **`…::test_ast1807_rejects_unregistered_base_retry`** |

**Broken / obsolete:** none.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestTransitionJobState::test_ast1807_bug_repro_base_to_implicit_retry \
  tests/component/core/test_tracker.py::TestTransitionJobState::test_ast1807_derived_priors_still_gate_retry \
  tests/component/core/test_tracker.py::TestTransitionJobState::test_ast1807_rejects_unregistered_base_retry \
  -q
```

### AST-1864 · AST-1853 (run_id on job state_history)

**Parent:** [AST-1853 — Execution History for job modals](https://linear.app/astralcareermatch/issue/AST-1853). **Publish:** `origin/sub/AST-1853/AST-1864-record-producing-run-on-job-state-rows`. Product: private `_stamp_run_id` adds `run_id` = active `log_batch_id` to entries appended by `transition_job_state` and `write_job_dispatch_hop_label`; `batch_id` unchanged; no run context (`None` / `""`) → key **absent**. Modal clickability (AC3 tail) belongs to the frontend sibling — not asserted here.

| Area | Source | Component tests |
| --- | --- | --- |
| AC1 single-hop: run ctx `X` = claim `X` → `run_id == X` | `src/core/tracker.py` `transition_job_state` | **`TestAst1864RunIdStamp::test_single_hop_transition_stamps_dispatch_batch`** |
| AC2 chained hop row: `run_id == H`, `batch_id == C` | same `write_job_dispatch_hop_label` | **`…::test_chained_hop_label_stamps_hop_id_not_claim`** |
| AC2 graduation / chain-error row inside hop ctx | same `transition_job_state` | **`…::test_chained_transition_stamps_hop_id_not_claim`** |
| AC3 no run ctx (`None`, `""`) → no `run_id` key, both appenders | same `_stamp_run_id` false branch | **`…::test_no_run_context_leaves_key_absent[None]`**, **`…[]`** |
| Regression (partial-key asserts unchanged) | same | **`TestTransitionJobState`**, **`TestAst848DispatchChainTracker`** |

**Broken / obsolete:** none. **Pre-existing reds (not this ticket):** 17 `test_tracker.py` failures identical with `src/core/tracker.py` at `origin/dev` (`TestAst733InitializeJobCollision` ×3, `TestAst551StructureAlignedResumeChain` ×3, `TestAst552BuildArtifactsGate` ×1, `TestAst562ArtifactBuildTransitions` ×6, `TestAst997ExperienceJobArrayPersist` ×1, `TestAst1523NotesMetadataRetention` ×1, `TestAst1693SaveMeteoriteDuplicateLinkBackfill` ×2) — manifest is narrowed so they do not gate this child.

**Integration:** none — do not invent.

## QA test manifest

1. **AC1–AC3 + regression (pytest):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1864RunIdStamp \
  tests/component/core/test_tracker.py::TestTransitionJobState \
  tests/component/core/test_tracker.py::TestAst848DispatchChainTracker \
  -q
```

2. **AC4 (no API / schema change):** `git diff origin/dev...origin/sub/AST-1853/AST-1864-record-producing-run-on-job-state-rows -- src/ui/api/ src/data/` is empty.

**Pass criterion:** item 1 green + item 2 empty — narrowed run, not zero-arg harness / branch-lock gate (pre-existing reds above).

**Bible shasum (publish tip):**
- `docs/test-bible/core/tracker.md` — *(filled after publish)*

### AST-1872 · AST-1862 (config tab order, score template, server-side skip flag)

Public **`job_state_admits_transition(current_state, to_state)`** wraps `_job_state_matches_prior` + `state_prior_states(JOB_STATES, to_state)` — same rule `transition_job_state` enforces (hop sub-states resolve via base; non-hop suffix does not). Unregistered `to_state` raises `KeyError`. `GET /api/jobs/<id>` attaches **`can_skip`** (always present) via this function with target `CANDIDATE_SKIPPED`. Config slice: `JOBS_RECOMMENDED_REPORT_TOP_TABS` Analysis-first; `PHASE_SCORE_HEADER_TITLE_TEMPLATE` gains ` - {score}`. Route: **`docs/test-bible/ui/api/api_jobs.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Admitted: `RECOMMENDED`, `CANDIDATE_REVIEW`, `BUILD_ARTIFACTS`, `BUILD_ARTIFACTS.draft_job_resume` | `src/core/tracker.py` `job_state_admits_transition` | **`TestAst1872JobStateAdmitsTransition::test_skip_admitted`** |
| Refused: `CANDIDATE_SKIPPED`, `CANDIDATE_APPLIED`, `BUILD_ARTIFACTS.resume` (non-hop), `""`, `None` | same | **`…::test_skip_refused`** |
| Unregistered target fails loud | same | **`…::test_unregistered_target_fails_loud`** |
| AC2 detail `can_skip` per state (real core rule, not mocked); missing state → `false` | `src/ui/api/api_jobs.py` `detail` | **`test_api_jobs.py::TestAst1872DetailCanSkip`** |
| AC1 config: tab order Analysis, Summary, Artifacts, Discussion, Meteorite (constant + manifest) | `src/utils/config.py` | **`test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs`** (revised) · **`TestAst1550DiscussionHopKeys::test_top_tabs_discussion_after_artifacts`** (revised) · **`TestAst1691MeteoriteReportConfig`** (unchanged, holds) |
| Header template exact text with `{score}` | same | **`TestAst1348PhaseScoreHeaderTitleConfig`** (extended) |
| Regression: detail skipped-edit meta / other detail fields | `src/ui/api/api_jobs.py` | **`TestAst1453SkippedEditMetaAndPut`**, **`TestAst1704JobsDetailParentFields`** |

**Broken / obsolete (revised this pass):** `test_config.py` `TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs` and `TestAst1550DiscussionHopKeys::test_top_tabs_discussion_after_artifacts` asserted Summary-first order.

**Out of scope (sibling AST-1874):** `test_JobAnalysisReportModal.test.tsx` default-tab / tab-bar asserts and `tests/component/frontend/fixtures/stateUiManifestFixture.ts` (`report_top_tabs` order + `phase_score_header_title_template`) — the fixture feeds `formatPhaseSectionScoreTitle`, which #3 owns; re-pinning here would red Vitest before the formatter lands.

**Pre-existing reds (not this ticket, identical on dev-only tip `5ee6d34b`):** `TestJobsRoutes::test_put_resume_content_persists_via_tracker`, `test_api_system.py::TestSystemNavHelpers::test_resolve_nav_keeps_candidate_facing_groups_and_stubs`, `TestAst1375InflightHideStatesManifest::test_manifest_includes_inflight_hide_states` — not in this manifest.

**Integration:** none — no scenario touches detail / report tabs / skip.

## QA test manifest

1. **AC1 + AC2 + regression (pytest):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1872JobStateAdmitsTransition \
  tests/component/ui/api/test_api_jobs.py::TestAst1872DetailCanSkip \
  tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut \
  tests/component/ui/api/test_api_jobs.py::TestAst1704JobsDetailParentFields \
  tests/component/utils/test_config.py::TestAst1348PhaseScoreHeaderTitleConfig \
  tests/component/utils/test_config.py::TestAst1550DiscussionHopKeys \
  tests/component/utils/test_config.py::TestAst1691MeteoriteReportConfig \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs \
  -q
```

2. **AC3 (no routes / schema / Modal):** `git diff origin/dev...origin/sub/AST-1862/AST-1872-config-tab-order-score-template-skip-flag -- src/data/ src/ui/frontend/src/components/Modal.tsx` is empty; `grep -n "@jobs_bp.route" src/ui/api/api_jobs.py | wc -l` prints `15`.

**Pass criterion:** item 1 green + item 2 holds — narrowed run, not zero-arg harness / branch-lock gate (pre-existing reds above).

**Bible shasum (publish tip):**
- `docs/test-bible/core/tracker.md` — *(filled after publish)*

---

### AST-1974 · AST-1970

New `candidate_skip_job`: not found → ValueError; illegal (e.g. `CANDIDATE_APPLIED`) → ValueError with claim untouched; legal → clear held `batch_id`, transition to `CANDIDATE_SKIPPED` (hop labels resolve via base). `list_jobs` / `count_jobs` facades forward `exclude_states`.

**New:** **`TestAst1974CandidateSkipJob`** (6, real SQLite with `candidate_id` seeds). Manifest: [`ui/api/api_jobs.md`](../ui/api/api_jobs.md) § AST-1974 item 4.

### AST-2066 · AST-2043

`save_job_artifact` identical-to-current no-op: when the prepared body equals the current row's body, it returns the existing uuid and adds no row (AC7). New `list_job_artifact_versions` / `set_job_artifact_current` (job catalog keys only; candidate keys raise `not job-scoped`).

**New:** **`TestAst2066JobVersions`** (6, real SQLite; new lines fully branch-covered for `LOCKED_AT_100`). Existing cover-letter `save_job_artifact` tests stub only `save_artifact`, so the no-op lookup reads the harness DB; the fake job ids never match, and they stay green. Manifest: [`candidate.md`](candidate.md) § AST-2066 item 4.

### AST-2081 · AST-2046 (job resume structure, Line format, format/flow catalog)

**Publish:** `origin/sub/AST-2046/AST-2081-job-structure-line-format`. Backend only. New catalog key `job.artifacts.job_resume_structure`. `get_job_effective_resume_structure(jid, cd=None, *, hydrate_from_base=False)` returns the job's current row when it has non-empty `sections`, else the candidate's resolved structure (hydrated from `base_resume` only on the editor GET path). The read never writes. `save_job_artifact` merges the structure body over the job's effective structure, slugs the sections, normalizes, and raises `ValueError` on an invalid body. `_prepare_job_resume_content(content, cd, jid=None)` filters to the job's effective structure, so job-only sections survive a `job_resume` save.

| Area | Source | Component tests |
| --- | --- | --- |
| AC16 inherit until edited; GET writes no row; blank jid / non-dict artifacts / empty-sections row fall back | `src/core/tracker.py` | **`TestAst2081JobResumeStructure::test_inherits_candidate_until_edited_and_get_never_writes`**, **`…::test_blank_jid_and_non_dict_artifacts_fallbacks`**, **`…::test_own_row_with_empty_sections_falls_back`** |
| AC15 + AC18 isolation (rename / format → line / reorder / accent on job A; job B and candidate untouched); partial bodies merge | same | **`…::test_save_isolates_job_structure`**, **`…::test_save_partial_bodies_merge_over_effective`** |
| Invalid body → `ValueError`, no row | same | **`…::test_save_rejects_invalid`** (3) |
| AC17 job-only section survives the `job_resume` save (job B, inheriting, drops it) | same | **`…::test_job_only_section_survives_job_resume_save`** |

Real SQLite (`sqlite_in_memory`). Only `_candidate_id_for_job` / `_candidate_data_for_job` are stubbed. New lines are fully branch-covered for `LOCKED_AT_100`. Sibling pages: [`builder.md`](builder.md), [`candidate.md`](candidate.md), [`../ui/api/api_jobs.md`](../ui/api/api_jobs.md), [`../ui/api/api_candidate.md`](../ui/api/api_candidate.md), [`../utils/config.md`](../utils/config.md) § AST-2081.

**Broken / obsolete (revised this pass):** the plan's two known config drifts. `test_config.py::TestAst1303ResumeStructureCatalog::test_body_formats_defaults_emphasis_and_extra_id_rules` gains `line`. `…::TestAst1590JobArtifactCatalogKeys::test_artifact_config_has_pilot_and_job_keys` gains `job.artifacts.job_resume_structure`. A full `tests/component` diff against the `origin/dev` product found no other new failures. No integration scenario touches resume structure.

**Manifest (test-child) — narrowed:**

1. AST-2081 nodes, 42 tests (4 config + 2 revised config + 3 candidate + 9 tracker + 5 builder + 13 job routes + 6 candidate GET class):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst2081FormatCatalogAndJobStructureKey \
  tests/component/utils/test_config.py::TestAst1303ResumeStructureCatalog::test_body_formats_defaults_emphasis_and_extra_id_rules \
  tests/component/utils/test_config.py::TestAst1590JobArtifactCatalogKeys::test_artifact_config_has_pilot_and_job_keys \
  tests/component/core/test_candidate.py::TestAst2081ResumeStructureEditorPayload \
  tests/component/core/test_tracker.py::TestAst2081JobResumeStructure \
  tests/component/core/test_builder.py::TestAst2081LineFormatAndJobStructure \
  tests/component/ui/api/test_api_jobs.py::TestAst2081JobResumeStructureRoutes \
  tests/component/ui/api/test_api_candidate.py::TestAst1306ResumeStructureAuthorApi \
  -q
```

2. Regression: `tests/component/core/test_builder.py` must be fully green (197 passed). The other five files have to match the `origin/dev`-product baseline failure counts, which predate this ticket: `test_candidate.py` 18, `test_tracker.py` 17, `test_api_candidate.py` 2, `test_api_jobs.py` 2, `test_config.py` 31. AST-2081 must add **no** new failure.

3. AC14 grep (frontend half): this is **AST-2083 / AST-2084**. The data half is covered by item 1 (config + catalog payload).

**Pass criterion:** item 1 is 42 passed, and item 2 holds. This is a narrowed run, not the zero-arg harness / branch-lock gate.
