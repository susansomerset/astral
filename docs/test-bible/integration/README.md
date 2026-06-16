# Integration test tier

**Location:** `tests/integration/` — multi-layer in-process wiring (Flask blueprints → core → data). Not UAT; not live deploy smoke.

**Component suite:** `tests/component/` remains independent. `run_component_tests.sh` does **not** run integration tests unless paths are passed explicitly.

## Harness

```bash
./scripts/testing/run_integration_tests.sh
```

Default target: all of `tests/integration/`. Pass pytest paths or flags after the script name to narrow runs.

**Pass criterion:** pytest green — no branch-coverage gate, no Vitest tail.

## External I/O policy

- **Default:** stub only — env defaults in `tests/integration/conftest.py`; live network blocked in product when `ASTRAL_INTEGRATION_MODE=1` (`src/utils/integration_io.py`).
- **Spikes / manual only:** `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1` opts out of the guard.

## Fixtures

- Temp SQLite per test (`integration_db` / `seeded_candidate`) — same real-DB pattern as `tests/component/data/conftest.py`.
- Auth via mock token authenticator (`test-token` → admin Susan) — no API↔core mocks at blueprint boundaries.
- `integration_app` registers `system_bp` + `candidate_bp` only (minimal v1 harness).

## Growth

- Add scenarios under `tests/integration/scenarios/test_<name>.py`.
- Shared fixtures stay in `tests/integration/conftest.py`.

**Maintainer:** Betty (`qa-child`).

## Joan operator (AST-712)

**Trigger:** after `origin/dev` lands and Susan’s Railway **test** service deploy completes (Chuckles post-`push-dev` / `prep-uat`, or Susan manual invoke).

**Commands:**

```bash
./scripts/testing/verify_integration_deploy_ref.sh
./scripts/testing/run_railway_integration_tests.sh
```

**Skill:** `~/.cursor/skills/integration-operator/SKILL.md`

**Failure triage:** non-zero exit → Joan opens Linear **Discussion** for Chuckles with repro log under `debug/integration-operator/`; Joan does not patch product or enable live external I/O.

**Operator contract:** see [`docs/integration-operator/README.md`](../../integration-operator/README.md) (controlled-vs-live table — do not duplicate here).

### AST-711

**Harness (AST-711 gate — integration only):**

```bash
./scripts/testing/run_integration_tests.sh
```

**Scenarios:**

- `tests/integration/scenarios/test_candidate_nav_api.py` — seeded SQLite + `GET /api/candidates` + `GET /api/nav_config` with Bearer auth; 401 without auth

**Pass criterion:** integration harness green on publish ref tip.

**Out of scope for this ticket:** zero-arg `./scripts/testing/run_component_tests.sh` — full component tree is red on `origin/dev` today from unrelated roster prefilter/rubric expectations (`WEBSITE_FOUND_RETRY` vs `TO_WATCH`); not caused by AST-711 product (`integration_io` + harness + CI only). Track roster component fixes separately; do not block AST-711 closure on zero-arg component gate.

### AST-712

**Harness sanity (required):**

```bash
./scripts/testing/run_integration_tests.sh
```

**Operator scripts — syntax check (required):**

```bash
bash -n scripts/testing/verify_integration_deploy_ref.sh
bash -n scripts/testing/run_railway_integration_tests.sh
```

**Railway E2E (Susan/Chuckles when test host live):** run `integration-operator` skill per § Joan operator above — not required for Betty/test-child closure when Railway CLI absent.

**Pass criterion:** items 1–2 exit 0 on publish ref tip.

**Out of scope:** zero-arg `run_component_tests.sh`; production Railway smoke.
