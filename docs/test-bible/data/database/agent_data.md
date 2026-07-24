# Agent Data

**Test module:** `tests/component/data/database/test_agent_data.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/data/database.py` (`agent_data` schema / save / get / resolve) | `tests/component/data/database/test_agent_data.py` | no |

---

### AST-392

Baseline `save_agent_data` / `get_agent_data_by_batch` smoke (invalid `block_type`; save+read).

| Area | Source | Component tests |
| --- | --- | --- |
| Invalid block_type | `src/data/database.py` | `TestSaveAgentData::test_rejects_invalid_block_type` |
| Save + batch read | `src/data/database.py` | `TestSaveAgentData::test_saves_and_reads_batch_blocks` |

### AST-977 · AST-974

Nullable `ref_agent_data_id` on `agent_data`: every content write creates an audit row; identical logical `block_data` sets ref → earliest canonical and omits payload; reads resolve refs to plain text; cycle/missing ref raise. Historical backfill is **AST-978** (out of scope). Agent found/recorded debug: **`docs/test-bible/core/agent.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Schema ensure (fresh + ALTER) | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_ensure_schema_adds_ref_column_on_fresh_and_legacy` |
| Match → ref earliest + omit payload; block_type may differ | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_identical_write_refs_earliest_and_omits_payload` |
| Resolve by id / batch / ids | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_reads_resolve_ref_to_plain_text` |
| PK retry → `duplicate_id` | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_duplicate_primary_key_returns_duplicate_id` |
| Missing ref / cycle raise | `src/data/database.py` | `TestAst977AgentDataSelfRefDedupe::test_resolve_raises_on_missing_ref_and_cycle` |
| Obsolete bool return assert | `tests/component/data/database/test_agent_data.py`, `test_rubric_vectors.py` | revised — `save_agent_data` returns outcome dict |

**AST-977** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py \
  tests/component/data/database/test_rubric_vectors.py::TestFeedbackBlockType \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
