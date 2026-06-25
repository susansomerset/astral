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
