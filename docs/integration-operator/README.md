# Integration operator (Joan)

## Purpose

Joan is Astral’s **integration-test operator**: after `origin/dev` lands, Joan runs the in-process integration harness on Susan’s dedicated Railway **test** service and surfaces failures to Chuckles for triage. This satisfies parent **AST-512** acceptance criterion **#7** (v2 Joan + Railway).

## When to run

Run after **`origin/dev` advances** and Susan’s Railway **test** service has finished deploying that commit:

- Chuckles after **`prep-uat`** / **`git push origin dev`**, once the test deploy completes, or
- Susan manual invoke (`integration-operator` skill).

Do **not** run against production Railway or Susan’s browser staging UAT host.

## Controlled vs live

| Mode | Who | Where | `ASTRAL_INTEGRATION_MODE` | `ASTRAL_ALLOW_LIVE_EXTERNAL_IO` | External I/O |
|------|-----|-------|---------------------------|----------------------------------|--------------|
| **Local / CI harness** | Engineers, GitHub Actions | Workstation / GHA runner | `1` (harness sets) | unset | Stubbed; product guard blocks live calls |
| **Joan operator (AST-712)** | Joan skill | Railway **test** service via `railway run` | `1` (harness sets) | **must stay unset** | Same as harness — Joan never opts into live I/O |
| **Spikes / manual ops** | Susan / engineers | Local or ad hoc | optional | `1` when explicitly needed | Live — out of integration tier (Bible) |
| **Production / staging UAT** | Susan browser UAT | Production or staging Railway | unset | unset | Real — **not** Joan’s integration pass |

## Prerequisites

- **AST-711** harness green on the deployed ref (`./scripts/testing/run_integration_tests.sh` passes in CI).
- **Railway CLI** installed: https://docs.railway.com/guides/cli
- **`railway link`** to the **test** project/service (not production) — see [RAILWAY_TEST_HOST.md](./RAILWAY_TEST_HOST.md).
- Astral repo checkout with `git fetch origin` before each run.
- Operator env vars documented in repo root `env.example` (`ASTRAL_RAILWAY_TEST_HOST_URL`, etc.).

## Commands

Deploy-ref pin, then harness on Railway test service:

```bash
./scripts/testing/verify_integration_deploy_ref.sh
./scripts/testing/run_railway_integration_tests.sh
```

`verify_integration_deploy_ref.sh` compares `git rev-parse origin/dev` to `RAILWAY_GIT_COMMIT_SHA` inside the linked test project. `run_railway_integration_tests.sh` runs `./scripts/testing/run_integration_tests.sh` via `railway run` and writes a timestamped log under `debug/integration-operator/`.

## Post-deploy gate (AST-818)

After **astral-test** redeploys **origin/dev**, run the automated gate (GitHub commit status + Linear on failure):

```bash
./scripts/testing/watch_post_deploy_integration.sh
# or single shot:
./scripts/testing/post_deploy_integration_gate.sh
```

Full contract, env vars, and cron example: [POST_DEPLOY_GATE.md](./POST_DEPLOY_GATE.md).

## Failure triage

On **non-zero exit** from either script:

1. Capture the `log:` path printed by `run_railway_integration_tests.sh`.
2. Joan opens a Linear **Discussion** ticket for **Chuckles** (template in `~/.cursor/skills/integration-operator/SKILL.md`).
3. Joan **stops** — no product patches, no live I/O opt-in.

Chuckles triages (bug child, infra, or definition fix). Joan does not own product fixes.

## Out of scope for Joan

- Product code fixes on failed runs
- Setting `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`
- Production or staging UAT hosts
- Zero-arg `./scripts/testing/run_component_tests.sh` as the integration gate
- Git merges / rollups (use Chuckles / `git-astral` skills)
