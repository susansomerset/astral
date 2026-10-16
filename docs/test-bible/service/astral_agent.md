# Astral Agent service (`service/astral_agent/`)

**Test modules:** `tests/component/service/test_astral_agent_*.py`

Isolated FastAPI Postgres queue consumer — **not** under `src/`. Flat imports (`from settings import …`); component conftest swaps `service/astral_agent/` onto `sys.path` (Telescope uses the same flat names — purge before swap). No `LOCKED_AT_100` (coverage gate is `--cov=src` only).

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| Tree / Dockerfile / requirements / ban greps | `tests/component/service/test_astral_agent_fence.py` | no |
| Settings, stub executor, result codec, claim/lease/terminal | `tests/component/service/test_astral_agent_queue.py` | no |
| `app.py` `/healthz` + `/wake` | `tests/component/service/test_astral_agent_app.py` | no |
| Railway Phase 1 + fence extension | `tests/component/service/test_astral_agent_deploy_ci.py` | no |

**Integration tier:** no existing `tests/integration/` scenario exercises astral-agent (platform client is sibling **AST-2238**). No integration revision this pass.

---

### AST-2237 · AST-2235 (astral-agent queue schema and worker skeleton)

**Scope:** Stand up `service/astral_agent/` — `agent_job` / `agent_worker` DDL + claim/lease/NOTIFY, stub executor, FastAPI `/healthz` + `/wake`, Dockerfile + requirements. No platform client, no provider HTTP, no Railway/CI fence (siblings).

| Area | Component tests |
| --- | --- |
| Service tree + Dockerfile + requirements pins | `test_astral_agent_fence.py::TestAst2237ServiceTree`, `…::TestAst2237DockerfileAndRequirements` |
| Zero `src` imports + AC3/AC5 ban strings | `test_astral_agent_fence.py::TestAst2237ImportAndBanFence` |
| Required `ASTRAL_DATABASE_URL` (crash loud) + tunables | `test_astral_agent_queue.py::TestAst2237Settings` |
| Stub executor echo / non-dict | `test_astral_agent_queue.py::TestAst2237Executor` |
| zlib JSON result codec + SKIP LOCKED contract | `test_astral_agent_queue.py::TestAst2237ResultCodec` |
| Insert→claim→stub terminal `done` | `…::TestAst2237ClaimLeaseTerminal::test_insert_claim_complete_stub_terminal` |
| Dual-replica: second claim empty while leased | `…::test_dual_replica_second_claim_empty_while_leased` |
| Stub crash → terminal `failed` / `stub_error` | `…::test_stub_crash_writes_failed_terminal` |
| `/healthz` ok / asleep / unhealthy; `/wake`; no auth | `test_astral_agent_app.py::TestAst2237HealthzAndWake` |

**AC2 harness note:** claim/lease/terminal uses an in-memory store that mirrors `status=queued` eligibility (same dual-replica rule as `FOR UPDATE SKIP LOCKED`). Live Postgres is not required for the component harness; SQL contract asserts `FOR UPDATE SKIP LOCKED` + `agent_job` table name.

## QA test manifest

1. **Fence (AC1/AC3/AC5):** `tests/component/service/test_astral_agent_fence.py`
2. **Queue / settings / executor / AC2 claim-lease-terminal:** `tests/component/service/test_astral_agent_queue.py`
3. **App health/wake (AC4 openness):** `tests/component/service/test_astral_agent_app.py`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_astral_agent_fence.py \
  tests/component/service/test_astral_agent_queue.py \
  tests/component/service/test_astral_agent_app.py \
  -q
```

**Pass criterion:** pytest green on the three paths — not zero-arg harness / branch-lock gate.

**Broken / obsolete:** none (new service; no deleted modules).

**Out of scope:** live Postgres dual-replica race, platform client (**AST-2238**), provider wrappers (**AST-2239**). Railway/CI owned by **AST-2241** below.

**Bible shasum (publish tip `8f385ce71`):** `931ca561cc9499a6fe0a896b6f7d568b13b71df7  -`

---

### AST-2241 · AST-2235 (Railway Phase 1 + import-fence extension)

**Scope:** `service/astral_agent/railway.toml` (Phase 1 replicas, Dockerfile builder, 1 GiB, `/healthz`, drain); widen `scripts/ci/check-service-src-import-fence.sh` to all `service/**/*.py`; rename workflow step to full service↔src fence. No app/provider/client code.

| Area | Component tests |
| --- | --- |
| railway.toml Phase 1 contract | `test_astral_agent_deploy_ci.py::TestAst2241RailwayPhase1Toml` |
| Fence green + probe under `service/astral_agent/` | `test_astral_agent_deploy_ci.py::TestAst2241ImportFenceExtension` |
| Workflow step title | `…::test_workflow_step_names_full_service_fence` |
| Telescope healthcheck assert (obsolete AST-1727) | `test_telescope_deploy_ci.py::TestRailwayPhase1Toml::test_healthcheck_and_no_phase2_hooks` |
| Fence ok wording regression | `test_telescope_deploy_ci.py::TestBidirectionalImportFence::test_ci_fence_script_exits_zero` |

## QA test manifest

1. **Astral-agent Railway + fence (required):** `tests/component/service/test_astral_agent_deploy_ci.py`
2. **Telescope deploy/fence revise (required):** `tests/component/service/test_telescope_deploy_ci.py`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_astral_agent_deploy_ci.py \
  tests/component/service/test_telescope_deploy_ci.py \
  -q
```

**Pass criterion:** pytest green on both paths — not zero-arg harness / branch-lock gate.

**Broken / obsolete revised:** `TestRailwayPhase1Toml::test_no_healthcheck_path_and_no_phase2_hooks` → `test_healthcheck_and_no_phase2_hooks` (live Telescope toml has `healthcheckPath`; AST-2241 mirrors that for astral-agent).

**Out of scope:** Judoscale / Phase-2 autoscaler, live Railway dashboard, AST-2237–2240 product logic.

**Bible shasums (publish tip `edc4cded6`):**
- `docs/test-bible/service/astral_agent.md` — `c30f52ecaac0747919975f428fe0aafcdda30e90  -`
- `docs/test-bible/service/telescope.md` — `03454db08734dc5a50d1b13f177981d81db62d59  -`
