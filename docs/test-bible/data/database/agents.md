# Agents

**Test module:** `tests/component/data/database/test_agents.py`

---

### AST-492 · AST-495 · AST-491

**`save_agent`** / **`get_agent`** / **`list_agents`** — **`brain_setting`** column required on insert; migration off legacy **`model_code`**. Full **AST-492** epic (tier helpers, **`do_task`**, admin CRUD, Manage Agents UI) lives in **`docs/test-bible/ui/api/api_admin.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Agent persistence + insert requires **`brain_setting`** | `src/data/database.py` | **`tests/component/data/database/test_agents.py`** |

Narrow manifest (**agents cluster**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agents.py
```

---

### AST-782 · AST-756

**Repo-wins startup upsert for `agent`:** upsert rows from JSON; delete agents absent from payload. Export selects configured columns only (excludes legacy `model_code`).

| Area | Source | Component tests |
| --- | --- | --- |
| Upsert / update / delete-not-in-json | `src/data/database.py` | `TestAst782AgentRepoJsonStartup::test_apply_upserts_updates_and_deletes_absent_agents` |
| Export column policy | `src/data/database.py` | `TestAst782AgentRepoJsonStartup::test_fetch_export_rows_use_repo_columns` |
| Row shape validation | `src/data/database.py` | `TestAst782AgentRepoJsonStartup::test_rejects_wrong_row_keys` |

---

### AST-787 · AST-756 (UAT bug)

**Data-only:** Replace empty **AST-782** `data/admin/agent.json` with six persona rows mapped from **`docs/uat-fixtures/AST-756/expected-agent.json`** (repo column shape — **`model_code` stripped**, sorted by `agent_id`). No `src/**` changes.

| Area | Source | Component tests |
| --- | --- | --- |
| Fixture mapping + 6-id catalog | `data/admin/agent.json`, `docs/uat-fixtures/AST-756/expected-agent.json` | `tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed` |
| Startup import smoke | `src/core/repo_admin_json.py`, `src/data/database.py` | `TestAst787AgentRepoJsonSeed::test_startup_apply_loads_all_six_agents` |

**AST-787** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst787AgentRepoJsonSeed \
  -q
```

**test-child scope gate (required):** `git show 1c8364e --name-only` — expect **only** `data/admin/agent.json` and `docs/features/foundation/ast-787-uat-agent-json-empty-seed-six-agent-personas.md` under `code(AST-787)` (no `src/`).

### AST-1878 · AST-1851 (agent model_id + per-model brain validation)

**Primary manifest:** **`docs/test-bible/data/database/candidates.md`** § AST-1878.

| Area | Source | Component tests |
| --- | --- | --- |
| New — `model_id` save/update/list, catalog SKU as `model_code` / `resolved_model_key` (None without model), per-model size check on insert/update/`update_agent`, repo JSON `model_id` required + size check before writes | `src/data/database.py` | `TestAst1878AgentModelField` |
| Revised — repo JSON row helper carries `model_id` (default `claude`) | fixture | `_agent_repo_row` → `TestAst782AgentRepoJsonStartup` |

### AST-1948 · AST-1946 (agent `mode` column; `temperature` / `model_code` dropped)

**Primary manifest:** **`docs/test-bible/core/agent.md`** § AST-1948.

`save_agent(agent_id, content, *, mode, …)` requires a valid mode on every write (insert and update) and has no `temperature` parameter. `update_agent` allows only {content, model_id, brain_setting, mode, max_tokens} and validates `mode` when it is passed. `_ensure_agent_schema` adds `mode` and drops `temperature` / `model_code` (native `ALTER TABLE … DROP COLUMN`). It is DDL only, so existing rows keep their data with `mode` NULL until AST-1950. `_expose_agent_public` no longer sets `model_code`. `resolved_model_key` is the catalog SKU and does not depend on mode, so mode-less rows still list. The repo JSON loader validates `mode` per row before any write.

| Area | Source | Component tests |
| --- | --- | --- |
| New — AC 2 / 7: schema ensure on the pre-1948 table (with `model_code` + `temperature` and a live row). `PRAGMA table_info` shows `mode` and neither old column; content / max_tokens are kept; `mode` is None; the SKU still resolves; the row still lists | `_ensure_agent_schema`, `get_agent`, `list_agents` | `TestAst1948AgentModeColumn::test_schema_ensure_drops_retired_columns_and_adds_mode` |
| New — `save_agent` `"Wild"` on insert (nothing written) and on update (row unchanged) | `save_agent` | `…::test_save_agent_rejects_unknown_mode` |
| New — `update_agent` mode Creative ok; `"Wild"` / None raise; `temperature` / `model_code` kwargs ignored (rowcount 0) | `update_agent` | `…::test_update_agent_mode_validated_and_retired_keys_ignored` |
| New — repo JSON `"Wild"` (row 2) / None mode raise; an old-shape row (`temperature` instead of `mode`) fails the key check; nothing written | `apply_agent_repo_json_startup` | `…::test_repo_json_rejects_bad_or_missing_mode` |
| Revised — every `save_agent` call passes `mode`. Insert/update round-trip mode, and the row has no `temperature` / `model_code` | `save_agent` / `get_agent` / `list_agents` | `TestSaveAgent`, `TestListAgents`, `TestDeleteAgent`, `TestCountAgentTaskRefs`, `TestAst782AgentRepoJsonStartup`, `TestAst1878AgentModelField` |
| Revised — `_agent_repo_row` `temperature` → `mode` (default Deterministic). Apply/export carry mode | fixture | `TestAst782AgentRepoJsonStartup` |
| Revised — `model_code` assertions → `"model_code" not in row`. `resolved_model_key` is the only SKU field | `_expose_agent_public` | `TestAst1878AgentModelField::test_save_with_model_exposes_catalog_sku` · `::test_model_less_row_exposes_no_sku_and_uses_global_tiers` |

Tool note: the workspace `.cursorignore` has an unanchored `data/` rule, so it also matches `tests/component/data/` and `docs/test-bible/data/`. Editor file tools refuse those paths, but shell and git work normally.

**Integration:** none.

### AST-1955 · AST-1953 (plain agent settings; `brain_setting` / `mode` retired from writes)

**Primary manifest:** [`../../utils/config.md`](../../utils/config.md) § AST-1955.

The agent row carries seven optional settings — `quantization` TEXT, `temperature` REAL, `reasoning_effort` TEXT, `provider_allow_fallbacks` INTEGER (bool), `provider_only` / `provider_ignore` TEXT (JSON array), `provider_sort` TEXT — type-checked only (`_check_agent_setting`; a bool is not a temperature; list items must be str; no vocabulary, no per-model check). `save_agent(agent_id, content, *, model_id, max_tokens, <settings>)`: nothing required; new rows default `provider_allow_fallbacks` True (in code, not SQL `DEFAULT`); on an existing row `None` leaves a column as is. `update_agent` allow-list = content / model_id / max_tokens / settings; `None` clears. `model_id` keeps its non-empty + catalog check. `_ensure_agent_schema` adds the setting columns, drops only `model_code`, and leaves `brain_setting` / `mode` for the **AST-1958** migration (DDL only, no backfill). `get_agent` / `list_agents` return only public columns, with list settings decoded and `resolved_model_key` = catalog SKU or None (a retired id like `claude` lists instead of raising). Repo JSON: validation runs model + type checks before any write; list settings travel as JSON-array text; export keeps bools as bools.

| Area | Source | Component tests |
| --- | --- | --- |
| New — wrong type rejected on `save_agent` (nothing written), `update_agent`, repo JSON (row number) — 8 cases incl. bool temperature, non-str list item | `_check_agent_setting` | `TestAst1955AgentSettings::test_wrong_type_rejected_on_every_write` |
| New — any right-typed value accepted (no vocabulary); empty list kept | `save_agent` / `get_agent` | `…::test_any_value_of_the_right_type_is_accepted` |
| New — `update_agent` sets / clears (`None`); `brain_setting` / `mode` / `model_code` kwargs ignored (rowcount 0) | `update_agent` | `…::test_update_agent_sets_clears_and_ignores_retired_keys` |
| New — `save_agent` no longer accepts `brain_setting` / `mode` | `save_agent` | `…::test_retired_kwargs_rejected_by_save_agent` |
| New — schema ensure on the pre-1955 table (`brain_setting`, `mode`, `model_code`, row on `claude`): settings added, `model_code` dropped, `brain_setting` / `mode` kept with data, no backfill, not in the API row, retired id lists with SKU None | `_ensure_agent_schema` / `_expose_agent_public` | `…::test_schema_ensure_on_pre_1955_table` (replaces `TestAst1948…::test_schema_ensure_drops_retired_columns_and_adds_mode`) |
| New — AC 8: checked-in seed applies and exports back equal; DB edit diverges; Revert-to-file restores Grace (0.2, no sort, `deepseek-v4-pro`) | `apply_agent_repo_json_startup` / `fetch_agent_repo_json_export_rows` / `repo_admin_json.revert_repo_admin_json_table` | `…::test_seed_round_trips_and_revert_restores_it` |
| Revised — insert/update round-trip of settings (`None` leaves, 0.0 written); insert needs nothing and defaults fallbacks true | `save_agent` / `get_agent` | `TestSaveAgent::test_insert_and_update` · `::test_insert_without_settings_defaults_fallbacks_true` (replaces `test_insert_requires_brain_setting`) |
| Revised — list view decodes settings; delete / task refs without retired kwargs | `list_agents` etc. | `TestListAgents`, `TestDeleteAgent`, `TestCountAgentTaskRefs` |
| Revised — `_agent_repo_row` = AST-1955 repo shape (per-SKU default model, list settings as JSON text); apply / export carry settings (bool stays bool, list stays text) | fixture / repo JSON | `TestAst782AgentRepoJsonStartup` (2 revised) |
| Revised — model check kept: per-SKU SKU exposure, model-less row, blank / unknown / retired id (`claude`, `deepseek-v4`) rejected on save, update, repo JSON | `_check_agent_model_id` | `TestAst1878AgentModelField` (5; size-check tests dropped) |
| Retired — AST-1948 mode validation (no `mode` column on writes) | — | `TestAst1948AgentModeColumn::test_save_agent_rejects_unknown_mode` · `::test_update_agent_mode_validated_and_retired_keys_ignored` · `::test_repo_json_rejects_bad_or_missing_mode` |
| Retired — AST-1878 per-model size checks | — | `TestAst1878AgentModelField::test_save_insert_rejects_size_model_lacks` · `::test_save_update_rechecks_effective_pair` · `::test_model_less_row_exposes_no_sku_and_uses_global_tiers` (→ `test_model_less_row_exposes_no_sku`) |

**Integration:** none.
