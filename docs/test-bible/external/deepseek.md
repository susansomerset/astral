# Deepseek

**Test module:** `tests/component/external/test_deepseek.py`

### AST-493 · AST-494 · AST-491

**AST-491 (parent epic):** **`qa-astral`** treats **`origin/ftr/AST-491-support-other-ai-models-deepseek`** as the definitive tip for bible **`§7.13zd–§7.13ze`** (now `docs/test-bible/utils/config.md`, `external/deepseek.md`, etc.); **`origin/sub/AST-491/*`** sibling branches take the same blob via Betty publish (**§ Test Bible**).

**`src/external/deepseek.py`** (**`send_to_deepseek`**) implements **AST-493**; mocked **`do_task`** / **`run_adhoc`** contract lives in **`TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta`**. **`_add_timesheet_entry`** (**AST-494**) mirrors Anthropic rows into **`anthropic_timesheets`** plus **`agent_timesheets`**; listing reads **`agent_timesheets`** with **`agent_req_id`**. **`tests/component/data/database/test_timesheets.py`**, **`tests/component/core/test_timesheets.py`** assert **`record_timesheet_entry(agent_req_id=…)`** and list row shape.

Manifest (narrow **`AST-493`** + **`AST-494`**; includes **`AST-492`** **`do_task`** DeepSeek assertion):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/data/database/test_timesheets.py \
  tests/component/core/test_timesheets.py
```

### AST-903 · AST-900 (UAT fix)

JSON **`stop_reason == max_tokens`** hard-fail (no heal). Primary manifest: **`docs/test-bible/core/agent.md`** § AST-903.

| Area | Source | Component tests |
| --- | --- | --- |
| Fail-closed truncation | `src/external/deepseek.py` | **`TestAst903JsonMaxTokensHardFail`** |
