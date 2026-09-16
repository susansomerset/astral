# AST-1694 — Minimal listing-href on job GET

**Linear:** [AST-1694](https://linear.app/astralcareermatch/issue/AST-1694/minimal-listing-href-on-job-get-hyperlink-to-job-with-meteorite-http)  
**Parent:** [AST-1686](https://linear.app/astralcareermatch/issue/AST-1686/hyperlink-to-job-with-meteorite-http-link) — Hyperlink to job with meteorite http link  
**Publish ref:** `sub/AST-1686/AST-1694-minimal-listing-href-job-get`

DB reverse link lookup + `GET /api/jobs/<id>` resolved http(s) listing href (`job.job_link` when http(s), else related meteorite http `link`, else `null`). Does not own land/qualify writers (AST-1693) or React surfaces (AST-1695).

## UAT fitness

- **AC restored:** Parent AC4 — "`GET /api/jobs/<id>` includes a resolved listing href that is the http(s) `job.job_link` when set, else http(s) related `meteorite.link`, else `null`." Parent AC5 / this child AC5 — "`grep` of this epic’s diff does not add a second full `related_meteorite` provenance payload for AST-1685’s pane — only the minimal link/href lookup."
- **Correct outcome:** Job detail JSON always includes `listing_href` as an http(s) string or JSON `null`. When `job.job_link` is empty/non-http but a related meteorite row carries an http(s) `link`, that URL is the value so Apply/title UIs (AST-1695) can open the ATS page even on bot-blocked jobs.
- **Sibling check:** AST-1693 writes/preserves `job.job_link` on land/qualify — this ticket only reads; prefer that column first. AST-1695 consumes `listing_href` — do not edit frontend. AST-1691 (AST-1685) may add full `related_meteorite` + `get_meteorite_by_astral_job_id` — this ticket must **not** attach `related_meteorite` or project provenance fields; verified by Files Changed + Stage 2 (key `listing_href` only).
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Overwriting `job.job_link` in the GET response (or returning a non-http breadcrumb) hides the raw column and fails http(s)-only. Emitting AST-1685’s full `related_meteorite` payload here fails AC5. Skipping the meteorite fallback when `job.job_link` is empty fails AC4.

## Explicit scope gate

This ticket’s **Scope** names only:

- `src/data/database.py` — minimal `astral_job_id` → meteorite link/row read + header inventory
- `src/ui/api/api_jobs.py` — resolved listing href on detail

Technical: http(s)-only string or null; prefer job column then meteorite link. Stages below stay inside those two files and those change kinds.

**Field name (locked):** `listing_href` on the `GET /api/jobs/<id>` JSON body.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `get_meteorite_link_by_astral_job_id`; note helper on meteorite header inventory line | data |
| `src/ui/api/api_jobs.py` | Resolve and attach `listing_href` on `GET /api/jobs/<id>` detail | ui |

## Canon Scope (this ticket)

- `stat.logging.info.api` — **id + pattern read:** idempotent GETs that only return current state are **not** progress → **no** `logger.info` on `detail` for this attach.
- `stat.logging.debug` — **pattern read:** `logger.debug` at API logic joints (callee in/out for the link lookup); no `if debug` gate; **no** debug noise in `src/data/`.
- `stat.logging.error` — **pattern read:** on thrown lookup/route failures handled in the API, one `logger.exception` at the handler with live facts + next step; data raises, does not log.

## Stages

### Stage 1: Minimal reverse link read

**Done when:** `get_meteorite_link_by_astral_job_id(astral_job_id)` returns the meteorite `link` string when a matching row exists, else `None`. Blank/None job id returns `None` without querying. Header inventory documents the helper. No API changes yet.

1. In `src/data/database.py`, on the `meteorite` line of the module header table inventory, append that listing-href fallback reverse lookup is via `get_meteorite_link_by_astral_job_id(astral_job_id)` (AST-1694 — link column only; not AST-1685 provenance).

2. Immediately after `get_meteorite`, add:

```python
def get_meteorite_link_by_astral_job_id(astral_job_id: str) -> Optional[str]:
    """Return meteorite.link for astral_job_id, or None. Read-only; no create/update."""
```

   Implementation mirrors `get_meteorite`: `_run_with_retry` + `_get_connection` + `_ensure_meteorite_schema`. If `astral_job_id` is None or `str(astral_job_id).strip() == ""`, return `None` before opening a connection. Otherwise:

```sql
SELECT link FROM meteorite
WHERE astral_job_id = ?
ORDER BY id DESC
LIMIT 1
```

   with the stripped string as the bind param. Return the `link` cell as `str` when present and non-empty after strip; otherwise `None` (including when the row exists but `link` is NULL/blank). Do **not** filter http(s) in the data layer — the API owns the http(s)-only rule.

⚠️ **Decision:** Helper name is `get_meteorite_link_by_astral_job_id` (returns `Optional[str]`), not AST-1691’s planned `get_meteorite_by_astral_job_id` (full row for `related_meteorite`). Parent AC5 forbids a second full provenance payload in this epic; link-only keeps the contract minimal and avoids colliding with AST-1685 when both land on `dev`.

⚠️ **Decision:** `ORDER BY id DESC LIMIT 1` if multiple rows share an `astral_job_id` — same tie-break as AST-1691’s plan; newest id wins. Do **not** add a new index (not in Scope).

⚠️ **Decision:** No logging inside `database.py` (`stat.logging.debug` forbids data-layer debug noise; `stat.logging.error` — data raises, does not log).

### Stage 2: Resolve `listing_href` on job detail

**Done when:** `GET /api/jobs/<id>` JSON always includes key `listing_href`. Value is the http(s) `job.job_link` when that column starts with `http://` or `https://`; else the http(s) string from `get_meteorite_link_by_astral_job_id` when that link is http(s); else JSON `null`. Non-http breadcrumbs never appear. Lookup failures soft-fail to resolving from `job.job_link` only (or `null`) after one `logger.exception`. `related_meteorite` is **not** set by this ticket.

1. In `src/ui/api/api_jobs.py`, import `get_meteorite_link_by_astral_job_id` from `src.data.database` (add import; do not route through tracker for this read).

2. In the same module (module-level, near other private helpers), add:

```python
def _http_listing_url(raw) -> Optional[str]:
    """Return stripped http(s) URL, else None. Non-http breadcrumbs → None."""
    if raw is None:
        return None
    s = str(raw).strip()
    if s.startswith("http://") or s.startswith("https://"):
        return s
    return None
```

3. In `detail(astral_job_id)`, after the `agent_story` try/except block and **before** `return jsonify(job)`:

```python
listing = _http_listing_url(job.get("job_link"))
if listing is None:
    try:
        logger.debug(
            "Calling get_meteorite_link_by_astral_job_id: [astral_job_id=%s]",
            astral_job_id,
        )
        meta_link = get_meteorite_link_by_astral_job_id(astral_job_id)
        logger.debug(
            "Response from get_meteorite_link_by_astral_job_id: %s",
            meta_link,
        )
        listing = _http_listing_url(meta_link)
    except Exception as exc:
        logger.exception(
            "%s | api %s listing_href meteorite lookup failed\n  %s: %s\n  Continuing with listing_href from job.job_link only",
            job.get("candidate_id") or "-",
            f"/api/jobs/{astral_job_id}",
            type(exc).__name__,
            exc,
        )
        listing = None
job["listing_href"] = listing
```

   Prefer path: when `_http_listing_url(job.get("job_link"))` is non-None, **do not** call the meteorite helper (no unnecessary DB read).

⚠️ **Decision:** Always set key `listing_href` (string or `null`) so absence cannot mean “old client.” Do **not** mutate `job["job_link"]`.

⚠️ **Decision:** No `logger.info` on this GET — `stat.logging.info.api` excludes idempotent GETs that only return current state. Parent “log once at completing route” wording yields to the statute: debug for the lookup walk; `logger.exception` only when the handler catches a throw.

⚠️ **Decision:** Do **not** attach `related_meteorite`, content, classify_outcome, or other provenance fields (parent AC5 / this child AC5).

## Estimate

Confirm Chuckles estimate: 2 — agree

## AC → stage map

| AC (this child) | Stage |
|-----------------|-------|
| AC4 resolved `listing_href` http(s) / null prefer job then meteorite | Stage 1 + 2 |
| AC5 no full `related_meteorite` payload in this epic | Stage 1 name/return + Stage 2 (key only `listing_href`) |

Parent AC1–3 → AST-1693 (writers). Parent AC5–6 UI → AST-1695. Out of scope here.
