# migrate_agent_data

**Test module:** `tests/component/scripts/test_migrate_agent_data.py`

### AST-981 · AST-975

**Scope:** Retire `scripts/migrations/migrate_agent_data.py` — no SELECT/JOIN against the standalone `agent_responses` table; CLI/`run_*` exit retired before any DB open.

| Area | Source | Component tests |
| --- | --- | --- |
| Module entrypoints raise retired SystemExit | `scripts/migrations/migrate_agent_data.py` | `TestAst981MigrateAgentDataRetired::test_module_entrypoints_exit_retired` |
| CLI exits 2 + stderr message | same | `TestAst981MigrateAgentDataRetired::test_cli_exits_2` |

**AST-981** narrowed run: see **`docs/test-bible/core/agent.md`** § AST-981.
