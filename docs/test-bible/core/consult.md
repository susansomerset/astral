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

Orchestration literals for gazer steps live in **`GAZER_CONFIG`** (`validate_title`, `scrape_jd`, **`gaze`** error_state). Job consult scored steps carry pass/fail/error, **`save_prefix`**, **`pass_threshold`**, **`requires_company`**, JD/qualify thresholds, and **`fallback_batch_size`** on **`TASK_CONFIG`** (`qualify_job_listings`, **`evaluate_jd`**, **`grade_do`**, **`grade_get`**, **`grade_like`**). **`src/core/consult.py`** and **`src/core/gazer.py`** read **`TASK_CONFIG` / `GAZER_CONFIG` directly** (`consult_*` dispatch keys → **`grade_*`** orchestration via **`_consult_orchestration`** in consult). **`CONSULT_CONFIG`** removed (AST-468 Stage 6). **`RUBRIC_ARTIFACT_KEYS`** derives from the five **`TASK_CONFIG`** **`rubric_artifact`** fields. **`pass_threshold`** vs **`dispatch_task.score_floor`**: see **`docs/ASTRAL_CODE_RULES.md`** §2.1 (different lifecycle — not a numeric override).

| Area | Source | Component tests |
| --- | --- | --- |
| **`GAZER_CONFIG`**, **`RUBRIC_ARTIFACT_KEYS`**, board registry layout | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestBoardRegistryAst457`**, **`TestAst309CoverLetterTaskConfig`** where applicable, **`TestAst479LikePassStates`**); branch lock for **`config.py`** via full component run |
| **`TASK_CONFIG` / `GAZER_CONFIG` orchestration (**AST-467**)** | `src/core/consult.py`, `src/core/gazer.py` | `tests/component/core/test_consult.py` ( **`monkeypatch` / assertions on `TASK_CONFIG` — `consult_*` dispatch → **`grade_*`** orch via **`_consult_orchestration`**); `test_gazer.py` for **`validate_title_batch`**, **`scrape_jd_batch`**, **`process_gazer_batch`** ( **`GAZER_CONFIG`** ). **`TestProcessGazeBoardBatch`** is **`§7.13q`** / boards spine (**`process_gaze_board_batch`**) — if that symbol is absent on your tip, rerun gazer narrowly with **`pytest tests/component/core/test_gazer.py -k 'not ProcessGazeBoardBatch'`** alongside consult before asserting full-file green. |
| Dispatch resolution helpers (**AST-468**) | `src/core/dispatcher.py`, `src/data/database.py`, `src/ui/api/api_admin.py` | `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_admin.py` |
| Board-sourced pipeline still sees same states | `src/core/tracker.py`, consult + gazer | `tests/component/core/test_board_sourced_qualify_evaluate.py` |

Sibling **AST-468** dispatch helpers documented in **§7.13x**.

Manifest default ( **`test-astral`** on publish tip — consult/config scope; avoids unrelated **`origin/dev`** board integration gaps): `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py tests/component/core/test_consult.py tests/component/core/test_gazer.py tests/component/core/test_dispatcher.py tests/component/core/test_agent.py`.

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
