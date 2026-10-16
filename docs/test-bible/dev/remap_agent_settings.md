# Remap Agent Settings (migration script)

**Test module:** `tests/component/scripts/test_remap_agent_settings.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/remap_agent_settings.py` | `tests/component/scripts/test_remap_agent_settings.py` | no |

**Catalog / resolver SSOT:** [`../utils/config.md`](../utils/config.md) § AST-1955. **Agent setting columns:** [`../data/database/agents.md`](../data/database/agents.md) § AST-1955.

---

### AST-1958 · AST-1953 (run-once migration of live agent rows)

This is an operator CLI, run once per environment right after the AST-1953 deploy. It is a dry run by default and `--apply` writes. It moves every agent row onto per-SKU model ids and plain settings, then drops `brain_setting` and `mode` in the same transaction. It knows the old world only through literal 2026-10-03 snapshots: `SKU_IDS` (6 rows), `CAN_THINK` (58 ids) and `MODE_TEMPERATURE`. A row with no mode (NULL or `""`) counts as Creative if Big, otherwise Deterministic. A call "thought" only on Creative with a `CAN_THINK` id, so the temperature is empty there and otherwise the mode's 0.2 / 0.6. `reasoning_effort` is `"none"` only for a `CAN_THINK` id that didn't think. Every row gets `provider_allow_fallbacks` 1, and quantization and the provider lists are explicitly emptied. The DB seam is the real `_get_connection`, pointed at a temp file with `DB_PATH` and the `_agent_schema_ensured` flag reset, starting from the pre-AST-1955 legacy table (no setting columns).

| Area | Source | Component tests |
| --- | --- | --- |
| AC 11 dry run: rows and columns are unchanged (no setting columns added), and the exact per-row planned-change lines plus the "6 row(s) would change" summary are printed | `main([])` | `TestAst1958RemapAgentSettings::test_ac11_dry_run_writes_nothing_and_prints_each_planned_change` |
| AC 11 `--apply`, via `main()` reading `sys.argv`: the exact six-row result (null-mode row = the plan's hand-check row, Big on `openai/gpt-oss-120b`), and `PRAGMA table_info(agent)` lists no `brain_setting` or `mode` | `main()` | `…::test_ac11_apply_writes_exact_rows_and_drops_both_columns` |
| Idempotence by column presence: once the columns are gone, a dry run and `--apply` each print only `brain_setting / mode already dropped. Nothing to migrate.` and change nothing | `main` | `…::test_second_run_reports_already_dropped_and_changes_nothing` |
| Plan decisions, on a table that already has setting columns with stray values (all overwritten): every `SKU_IDS` row; an unexpected size on `claude` keeps its id; the deepseek-v4 floor applies to Big only and a larger stored value wins; kimi 32000 fills only an empty `max_tokens`; null mode on a non-Big row → Deterministic; `""` counts as no mode | `main(["--apply"])` | `…::test_plan_decision_rows_and_settings_already_written_are_overwritten` |
| UPDATE + both drops are one transaction: an index on `mode` makes the second drop fail, and every legacy column and value survives | `main(["--apply"])` | `…::test_failed_drop_rolls_back_the_whole_migration` |
| An unknown non-null mode raises `KeyError` in both the dry run and `--apply` before any write or DDL | `main` | `…::test_unknown_mode_raises_before_anything_writes` |
| Snapshot sanity: 58 `CAN_THINK` ids (kimi in; claude and deepseek-v4 out); `SKU_IDS` covers only the two retired ids, which are absent from today's catalog, and every target is in `LLM_MODEL_CONFIG`; the mode temperatures | `SKU_IDS` / `CAN_THINK` / `MODE_TEMPERATURE` | `…::test_snapshot_tables` |

The proof that `CAN_THINK` equals the AST-1947 `reasoning-capable` column needs the pre-epic `config.py`, which is gone on this sub. That check is the engineer's build-time step (plan § Old-world rules), not a component test.

Mutation-checked: adding a `commit()` before the drops fails the rollback test, and running `_ensure_agent_schema` in the dry run fails the dry-run test.

Coverage: `--cov-branch` over the script reports only line 155 missing (the `if __name__ == "__main__"` exit).

**Broken / obsolete:** `tests/component/scripts/test_remap_openrouter_agents.py` and `dev/remap_openrouter_agents.md` (AST-1950) are deleted. They load the deleted `scripts/migrations/remap_openrouter_agents.py` and so fail at collection.

**Sequencing:** on this sub, `test_backfill_collapse_blank_lines.py` fails to collect with the `resolve_model_brain` ImportError until **AST-1956** lands (same break as [`../utils/config.md`](../utils/config.md) § AST-1955 Sequencing). Not this ticket's.

**Integration:** none.

## QA test manifest (AST-1958)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_remap_agent_settings.py
```

**Pass criterion:** narrowed run green (7 passed), not the zero-arg harness.

**Bible shasums (after publish):** `for p in dev/remap_agent_settings.md; do git show origin/sub/AST-1953/AST-1958-migrate-agent-settings:docs/test-bible/$p | shasum; done`
