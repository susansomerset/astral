# Railway Phase 1 deploy and import-boundary CI

**Linear:** [AST-1727](https://linear.app/astralcareermatch/issue/AST-1727)
**Parent:** [AST-1721](https://linear.app/astralcareermatch/issue/AST-1721) — Astral Telescope — stateless headless-scraping microservice (per-URL)
**Publish ref:** `sub/AST-1721/AST-1727-railway-phase-1-deploy-import-boundary-ci`

Land Railway config-as-code for the Telescope service under `service/telescope/` (Dockerfile build from monorepo root, Phase 1 `numReplicas = 1`, memory ceiling, restart-on-failure) plus a CI fence that fails the build on any real `service/telescope` ↔ `src` import in either direction. Does not own service app code ([AST-1725](https://linear.app/astralcareermatch/issue/AST-1725)) or the platform client ([AST-1726](https://linear.app/astralcareermatch/issue/AST-1726)). No Phase 2 autoscaler. No Surfer.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `service/telescope/railway.toml` (or equivalent Railway service config colocated with the service) — **new** — subdirectory deploy for the Telescope service.
- `.github/workflows/` (or a tracked lint script invoked by CI) — **modified/new** — fail the build if `service/telescope/` imports from `src/` **or** `src/` imports from `service/`.

Every **Files Changed** row is one of those paths (plus the tracked lint script under `scripts/ci/` that the workflow invokes — same Scope clause “or a tracked lint script”). No edits to `service/telescope/*.py`, `Dockerfile`, root `railway.toml`, `src/**`, Surfer, or Phase 2 autoscaler code.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `service/telescope/railway.toml` | **New** — Dockerfile builder, watch patterns, Phase 1 replicas=1, memory limit, restart policy; operator checklist comments (private networking, bearer secret, no public domain, fan-out) | service / deploy |
| `scripts/ci/check-service-src-import-fence.sh` | **New** — exit non-zero on real bidirectional `service/telescope` ↔ `src` imports | ci |
| `.github/workflows/service-src-import-fence.yml` | **New** — run the fence script on push/PR to `dev` (and `ftr/**` pushes) | ci |

**Out of this ticket:** `service/telescope/{app,auth,browser,…}.py` / `Dockerfile` / `requirements.txt` (AST-1725); `src/external/telescope.py` / platform config (AST-1726); root `railway.toml` / `railway-cron.toml`; statute file amendment for `stat.layers.import-rules` (Archie/Joan — CI enforces the requested fence only); `tests/` / bible (Betty); Surfer; Judoscale / `serviceInstanceUpdate` / autoscaler.

## Canon notes (planner)

- **`stat.logging.info` (full):** Everyday progress is succinct, always-on, operator-scannable; no payloads/fail guts on info; channel for `src/**` is `get_logger`. This ticket’s deliverables are bash + toml — any progress the fence script prints uses a single succinct stdout line on failure listing offenders (operator-readable). Do not add Python `print` spam or invent `app_log` from CI.
- **`stat.layers.import-rules` (amendment requested, not scoring law yet):** Parent asks for a bidirectional `service/*` ↔ `src/` ban with CI enforcement. This ticket **implements the CI fence** only — do **not** edit `canon/directives/draft/stat.layers.import-rules.md` or related statutes. Id-only beyond that.
- **Pending pattern** `patt.external.web-scraping-via-telescope`: not on this child’s Citations — ignore.

## Stage 1: `service/telescope/railway.toml`

**Done when:** `service/telescope/railway.toml` exists with the exact build/deploy keys below, plus a comment block listing dashboard-only operator steps. Root `railway.toml` is untouched. No CI files yet.

1. Create `service/telescope/railway.toml` with this body (comments included):

```toml
# Astral Telescope — Railway config-as-code (AST-1727 / Phase 1).
# Point this Railway *service* Config-as-Code path at:
#   /service/telescope/railway.toml
# Do NOT set Railway Root Directory to /service/telescope — the Dockerfile
# COPY paths are monorepo-root relative (`COPY service/telescope/ …`).
# Build context = repository root; dockerfilePath below selects the image.
#
# Dashboard-only (not expressible / not safe in this file):
#   - Create a *separate* Railway service from the platform (AC 9 / AC 12).
#   - Private networking: no public domain / generate domain OFF for Telescope.
#     Platform reaches it at http://<telescope-service-name>.railway.internal:8080
#     (set TELESCOPE_BASE_URL / TELESCOPE_BASE_URLS on the *platform* service).
#   - Shared secret: set TELESCOPE_BEARER_TOKEN on Telescope *and* platform
#     (same value; never commit the secret).
#   - Optional fan-out: after 1-replica validation, raise replicas in the
#     dashboard (Phase 1 fixed fleet). Do not add Judoscale / GraphQL
#     serviceInstanceUpdate / autoscaler code (AC 13).
#   - /dev/shm: if Firefox flakes on shared memory, raise container disk or
#     follow Railway shm guidance; Dockerfile documents --shm-size for local Docker.
#   - Do NOT enable Railway healthcheckPath=/healthz — /healthz requires
#     Authorization: Bearer (AST-1725); Railway probes cannot send that header.
#     Verify with: curl -H "Authorization: Bearer $TELESCOPE_BEARER_TOKEN" \
#       http://<private-host>:8080/healthz

[build]
builder = "DOCKERFILE"
dockerfilePath = "service/telescope/Dockerfile"
watchPatterns = ["service/telescope/**"]

[deploy]
# Phase 1: start at 1 replica; fan out manually in the dashboard later.
numReplicas = 1
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
# ~2 GiB per replica — matches parent “~2–4 pages in a 2GB container” +
# TELESCOPE_MAX_CONCURRENT_PAGES default 3 (AST-1725 settings).
limitOverride = { containers = { memoryBytes = 2147483648 } }
```

⚠️ **Decision — monorepo root build context:** AST-1725’s Dockerfile uses `COPY service/telescope/…`, so Railway Root Directory must stay `/` (repo root). Config-as-Code file lives under the service dir; dashboard Config-as-Code path is `/service/telescope/railway.toml`.

⚠️ **Decision — no `healthcheckPath`:** `/healthz` is bearer-gated (AST-1725 plan). Railway’s HTTP probe cannot attach `Authorization`. Omitting healthcheck avoids false-failed deploys; `restartPolicyType = ON_FAILURE` covers crash loops; operators prove health with authenticated curl.

⚠️ **Decision — `numReplicas = 1` in toml:** Encodes Phase 1 “start at 1”; later fixed fan-out is a dashboard replica bump only — no Phase 2 autoscaler code (AC 13). Do not add `serviceInstanceUpdate`, Judoscale, or cron scale scripts.

⚠️ **Decision — memory via `limitOverride`:** Schema supports `deploy.limitOverride.containers.memoryBytes`. Set **2147483648** (2 GiB). Do not invent Judoscale or vertical-autoscaler hooks.

2. Do **not** set `startCommand` — Dockerfile `CMD` (`uvicorn app:app … --workers 1`) is authoritative.

3. Do **not** modify root `railway.toml` or `railway-cron.toml`.

## Stage 2: Bidirectional import fence (script + workflow)

**Done when:** `./scripts/ci/check-service-src-import-fence.sh` exits 0 on the current tree; a deliberate temporary import in a scratch sense is **not** committed — instead verify the script’s regexes match the Betty-style import-line patterns below. Workflow file exists and invokes the script. Parent AC 2 intent satisfied for CI.

1. Create `scripts/ci/check-service-src-import-fence.sh` (executable bit in git: `chmod +x` before commit):

```bash
#!/usr/bin/env bash
# AST-1727 — fail if service/telescope ↔ src imports exist either direction.
# Matches real import lines only (not docstrings/comments saying "import src").
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Same spirit as tests/component/service/test_telescope_fence.py
SRC_IN_SERVICE="$(rg -n --glob '*.py' -e '^\s*(from|import)\s+src(\.|\s|,|$)' service/telescope || true)"
SERVICE_IN_SRC="$(rg -n --glob '*.py' -e '^\s*(from|import)\s+service(\.|\s|,|$)' src || true)"

fail=0
if [[ -n "$SRC_IN_SERVICE" ]]; then
  echo "import fence: service/telescope must not import src:"
  echo "$SRC_IN_SERVICE"
  fail=1
fi
if [[ -n "$SERVICE_IN_SRC" ]]; then
  echo "import fence: src must not import service:"
  echo "$SERVICE_IN_SRC"
  fail=1
fi
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "import fence: ok (service/telescope ↔ src)"
```

⚠️ **Decision — anchored import-line regex, not raw parent `rg`:** Parent AC 2’s literal `rg -n "from src\\.|import src"` false-positives on docstrings such as settings.py’s “Never import src.” Betty’s component test already anchors `^\s*(?:from|import)\s+src`. CI uses the same class of pattern both directions so the fence measures **imports**, which is the statute intent.

2. Create `.github/workflows/service-src-import-fence.yml`:

```yaml
name: Service↔src import fence

on:
  push:
    branches:
      - dev
      - 'ftr/**'
  pull_request:
    branches:
      - dev

jobs:
  import-fence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ripgrep
        run: sudo apt-get update && sudo apt-get install -y ripgrep
      - name: Check service/telescope ↔ src import fence
        run: ./scripts/ci/check-service-src-import-fence.sh
```

3. Locally run `./scripts/ci/check-service-src-import-fence.sh` and confirm exit 0 before the stage commit.

4. Confirm with ripgrep that this ticket’s diff does **not** introduce `serviceInstanceUpdate`, `Judoscale`, or `numReplicas` **mutation** code under `service/` or `src/` (static `numReplicas = 1` in toml is the Phase 1 fixed count — allowed). AC 13.

## Stage 3: Sanity — no Phase 2 / no Surfer / fence green

**Done when:** Fence script green; `rg -n "serviceInstanceUpdate|Judoscale" service/ src/ scripts/ci/ .github/workflows/service-src-import-fence.yml` is empty (or only hits this plan doc if searched under `docs/` — do not search docs for the gate); no Surfer package added; railway.toml still has `numReplicas = 1` and no healthcheckPath.

1. Re-run `./scripts/ci/check-service-src-import-fence.sh`.
2. `test -f service/telescope/railway.toml && test -f scripts/ci/check-service-src-import-fence.sh && test -f .github/workflows/service-src-import-fence.yml`.
3. Stop. Live Railway service creation + private URL wiring on the platform env vars is **Susan/operator** using the comment checklist in `railway.toml` after this lands on `dev` — not a build-child `railway up` step (no Railway token assumed in engineer sessions).

## Parent AC mapping (this child)

| Parent AC | How this plan covers it |
|-----------|-------------------------|
| **2** Bidirectional import fence | Stage 2 script + workflow; real import lines both directions |
| **9** Separate host | `railway.toml` + dashboard checklist: separate service, private DNS, platform `TELESCOPE_BASE_URL(S)` — never `import service` |
| **12** OOM isolation / Phase 1 replicas | `numReplicas = 1`, `memoryBytes = 2GiB`, restart policy; fan-out note; semaphore already on AST-1725/1726 |
| **13** No Phase 2 / no Surfer | Explicit non-goals; Stage 3 rg gate; no Surfer package |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1727
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref tip:** b7d41e9426848c73a9d5d2c14c1b658f98ef9379 (`origin/sub/AST-1721/AST-1727-railway-phase-1-deploy-import-boundary-ci`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.layers.import-rules (amendment request) | B | | |
| stat.logging.info | B | | |

## Traceability

AC2→S2 `check-service-src-import-fence.sh` + `service-src-import-fence.yml` (anchored import-line regex both directions); AC9→S1 `railway.toml` separate-service checklist + private DNS + platform `TELESCOPE_BASE_URL(S)` (operator wiring post-land); AC12→S1 `numReplicas=1`, 2 GiB `limitOverride`, `ON_FAILURE` restart (semaphore on AST-1725/1726); AC13→S3 `Judoscale`/`serviceInstanceUpdate` rg gate + explicit non-goals.

## Findings

### discuss — Parent AC 2 literal `rg` vs anchored CI regex

- **Severity:** discuss
- **Location:** Stage 2 ⚠️ Decision; parent AC 2
- **Finding:** Parent AC 2 quotes literal `rg "from src\\.|import src"` / `from service\\.|import service`. Plan uses anchored import-line patterns (aligned with `tests/component/service/test_telescope_fence.py`) to avoid docstring false positives (e.g. settings.py “Never import src.”). Measures **imports**, which is the amendment intent.
- **Recommendation:** No plan change required; note in build/UAT that AC 2’s literal grep is superseded by the anchored fence for CI truth.

### discuss — Betty component test is one-way only

- **Severity:** discuss
- **Location:** Stage 2 script; `tests/component/service/test_telescope_fence.py`
- **Finding:** Betty’s fence test covers `service/telescope` → `src` only. CI script adds `src` → `service` (required for bidirectional AC 2). Not a plan defect — CI is the stronger gate.
- **Recommendation:** Optional Betty follow-up to mirror `SERVICE_IN_SRC` check; out of AST-1727 Scope.

### acceptable — Scope gate / lint script path

- **Severity:** acceptable
- **Location:** Explicit scope gate; Files Changed
- **Finding:** `scripts/ci/check-service-src-import-fence.sh` is authorized by ticket Scope (“or a tracked lint script invoked by CI”). No `service/telescope/*.py`, `src/**`, or root `railway.toml` edits.
- **Recommendation:** None.

### acceptable — `stat.logging.info` on bash deliverables

- **Severity:** acceptable
- **Location:** Canon notes; Stage 2 script
- **Finding:** Statute `applies_when.paths` is `src/**`; this ticket is toml + bash. Plan applies semantic (succinct operator-readable stdout on failure; no payload spam) to the fence script — appropriate variance for CI.
- **Recommendation:** None.

### acceptable — Railway operator steps

- **Severity:** acceptable
- **Location:** Stage 1 comment block; Stage 3 step 3
- **Finding:** Live Railway service creation, private networking, bearer secret, and platform env vars are dashboard/operator steps after land — correctly excluded from build-child `railway up`. AC 9 satisfied via config-as-code + checklist, not in-process import.
- **Recommendation:** None.

### acceptable — No `healthcheckPath`

- **Severity:** acceptable
- **Location:** Stage 1 ⚠️ Decision
- **Finding:** Omitting Railway HTTP healthcheck avoids false deploy failures against bearer-gated `/healthz` (AST-1725). `restartPolicyType = ON_FAILURE` + operator authenticated curl documented.
- **Recommendation:** None.

### acceptable — R6 definition fidelity

- **Severity:** acceptable
- **Location:** Explicit scope gate; Stages 1–3; `## Estimate`
- **Finding:** Plan matches child Scope (railway.toml + CI only). No Phase 2 autoscaler, Surfer, or sibling product code. Self-assessment (`Confirm Chuckles estimate: 3 — agree`) is honest for three focused stages. No `!!-NONE` conf gaps.
- **Recommendation:** None.

### acceptable — Plan Discuss

- **Severity:** acceptable
- **Location:** Linear comments
- **Finding:** Plan Discuss rounds completed: **0** (status Plan Ready; assignee Joan).
- **Recommendation:** N/A.

context_tokens≈95000

## Review (build stub)

**Built:** `origin/sub/AST-1721/AST-1727-railway-phase-1-deploy-import-boundary-ci` @ `95f04c2f` (+ Stage 3 tip after this commit).

**Stages delivered:**
- Stage 1: `service/telescope/railway.toml` (Dockerfile build, numReplicas=1, 2 GiB, ON_FAILURE) — `36ffc0ae`.
- Stage 2: `scripts/ci/check-service-src-import-fence.sh` + `.github/workflows/service-src-import-fence.yml` — `95f04c2f`.
- Stage 3: AC13 comment cleanup + fence re-run green — (this commit).

**Betty:** CI bidirectional fence (service/telescope ↔ src import lines); railway.toml Phase 1 deploy posture (no Phase 2 / Surfer). Live Railway attach is operator checklist in toml comments.
