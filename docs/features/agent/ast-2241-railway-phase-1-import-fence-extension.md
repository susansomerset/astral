# AST-2241 — Railway Phase 1 + import-fence extension

- **Linear:** [AST-2241](https://linear.app/astralcareermatch/issue/AST-2241) · parent [AST-2235](https://linear.app/astralcareermatch/issue/AST-2235) (Build astral-agent microservice)
- **Publish ref:** `origin/sub/AST-2235/AST-2241-railway-phase-1-import-fence-extension`
- **Assignee:** Katherine
- **Canon Scope:** `astral.layers.import-direction`; `stat.logging.info`; `astral.config.secrets-and-env-specific-from-environ`

Land `service/astral_agent/railway.toml` (Phase 1 fixed replicas, Dockerfile build from monorepo root, memory ceiling, healthcheck) and extend the existing bidirectional `service`↔`src` CI fence so `service/astral_agent/` is covered the same way as Telescope. Does not own worker/provider/cutover logic (AST-2237–AST-2240). After #1 so deploy targets a real tree.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `service/astral_agent/railway.toml` — **new**.
- `scripts/ci/check-service-src-import-fence.sh` + `.github/workflows/service-src-import-fence.yml` — **modified**.

Every **Files Changed** row is one of those three paths. No edits to `service/astral_agent/*.py`, `Dockerfile`, `requirements.txt`, root `railway.toml`, `src/**`, provider modules, or Phase-2 autoscaler code.

## Canon notes (planner)

- **`astral.layers.import-direction` (placement):** One-line-per-layer rules live under `src/**`. This ticket does **not** change `src/` imports; it **extends CI** so `service/astral_agent/` cannot import `src` and `src` cannot import `service` (parent AC 2 / statute intent for the service↔src fence family Telescope already enforces).
- **`stat.logging.info`:** Fence script progress is one succinct stdout line on success and on failure (list offenders). No Python/`app_log` from CI.
- **`astral.config.secrets-and-env-specific-from-environ`:** `railway.toml` comments instruct operators to set `ASTRAL_DATABASE_URL` (and later provider keys) via Railway env — never commit secrets. No secret values in the toml.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `service/astral_agent/railway.toml` | **New** — Dockerfile builder, watch patterns, Phase 1 `numReplicas = 1`, memory limit, restart + drain + `/healthz` healthcheck; operator checklist comments | service / deploy |
| `scripts/ci/check-service-src-import-fence.sh` | **Modified** — scan all `service/**/*.py` (not only `service/telescope`) for `src` imports; keep `src` → `service` ban; update header/ok message | ci |
| `.github/workflows/service-src-import-fence.yml` | **Modified** — step name/comments reflect full `service`↔`src` fence (same script path) | ci |

**Out of this ticket:** `service/astral_agent/{app,worker,jobqueue,…}.py` / `Dockerfile` / `requirements.txt` (AST-2237); provider wrappers (AST-2239); platform client / config (AST-2238); `agent.py` cutover (AST-2240); root `railway.toml`; `tests/` / bible (Betty); Judoscale / `serviceInstanceUpdate` / Phase-2 autoscaler.

**Dependency:** AST-2237 must have created `service/astral_agent/` (Dockerfile + package). If that tree is missing on the working line after `sync-child.sh`, **stop** and comment on AST-2241 — do not invent app code here. Creating `railway.toml` alone under an empty dir is allowed only when `service/astral_agent/Dockerfile` already exists on HEAD.

## Stage 1: `service/astral_agent/railway.toml`

**Done when:** `service/astral_agent/railway.toml` exists with the keys below; root `railway.toml` / `service/telescope/railway.toml` untouched; no CI edits yet.

1. Create `service/astral_agent/railway.toml` with this body (comments included):

```toml
# Astral Agent — Railway config-as-code (AST-2241 / Phase 1).
# Point this Railway *service* Config-as-Code path at:
#   /service/astral_agent/railway.toml
# Do NOT set Railway Root Directory to /service/astral_agent — the Dockerfile
# COPY paths are monorepo-root relative (`COPY service/astral_agent/ …`).
# Build context = repository root; dockerfilePath below selects the image.
#
# Astral-agent is a queue consumer: it claims provider jobs from the agent_job
# table in Postgres and writes results back. Nothing calls into it for work over
# HTTP — only /healthz and /wake (AST-2237).
#
# Dashboard-only (not expressible / not safe in this file):
#   - Create a *separate* Railway service from the platform (and from Telescope).
#   - Set ASTRAL_DATABASE_URL on astral-agent *and* the platform to the astral
#     Postgres private URL (same DB Telescope uses). The service ensures
#     agent_* tables on startup (idempotent). Never commit the DSN.
#   - Provider API keys (OpenRouter / Anthropic / etc.) land with AST-2239 —
#     set them as Railway env on this service only; never commit.
#   - Private networking: no public domain required. Platform wakes replicas at
#     http://<astral-agent-service>.railway.internal:8080 (wake URL config is
#     AST-2238 on the platform).
#   - Serverless: after IDLE_SLEEP_SECONDS with no work, the process drops its
#     Postgres pool so Railway can sleep it; platform GET /wake resumes.
#   - Scale out by raising replicas in the dashboard (Phase 1 fixed fleet).
#     Do not add Judoscale / serviceInstanceUpdate / autoscaler code.
#   - Optional: raise memory in the dashboard if provider payloads OOMs.

[build]
builder = "DOCKERFILE"
dockerfilePath = "service/astral_agent/Dockerfile"
watchPatterns = ["service/astral_agent/**"]

[deploy]
# Phase 1: start at 1 replica; fan out manually in the dashboard later.
numReplicas = 1
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/healthz"
healthcheckTimeout = 120
# Old replica keeps running after SIGTERM so in-flight jobs finish;
# leftovers are handed back to the queue (SHUTDOWN_GRACE_SECONDS = 25 in agent_config).
drainingSeconds = 30
# 1 GiB per replica — no Firefox; WORKER_CONCURRENCY=4 HTTP jobs (AST-2237 defaults).
limitOverride = { containers = { memoryBytes = 1073741824 } }
```

⚠️ **Decision — mirror live Telescope toml shape (not the archived AST-1727 “no healthcheck” plan):** Current `service/telescope/railway.toml` sets `healthcheckPath = "/healthz"` because wake/health are unauthenticated on the private network (same for astral-agent AST-2237). Include healthcheck here.

⚠️ **Decision — 1 GiB not 2 GiB:** Telescope needs ~2 GiB for Firefox. Astral-agent is HTTP-only; Phase 1 starts at **1073741824**. Operators may raise in the dashboard if needed. Do not add autoscaler code.

⚠️ **Decision — monorepo root build context:** AST-2237 Dockerfile uses `COPY service/astral_agent/…`, so Railway Root Directory stays `/`. Config-as-Code path is `/service/astral_agent/railway.toml`.

2. Do **not** set `startCommand` — Dockerfile `CMD` is authoritative.

3. Do **not** modify root `railway.toml`, `railway-cron.toml`, or `service/telescope/railway.toml`.

**Stage 1 commit message:** `code(AST-2241): astral-agent railway Phase 1 toml`

## Stage 2: Extend bidirectional import fence (script + workflow)

**Done when:** `./scripts/ci/check-service-src-import-fence.sh` exits 0 on the current tree; a probe `from src…` under `service/astral_agent/` (temporary, deleted in the same shell — do not commit) makes the script exit non-zero; workflow still invokes the same script; parent AC 2 is enforceable for astral-agent.

1. Edit `scripts/ci/check-service-src-import-fence.sh`:
   - Update the header comment from “service/telescope ↔ src” to “service/* ↔ src (Telescope + astral-agent + future service packages)”.
   - Change the `SRC_IN_SERVICE` `rg` path from `service/telescope` to **`service`** (entire tree, `--glob '*.py'`, same regex `^\s*(from|import)\s+src(\.|\s|,|$)`).
   - Keep `SERVICE_IN_SRC` scanning `src` with the existing `service` import regex (already bans any `src` → `service` import, including a future `import service.astral_agent`).
   - Failure messages: say `service must not import src` / `src must not import service` (drop telescope-only wording).
   - Success line: `import fence: ok (service ↔ src)`.

⚠️ **Decision — widen to all of `service/`, not a second telescope-only + astral_agent pair:** Parent AC 2 is bidirectional for astral-agent; scanning every `service/**/*.py` avoids editing this script again for the next microservice and still covers Telescope. Same regex spirit as AST-1727 / `test_telescope_fence.py`.

2. Edit `.github/workflows/service-src-import-fence.yml`:
   - Rename the step from `Check service/telescope ↔ src import fence` to `Check service ↔ src import fence`.
   - Keep `run: ./scripts/ci/check-service-src-import-fence.sh`, same triggers (`dev`, `ftr/**`, PRs to `dev`).
   - Do **not** change workflow `name:` unless needed for clarity — optional one-line update to `Service↔src import fence` is already present; leave it if unchanged.

3. Builder verification (local, before commit; do not leave probe files):
   ```bash
   ./scripts/ci/check-service-src-import-fence.sh   # expect exit 0
   # optional probe under service/astral_agent/ then delete — expect exit 1
   ```

**Stage 2 commit message:** `code(AST-2241): extend service↔src import fence to astral-agent`

## Execution contract

- Stages in order; one commit per stage; publish each with `git push origin HEAD:sub/AST-2235/AST-2241-railway-phase-1-import-fence-extension`.
- Do not add files outside **Files Changed**. Do not implement worker/provider/client/cutover.
- Ambiguity / missing AST-2237 tree → stop and comment on **AST-2241** (not parent) with the Stage-blocked template.

## Estimate

Confirm Chuckles estimate: 2 — agree
