# Bootstrap

**Test module:** `tests/component/core/test_bootstrap.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py` | no |

---

### AST-782 · AST-756

**Repo-owned admin JSON (historical AST-782):** boot once called `apply_repo_admin_json_at_startup()` after `_validate_runtime_coupling()`. **AST-1502 / AST-1497 kill-switch:** that boot wire is removed — see **§ AST-1502** below. Export / explicit apply paths remain.

**AST-843 (parent AST-842):** `bootstrap_runtime()` calls `database.ensure_all_upsert_registry_schemas_at_startup()` — idempotent lazy schema ensure for every `_UPSERT_LAZY_SCHEMA_HANDLERS` table before the scheduler. **AST-1497** strips content migrates from ensure bodies (DDL-only); coverage: **§ AST-1502**.

| Area | Source | Component tests |
| --- | --- | --- |
| Bootstrap ordering | `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py::TestBootstrapRuntime::test_runs_validation_schema_ensure_and_scheduler_in_order` (**AST-1502** revise) |
| Registry-wide startup schema ensure | `src/data/database.py` (`ensure_all_upsert_registry_schemas_at_startup`) | `tests/component/data/test_database.py::TestAst843BootstrapSchemaEnsure::test_ensure_all_upsert_registry_schemas_at_startup_idempotent` |
| File load / export / startup orchestration | `src/core/repo_admin_json.py` | `tests/component/core/test_repo_admin_json.py` (full file; boot apply = **AST-1502**) |
| Config paths + apply order | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig` |
| Agent repo upsert + export | `src/data/database.py` | `tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup` |
| Agent_task repo upsert + export | `src/data/database.py` | `tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup` |

**Broken / obsolete:** pre-kill-switch `test_runs_validation_sync_and_scheduler_in_order` (expected `repo_json` + `sync_agent_tasks`) — rewritten **AST-1502**.

**AST-843** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/data/test_database.py::TestAst843BootstrapSchemaEnsure \
  -q
```

**AST-782** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/core/test_repo_admin_json.py \
  tests/component/utils/test_config.py::TestAst782RepoAdminJsonConfig \
  tests/component/data/database/test_agents.py::TestAst782AgentRepoJsonStartup \
  tests/component/data/database/test_agent_tasks.py::TestAst782AgentTaskRepoJsonStartup \
  -q
```

See also **`docs/test-bible/ui/server.md`** (**AST-654** pipeline row — bootstrap entry point unchanged; ordering extended by AST-782).

---

### AST-960 · AST-957

**Scope:** Drop bootstrap inventory over deleted **`DISPATCH_SCHEDULABLE_TASK_KEYS`**. `_validate_runtime_coupling` checks LLM env + `get_task_keys()` ⊆ `TASK_CONFIG` only — gap keys (`fetch_jd`, `prefilter`, …) must not force boot failure.

| Area | Source | Component tests |
| --- | --- | --- |
| Coupling without frozenset | `src/core/bootstrap.py` | `tests/component/core/test_bootstrap.py::TestValidateRuntimeCoupling` (incl. `test_passes_with_live_task_config_without_gap_key_inventory`) |
| Pipeline order | same | `::TestBootstrapRuntime::test_runs_validation_schema_ensure_and_scheduler_in_order` (**AST-1502**) |

**Broken / obsolete (Betty revision this pass):**
- `test_raises_when_dispatch_key_missing_from_task_config` — deleted (inventory loop gone).
- Frozenset monkeypatches on empty/orphan/aligned cases — removed.

**AST-960** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_bootstrap.py \
  tests/component/utils/test_config.py::TestAst960DropSchedulableFrozensetInventory \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover \
  tests/component/utils/test_config.py::TestAst702PrefilterBatchConfig \
  tests/component/utils/test_config.py::TestAst719FetchJobPagesConfig \
  tests/component/utils/test_config.py::TestAst701FetchWebsiteConfig \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers \
  tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys \
  tests/component/ui/api/test_api_admin.py::TestAst960TaskKeysNoFrozensetInventory \
  tests/component/ui/api/test_api_admin.py::TestAst955AlignScheduledActionsSave \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

Config / admin bible: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/ui/api/api_admin.md`** (**AST-960**).

---

### AST-1502 · AST-1492 (gap — bootstrap kill-switch test hole)

**Parent:** [AST-1492 — Updates to candidate are happening when we deploy](https://linear.app/astralcareermatch/issue/AST-1492). **Sibling product:** AST-1497. **Publish:** `origin/sub/AST-1492/AST-1502-cover-bootstrap-kill-switch-test-hole`.

Board REVISE on AST-1497 (copied to this gap): revise bootstrap order + `TestApplyRepoAdminJsonAtStartup` for kill-switch; add repro that `_ensure_candidate_schema` leaves live `ARTIFACTS_READY` without content migrates.

| Area | Source | Component tests |
| --- | --- | --- |
| Boot order without repo-JSON / sync | `src/core/bootstrap.py` | **`TestBootstrapRuntime::test_runs_validation_schema_ensure_and_scheduler_in_order`** |
| Startup apply unconditional no-op | `src/core/repo_admin_json.py` | **`TestApplyRepoAdminJsonAtStartup::test_startup_apply_is_noop_on_all_deploy_envs`** — see **`docs/test-bible/core/repo_admin_json.md`** |
| Ensure leaves live candidate content | `src/data/database.py` (`_ensure_candidate_schema`) | **`TestAst1502EnsureLeavesLiveCandidateContent::test_ensure_candidate_schema_leaves_artifacts_ready_without_content_migrates`** (**[bug-repro]**) — see **`docs/test-bible/data/database/candidates.md`** |

**Broken / obsolete this pass:** `test_runs_validation_sync_and_scheduler_in_order`; `TestApplyRepoAdminJsonAtStartup::test_applies_agent_then_agent_task_on_one_connection` (+ local-only skip as sole no-op case).

**Integration:** none revised; do not invent new integration coverage.

## QA test manifest

1. Ensure leaves ARTIFACTS_READY / no content migrates (**[bug-repro]**): `tests/component/data/database/test_candidates.py::TestAst1502EnsureLeavesLiveCandidateContent::test_ensure_candidate_schema_leaves_artifacts_ready_without_content_migrates`
2. Bootstrap kill-switch order: `tests/component/core/test_bootstrap.py::TestBootstrapRuntime::test_runs_validation_schema_ensure_and_scheduler_in_order`
3. Repo JSON boot no-op: `tests/component/core/test_repo_admin_json.py::TestApplyRepoAdminJsonAtStartup`

**AST-1502** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1502EnsureLeavesLiveCandidateContent \
  tests/component/core/test_bootstrap.py::TestBootstrapRuntime::test_runs_validation_schema_ensure_and_scheduler_in_order \
  tests/component/core/test_repo_admin_json.py::TestApplyRepoAdminJsonAtStartup \
  -q
```

**Pass criterion:** nodes fail on pre-fix product tree (boot still wires repo-JSON/sync; ensure still calls content migrates); flip green after AST-1497 `make-fix`.
