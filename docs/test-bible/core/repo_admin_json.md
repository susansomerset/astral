# Repo Admin JSON

**Test module:** `tests/component/core/test_repo_admin_json.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py` | no |

---

### AST-782 · AST-756

Repo-owned **`data/admin/agent.json`** and **`data/admin/agent_task.json`**: bare Copy Output arrays loaded at startup; export writes current DB rows back to disk. Not invoked from admin save paths.

| Area | Source | Component tests |
| --- | --- | --- |
| Missing / malformed file handling | `src/core/repo_admin_json.py` | `TestLoadRepoAdminJsonFile` |
| Transactional apply order (agent → agent_task) | `src/core/repo_admin_json.py` | `TestApplyRepoAdminJsonAtStartup::test_applies_agent_then_agent_task_on_one_connection` |
| Export UTF-8 round-trip files | `src/core/repo_admin_json.py` | `TestExportRepoAdminJsonToFiles` |

Data-layer SQL: **`docs/test-bible/data/database/agents.md`** and **`agent_tasks.md`**. Bootstrap wire: **`docs/test-bible/core/bootstrap.md`**.

---

### AST-783 · AST-756

**Divergence compare + revert:** normalized export-shape compare of live DB vs checked-in repo JSON; **`revert_repo_admin_json_table`** reuses AST-782 startup apply. Admin **`GET /api/admin/repo_json/status`**, **`POST /api/admin/repo_json/revert/<table_key>`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Scalar normalization + compare/revert | `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py::TestAst783RepoAdminJsonDivergence` |
| Admin HTTP routes | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi` |
| Shared banner + themed confirm | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` |

Routed pages: **`docs/test-bible/frontend/pages.md`** (**AST-783**).

**UAT seed (AST-786 / AST-878):** populated **38**-row catalog (includes **`fetch_culture_pages`**) — see **`docs/test-bible/data/database/agent_tasks.md`** (**AST-786**, **AST-878**).

**UAT seed (AST-787):** six agent personas — see **`docs/test-bible/data/database/agents.md`** (**AST-787**).

**Grouping on revert/startup (AST-790):** import forwards four grouping columns — see **`docs/test-bible/data/database/agent_tasks.md`** (**AST-790**).

---

### AST-793 · AST-756 (UAT bug)

**Product fix:** `apply_agent_task_repo_json_startup` writes repo JSON rows verbatim (including **`task_key_uuid`** and **`updated_at`**) via **`_apply_agent_task_repo_json_rows_exact`** so post-revert **`get_repo_admin_json_divergence_status`** clears **`agent_task.diverged`**. **`src/data/database.py` only** — compare/UI unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Revert clears divergence | `src/core/repo_admin_json.py`, `src/data/database.py` | `tests/component/core/test_repo_admin_json.py::TestAst793AgentTaskRevertDivergence::test_revert_clears_agent_task_divergence_after_db_edit` |
| Preserves file UUID | `src/data/database.py` | `TestAst793AgentTaskRevertDivergence::test_revert_preserves_repo_task_key_uuid` |
| Idempotent double revert | same | `TestAst793AgentTaskRevertDivergence::test_double_revert_agent_task_stays_not_diverged` |

**AST-793** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst793AgentTaskRevertDivergence \
  -q
```

**test-child scope gate (required):** `git show 05b4374 --name-only` — expect **only** `src/data/database.py` and `docs/features/foundation/ast-793-uat-divergence-banner-persists-after-revert-to-file.md` (no `data/admin/**`).

---

### AST-878 · AST-872 (UAT bug)

Repo **`agent_task.json`** catalog gains **`fetch_culture_pages`** — primary manifest in **`docs/test-bible/data/database/agent_tasks.md`** (**AST-878**).

---

### AST-880 · AST-879

**`vet_inflow_discovery`** repo JSON + UAT fixture carry AST-880 encoded A–F rubric marker — byte identity with **`docs/uat-fixtures/AST-756/expected-agent_task.json`** unchanged (**AST-786**). DB migration: **`docs/test-bible/data/database/agent_tasks.md`** / **`TestAst880VetInflowEncodedPromptMigration`**.
