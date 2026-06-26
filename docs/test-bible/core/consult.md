# Consult

**Test module:** `tests/component/core/test_consult.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/consult.py` | `tests/component/core/test_consult.py` | yes |

---

### AST-429 · AST-358

**`_render_score`** uses AST-358 three-knob math (`RUBRIC_TOTAL / V`, `grade_value` × confidence, `importance_multiplier` per rubric row). **`_rubric_to_weights`** and **`GRADE_QUALITY_LEGACY`** removed. Depends on **AST-428** config on the same sub branch stack.

| Area | Source | Component tests |
| --- | --- | --- |
| Scored grading + importance lookup | `src/core/consult.py` (`_render_score`, `_importance_for_label`) | `tests/component/core/test_consult.py` (`TestRenderScore`, `TestRenderScoreBranches`, `TestRubricHelpers`) |
| V==0 / all no-signal rows | `src/core/consult.py` (`_render_score`) | `tests/component/core/test_consult.py` (`TestRemainingConsultBranches::test_render_score_with_only_no_signal_rows`) |

---

### AST-466 · AST-467 · AST-468 · AST-376

Orchestration literals for gazer steps live in **`GAZER_CONFIG`** (`validate_title` inline-only, **`fetch_jd`**, **`gaze`** error_state). Job consult scored steps carry pass/fail/error, **`save_prefix`**, **`pass_threshold`**, **`requires_company`**, JD/qualify thresholds, and **`fallback_batch_size`** on **`TASK_CONFIG`** (`qualify_job_listings`, **`evaluate_jd`**, **`grade_do`**, **`grade_get`**, **`grade_like`**). **`src/core/consult.py`** and **`src/core/gazer.py`** read **`TASK_CONFIG` / `GAZER_CONFIG` directly** — dispatch and catalog share **`grade_*`** strings (**AST-736** / **AST-748**; **`_consult_orchestration`** is direct **`TASK_CONFIG`** lookup). **`CONSULT_CONFIG`** removed (AST-468 Stage 6). **`RUBRIC_ARTIFACT_KEYS`** derives from the five **`TASK_CONFIG`** **`rubric_artifact`** fields. **`pass_threshold`** vs **`dispatch_task.score_floor`**: see **`docs/ASTRAL_CODE_RULES.md`** §2.1 (different lifecycle — not a numeric override).

| Area | Source | Component tests |
| --- | --- | --- |
| **`GAZER_CONFIG`**, **`RUBRIC_ARTIFACT_KEYS`** | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestAst309CoverLetterTaskConfig`** where applicable, **`TestAst479LikePassStates`**); branch lock for **`config.py`** via full component run |
| **`TASK_CONFIG` / `GAZER_CONFIG` orchestration (**AST-467**)** | `src/core/consult.py`, `src/core/gazer.py` | `tests/component/core/test_consult.py` ( **`monkeypatch` / assertions on `TASK_CONFIG` — `grade_*` dispatch via **`_consult_orchestration`**); `test_gazer.py` for **`validate_title_batch`**, **`fetch_jd_batch`**, **`process_gazer_batch`** ( **`GAZER_CONFIG`** ). |
| Dispatch resolution helpers (**AST-468**) | `src/core/dispatcher.py`, `src/data/database.py`, `src/ui/api/api_admin.py` | `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_admin.py` |

Sibling **AST-468** dispatch helpers documented in **§7.13x**.

Manifest default ( **`test-astral`** on publish tip — consult/config scope): `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py tests/component/core/test_consult.py tests/component/core/test_gazer.py tests/component/core/test_dispatcher.py tests/component/core/test_agent.py`.

**Harness:** `./scripts/testing/run_component_tests.sh` with trailing paths forwards them to **`pytest`** (narrow selection + same **`--cov=src`** / JSON report wiring). **`check_per_file_coverage.py`** (**`LOCKED_AT_100`**) runs **only** with zero args (full **`tests/component`** selection); narrowed manifest calls skip that gate because branch rows are incomplete for untouched locked modules.

---

### AST-534 · AST-535 · AST-533

**AST-533 (parent):** Scheduled Actions **Run** must execute the **`dispatch_task.task_key`** on the row — **`trigger_state`** claims entities only. **AST-534**: job consult + artifact entry via row **`task_key`**. **AST-535**: triple unique **`(candidate_id, task_key, trigger_state)`** and company roster **`TO_WATCH`** trio routing (`find_job_page`, `select_job_page`, `parse_job_list` each run their task). **`_INPUT_STATE_TO_TASK`** is not dispatch routing.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-534** | Row **`task_key`** drives first hop; **`anticipate_scan`** @ **`BUILD_ARTIFACTS`** does not enter **`contemplate_job`** / cover letter when unlinked | `src/core/dispatcher.py`, `src/core/consult.py`, `src/core/agent.py` | `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch` |
| **AST-535** | Triple unique schema; **`TO_WATCH`** rows route by row **`task_key`**; admin 409 names triple | `src/data/database.py`, `src/core/roster.py`, `src/core/consult.py`, `src/ui/api/api_admin.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst535DispatchTaskTripleUnique`; `tests/component/core/test_roster.py::TestAst535ToWatchDispatchTaskKeyRouting`; `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast535_create_dispatch_task_triple_unique_409` |

**AST-534** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult
```

**AST-535** narrowed run (includes **AST-534** job forward regression — `test_ast534_forwards_dispatch_task_key_to_consult` must stay green after product fix on **`dispatcher._run_unified`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst535DispatchTaskTripleUnique \
  tests/component/core/test_roster.py::TestAst535ToWatchDispatchTaskKeyRouting \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast535_create_dispatch_task_triple_unique_409 \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult
```

---

### AST-603 · AST-602

**AST-603** routes **`prefilter_company`** model responses through shared **`consult._normalize_rubric_task_response`** (dict JSON, letter-pipe, JSON string, compact encoded + **`JOB:`** / **`CULT:`** tails) before **`do_task`** schema validation; roster hydrates grade **`reason`** via **`_hydrate_grade_reasons_from_rubric`**. Preserves **AST-507** pass/fail/score semantics and inflow **PREFILTER_*** vs legacy **TO_WATCH** / **IGNORE** mapping. Output type **`grades_encoded_prefilter_links`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-603** | Shared rubric normalizer; **`do_task`** pre-decode skip for rubric encoded tasks; roster hydration + link list persistence | `src/core/consult.py`, `src/core/agent.py`, `src/core/roster.py`, `src/utils/config.py` | `tests/component/core/test_agent.py::TestAst603RubricNormalize`; `tests/component/core/test_roster.py::TestAst603ConsultParityHydration`; `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded`; **AST-507** regression rows in **§7.13zh** |

**AST-603** narrowed run (includes **AST-507** prefilter smoke):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst603RubricNormalize \
  tests/component/core/test_roster.py::TestAst603ConsultParityHydration \
  tests/component/core/test_roster.py::TestAst507EncodedPrefilter \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig
```

---

### AST-697 · AST-696

**AST-697** fixes **prefilter_company** prompt contract and decode: **`stringify_response_schema`** shows bracket **link_set** tails (`000|ERC2|MEA3|PGA2|[13]|[3,6,19]`); **`_apply_prefilter_encoded_link_meta`** maps positional bracket tails and existing **`JOB:`** / **`CULT:`** prefixes onto **`possible_job_links`** / **`culture_links_to_explore`**. **`_decode_payload`** delegates to the shared helper. Roster persist unchanged (**AST-603**). Grades-only encoded lines omit link keys.

| Area | Source | Component tests |
| --- | --- | --- |
| Bracket **link_set** decode + prefix precedence | `src/core/consult.py` (`_apply_prefilter_encoded_link_meta`) | `tests/component/core/test_agent.py::TestAst697PrefilterBracketLinkDecode`; `tests/component/core/test_agent.py::TestAst603RubricNormalize::test_lovable_encoded_line_with_bracket_tails` |
| **`_decode_payload`** wiring | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst697PrefilterBracketLinkDecode` |
| **`stringify_response_schema`** bracket example | `src/utils/config.py` | `tests/component/utils/test_config.py::TestStringifyResponseSchema::test_prefilter_company_schema_shows_bracket_link_set_tails` |

**AST-697** narrowed run (includes **AST-603** prefix-tail regression):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestStringifyResponseSchema::test_prefilter_company_schema_shows_bracket_link_set_tails \
  tests/component/core/test_agent.py::TestAst697PrefilterBracketLinkDecode \
  tests/component/core/test_agent.py::TestAst603RubricNormalize \
  tests/component/core/test_roster.py::TestAst603ConsultParityHydration \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded
```

---

### AST-699 · AST-696

**UAT fix:** **`_normalize_rubric_task_response`** gates **`_decode_payload`** with **`_should_decode_as_encoded_line`** — position-prefixed letter-pipe lines like **`0|A|B|A|[35]|[22,34,39,52,53]`** fall through to **`_job_from_letter_pipe`** instead of misrouting on **`^\d{1,3}\|`** alone. True encoded lines (**`000|RCA3|…`**) unchanged (**AST-697**).

| Area | Source | Component tests |
| --- | --- | --- |
| Position-prefixed letter-pipe bracket tails | `src/core/consult.py` (`_should_decode_as_encoded_line`, `_normalize_rubric_task_response`) | `tests/component/core/test_agent.py::TestAst699LetterPipePositionPrefix::test_position_prefixed_letter_pipe_bracket_tails` |
| Bare letter-pipe bracket tails (regression) | `src/core/consult.py` | `tests/component/core/test_agent.py::TestAst699LetterPipePositionPrefix::test_bare_letter_pipe_bracket_tails` |
| Encoded vs letter routing helper | `src/core/consult.py` | `tests/component/core/test_agent.py::TestAst699LetterPipePositionPrefix::test_should_decode_as_encoded_line_routing` |
| Encoded bracket tails unchanged (**AST-697**) | `src/core/consult.py`, `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst603RubricNormalize::test_lovable_encoded_line_with_bracket_tails`; `TestAst697PrefilterBracketLinkDecode` |
| Numeric letter-pipe tails unchanged (**AST-603**) | `src/core/consult.py` | `tests/component/core/test_agent.py::TestAst603RubricNormalize::test_letter_pipe_parses_grades_and_link_indices` |

**AST-699** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_agent.py::TestAst699LetterPipePositionPrefix \
  tests/component/core/test_agent.py::TestAst603RubricNormalize::test_lovable_encoded_line_with_bracket_tails \
  tests/component/core/test_agent.py::TestAst603RubricNormalize::test_letter_pipe_parses_grades_and_link_indices \
  -q
```

---

### AST-719 · AST-716

**AST-719:** Company **`entity_type`** dispatch with **`dispatch_task_key=fetch_job_pages`** routes to **`fetch_job_pages_batch`** (not **`run_company_task`**). Returns normalized summary counts like **`fetch_website`**.

| Area | Source | Component tests |
| --- | --- | --- |
| **`fetch_job_pages`** routing | `src/core/consult.py` (`run_consult_task`) | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_job_pages_batch` |

Gazer batch manifest: **`docs/test-bible/core/gazer.md`** (**AST-719**).

---

### AST-701 · AST-700

**AST-701:** Company **`entity_type`** dispatch with **`dispatch_task_key=fetch_website`** routes to **`fetch_website_batch`** (not **`run_company_task`** / **`prefilter_company`**). Returns normalized **`total_processed` / `total_passed` / `total_failed` / `total_errors`**.

| Area | Source | Component tests |
| --- | --- | --- |
| **`fetch_website`** routing | `src/core/consult.py` (`run_consult_task`) | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_website_batch` |

Gazer batch manifest: **`docs/test-bible/core/gazer.md`** (**AST-701**).

---

### AST-702 · AST-700

**AST-702:** **`dispatch_task_key=prefilter`** routes to **`prefilter_company_batch`** with **`skipped`** folded into **`total_errors`**.

| Area | Source | Component tests |
| --- | --- | --- |
| **`prefilter`** batch routing | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch` |

Roster batch runner: **`docs/test-bible/core/roster.md`** (**AST-702**).

---

### AST-703 · AST-700

**UAT fix:** Admin **`GET /api/admin/dispatch_tasks`** no longer 500 when legacy **`prefilter`** rows existed at both **`WEBSITE_FOUND`** and **`WEBSITE_FOUND_RETRY`** — migration DELETE-before-UPDATE in **`_ensure_dispatch_task_schema`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Migration collision | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision` |

**AST-703** narrowed run: **`docs/test-bible/core/roster.md`** (**AST-703**).

---

### AST-707 · AST-700

**UAT fix:** **`EMBEDDED_COMPANY_PREFILTER_CRITERIA`** in **`config.py`** supplies global **RC** (Reality Check); **`_rubric_criteria_from_cd`** prepends embedded rows for **`company_prefilter`**; **`_lookup_rubric_reason_for_grade`** and **`_importance_for_label`** match criterion **code** or **label** so batch prefilter hydration succeeds when the candidate artifact omits **RC**.

| Area | Source | Component tests |
| --- | --- | --- |
| Embedded RC registry | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig` |
| Merge + code-aware lookup | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRubricHelpers::test_merges_embedded_rc_for_company_prefilter`; `TestRubricHelpers::test_hydrates_rc_by_code_without_artifact_row`; `TestRubricLookup::test_matches_criterion_by_code`; `TestImportanceForLabelBranches::test_importance_matches_by_code` |
| Batch hydration regression | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration::test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact` |

**AST-707** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig \
  tests/component/core/test_consult.py::TestRubricHelpers::test_merges_embedded_rc_for_company_prefilter \
  tests/component/core/test_consult.py::TestRubricHelpers::test_hydrates_rc_by_code_without_artifact_row \
  tests/component/core/test_consult.py::TestRubricLookup::test_matches_criterion_by_code \
  tests/component/core/test_consult.py::TestImportanceForLabelBranches::test_importance_matches_by_code \
  tests/component/core/test_roster.py::TestAst707EmbeddedRcBatchHydration::test_batch_prefilter_hydrates_embedded_rc_when_missing_from_artifact
```

---

### AST-619 · AST-543

**AST-543 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/consult.py`** — Pattern-A **`_run_batch_consult`** per-job index headers + **`|`** detail before batch summaries; **`qualify_job_listings`** / **`evaluate_jd_batch`** wrappers; encoded **`consult_do`** / **`consult_get`** / **`consult_like`** batches; single-job **`render_verdict`**; rubric grading helpers **`_render_pass_fail`**, **`_render_score`**, **`_apply_render_verdict_decoded_job`**; retire hand-rolled **`[DEBUG]`** and **`_LOG_DEBUG`** guards in touched blocks. **No Betty log-string tests** (parent + child explicit); Radia enforces instrumentation on review.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-619** | Contract debug across batch loops, grading branches, qualify/evaluate, encoded consult batches, `render_verdict` | `src/core/consult.py` | **`tests/component/core/test_consult.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-619** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_consult.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_consult.py
```

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `_render_pass_fail` / `_render_score` grading branches | **`TestRenderPassFail`**, **`TestRenderPassFailDebug`**, **`TestRenderScore`**, **`TestRenderScoreBranches`** |
| `_run_batch_consult` batch start, per-job indices, envelope failure | **`TestRunBatchConsult`**, **`TestRunBatchConsultBranches`** |
| `qualify_job_listings` / `evaluate_jd_batch` Pattern-A wrappers | **`TestQualifyJobListings`**, **`TestEvaluateJdBatch`** |
| `render_verdict` single-job decode path | **`TestRenderVerdict`** |
| Encoded DO/GET/LIKE batch routing | **`TestAst503`**, **`TestRunConsultTask`** consult batch rows |
| `debug=False` unchanged | **`TestRemainingConsultBranches::test_runs_without_debug_logging`**; full-file branch lock |

**Betty test fix (AST-619):** **`enable_debug_log`** fixture uses **`logger.set_debug_flag(True)`** — product removed **`_LOG_DEBUG`** / **`isEnabledFor`** guards in favor of **`debug_detail`**.

### AST-726 (parent AST-717)

**Scope:** Latest-only rubric outcome fields on job blobs — always persist `{prefix}_notes` (empty clears stale); `qualify_job_listings` saves `joblist_score` when scored.

| Area | Source | Component tests |
| --- | --- | --- |
| `{prefix}_notes` always written (empty clears) | `src/core/consult.py` (`_apply_render_verdict_decoded_job`) | `tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes::test_apply_render_verdict_always_persists_notes_including_empty` |
| `joblist_score` on pass/fail | `src/core/consult.py` (`qualify_job_listings`) | `TestAst726LatestOnlyConsultOutcomes::test_qualify_job_listings_persists_joblist_score_on_pass`; `::test_qualify_job_listings_persists_joblist_score_on_fail` (grades only, no score on F fail) |

Entity ref upsert + modal story: **`docs/test-bible/data/database/agent_responses.md`**, **`docs/test-bible/core/roster.md`** (**AST-726**).

**AST-726** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst726LatestOnlyConsultOutcomes \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-723 · AST-378

Runtime rubric load cutover: **`_rubric_criteria_for_cfg`** + **`rubric_criteria_for_task`** replace **`_rubric_criteria_from_cd`** artifact reads. **`TestRubricHelpers`** revised for table-backed criteria.

| Area | Source | Component tests |
| --- | --- | --- |
| Table-backed rubric helpers + grade hydration | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRubricHelpers` |
| Roster prefilter reads | `src/core/roster.py` | existing **AST-507** / **AST-603** roster regression rows (no new file) |


### AST-733 · AST-728

**`qualify_job_listings`** passing path: when **`tracker.initialize_job`** returns **`False`** (identity collision), skip **`save_job_data`** and state transition; batch returns **`fail_state`** for that job and continues without raising.

| Area | Source | Component tests |
| --- | --- | --- |
| Qualify batch collision wiring | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst733QualifyIdentityCollision` |

**AST-733** narrowed run (full manifest):

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_jobs.py::TestAst733JobIdentityHelpers \
  tests/component/core/test_tracker.py::TestAst733InitializeJobCollision \
  tests/component/core/test_consult.py::TestAst733QualifyIdentityCollision \
  tests/component/core/test_tracker.py::TestInitializeJob \
  tests/component/core/test_consult.py::TestQualifyJobListings::test_runs_debug_and_passing_job_path \
  -q
```

### AST-748 · AST-736

**AST-736 runtime cutover:** `consult_*` → `grade_*` dispatch routing in **`run_consult_task`**, **`render_verdict`**, **`grade_do_batch` / `grade_get_batch` / `grade_like_batch`**; **`_consult_orchestration`** direct **`TASK_CONFIG`** lookup (no alias). Prerequisite **AST-747** config on publish tip.

| Area | Source | Component tests |
| --- | --- | --- |
| Graded batch routing + `render_verdict` | `src/core/consult.py` | **`TestRunConsultTask`**, **`TestAst534DispatchTaskKeyHonesty`**, **`TestRenderVerdict`** (revised `grade_*` keys) |
| DB row rename | `src/data/database.py` | **`TestAst748ConsultToGradeDispatchMigration`** (`test_dispatch_tasks.py`) |

**AST-748** narrowed run (with **AST-747** config on tip):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst748ConsultToGradeDispatchMigration \
  tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_grade_do_batch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_uses_default_score_floor_for_scored_states \
  -q
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness until siblings integrated.

---

### AST-797 · AST-794

Runtime cutover after **AST-796**: **`fetch_jd`** routing via **`fetch_jd_batch`**; **`validate_title_batch`** inline inside **`qualify_job_listings`** for **NEW** jobs; **`validate_title`** / **`scrape_jd`** retired from **`run_consult_task`**; qualify primary dispatch @ **NEW** with **VALID_TITLE_RETRY** companion row (migration).

| Area | Source | Component tests |
| --- | --- | --- |
| Inline title screen + routing | `src/core/consult.py` | `TestAst797QualifyInlineValidateTitle`; `TestRunConsultTaskRoutes::test_routes_fetch_jd_batch`; `TestRunConsultTask::test_validate_title_dispatch_key_unhandled_returns_zero` |
| DB migration | `src/data/database.py` | `TestAst797DispatchKeyCutoverMigration` |
| Config qualify @ NEW | `src/utils/config.py` | `TestAst797ConfigRuntimeCutover` |
| Gazer rename | `src/core/gazer.py` | `TestFetchJdBatch` (+ debug path classes) |
| Tracker coat-check | `src/core/tracker.py` | existing self-heal tests (monkeypatch **`fetch_jd_batch`**) |
| Dispatcher claim @ NEW | `src/core/dispatcher.py` | `TestRunUnified::test_ast641_primary_job_trigger_passes_union_claim_states`; `test_qualify_valid_title_claim_without_score_floor` |
| Admin adhoc | `src/ui/api/api_admin.py` | `TestAdhocHelpers::test_trigger_state_helpers` |

**AST-797** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst797DispatchKeyCutoverMigration \
  tests/component/utils/test_config.py::TestAst797ConfigRuntimeCutover \
  tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_fetch_jd_batch \
  tests/component/core/test_gazer.py::TestFetchJdBatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_primary_job_trigger_passes_union_claim_states \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers \
  -q
```

---

### AST-789 · AST-788

**AST-788 (parent):** BUILD_ARTIFACTS compound substates do not auto-graduate per hop — terminal batch exit in **`consult._run_job_artifact_entry_batch`** promotes to **`CANDIDATE_REVIEW`** after persist gate passes. **AST-789** extracts **`_try_graduate_artifact_job_to_candidate_review`** (fresh DB persist read via **`job_has_persisted_resume_body(..., None)`**, structured failure reasons, AST-538 Style D debug); wires batch loop; graduation stays in **`consult.py`** only (not **`agent.py`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Terminal graduation helper + batch wiring | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst789TerminalGraduation` |
| Full-chain / first-hop regression | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::{test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job,test_artifact_entry_batch_empty_persist_releases_claim}`; `TestAst789TerminalGraduation::test_artifact_entry_batch_graduates_on_anticipate_scan_first_hop` |
| Persist / transition failure paths | `src/core/consult.py` | `TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_releases_claim`; `TestAst789TerminalGraduation::test_artifact_entry_batch_transition_failure_releases_claim` |
| AST-597 per-hop regression (unchanged) | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` |

**AST-789** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst789TerminalGraduation \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-803 · AST-788

**AST-803:** Flat **`BUILD_ARTIFACTS`** + **`ERROR_BUILD_ARTIFACTS`**; resume hops carry **`task_type: CHAIN`**; **`do_chain_for_job`** + **`_run_build_artifacts_chain_batch`** replace compound per-hop transitions (**AST-595/597**) and **`run_resume_artifact_chain_for_job`** / **`_try_graduate_artifact_job_to_candidate_review`** (**AST-789**). Job stays on flat **`BUILD_ARTIFACTS`** during hops; terminal **`CANDIDATE_REVIEW`** via **`_chain_graduate_to_candidate_review`**; retry hop failure releases claim; hard missing-job/candidate → **`ERROR_BUILD_ARTIFACTS`**. Legacy **`BUILD_ARTIFACTS.<hop>`** rows still readable for in-flight resume.

| Area | Source | Component tests |
| --- | --- | --- |
| Chain entry + helpers | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst803ChainHelpers` |
| **`do_chain_for_job`** graduation / hard error | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst803ChainGraduation` |
| Batch wiring + retry release | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch` |
| Dispatch row honesty (flat + legacy trigger) | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty` |
| Flat config + CHAIN **`task_type`** | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch`; `TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like`; `TestBuildStateUiManifest::{test_ast522_recommended_manifest_sections_and_phase_columns,test_ast562_recommended_primary_actions_by_state,test_ast562_recommended_prior_states_allow_cancel_from_build}`; `TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged`; `TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort` |
| Generate/cancel flat state | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::{test_start_artifact_build_from_recommended,test_cancel_from_mid_hop_compound_state,test_cancel_rejects_wrong_state}` |
| Dispatcher flat trigger + legacy claim | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::{test_ast534_forwards_dispatch_task_key_to_consult,test_ast596_resume_hop_mismatch_skips_claim}` |
| Admin dispatch validation | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry` |
| Jobs API generate/cancel | `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default`; `TestAst562GenerateCancelRoutes::{test_generate_artifacts_happy_path,test_cancel_artifact_build_happy_path}` |
| Mid-chain hydration (no per-hop state transition) | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` |

**AST-803** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst803ChainGraduation \
  tests/component/core/test_consult.py::TestAst803ChainHelpers \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast596_resume_hop_mismatch_skips_claim \
  tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-803 · AST-788

**AST-803:** Flat **`BUILD_ARTIFACTS`** + **`ERROR_BUILD_ARTIFACTS`**; resume hops carry **`task_type: CHAIN`**; **`do_chain_for_job`** + **`_run_build_artifacts_chain_batch`** replace compound per-hop transitions (**AST-595/597**) and **`run_resume_artifact_chain_for_job`** / **`_try_graduate_artifact_job_to_candidate_review`** (**AST-789**). Job stays on flat **`BUILD_ARTIFACTS`** during hops; terminal **`CANDIDATE_REVIEW`** via **`_chain_graduate_to_candidate_review`**; retry hop failure releases claim; hard missing-job/candidate → **`ERROR_BUILD_ARTIFACTS`**. Legacy **`BUILD_ARTIFACTS.<hop>`** rows still readable for in-flight resume.

| Area | Source | Component tests |
| --- | --- | --- |
| Chain entry + helpers | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst803ChainHelpers` |
| **`do_chain_for_job`** graduation / hard error | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst803ChainGraduation` |
| Batch wiring + retry release | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch` |
| Dispatch row honesty (flat + legacy trigger) | `src/core/consult.py` | `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty` |
| Flat config + CHAIN **`task_type`** | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch`; `TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like`; `TestBuildStateUiManifest::{test_ast522_recommended_manifest_sections_and_phase_columns,test_ast562_recommended_primary_actions_by_state,test_ast562_recommended_prior_states_allow_cancel_from_build}`; `TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged`; `TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort` |
| Generate/cancel flat state | `src/core/tracker.py` | `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::{test_start_artifact_build_from_recommended,test_cancel_from_mid_hop_compound_state,test_cancel_rejects_wrong_state}` |
| Dispatcher flat trigger + legacy claim | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::{test_ast534_forwards_dispatch_task_key_to_consult,test_ast596_resume_hop_mismatch_skips_claim}` |
| Admin dispatch validation | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry` |
| Jobs API generate/cancel | `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default`; `TestAst562GenerateCancelRoutes::{test_generate_artifacts_happy_path,test_cancel_artifact_build_happy_path}` |
| Mid-chain hydration (no per-hop state transition) | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` |

**AST-803** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst803ChainGraduation \
  tests/component/core/test_consult.py::TestAst803ChainHelpers \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast596_resume_hop_mismatch_skips_claim \
  tests/component/utils/test_config.py::TestAst803FlatBuildArtifactsChainDispatch \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-817 · AST-815

**AST-817 (child):** Remove stale **`vet_inflow_discovery`** early-return in **`run_consult_task`** company branch that mis-routed to **`run_inflow_discovery_batch`**. Company vet dispatch falls through to **`run_company_task`** → **`vet_inflow_discovery_company`** (**AST-776**). Surgical **`consult.py`** deletion only — roster/config unchanged.

**Manifest focus (existing coverage — no new tests):**

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Company vet consult → **`run_company_task`** (not discovery batch) | `src/core/consult.py` | `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` |
| 2 | **`vet_inflow_discovery_company`** outcomes + routing (**AST-776** regression) | `src/core/roster.py` | `::TestAst776VetInflowDiscoveryCompany` |
| 3 | Discovery batch no inline vet (**AST-775** regression) | `src/core/roster.py` | `::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors` |
| 4 | Config company entity (**AST-776** regression) | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task` |

**AST-817** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task \
  tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-822 · AST-815 (UAT bug)

**AST-822 (UAT bug):** Company **`vet_inflow_discovery`** consult guard routes to **`vet_inflow_discovery_company_batch`** (full claimed entity list) before **`run_company_task`** fallback — replaces **AST-817**/`819` **`run_company_task`** consult path for dispatch batching.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Consult vet → batch runner (not discovery batch / not per-entity warm) | `src/core/consult.py` | `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` |
| 2 | Batch assembly + **`hit_index`** decode | `src/core/roster.py` | `::TestAst822VetInflowDiscoveryBatch` |
| 3 | Single-company wrapper (**AST-776** regression) | `src/core/roster.py` | `::TestAst776VetInflowDiscoveryCompany` |

**Regression note:** **AST-817** manifest consult line updated in **AST-822** — batch mock replaces **`run_company_task`** expectation.

---

---

### AST-823 · AST-821

**AST-823 (UAT bug):** **`run_consult_task`** company branch routes **`dispatch_task_key`** in **`("prefilter", "prefilter_company")`** to **`prefilter_company_batch`** — legacy mis-keyed dispatch rows no longer fall through to **`run_company_task`** on **HOMEPAGE_READY**. Idempotent **`dispatch_task`** migration retargets **`prefilter_company`** agent-key rows and stale **`batch_call_mode` / `trigger_state`** on company prefilter rows (**AST-703** DELETE-before-UPDATE order preserved).

| Area | Source | Component tests |
| --- | --- | --- |
| **`prefilter`** batch routing (regression) | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch` |
| Legacy **`prefilter_company`** dispatch key | `src/core/consult.py` | `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch_legacy_dispatch_key` |
| Batch runner unchanged | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch` |
| Dispatcher union claim | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states` |
| Migration retarget | `src/data/database.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst823PrefilterDispatchMigration` |

**Broken / obsolete (Betty revision):** **`TestAst702PrefilterCompanyBatch::test_batch_pass_and_fail_counts`** — batch runner loads rubric via **`rubric_criteria_for_task(astral_candidate_id, …)`**; test stubs lookup with embedded **RC** + sets **`astral_candidate_id`** in ctx.

Regression: **`TestAst702PrefilterDispatchMigration`**, **`TestAst703PrefilterMigrationUniqueCollision`** (**AST-702** / **AST-703**).

**AST-823** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch_legacy_dispatch_key \
  tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states \
  tests/component/data/database/test_dispatch_tasks.py::TestAst823PrefilterDispatchMigration \
  tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-765 · AST-757 (SUNSET — documentation)

**RETIRED (AST-757):** Boards channel removed from product (**AST-765**) and schema (**AST-766**). No active boards manifest obligations. See **`docs/ASTRAL_CODE_RULES.md` §3.7**.
