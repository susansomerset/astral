# Railway test host — Susan provisioning checklist

Susan provisions and maintains the dedicated Railway **integration test** service. Ada documents the contract; Joan consumes it after deploy.

## Service requirements

1. **Separate service** — Dedicated Railway project or service for integration testing. **Not** production. **Not** Susan’s browser staging UAT host if that is a distinct deploy target.

2. **Git deploy source** — Track the **`dev`** branch on GitHub (`origin/dev`). The test host must reflect landed epic work after `prep-uat` / `push-dev`.

3. **Environment label** — Set `ASTRAL_DEPLOY_ENV=integration-test` on the test service (admin nav footer visibility only; optional).

4. **Harness env vars** — Set placeholder values on the Railway service (not committed to git). Mirror `tests/integration/conftest.py` import-time needs and `src/external/gmail.py` `_REQUIRED_VARS`:
   - `GMAIL_USER` (e.g. `astral.test@example.com`)
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (dummy OAuth placeholders)
   - `ANTHROPIC_API_KEY` (dummy placeholder)
   - `ASTRAL_ALLOWED_IPS=` (empty for test harness)

5. **SQLite / data** — Harness uses **temp SQLite per test**; no production database. Default app `data/` directory is sufficient unless Susan mounts a persistent volume for other reasons.

6. **Public URL** — Record the test service URL in the operator machine `.env` as `ASTRAL_RAILWAY_TEST_HOST_URL` (optional HTTP sanity; deploy pin uses Railway CLI, not admin API).

7. **Never on test service** — Do **not** set `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`.

## Operator machine setup

1. Install Railway CLI and authenticate.
2. In the astral repo checkout: `railway link` → select the **test** project/service documented above.
3. Copy `env.example` integration-operator block into operator `.env`.
4. Document the linked service name in operator notes (not in repo secrets).

## Deploy pin (reproducible ref)

Joan’s `verify_integration_deploy_ref.sh` requires:

- Local: `git fetch origin && git rev-parse origin/dev`
- Railway: `railway run -- printenv RAILWAY_GIT_COMMIT_SHA`

Both SHAs must match before the harness runs. If mismatch, wait for Railway deploy to finish after `git push origin dev`.

## Related docs

- Operator runbook: [README.md](./README.md)
- Joan skill: `~/.cursor/skills/integration-operator/SKILL.md`
- Harness: `./scripts/testing/run_integration_tests.sh` (AST-711)
