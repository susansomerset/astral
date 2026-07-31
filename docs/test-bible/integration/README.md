# Integration test tier

**Location:** `tests/integration/` — multi-layer in-process wiring (Flask blueprints → core → data). Not UAT; not live deploy smoke.

**Component suite:** `tests/component/` remains independent. `run_component_tests.sh` does **not** run integration tests unless paths are passed explicitly.

**Maintainer (existing scenarios):** Betty (`qa-child`) — revise when product invalidates an existing scenario; keep this map honest. Inventing new integration coverage is **not** the default deliverable of a Betty pass.

## How to run

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

## Coverage by function area

### Candidate list + nav config (API → core → data)

**Status:** has coverage

**What it proves:** Seeded SQLite + Bearer auth for `GET /api/candidates` and `GET /api/nav_config`; Jobs group visibility follows candidate state (`ACTIVE_SEARCH` shows Jobs; `NEW_CANDIDATE` hides the group); unauthenticated nav returns 401.

**Scenarios:**

- `tests/integration/scenarios/test_candidate_nav_api.py`

**Citations:** AST-711 (first scenario + harness); AST-990 (early-lifecycle seed aligned to `NEW_CANDIDATE`)

### Controlled external I/O (product guard)

**Status:** has coverage (infrastructure)

**What it proves:** Under default harness mode, live external network calls are blocked unless an explicit opt-out is set.

**Where:** `src/utils/integration_io.py` plus harness env defaults in `tests/integration/conftest.py` — exercised whenever the suite runs under stub policy.

**Citations:** AST-711

### Additional API blueprints beyond system + candidate

**Status:** should-have

**Gap:** The v1 harness registers only `system_bp` + `candidate_bp`. Other UI blueprints have no multi-layer in-process scenarios in this tier yet.

**Citations:** none (gap)

### Company / roster cultivation paths

**Status:** should-have

**Gap:** No integration scenario covers company roster multi-layer flows through API → core → data.

**Citations:** none (gap)

### Job pipeline (qualify / gaze / consult seams)

**Status:** should-have

**Gap:** No integration scenario covers job-entity multi-layer paths end-to-end in this tier.

**Citations:** none (gap)

### Artifact generation pipeline

**Status:** should-have

**Gap:** No integration scenario covers artifact generate/resume through UI → core → data (external stubs).

**Citations:** none (gap)

### Full-server / scheduler bootstrap

**Status:** should-have

**Gap:** v1 harness intentionally avoids full `ui.server` bootstrap and the in-process scheduler. Full-boot scenarios are not present yet.

**Citations:** AST-711 (minimal-app decision; full-server left open)

## Related: Joan Railway post-deploy operator

Adjacency only — **not** an in-process `tests/integration/` scenario area, and **not** a prep-uat smoke proposal.

**Trigger:** after `origin/dev` lands and Susan’s Railway **test** service deploy completes (Chuckles post-`push-dev` / `prep-uat`, or Susan manual invoke).

**Commands:**

```bash
./scripts/testing/verify_integration_deploy_ref.sh
./scripts/testing/run_railway_integration_tests.sh
```

**Skill:** `~/.cursor/skills/integration-operator/SKILL.md`

**Failure triage:** non-zero exit → Joan opens Linear **Discussion** for Chuckles with repro log under `debug/integration-operator/`; Joan does not patch product or enable live external I/O.

**Post-deploy gate (extends operator):** automatic Railway harness run after `origin/dev` deploy, GitHub commit status on the dev SHA (`integration/tests`), Linear **Discussion** auto-create on failure. Contract: [`docs/integration-operator/POST_DEPLOY_GATE.md`](../../integration-operator/POST_DEPLOY_GATE.md).

**Operator contract:** see [`docs/integration-operator/README.md`](../../integration-operator/README.md) (controlled-vs-live table — do not duplicate here).

**Citations:** AST-712 (operator + Railway test host); AST-818 (post-deploy GitHub status + failure Discussion)

## Growth

- Add scenarios under `tests/integration/scenarios/test_<name>.py`.
- Shared fixtures stay in `tests/integration/conftest.py`.
- Program positions for **new** coverage ownership, prep-uat smoke, and CI vendors are **out of scope for this README** — sibling ADR AST-1004 after Archie approval.
