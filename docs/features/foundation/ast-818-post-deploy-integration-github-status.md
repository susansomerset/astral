# AST-818 — UAT: Post-deploy integration run with GitHub commit status on origin/dev

- **Linear (this ticket):** [AST-818](https://linear.app/astralcareermatch/issue/AST-818/uat-post-deploy-integration-run-with-github-commit-status-on-origindev)
- **Parent:** [AST-512](https://linear.app/astralcareermatch/issue/AST-512/astral-integration-testing) — UAT bug (extends **AST-712** Joan operator). **Depends on:** [AST-711](https://linear.app/astralcareermatch/issue/AST-711) harness, [AST-712](https://linear.app/astralcareermatch/issue/AST-712) Railway operator scripts + skill.
- **Publish ref:** `origin/sub/AST-512/AST-818-post-deploy-integration-github-status`

## Summary

Close Susan UAT gap after **astral-test** (`ASTRAL_DEPLOY_ENV=test`, `astral-test.up.railway.app`) redeploys **origin/dev**: operator scripts must **automatically** wait for deploy pin, run the integration harness on Railway, post a **GitHub commit status** on the landed **origin/dev** SHA (`context: integration/tests`), and on failure **auto-open** a Linear **Discussion** for Chuckles with deploy SHA + log tail. **No** new GitHub Actions workflow; **no** empty commits to **origin/dev**.

## UAT delta (this ticket only)

| Gap (Susan 2026-06-26) | Fix |
|------------------------|-----|
| Integration run requires manual Joan invoke | `watch_post_deploy_integration.sh` + documented cron/systemd on operator machine |
| No GitHub status on dev SHA | `post_github_commit_status.sh` via `gh api` / Commit Statuses API |
| Failures not routed to Linear with full context | `create_integration_failure_discussion.py` + gate orchestrator calls it on non-zero harness exit |

## Out of scope (explicit)

| Item | Reason |
|------|--------|
| New `.github/workflows/*` for integration | Susan deferred proper CI/CD |
| Empty or log-only commits to **origin/dev** | UAT boundary |
| Production / staging Railway hosts | Test service only |
| `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1` | Integration tier contract |
| Changes to pytest scenarios / harness assertions | AST-711 |
| `tests/` or `docs/test-bible/**` | Betty (`qa-child`) |

## Build prerequisite (mandatory before Stage 1)

On **`epic worktree`**, branch **`sub/AST-512/AST-818-post-deploy-integration-github-status`**:

```bash
git fetch origin
git merge origin/ftr/AST-512-astral-integration-testing
```

**Done when:** AST-712 operator scripts exist and `./scripts/testing/run_integration_tests.sh` passes locally (3 tests):

```bash
./scripts/testing/run_integration_tests.sh
bash -n scripts/testing/verify_integration_deploy_ref.sh
bash -n scripts/testing/run_railway_integration_tests.sh
```

If **AST-712** product is not on **`ftr/`** yet, merge **`origin/sub/AST-512/AST-712-joan-operator-railway-test-host`** into the publish ref before Stage 1 — do not plan around missing operator scripts.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `scripts/post_github_commit_status.sh` | Post success/failure status to GitHub Commit Statuses API | scripts | Ada (build) |
| `scripts/create_integration_failure_discussion.py` | Create Linear Discussion for Chuckles with repro template | scripts | Ada (build) |
| `scripts/testing/post_deploy_integration_gate.sh` | Orchestrator: wait pin → harness → GitHub status → Linear on fail | scripts | Ada (build) |
| `scripts/testing/watch_post_deploy_integration.sh` | Poll `origin/dev`; invoke gate when deploy ready; dedupe by SHA | scripts | Ada (build) |
| `env.example` | `GITHUB_TOKEN` / status context vars; operator automation notes | docs | Ada (build) |
| `docs/integration-operator/README.md` | § Post-deploy gate + automation (cron example) | docs | Ada (build) |
| `docs/integration-operator/POST_DEPLOY_GATE.md` | Gate contract, env vars, idempotency, GitHub/Linear behavior | docs | Ada (build) |
| `~/.cursor/skills/integration-operator/SKILL.md` | Auto gate + status + auto Linear; deprecate manual-only flow | skill | Ada (build) |
| `docs/test-bible/integration/README.md` | § AST-818 post-deploy gate pointer | bible | Betty (qa-child) |

## Stage 1: GitHub commit status helper

**Done when:** `scripts/post_github_commit_status.sh` is executable; with valid `GITHUB_TOKEN` (or `gh auth`), posting to a test SHA succeeds; script exits non-zero on missing token or API error.

1. Create `scripts/post_github_commit_status.sh`:

```bash
#!/usr/bin/env bash
# Post GitHub commit status for integration gate (AST-818). No GHA — Statuses API only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SHA="${1:?commit sha}"
STATE="${2:?state: pending|success|failure|error}"
DESCRIPTION="${3:-}"
CONTEXT="${ASTRAL_INTEGRATION_STATUS_CONTEXT:-integration/tests}"

if ! command -v gh >/dev/null 2>&1; then
  echo "BLOCKED: gh CLI not installed (https://cli.github.com/)" >&2
  exit 2
fi

REMOTE="$(git remote get-url origin)"
# susansomerset/astral from git@github.com:susansomerset/astral.git or https URL
if [[ "$REMOTE" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]%.git}"
else
  echo "BLOCKED: cannot parse owner/repo from origin: $REMOTE" >&2
  exit 2
fi

ARGS=(-f "state=$STATE" -f "context=$CONTEXT")
if [[ -n "$DESCRIPTION" ]]; then
  ARGS+=(-f "description=$DESCRIPTION")
fi

gh api "repos/${OWNER}/${REPO}/statuses/${SHA}" "${ARGS[@]}"
echo "github-status ok: $CONTEXT $STATE @ ${SHA:0:7}"
```

2. `chmod +x scripts/post_github_commit_status.sh`.

3. In `env.example`, after the integration-operator block (`ASTRAL_RAILWAY_TEST_HOST_URL`), append:

```bash
# Post-deploy integration gate (AST-818) — GitHub commit status on origin/dev SHA
# gh auth login OR token with repo:status (never commit real token)
# GITHUB_TOKEN=ghp_...
ASTRAL_INTEGRATION_STATUS_CONTEXT=integration/tests
```

⚠️ **Decision:** Use **`gh api`** (Susan user rule) — not raw curl — so operator machine uses existing `gh auth` when token env unset. Script requires **`gh`** installed; no new Python GitHub client.

## Stage 2: Linear failure Discussion automation

**Done when:** `scripts/create_integration_failure_discussion.py` creates a **Discussion** issue assigned to Chuckles, parent **AST-512**, with deploy SHA, command, and log tail; exits 0 on create; exits 2 when Linear key missing.

1. Create `scripts/create_integration_failure_discussion.py` — stdlib + urllib only (mirror `scripts/rebuild_merge_ticket_log.py` style; **no** `src/` imports):

   - **`_api_key()`** — first non-empty among `LINEAR_KEY_CHUCKLES`, `LINEAR_API_KEY`, `LINEAR_KEY_CURSOR`; exit **2** with `BLOCKED:` stderr if missing.
   - **`_gql(key, query, variables=None)`** — POST to `https://api.linear.app/graphql`; raise on `errors`.
   - **`_resolve_ids(key)`** — one GraphQL query returning `(team_id, project_id, state_id, chuckles_user_id, parent_id)` for:
     - team **`AST`**
     - workflow state **`Discussion`**
     - project **`Astral Foundation`**
     - Chuckles user email from env **`LINEAR_CHUCKLES_EMAIL`** default **`susan+chuckles@susansomerset.com`**
     - parent issue **`AST-512`** (number 512)
   - **CLI args:** `--sha` (required), `--railway-sha`, `--host` (default `os.environ.get("ASTRAL_RAILWAY_TEST_HOST_URL", "")`), `--log`, `--tail-lines` default **80**.
   - **Body template** — same sections as AST-712 skill (Deploy / Command / Log tail / Joan action); command line **`./scripts/testing/post_deploy_integration_gate.sh`**; default host fallback **`astral-test.up.railway.app`** when `--host` and env empty.
   - **Title:** `Integration harness failure — test host @ <short-sha>`.
   - **`issueCreate`** with `teamId`, `projectId`, `stateId`, `assigneeId`, `parentId`, `title`, `description`.
   - **Success:** print `identifier` and `url` to stdout; exit **0**. **GraphQL failure:** stderr + exit **1**.

2. `chmod +x scripts/create_integration_failure_discussion.py`.

3. Do **not** extend `src/external/linear.py` — keep operator-only script under `scripts/` (no Flask/runtime import path).

⚠️ **Decision:** Failures create **new** Discussion issues (not comments) so Chuckles inbox triage matches AST-712 skill; dedupe is Chuckles’ job if the same SHA fails twice.

## Stage 3: Post-deploy gate orchestrator

**Done when:** `post_deploy_integration_gate.sh` waits for deploy pin (optional), runs harness, always posts GitHub status (success or failure), calls Linear script on failure, exits with harness exit code.

1. Create `scripts/testing/post_deploy_integration_gate.sh`:

```bash
#!/usr/bin/env bash
# Post-deploy integration gate: Railway harness + GitHub status + Linear on fail (AST-818).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
git fetch origin
SHA="$(git rev-parse origin/dev)"
SHORT="${SHA:0:7}"
LOG=""
HARNESS_STATUS=0
GATE_LOG_DIR="$ROOT/debug/integration-operator"
mkdir -p "$GATE_LOG_DIR"

# Optional wait for Railway deploy (seconds between tries)
WAIT="${ASTRAL_INTEGRATION_GATE_WAIT_SEC:-30}"
MAX_TRIES="${ASTRAL_INTEGRATION_GATE_MAX_TRIES:-40}"
TRIES=0
until "$ROOT/scripts/testing/verify_integration_deploy_ref.sh" "$SHA"; do
  TRIES=$((TRIES + 1))
  if (( TRIES >= MAX_TRIES )); then
    "$ROOT/scripts/post_github_commit_status.sh" "$SHA" failure "deploy pin timeout @ ${SHORT}"
    exit 1
  fi
  sleep "$WAIT"
done

RAILWAY_SHA="$(railway run -- printenv RAILWAY_GIT_COMMIT_SHA 2>/dev/null | tr -d '[:space:]' || true)"

"$ROOT/scripts/post_github_commit_status.sh" "$SHA" pending "integration harness running @ ${SHORT}" || true

set +e
"$ROOT/scripts/testing/run_railway_integration_tests.sh"
HARNESS_STATUS=$?
set -e

LOG="$(ls -t "$GATE_LOG_DIR"/run-*.log 2>/dev/null | head -1 || true)"

if (( HARNESS_STATUS == 0 )); then
  "$ROOT/scripts/post_github_commit_status.sh" "$SHA" success "integration tests passed @ ${SHORT}"
  echo "gate ok: $SHA"
  exit 0
fi

"$ROOT/scripts/post_github_commit_status.sh" "$SHA" failure "integration tests failed @ ${SHORT}"
if command -v python3 >/dev/null 2>&1; then
  python3 "$ROOT/scripts/create_integration_failure_discussion.py" \
    --sha "$SHA" \
    --railway-sha "${RAILWAY_SHA:-}" \
    --log "${LOG:-}" || true
fi
echo "gate failed: $SHA log=${LOG:-none}"
exit "$HARNESS_STATUS"
```

2. `chmod +x scripts/testing/post_deploy_integration_gate.sh`.

3. Do **not** modify `run_railway_integration_tests.sh` or `verify_integration_deploy_ref.sh` except if build discovers a bug — prefer wrapping in gate script.

⚠️ **Decision:** Gate posts **`pending`** before harness run so GitHub shows in-progress status on the dev SHA; final state overwrites same `context`.

## Stage 4: Deploy watcher (automation entry)

**Done when:** `watch_post_deploy_integration.sh` detects new `origin/dev` SHA, skips if already gated (state file), invokes gate once per SHA.

1. Create `scripts/testing/watch_post_deploy_integration.sh`:

```bash
#!/usr/bin/env bash
# Poll origin/dev + Railway deploy; run post_deploy_integration_gate once per SHA (AST-818).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
STATE_FILE="$ROOT/debug/integration-operator/last_gate_sha"
git fetch origin
SHA="$(git rev-parse origin/dev)"
if [[ -f "$STATE_FILE" ]] && [[ "$(cat "$STATE_FILE")" == "$SHA" ]]; then
  echo "skip: already gated $SHA"
  exit 0
fi
"$ROOT/scripts/testing/post_deploy_integration_gate.sh"
echo "$SHA" > "$STATE_FILE"
```

2. `chmod +x scripts/testing/watch_post_deploy_integration.sh`.

3. Create `docs/integration-operator/POST_DEPLOY_GATE.md` documenting:
   - **Purpose** — automatic post-deploy integration gate (AST-818)
   - **Entry points** — `watch_post_deploy_integration.sh` (automation), `post_deploy_integration_gate.sh` (single shot)
   - **Env vars** — `ASTRAL_INTEGRATION_STATUS_CONTEXT`, `ASTRAL_INTEGRATION_GATE_WAIT_SEC`, `ASTRAL_INTEGRATION_GATE_MAX_TRIES`, `GITHUB_TOKEN` / `gh auth`, `LINEAR_KEY_CHUCKLES`, `ASTRAL_RAILWAY_TEST_HOST_URL`
   - **Cron example** (operator machine, every 5 min after dev pushes):
     ```cron
     */5 * * * * cd /path/to/astral && ./scripts/testing/watch_post_deploy_integration.sh >> debug/integration-operator/watch.log 2>&1
     ```
   - **Idempotency** — `debug/integration-operator/last_gate_sha` prevents duplicate runs for same SHA
   - **No dev mutations** — status API only; never commit to **origin/dev**

4. Append to `docs/integration-operator/README.md` section **Post-deploy gate (AST-818)** linking `POST_DEPLOY_GATE.md` and listing the two new scripts.

⚠️ **Decision:** Automation is **operator-machine cron** (or systemd timer), not Railway in-container hook — Susan already redeploys astral-test on dev push; watcher closes the loop without GHA.

## Stage 5: Joan skill update

**Done when:** `~/.cursor/skills/integration-operator/SKILL.md` documents automated post-deploy flow as primary path; manual two-script flow remains as fallback.

1. Replace **Procedure** § with:
   - Primary: `./scripts/testing/watch_post_deploy_integration.sh` (or cron)
   - Single shot after known deploy: `./scripts/testing/post_deploy_integration_gate.sh`
   - Manual fallback: verify + run_railway (AST-712)

2. Add **GitHub status** bullet — context `integration/tests` on **origin/dev** SHA; verify on GitHub commit checks UI.

3. Replace manual **Failure triage** with: gate auto-creates Discussion via `create_integration_failure_discussion.py`; Joan only files manually if automation failed.

4. Add **Does NOT** bullets: no GHA workflow; no empty dev commits.

## Stage 6: Bible appendix (Betty — `qa-child`, not Ada commits)

**Done when:** `docs/test-bible/integration/README.md` has **§ AST-818** with gate commands and manifest pointers.

1. Append section **AST-818** with:
   - `bash -n` on all four operator/gate scripts
   - `./scripts/testing/run_integration_tests.sh` sanity
   - `post_deploy_integration_gate.sh` dry-run blocked without Railway (document `[qa-handoff]` only if manifest impossible on `astral-tests`)

2. Link `docs/integration-operator/POST_DEPLOY_GATE.md` — no duplicate env table.

## QA manifest (Betty → test-child)

```bash
./scripts/testing/run_integration_tests.sh
bash -n scripts/post_github_commit_status.sh
bash -n scripts/testing/post_deploy_integration_gate.sh
bash -n scripts/testing/watch_post_deploy_integration.sh
python3 -m py_compile scripts/create_integration_failure_discussion.py
```

**Railway + GitHub E2E:** Susan/Chuckles after cron wired — not required for test-child if CLI/tokens absent.

**Out of scope:** zero-arg `run_component_tests.sh`; GHA workflow existence check.

## Self-Assessment

**Scope:** `Single-Component` — four bash scripts, one Python CLI, operator docs, Joan skill patch; no core/data/UI modules.

**Conf:** `Medium` — GitHub Statuses API and Linear create are straightforward; Chuckles email / workflow state IDs must resolve correctly; cron wiring is Susan/operator-machine ops.

**Risk:** `Medium` — Wrong Linear assignee or missing `gh auth` silently skips status/ticket; mitigated by explicit BLOCKED exits and gate posting failure status before exit. Duplicate Discussion tickets on re-run mitigated by `last_gate_sha` idempotency.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Gate wraps AST-712 scripts; status + Linear are separate helpers |
| §2.1 config | Gate env vars env-only; not `config.py` literals |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §3.3 imports | Linear script standalone; no cross-layer product imports |
| §3.5 naming | `post_deploy_*` / `watch_post_deploy_*` parallel existing operator scripts |
| §3.6 debug output | State + logs under `debug/integration-operator/` (gitignored) |

No plan conflicts requiring `conf-!!-NONE`.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-512/AST-818-post-deploy-integration-github-status` |
| **Built tip** | `10bc9f8` (repo) + `~/.cursor/skills/integration-operator/SKILL.md` (Stage 5) |
| **Stages** | 1 — GitHub status (`3087ce2`); 2 — Linear script (`8bef457`); 3 — gate (`c7c447f`); 4 — watcher + docs; 5 — Joan skill (operator machine) |
| **Betty next** | Stage 6 bible § AST-818 |
| **test-child manifest** | § QA manifest above |
