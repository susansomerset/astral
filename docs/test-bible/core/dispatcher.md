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

### AST-972 · AST-871

Primary manifest: **`docs/test-bible/core/candidate.md`** § AST-972. Dispatcher: **`ensure_candidate_stage_dispatch_tasks`** / **`provision_candidate_stage_dispatch_tasks`**; candidate claim gate in **`_run_unified`**; tick calls **`age_stale_candidate_states`**; **`start_scheduler`** provisions stage rows. Revised **`LIVE_PROMPTS` → `ACTIVE_SEARCH`** in dispatcher fixtures; AST-875 template fixture uses **`qualify_job_listings`** (TASK_CONFIG tip).


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

`ensure_meteorite_dispatch_tasks` / `provision_meteorite_dispatch_tasks` seed `METEORITE_DISPATCH_TASKS` rows (idempotent; twin keys `skipped_missing_config` until `TASK_CONFIG` has them); `start_scheduler` provisions after stage rows. **AST-1060** adds `retired` count + surgical delete of `evaluate_jd`@`METEORITE_NEW`. Config/consult primary: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/core/consult.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Ensure GDL + twin skip/insert; provision; scheduler hook | `src/core/dispatcher.py` | **`TestAst1054MeteoriteDispatchProvision`** (counts/trigger + retire revised **AST-1060**) |
| Stage scheduler stub | `src/core/dispatcher.py` | revised **`TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision`** (stubs meteorite provision) |

**Broken / obsolete:** AST-972 start_scheduler test — stub `provision_meteorite_dispatch_tasks` so the new try-path does not hit live DB; insert-count / evaluate_jd@METEORITE_NEW asserts revised by **AST-1060**.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  -q
```

### AST-1060 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1060-meteorite-qualified-qualify-meteorite-config-dispatch`.

`ensure_meteorite_dispatch_tasks` retires live `evaluate_jd`@`METEORITE_NEW` after insert (`retired` in return; provision sums it). Config primary: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Retire stale meteorite evaluate_jd row; insert counts | `src/core/dispatcher.py` | **`TestAst1054MeteoriteDispatchProvision`** (incl. `test_ensure_retires_stale_evaluate_jd_at_meteorite_new`) |

**Broken / obsolete:** AST-1054 insert counts / trigger assert — see above.

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
| Stage / meteorite scheduler stubs | `src/core/dispatcher.py` | revised **`TestAst972…::test_start_scheduler_invokes_stage_provision`**, **`TestAst1054…::test_start_scheduler_invokes_meteorite_provision`** (stub gaze provision) |

**Broken / obsolete:** start_scheduler unit helpers must stub `provision_gaze_email_dispatch_task` so the new try-path does not hit live DB.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestAst1088GazeEmailDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision::test_start_scheduler_invokes_meteorite_provision \
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
