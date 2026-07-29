# AST-1042 — API create job under meteorite from raw HTML

**Linear:** [AST-1042](https://linear.app/astralcareermatch/issue/AST-1042/api-create-job-under-meteorite-from-raw-html-support-meteorite-jobs)
**Parent:** [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs) — Support meteorite jobs
**Publish ref:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`

Authenticated API that lazy-ensures the candidate’s meteorite company (AST-1041 `ensure_meteorite_company`), then creates a job under `meteorite-<candidate_id>` from raw HTML as the JD. The job lands in **JD_READY** with **latest_score 10.0** from `METEORITE_CONFIG` (synthetic joblist-qualifier stand-in) via a documented create carve-out — no new job state, no admin UI, no email ingest, no fetch_jd scrape.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | Add `create_meteorite_job` (ensure → insert JD_READY + score + HTML JD) | core |
| `src/ui/api/api_meteorite.py` | New blueprint: `POST …/meteorite/jobs` under `@require_auth` | ui |
| `src/ui/server.py` | Register `meteorite_bp` | ui |

## Stage 1: Core create carve-out (ensure + JD_READY insert)

**Done when:** Callers can `create_meteorite_job(candidate_id, html_body)` and get a persisted job under the meteorite short_name in `METEORITE_CONFIG["job_create_state"]` with `latest_score == METEORITE_CONFIG["job_create_latest_score"]` and HTML in `job_data` under the tracker JD key — without calling `transition_job_state`, without inventing a new `JOB_STATES` key, and without scraping.

1. In `src/core/meteorite.py`, update the module docstring to state that this module owns meteorite company ensure **and** API-facing job create from raw HTML (AST-1042). Still no email ingest and no admin UI.

2. Add imports needed for create (keep ensure imports; add only what create uses):

```python
import uuid
from datetime import datetime, timezone

from src.core.candidate import get_candidate
from src.data.database import get_company, get_job, save_company, save_job
from src.utils.config import METEORITE_CONFIG, TRACKER_CONFIG
```

(`get_logger` already present for ensure.)

3. Add public `create_meteorite_job` **above** any new helpers (public-first). Signature and contract:

```python
def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Lazy-ensure meteorite company, then insert a JD_READY job from raw HTML.

    Create carve-out (not transition_job_state): first write inserts directly into
    METEORITE_CONFIG["job_create_state"] the same way ingest_jobs inserts into NEW
    (JOB_STATES prior_states=None unrestricted entry). JD_READY's registered
    prior_states remain ["PASSED_JOBLIST"] for scrape/qualify hops — this path does
    not expand those priors and does not invent a new job state.

    Returns:
      {
        "astral_job_id": str,
        "company": str,           # meteorite-<candidate_id>
        "state": str,             # job_create_state
        "latest_score": float,    # job_create_latest_score
        "company_inserted": bool, # from ensure
        "job": dict,              # get_job row after writes
      }
    """
```

4. Concrete steps inside `create_meteorite_job`:

- Strip `candidate_id`; if empty → `ValueError("candidate_id is required")`.
- Require `html_body` to be a `str`; strip for emptiness check only — **persist the original `html_body` string as provided** (do not `parse_text` / cull / convert). If `not isinstance(html_body, str) or not html_body.strip()` → `ValueError("html_body is required")`.
- Load candidate: `cand = get_candidate(candidate_id)`; if missing → `ValueError(f"candidate not found: {candidate_id}")` (API maps to 404).
- `ensured = ensure_meteorite_company(candidate_id, debug=debug)`.
- `short_name = ensured["short_name"]` (must equal `METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)`).
- Resolve JD key: `jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]` (today `"job_description"` — do not hardcode the string in meteorite.py).
- `state = METEORITE_CONFIG["job_create_state"]`  # JD_READY
- `score = float(METEORITE_CONFIG["job_create_latest_score"])`  # 10.0
- `astral_job_id = str(uuid.uuid4())`
- `now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")`
- **Insert** via `save_job` (create carve-out — do **not** call `transition_job_state`):

```python
inserted = save_job(
    astral_job_id,
    company=short_name,
    state=state,
    job_title=None,
    job_link=None,
    company_job_id=None,
    job_data={jd_key: html_body},
    state_history=[{"to_state": state, "timestamp": now, "score": score}],
    state_changed_at=now,
    merge=False,
)
if not inserted:
    raise RuntimeError(f"meteorite job insert failed: {astral_job_id}")
```

- **Score column:** `database.save_job` INSERT path does not write `latest_score` today. Immediately follow with an update-only call:

```python
save_job(astral_job_id, latest_score=score)
```

⚠️ **Decision:** Two-step insert + `latest_score` update rather than changing `save_job` INSERT SQL for all callers. Same end state as a single insert that included the column; keeps AST-1042 scoped to meteorite create.

- `row = get_job(astral_job_id)`; if None → `RuntimeError`.
- Verify `row["state"] == state` and `row.get("latest_score") == score` (float compare OK); if not → `RuntimeError` with detail.
- Return the dict shape above (`company_inserted=ensured["inserted"]`, `job=row`).

5. Do **not** call `initialize_job`, `transition_job_state`, playwright / `get_job_data` coat-check, or invent `job_title` / `job_link` / `company_job_id`. Do **not** expand `JOB_STATES["JD_READY"]["prior_states"]`. Do **not** add a new job state.

⚠️ **Decision:** Create carve-out (direct insert into JD_READY) instead of expanding `prior_states` to `None` or adding a predecessor state — parent forbids a new job state; unrestricted JD_READY would legalize illegal scrape hops; insert-on-create mirrors `ingest_jobs` → NEW.

**Done when (recheck):** Calling create twice for the same candidate yields two jobs (no dedup by HTML); each has company `meteorite-<id>`, state JD_READY, latest_score 10.0, and `job_data[jd_key]` equal to the supplied HTML; ensure is idempotent across calls.

## Stage 2: Auth-gated HTTP create API

**Done when:** Authenticated clients can `POST` raw HTML + candidate id and receive the create payload; missing/invalid session → 401; validation / missing candidate / upstream failures map to 400 / 404 / 502; no React/admin UI files.

1. Create `src/ui/api/api_meteorite.py` with module docstring:

```
Meteorite job-create API (AST-1042 / Support meteorite jobs).

Thin Flask wrapper over src.core.meteorite.create_meteorite_job.
No admin UI; no email ingest; no Gmail I/O.
```

2. Blueprint + route:

```python
from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.meteorite import create_meteorite_job
from src.utils.logging import get_logger

logger = get_logger(__name__)

meteorite_bp = Blueprint("meteorite", __name__, url_prefix="/api")


@meteorite_bp.route("/candidates/<candidate_id>/meteorite/jobs", methods=["POST"])
@require_auth
def meteorite_create_job(candidate_id: str):
    ...
```

⚠️ **Decision:** Path under `/api/candidates/<candidate_id>/meteorite/jobs` (not `/api/admin/…`) — parent AC is authenticated API capability, not an admin tool; matches intake-style candidate-scoped routes. `@require_auth` (not `@require_admin`) matches “authenticated API create call.”

3. Handler body:

- Parse JSON: `data = request.get_json(silent=True) or {}`.
- `html_body = data.get("html_body")` — require key present as string (see core validation).
- Optional `debug = bool(data.get("debug", False))`.
- `try: payload = create_meteorite_job(candidate_id, html_body, debug=debug)`
- Map exceptions:
  - `ValueError` whose message starts with `"candidate not found"` → `404` `{"error": str(e)}`
  - Other `ValueError` → `400` `{"error": str(e)}`
  - Any other `Exception` → log `logger.warning("[api_meteorite] create failed candidate_id=%s: %s", candidate_id, e)` → `502` `{"error": str(e)}`
- Success → `201` with JSON:

```json
{
  "astral_job_id": "...",
  "company": "meteorite-<candidate_id>",
  "state": "JD_READY",
  "latest_score": 10.0,
  "company_inserted": true|false
}
```

Do **not** return the full `job` blob unless needed — keep the response small; omit nested `job` from the HTTP body (core still returns it for callers/tests).

4. In `src/ui/server.py`, after the existing `jobs_bp` registration block, register:

```python
from ui.api.api_meteorite import meteorite_bp  # noqa: E402
app.register_blueprint(meteorite_bp)
```

Follow neighboring `# noqa: E402` style.

5. Do **not** add React pages, `NAV_CONFIG` items, `DATA_SHAPES`, or Gmail/email ingest callers. Do **not** edit `tests/` / bible.

**Done when (recheck):** Bearer-authenticated POST creates the job; unauthenticated → 401; empty `html_body` → 400; unknown candidate → 404; no UI routes added.

## Out of scope (do not implement here)

- Meteorite company config / ensure / claim exclusion (AST-1041 — already on ftr).
- Email ingest calling create/ensure (later ingest epic / AST-1031 sibling).
- Admin UI to paste HTML or create meteorite jobs.
- Expanding `JOB_STATES["JD_READY"]["prior_states"]` or adding a new job state.
- fetch_jd / playwright scrape for these jobs.
- Deleting or transitioning `meteorite-*` when candidate leaves ACTIVE_SEARCH.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — extends `src/core/meteorite.py` with one create helper; adds one thin auth-gated blueprint + server registration; no config literals beyond existing `METEORITE_CONFIG` / `TRACKER_CONFIG` keys; no UI/external.

**Conf:** `high` — ensure + `METEORITE_CONFIG` job-create defaults already shipped on AST-1041; insert carve-out mirrors `ingest_jobs` → NEW; auth pattern matches other `/api/candidates/…` routes.

**Risk:** `Medium` — wrong carve-out (calling `transition_job_state` into JD_READY from empty state) would raise; forgetting `latest_score` update would leave NULL and score-floor claim would drop the job; mitigated by explicit two-step write + postcondition checks in core.

## Rules self-review

- **§2.1 / no-hardcoded-sets:** State + score from `METEORITE_CONFIG`; JD key from `TRACKER_CONFIG["job_data_keys"]`.
- **§2.6 / job-prior-states-enforced:** Create carve-out documented; `transition_job_state` priors for JD_READY unchanged; no new `JOB_STATES` key.
- **§2.6 / core-decides-transitions:** Core chooses JD_READY + score from config; data only persists.
- **pass-threshold-vs-score-floor:** Synthetic `10.0` is dispatch eligibility stand-in only — not grading `pass_threshold`.
- **§3.3 import-direction:** `api_meteorite` → core + utils + `ui.auth`; `meteorite.py` → data + utils + `get_candidate`; no ui→external/data.
- **require-auth-on-protected-endpoints:** `@require_auth` on the create route.
- **§1.3 public-then-helpers:** Public `create_meteorite_job` after ensure; no private helpers required unless DRY appears during build.
- **In-scope only:** No UI, no email, no JOB_STATES expansion, no tests/bible.
