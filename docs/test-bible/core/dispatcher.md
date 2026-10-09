# Dispatcher

**Test module:** `tests/component/core/test_dispatcher.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py` | yes |

---

### AST-458 · AST-471 · AST-379 (historical — SUNSET AST-757)

**RETIRED (AST-757):** Astral Boards product and schema removed (**AST-765**, **AST-766**). No active manifest. Revival SHAs and rationale: **`docs/ASTRAL_CODE_RULES.md` §3.7**. Historical plans: **`docs/features/boards/`**.

---

### AST-501 · AST-500

**Parent:** **`origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs`** is assembled by **`rollup-child`** from **`origin/sub/AST-500/*`** in dependency order; Betty publishes bible manifests to **`sub/*` only**.

| Child | Behavior | Sources | Manifest tests (extend per child as Betty publishes) |
| --- | --- | --- | --- |
| **AST-501** — single-call batches for **`qualify_job_listings`** + **`evaluate_jd`**, envelope-first decode | **`_run_unified`** `batch_call_mode=1`; **`do_task`** strict envelope (**`_strict_encoded_batch_consult_envelope_err`**) | `src/core/dispatcher.py`, `src/core/agent.py`, `src/core/consult.py`, `src/utils/config.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities`; **`TestDoTask`**: **`test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope`**, **`test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object`** |
| **AST-502** | Multi-chunk cache-warm exhaustion / parallel follow-on chunks + **`batch_chunk_index`** dedupe suffix | `src/core/dispatcher.py`; `consult.py`; `database.py`; `tracker.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails`; **`test_ast502_two_chunks_skips_sleep_when_delay_zero`** |
| **AST-503** | DO / GET / LIKE batch `_run_batch_consult` parity; `grade_*` strict envelope parity with AST-501 | `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/agent.py` | `tests/component/core/test_agent.py::TestDoTask::{test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope,test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object}`; `tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_grade_do_batch` |

**AST-501** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object
```

**AST-501 + AST-502** dispatcher slice:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_two_chunks_skips_sleep_when_delay_zero \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object
```

**AST-503** graded batch envelope + PASSED_JD routing (extends AST-501 DO path):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object \
  tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_grade_do_batch
```

---

### AST-615 · AST-540

**AST-540 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/dispatcher.py`** orchestration — task start, per-entity claim index/detail, loop drain iterations, skip/guard early exits, batch-end summaries (after per-index detail), unchanged **debug** passthrough to consult. **No Betty log-string tests** (parent + child explicit); plan Stage 6 is manual UAT spot-check only. **AST-557** representative **inflow_discovery** instrumentation is generalized to all task keys in **AST-615**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-615** | Generalize AST-557 inflow-only debug gates to all dispatcher paths; retire `[DEBUG]` in touched blocks; `_dispatch_entity_identifier` helper | `src/core/dispatcher.py` | **`tests/component/core/test_dispatcher.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-615** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_dispatcher.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py
```

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `_run_unified` claim / chunk / batch-call / network skip | **`TestRunUnified`** (`test_returns_zero_without_debug_logging`, `test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails`, inflow rows) |
| `_run_dispatch_loop` min_count / drain / max_runs / zero processed | **`TestRunDispatchLoop`** |
| `_dispatch_one` scheduler handoff | **`TestDispatchOne`** |
| `_run_task` debug=False passthrough | **`TestRunTask::test_runs_without_debug_logging`** |
| `_check_circuit_breaker` | **`TestCircuitBreaker`** |

---

### AST-765 · AST-757 (SUNSET — documentation)

**RETIRED (AST-757):** Boards channel removed from product (**AST-765**) and schema (**AST-766**). No active boards manifest obligations. See **`docs/ASTRAL_CODE_RULES.md` §3.7** and monolith **`docs/ASTRAL_TEST_BIBLE.md`** §7.13 boards (sunset).


### AST-814 · AST-813

**AST-814:** Inject **`ctx["inflow_discovery_freq_hrs"]`** from dispatch row before consult; debug skip cites row **`freq_hrs`** in eligibility detail.

| Behavior | Sources | Manifest tests |
| --- | --- | --- |
| Debug skip cites **`freq_hrs=`** when all terms fresh | `src/core/dispatcher.py`, `src/data/database.py` | **`TestAst814InflowDiscoveryDebug::test_skip_cites_freq_hrs_when_all_terms_fresh`** |

**Builds on:** **AST-802** eligibility debug path.

### AST-802 · AST-801

**AST-802:** When **`inflow_discovery`** dispatch loop skips for **`available < min_count`** at first iteration with **`debug=True`**, emit eligibility reason via **`database.describe_candidate_inflow_discovery_eligibility`** → **`logger.debug_detail`**. Narrow exception to **AST-615** no log-string policy — **`eligibility:`** substring only.

| Behavior | Sources | Manifest tests |
| --- | --- | --- |
| Skip debug reason line | `src/core/dispatcher.py`, `src/data/database.py` | **`TestAst802InflowDiscoveryDebug::test_skip_emits_eligibility_reason_when_debug_true`** |

**AST-802** narrowed pytest (with data-layer items — see **`data/database/dispatch_tasks.md`**):

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_dispatcher.py::TestAst802InflowDiscoveryDebug \
  -q
```

---

### AST-841 · AST-838

**AST-838 (parent):** Execution History Level filter (**AST-840**). **AST-841:** Align **inflow_discovery** (and all dispatch tasks sharing **`_dispatch_one`**) ledger terminal status with **ERROR**/**WARNING** **`app_log`** rows — Susan can triage FAILED/INTERRUPTED runs and COMPLETED-with-errors without INFO-only exports.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-841** | **`_dispatch_one` finally** — ERROR on FAILED/INTERRUPTED; WARNING on COMPLETED with **`total_errors > 0`**. **`run_inflow_discovery_batch`** — non-debug WARNING batch summary when **`errors > 0`**. | `src/core/dispatcher.py`, `src/core/roster.py` | **`TestAst841DispatchTerminalLogging`** in `test_dispatcher.py`; **`TestAst505InflowDiscovery::test_run_batch_cse_failure_continues`** (caplog WARNING: per-term **`CSE failed`** + batch **`CSE term error(s)`**) |

**AST-841** narrowed run:

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_dispatcher.py::TestAst841DispatchTerminalLogging \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues \
  -q
```

**Regression guard:** full **`test_dispatcher.py`** + **`TestAst505InflowDiscovery`** when parent UAT runs full epic.

---

### AST-849 · AST-847

**Dispatch-chain claim:** **`dispatch_chain_claim_states_for_row`** passed as **`states=`** to **`get_new_job_batch`** when **`is_dispatch_chain_trigger(input_state)`**; post-claim filter via **`dispatch_chain_row_matches_job`** before **`run_consult_task`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Forward **`dispatch_task_key`** + chain claim filter | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::{test_ast534_forwards_dispatch_task_key_to_consult,test_ast849_post_claim_filter_skips_row_mismatch}` |

Primary manifest: **`docs/test-bible/core/agent.md`** AST-849.

---

### AST-875 · AST-873

**`set_candidate_dispatch_tasks_from_template`**: resolve template from config, require both candidates exist, call data set-from-rows; never **`run_task`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Core orchestration + LookupError / blank target | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestAst875SetCandidateDispatchTasksFromTemplate` |

Primary data/API manifest: **`docs/test-bible/data/database/dispatch_tasks.md`** (**AST-875**).

---

### AST-891 · AST-890

**AST-891:** **`_run_unified`** sets **`use_full_batch`** when **`task_key == "parse_job_list"`** even if DB **`batch_call_mode=0`** — one **`run_consult_task`** with the full claimed company list (no **`_warm_then_gather`** Firefox fan-out). Adjacent company hops (e.g. **`gaze`**) stay on per-entity gather when **`batch_call_mode=0`**. **`clear_company_batch`** in **`finally`** unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Full-list consult for **`parse_job_list`** | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast891_parse_job_list_full_batch_despite_batch_call_mode_zero` |

Primary roster / consult manifest: **`docs/test-bible/core/roster.md`** · **`docs/test-bible/core/consult.md`** (**AST-891**).

Timeout partial counts: § AST-1847 · AST-1848.

### AST-972 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-972 / **AST-1252**. Dispatcher: **`retire_candidate_requested_wrapper_dispatch_tasks`** (retire-only); candidate claim gate in **`_run_unified`**; tick calls **`age_stale_candidate_states`**; **`start_scheduler`** runs wrapper retire after meteorite provision.


### AST-1022 · AST-1018

**AST-1022:** Candidate stage-dispatch rows seed **AUTO off** from `CANDIDATE_STAGE_DISPATCH.auto_mode`; `ensure_candidate_stage_dispatch_tasks` reads config (insert-missing only — never rewrites existing `auto_mode`). Tick Style D helper `_debug_log_auto_off_stage_skips` logs AUTO-off + `debug` stage rows that meet `min_count` (index N/M); does not spawn. `get_due_tasks` / CLICK `run_task(..., ui_initiated=True)` unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Config seed `auto_mode: False` | `src/utils/config.py` | **`TestAst1022HonorAutoOffStageDispatch`** (`test_config.py`) |
| Ensure seed + persist; Style D skip; tick calls helper before spawn | `src/core/dispatcher.py` | **`TestAst1022HonorAutoOffStageDispatch`**; revised **`_run_one_tick`** / **`TestScheduler`** (list_dispatch_tasks stub) |

**Broken / obsolete:** tick unit helpers must stub `list_dispatch_tasks` (new side path) — same DB-free contract as AST-972 `age_stale` stub.

**Existing coverage (unchanged paths):** AUTO-on tick spawn — **`TestScheduler::test_tick_loop_spawns_due_auto_tasks`**; CLICK with `auto_mode=0` — **`TestDispatchOne`** / run_task paths already covering AUTO-off CLICK.

**AST-1022** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch \
  tests/component/core/test_dispatcher.py::TestScheduler \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch \
  -q
```

### AST-1054 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`.

`ensure_meteorite_dispatch_tasks` / `provision_meteorite_dispatch_tasks` seed `METEORITE_DISPATCH_TASKS` rows (idempotent; twin keys `skipped_missing_config` until `TASK_CONFIG` has them); `start_scheduler` provisions after stage rows. Twin GDL entry insert is `evaluate_meteorite`@**METEORITE_QUALIFIED**; live retirement of `evaluate_jd`@`METEORITE_*` when twin present is **AST-1209** (not NEW-only). Config/consult primary: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure GDL + twin skip/insert; provision helpers | `src/core/dispatcher.py` | **`TestAst1054MeteoriteDispatchProvision`** (counts/trigger + retire revised **AST-1060**; scheduler hook flipped **AST-1500**) |
| Stage scheduler stub | `src/core/dispatcher.py` | revised **`TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision`** (stubs meteorite provision) |

**Broken / obsolete:** AST-972 start_scheduler test — stub `provision_meteorite_dispatch_tasks` so the new try-path does not hit live DB; insert-count / evaluate_jd@METEORITE_NEW asserts revised by **AST-1060**. **AST-1500:** `test_start_scheduler_invokes_meteorite_provision` → `test_start_scheduler_does_not_invoke_meteorite_provision` (ban auto writers).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  -q
```

### AST-1060 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`.

`ensure_meteorite_dispatch_tasks` retirement of live meteorite `evaluate_jd` rows is **AST-1209** (`METEORITE_*` when twin present — supersedes NEW-only). Config primary: **`docs/test-bible/utils/config.md`**. Twin insert/retire asserts: **AST-1209** / **AST-1210** section below.

| Area | Source | Component tests |
| --- | --- | --- |
| Retire meteorite evaluate_jd; insert twin counts | `src/core/dispatcher.py` | **`TestAst1054MeteoriteDispatchProvision`** (revised **AST-1209**) |

**Broken / obsolete:** NEW-only retire + insert-as-`evaluate_jd`@**METEORITE_QUALIFIED** asserts — see **AST-1209**.

**Integration:** none.

### AST-1062 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1062-qualify-meteorite-batch-apply-meteorite-qualified`.

`qualify_meteorite` joins `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` (same widen-claim + chunk waves as listing qualify).

| Area | Source | Component tests |
| --- | --- | --- |
| Chunk exhaust membership | `src/core/dispatcher.py` | **`TestAst1062QualifyMeteoriteChunkExhaust`** |

**Broken / obsolete:** none — additive frozenset member.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1062QualifyMeteoriteChunkExhaust \
  -q
```

### AST-1088 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`.

`ensure_gaze_email_dispatch_task` / `provision_gaze_email_dispatch_task` insert one null-`candidate_id` `gaze_email` row from `GAZE_EMAIL_CONFIG` (idempotent; `skipped_missing_config` if key absent from `TASK_CONFIG`). `start_scheduler` provisions after meteorite. Does **not** wire due-task / mailbox runner (**AST-1090**). Config / data / Gmail: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** · **`docs/test-bible/external/gmail.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure add/skip; missing config; provision wrapper; scheduler hook | `src/core/dispatcher.py` | **`TestAst1088GazeEmailDispatchProvision`** |
| Stage / meteorite scheduler stubs | `src/core/dispatcher.py` | revised **`TestAst972…::test_start_scheduler_invokes_stage_provision`**, **`TestAst1054…::test_start_scheduler_does_not_invoke_meteorite_provision`** (**AST-1500** ban) |

**Broken / obsolete:** start_scheduler unit helpers must stub `provision_gaze_email_dispatch_task` so the new try-path does not hit live DB.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1088GazeEmailDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision::test_start_scheduler_does_not_invoke_meteorite_provision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  -q
```

### AST-1090 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`.

`_dispatch_one` special-cases `gaze_email`: no candidate API key; ledger uses `dispatch_ledger_candidate_id`; awaits `run_gaze_email` (not `_run_unified`). Due path: **`docs/test-bible/data/database/dispatch_tasks.md`**. Runner: **`docs/test-bible/core/gaze_email.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Gaze dispatch route | `src/core/dispatcher.py` | **`TestAst1090GazeEmailDispatchOne`** |

**Broken / obsolete:** none — additive branch before unified loop.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne \
  -q
```


### AST-1134 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`.

`ensure_gaze_email_dispatch_task(candidate_id)` inserts one bound row; `provision_gaze_email_dispatch_tasks()` retires null-`candidate_id` shells then coverage-joins every `list_candidates()` id. `_dispatch_one` ledger uses row `candidate_id` (skips unbound). Config / data: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`**. Runner stamp / live Avail: **AST-1136** / **AST-1135**.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure / provision / scheduler hook | `src/core/dispatcher.py` | **`TestAst1134GazeEmailDispatchProvision`** (replaces **`TestAst1088GazeEmailDispatchProvision`**) |
| Bound ledger cid + unbound skip | `src/core/dispatcher.py` | revised **`TestAst1090GazeEmailDispatchOne`** |
| Stage / meteorite scheduler stubs | `src/core/dispatcher.py` | revised stubs → **`provision_gaze_email_dispatch_tasks`** |

**Broken / obsolete (Betty revision):** null-shell ensure/provision wrapper; `_dispatch_one` null-cid runner path; singular `provision_gaze_email_dispatch_task` stubs.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1134GazeEmailDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne \
  -q
```

### AST-1135 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`.

`_gaze_email_due_tasks` merges AUTO candidate-bound gaze rows when live bind Avail ≥ `min_count` and `dispatch_task_freq_allows`; `_tick_loop` concatenates with `get_due_tasks()`. `run_task` enriches gaze `available_count` via inbox bind count. Inbox / data / admin: **`docs/test-bible/core/inbox.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** · **`docs/test-bible/ui/api/api_admin.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| AUTO due merge + click enrich | `src/core/dispatcher.py` | **`TestAst1135GazeEmailDueTasks`** |

**Broken / obsolete:** none — additive due path (data fake due retired under dispatch_tasks).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1135GazeEmailDueTasks \
  -q
```

### AST-1209 · AST-1186

**Parent:** [AST-1186 — evaluate_meteorite: fold recent work into tests + statute/pattern check](https://linear.app/astralcareermatch/issue/AST-1186/evaluate-meteorite-fold-recent-work-into-tests-statutepattern-check). **Publish:** `origin/sub/AST-1186/AST-1209-evaluate-meteorite-twin-audit-conformance-fixes`.

`ensure_meteorite_dispatch_tasks` retires **every** live `evaluate_jd` row whose `trigger_state` starts with `METEORITE_` (NEW + QUALIFIED eras), but **only when** twin `evaluate_meteorite`@`METEORITE_QUALIFIED` is already present or was just inserted. Keeps `evaluate_jd`@`JD_READY`. Insert loop seeds twin GDL entry (`evaluate_meteorite`, not classic `evaluate_jd`). Full twin bible/config/consult lock: sibling **AST-1210**. Fixture lockstep: **AST-1211**.

| Area | Source | Component tests |
| --- | --- | --- |
| Twin GDL insert key + trigger | `src/core/dispatcher.py` | revised **`TestAst1054MeteoriteDispatchProvision::test_ensure_inserts_shared_gdl_and_twins_per_task_config`** |
| Retire `evaluate_jd`@`METEORITE_*` when twin present; keep `@JD_READY` | `src/core/dispatcher.py` | **`TestAst1054MeteoriteDispatchProvision::test_ensure_retires_evaluate_jd_on_meteorite_triggers_when_twin_present`** (replaces AST-1060 NEW-only retire) |
| No retire when twin absent from `TASK_CONFIG` | `src/core/dispatcher.py` | **`TestAst1054MeteoriteDispatchProvision::test_ensure_skips_retire_when_twin_absent`** |

**Broken / obsolete:** AST-1060 `test_ensure_retires_stale_evaluate_jd_at_meteorite_new` (NEW-only + assert insert of `evaluate_jd`@`METEORITE_QUALIFIED`); insert assert that meteorite GDL entry is still `evaluate_jd`; `test_start_scheduler_invokes_meteorite_provision` stub of removed `provision_candidate_stage_dispatch_tasks` (scheduler tip is meteorite → gaze only).

**Integration:** none — no existing scenarios assert meteorite dispatch retirement.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  -q
```

### AST-1221 · AST-1184

**Parent:** [AST-1184 — Task config aliases via master_task_key](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key). **Publish:** `origin/sub/AST-1184/AST-1221-runtime-alias-resolution-retire-do-get-overlay`.

`meteorite_grade_do` / `meteorite_grade_get` join `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` (explicit frozenset, same pattern as `meteorite_like`). Dispatch retarget / seed is **AST-1222**.

| Area | Source | Component tests |
| --- | --- | --- |
| Alias exhaust membership | `src/core/dispatcher.py` | **`TestAst1221AliasChunkExhaust`** |

**Broken / obsolete:** none — additive frozenset keys.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1221AliasChunkExhaust \
  -q
```

### AST-1222 · AST-1184

**Parent:** [AST-1184 — Task config aliases via master_task_key](https://linear.app/astralcareermatch/issue/AST-1184/task-config-aliases-via-master-task-key). **Publish:** `origin/sub/AST-1184/AST-1222-meteorite-do-get-alias-seed-retarget-dispatch`.

`METEORITE_DISPATCH_TASKS` Do/Get → alias keys; `ensure_meteorite_dispatch_tasks` retires shared-key meteorite triggers when aliases present (classic Gaze `PASSED_JD` / `PASSED_DO` kept). Catalog / fixture: **`docs/test-bible/core/repo_admin_json.md`** · config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Alias insert + score_floor | `src/core/dispatcher.py` | revised **`TestAst1054MeteoriteDispatchProvision`** |
| Retire shared-key meteorite Do/Get | same | **`TestAst1054MeteoriteDispatchProvision::test_ensure_retires_shared_key_meteorite_do_get_when_aliases_present`** |

**Broken / obsolete:** AST-1054 `by_key["grade_do"]` / `grade_get` meteorite insert lookups.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  -q
```

### AST-1259 · AST-1257

**Parent:** [AST-1257 — candidate table does not have batch_id](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id). **Publish:** `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`.

`_run_unified` for `entity_type=candidate` claims via `get_new_candidate_batch` (`dispatch_claim_states` + `batch_size`), forces per-entity process (`use_full_batch=False`), clears on empty early-exit and in `finally` (no unlocked `[ctx]` arm). Core wrappers: **`docs/test-bible/core/candidate.md`** § AST-1259. Data claim APIs: **AST-1258**.

| Area | Source | Component tests |
| --- | --- | --- |
| Pool claim + clear; no job/company clear | `src/core/dispatcher.py` | revised **`TestRunUnified::test_ast505_candidate_entity_claims_without_company_clear`**; **`TestAst1259CandidatePoolClaim`** |
| Empty claim clears; claimed → consult | same | revised **`TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate`**; **`::test_empty_batch_clears_candidate_batch`** |
| `batch_size` / claim states; multi-row per-entity | same | **`TestAst1259CandidatePoolClaim::test_claim_honors_batch_size_and_claim_states`** |

**Broken / obsolete (Betty revision):** unlocked-`[ctx]` asserts in `test_ast505_candidate_entity_routes_ctx_without_company_clear` and ctx-state-only `test_run_unified_candidate_claim_gate`.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_claims_without_company_clear \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate \
  tests/component/core/test_dispatcher.py::TestAst1259CandidatePoolClaim \
  tests/component/core/test_candidate.py::TestAst1259CandidateBatchApi \
  -q
```

### AST-1500 · AST-1456

**Parent:** [AST-1456 — Do not overwrite dispatch_task](https://linear.app/astralcareermatch/issue/AST-1456). **Publish:** `origin/sub/AST-1456/AST-1500-gap-dispatcher-provision-tests`. Gap child for AST-1496 board REVISE.

Ban automatic `dispatch_task` writers on scheduler start; script hard-fail on `dispatch_task`. Product ban lands on sibling **AST-1496**.

| Area | Source | Component tests |
| --- | --- | --- |
| start_scheduler no meteorite / fetch_email provision | `src/core/dispatcher.py` | revised **`TestAst1054…::test_start_scheduler_does_not_invoke_meteorite_provision`** |
| start_scheduler no meteorite_email provision | same | revised **`TestAst1134…::test_start_scheduler_does_not_invoke_gaze_provision`** (ex-AST-1088) |
| push/upsert CLI hard-fail | `scripts/push_tables_to_prod.py`, `scripts/upsert_tables_from_prod.py` | **`TestAst1500DispatchTaskScriptBan`** |
| ensure content migrations left alone | `src/data/database.py` | revised **`TestAst703…::test_schema_leaves_dual_prefilter_rows_unchanged`** — see **`docs/test-bible/data/database/dispatch_tasks.md`** |

**Broken / obsolete:** `test_start_scheduler_invokes_meteorite_provision`, `test_start_scheduler_invokes_gaze_provision`; TestAst703 HOMEPAGE_READY migration assert.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision::test_start_scheduler_does_not_invoke_meteorite_provision \
  tests/component/core/test_dispatcher.py::TestAst1134MeteoriteEmailDispatchProvision::test_start_scheduler_does_not_invoke_gaze_provision \
  tests/component/scripts/test_ast1500_dispatch_task_script_ban.py::TestAst1500DispatchTaskScriptBan \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  -q
```

### AST-1559 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1559-check-inbox-monitoring-log`.

Mailbox branch awaits **`check_inbox`** — revised **`TestAst1090GazeEmailDispatchOne`**.

---

### AST-1560 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1560-stage-scrape-land-transitions`.

`_dispatch_one` custom branch before mailbox / `_run_unified`: mints `entity_batch_id`, sets `task["entity_batch_id"]`, routes `stage_meteorite` / `scrape_meteorite` / `land_meteorite` to meteorite transition runners (not consult). **`TestAst1560IngressTransitionDispatchOne`**. Runners: **`docs/test-bible/core/meteorite.md`** § AST-1560.

**Integration:** none revised.

Primary numbered manifest: **`docs/test-bible/core/meteorite.md`** § AST-1560.

---

### AST-1774 · AST-1762

**Parent:** [AST-1762](https://linear.app/astralcareermatch/issue/AST-1762/meteorite-state-check-unique-before-landed). **Publish:** `origin/sub/AST-1762/AST-1774-check-unique-meteorite-sql-transitions`.

Ingress adds `check_unique_meteorite` twin of stage/scrape (provision via `_ensure_ingress_transition_tasks` + route in `_run_dispatch_loop` / `_dispatch_one`). Assertions live on **`TestAst1560IngressTransitionDispatchOne`** (`test_routes_check_unique_…`, `test_ensure_ingress_includes_check_unique`). Runners + stage/scrape retarget: **`docs/test-bible/core/meteorite.md`** § AST-1774.

**Integration:** none revised.

Primary numbered manifest: **`docs/test-bible/core/meteorite.md`** § AST-1774.

---

### AST-1562 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email`.

`_dispatch_one` retention branch → `run_meteorite_retention` with minted `entity_batch_id` (after notify, before mailbox `check_inbox`). **`TestAst1562RetentionDispatchOne`**. Runners + config: **`docs/test-bible/core/meteorite.md`** § AST-1562.

**Integration:** none revised.

Primary numbered manifest: **`docs/test-bible/core/meteorite.md`** § AST-1562.

---

### AST-1561 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste`.

`_dispatch_one` notify branch → `run_notify_meteorite_bot_blocked` with minted `entity_batch_id`. **`TestAst1561BotBlockedNotifyDispatchOne`**. Runners + paste: **`docs/test-bible/core/meteorite.md`** § AST-1561.

**Integration:** none revised.

Primary numbered manifest: **`docs/test-bible/core/meteorite.md`** § AST-1561.

---

### AST-1829 · AST-1824

**Parent:** [AST-1824](https://linear.app/astralcareermatch/issue/AST-1824). **Publish:** `origin/sub/AST-1824/AST-1829-sweep-interval-data-scheduled-sweep`.

`dispatch_task.sweep_hrs` scheduled sweep: an AUTO row with 0 < Avail < `min_count` is due **as a sweep** (`_scheduled_sweep=True`) once `sweep_hrs` has elapsed since `last_run_at`. Both due paths (claim-queue `database.get_due_tasks`, mailbox `_meteorite_email_due_tasks`); `_tick_loop` logs sweep-due once and passes `run_task(..., scheduled_sweep=)`; `_run_dispatch_loop` caps a flagged AUTO row at one batch, min 1. `_dispatch_one` debug forcing stays `_ui_initiated`-only. Data half: **`docs/test-bible/data/database/dispatch_tasks.md`** § AST-1829.

| AC | Source | Component tests |
| --- | --- | --- |
| 1 column fresh + migrated, NULL | `src/data/database.py` `_ensure_dispatch_task_schema` | `tests/component/data/database/test_dispatch_tasks.py::TestAst1829SweepInterval::{test_fresh_schema_has_nullable_real_column,test_existing_db_migrates_column_without_backfill}` |
| 2–7 claim-queue due rule | `database.get_due_tasks` / `dispatch_task_sweep_due` | `::TestAst1829SweepInterval::{test_get_due_tasks_sweep_rule,test_sweep_due_helper}` |
| 7 unflagged AUTO below min skips | `_run_dispatch_loop` | `tests/component/core/test_dispatcher.py::TestAst1829ScheduledSweep::test_loop_unflagged_auto_below_min_skips` (+ existing `TestRunDispatchLoop::test_continues_when_max_runs_zero`) |
| 8 one batch, no min gate, `last_run_at` stamped | `_run_dispatch_loop` / `_dispatch_one_body` | `::TestAst1829ScheduledSweep::test_sweep_one_batch_no_min_gate_and_debug[scheduled_sweep]` |
| 9 mailbox parity (freq gate kept) | `_meteorite_email_due_tasks` | `::TestAst1829ScheduledSweep::{test_mailbox_sweep_due_marked,test_mailbox_sweep_blocked_by_freq,test_mailbox_sweep_not_due,test_mailbox_full_batch_unmarked}` |
| 10 debug forcing UI-only | `_dispatch_one` | `::TestAst1829ScheduledSweep::test_sweep_one_batch_no_min_gate_and_debug` (both ids) |
| tick → spawn flag + sweep-due debug | `_tick_loop` / `run_task` | `::TestAst1829ScheduledSweep::{test_tick_passes_sweep_flag_and_logs_sweep_due,test_run_task_stores_scheduled_sweep}` |
| 11 template copy | `_DISPATCH_TASK_TEMPLATE_COPY_COLS` / `_dispatch_task_schedule_assign` | `tests/component/data/database/test_dispatch_tasks.py::TestAst1829SweepInterval::test_template_copy_carries_sweep_hrs` |
| 12 no parallel scheduler | `src/core/dispatcher.py` | shell grep (manifest item 3) |

**Broken / obsolete → revised:** `run_task` stubs taking only `task_id` now accept `**_kw` (tick passes `scheduled_sweep=`): `TestScheduler::{test_tick_loop_spawns_due_auto_tasks,test_tick_loop_skips_running_and_full_slots,test_tick_loop_ignores_failed_spawn,test_tick_loop_stops_when_spawn_slots_are_exhausted,test_tick_loop_skips_when_auto_slots_full}` and `TestAst1022HonorAutoOffStageDispatch::test_tick_loop_calls_auto_off_debug_helper_before_spawn`. `test_api_admin.py` `run_task` stubs unchanged (admin API is sibling AST-1830).

**Integration:** none revised — no scenario exercises the tick / due selection.

## QA test manifest

1. **New + revised (required, green):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1829ScheduledSweep \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1829SweepInterval \
  tests/component/core/test_dispatcher.py::TestScheduler \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch::test_tick_loop_calls_auto_off_debug_helper_before_spawn \
  tests/component/core/test_dispatcher.py::TestRunDispatchLoop \
  tests/component/core/test_dispatcher.py::TestAst1135GazeEmailDueTasks \
  tests/component/data/database/test_dispatch_tasks.py::TestAst875SetDispatchTasksFromTemplate \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1135DispatchTaskFreqAllows \
  -q
```

2. **Regression sweep (no new reds):** `tests/component/core/test_dispatcher.py` + `tests/component/data/database/test_dispatch_tasks.py` whole-file. **Baseline at QA time (pre-AST-1829 `tests` @ `bd5dc48c` on `origin/dev` product): 11 + 19 failures already red and unrelated to sweep** (candidate `candidate_id required` claim, circuit breaker, AST-641/891 claim states, AST-802/814 debug, AST-841 terminal logs, AST-1022 style-D, meteorite count, `TestSaveDispatchTask::test_inserts_and_reads_task`). Pass = the failing set is identical to that baseline; any new red is AST-1829's.
3. **AC 12:** `grep -n "Thread(" src/core/dispatcher.py` → exactly 2 lines (per-task thread in `run_task`, tick thread in `start_scheduler`).
4. **Branch lock:** `src/core/dispatcher.py` (`LOCKED_AT_100`) — no new missed lines in the AST-1829 hunks (`_run_dispatch_loop` flag, `run_task`, `_meteorite_email_due_tasks` sweep branch, `_tick_loop` sweep-due loop). Zero-arg harness gate is unreliable on this tip given item 2 baseline reds.

**Bible shasum (publish tip):** fill after `merge-tests` —
- `docs/test-bible/core/dispatcher.md`
- `docs/test-bible/data/database/dispatch_tasks.md`

---

### AST-1847 · AST-1848 (qa-fix bug-repro — parse_job_list timeout partial counts in ledger)

**Parent:** [AST-1845](https://linear.app/astralcareermatch/issue/AST-1845) (orphaned-bug mini-parent). Product: **AST-1847** (`ba60f8e4` on `origin/sub/AST-1845/AST-1847-parse-job-list-timeout-partial-counts`, not yet on ftr); test/bible delivery on gap sibling **AST-1848** (`origin/sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests`). Contract: `_run_unified` puts a fresh copy of `_SUMMARY_ZERO` on `ctx["dispatch_partial"]` per run and pops it on normal return only; the `_dispatch_one_body` **timeout** branch folds the in-flight partial into `accumulated`, adds the `+1` timeout error **before** logging, and the timeout log line carries `processed= passed= failed= errors=` matching the INTERRUPTED ledger write. Admin-kill (`CancelledError`) branch unchanged (out of scope).

**Sequencing deviation (gap child, AST-1844 / AST-1846 precedent):** product landed first. `[bug-repro]` proven both ways — **RED at ftr base `8e7b77a5`** on assertions (ledger `0/0/0/1`, log without counts; node 5 `KeyError: 'dispatch_partial'`) and **GREEN with `ba60f8e4`'s `roster.py` + `dispatcher.py` overlaid** (scratch worktree, not committed).

| Area | Source | Component tests |
| --- | --- | --- |
| Real dispatch → consult → `parse_job_list_batch` timeout: ledger `3/2/0/1` + log counts; `clear_company_batch` on cancel | `_dispatch_one_body` / `_run_unified` + `roster.parse_job_list_batch` | **`tests/component/core/test_dispatcher.py::TestAst1847TimeoutPartialCounts::test_parse_job_list_timeout_ledger_and_log_carry_partial_counts`** (**bug-repro**) |
| Fold-in loop with items on top of prior runs; `+1` before log; partial popped | `_dispatch_one_body` timeout branch | **`::TestAst1847TimeoutPartialCounts::test_timeout_folds_partial_on_top_of_prior_runs`** (branch lock) |
| Fresh copy per run (stale replaced, constant not aliased); popped on return | `_run_unified` | **`::TestRunUnified::test_ast1847_sets_fresh_dispatch_partial_and_pops_on_return`** (branch lock) |
| Cancel leaves partial in place; `finally` still clears batch | `_run_unified` | **`::TestRunUnified::test_ast1847_cancel_keeps_dispatch_partial_and_clears_batch`** (branch lock) |
| Empty-partial fold (`wait_for` raises before `_run_unified` sets the key) | `_dispatch_one_body` timeout branch | existing **`::TestDispatchOne::test_auto_dispatch_uses_timeout`** (unchanged) |

Roster tally nodes: **`docs/test-bible/core/roster.md`** § AST-1847 · AST-1848.

**Branch lock (AST-1847 lines only):** full component run with `--cov-branch` and the `ba60f8e4` overlay — **0 missing lines / 0 missing branches** on every line `ba60f8e4` added in `dispatcher.py` (16) and `roster.py` (23); missing-branch count unchanged vs base (dispatcher 42 / 42, roster 136 / 136). `check_per_file_coverage.py` on that report still exits 1 whole-file (dispatcher **86.1%**, roster **78.2%**; base 86.0% / 78.1%) solely from pre-existing host drift (316 failing + 5 uncollectable `SURFER_BATCH_CONFIG` modules at tip, 323 at base — the 7-node difference is exactly this ticket's red→green set).

**Broken / obsolete:** none.

**Integration:** none — do not invent.

## QA test manifest

1. **Repro + branch-lock nodes** (**[bug-repro]** — red at `8e7b77a5`, green with AST-1847; `test_auto_dispatch_uses_timeout` green both):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1847TimeoutPartialCounts \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast1847_sets_fresh_dispatch_partial_and_pops_on_return \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast1847_cancel_keeps_dispatch_partial_and_clears_batch \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_dispatch_uses_timeout \
  -q
```

2. **Branch lock:** full `tests/component` with `--cov-branch` (`--continue-on-collection-errors` on this host) — 0 missing lines / branches on AST-1847's added lines in `src/core/dispatcher.py`; whole-file % no lower than base.

**Bible shasum (record after publish):** `git show origin/sub/AST-1845/AST-1848-parse-job-list-timeout-partial-counts-tests:docs/test-bible/core/dispatcher.md | shasum`

---

### AST-1867 · AST-1870 (qa-fix bug-repro — provider balance refusal as one batch-level outage)

**Parent:** [AST-1860](https://linear.app/astralcareermatch/issue/AST-1860) (orphaned-bug mini-parent). Product: **AST-1867** (`144b8850` on `origin/sub/AST-1860/AST-1867-provider-balance-outage`, not yet on ftr); test/bible delivery on gap sibling **AST-1870** (`origin/sub/AST-1860/AST-1870-provider-balance-outage-tests`). Contract: the first result satisfying `is_provider_balance_refusal` sets `ctx["provider_balance_outage"] = {"error", "held"}` (one WARNING; later refusals only add `total_held`); `_run_unified` per-entity `_one` and chunk `_consult_chunk` return `_SUMMARY_ZERO` once it is set (no provider call, not processed; `finally` still releases the claim); `_run_dispatch_loop` breaks after the outage run's mid-run ledger write; `_dispatch_one_body` ends the run **INTERRUPTED**, sends `monitor.provider_balance_outage` **instead of** `auto_run_error` (AUTO + ledger id only), and never reaches `_check_circuit_breaker` (COMPLETED-only; non-COMPLETED rows are also invisible to `get_recent_ledger_summaries`). `total_held` / `failure_class` never enter the summary (ledger-safe). Ordinary errors never set the ctx key.

**Sequencing deviation (gap child, AST-1848 precedent):** product landed first. `[bug-repro]` proven both ways — **RED at ftr base `fbe9486e`** on assertions (`assert 9 == 1` on `run_select_job_page_dispatch.await_count`: 3 companies × 3 runs) and **GREEN with `144b8850`'s `roster.py` + `dispatcher.py` + `monitor.py` overlaid** (scratch worktree, not committed).

| Area | Source | Component tests |
| --- | --- | --- |
| Real dispatch → consult → `run_company_task` select_job_page balance hold: 1 provider call, 1 claim, INTERRUPTED `1/…/0` errors, outage alert `(task_key, batch, acc, {"error", "held": 1}, cid)`, no `auto_run_error`, no breaker | `_dispatch_one_body` / `_run_dispatch_loop` / `_run_unified` + `roster.run_company_task` | **`tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage::test_bug_repro_balance_refusal_one_call_interrupted_outage_alert`** (**bug-repro**) |
| Per-entity skip after refusal; summary has no `total_held` / `failure_class`; ctx marker `held=1`; claim released | `_run_unified` `_one` + `_note_provider_balance_outage` | **`::TestAst1867ProviderBalanceOutage::test_run_unified_per_entity_skips_after_refusal`** |
| Job chunk split: head chunk refusal skips both tail chunks; consult envelope → `held=0` | `_run_unified` `_consult_chunk` | **`::TestAst1867ProviderBalanceOutage::test_run_unified_chunk_split_skips_tail_after_head_refusal`** |
| Ordinary error (no `failure_class`) → every entity called, no ctx marker (guard) | `_run_unified` | **`::TestAst1867ProviderBalanceOutage::test_run_unified_ordinary_error_does_not_skip`** (green both) |
| Loop stops after the outage run; mid-run ledger write first (`max_runs=0`; finite eligibility `[24,24,24,0]` so the pre-fix loop terminates) | `_run_dispatch_loop` | **`::TestAst1867ProviderBalanceOutage::test_run_dispatch_loop_stops_after_outage_run`** |
| CLICK outage run → INTERRUPTED, no alert of either kind, no breaker | `_dispatch_one_body` | **`::TestAst1867ProviderBalanceOutage::test_dispatch_one_click_outage_interrupted_no_alert`** |
| Non-outage AUTO error still → `auto_run_error` | `_dispatch_one_body` | existing **`::TestDispatchOne::test_auto_run_error_on_auto_failures`** (unchanged; passes by accident — its 5-param `_bump` raises `TypeError` against the 6-arg call, run ends FAILED `+1` error; pre-existing, out of scope) |

Roster counting nodes: **`docs/test-bible/core/roster.md`** § AST-1867 · AST-1870. Alert body/subject: **`docs/test-bible/core/monitor.md`** § AST-1867 · AST-1870.

**Not covered (by design):** consult batch branches (`prefilter_company` etc.) rebuild the summary and drop `failure_class` — AST-1867 D5 leaves them unwired; no outage assertions there.

**Pre-existing drift on this tip (not AST-1867, left as-is):** `TestCircuitBreaker::*` (4-arg calls vs 3-arg product); `TestAutoRunErrorSubjectPrefix` (3 nodes). Full `test_dispatcher.py` + `test_roster.py` + `test_monitor.py` run: identical 65-node failure set at `fbe9486e` (base tests) and with the `144b8850` overlay (this ticket's tests) — zero new failures.

**Broken / obsolete:** none in dispatcher.

**Integration:** none — do not invent.

## QA test manifest

1. **Repro + outage nodes + alert-routing regression** (**[bug-repro]** red at `fbe9486e`, green with AST-1867):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures \
  tests/component/core/test_roster.py::TestAst1867BalanceHeldCounting \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_monitor.py::TestAst1867ProviderBalanceOutage \
  tests/component/core/test_monitor.py::TestAutoRunError \
  -q
```

Expect **23 passed** with AST-1867 product.

**Bible shasum (record after publish):** `git show origin/sub/AST-1860/AST-1870-provider-balance-outage-tests:docs/test-bible/core/dispatcher.md | shasum`

### AST-2010 · AST-2009 (qa-fix bug-repro — exhausted OpenRouter 429 stops the batch, ledger FAILED)

**Primary manifest:** [`../external/llm_compat.md`](../external/llm_compat.md) § AST-2010. Contract: the first result satisfying `is_provider_rate_limit` sets `ctx["provider_rate_limit_outage"] = {"error"}`. This happens at all three `_run_unified` call sites (per-entity `_one`, chunk `_consult_chunk`, full-batch call). Remaining entities and chunks are then skipped, and the claim is still released. `_run_dispatch_loop` breaks after the run. `_dispatch_one_body` finishes **FAILED**, which wins over a balance outage's INTERRUPTED, and never reaches the breaker. Untagged results (DeepSeek / Kimi 429) never set the key. Red at `c08219c32`: `assert 6 == 1` (2 entities × 3 runs) and status `COMPLETED`.

| Area | Source | Component tests |
| --- | --- | --- |
| AST-2009 shape: 2-entity `meteorite_like`, `batch_call_mode=0`, warm entity exhausted → 1 consult call, claim released, ledger FAILED `1/…/1`, no balance alert, no breaker | `_dispatch_one_body` / `_run_dispatch_loop` / `_run_unified` | **`tests/component/core/test_dispatcher.py::TestAst2010ProviderRateLimitOutage::test_bug_repro_rate_limit_stops_batch_ledger_failed`** (**bug-repro**) |
| Per-entity skip; summary carries no `failure_class` / `error`; ctx marker `{"error"}`; no balance key | `_one` | **`::TestAst2010ProviderRateLimitOutage::test_run_unified_per_entity_skips_after_rate_limit`** |
| Chunk split: head tagged → tail chunks skipped | `_consult_chunk` | **`::…::test_run_unified_chunk_split_skips_tail_after_head_rate_limit`** |
| Full-batch call marks ctx | full-batch branch | **`::…::test_run_unified_full_batch_marks_rate_limit`** |
| Untagged 429 → every entity called, no marker (guard, green both) | `_one` | **`::…::test_run_unified_untagged_429_does_not_skip`** |
| Loop stops after the outage run | `_run_dispatch_loop` | **`::…::test_run_dispatch_loop_stops_after_rate_limit_run`** |
| FAILED alone and with a balance outage (FAILED wins); breaker skipped | `_dispatch_one_body` | **`::…::test_dispatch_one_rate_limit_outage_failed[False/True]`** |

**Kept:** `TestAst1867ProviderBalanceOutage` (balance-only still INTERRUPTED + alert).

**Integration:** none — do not invent.

### AST-2098 · AST-2099 (failed host probe holds the batch)

**Parent:** [AST-2016](https://linear.app/astralcareermatch/issue/AST-2016) (orphaned-bug mini-parent). Product: **AST-2098** (`19036ccf0` on `origin/ftr/AST-2016-probe-fail-hold`); test/bible delivery on gap sibling **AST-2099** (`origin/sub/AST-2016/AST-2099-probe-fail-hold-gaps`); plan `docs/features/foundation/ast-1959-per-batch-probe-and-host-lock-on-the-openrouter-path.md` § Bug: AST-2099. **Primary manifest (this file).** Contract: the first result satisfying `is_provider_probe_failure` (`failure_class == "provider_probe_failure"`) sets `ctx["provider_probe_outage"] = {"error", "held"}` (one WARNING; later results only add `total_held`). This happens at all three `_run_unified` call sites (per-entity `_one`, chunk `_consult_chunk`, full-batch call). Remaining entities and chunks are then skipped, and the claim is still released in `finally`. `_run_dispatch_loop` breaks after the run. `_dispatch_one_body` finishes **INTERRUPTED** with no alert (AST-2098 Boundary) and no `auto_run_error`, and never reaches the breaker. A rate-limit outage's **FAILED** wins over it. `total_held` / `failure_class` never enter the summary (ledger-safe).

**Sequencing deviation (gap child, AST-1870 precedent):** product landed first. **[bug-repro]** red at pre-fix `25c7ab095` (`git restore --source 25c7ab095 -- src/` over this ticket's tests): `assert 6 == 1` (2 jobs × 3 runs), status `COMPLETED`. Green on `19036ccf0`. All 23 AST-2098 nodes across the six modules fail by assertion pre-fix (no import / setup errors — literals only, no AST-2098 symbol imports).

| Area | Source | Component tests |
| --- | --- | --- |
| AST-2016 shape: 2-job `meteorite_grade_get`, `batch_call_mode=0`, `max_runs=3`, warm job probe-held → 1 consult call, claim released, ledger INTERRUPTED `1/…/0`, no breaker / `auto_run_error` / balance alert | `_dispatch_one_body` / `_run_dispatch_loop` / `_run_unified` | **`tests/component/core/test_dispatcher.py::TestAst2098ProviderProbeOutage::test_bug_repro_probe_failure_holds_batch_interrupted`** (**bug-repro**) |
| Per-entity skip; summary exactly the four `_SUMMARY_ZERO` keys; ctx marker `{"error", "held": 1}`; no balance / rate-limit key; claim released | `_one` + `_note_provider_probe_outage` | **`::TestAst2098ProviderProbeOutage::test_run_unified_per_entity_skips_after_probe_failure`** |
| Chunk split: head held → tail chunks skipped | `_consult_chunk` | **`::…::test_run_unified_chunk_split_skips_tail_after_head_probe_failure`** |
| Full-batch call marks ctx, `held == 2` from the summary's `total_held` | full-batch branch | **`::…::test_run_unified_full_batch_marks_probe_outage`** |
| Loop stops after the outage run (`max_runs=0`; finite eligibility `[24,24,24,0]`) | `_run_dispatch_loop` | **`::…::test_run_dispatch_loop_stops_after_probe_outage_run`** |
| Probe outage alone → INTERRUPTED; with a rate-limit outage → FAILED; no alert, no `auto_run_error`, no breaker either way | `_dispatch_one_body` | **`::…::test_dispatch_one_probe_outage_status[False-INTERRUPTED/True-FAILED]`** (`True` is a guard, green both) |

Tag and hold nodes upstream: [`../external/llm_compat.md`](../external/llm_compat.md) § AST-2098, [`../external/openrouter.md`](../external/openrouter.md) § AST-2098, [`../utils/cost_calculator.md`](../utils/cost_calculator.md) § AST-2098, [`consult.md`](consult.md) § AST-2098, [`roster.md`](roster.md) § AST-2098.

**Kept:** `TestAst1867ProviderBalanceOutage`, `TestAst2010ProviderRateLimitOutage` (unchanged, green).

**Pre-existing drift (not AST-2098, left as-is):** the six touched modules carry the same failure set at the sub tip with and without this pass's tests (`TestCircuitBreaker::*` arity, roster `_is_verified_job_site_distinct` removed, etc.) — zero new failures; this pass fixes two (openrouter, below).

**Integration:** none — do not invent.

## QA test manifest (AST-2099)

1. **AST-2098 nodes + regressions** (**[bug-repro]** = `TestAst2098ProviderProbeOutage::test_bug_repro_probe_failure_holds_batch_interrupted`, red at `25c7ab095`, green with AST-2098):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst2098ProviderProbeOutage \
  tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage \
  tests/component/core/test_dispatcher.py::TestAst2010ProviderRateLimitOutage \
  tests/component/external/test_llm_compat.py::TestAst2098ProbeFailureTagged \
  tests/component/external/test_llm_compat.py::TestAst1959ProbeHostLock \
  tests/component/external/test_openrouter.py \
  tests/component/utils/test_cost_calculator.py \
  tests/component/core/test_consult.py::TestAst2098ProbeFailureHold \
  tests/component/core/test_consult.py::TestAst897HoldStateOnBalanceRefusal \
  tests/component/core/test_consult.py::TestAst2010RateLimitForwarding \
  tests/component/core/test_roster.py::TestAst2098ProbeFailureHold \
  tests/component/core/test_roster.py::TestAst1867BalanceHeldCounting \
  tests/component/core/test_roster.py::TestAst897HoldStateOnBalanceRefusal \
  -q
```

Expect **all passed** with AST-2098 product.

2. **Red check (test-fix):** `git restore --source 25c7ab095 --worktree -- src/`, run the **[bug-repro]** node → fails `assert 6 == 1`; then `git restore --worktree -- src/` → passes.

3. **No-regression:** the six touched test modules' failure set must not grow beyond the pre-existing drift above.

**Bible shasum (after publish):** `git show origin/sub/AST-2016/AST-2099-probe-fail-hold-gaps:docs/test-bible/core/dispatcher.md | shasum`

### AST-1879 · AST-1851 (skip gate on the task agent's server key)

**Primary manifest:** [`agent.md`](agent.md) § QA test manifest (AST-1879). `_dispatch_one_body` checks `candidate_api_keys[task_llm_server_id_or_none(task_key)]` **only when a server id comes back** (AST-1944). A non-LLM key (`agent_id` `"telescope"` / empty / no `agent_task` row — the AST-537 invariant) has no server and skips the key check; a missing candidate is still skipped. For an LLM key with no candidate, no map, an empty key, or only another platform's key, it skips: no ledger, plus a warning naming the server ("This task is not starting").

| Area | Source | Component tests |
| --- | --- | --- |
| No candidate → skip + server-naming warning, no ledger | `src/core/dispatcher.py` | `TestDispatchOne::test_skips_without_candidate_context` (now asserts; was assertion-free) |
| Missing / empty / other-platform key → skip (4 params) | same | `TestDispatchOne::test_skips_without_task_servers_api_key` (replaces `test_skips_without_api_key`) |
| Gate asks `task_llm_server_id_or_none(task_key)` which server to check | same | `TestDispatchOne::test_gate_reads_key_for_task_agents_server` |
| Revised — candidate stubs `candidate_api_key` → `candidate_api_keys: {"anthropic": …}`; autouse `_task_server_anthropic` pins `task_llm_server_id_or_none` → `"anthropic"` (AST-1945; no seeded agent_task rows in this file). Opt-out: request the `real_server_gate` fixture (fixture, not marker — `--strict-markers`) | `test_dispatcher.py` | 13 stubs across `TestDispatchOne`, `TestAst841…`, `TestAst1847…`, `TestAst1867…`, `TestAst1829ScheduledSweep` |
| AST-1944 — **`[bug-repro]`** non-LLM key (`telescope` / `empty_agent_id` / `no_row`) reaches `_run_dispatch_loop` with an empty key map on the **real** resolver (data layer patched: `agent_mod.get_agent_task` / `get_agent`) | same | `TestAst1944NonLlmGate::test_non_llm_key_reaches_handler_without_any_api_key` (3 params) |
| AST-1944 — non-LLM key + missing candidate → skip, warning server slot `None`; LLM key (`deepseek-v4` / Big) with only an anthropic key → skip naming `deepseek`; unknown real agent (`ghost`) → `ValueError` out of `_dispatch_one` | same | `TestAst1944NonLlmGate::{test_non_llm_key_missing_candidate_still_skipped,test_llm_key_without_server_key_still_skipped,test_unknown_real_agent_still_raises}` |

**Integration:** none.

### AST-1945 · AST-1943 (non-LLM gate tests + telescope sentinel — test gap for AST-1944)

**Publish:** `origin/sub/AST-1943/AST-1945-non-llm-gate-tests`. Test-only; product (`task_llm_server_id_or_none`, gated `_dispatch_one_body`, 12 `agent_task.json` rows `"n/a"` → `"telescope"`) landed by AST-1944 on `origin/ftr/AST-1943-non-llm-dispatch-key-gate`. Sentinel tuple is exactly `("", "telescope")` — no `"n/a"` transition tests. Helper unit tests: [`agent.md`](agent.md) § AST-1944.

Also in this pass: `test_repo_admin_json.py` sentinel asserts (L506 / L1378 / L1423) read `"telescope"`; `docs/uat-fixtures/AST-756/expected-agent_task.json` 12 `"agent_id": "n/a"` → `"telescope"` (literal replace, otherwise byte-identical) so `TestAst1269AliasAgentTaskSeedRestore::test_alias_identity_lockstep_with_fixture` is green. L1378 / L1423 stay red on pre-existing `task_seq` drift (`assert 3 == 5`, AST-1239 wipe) — out of scope.

## QA test manifest (AST-1945)

1. **`[bug-repro]` (must flip):** `test_dispatcher.py::TestAst1944NonLlmGate::test_non_llm_key_reaches_handler_without_any_api_key` — 3 params red on `origin/dev` product (`Agent 'telescope' … not found` / `has no agent_id assigned` / `No agent_task row`), green on ftr.
2. **Rest of the class + helper:** `TestAst1944NonLlmGate` (6) and `test_agent_ast1879.py::TestAst1944TaskLlmServerIdOrNone` (9) green.
3. **Retargeted stubs:** `TestDispatchOne` green (autouse fixture no longer errors at setup).
4. **Lockstep:** `TestAst1269AliasAgentTaskSeedRestore::test_alias_identity_lockstep_with_fixture` green; `rg -c '"n/a"' docs/uat-fixtures/AST-756/expected-agent_task.json` prints nothing.
5. **No new reds:** full `test_dispatcher.py` = the 12 pre-existing failures (`TestRunUnified` ×2, `TestCircuitBreaker` ×3, `TestAst841…` ×2, `TestAst802…`, `TestAst814…`, `TestTaskThreadTarget`, `TestAst1259…`, `TestAst1022…`); `test_repo_admin_json.py` failure set unchanged except the lockstep node going green.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1944NonLlmGate \
  tests/component/core/test_dispatcher.py::TestDispatchOne \
  tests/component/core/test_agent_ast1879.py \
  "tests/component/core/test_repo_admin_json.py::TestAst1269AliasAgentTaskSeedRestore::test_alias_identity_lockstep_with_fixture"
rg -c '"n/a"' docs/uat-fixtures/AST-756/expected-agent_task.json data/admin/agent_task.json
```

**Pass criterion:** narrowed run green — not the zero-arg harness / branch-lock gate (pre-existing reds above).

**Bible shasum (record after publish):** `git show origin/sub/AST-1943/AST-1945-non-llm-gate-tests:docs/test-bible/core/dispatcher.md | shasum`

### AST-1916 · AST-1875 (runtime AUTO-thread cap getter/setter + live tick read)

**Parent:** [AST-1875](https://linear.app/astralcareermatch/issue/AST-1875). **Publish:** `origin/sub/AST-1875/AST-1916-runtime-cap-api`. In-memory `_auto_thread_cap_override` (None = `ASTRAL_CONFIG["max_auto_threads"]`); `get_auto_thread_cap()` / `set_auto_thread_cap()` (strict `type(v) is int`, bounds from `max_auto_threads_min` / `_max`, raises `ValueError`, never cancels); `_tick_loop` computes `slots` from the getter every tick (capture-once `max_auto` removed). Admin routes: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1916. Config keys: [`../utils/config.md`](../utils/config.md) § AST-1916.

| AC | Source | Component tests |
| --- | --- | --- |
| getter default / override | `get_auto_thread_cap` | `tests/component/core/test_dispatcher.py::TestAst1916AutoThreadCap::{test_getter_falls_back_to_config_default,test_setter_accepts_in_range_and_getter_reports_it}` |
| 3 bounds + type confusion (0, 101, -1, `"abc"`, 2.5, `True`, `None`, `"5"`, 5.0) keep prior cap | `set_auto_thread_cap` | `::TestAst1916AutoThreadCap::test_setter_rejects_and_keeps_prior_cap` |
| 8 bounds read from config | same | `::TestAst1916AutoThreadCap::test_setter_bounds_come_from_config` |
| 5 / 6 raised cap applies next tick, no restart | `_tick_loop` | `::TestAst1916AutoThreadCap::test_tick_honours_raised_cap_on_next_tick` |
| 7 lowering below running: no spawn, registry intact, no cancel | `_tick_loop` | `::TestAst1916AutoThreadCap::test_lowering_below_running_spawns_none_and_cancels_none` |
| 6 capture-once line gone · 9 override initialised `None` (restart resets) | `src/core/dispatcher.py` | shell grep (manifest item 2) |

**Existing coverage (unchanged, must stay green):** `TestScheduler` tick tests set `cfg["max_auto_threads"]` with no override — getter falls through to that value. Class autouse `_reset_override` (monkeypatch) keeps setter writes from leaking into them.

**Broken / obsolete:** none. **Integration:** none — no scenario exercises the tick cap or the new routes.

## QA test manifest

1. **New + neighbours (required, green):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1916AutoThreadCap \
  tests/component/ui/api/test_api_admin.py::TestAst1916AutoThreadCapApi \
  tests/component/core/test_dispatcher.py::TestScheduler \
  tests/component/core/test_dispatcher.py::TestAst1022HonorAutoOffStageDispatch::test_tick_loop_calls_auto_off_debug_helper_before_spawn \
  tests/component/core/test_dispatcher.py::TestAst1829ScheduledSweep::test_tick_passes_sweep_flag_and_logs_sweep_due \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls \
  -q
```

Expect **40 passed** (27 new).

2. **AC 6 / AC 9 greps:**

```bash
grep -n 'max_auto = ASTRAL_CONFIG' src/core/dispatcher.py        # expect no output
grep -n '^_auto_thread_cap_override: Optional\[int\] = None' src/core/dispatcher.py   # expect 1 line
```

3. **Regression (no new reds):** `tests/component/core/test_dispatcher.py` + `tests/component/ui/api/test_api_admin.py` whole-file. **Baseline at QA time: 17 failures identical with `origin/dev` product and with AST-1916 product** (incl. `TestDispatchTasks::test_list_dispatch_tasks_and_keys`); AST-1916 adds 27 passes and zero failures. Pass = same failing set.
4. **Branch lock:** `src/core/dispatcher.py` + `src/ui/api/api_admin.py` (`LOCKED_AT_100`) — item 1 covers every new line/arc (`get_auto_thread_cap`, `set_auto_thread_cap`, `_auto_thread_cap_payload`, both routes). Zero-arg harness gate unreliable on this tip given item 3 baseline reds.

**Bible shasum (publish tip):** fill after `merge-tests` —
- `docs/test-bible/core/dispatcher.md`
- `docs/test-bible/ui/api/api_admin.md`
- `docs/test-bible/utils/config.md`

### AST-2025 · AST-2022 (`fetch_relative_jd` claim / release — AC6)

**New:** `TestRunUnified::test_ast2025_fetch_relative_jd_claims_trigger_state_and_releases_on_error` — claim by `RELATIVE_JOB_LINK` for the candidate with `states == ["RELATIVE_JOB_LINK", "RELATIVE_JOB_LINK_RETRY"]` only; `clear_job_batch(batch_id)` still runs when the runner raises; `dispatch_task_key` forwarded. Green on the pre-AST-2025 tree too (generic job path + AST-2024 config) — a regression guard, not a red-first node. Primary manifest: **`docs/test-bible/core/gazer.md`** § AST-2025.

### AST-2093 · AST-2012 (claimed position → `batch_index_offset`; retry re-claims counted once; test gap AST-2095)

`_run_unified` passes `batch_index_offset=ci * chunk_sz` on the chunk path and the entity's claimed index on the per-entity path (the full-batch call relies on the default 0). Each run records claimed ids in `ctx["dispatch_seen_ids"]` (falsy ids skipped). A normal return adds `repeat_processed = min(repeats, total_processed)`, which is not a `_SUMMARY_ZERO` key. `_run_dispatch_loop` subtracts it from `accumulated["total_processed"]`, but the `0 processed` stop still reads the raw per-run value. Primary block + manifest: [`agent.md`](agent.md) § AST-2093.

| Area | Component tests (`tests/component/core/test_dispatcher.py::TestAst2093BatchIndexDispatch`) |
| --- | --- |
| **[bug-repro]** 5 jobs, `batch_size=2`, `grade_get` → chunk offsets `{0: 0, 1: 2, 2: 4}` | **`test_bug_repro_chunks_send_global_offsets`** |
| **[bug-repro]** `batch_call_mode=0`, 3 jobs → offset = claimed index per entity | **`test_bug_repro_per_entity_sends_claimed_position`** |
| **[bug-repro]** same ctx, claims `[A,B]` then `[B,C]` → `repeat_processed` 0 then 1; seen `{A,B,C}` | **`test_bug_repro_reclaimed_ids_are_repeat_processed`** |
| Id-less entity never tracked (falsy-id arcs); outage-zeroed re-claim clamps to 0 (`min()`) | **`test_falsy_ids_never_tracked_and_outage_run_clamps_to_zero`** |
| **[bug-repro]** Somerset shape 27 + retry 23 (`repeat_processed` 23) → accumulated 27 / passed 4 / errors 23 | **`test_bug_repro_loop_counts_each_entity_once`** |
| All-repeat run (`3` processed, `3` repeat) does not trip the `0 processed` stop (guard) | **`test_all_repeat_run_does_not_trip_zero_processed_stop`** |

**Kept:** the five AST-2093 qa-handoff nodes (`test_ast505…`, `test_ast502_chunked…`, the two per-entity outage nodes, `test_run_unified_candidate_claim_gate`) — not touched. Every test builds its own `ctx`; no module-level `dispatch_seen_ids`.
