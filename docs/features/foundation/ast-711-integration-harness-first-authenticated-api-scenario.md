# AST-711 — Integration harness and first authenticated API scenario

- **Linear (this ticket):** [AST-711](https://linear.app/astralcareermatch/issue/AST-711/integration-harness-and-first-authenticated-api-scenario-astral-integration)
- **Parent:** [AST-512](https://linear.app/astralcareermatch/issue/AST-512/astral-integration-testing) — Slice 1 (harness + first scenario + Bible + CI). **Out of scope:** Joan operator / Railway test host (**AST-712**).
- **Publish ref:** `origin/sub/AST-512/AST-711-integration-harness-first-api-scenario`

## Summary

Open Astral’s **integration test tier** with a standalone `run_integration_tests.sh` entry point, a product-level **controlled-vs-live external I/O** guard, CI wiring, and Betty-owned first scenario under `tests/integration/`: **real SQLite + authenticated candidate list + nav_config round-trip** through Flask blueprints and core/data — **no** live Anthropic, Playwright, Gmail, Google CSE, or Stytch network calls. Component tests, branch-coverage locks, and Vitest gates stay unchanged.

## Layer contract (mandatory)

| Seam | Integration tier rule |
|------|------------------------|
| `src/external/*` | **Stub only** — monkeypatch or autouse fixtures; live network blocked when `ASTRAL_INTEGRATION_MODE=1` unless `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1` (spikes/manual only). |
| `src/data/*` ↔ `src/core/*` | **Real** — same temp-file SQLite pattern as component data fixtures. |
| `src/ui/api/*` ↔ `src/core/*` | **Real** — do **not** monkeypatch `get_candidate`, `list_candidates`, or other core calls at the API module boundary in integration scenarios. |
| Component suite | **Independent** — `run_component_tests.sh` must **not** invoke `tests/integration/` unless the caller passes those paths explicitly (default zero-arg behavior unchanged). |

⚠️ **Decision:** First scenario uses a **minimal Flask app** registering only `system_bp` + `candidate_bp` (not full `ui.server` bootstrap). Avoids scheduler/`bootstrap_runtime()` gating for v1; still proves auth + routing + persistence across API → core → data. Full-server boot scenarios remain valid later (**AST-512** decision **(a)**).

⚠️ **Decision:** Controlled I/O is enforced in **product code** at each external public entry point via `src/utils/integration_io.py`, not pytest markers alone — satisfies parent “implement a single product rule.”

## Out of scope (explicit)

| Item | Owner / ticket |
|------|----------------|
| `tests/` or `docs/test-bible/**` commits | **Betty** (`qa-child`) — engineer pre-commit hook blocks |
| Joan skill, Railway test host, failure ticketing | **AST-712** |
| Branch-coverage / `LOCKED_AT_100` for integration runs | N/A — behavioral pass/fail only |
| Live external I/O in default harness | Forbidden |
| Changes to `run_component_tests.sh` coverage gate or Vitest tail | Forbidden unless required to keep zero-arg component run green |

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `src/utils/integration_io.py` | New — `is_integration_harness()`, `require_controlled_external_io(caller)` | utils | Ada (build) |
| `src/external/anthropic.py` | Call guard at `send_to_anthropic` entry | external | Ada (build) |
| `src/external/deepseek.py` | Call guard at `send_to_deepseek` entry | external | Ada (build) |
| `src/external/playwright.py` | Call guard at primary browser/session entry used for live navigation | external | Ada (build) |
| `src/external/gmail.py` | Call guard at send/dispatch entry | external | Ada (build) |
| `src/external/google_cse.py` | Call guard at search entry | external | Ada (build) |
| `src/external/stytch.py` | Call guard at `authenticate_session_jwt` entry | external | Ada (build) |
| `scripts/testing/run_integration_tests.sh` | New standalone harness | scripts | Ada (build) |
| `.github/workflows/integration-tests.yml` | New CI job running harness on `dev` + `ftr/**` pushes | ci | Ada (build) |
| `tests/integration/conftest.py` | Shared fixtures: real DB, auth stub, minimal app, env defaults | tests | Betty (qa-child) |
| `tests/integration/scenarios/test_candidate_nav_api.py` | First scenario — list + nav round-trip | tests | Betty (qa-child) |
| `tests/integration/.gitkeep` | Remove when first test lands | tests | Betty (qa-child) |
| `docs/test-bible/integration/README.md` | Integration tier definition, I/O policy, fixture contract, harness command | bible | Betty (qa-child) |
| `docs/test-bible/README.md` | Replace integration placeholder; add `integration/` row to layer index | bible | Betty (qa-child) |
| `docs/ASTRAL_TEST_BIBLE.md` | §2 integration placeholder → pointer to `docs/test-bible/integration/` | bible | Betty (qa-child) |

## Stage 1: Controlled external I/O contract

**Done when:** With `ASTRAL_INTEGRATION_MODE=1` and without `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1`, each guarded external entry raises `RuntimeError` whose message includes the caller name and “integration mode”; with neither env var set, existing component behavior is unchanged.

1. Create `src/utils/integration_io.py`:

```python
"""Integration harness external I/O contract (AST-512 / AST-711)."""
import os

_INTEGRATION_ENV = "ASTRAL_INTEGRATION_MODE"
_LIVE_OPT_IN_ENV = "ASTRAL_ALLOW_LIVE_EXTERNAL_IO"


def is_integration_harness() -> bool:
    return os.environ.get(_INTEGRATION_ENV) == "1"


def require_controlled_external_io(caller: str) -> None:
    if not is_integration_harness():
        return
    if os.environ.get(_LIVE_OPT_IN_ENV) == "1":
        return
    raise RuntimeError(
        f"{caller}: live external I/O blocked in integration mode "
        f"(set {_LIVE_OPT_IN_ENV}=1 only for spikes or manual ops)"
    )
```

2. At the **first line** of each public network entry below (after docstring / imports, before any SDK client use), add `require_controlled_external_io("<module>.<function>")`:

   - `src/external/anthropic.py` — `send_to_anthropic`
   - `src/external/deepseek.py` — `send_to_deepseek`
   - `src/external/gmail.py` — the function that performs Gmail API send (currently used by monitor/core callers)
   - `src/external/google_cse.py` — the main search function exported to core
   - `src/external/stytch.py` — `authenticate_session_jwt`
   - `src/external/playwright.py` — the lowest-level function that launches a browser or opens a live page session (pick the single entry all scrape paths use — typically browser launch / `async_playwright` context creation)

3. Do **not** add integration env vars to `config.py` literals — these are harness-only env flags read in `integration_io.py` only (**ASTRAL_CODE_RULES** §2.1 env vs config split).

## Stage 2: Standalone integration harness

**Done when:** `./scripts/testing/run_integration_tests.sh` exits 0 once Betty’s Stage 4 tests exist; the script is executable; it sets integration env; it does **not** run coverage gates or Vitest.

1. Create `scripts/testing/run_integration_tests.sh` modeled on `run_component_tests.sh` **without** `--cov`, `check_per_file_coverage.py`, or the frontend tail:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
# Reuse component venv bootstrap
if [[ -n "${ASTRAL_PYTHON:-}" ]]; then
  PYTHON="$ASTRAL_PYTHON"
else
  "$ROOT/scripts/testing/ensure_component_venv.sh"
  PYTHON="$ROOT/.venv/bin/python"
fi
export ASTRAL_INTEGRATION_MODE=1
unset ASTRAL_ALLOW_LIVE_EXTERNAL_IO
export ASTRAL_DB_DIR="${ASTRAL_DB_DIR:-$ROOT/data}"
mkdir -p "$ASTRAL_DB_DIR"
PY_TARGETS=(tests/integration)
if (("$#" > 0)); then
  PY_TARGETS=("$@")
fi
exec "$PYTHON" -m pytest "${PY_TARGETS[@]}"
```

2. `chmod +x scripts/testing/run_integration_tests.sh`.

3. Confirm `run_component_tests.sh` is **unchanged** in default (zero-arg) behavior — no import or subprocess of the integration harness.

⚠️ **Decision:** Integration harness sets required Gmail/Anthropic env defaults in **`tests/integration/conftest.py`** (Betty), not in the shell script — matches component `conftest.py` import-time patterns.

## Stage 3: CI gate

**Done when:** GitHub Actions runs `./scripts/testing/run_integration_tests.sh` on pushes to `dev` and `ftr/**`, installs Python deps via existing `ensure_component_venv.sh` / `requirements.txt`, and fails the workflow when pytest fails.

1. Add `.github/workflows/integration-tests.yml`:

```yaml
name: Integration tests

on:
  push:
    branches:
      - dev
      - 'ftr/**'
  pull_request:
    branches:
      - dev

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run integration harness
        run: ./scripts/testing/run_integration_tests.sh
```

2. Do **not** add integration runs to `ftr-merge-ready.yml` (that workflow remains merge-tree hygiene only).

## Stage 4: First integration scenario + Bible (Betty — `qa-child`, not Ada commits)

**Done when:** `./scripts/testing/run_integration_tests.sh` passes; parent AC 1–4 and 6 are satisfied; component zero-arg harness still passes on the publish ref after Betty’s `merge-tests()`.

### 4a. `tests/integration/conftest.py`

1. Set import-time env defaults (before external imports): `GMAIL_*`, `GOOGLE_*`, `ANTHROPIC_API_KEY`, `ASTRAL_ALLOWED_IPS=""` — mirror `tests/component/ui/conftest.py` / `tests/component/external/conftest.py`.

2. `@pytest.fixture(autouse=True)` register mock token authenticator on `src.utils.auth` (same token map as `tests/component/ui/conftest.py`: `test-token` → admin Susan, `good-jwt` → non-admin, invalid → `ValueError`).

3. `@pytest.fixture` `integration_db(tmp_path, monkeypatch)` — copy the real SQLite pattern from `tests/component/data/conftest.py`: set `ASTRAL_DB_DIR`, patch `database.DB_PATH`, reset `_SCHEMA_FLAGS`, return `database` module.

4. `@pytest.fixture` `seeded_candidate(integration_db)` — `integration_db.save_candidate("cand-1", state="LIVE_PROMPTS", candidate_data={"name": "Integration Test"})`.

5. `@pytest.fixture` `integration_app(monkeypatch)` — build `Flask(__name__)`, register `system_bp` and `candidate_bp` from `ui.api.api_system` / `ui.api.api_candidate`, `app.config["TESTING"] = True`. **Do not** monkeypatch `get_candidate` or `list_candidates`.

6. `@pytest.fixture` `auth_headers` → `{"Authorization": "Bearer test-token"}`.

### 4b. `tests/integration/scenarios/test_candidate_nav_api.py`

1. Add module docstring stating AST-711 first scenario: persistence + HTTP + auth; external I/O stubbed via conftest env + product guard.

2. `test_list_candidates_returns_seeded_row(integration_app, seeded_candidate, auth_headers)`:
   - `client = integration_app.test_client()`
   - `GET /api/candidates` with `auth_headers` → **200**
   - JSON is a list containing one dict with `astral_candidate_id == "cand-1"` and `state == "LIVE_PROMPTS"` (read from **real DB**, not mocked core).

3. `test_nav_config_reflects_seeded_candidate_state(integration_app, seeded_candidate, auth_headers)`:
   - `GET /api/nav_config?candidate_id=cand-1` with `auth_headers` → **200**
   - Payload is a list of nav groups; at least one **non-Admin** item has `"enabled": true` that would be disabled for `NEW` state (prove state came from DB — e.g. an item gated on `LIVE_PROMPTS` or later in `CANDIDATE_STATES` order). Pick one stable path from `NAV_CONFIG` and assert `enabled` is `True` for `LIVE_PROMPTS` and would be `False` if you re-seeded as `NEW` (second assertion optional inline or parametrized).

4. `test_unauthenticated_nav_config_returns_401(integration_app, seeded_candidate)`:
   - `GET /api/nav_config?candidate_id=cand-1` without auth → **401**.

5. Delete `tests/integration/.gitkeep` when adding the scenario file.

### 4c. Betty bible deliverables

1. Create `docs/test-bible/integration/README.md` documenting:
   - **Location:** `tests/integration/` vs `tests/component/`
   - **Purpose:** multi-layer in-process wiring; not UAT; not live deploy smoke
   - **Harness:** `./scripts/testing/run_integration_tests.sh` (only integration gate by default)
   - **External I/O:** stubs at `src/external/*`; `ASTRAL_INTEGRATION_MODE=1`; opt-in live via `ASTRAL_ALLOW_LIVE_EXTERNAL_IO=1` for spikes only
   - **Fixtures:** temp SQLite per test; auth via mock authenticator; no API↔core mocks
   - **Growth:** add `tests/integration/scenarios/test_<name>.py`; shared fixtures stay in `conftest.py`
   - **Maintainer:** Betty

2. In `docs/test-bible/README.md`:
   - Replace the “placeholder only” integration bullet under **Where tests live** with a link to `integration/README.md`
   - Add layer index row: `Integration | integration/ | tests/integration/`

3. In `docs/ASTRAL_TEST_BIBLE.md` §2, replace the integration placeholder sentence with: “See `docs/test-bible/integration/README.md`.”

4. Append `### AST-711` manifest block to `docs/test-bible/integration/README.md`:

```
### AST-711

**Harness (full integration gate):**
./scripts/testing/run_integration_tests.sh

**Scenarios:**
- tests/integration/scenarios/test_candidate_nav_api.py — seeded SQLite + GET /api/candidates + GET /api/nav_config with Bearer auth; 401 without auth

**Pass criterion:** integration harness green on publish ref tip (`./scripts/testing/run_integration_tests.sh` exit 0). Zero-arg `./scripts/testing/run_component_tests.sh` is **not** an AST-711 closure gate — roster prefilter reds on `origin/dev` baseline are unrelated (Betty `cec444b` / `[qa-handoff]`).
```

## QA expectations (Betty manifest — test-child gate)

After Ada **Code Complete**, Betty runs `qa-child` and publishes `merge-tests(AST-711)` to `origin/sub/AST-512/AST-711-integration-harness-first-api-scenario` before **Tests Ready**.

**Tests Ready manifest for Ada (`test-child`) — authoritative @ `cec444b`:**

```bash
./scripts/testing/run_integration_tests.sh
```

Pass criterion: exit 0 on publish ref tip. **Not gated:** zero-arg `./scripts/testing/run_component_tests.sh` (dev-baseline roster drift; track separately).

## Execution contract (build-child)

- Execute Ada stages **1 → 2 → 3** in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-512/AST-711-integration-harness-first-api-scenario`.
- **Do not** commit under `tests/` or `docs/test-bible/**` — Betty Stage 4 owns those paths.
- If `NAV_CONFIG` gates make the Stage 4b nav assertion ambiguous at build time, stop with **`🛑`** on **AST-512** naming the chosen path + expected `enabled` for `LIVE_PROMPTS` vs `NEW`.
- After Betty lands tests, Ada **test-child** runs the integration harness manifest above; failures in product code → fix on epic worktree; failures in test/manifest → `[qa-handoff]` to Betty.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — New harness script, CI workflow, utils guard, and external-layer entry guards across six modules; Betty adds the first `tests/integration/` tree and bible tier docs.

**Conf:** `Medium` — Patterns are established (component conftest, UI auth stubs, `run_component_tests.sh`); the new tier is mostly wiring, but external guard placement and nav assertion stability need careful execution.

**Risk:** `Medium` — Incorrect guard placement could break component tests that patch externals after import; CI adds a new required gate on `dev`/`ftr` pushes — keep integration suite fast and isolated from coverage locks.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `integration_io.py` helper; external modules one-line guard; fixtures reuse component SQLite/auth patterns via Betty spec |
| §2.1 config | Harness flags env-only in `integration_io.py`, not config literals |
| §2.4 batch | N/A — no batch/schema changes |
| §2.6 state machine | Scenario uses real `CANDIDATE_STATES` / `NAV_CONFIG` gates — no new states |
| §3.3 imports | `integration_io` in utils; external modules import utils only — OK |
| §3.5 naming | `run_integration_tests.sh` parallels `run_component_tests.sh`; scenario file under `scenarios/` |

No plan conflicts requiring `conf-!!-NONE`.

## Review stub

| Field | Value |
|-------|-------|
| **Publish ref** | `origin/sub/AST-512/AST-711-integration-harness-first-api-scenario` |
| **Built tip** | `1252ff2` |
| **Stages** | 1 — `integration_io` + external guards (`5f73b60`); 2 — `run_integration_tests.sh` (`ec8f562`); 3 — CI workflow (`1252ff2`) |
| **Betty next** | Stage 4 — `tests/integration/` scenario + bible tier docs |
| **test-child manifest** | `./scripts/testing/run_integration_tests.sh` only (Betty `cec444b`) |

## Radia review (2026-06-16)

**Diff:** `origin/dev...origin/sub/AST-512/AST-711-integration-harness-first-api-scenario` @ `13f76cc`

### What's solid

| Area | Notes |
|------|-------|
| **Plan fidelity** | Stages 1–4 land as specced: `integration_io.py`, six external entry guards, standalone harness, CI workflow, Betty integration tree + bible tier. |
| **Layer contract** | Real SQLite + auth stub + minimal Flask (`system_bp` + `candidate_bp`); no API↔core mocks. Guards are no-ops outside `ASTRAL_INTEGRATION_MODE=1`. |
| **§3.3 / §5g** | External modules import `utils` only (`integration_io`); no cross-external LLM imports; playwright guard on `_launch_browser` covers all launch paths. |
| **§2.1 config** | Harness flags env-only in `integration_io.py`, not `config.py`. |
| **Scenario** | Nav assertion uses stable `Jobs` / `/jobs/in_review` gates tied to `LIVE_PROMPTS` vs `NEW` from real DB — matches plan Stage 4b. |
| **Isolation** | `run_component_tests.sh` unchanged vs `origin/dev`; integration harness green locally (3 passed). |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `docs/test-bible/integration/README.md` § AST-711 | Plan QA + this doc’s **test-child manifest** still require zero-arg `./scripts/testing/run_component_tests.sh` green on publish ref; `cec444b` narrows pass criterion to integration-only and documents unrelated roster red on `origin/dev`. Confirm Susan’s override is the closure bar for AST-711 vs updating plan/manifest to match. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Resolve manifest alignment (keep dual gate or formalize integration-only closure) | Susan / Chuckles |
| `resolve-child` — no product fix-now items | Ada |

## Resolution (2026-06-16)

**Radia review @ `13f76cc`:** No fix-now product items. Integration harness green (3 passed).

**Discuss closed:** Betty narrowed Tests Ready manifest to integration-only (`cec444b` → `13f76cc`) after Ada `[qa-handoff]` — roster component failures reproduce on `origin/dev`, not AST-711. Plan doc QA/manifest sections updated here to match bible + Betty handoff; integration-only is the AST-711 closure bar.

**Product tip:** `origin/sub/AST-512/AST-711-integration-harness-first-api-scenario` @ `e8c309d` (Radia doc) + this resolve doc commit.
