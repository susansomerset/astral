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
