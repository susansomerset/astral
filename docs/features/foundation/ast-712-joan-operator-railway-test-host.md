# AST-712 — Joan operator workflow and Railway test host

- **Linear (this ticket):** [AST-712](https://linear.app/astralcareermatch/issue/AST-712/joan-operator-workflow-and-railway-test-host-astral-integration-testing)
- **Parent:** [AST-512](https://linear.app/astralcareermatch/issue/AST-512/astral-integration-testing) — Slice 2 (Joan operator + Railway test host). **Depends on Slice 1:** [AST-711](https://linear.app/astralcareermatch/issue/AST-711/integration-harness-and-first-authenticated-api-scenario-astral-integration) harness + bible tier.
- **Publish ref:** `origin/sub/AST-512/AST-712-joan-operator-railway-test-host`

## Summary

Deliver the **v2 integration operator** lane: a Joan Cursor skill plus repo scripts/docs so Joan can run `./scripts/testing/run_integration_tests.sh` **on Susan’s dedicated Railway test service** after `origin/dev` lands, with a **deploy-ref pin** (`origin/dev` SHA vs Railway `RAILWAY_GIT_COMMIT_SHA`), a documented **controlled-vs-live operator contract**, and a **failure triage path** that opens a Linear **Discussion** ticket for Chuckles (Joan does not fix product).

⚠️ **Decision:** Joan runs the **same in-process pytest harness** as CI/local (`run_integration_tests.sh`) via **`railway run`** on the test service — not HTTP smoke against the gunicorn web process. The web service may stay up for deploy-status visibility; the harness is a one-off container command.

⚠️ **Decision:** Deploy ref verification uses **`RAILWAY_GIT_COMMIT_SHA`** inside the linked test project (Railway-injected) compared to **`git rev-parse origin/dev`** on the operator machine — no new public API, no admin token for Joan.

## Operator contract (controlled vs live)

| Mode | Who | Where | `ASTRAL_INTEGRATION_MODE` | `ASTRAL_ALLOW_LIVE_EXTERNAL_IO` | External I/O |
|------|-----|-------|---------------------------|----------------------------------|--------------|
| **Local / CI harness** | Engineers, GitHub Actions | Workstation / GHA runner | `1` (harness sets) | unset | Stubbed; product guard blocks live calls |
| **Joan operator (this ticket)** | Joan skill | Railway **test** service via `railway run` | `1` (harness sets) | **must stay unset** | Same as harness — Joan never opts into live I/O |
| **Spikes / manual ops** | Susan / engineers | Local or ad hoc | optional | `1` when explicitly needed | Live — out of integration tier (Bible) |
| **Production / staging UAT** | Susan browser UAT | Production or staging Railway | unset | unset | Real — **not** Joan’s integration pass |

**Joan must not** set `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`, patch externals for live calls, or open product PRs from a failed run.

## Out of scope (explicit)

| Item | Owner / ticket |
|------|----------------|
| In-process harness, first scenario, CI workflow | **AST-711** (shipped on `ftr`) |
| Production Railway or staging UAT host | Susan manual UAT only |
| Joan product fixes | Chuckles triages **Discussion** tickets |
| `tests/` or `docs/test-bible/**` commits | **Betty** (`qa-child`) — engineer pre-commit hook blocks |
| New Flask routes or deploy-status API changes | Forbidden — use existing env + Railway metadata |
| Wiring Joan into `prep-uat-land.sh` automatically | Future; this ticket documents **when** Chuckles/Susan invoke Joan |

## Build prerequisite (mandatory before Stage 1)

On **`epic worktree`**, checked out on **`sub/AST-512/AST-712-joan-operator-railway-test-host`**:

```bash
git fetch origin
git merge origin/ftr/AST-512-astral-integration-testing
```

**Done when:** `./scripts/testing/run_integration_tests.sh` exists and passes locally (3 tests). If merge conflicts, resolve on publish ref before product stages — do not plan around a stale sub tip.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `docs/integration-operator/README.md` | Operator contract, trigger, failure triage, env var table | docs | Ada (build) |
| `docs/integration-operator/RAILWAY_TEST_HOST.md` | Susan provisioning checklist (separate test service, `dev` branch, env) | docs | Ada (build) |
| `env.example` | Placeholder vars for test host URL + Railway link (no secrets) | docs | Ada (build) |
| `scripts/testing/verify_integration_deploy_ref.sh` | Compare `origin/dev` SHA to `RAILWAY_GIT_COMMIT_SHA` | scripts | Ada (build) |
| `scripts/testing/run_railway_integration_tests.sh` | Joan entry: verify ref → `railway run` harness → capture log path | scripts | Ada (build) |
| `~/.cursor/skills/integration-operator/SKILL.md` | Joan Cursor skill — full procedure + Discussion ticket template | skill | Ada (build) |
| `docs/test-bible/integration/README.md` | **§ Joan operator** — pointer to repo docs + skill name | bible | Betty (qa-child) |

## Stage 1: Operator docs and env contract

**Done when:** `docs/integration-operator/README.md` and `RAILWAY_TEST_HOST.md` exist; `env.example` documents required operator env vars; no secrets committed.

1. Create directory `docs/integration-operator/`.

2. Create `docs/integration-operator/README.md` with these sections (use exact headings):

   - **Purpose** — Joan as integration operator after dev land; satisfies parent AC **#7**.
   - **When to run** — After `origin/dev` advances and Susan’s Railway **test** service has finished deploying that commit (Chuckles after `prep-uat` / `push-dev`, or Susan manual invoke).
   - **Controlled vs live** — Copy the operator contract table from this plan (same four rows).
   - **Prerequisites** — Railway CLI installed; `railway link` to the **test** project/service (not production); repo checkout with `git fetch origin`; vars from `env.example`.
   - **Commands** — Document the two-script flow:
     ```bash
     ./scripts/testing/verify_integration_deploy_ref.sh
     ./scripts/testing/run_railway_integration_tests.sh
     ```
   - **Failure triage** — On non-zero exit: Joan opens Linear **Discussion** for Chuckles (template in Stage 3 skill); attach log path from `run_railway_integration_tests.sh`; Joan stops.
   - **Out of scope for Joan** — Product fixes, live I/O opt-in, production host, component suite.

3. Create `docs/integration-operator/RAILWAY_TEST_HOST.md` — **Susan provisioning checklist** (Susan executes; Ada documents):

   - Separate Railway **test** service (not production, not Susan browser staging if distinct).
   - Git deploy source: **`dev`** branch (tracks landed epic work).
   - Set `ASTRAL_DEPLOY_ENV=integration-test` on the test service (admin footer label — optional visibility only).
   - Required dummy external env vars for harness imports (mirror `tests/integration/conftest.py`: `GMAIL_*`, `GOOGLE_*`, `ANTHROPIC_API_KEY` placeholders) — Railway service variables, not committed.
   - Persistent volume / SQLite path: use Railway default app `data/` or document Susan’s mount — harness uses temp DB per test; no production DB.
   - Record public URL as `ASTRAL_RAILWAY_TEST_HOST_URL` in operator `.env` (for optional HTTP sanity only — scripts do not require admin auth).
   - **Never** set `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1` on the test service.

4. In `env.example`, after the `ASTRAL_DEPLOY_ENV` block, append:

   ```bash
   # Integration operator (AST-712) — Joan runs harness on Railway TEST service (Susan provisions)
   # Public URL of the dedicated test deploy (optional HTTP checks; deploy pin uses Railway CLI)
   ASTRAL_RAILWAY_TEST_HOST_URL=https://your-integration-test-host.up.railway.app
   # After `railway link` in the test project — Joan uses linked context; document service name in RAILWAY_TEST_HOST.md
   # RAILWAY_TOKEN=...  # operator machine only — never commit
   ```

## Stage 2: Deploy-ref verification and Railway harness scripts

**Done when:** Both scripts are executable; `verify_integration_deploy_ref.sh` exits 0 when SHAs match and non-zero with a clear message when they differ; `run_railway_integration_tests.sh` invokes the harness via `railway run` and writes a timestamped log under `debug/integration-operator/` (gitignored — create dir at runtime only).

1. Create `scripts/testing/verify_integration_deploy_ref.sh`:

```bash
#!/usr/bin/env bash
# Pin integration operator run to origin/dev SHA vs Railway deploy (AST-712).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
git fetch origin
EXPECTED="${1:-$(git rev-parse origin/dev)}"
if ! command -v railway >/dev/null 2>&1; then
  echo "BLOCKED: railway CLI not installed (https://docs.railway.com/guides/cli)" >&2
  exit 2
fi
ACTUAL="$(railway run -- printenv RAILWAY_GIT_COMMIT_SHA | tr -d '[:space:]')"
if [[ -z "$ACTUAL" ]]; then
  echo "BLOCKED: RAILWAY_GIT_COMMIT_SHA empty — link test project (railway link) and ensure deploy finished" >&2
  exit 2
fi
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "DEPLOY MISMATCH: origin/dev=$EXPECTED railway=$ACTUAL" >&2
  echo "Wait for test service deploy or re-run after push-dev." >&2
  exit 1
fi
echo "deploy-ref ok: $ACTUAL"
```

2. `chmod +x scripts/testing/verify_integration_deploy_ref.sh`.

3. Create `scripts/testing/run_railway_integration_tests.sh`:

```bash
#!/usr/bin/env bash
# Joan operator entry — run integration harness on Railway test service (AST-712).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
"$ROOT/scripts/testing/verify_integration_deploy_ref.sh"
LOG_DIR="$ROOT/debug/integration-operator"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LOG_DIR/run-${STAMP}.log"
if ! command -v railway >/dev/null 2>&1; then
  echo "BLOCKED: railway CLI not installed" >&2
  exit 2
fi
set +e
railway run -- bash -lc 'cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && ./scripts/testing/run_integration_tests.sh' 2>&1 | tee "$LOG"
STATUS=${PIPESTATUS[0]}
set -e
echo "log: $LOG"
exit "$STATUS"
```

4. `chmod +x scripts/testing/run_railway_integration_tests.sh`.

5. Do **not** modify `scripts/testing/run_integration_tests.sh` — reuse AST-711 harness as-is.

⚠️ **Decision:** Logs under `debug/integration-operator/` follow **ASTRAL_CODE_RULES** §3.6 spike output — gitignored parent `debug/` already; no new `.gitignore` rows unless the repo lacks `debug/` ignore (if missing, add single line `debug/` only in this stage).

## Stage 3: Joan Cursor skill

**Done when:** `~/.cursor/skills/integration-operator/SKILL.md` exists with front matter, procedure, and Discussion ticket template; skill references repo paths and env vars from Stages 1–2.

1. Create directory `~/.cursor/skills/integration-operator/` if missing.

2. Create `~/.cursor/skills/integration-operator/SKILL.md`:

```markdown
---
name: integration-operator
description: >-
  Joan: after origin/dev lands, verify Railway test deploy ref and run
  run_integration_tests.sh via railway run; on failure open Linear Discussion
  for Chuckles with repro log. Never fix product or enable live external I/O.
---

# Integration operator (Joan)

**Who:** Joan — git/integration operator. **Not** product engineer.

## When

- Chuckles or Susan after **`git push origin dev`** (or **`prep-uat`**) once Susan’s Railway **test** service deploy completes.
- Susan says `integration-operator` or `run integration tests on test host`.

## Prerequisites

- [AST-711](https://linear.app/astralcareermatch/issue/AST-711) harness on deployed ref (`run_integration_tests.sh` green in CI).
- Railway CLI + `railway link` to **test** project (see `docs/integration-operator/RAILWAY_TEST_HOST.md`).
- `git fetch origin` in astral checkout; `ASTRAL_RAILWAY_TEST_HOST_URL` in operator `.env` if documented checks need it.

## Procedure

1. `cd` to astral repo root (Susan’s main checkout or Chuckles `ASTRAL_MAIN`).
2. `git fetch origin` — note `git rev-parse origin/dev`.
3. `./scripts/testing/verify_integration_deploy_ref.sh` — stop on mismatch (wait for deploy).
4. `./scripts/testing/run_railway_integration_tests.sh` — capture printed `log:` path.
5. Exit 0 → comment on parent **AST-512** (optional): `Integration operator: PASS @ <sha> log <path>`.
6. Exit non-zero → **Failure triage** below; do **not** patch product.

## Controlled vs live (operator)

- Harness sets `ASTRAL_INTEGRATION_MODE=1`.
- **Never** export `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`.
- **Never** run against production Railway hostname.

## Failure triage — Linear Discussion for Chuckles

Use **`linear-chuckles`** or Joan’s Linear MCP if configured; else Chuckles files from Joan’s pasted output.

Create issue:
- **Team:** Astral
- **Project:** Astral Foundation
- **State:** Discussion
- **Assignee:** Chuckles
- **Parent:** AST-512 (link)
- **Title:** `Integration harness failure — test host @ <short-sha>`

**Description template:**

```
## Deploy
- origin/dev: <full sha>
- railway RAILWAY_GIT_COMMIT_SHA: <sha>
- test host: <ASTRAL_RAILWAY_TEST_HOST_URL or railway project name>

## Command
./scripts/testing/run_railway_integration_tests.sh

## Log
<paste tail of log file or attach path>

## Joan action
Discussion only — Chuckles triages (bug child / infra / definition). Joan does not fix product.
```

## Does NOT

- Merge git branches (use `git-astral` / Chuckles skills).
- Edit `tests/` or `docs/test-bible/**`.
- Run `./scripts/testing/run_component_tests.sh` as the integration gate.
```

3. Do **not** register the skill in repo — Susan’s Cursor picks up `~/.cursor/skills/` automatically.

## Stage 4: Bible Joan operator section (Betty — `qa-child`, not Ada commits)

**Done when:** `docs/test-bible/integration/README.md` has a **Joan operator** section pointing to `docs/integration-operator/README.md`, skill name `integration-operator`, and the two script commands; parent AC **#7** bible cross-link satisfied.

1. Append to `docs/test-bible/integration/README.md`:

   - **Heading:** `## Joan operator (AST-712)`
   - **Trigger:** after `origin/dev` land + Railway test deploy
   - **Commands:** `verify_integration_deploy_ref.sh` then `run_railway_integration_tests.sh`
   - **Skill:** `~/.cursor/skills/integration-operator/SKILL.md`
   - **Failure:** Linear **Discussion** → Chuckles; repro log under `debug/integration-operator/`
   - **Link:** `docs/integration-operator/README.md`

2. Do **not** duplicate the full operator contract table — link to repo doc.

## QA manifest (Betty → test-child)

**Gate for AST-712 closure:**

```bash
# Local sanity (engineer / Betty before Joan skill invoke)
./scripts/testing/run_integration_tests.sh

# Operator scripts — syntax / dry-run where Railway unavailable:
bash -n scripts/testing/verify_integration_deploy_ref.sh
bash -n scripts/testing/run_railway_integration_tests.sh
```

**Railway E2E:** Susan/Chuckles run Stage 3 skill once test host is provisioned — not required for Betty manifest if Railway CLI absent on `astral-tests`; document `[qa-handoff]` only if bible section missing.

**Out of scope for this ticket’s manifest:** zero-arg `run_component_tests.sh`; production deploy smoke.

## Self-Assessment

**Scope:** `Single-Component` — Adds operator docs, two bash scripts, and a Joan skill under `~/.cursor/skills/`; no core/data/UI product modules.

**Conf:** `Medium` — Railway CLI + deploy SHA pin is established industry practice; Joan skill is new but follows existing prep-uat / git-operator patterns; Susan must provision test host before E2E proof.

**Risk:** `Medium` — Wrong deploy pin could green-light a stale test host; mitigated by explicit SHA compare and documented wait-for-deploy step. Skill mis-invocation on production host is mitigated by checklist + `ASTRAL_DEPLOY_ENV=integration-test` labeling.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses AST-711 harness; verification script separate from run wrapper |
| §2.1 config | Operator vars env-only in `env.example`; no new `config.py` literals |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §3.3 imports | N/A — scripts only |
| §3.5 naming | `run_railway_integration_tests.sh` parallels `run_integration_tests.sh` |
| §3.6 debug output | Logs under `debug/integration-operator/` — gitignored |

No plan conflicts requiring `conf-!!-NONE`.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-512/AST-712-joan-operator-railway-test-host` |
| **Built tip** | _(after build-child)_ |
| **Stages** | 1 — operator docs + env.example; 2 — verify + railway run scripts; 3 — Joan skill; 4 — Betty bible § Joan operator |
| **Betty next** | Stage 4 bible appendix |
| **test-child manifest** | `run_integration_tests.sh` + `bash -n` on operator scripts; Railway E2E via Susan/Chuckles when host live |
