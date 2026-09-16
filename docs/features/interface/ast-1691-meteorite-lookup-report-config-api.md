# AST-1691 — Meteorite lookup + report config/API

**Linear:** [AST-1691](https://linear.app/astralcareermatch/issue/AST-1691/meteorite-lookup-report-config-api-view-related-meteorite-record-data)
**Parent:** [AST-1685](https://linear.app/astralcareermatch/issue/AST-1685/view-related-meteorite-record-data-on-recommended-job-modal) — View related meteorite record data on recommended job modal
**Publish ref:** `sub/AST-1685/AST-1691-meteorite-lookup-report-config-api`

Add an `astral_job_id` → meteorite reverse-link read helper, register **Meteorite** on the Recommended report top-tab list and section manifest, and attach a flat `related_meteorite` object (or `null`) on `GET /api/jobs/<id>`. Retention skip is sibling AST-1690; React pane is sibling AST-1692.

## UAT fitness

- **AC restored:** Parent AC2 — "`GET /api/jobs/<id>` JSON includes `related_meteorite` with at least `id`, `created_at`, `updated_at`, `state_changed_at`, `link`, `classify_outcome`, `content`, `state`, `source_kind`, `source_id` when the reverse link hits; otherwise `null`." Parent AC6 — "`grep` / manifest: Meteorite is on `JOBS_RECOMMENDED_REPORT_TOP_TABS` and section list comes from config/manifest, not a TSX-only tab array."
- **Correct outcome:** Job detail JSON always has `related_meteorite` (object or `null`); when a staging row’s `astral_job_id` matches the job, operators (and sibling AST-1692) receive the provenance fields needed for a Meteorite top tab driven by config/`report_meteorite_sections`, not a hardcoded React tab list.
- **Sibling check:** AST-1690 (retention) must leave job-linked LANDED rows readable — this ticket only reads; do not change purge. AST-1692 (React pane) consumes `related_meteorite` + `report_top_tabs` + `report_meteorite_sections` — do not edit frontend files here. Verified by Scope Boundaries and Files Changed (no `meteorite.py`, no `src/ui/frontend/**`).
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hardcoding a Meteorite tab label/order only in React (or inventing section ids in TSX) fails AC6. Returning the full meteorite row unprojected (or omitting `related_meteorite` when null) fails AC2’s contract. Snapshotting meteorite fields onto `job_data` is out of epic scope.

## Explicit scope gate

This ticket’s **Scope** names only: `src/data/database.py` (read helper + header inventory); `src/utils/config.py` (Meteorite top tab + section defs); `src/ui/api/api_system.py` (manifest sections); `src/ui/api/api_jobs.py` (`related_meteorite` on detail). Stages below stay inside those four files and those change kinds.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `get_meteorite_by_astral_job_id`; note helper on meteorite header inventory line | data |
| `src/utils/config.py` | Append Meteorite to `JOBS_RECOMMENDED_REPORT_TOP_TABS`; add `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS` | utils |
| `src/ui/api/api_system.py` | Attach `jobs.recommended.report_meteorite_sections` on `GET /api/state_ui_manifest` | ui |
| `src/ui/api/api_jobs.py` | Attach projected `related_meteorite` on `GET /api/jobs/<id>` | ui |

## Canon Scope (this ticket)

- `stat.logging.info.api` — **id + pattern read:** idempotent GETs that only return current state are **not** progress → **no** `logger.info` on `detail` / `state_ui_manifest` for this attach.
- `stat.logging.debug` — **pattern read:** `logger.debug` at API logic joints (callee in/out for the lookup); no `if debug` gate; **no** debug noise in `src/data/`.
- `stat.logging.error` — **pattern read:** on thrown lookup/route failures handled in the API, one `logger.exception` at the handler with live facts + next step; data raises, does not log.

## Stages

### Stage 1: Reverse-link read helper

**Done when:** `get_meteorite_by_astral_job_id(astral_job_id)` returns one meteorite row dict when a matching `astral_job_id` exists, else `None`. Blank/None job id returns `None` without querying. Header inventory documents the helper. No config/API changes yet.

1. In `src/data/database.py`, on the `meteorite` line of the module header table inventory, append that reverse lookup is via `get_meteorite_by_astral_job_id(astral_job_id)`.
2. Immediately after `get_meteorite`, add:

```python
def get_meteorite_by_astral_job_id(astral_job_id: str) -> Optional[Dict[str, Any]]:
    """Return one meteorite row for astral_job_id, or None."""
```

   Implementation mirrors `get_meteorite`: `_run_with_retry` + `_get_connection` + `_ensure_meteorite_schema` + `_meteorite_row_to_dict`. If `astral_job_id` is None or `str(astral_job_id).strip() == ""`, return `None` before opening a connection. Otherwise:

```sql
SELECT * FROM meteorite
WHERE astral_job_id = ?
ORDER BY id DESC
LIMIT 1
```

   with the stripped string as the bind param.

⚠️ **Decision:** `ORDER BY id DESC LIMIT 1` if multiple rows share an `astral_job_id` — land normally writes one link; newest id wins for the Recommended pane. Do **not** add a new index in this ticket (not in Scope).

⚠️ **Decision:** No logging inside `database.py` (`stat.logging.debug` forbids data-layer debug noise; `stat.logging.error` — data raises, does not log).

### Stage 2: Top tab + Meteorite section defs in config

**Done when:** `JOBS_RECOMMENDED_REPORT_TOP_TABS` ends with Discussion then **Meteorite**; a public `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS` list defines the four ordered pane sections. Manifest/API not wired yet.

1. In `src/utils/config.py`, immediately after the Discussion entry in `JOBS_RECOMMENDED_REPORT_TOP_TABS`, append:

```python
{"tab_id": "meteorite", "nav_label": "Meteorite"},
```

   Update the comment above the list to note AST-1691 (Meteorite after Discussion).

2. Immediately after `JOBS_RECOMMENDED_REPORT_SUMMARY_SECTIONS` (same recommended-report block), add:

```python
# AST-1691: Recommended report Meteorite pane sections (config → manifest; React must not invent order).
JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS = [
    {"section_id": "meteorite_timestamps", "nav_label": "Timestamps", "default_expanded": True},
    {"section_id": "meteorite_link", "nav_label": "Link", "default_expanded": True},
    {"section_id": "meteorite_ai", "nav_label": "AI Content", "default_expanded": True},
    {
        "section_id": "meteorite_provenance",
        "nav_label": "Provenance",
        "default_expanded": False,
    },
]
```

⚠️ **Decision:** Four sections map parent Functional scope groups (timestamps / link / AI `classify_outcome`+`content` / provenance `id`·`state`·`source_kind`·`source_id`·`error`). Do **not** reuse `JOBS_RECOMMENDED_METEORITE_SECTION` (list-page Meteorites partition by company prefix) — different surface.

⚠️ **Decision:** Do **not** add `report_meteorite_sections` inside `build_state_ui_manifest()` — Stage 3 attaches it in `api_system.py` (ticket Scope / peer to AST-1550 Discussion attach location). Top tab still flows via existing `report_top_tabs: list(JOBS_RECOMMENDED_REPORT_TOP_TABS)`.

### Stage 3: Manifest attach

**Done when:** `GET /api/state_ui_manifest` → `jobs.recommended.report_meteorite_sections` equals `list(JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS)` (same four `{section_id, nav_label, default_expanded}` rows). `report_top_tabs` already includes Meteorite from Stage 2.

1. In `src/ui/api/api_system.py`, import `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS` from `src.utils.config` (alongside existing config imports).
2. In `state_ui_manifest()`, after the Discussion soft-fail block and before `return jsonify(manifest)`, attach:

```python
manifest.setdefault("jobs", {}).setdefault("recommended", {})[
    "report_meteorite_sections"
] = list(JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS)
```

   No try/except required — pure config copy (unlike Discussion’s live hop walk).

### Stage 4: `related_meteorite` on job detail

**Done when:** `GET /api/jobs/<id>` JSON always includes key `related_meteorite`. When `get_meteorite_by_astral_job_id` returns a row, value is a flat object with at least the AC2 fields (plus `estelle_notified_at` and `error`, null-ok). When no row (or blank lookup), value is JSON `null`. Lookup failures soft-fail to `null` after one `logger.exception`.

1. In `src/ui/api/api_jobs.py`, import `get_meteorite_by_astral_job_id` from `src.data.database` (add import; do not route through tracker for this read).
2. In `detail(astral_job_id)`, after the `agent_story` try/except block and **before** `return jsonify(job)`:

```python
try:
    logger.debug(
        "Calling get_meteorite_by_astral_job_id: [astral_job_id=%s]",
        astral_job_id,
    )
    row = get_meteorite_by_astral_job_id(astral_job_id)
    logger.debug(
        "Response from get_meteorite_by_astral_job_id: %s",
        None if row is None else {"id": row.get("id"), "state": row.get("state")},
    )
    if row is None:
        job["related_meteorite"] = None
    else:
        job["related_meteorite"] = {
            "id": row.get("id"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
            "state_changed_at": row.get("state_changed_at"),
            "estelle_notified_at": row.get("estelle_notified_at"),
            "link": row.get("link"),
            "classify_outcome": row.get("classify_outcome"),
            "content": row.get("content"),
            "state": row.get("state"),
            "source_kind": row.get("source_kind"),
            "source_id": row.get("source_id"),
            "error": row.get("error"),
        }
except Exception as exc:
    logger.exception(
        "%s | api %s related_meteorite lookup failed\n  %s: %s\n  Returning related_meteorite=null",
        job.get("candidate_id") or "-",
        f"/api/jobs/{astral_job_id}",
        type(exc).__name__,
        exc,
    )
    job["related_meteorite"] = None
```

⚠️ **Decision:** Always set the key (object or `null`) so absence cannot mean “old client.” Project a flat field set — do not nest the raw row or dump claim/batch columns.

⚠️ **Decision:** No `logger.info` on this GET — `stat.logging.info.api` excludes idempotent GETs that only return current state. Parent “log once at completing route” wording yields to the statute: debug for the lookup walk; `logger.exception` only when the handler catches a throw.

## Estimate

Confirm Chuckles estimate: 3 — agree

## AC → stage map

| AC (this child) | Stage |
|-----------------|-------|
| AC2 `related_meteorite` object/null | Stage 1 + 4 |
| AC3 / Parent AC6 Meteorite on top tabs + config/manifest sections | Stage 2 + 3 |

Parent AC1/3–5/7–9 → siblings AST-1690 / AST-1692 (out of scope).

## Joan validate

[plan-rubric]
**Ticket:** AST-1691
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1685/AST-1691-meteorite-lookup-report-config-api` @ `f8b6f15efd9a968f4f7db5491f9100a01c2eb690`

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.info.api | A | | |
| stat.logging.debug | C | 2 | Stage 4 `Response from get_meteorite_by_astral_job_id` logs only `{id, state}` — statute wants full callee response, no truncation |
| stat.logging.error | A | | |

### Traceability

Child AC **2** (`related_meteorite` object or `null` on `GET /api/jobs/<id>`) → Stages **1+4**; child AC **3** (Meteorite on `JOBS_RECOMMENDED_REPORT_TOP_TABS` + config/manifest sections, parent AC6) → Stages **2+3**. Parent AC **1, 3–5, 7–9** → siblings AST-1690 / AST-1692 (plan marks N/A). No orphan stages; no unmapped child AC.

### Findings

#### discuss

- **Location:** Stage 4 — `api_jobs.py` `detail()` debug pair around `get_meteorite_by_astral_job_id`
- **Finding:** `Response from get_meteorite_by_astral_job_id` is projected to `{"id", "state"}` only. `stat.logging.debug` Resolution §3 and Don't examples require the full response string without truncation (relevant when `content` is large).
- **Recommendation:** Log `row` (or `str(row)`) on the response line, or document an explicit Resolution path if redaction is intentional. Effort **2** — one debug call edit.

#### acceptable

- **Location:** Stage 4 — no `logger.info` on job detail GET
- **Finding:** Parent Technical scope wording (“log once at completing route”) reads against `stat.logging.info.api`, but the plan correctly yields to the statute: idempotent GET returning current state is not progress.
- **Recommendation:** None — plan’s Canon Scope call-out and Stage 4 decision note are sufficient.

- **Location:** Scope / Files Changed
- **Finding:** `GET /api/state_ui_manifest` gains `report_meteorite_sections` while `JOBS_RECOMMENDED_REPORT_TOP_TABS` always includes Meteorite; parent AC1 tab omission when no row is sibling AST-1692’s React filter, not this ticket’s config surface.
- **Recommendation:** None for this child — UAT fitness sibling check and boundaries are explicit.

### R6 (summary)

Definition fidelity: plan implements only the database read helper, config tab/section defs, manifest attach, and `related_meteorite` projection — all four files match ticket `## Scope`; no retention or frontend creep. DRY: new helper mirrors existing `get_meteorite` / `_meteorite_row_to_dict` pattern; distinct from list-page `JOBS_RECOMMENDED_METEORITE_SECTION`. Self-assessment: estimate confirm **3 — agree** is proportionate. No `!!-NONE` conf gaps. Plan Discuss rounds: **0** completed (Plan Ready; one Hedy publish comment only).

context_tokens≈32000

## Review

**Publish ref:** `sub/AST-1685/AST-1691-meteorite-lookup-report-config-api`
**Build tip:** `8d159e4ee7ecdc3b204d2581ea66110bd8f8670e`
**Status:** Code Complete pending Betty

Stages 1–4: `get_meteorite_by_astral_job_id`; Meteorite on `JOBS_RECOMMENDED_REPORT_TOP_TABS` + `JOBS_RECOMMENDED_REPORT_METEORITE_SECTIONS`; `report_meteorite_sections` on `state_ui_manifest`; `related_meteorite` on job detail GET (full-row debug per Joan discuss). Tests deferred to Betty.
