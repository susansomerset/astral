# AST-1061 — Gazer email → meteorite jobs (Playwright + dedupe)

**Linear:** [AST-1061](https://linear.app/astralcareermatch/issue/AST-1061/gazer-email-meteorite-jobs-playwright-dedupe-qualify-meteorite)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`

Owns **gazer reads email** for meteorite ingest: classify stripped email HTML as JD body / recruiter-forward body / single job link / link list; Playwright `get_visible_text` for each link **before** create; skip create when a known external `company_job_id` (or exact `job_link`) already exists; insert survivors via `create_meteorite_job` into **METEORITE_NEW** with JD text and no Ruth metadata. Wire Manage Email Create through this path. Does **not** own Ruth `qualify_meteorite` apply (AST-1062) or qualify config/dispatch (AST-1060 — already on tip).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_EMAIL_INGEST_CONFIG` (link filters, concurrency, min JD length) | utils |
| `src/data/database.py` | Add global inverted `company_job_id` match + exact `job_link` existence helpers | data |
| `src/core/meteorite.py` | Optional `job_link=` on `create_meteorite_job` (still `company_job_id=None`) | core |
| `src/core/gazer.py` | Email shape classify → Playwright → dedupe → create orchestration + Style D | core |
| `src/core/inbox.py` | After strip, call gazer ingest instead of bare `create_meteorite_job`; multi-result return | core |
| `src/ui/api/api_inbox.py` | Create-job JSON shape for created/skipped lists (keep 201 when ≥1 created; 200 when all skipped) | ui |
| `src/ui/frontend/src/pages/AdminManageEmail.tsx` | Toast for N created / M skipped | ui |

No `consult.py` / dispatcher / `agent_task.json` / GDL / `qualify_*` TASK_CONFIG. No `tests/` / bible (Betty after Code Complete). No new Playwright primitives — call existing `get_visible_text`.

## Stage 1: Config + data-layer dedupe helpers

**Done when:** `METEORITE_EMAIL_INGEST_CONFIG` imports from `src.utils.config`; `database` exposes the two helpers below; no core/UI changes yet.

1. In `src/utils/config.py`, immediately after `METEORITE_CONFIG` (or `INBOX_CREATE_JOB_CONFIG` if adjacent is clearer — **prefer after `METEORITE_CONFIG`**), add:

```python
# AST-1061: gazer email → meteorite ingest (link detect, Playwright, external-id dedupe).
METEORITE_EMAIL_INGEST_CONFIG = {
    # Only http(s) hrefs are job-link candidates (mailto:/tel: excluded by scheme).
    "link_schemes": ("http", "https"),
    # Lowercased path/host fragments that disqualify an href (unsubscribe, tracking, etc.).
    "link_exclude_substrings": (
        "unsubscribe",
        "mailto:",
        "list-manage.com",
        "/preferences",
        "/email-settings",
    ),
    # Max concurrent Playwright fetches for a link list (same idea as gazer JD scrape caps).
    "playwright_concurrency": 3,
    # Skip create when visible/body text length is below this after strip/fetch.
    "min_jd_chars": 40,
}
```

If the top-of-file config inventory lists named `*_CONFIG` blocks, add a one-line `METEORITE_EMAIL_INGEST_CONFIG` entry next to meteorite / inbox bullets.

⚠️ **Decision — config owns link filters and thresholds:** No inline unsubscribe lists or magic length in gazer (§2.1 / config-source-of-truth).

2. In `src/data/database.py`, near `raw_job_listing_is_duplicate`, add:

```python
def text_matches_known_company_job_id(text: str) -> Optional[str]:
    """Global inverted match (AST-80 shape, no company filter).

    Returns the matched company_job_id when any non-empty company_job_id
    appears as a substring of text; else None.
    """
```

SQL (same LIKE pattern as `raw_job_listing_is_duplicate`, drop `company = ?`):

```sql
SELECT company_job_id FROM job
 WHERE company_job_id IS NOT NULL AND TRIM(company_job_id) != ''
   AND ? LIKE '%' || company_job_id || '%'
 LIMIT 1
```

Empty/`None` `text` → return `None` without querying.

3. In the same module, add:

```python
def job_link_exists(job_link: str) -> bool:
    """True when any job row has this exact job_link (non-empty)."""
```

SQL: `SELECT 1 FROM job WHERE job_link = ? AND job_link IS NOT NULL AND TRIM(job_link) != '' LIMIT 1`.

⚠️ **Decision — global id match + exact link match:** Meteorite creates today leave `company_job_id=None`, so company-scoped AST-80 alone cannot skip a second email for the same ATS URL. Exact `job_link` covers re-ingest of the same URL before Ruth fills the UUID; global inverted match covers ids already stored on any company (including post-qualify meteorite rows). Do **not** invent fuzzy URL normalization in this ticket.

**Done when (recheck):** `from src.utils.config import METEORITE_EMAIL_INGEST_CONFIG` works; helpers importable; `python3 -m py_compile src/utils/config.py src/data/database.py` succeeds.

## Stage 2: `create_meteorite_job` optional `job_link`

**Done when:** Callers can pass `job_link=`; omitted behavior matches today (`job_link=None`, `company_job_id=None`, state **METEORITE_NEW**, JD in `job_data`); no gazer/inbox changes yet.

1. In `src/core/meteorite.py`, extend signature:

```python
def create_meteorite_job(
    candidate_id: str,
    html_body: str,
    *,
    job_link: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
```

2. Pass `job_link=(job_link.strip() if job_link and str(job_link).strip() else None)` into `save_job`. Keep `company_job_id=None` always on this path (Ruth / AST-1062 owns external UUID persist).

3. Update the module docstring one line: optional `job_link` for link-sourced ingest (AST-1061); still no Ruth metadata.

⚠️ **Decision — do not set `company_job_id` here:** Extracting ATS UUIDs from URLs is vendor-specific and belongs with qualify enrichment. Link-based dedupe uses `job_link_exists` + global inverted match on URL/visible text instead.

**Done when (recheck):** Existing inbox/API create without `job_link` still inserts **METEORITE_NEW**; with `job_link="https://example.com/j/1"` the row’s `job_link` column equals that string.

## Stage 3: Gazer ingest orchestration (new pattern)

**Done when:** Given `candidate_id` + stripped email HTML, gazer returns created/skipped summaries; link shapes Playwright before create; known id/link skips insert; body shapes create without Playwright; Style D only when `debug=True`.

1. In `src/core/gazer.py`, update the module docstring to note AST-1061 meteorite email ingest (gazer-reads-email). Keep existing scrape/listing functions unchanged.

2. Add private helpers (below existing public batch entry points is fine; keep public ingest function above them if the file’s public-first convention requires it — **match existing gazer style**: public async entry near other batch publics, privates nearby):

```python
def _meteorite_email_candidate_links(html: str) -> List[str]:
    """Ordered unique http(s) hrefs from html, minus METEORITE_EMAIL_INGEST_CONFIG excludes."""

def _meteorite_email_body_text(html: str) -> str:
    """Plain visible-ish text from stripped email HTML for body/forward shapes (bs4 get_text)."""

async def _meteorite_fetch_link_visible_text(
    url: str, *, debug: bool = False
) -> Tuple[str, str]:
    """Return (visible_text, final_url) via get_visible_text(..., return_final_url=True)."""
```

Link extraction: lazy-import `bs4.BeautifulSoup` (same B1 pattern as inbox strip). Walk `a[href]`; keep hrefs whose scheme (via `urllib.parse.urlparse`) is in `link_schemes`; drop when any `link_exclude_substrings` appears in the lowercased href; preserve first-seen order; de-dupe exact href strings.

3. Add the public async entry:

```python
async def ingest_meteorite_jobs_from_email_html(
    candidate_id: str,
    html: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    """Classify email HTML → optional Playwright → dedupe → create_meteorite_job.

    Returns:
      {
        "astral_candidate_id": str,
        "mode": "links" | "body",
        "created": [ create_meteorite_job result dicts ... ],
        "skipped": [ {"reason": str, "url": Optional[str], "matched_company_job_id": Optional[str]} ... ],
      }
    """
```

Also add a thin sync wrapper for inbox (Flask is sync):

```python
def ingest_meteorite_jobs_from_email_html_sync(
    candidate_id: str,
    html: str,
    *,
    debug: bool = False,
) -> dict[str, Any]:
    return asyncio.run(
        ingest_meteorite_jobs_from_email_html(candidate_id, html, debug=debug)
    )
```

Import `asyncio` at module top if not already present.

4. **Classify:**
   - `links = _meteorite_email_candidate_links(html)`
   - If `links`: `mode = "links"`
   - Else: `mode = "body"` (covers JD-body and recruiter-forward — both are email text without qualifying job links)

⚠️ **Decision — no separate NLP “forward” detector:** AC names recruiter forward as a shape; after AST-1049 strip/subject wrap, forward bodies are still body text. Link presence is the only branch that requires Playwright. Do not call Anthropic here.

5. **Links path:**
   - Cap concurrency with `asyncio.Semaphore(METEORITE_EMAIL_INGEST_CONFIG["playwright_concurrency"])`.
   - For each URL (index `i` of `n`):
     - `text, final_url = await _meteorite_fetch_link_visible_text(url, debug=debug)` inside the semaphore.
     - On Playwright exception: append `skipped` with `reason="playwright_error"` and `url`; continue (do not abort the whole batch). Log a warning via `get_logger` (not Style D).
     - Build `haystack = f"{final_url or url}\n{text}"`.
     - If `job_link_exists(final_url or url)`: skip `reason="known_job_link"`.
     - Else if `(matched := text_matches_known_company_job_id(haystack))`: skip `reason="known_company_job_id"`, include `matched_company_job_id=matched`.
     - Else if `len(text.strip()) < min_jd_chars`: skip `reason="jd_too_short"`.
     - Else: `create_meteorite_job(candidate_id, text, job_link=(final_url or url), debug=debug)` and append to `created`.
     - Style D when `debug=True`: `debug_index(func="gazer.meteorite_email_ingest", index=i, total=n, identifier=(final_url or url)[:80], outcome="found"|"skipped-duplicate"|"skipped-short"|"skipped-error"|"recorded")` plus `debug_detail` lines for reason / astral_job_id / matched id as applicable.

6. **Body path:**
   - `text = _meteorite_email_body_text(html)` (if empty, fall back to raw `html` stripped of tags only if get_text is empty — prefer get_text; if still empty raise `ValueError("email body is empty")`).
   - Dedupe on `text` only via `text_matches_known_company_job_id` (no `job_link`).
   - If matched → `skipped` with `reason="known_company_job_id"`; `created=[]`.
   - Elif `len(text.strip()) < min_jd_chars` → skip `jd_too_short`.
   - Else → one `create_meteorite_job(candidate_id, html if html.strip() else text, job_link=None, debug=debug)`.
     - Prefer storing the **stripped HTML** as JD when non-empty (preserves AST-1049 subject wrapper); use plain `text` only when HTML is empty.

⚠️ **Decision — body create keeps HTML JD:** Matches AST-1049 create payload so qualify still sees subject+body structure; link path stores Playwright visible text (plain) because that is the fetched page content.

7. Do **not** change `process_gazer_batch`, `fetch_jd_batch`, listing ingest, or company scrape paths beyond adding the new functions/imports.

**Done when (recheck):** Unit-level manual calls (or a short spike under `debug/spikes/` only — not committed) show: body→one **METEORITE_NEW**; one link→Playwright then create with `job_link` set; second Create with same link→skipped `known_job_link`; text containing an existing `company_job_id`→skipped; `debug=False` emits no new `debug_index`/`debug_detail` from this path.

## Stage 4: Inbox + API + Manage Email Create UI

**Done when:** Manage Email Create runs gazer ingest after strip; API returns multi-result JSON; toast reports created/skipped counts; unmatched candidate / empty strip still 400.

1. In `src/core/inbox.py` `create_meteorite_job_from_inbox_message`:
   - Keep fetch / From→candidate / `strip_extract_email_html` / empty-strip `ValueError` / Style D steps 1–3 as today.
   - Replace the direct `create_meteorite_job(...)` call with:

```python
from src.core.gazer import ingest_meteorite_jobs_from_email_html_sync

ingest = ingest_meteorite_jobs_from_email_html_sync(cid, html, debug=debug)
```

   - Style D step 4: outcome `"recorded"` when `len(ingest["created"]) > 0`, else `"skipped"`; detail `created=N skipped=M mode=...`.
   - Return shape:

```python
{
  "astral_candidate_id": cid,
  "mode": ingest["mode"],
  "created": ingest["created"],
  "skipped": ingest["skipped"],
  # Back-compat for single-create callers/tests:
  "astral_job_id": ingest["created"][0]["astral_job_id"] if ingest["created"] else None,
  "company": ingest["created"][0]["company"] if ingest["created"] else METEORITE_CONFIG["short_name_template"].format(candidate_id=cid),
  "state": ingest["created"][0]["state"] if ingest["created"] else None,
  "latest_score": ingest["created"][0]["latest_score"] if ingest["created"] else None,
  "company_inserted": any(c.get("company_inserted") for c in ingest["created"]),
}
```

   - If `created` is empty and `skipped` is empty: raise `ValueError("no meteorite jobs created")`.
   - If `created` is empty and `skipped` is non-empty: **do not raise** — return the dict (API maps to 200).

2. In `src/ui/api/api_inbox.py` `inbox_create_job_from_message`:
   - Docstring note AST-1061 multi-create.
   - On success:
     - If `result["created"]`: status **201**, JSON:

```python
{
  "astral_candidate_id": result["astral_candidate_id"],
  "mode": result["mode"],
  "created": [
    {
      "astral_job_id": c["astral_job_id"],
      "company": c["company"],
      "state": c["state"],
      "latest_score": c["latest_score"],
      "company_inserted": c["company_inserted"],
    }
    for c in result["created"]
  ],
  "skipped": result["skipped"],
  # keep top-level astral_job_id for older UI:
  "astral_job_id": result["astral_job_id"],
  "company": result["company"],
  "state": result["state"],
  "latest_score": result["latest_score"],
  "company_inserted": result["company_inserted"],
}
```

     - If only skips: status **200**, same JSON with `created: []`.

3. In `AdminManageEmail.tsx` `onCreateClick` success branch:
   - Prefer `created` array length when present; toast e.g. `Created N job(s)` and if `skipped.length` append `; skipped M`.
   - If `created` empty and `skipped` non-empty: success-variant toast `Skipped M (already known or empty)` (not error).
   - Keep error path for non-OK responses.

4. Smoke (manual / existing component tests only if already covering Create — do not add Betty bible here): Create still works for body-only email; non-meteorite scrape/GDL untouched (no code edits there — AC4 is “do not change”).

**Done when (recheck):** `python3 -m py_compile` on touched Python files; frontend typechecks if the repo’s usual `npm` lint script is used for TS edits; Create toast shows multi counts; all-skipped returns 200 not 502.

## Out of scope (do not implement here)

- Ruth `qualify_meteorite` batch apply / persist UUID/title/link/JD (AST-1062).
- Qualify states / TASK_CONFIG / dispatch rows (AST-1060).
- Changing non-meteorite `process_gazer_batch` / `qualify_job_listings` / GDL priors.
- Auto-polling unread Gmail without Manage Email Create (no new dispatcher task).
- Vendor-specific URL→UUID parsers writing `company_job_id` on create.
- `tests/` / `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new gazer email-ingest path plus data dedupe helpers, meteorite `job_link` kwarg, and inbox/API/UI Create multi-result wiring; layers utils/data/core/ui.

**Conf:** `Medium` — Playwright + `create_meteorite_job` reuse is clear; shape split is link-vs-body (no NLP); residual uncertainty is how noisy global inverted match is on short numeric ids (mitigated by existing id lengths on real ATS rows + exact `job_link` gate).

**Risk:** `Medium` — false-positive global id substring match could skip a legitimate create; Playwright failures skip that link rather than failing the whole Create; non-meteorite gazer paths are untouched.

## Rules self-review

- **§2.1 / config-source-of-truth:** Link schemes, excludes, concurrency, min JD length live in `METEORITE_EMAIL_INGEST_CONFIG` only.
- **§3.3 / core-vs-external:** Gazer (core) calls `get_visible_text` (external) and `database.*` / `create_meteorite_job`; no Playwright or Gmail imports in UI; inbox stays orchestration.
- **§ debug-contract-gated:** Style D only when `debug=True` on gazer + inbox paths; no new contract lines from data layer.
- **§1.3 DRY:** Reuse `create_meteorite_job`, `get_visible_text`, AST-80 LIKE shape (global variant); do not fork a second meteorite insert.
- **In-scope only:** No qualify apply, no GDL edits, no tests/bible.
