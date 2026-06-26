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
