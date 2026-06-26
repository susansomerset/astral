# Post-deploy integration gate (AST-818)

Automatic integration harness run after **astral-test** deploys **origin/dev**, with GitHub commit status and Linear failure routing.

## Purpose

Closes the UAT gap where Railway redeploys on dev push but integration tests do not run until Joan is invoked manually. The gate waits for deploy pin, runs the AST-712 Railway harness, posts GitHub status on the **origin/dev** SHA, and opens a Linear **Discussion** for Chuckles on failure.

## Entry points

| Script | Use |
|--------|-----|
| `./scripts/testing/watch_post_deploy_integration.sh` | **Automation** — skip if SHA already gated; invoke gate once per new dev tip |
| `./scripts/testing/post_deploy_integration_gate.sh` | **Single shot** — after known deploy complete |

Manual AST-712 fallback (no GitHub status / auto Linear):

```bash
./scripts/testing/verify_integration_deploy_ref.sh
./scripts/testing/run_railway_integration_tests.sh
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ASTRAL_INTEGRATION_STATUS_CONTEXT` | `integration/tests` | GitHub commit status context |
| `ASTRAL_INTEGRATION_GATE_WAIT_SEC` | `30` | Seconds between deploy-pin retries |
| `ASTRAL_INTEGRATION_GATE_MAX_TRIES` | `40` | Max deploy-pin attempts (~20 min) |
| `ASTRAL_RAILWAY_TEST_HOST_URL` | — | Recorded in failure tickets (optional) |
| `LINEAR_KEY_CHUCKLES` / `LINEAR_API_KEY` | — | Required for auto Discussion on failure |
| `LINEAR_CHUCKLES_EMAIL` | `susan+chuckles@susansomerset.com` | Assignee lookup |
| `GITHUB_TOKEN` or `gh auth login` | — | Required for commit status API |

See also `env.example` integration-operator and post-deploy blocks.

## Automation (operator machine)

Susan/Chuckles wire a cron or systemd timer on the machine with `railway link` to **astral-test** and `gh auth`:

```cron
*/5 * * * * cd /path/to/astral && ./scripts/testing/watch_post_deploy_integration.sh >> debug/integration-operator/watch.log 2>&1
```

## Idempotency

- `debug/integration-operator/last_gate_sha` — watcher skips duplicate runs for the same **origin/dev** SHA
- Harness logs: `debug/integration-operator/run-<timestamp>.log`

## GitHub status

- Context: **`integration/tests`** (override via `ASTRAL_INTEGRATION_STATUS_CONTEXT`)
- States: `pending` → `success` or `failure` on the **origin/dev** commit SHA
- **No** GitHub Actions workflow; **no** commits to **origin/dev**

## Failure routing

On harness failure, `post_deploy_integration_gate.sh` calls `scripts/create_integration_failure_discussion.py` to open a Linear **Discussion** assigned to Chuckles, parent **AST-512**, with deploy SHA and log tail.

## Related

- [Operator runbook](./README.md)
- [Railway test host checklist](./RAILWAY_TEST_HOST.md)
- Joan skill: `~/.cursor/skills/integration-operator/SKILL.md`
