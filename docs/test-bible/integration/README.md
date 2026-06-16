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

### AST-711

**Harness (full integration gate):**

```bash
./scripts/testing/run_integration_tests.sh
```

**Scenarios:**

- `tests/integration/scenarios/test_candidate_nav_api.py` — seeded SQLite + `GET /api/candidates` + `GET /api/nav_config` with Bearer auth; 401 without auth

**Pass criterion:** integration harness green; component zero-arg harness unchanged
