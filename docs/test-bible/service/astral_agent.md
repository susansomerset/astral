# Astral Agent service (`service/astral_agent/`)

**Test modules:** `tests/component/service/test_astral_agent_*.py`

Isolated FastAPI Postgres queue consumer — **not** under `src/`. Flat imports (`from settings import …`); component conftest swaps `service/astral_agent/` onto `sys.path` (Telescope uses the same flat names — purge before swap). No `LOCKED_AT_100` (coverage gate is `--cov=src` only).

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| Tree / Dockerfile / requirements / ban greps | `tests/component/service/test_astral_agent_fence.py` | no |
| Settings, executor, codec, claim/lease/terminal | `tests/component/service/test_astral_agent_queue.py` | no |
| Provider errors + executor validate/dispatch | `tests/component/service/test_astral_agent_providers.py` | no |
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

**Out of scope (AST-2237 pass):** live Postgres dual-replica race, Railway/CI, platform client, provider wrappers (owned by siblings).

**Bible shasum (publish tip `8f385ce71`):** `931ca561cc9499a6fe0a896b6f7d568b13b71df7  -`

---

### AST-2239 · AST-2235 (provider wrappers inside the worker)

**Scope:** `service/astral_agent/providers/*` + live `executor.execute`; worker soft-fail→`complete` / `ProviderJobError`→`fail`; thin-stub `send_to_anthropic` / `send_to_llm_compat`. No `agent.py` cutover.

| Area | Component tests |
| --- | --- |
| Classify / soft_fail / success_result / tool_use | `test_astral_agent_providers.py::TestAst2239ProviderErrors` |
| Executor validate + anthropic/compat dispatch | `…::TestAst2239ExecutorValidate` + revised `test_astral_agent_queue.py::TestAst2237Executor` |
| Claim→complete / soft-fail complete / bad_request / executor_error | `test_astral_agent_queue.py::TestAst2237ClaimLeaseTerminal` (revised) |
| requirements anthropic+httpx; recursive ban greps | `test_astral_agent_fence.py` (revised) |
| Platform `send_to_*` raise retired | `test_anthropic.py::TestAst2239SendToAnthropicRetired`, `test_llm_compat.py::TestAst2239SendToLlmCompatRetired` |

**Broken / obsolete revised:** AST-2237 stub echo / `stub_error` / requirements-without-providers asserts. Platform `send_to_*` HTTP suites skipped (`@_SEND_RETIRED`) — wire coverage lives under `service/astral_agent/providers` until AST-2240 retargets callers.

## QA test manifest

1. **Service providers + queue revise (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_astral_agent_fence.py \
  tests/component/service/test_astral_agent_queue.py \
  tests/component/service/test_astral_agent_providers.py \
  -q
```
2. **Platform retirement (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_anthropic.py::TestAst2239SendToAnthropicRetired \
  tests/component/external/test_llm_compat.py::TestAst2239SendToLlmCompatRetired \
  -q
```

**Pass criterion:** pytest green on both commands — not zero-arg harness / branch-lock gate.

**Out of scope:** live provider HTTP, `do_task` cutover (**AST-2240**), platform enqueue (**AST-2238**).

**Bible shasum (after publish):** fill after tip push.
