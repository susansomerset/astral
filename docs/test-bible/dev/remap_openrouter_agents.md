# Remap OpenRouter Agents (migration script)

**Test module:** `tests/component/scripts/test_remap_openrouter_agents.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/migrations/remap_openrouter_agents.py` | `tests/component/scripts/test_remap_openrouter_agents.py` | no |

**Catalog / mode SSOT:** [`../utils/config.md`](../utils/config.md) § AST-1947. **Agent `mode` column:** [`../data/database/agents.md`](../data/database/agents.md) § AST-1948.

---

### AST-1950 · AST-1946 (run-once agent remap: starting modes, new sizes, Kimi fold)

This is an operator CLI, run once per environment right after the AST-1946 deploy. It is a dry run by default, and `--apply` writes. Rows with no mode (NULL or `""`) get Creative if their pre-remap size is Big, otherwise Deterministic. A mode that is already set is kept. Each OpenRouter row's size moves to the one size in the literal `REMAP` snapshot (64 entries: 63 kept slugs plus `kimi-k2.6-openrouter` → `moonshotai/kimi-k2.6` / Little). Rows on the 12 `REMOVED` models keep their model and size; they are listed on every run but still get a mode. Direct models pass through. The DB seam is the module-level `_get_connection`, which the test monkeypatches onto a temp file DB built with the real `_ensure_agent_schema`.

| Area | Source | Component tests |
| --- | --- | --- |
| AC 13 dry run: the table is unchanged; output lists `morph/morph-v3-large` as removed, shows the planned Kimi fold, and reports 8 rows would change | `main([])` | `TestAst1950RemapOpenrouterAgents::test_ac13_dry_run_writes_nothing_and_lists_removed` |
| AC 13 `--apply`: exact eight-row result. The Kimi Big row becomes Creative even though the fold lands on Little. Every non-removed row passes `validate_brain_setting_for_model` + `validate_agent_mode`, and the removed slug is not in the catalog | `main(["--apply"])` | `…::test_ac13_apply_remaps_exact_rows_and_non_removed_validate` |
| A second `--apply` is a no-op: it prints only the removed-row line plus `No agent rows to change.`, and the table is unchanged | `main` | `…::test_second_apply_changes_nothing` |
| Plan decisions: a set mode is kept while the size is still remapped; `""` counts as no mode; an unchanged row is not printed or updated | `main` | `…::test_existing_mode_kept_size_still_remapped_and_blank_mode_filled` |
| Snapshot integrity against the AST-1947 catalog: 64 / 12 entries, the two tables don't overlap, each target is that model's only size, the Kimi fold row is present, removed slugs are absent from the catalog, and direct models are in neither table | `REMAP` / `REMOVED` | `…::test_snapshot_tables_match_ast1947_catalog` |

The proof that `REMAP ∪ REMOVED` equals the 76 OpenRouter ids from before the epic needs `origin/dev:src/utils/config.py`. That check is the engineer's build-time step (plan § Verification step 2, recorded in the plan Review), not a component test. Once AST-1946 lands, the pre-epic catalog is gone from `dev`.

Coverage: `--cov-branch` over the script reports only line 147 missing (the `if __name__ == "__main__"` exit).

**Broken / obsolete:** none. No product file changed.

**Integration:** none.

## QA test manifest (AST-1950)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/scripts/test_remap_openrouter_agents.py \
  -q
```

**Pass criterion:** narrowed run green (5 passed), not the zero-arg harness. On `origin/ftr/AST-1946-big-brain-openrouter` before this sub merges, the module fails to load because the script doesn't exist yet.
