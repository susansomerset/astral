# Agent

**Test module:** `tests/component/core/test_agent.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/agent.py` | `tests/component/core/test_agent.py` | yes |

---

### AST-455 · AST-453

Hop-to-hop **`chain_context`** uses **`CALLER_SYSTEM`**, **`CALLER_CACHE_A`**–**`D`**, **`CALLER_RESPONSE`** only ( **`{$CACHE_BLOCK_*}`** retired from **`TOKEN_SOURCES`** — literals pass through unresolved). **`do_task`** / **`preview_prompt`** assemble ≤5 ephemeral **`system`** blocks from resolved system + cache A–D; **`send_to_anthropic`** payloads store distinct **`CACHE_B`**/**`C`**/**`D`** **`agent_data`** rows when exercised.

| Area | Source | Component tests |
| --- | --- | --- |
| Assembly + caller hop dict | `src/core/agent.py` (`_assemble_blocks_seven_segment`, `_chain_tokens_for_next_hop`) | `tests/component/core/test_agent.py` (`TestAst455SevenSegmentAssembly`, `TestChainContext`, `TestPromptHelpers`) |
| **`TOKEN_SOURCES` / Manage Tasks picker** | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestManageTasksTokenPickerLookup`**, **`CALLER_*`**, **`get_manage_tasks_chain_tokens`**) |
| Admin chain token list endpoint | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (`test_list_tasks_and_tokens` — meta + chain **exactly** `get_tokens()` / `get_manage_tasks_chain_tokens()`) |

---

### AST-618 · AST-541

**AST-541 (parent):** Backfill **AST-538** §1.5.1 contract across **`src/core/agent.py`** **`do_task`** orchestration — generalized entry header (task key, batch id, index) before external LLM call; token overlay / job-context detail; assembly **`llm_params`** + block counts; truncated response payload via **`debug_detail_block`**; **`run_next`** hop boundary detail; retire hand-rolled **`[DEBUG]`** in touched blocks. **No Betty log-string tests** (parent + child explicit); Radia enforces instrumentation on review. **AST-597** resume-hop index lines generalized to all tasks via **`_do_task_debug_entry`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-618** | Contract debug across `do_task` entry/exit, token overlay, assembly, response payload, `run_next` boundary | `src/core/agent.py` | **`tests/component/core/test_agent.py`** (full file — **`LOCKED_AT_100`**); **`tests/component/utils/test_debug_logging.py`** + **`tests/component/utils/test_logging_batch.py`** (**§7.13zt** contract regression) |

**AST-618** narrowed run (pytest-only — instrumentation-only child; no new log-string assertions):

```bash
.venv/bin/python -m pytest tests/component/core/test_agent.py tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

Equivalent harness:

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py
```

**Manifest focus (existing coverage — no new tests):**

| Touched path | Existing tests |
| --- | --- |
| `do_task` entry header + batch/index detail | **`TestDoTask::test_debug_flag_passed_to_child`**; **`TestAst597MidChainResumeHydrationAndTransitions::test_resume_hop_debug_logs_agent_data_source_on_mid_chain_entry`** |
| Token overlay / caller hydration | **`test_resume_hop_debug_logs_agent_data_source_on_mid_chain_entry`** (asserts `caller_source` / `caller_hydration`, not golden index lines) |
| `run_next` hop boundary INFO (unchanged §1.5.1) | **`TestDoTask::test_hop_boundary_log_on_run_next`**; **`TestDoTask::test_chain_entry_log`** |
| Per-hop ledger + chain skip | **`TestAst531RunNextHopLedger`**; **`TestDoTask::test_mid_chain_empty_caller_skips_api`** |
| `debug=False` unchanged | **`TestDoTask`** paths without **`debug=True`**; full-file branch lock |

---

### AST-676 · AST-655

**`_validate_response_schema`:** int **`min`** / **`max`** bounds; reject **`bool`** masquerading as int. Nested **`criteria`** list items use shared craft rubric schema from **`config.py`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Int bounds + bool guard | `src/core/agent.py` | **`TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection`** |
| Craft rubric criteria validation | `src/core/agent.py` | **`TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema`** |

Config registry tests: **`TestAst676CraftRubricSchema`** in **`docs/test-bible/utils/config.md`** (**AST-676**).
