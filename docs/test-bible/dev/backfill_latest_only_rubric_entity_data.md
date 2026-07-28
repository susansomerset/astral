# Backfill Latest-Only Rubric Entity Data (migration script)

**Test module:** `tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | `tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py` | no |

**Existing coverage (reuse):** latest-per-task via `list_entity_latest_agent_refs` — `docs/test-bible/data/database/agent_responses.md` (**AST-984**). Entity-row JSON columns and this CLI are **retired**.

---

### AST-727 (parent AST-717) — historical

One-time backfill collapsed duplicate **entity-row** `agent_responses` JSON refs. **Superseded by AST-984** (columns dropped; CLI exits 2).

### AST-984 · AST-975

**Scope:** CLI retired — prints AST-984 message, exit 2. Use `agent_data.entity_id` / `list_entity_latest_agent_refs`.

| Area | Source | Component tests |
| --- | --- | --- |
| CLI exit 2 + retired message | `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | `TestAst984BackfillEntityColumnsRetired` |

**AST-984** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
