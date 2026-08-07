# AST-1227 — Listing to meteorite ingest

**Linear:** [AST-1227](https://linear.app/astralcareermatch/issue/AST-1227/listing-to-meteorite-ingest-page-intake-server-side-page)
**Parent:** [AST-1168](https://linear.app/astralcareermatch/issue/AST-1168/page-intake-server-side-page-classification-and-single-listing-ingest) — page_intake — server-side page classification and single-listing ingest
**Publish ref:** `origin/sub/AST-1168/AST-1227-listing-to-meteorite-ingest`

When classification has already decided a page is a single recognized job listing, create (or dedupe) a meteorite job for that candidate through the existing `create_meteorite_job` path so Surfer listings land identically to email-sourced meteorites (`METEORITE_NEW`, JD in `job_data`, optional `job_link`). Owns the core create/dedupe entry and Style D found/recorded when `debug=True`. Does **not** own classification, the HTTP intake surface, Playwright, or the meteorite state ladder / evaluate chain.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/page_intake.py` | **New** module: `ingest_recognized_listing` — per-candidate link/id dedupe → `create_meteorite_job` + Style D | core |

No `src/ui/**`, no Flask route, no `gazer.py` / Playwright changes, no `JOB_STATES` / dispatcher / qualify edits, no `tests/` / bible (Betty after Code Complete). No new config block — reuse existing meteorite create defaults and per-candidate dedupe helpers already used by email ingest.

## Stage 1: Core ingest entry (`ingest_recognized_listing`)

**Done when:** Callers can pass `candidate_id` + `page_url` + JD body and get either a newly created meteorite job in `METEORITE_NEW` (same shape as email create) or a duplicate outcome with no second row; `debug=True` emits Style D found/recorded (or skipped-duplicate) index headers with working detail. No HTTP surface.

1. Create `src/core/page_intake.py` with module docstring stating: Surfer page_intake listing→meteorite ingest (AST-1227); classification and HTTP surface are siblings (AST-1226 / AST-1228); reuses `create_meteorite_job` and per-candidate dedupe helpers — does not scrape.

2. Imports (core→data and core→meteorite allowed; **do not** import `src.ui` or `src.external`):

```python
from typing import Any, Optional

from src.core.meteorite import create_meteorite_job
from src.data.database import (
    job_link_exists_for_candidate,
    text_matches_known_company_job_id_for_candidate,
)
from src.utils.logging import get_logger
```

3. Add public function:

```python
def ingest_recognized_listing(
    candidate_id: str,
    page_url: str,
    html_body: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Dedupe then create a meteorite job for a classified single listing.

    Caller is responsible for having classified the page as a single listing
    (AST-1226 / AST-1228). This function does not classify or fetch.

    Returns:
      {
        "outcome": "created" | "duplicate",
        "reason": None | "known_job_link" | "known_company_job_id",
        "matched_company_job_id": Optional[str],  # set when reason is known_company_job_id
        "page_url": str,
        # when outcome == "created", also the create_meteorite_job fields:
        "astral_job_id": str,
        "company": str,
        "state": str,
        "latest_score": float,
        "company_inserted": bool,
        "job": dict,
        # when outcome == "duplicate":
        # astral_job_id / company / state / latest_score / company_inserted / job are absent
      }
    """
```

4. Validation (raise `ValueError` — caller logs; no log in this function on the error path beyond optional debug, per `astral.standards.data-raises-caller-logs` for data and this core entry’s raise-on-bad-input pattern matching `create_meteorite_job`):

- Strip `candidate_id`; empty → `ValueError("candidate_id is required")`.
- Strip `page_url`; empty → `ValueError("page_url is required")`.
- `html_body` must be a non-empty stripped string → else `ValueError("html_body is required")` (same bar as `create_meteorite_job`).

⚠️ **Decision — `page_url` is required:** Surfer always has a page URL; exact `job_link` is the primary duplicate key for AC2. Do not invent a body-only create path here (email body mode without link stays on the gazer/inbox path).

⚠️ **Decision — parameter name `html_body`:** Matches `create_meteorite_job`. Content is the JD payload to persist under `TRACKER_CONFIG["job_data_keys"]["job_description"]`. Prefer the visible text AST-1226 derives (email link-sourced meteorites store Playwright visible text). Do **not** re-derive visible text in this module.

5. Logger setup: `log = get_logger(__name__); log.set_debug_flag(debug)`.

6. Dedupe order (mirror gazer email link path; **per-candidate only** — never global `job_link_exists` / global `text_matches_known_company_job_id`):

   a. If `job_link_exists_for_candidate(candidate_id, page_url)`:
      - If `debug`: `debug_index(func="page_intake.ingest_recognized_listing", index=1, total=1, identifier=page_url[:80], outcome="skipped-duplicate")` then `debug_detail("reason=known_job_link")`.
      - Return `{"outcome": "duplicate", "reason": "known_job_link", "matched_company_job_id": None, "page_url": page_url}`.

   b. Build `haystack = f"{page_url}\n{html_body}"`. If `text_matches_known_company_job_id_for_candidate(candidate_id, haystack)` returns a match `matched`:
      - If `debug`: same index header `outcome="skipped-duplicate"` with `debug_detail(f"reason=known_company_job_id matched={matched}")`.
      - Return `{"outcome": "duplicate", "reason": "known_company_job_id", "matched_company_job_id": matched, "page_url": page_url}`.

⚠️ **Decision — both dedupe gates, candidate-scoped:** Parent AC2 + email parity. Exact URL covers re-posts before Ruth fills `company_job_id`; inverted id match covers re-posts after qualify. Same URL for two candidates may create two jobs (same as `gaze_email`). Do **not** add URL normalization / fuzzy match.

7. Found / create / recorded:

   - If `debug`: `debug_index(..., outcome="found")` then `debug_detail(f"jd_len={len(html_body)} candidate_id={candidate_id}")`.
   - Call `create_meteorite_job(candidate_id, html_body, job_link=page_url, debug=debug)`.
   - If `debug`: `debug_index(..., outcome="recorded")` then `debug_detail(f"astral_job_id={result['astral_job_id']}")`.
   - Return dict merging `{"outcome": "created", "reason": None, "matched_company_job_id": None, "page_url": page_url}` with the full `create_meteorite_job` result keys (`astral_job_id`, `company`, `state`, `latest_score`, `company_inserted`, `job`).

⚠️ **Decision — do not change `create_meteorite_job`:** It already lands `METEORITE_NEW` with synthetic score and optional `job_link` / `company_job_id=None`. Surfer must not invent a parallel insert or a new job state. Style D for this ticket lives in the wrapper (gazer pattern), not inside `create_meteorite_job`.

⚠️ **Decision — no min_jd_chars gate here:** Classification already recognized the page as a listing. Empty body still fails validation via step 4 / `create_meteorite_job`. Re-applying `METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"]` would couple Surfer ingest to email scrape thresholds without a Surfer config owner on this ticket.

8. Do **not** add Flask routes, blueprints, or imports from `src.ui`. AST-1228 wires this function after classification.

9. Compile check: `python3 -m py_compile src/core/page_intake.py`.

**Done when (recheck):**

- First call with a fresh `page_url` returns `outcome="created"`, `state` equal to `METEORITE_CONFIG["job_create_state"]` (`METEORITE_NEW`), and `job_link` on the row equals `page_url`.
- Second call with the same `candidate_id` + `page_url` returns `outcome="duplicate"`, `reason="known_job_link"`, and does not insert another job.
- With `debug=True`, logs show found→recorded on create and skipped-duplicate on dedupe; with `debug=False`, no Style D lines.

## Self-Assessment

**Scope:** `Single-Component` — one new core module wrapping existing meteorite create + existing per-candidate dedupe helpers; no UI, config, or state-machine edits.

**Conf:** `high` — exact create/dedupe/Style D pattern already shipped in `gazer.ingest_meteorite_jobs_from_email_html` / `gaze_email`; this ticket is the Surfer-facing entry without Playwright.

**Risk:** `Medium` — incorrect dedupe would either spawn duplicate meteorites for the same candidate or (if someone switched to global helpers) block cross-candidate legitimate creates; create itself is the established carve-out into `METEORITE_NEW`.

## Code rules check

- **§1.3 DRY:** Reuses `create_meteorite_job`, `job_link_exists_for_candidate`, `text_matches_known_company_job_id_for_candidate` — no second insert path.
- **§1.5.1 / debug-contract-gated:** Style D only when `debug=True`; index header + detail; no new `[DEBUG] info` lines.
- **§2.1 config:** No new literals for states/scores — create still reads `METEORITE_CONFIG`. No new config block on this ticket (classification owns PAGE_INTAKE copy/thresholds).
- **§2.6 / core-decides-transitions / job-prior-states:** Create carve-out unchanged (`prior_states=None` entry into `METEORITE_NEW`); no `transition_job_state` calls; ladder untouched.
- **§3.3 imports:** `page_intake` core → `meteorite` + `data` + `utils` only; no `ui` / `external`.
- **data-raises-caller-logs:** Raises on bad input; data helpers stay quiet; caller (AST-1228) owns HTTP logging.
