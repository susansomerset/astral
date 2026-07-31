# Backfill Agent Data Refs (migration script)

**Test module:** `tests/component/scripts/test_backfill_agent_data_refs.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/backfill_agent_data_refs.py` | `tests/component/scripts/test_backfill_agent_data_refs.py` | no |

**Data-layer backfill:** `docs/test-bible/data/database/agent_data.md` (**AST-978**).

---

### AST-978 · AST-974

Operator CLI: default dry-run, `--execute` live, `--debug` §1.5.1 per-index trail; quiet without `--debug`. Never clears `block_data`.

| Area | Source | Component tests |
| --- | --- | --- |
| Default dry-run banner + summary JSON | `scripts/migrations/backfill_agent_data_refs.py` | `TestAst978BackfillAgentDataRefsCli::test_default_dry_run_prints_banner_and_summary` |
| `--execute` → `dry_run=False` | same | `TestAst978BackfillAgentDataRefsCli::test_execute_passes_dry_run_false` |
| `--debug` trail / quiet without | same | `TestAst978BackfillAgentDataRefsCli::test_debug_emits_index_lines_and_quiet_without` |
| errors → exit 1 | same | `TestAst978BackfillAgentDataRefsCli::test_errors_exit_nonzero` |

**AST-978** narrowed run: see `docs/test-bible/data/database/agent_data.md`.
