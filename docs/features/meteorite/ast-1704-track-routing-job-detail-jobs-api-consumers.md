# AST-1704 — Track routing + Job Detail / jobs API consumers

**Linear:** [AST-1704](https://linear.app/astralcareermatch/issue/AST-1704/track-routing-job-detail-jobs-api-consumers)  
**Parent:** [AST-1640](https://linear.app/astralcareermatch/issue/AST-1640/job-source-entity-parent-meteoritecompany-candidate-facing-link) — Job source_entity parent (meteorite|company) + candidate-facing link  
**Publish ref:** `sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`

Rewire analysis-track selection and gazed create so track follows the job’s source-entity parent (`source` column / `SOURCE_ENTITY_TYPES`), and make Job Detail treat `job_link` as an href only when it is `http(s)` while still showing non-http inherited text. Depends on #1 schema SSOT and #2 land/parent writers (already on `origin/ftr/AST-1640-job-source-entity-parent`).

## Scope gate

Ticket **## Scope** (amended after `[scope-gate]` — Chuckles 2026-09-17):

- `src/core/consult.py` — qualify / land-packet / track selection uses `source_entity_type` so meteorite+`company_id` stays on meteorite GDL
- `src/core/gazer.py` and/or `src/core/tracker.py` — gazed ingest sets company parent fields
- `src/ui/api/api_jobs.py` — expose parent fields, nullable `company_id`, `job_link` for detail
- `src/ui/frontend/src/pages/JobsJobDetail.tsx` — deeplink host (prefetch/mount only)
- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `JobDetailModal.tsx` — http(s)-only href; non-http text still shown

All Files Changed / Stages stay inside that set. Out of scope: schema (#1), land create / link inherit (#2), breadcrumb authorship (#3). Do **not** add helpers to `src/utils/config.py` or `src/core/meteorite.py` — use existing `SOURCE_ENTITY_TYPE_*` imports.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Track partition for qualify NEW / title-screen skip uses `source == meteorite`, not `is_meteorite_company(company)` | core |
| `src/core/gazer.py` | `validate_title_batch` skip-meteorite uses source-entity track | core |
| `src/core/tracker.py` | `ingest_jobs` writes `source=company`, `source_entity_id=short_name`, `company_id=employer` | core |
| `src/ui/api/api_jobs.py` | Detail (and list if needed) exposes `source`, `source_entity_id`, `company_id`, `job_link` explicitly | ui |
| `src/ui/frontend/src/pages/JobsJobDetail.tsx` | Prefetch align key from `company_id` (fallback `company`) | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Link row: href only for http(s); else plain text | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Title link href only for http(s); else plain title + show non-http link text if present | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | “Open listing” / `window.open(job_link)` only when http(s) | ui |

## Stage 1: Track SoT in consult + gazer + gazed ingest

**Done when:** A job with `source=meteorite` and a real `company_id` is treated as meteorite track in `qualify_job_listings` / `validate_title_batch` (no title-pattern fail-early). Gazed `ingest_jobs` inserts write company parent fields. No FE changes yet.

1. In `src/core/consult.py`, near `_entity_state_is_meteorite`, add a private helper (do not put this in `config.py`):

```python
def _job_is_meteorite_track(job: Optional[Dict[str, Any]]) -> bool:
    """True when job parent/track SoT is meteorite (AST-1704; physical column `source`)."""
    if not job:
        return False
    return (job.get("source") or "").strip() == SOURCE_ENTITY_TYPE_METEORITE
```

Import `SOURCE_ENTITY_TYPE_METEORITE` from `src.utils.config` (already imports `METEORITE_CONFIG` nearby).

2. In `qualify_job_listings` (the NEW / title-screen block that currently imports `is_meteorite_company`), replace every `is_meteorite_company(j.get("company"))` with `_job_is_meteorite_track(j)`. Remove the `is_meteorite_company` import from that block if unused afterward. Keep `METEORITE_CONFIG["job_create_state"]` re-home for meteorite-track NEW jobs unchanged.

3. In `src/core/gazer.py` `validate_title_batch`, replace the `is_meteorite_company(job.get("company"))` skip with:

```python
from src.utils.config import SOURCE_ENTITY_TYPE_METEORITE
# ...
if (job.get("source") or "").strip() == SOURCE_ENTITY_TYPE_METEORITE:
    # skip title-pattern screen
```

Drop `is_meteorite_company` from this function’s use; remove the module import if nothing else in `gazer.py` still needs it (grep first — `create_meteorite_job` import stays if still used).

4. In `src/core/tracker.py` `ingest_jobs`, change the `database.save_job(...)` call so gazed creates set parent fields explicitly (AST-1701 bridge already accepts `company=` → `company_id`; make the parent SoT explicit):

```python
inserted = database.save_job(
    str(uuid.uuid4()),
    job_title=parse_text(raw_job_listing),
    company=company,  # temporary alias → company_id
    company_id=company,
    source=SOURCE_ENTITY_TYPE_COMPANY,  # or JOB_SOURCE_DEFAULT / SOURCE_ENTITY_TYPE_DEFAULT
    source_entity_id=company,
    state=initial_state,
    job_data={"raw_job_listing": raw_job_listing},
    state_history=[...],
    state_changed_at=now,
)
```

Import `SOURCE_ENTITY_TYPE_COMPANY` (ftr tip already imports source-entity symbols after #2 — add if missing). Do **not** change `save_meteorite_job` (sibling #2 owns land).

⚠️ **Decision:** Track helper lives in `consult.py` / one-liners in `gazer.py` rather than a new `config.py` API — Scope does not include `config.py`. Physical column remains `source` (AST-1701 prefer-repurpose); compare to `SOURCE_ENTITY_TYPE_METEORITE`, not legacy company-state / short_name heuristics.

## Stage 2: jobs API parent fields + Job Detail http(s)-only href

**Done when:** `/api/jobs/:id` JSON includes `source`, `source_entity_id`, `company_id`, and `job_link`. Job Detail link chrome shows non-http text without using it as `href` / `window.open`.

1. In `src/ui/api/api_jobs.py` `detail`, after `get_job` / flatten, ensure the response includes parent fields even if callers strip unknowns later. Minimal approach: before `return jsonify(job)`, set:

```python
job["company_id"] = job.get("company_id")  # may be None
job["source"] = job.get("source")
job["source_entity_id"] = job.get("source_entity_id")
# job_link already on row; leave as-is (inherited by #2 land)
```

If list endpoints return job rows used by Detail chrome, apply the same keys there only when those endpoints already serialize full job dicts — do not invent new list columns outside current list payload shape. Prefer detail-only if list is a projection without `job_link` chrome.

2. In `src/ui/frontend/src/pages/JobsJobDetail.tsx`, when reading the prefetch JSON, prefer `company_id` for candidate align:

```typescript
const data = (await res.json()) as { company_id?: unknown; company?: unknown }
const co =
  (typeof data.company_id === "string" ? data.company_id.trim() : "") ||
  (typeof data.company === "string" ? data.company.trim() : "")
setCompany(co)
```

3. Shared FE predicate — **inline** the same one-liner in each of the three components (no new shared module file outside Scope):

```typescript
const isHttpJobLink = (link: string | null | undefined) => {
  const t = (link ?? "").trim().toLowerCase()
  return t.startsWith("http://") || t.startsWith("https://")
}
```

4. `JobDetailModal.tsx` Link row (read-only branch that currently always wraps in `<a href={job.job_link}>`):

- If `job.job_link` is non-empty and `isHttpJobLink(job.job_link)` → keep `<a href=…>`.
- Else if `job.job_link` is non-empty → render plain `<span>{job.job_link}</span>` (breadcrumb / non-http text visible).
- Else → omit the row as today when falsy.

Editable draft input for skipped-state edits may keep a text input of the raw string (no href).

5. `RecommendedJobReportHeader.tsx`:

- Compute `const httpLink = isHttpJobLink(link) ? link : null`.
- Title: if `httpLink` → `<a href={httpLink}>…</a>`; else plain title `<span>`.
- If `link` is non-empty and **not** http → still show the string as secondary text (e.g. a muted line under the title or next to it) so AC5 “non-http text still shown” holds — do not hide breadcrumb text just because it is not a navigable href.

6. `JobAnalysisReportModal.tsx`:

- Wherever `window.open(job.job_link, …)` or equivalent “open listing” runs, gate with `isHttpJobLink(job.job_link)`.
- Pass `jobLink={isHttpJobLink(job.job_link) ? (job.job_link ?? null) : null}` into `RecommendedJobReportHeader` **only if** the header would otherwise invent an href from a non-http string — **or** pass the raw `job_link` and let the header apply step 5 (prefer one place: header owns title href; modal owns `window.open` gates). Do not double-hide text: if header receives null for href purposes, still pass raw link for text display via a separate prop **only if** step 5 needs it. Simplest: pass raw `job.job_link` into `jobLink` and let RecommendedJobReportHeader implement step 5 fully; modal only gates its own `window.open` / open-listing handlers.

⚠️ **Decision:** Prefer raw `jobLink` into the header + local http check (single text-surface rule in the header) rather than stripping non-http before the child and losing the string.

## Estimate

Confirm Chuckles estimate: 3 — agree

Cross-layer glue (consult/gazer/tracker + API + three FE surfaces) with a clear SoT from #1/#2 — fits a 3.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`.
- Before coding, `sync-child.sh` must attach current `origin/ftr/AST-1640-job-source-entity-parent` (or re-run with the parent segment that exists on origin) so #1/#2 symbols are present — if `SOURCE_ENTITY_TYPE_*` are missing on the worktree tip, stop and comment on parent AST-1640 rather than inventing config.
- Do not edit `meteorite.py` land, schema DDL, or breadcrumb authorship.
- Ambiguity → stop, comment on parent AST-1640 with Stage blocked template.

## Revisions

Revision 1 — 2026-09-17  
Driven by: Chuckles `[scope-gate] cleared` — Scope amended to name `JobAnalysisReportModal` / `RecommendedJobReportHeader` / `JobDetailModal` for AC5.  
Changes: first full plan after scope-gate unblock (no prior plan doc on publish ref).

## Joan validate

[plan-rubric]
**Ticket:** AST-1704
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers` @ `9c8158e7ffddd1452815fc6da373e8c5b5b8ef78`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | X | | Consumer rewire only — no `dispatch_task` claim-shape literals or criteria sourcing changes |
| stat.logging.debug | A | | No new gated `logger.debug`, `print`, or `logger.info("[DEBUG]")`; existing consult loop debug preserved; FE out of statute scope |

## Traceability

AC4 → Stage 1 (`_job_is_meteorite_track` + `validate_title_batch` skip on `source=meteorite`; meteorite+real `company_id` avoids gazed title fail-early). AC5 → Stage 2 (`api_jobs` detail fields + `JobDetailModal` / `RecommendedJobReportHeader` / `JobAnalysisReportModal` http(s)-only href with non-http text shown). AC6 → Stage 1 (track partition from `source` / `SOURCE_ENTITY_TYPE_METEORITE`, not `is_meteorite_company(company)`). Parent AC1–3, 7–9 N/A — siblings #1–#3. Stages 1–2 → parent Functional scope items 3–4, 8–9 (child partition).

## Findings

### discuss

- **Location:** Stage 1 — `_job_is_meteorite_track` vs `gazer.py` one-liner
- **Finding:** Track predicate duplicated (`consult.py` helper vs inline compare in `validate_title_batch`) because Scope excludes new `config.py` shared helper.
- **Recommendation:** Accept for this ticket; optional future extract if a later scope allows config wiring.

- **Location:** Scope header “land-packet / track selection” vs stages
- **Finding:** Plan names land-packet in Scope but stages only touch `qualify_job_listings` title partition and gazer title skip; `enrich_meteorite_land_packet` already routes through `qualify_meteorite` without `is_meteorite_company`.
- **Recommendation:** No plan change; note in stage comment that land-packet path is already source-entity-neutral.

- **Location:** Stage 2 step 1 — `api_jobs.detail`
- **Finding:** Explicit `job["source"] = job.get("source")` assignments are defensive if `get_job` already returns parent columns post-#1; low risk either way.
- **Recommendation:** Implementer confirms detail JSON includes `source`, `source_entity_id`, `company_id`, `job_link` in manual check.

- **Location:** `consult.py` `_entity_state_is_meteorite` (unchanged)
- **Finding:** Still used for evaluate rubric override by job state prefix; not rewired to `source`. Parent AC6 fail test targets qualify/gazer old-flag routing — outside that narrow fail mode.
- **Recommendation:** Escalate only if UAT shows rubric mis-selection on meteorite-parent + real employer; not a plan blocker for declared ACs.

### acceptable

- **Location:** `[scope-gate]` thread + amended Scope gate
- **Finding:** Prior gate correctly named `JobAnalysisReportModal`, `RecommendedJobReportHeader`, `JobDetailModal`; republished plan covers all three href surfaces AC5 needs.
- **Recommendation:** None.

- **Location:** Stage 2 steps 4–6
- **Finding:** Targets current bug surfaces (`RecommendedJobReportHeader` `{link ? <a>}`, `JobDetailModal` always `<a href>`, `JobAnalysisReportModal` ungated `window.open(job.job_link)`).
- **Recommendation:** None.

- **Location:** Stage 1 step 4 — `tracker.ingest_jobs`
- **Finding:** Explicit `source=company`, `source_entity_id=company`, `company_id=company` aligns gazed create with #1 parent SoT.
- **Recommendation:** None.

### fix-now

(none)

context_tokens≈72000

---

## Review

- **Build tip:** `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers` @ `9c2e34c71d4c81e86d66a97986273730b00f7579`
- **Stages:** track SoT consult/gazer/ingest_jobs → API parent fields + http(s)-only Job Detail hrefs

