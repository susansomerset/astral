# Astral Agent (platform queue client)

**Test module:** `tests/component/external/test_astral_agent.py`

Platform half of the astral-agent Postgres job queue (`src/external/astral_agent.py`). Service consumer: [`service/astral_agent.md`](../service/astral_agent.md). Config keys: [`utils/config.md`](../utils/config.md) § AST-2238.

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/astral_agent.py` | `tests/component/external/test_astral_agent.py` | no |
| `ASTRAL_AGENT_CONFIG` | `tests/component/utils/test_config.py::TestAst2238AstralAgentConfig` | via `config.py` lock |

**Integration tier:** no existing `tests/integration/` scenario exercises astral-agent enqueue. No integration revision this pass.

---

### AST-2238 · AST-2235 (platform astral_agent client enqueue/await)

**Scope:** `src/external/astral_agent.py` (Telescope-shaped enqueue/await/wake) + `ASTRAL_AGENT_CONFIG` in `config.py`. No `do_task` cutover, no provider HTTP, no `service.*` imports.

| Area | Component tests |
| --- | --- |
| Contract constants + no `service.*` import | `test_astral_agent.py::TestAst2238ContractAndFence` |
| Strict DSN (`os.environ` / blank) + submit before insert | `…::TestAst2238DsnStrict` |
| Terminal `done` / passthrough / timeout / cancel / job_failed | `…::TestAst2238SubmitTerminal` |
| Wake URL from env / empty when unset | `…::TestAst2238WakeUrl` |
| `run_one_shot` releases loop pool; module `submit` delegates | `…::TestAst2238OneShotLoopTeardown` |
| Config keys + no DSN/secret literals | `test_config.py::TestAst2238AstralAgentConfig` |

## QA test manifest

1. **Client (required):** `tests/component/external/test_astral_agent.py`
2. **Config (required):** `tests/component/utils/test_config.py::TestAst2238AstralAgentConfig`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_astral_agent.py \
  tests/component/utils/test_config.py::TestAst2238AstralAgentConfig \
  -q
```

**Pass criterion:** pytest green on both paths — not zero-arg harness / branch-lock gate.

**Broken / obsolete:** none (new module).

**Out of scope:** live Postgres dual-replica, provider wrappers (**AST-2239**), `agent.py` cutover (**AST-2240**), service worker (**AST-2237**).

**Bible shasum (after publish):** fill after tip push.
