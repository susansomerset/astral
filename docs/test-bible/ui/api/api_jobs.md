# Api Jobs

**Test module:** `tests/component/ui/api/test_api_jobs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py` | yes |

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

Job GET runs `hydrate_job_artifacts_for_display` (overlay only). PUT `…/artifacts/proposed_answers` still writes a body dict onto that key. PUT `…/artifacts/job_resume` body dual-write is **AST-1548 / AST-1554** (was keep-pin under AST-1430).

| Area | Source | Component tests |
| --- | --- | --- |
| GET hydrate + PUT aliases | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi`** |

**Broken / obsolete:** `test_put_job_resume_writes_body_dict` (pre-AST-1430); `test_put_job_resume_writes_resume_content_keeps_pin` — AST-1554 (keep-pin).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi \
  -q
```

### AST-1430 · AST-1422

**Parent:** [AST-1422](https://linear.app/astralcareermatch/issue/AST-1422/finalize-job-resume-isnt-getting-parsed-into-the-job-resume-renderer). **Publish:** `origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin`. Product fix: **AST-1428**.

**Broken / obsolete under AST-1548/AST-1554:** PUT keep-pin (`test_put_job_resume_writes_resume_content_keeps_pin`) — see AST-1554 dual-write node.

### AST-1554 · AST-1547 (gap — PUT body dual-write)

**Parent:** [AST-1547](https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record). Product: **AST-1548**.

`PUT /api/jobs/<id>/artifacts/job_resume` stays thin → `save_job_artifact_job_resume_body` (table SoT under **AST-1556**).

| Area | Source | Component tests |
| --- | --- | --- |
| PUT via tracker body helper | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi::test_put_job_resume_persists_via_tracker_body_helper`** |

**Broken / obsolete:** dual-write / keep-pin PUT node names — AST-1556.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1100JobArtifactPinResolveApi::test_put_job_resume_persists_via_tracker_body_helper \
  -q
```

### AST-1156 · AST-1150

**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt). **Publish:** `origin/sub/AST-1150/AST-1156-skipped-retry-hop-correct-dispatchable-state`.

`POST /api/jobs/bulk_state` uses `transition_job_state` (priors + history) instead of `save_job` bypass; partial success on per-id `ValueError`.

| Area | Source | Component tests |
| --- | --- | --- |
| bulk_state transition | `api_jobs.py` | revised **`TestJobsRoutes::test_bulk_state_updates_jobs`** |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_bulk_state_updates_jobs \
  -q
```

### AST-1347 · AST-1346

**Parent:** [AST-1346](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header). **Publish:** `origin/sub/AST-1346/AST-1347-persist-phase-score-breakdown`.

`_flatten_grades` lifts `{jd,do,get,like}_score_breakdown` when present on `job_data` (same loop as grades/scores/rubrics). Does not invent when absent. Persist math: **`docs/test-bible/core/consult.md`** (**AST-1347**).

| Area | Source | Component tests |
| --- | --- | --- |
| Flatten lift + absent | `src/ui/api/api_jobs.py` (`_flatten_grades`) | **`TestAst1347FlattenScoreBreakdown`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1347FlattenScoreBreakdown \
  tests/component/ui/api/test_api_jobs.py::TestFlattenGrades \
  -q
```

### AST-1348 · AST-1346

**Parent:** [AST-1346](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header). **Publish:** `origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome`.

After stored-trio lift, `_flatten_grades` derives missing `{jd,do,get,like}_score_breakdown` via `_phase_score_breakdown` when `{prefix}_score` + grades + job-carried rubric are present (response only). Header chrome: **`docs/test-bible/frontend/components.md`** / **`docs/test-bible/frontend/lib.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Derive / keep stored / omit unscored | `src/ui/api/api_jobs.py` (`_flatten_grades`) | **`TestAst1348FlattenDeriveBreakdown`** |

**Broken / obsolete:** none — AST-1347 absent-without-rubric case still holds.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1348FlattenDeriveBreakdown \
  tests/component/ui/api/test_api_jobs.py::TestAst1347FlattenScoreBreakdown \
  -q
```

---

### AST-1420 · AST-1419

**Parent:** [AST-1419 — Create a Copy button on the Job Modal](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal). **Publish:** `origin/sub/AST-1419/AST-1420-job-copy-snapshot-payload`.

`GET /api/jobs/<astral_job_id>/copy` (`@require_auth`) returns `assemble_job_copy_snapshot` JSON: 401 unauthenticated, 404 missing job, 500 assembler exception. Does not hydrate artifacts, flatten grades, or attach `agent_story`. Assembler contract: **`docs/test-bible/core/tracker.md`**. Copy button: AST-1421.

| Area | Source | Component tests |
| --- | --- | --- |
| Copy route wrap | `src/ui/api/api_jobs.py` | **`TestAst1420CopySnapshotRoute`** |

**Broken / obsolete:** none — detail hydrate (**AST-1100**) unchanged.

**Integration:** none — no existing jobs copy/detail scenario to revise.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestAst1420CopySnapshotRoute \
  tests/component/core/test_tracker.py::TestAst1420AssembleJobCopySnapshot \
  -q
```

### AST-1453 · AST-1446

**Parent:** [AST-1446 — When a job is in a Skipped state, make all fields editable](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable). **Publish:** `origin/sub/AST-1446/AST-1453-persist-skipped-job-field-and-state-edits`.

GET detail attaches `fields_editable` + `legal_next_states` (empty when not skipped). Authenticated `PUT /api/jobs/<id>` persists via `persist_skipped_job_edits` (409 not-skipped / unregistered non-`JOB_STATES` target — "not in allowed list" (**AST-1811**: registry keys no longer 409 on this path; see core § AST-1812) / identity collision; 400 empty title/link/state/body; 404 missing). Core contract: **`docs/test-bible/core/tracker.md`**. Form chrome: AST-1454.

| Area | Source | Component tests |
| --- | --- | --- |
| GET meta + PUT status map | `src/ui/api/api_jobs.py` | **`TestAst1453SkippedEditMetaAndPut`** |

**Broken / obsolete:** none — additive keys on GET detail; existing story/hydrate suites still hold. **AST-1812:** `test_put_illegal_transition_409` → `test_put_unregistered_state_409`; `_detail_wire` hydrate mock accepts `astral_job_id=` (pre-existing drift vs `origin/dev` `detail()`).

**Integration:** none — no existing jobs detail/persist scenario to revise.

## QA test manifest

1. Core successors + persist gate/writes/hop ordering: `tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates` + `::TestAst1453PersistSkippedJobEdits`
2. GET meta + PUT auth/status/detail shape: `tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1453LegalJobSuccessorStates \
  tests/component/core/test_tracker.py::TestAst1453PersistSkippedJobEdits \
  tests/component/ui/api/test_api_jobs.py::TestAst1453SkippedEditMetaAndPut \
  -q
```

**Bible shasum (this pass):** `docs/test-bible/ui/api/api_jobs.md` → `0dc463232d8241a0f85e6a85c71b9073aa9a7143` (pre-line)

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1479 · AST-1464

**Parent:** [AST-1464 — Add means to mark job as applied for](https://linear.app/astralcareermatch/issue/AST-1464). **Publish:** `origin/sub/AST-1464/AST-1479-applied-jobs-list-home`.

`GET /api/jobs?view=applied` lists `APPLIED_JOB_STATES` ordered by `state_changed_at`. Page: **`docs/test-bible/frontend/pages.md`** § AST-1479.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied view list | `src/ui/api/api_jobs.py` | **`test_list_applied_uses_applied_job_states`**; revised **`test_list_recommended_and_default`** (unknown view → `[]`, not `view=applied`) |

**Broken / obsolete:** `test_list_recommended_and_default` asserting `view=applied` → `[]`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  -q
```

### AST-1488 · AST-1485

**Parent:** [AST-1485 — Enable Applied job list in nav](https://linear.app/astralcareermatch/issue/AST-1485). **Publish:** `origin/sub/AST-1485/AST-1488-applied-jobs-list-home-re-land`.

**Re-land of AST-1479** — same `view=applied` list branch. **Existing coverage — no new tests.** Full manifest: **`docs/test-bible/frontend/pages.md`** § AST-1488.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied view list | `src/ui/api/api_jobs.py` | **`test_list_applied_uses_applied_job_states`**; **`test_list_recommended_and_default`** |

**Broken / obsolete:** none.

**Integration:** none.

### AST-1498 · AST-1485

**Parent:** [AST-1485 — Enable Applied job list in nav](https://linear.app/astralcareermatch/issue/AST-1485). **Publish:** `origin/sub/AST-1485/AST-1498-candidate-applied-missing-from-applied-screen`.

Applied list must include post-applied jobs on stem/meteorite companies when `company.candidate_id` is NULL — supplement + repair pass on `view=applied` only. Page POST body: **`docs/test-bible/frontend/pages.md`** § AST-1498.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied view stem linkage (**[bug-repro]**) | `src/ui/api/api_jobs.py` | **`test_list_applied_includes_stem_job_null_company_candidate_id_ast1498`** |
| Primary pass params (regression) | same | revised **`test_list_applied_uses_applied_job_states`** (multi-call safe) |

**Broken / obsolete:** none pre-fix — **`test_list_applied_uses_applied_job_states`** revised so supplement pass does not false-fail post-fix.

**Integration:** none.

## QA test manifest

1. **[bug-repro]** API stem NULL linkage: `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_includes_stem_job_null_company_candidate_id_ast1498`
2. Applied primary pass regression: `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states`
3. **[bug-repro]** Page POST `candidate_id`: `tests/component/frontend/pages/test_JobsApplied.test.tsx` — **`AST-1498 [bug-repro]`**

**AST-1498** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_includes_stem_job_null_company_candidate_id_ast1498 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_applied_uses_applied_job_states \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  --testNamePattern="AST-1498"
```

**Pass criterion:** repro lines flip red→green after `make-fix`; regression line stays green — not zero-arg harness / branch-lock gate.


---

### AST-1592 · AST-1588

**Publish:** `origin/sub/AST-1588/AST-1592-tracker-generic-catalog-write-read-citation`.

PUT job_resume / cover_letter / legacy resume_content call `save_job_artifact` with catalog keys (not type-specific helpers). Primary tracker coverage: **`docs/test-bible/core/tracker.md`** § AST-1592.

| Area | Source | Component tests |
| --- | --- | --- |
| PUT job_resume → catalog write | `src/ui/api/api_jobs.py` | **`TestAst1100JobArtifactPinResolveApi::test_put_job_resume_persists_via_tracker_body_helper`** (revised) |
| PUT cover_letter → catalog write | `src/ui/api/api_jobs.py` | **`TestJobsRoutes::test_put_cover_letter_persists_via_tracker`** (revised) |

**Broken / obsolete this pass:** spies on `save_job_artifact_job_resume_body` / `save_job_artifact_cover_letter` — retargeted to `save_job_artifact`.

### AST-1694 · AST-1686

**Parent:** [AST-1686](https://linear.app/astralcareermatch/issue/AST-1686/hyperlink-to-job-with-meteorite-http-link). **Publish:** `origin/sub/AST-1686/AST-1694-minimal-listing-href-job-get`.

`GET /api/jobs/<id>` always includes `listing_href` (http(s) string or JSON `null`). Prefer http(s) `job.job_link`; else http(s) from `get_meteorite_link_by_astral_job_id`; soft-fail on lookup throw → `null`. Primary data helper: **`docs/test-bible/data/database/meteorites.md`** § AST-1694. Does **not** attach `related_meteorite` (AST-1691 / AST-1685).

| Area | Source | Component tests |
| --- | --- | --- |
| Prefer job_link / meteorite fallback / non-http null / soft-fail | `src/ui/api/api_jobs.py` | **`tests/component/ui/api/test_api_jobs_ast1694_listing_href.py::TestAst1694ListingHref`** |
| Detail key + hydrate kwargs | same | **`TestAst1694DetailListingHrefKey`** (same module) |

**Broken / obsolete:** shared `TestJobsRoutes` detail cases that omit `listing_href` / hydrate `astral_job_id` — covered by **`TestAst1694DetailListingHrefKey`**.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs_ast1694_listing_href.py \
  tests/component/data/database/test_meteorites.py::TestAst1694GetMeteoriteLinkByAstralJobId \
  -q
```

### AST-1691 · AST-1685

**Publish:** `origin/sub/AST-1685/AST-1691-meteorite-lookup-report-config-api`.

`GET /api/jobs/<id>` includes `related_meteorite` (flat object or `null`); soft-fail → `null` (not 500). Primary: **`docs/test-bible/data/database/meteorites.md`** § AST-1691.

| Area | Source | Component tests |
| --- | --- | --- |
| related_meteorite object | `src/ui/api/api_jobs.py` | **`TestJobsRoutes::test_detail_related_meteorite_object`** |
| related_meteorite soft-fail | same | **`TestJobsRoutes::test_detail_related_meteorite_soft_fail`** |
| related_meteorite null (no link) | same | revised **`test_detail_returns_agent_story`**, **`test_detail_soft_fails_agent_story`** |

**Broken / obsolete:** detail hydrate mocks — add `astral_job_id=None` kw so related_meteorite path does not TypeError.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_returns_agent_story \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_soft_fails_agent_story \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_object \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_soft_fail \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1769 · AST-1685

**Publish:** `origin/sub/AST-1685/AST-1769-meteorite-tab-missing-prod`.

Job detail `related_meteorite`: when reverse `astral_job_id` miss, fall back to `get_meteorite(int(source_entity_id))` if `source == "meteorite"` and sid digit. Primary: **`docs/test-bible/data/database/meteorites.md`** § AST-1691 helpers. UI tab omit-when-null unchanged (AST-1692).

| Area | Source | Component tests |
| --- | --- | --- |
| source_entity fallback (**[bug-repro]**) | `src/ui/api/api_jobs.py` | **`TestJobsRoutes::test_detail_related_meteorite_source_entity_fallback`** |

**Broken / obsolete:** none — additive resolve path; existing reverse-link / soft-fail / null asserts stay.

**Integration:** none — do not invent.

## QA test manifest

1. **[bug-repro]** `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_source_entity_fallback`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_source_entity_fallback \
  -q
```

**Pass criterion:** red on pre-fix (related_meteorite null); green after make-fix fallback lands.

---

### AST-1704 · AST-1640

**Parent:** [AST-1640 — Job source_entity parent](https://linear.app/astralcareermatch/issue/AST-1640). **Publish:** `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`.

`GET /api/jobs/:id` exposes `company_id`, `source`, `source_entity_id`, and inherited `job_link`. Primary manifest: **`docs/test-bible/core/consult.md`** § AST-1704.

| Area | Source | Component tests |
| --- | --- | --- |
| Detail parent + job_link | `src/ui/api/api_jobs.py` | **`TestAst1704JobsDetailParentFields`** |

**Broken / obsolete this pass:** none.

**Integration:** none.

**AST-1872 (pointer):** `GET /api/jobs/<id>` always includes boolean **`can_skip`** from core `job_state_admits_transition(state, "CANDIDATE_SKIPPED")` — **`TestAst1872DetailCanSkip`**. Manifest: **`docs/test-bible/core/tracker.md`** § AST-1872.

---

### AST-1974 · AST-1970

**Parent:** [AST-1970 — Jobs Navigation changes](https://linear.app/astralcareermatch/issue/AST-1970). **Publish:** `origin/sub/AST-1970/AST-1974-jobs-nav`. Backend half of the Jobs re-cut: six lists (Ready, Review, Applied, Processing, Skipped, Meteorites). Processing = complement of `JOBS_PROCESSING_EXCLUDED_STATES` (Ready + Review + Applied + Skipped, import-time disjoint guard). `view=ready|review|processing` replace `in_review|recommended|responded` (default `ready`). Applied repair-on-read loop deleted (single `job.candidate_id`-scoped read). Skip route delegates to core `candidate_skip_job` (releases a held batch claim) and logs one completion info line.

| Area | Source | Component tests |
| --- | --- | --- |
| Views + default + retired views | `src/ui/api/api_jobs.py` | `TestJobsRoutes::test_list_ready_review_and_default`, `test_retired_in_review_view_falls_through`, `test_list_processing_*` (3) |
| Applied single read (supersedes AST-1498 repair) | `src/ui/api/api_jobs.py` | `TestJobsRoutes::test_list_applied_single_scoped_read_no_repair_ast1974` |
| Skip route → core + one info line / 409 silent | `src/ui/api/api_jobs.py` | `TestJobsRoutes::test_skip_job_*` (4) |
| Real-SQLite partition / nav counts / skip / AC 5 detail | api_jobs + api_system + tracker + database | **`TestAst1974JobsPartitionRealDb`** |
| Config state model, nav, manifest, columns | `src/utils/config.py` | [`utils/config.md`](../../utils/config.md) § AST-1974 |
| Six nav counts | `src/ui/api/api_system.py` | [`api_system.md`](api_system.md) § AST-1974 |
| Core skip + facades | `src/core/tracker.py` | [`core/tracker.md`](../../core/tracker.md) § AST-1974 |
| exclude_states + meteorite `job_state` join | `src/data/database.py` | [`data/database/jobs.md`](../../data/database/jobs.md) § AST-1974 |
| Meteorites list `job_state` | `src/ui/api/api_meteorite.py` | [`api_meteorite.md`](api_meteorite.md) § AST-1974 |

**Broken / obsolete revised this pass:** `test_list_in_review_*` → processing; `test_list_recommended_and_default` → ready/review/default; `test_list_applied_includes_stem_job_null_company_candidate_id_ast1498` → single-read (AC 4 removes the repair by design); skip tests mock `candidate_skip_job`; 13 `test_config.py` tests (`IN_REVIEW_STATES` / `JOBS_IN_REVIEW_UI_SECTIONS` / `RECOMMENDED_JOB_STATES` / meteorite_section / Responded / AST-1808 snapshot exemption for `CANDIDATE_SKIPPED`); `test_api_system.py` nav count path + Jobs stub test; integration `test_candidate_nav_api.py`. Fixture: `_meteorite_schema_ensured` added to `tests/component/ui/conftest.py` + `tests/integration/conftest.py` flag resets.

**Frontend:** none here — `stateUiManifestFixture.ts`, `test_JobsInReview`, `test_JobsRecommended`, `test_StateUiContext`, `test_routes` follow **AST-1975** / **AST-1976**.

## QA test manifest

Pass criterion: every node below green. Narrowed runs only (zero-arg harness carries unrelated pre-existing reds on this tree).

1. **API views / skip / real-DB partition (AC 1–6, 8–10):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes \
  tests/component/ui/api/test_api_jobs.py::TestAst1974JobsPartitionRealDb \
  -q
```

   Expect only `TestJobsRoutes::test_put_resume_content_persists_via_tracker` red — pre-existing on `origin/dev`, unrelated.

2. **Config (AC 1, 5, 7, manifest contract):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1974JobsListPartition \
  tests/component/utils/test_config.py::TestAst479LikePassStates \
  tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig::test_score_gate_and_ui_manifests \
  tests/component/utils/test_config.py::TestAst898NewRetryQualifyHolding \
  tests/component/utils/test_config.py::TestAst1339MeteoriteNewRetryQualifyHolding::test_ui_sections_label_no_grade_field \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1057MeteoriteRecommendedSection \
  tests/component/utils/test_config.py::TestAst1155GradedRetryHoldings \
  tests/component/utils/test_config.py::TestAst1749JobsMeteoritesNav \
  tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned \
  tests/component/utils/test_config.py::TestBuildStateUiManifest \
  -q
```

3. **Nav counts (AC 1, 10):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes \
  tests/component/ui/api/test_api_system.py::TestSystemNavHelpers \
  -q
```

4. **Core skip + data + meteorite list (AC 6, 8, Meteorites `job_state`):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst1974CandidateSkipJob \
  tests/component/data/database/test_jobs.py::TestAst1974ExcludeStatesAndMeteoriteJobState \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```

5. **Integration (revised existing scenario):**

```bash
./scripts/testing/run_integration_tests.sh tests/integration -q
```

6. **Greps / builds (AC 4, 7, 9, 11, 12 — backend half):**

```bash
rg -n "candidate_id=None" src/ui/api/api_jobs.py                                   # expect nothing
rg -n "jobs/in_review|jobs/recommended|jobs/responded" src/utils/config.py src/ui/api  # expect nothing
git diff origin/dev -- src/ui/api | rg "^\+.*logger\.info"                         # expect exactly the skip line
git diff origin/dev -- src/core/tracker.py | rg "^\+.*logger\.info"                # expect nothing
python -c "import src.utils.config"                                                # exit 0
```

   AC 11 frontend paths / `npm run build` / `npm run lint` are **AST-1975**.

**Branch locks:** every added line/branch in `tracker.py`, `config.py`, `api_jobs.py`, `api_system.py` covered by the nodes above (checked with `--cov-branch` on the merged tree).

**Known pre-existing (not this ticket):** `tests/component/data/database/test_meteorites.py` fails collection on `origin/dev` (imports `METEORITE_STATES_RETENTION`, removed 2026-09-20) — hence the meteorite join test lives in `test_jobs.py`.

**Bible shasum (after publish):** `git show origin/sub/AST-1970/AST-1974-jobs-nav:docs/test-bible/ui/api/api_jobs.md | shasum` (same command for `utils/config.md`, `ui/api/api_system.md`, `ui/api/api_meteorite.md`, `core/tracker.md`, `data/database/jobs.md`, `integration/README.md`).

### AST-2067 · AST-2043

`GET|PUT /api/jobs/<jid>/artifacts/<job_catalog_key>/{versions,current}`: 404 `{"error": "Not found"}` for a missing job; PUT body 400; a candidate key on the job route → 400 `not job-scoped`; AC7 (a `job_resume` uuid or another job's uuid on the `cover_letter` route → 400, current unchanged); an unexpected error logs one ERROR line (prefixed by the job's `candidate_id`, or `-`) and returns the 500 payload; a 200 PUT logs one completion line.

**New:** **`TestAst2067JobVersionRoutes`** (14; real tracker/data on `sqlite_in_memory`, only `get_job` stubbed; new route lines fully branch-covered). Manifest: [`api_candidate.md`](api_candidate.md) § AST-2067 item 2.

### AST-2081 · AST-2046

`GET /api/jobs/<jid>/resume_structure` returns the shared editor payload for the job's effective structure (hydrated, read-only). `PUT /api/jobs/<jid>/artifacts/job_resume_structure` with body `{"job_resume_structure": {...}}` writes it through `save_job_artifact`. Both return 404 `{"error": "Not found"}` for a missing job. PUT returns 400 when the body is not a dict, and returns 400 with the `ValueError` text and no log for an invalid structure. An unexpected error logs one ERROR line (prefixed by the job's `candidate_id`, or `-`) and returns the 500 payload. Only the PUT logs a completion INFO line (Joan revision: no GET info).

**New:** **`TestAst2081JobResumeStructureRoutes`** (13; real tracker/data on `sqlite_in_memory`; `get_job`, `_candidate_id_for_job`, and `_candidate_data_for_job` stubbed). Covers AC16 (GET equals the candidate payload and writes no row) and AC15/AC18 (PUT on job A shows on A; job B and the candidate are unchanged). New route lines are fully branch-covered. Manifest: [`../../core/tracker.md`](../../core/tracker.md) § AST-2081.

### AST-2133 · AST-2130 (composed read-only JD)

Every list row (`ready` / `review` / `applied` / `processing` / `skipped` incl. virtual skips) and `GET /api/jobs/<id>` return `job_data.job_description` = `tracker.compose_job_description(job)` on a new dict (stored `job_data` never written). `PUT /api/jobs/<id>` drops `job_description` from the accepted fields: JD-only body → 400 "No valid fields"; title + JD → title persists, `job_data` unchanged.

**New:** **`TestAst2133ComposedJdResponses`** (9; real `telescope_data` rows on ui `sqlite_in_memory`), **`TestAst2133PutJdReadOnlyE2E`** (1; `seeded_db`, real tracker / data). **Revised:** `TestJobsRoutes::test_list_processing_filters_score_floor`. Manifest: [`../../core/tracker.md`](../../core/tracker.md) § AST-2133.
