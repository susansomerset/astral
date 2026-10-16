# Astral Agent service (`service/astral_agent/`)

**Test modules:** `tests/component/service/test_astral_agent_*.py`

Isolated FastAPI Postgres queue consumer — **not** under `src/`. Flat imports (`from settings import …`); component conftest swaps `service/astral_agent/` onto `sys.path` (Telescope uses the same flat names — purge before swap). No `LOCKED_AT_100` (coverage gate is `--cov=src` only).

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| Tree / Dockerfile / requirements / ban greps | `tests/component/service/test_astral_agent_fence.py` | no |
| Settings, stub executor, result codec, claim/lease/terminal | `tests/component/service/test_astral_agent_queue.py` | no |
| `app.py` `/healthz` + `/wake` | `tests/component/service/test_astral_agent_app.py` | no |

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

**Out of scope:** live Postgres dual-replica race, Railway/CI (**AST-2241**), platform client (**AST-2238**), provider wrappers (**AST-2239**).

**Bible shasum (after publish):** fill per qa-child §9 — `git show origin/sub/AST-2235/AST-2237-astral-agent-queue-schema-and-worker-skeleton:docs/test-bible/service/astral_agent.md | shasum`
