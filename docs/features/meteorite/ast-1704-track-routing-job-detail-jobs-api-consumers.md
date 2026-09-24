<!-- linear-archive: AST-1704 archived 2026-09-24 -->

## Linear archive (AST-1704)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1704/track-routing-job-detail-jobs-api-consumers-job-source-entity-parent  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1640 — Job source_entity parent (meteorite|company) + candidate-facing link  
**Blocked by / blocks / related:** parent: AST-1640

### Description

## What this implements

Rewires qualify/consult/gazer so track follows `source_entity_type`; gazed ingest writes company parent fields; jobs API + Job Detail show inherited `job_link` with http(s)-only href.

## Citations

`patt.entity.batch-criteria`, `stat.logging.debug`.

## Scope

- [X] `src/core/consult.py` — qualify / land-packet / track selection uses `source_entity_type` so meteorite+`company_id` stays on meteorite GDL.
- [X] `src/core/gazer.py` and/or `src/core/tracker.py` gazed ingest — gazed creates set `source_entity_type=company`, `source_entity_id=short_name`, `company_id` to that employer when known.
- [X] `src/ui/api/api_jobs.py` — expose parent fields, nullable `company_id`, and `job_link` (inherited) for detail.
- [X] `src/ui/frontend/src/pages/JobsJobDetail.tsx` — deeplink host for Job Detail (prefetch/mount only).
- [X] `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, and `src/ui/frontend/src/components/JobDetailModal.tsx` — show inherited `job_link` text; “open listing” / title / Link-row href only when `http(s)` (non-http text still shown; no new meteorite pages).
- [X] Technical: `consult` / consumers — track from `source_entity_type` (or single config helper), not company state `METEORITE` and not legacy `source == "meteorite"` meaning. `gazer` create — company parent + `company_id` for gazed employer. `api_jobs` + Job Detail FE — serialize fields; href only for http(s) `job_link`.

## Acceptance criteria

- [X] 4\. A meteorite-parented job with real `company_id` is claimed/run by `qualify_meteorite`, not gazed title-pattern fail-early. Fail: track flips to gazed solely because `company_id` is set.
- [X] 5\. Job Detail “open listing” is a navigable href only when `job.job_link` starts with `http://` or `https://`; non-http inherited text is still shown as text. Fail: breadcrumb/`email-` token used as href, or non-http `job_link` hidden with no text surface.
- [X] 6\. Track/parent selection paths use `source_entity_type` (or its config helper), not legacy `source == "meteorite"` / company state `METEORITE` as SoT. Fail: qualify/gazer still keys off the old flag meaning.

## Boundaries

- [X] Does not own schema migration (#1) or land create (#2). After #2.

## Notes for planning

Estimate 3. After #2.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1640-job-source-entity-parent`, child `sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-17T01:54:02.619Z
[code-rubric] PROCEED (Commit: 211e9e01) track routing consumers clean

#### betty — 2026-09-17T01:51:24.770Z
`origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers` @ `211e9e013c3a65b6ede67652d41f87a19968491b` · track + href coverage

#### joan — 2026-09-17T01:39:15.790Z
[plan-rubric] PROCEED (Commit: 9c8158e) track routing Job Detail clear

#### ada — 2026-09-17T01:37:06.227Z
`origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers` @ `9c8158e7ffddd1452815fc6da373e8c5b5b8ef78` · plan ready

#### chuckles — 2026-09-17T01:35:18.771Z
[scope-gate] cleared — Scope amended on AST-1704 + parent Component/Technical/#4 partition.

Named Job Detail link surfaces: `JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `JobDetailModal.tsx` (JobsJobDetail remains deeplink host). AC5 unchanged — http(s)-only href; non-http text still shown. Re-spawning plan-child.

#### ada — 2026-09-17T01:34:00.298Z
[scope-gate] AST-1704 cannot satisfy AC5 within declared ## Scope alone.

Need: frontend surfaces that render Job Detail “open listing” / job_link as an href — at minimum `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` and `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` (title link / window.open on job_link), and likely `src/ui/frontend/src/components/JobDetailModal.tsx` (always `<a href={job.job_link}>` for the Link row).

Quoted Scope (frontend only):
`src/ui/frontend/src/pages/JobsJobDetail.tsx` — show inherited `job_link` text; “open listing” href only when `http(s)` (no new meteorite pages).

Why blocked: `JobsJobDetail.tsx` is a deeplink host — it prefetches company for candidate align and mounts `JobAnalysisReportModal`; it does not render job_link chrome. AC5 Fail (“breadcrumb/email- token used as href”) is produced by the modal/header components above, which are not named in this child’s Scope. Adding them here would be scope invention.

Also needed for AC4/AC6 consumers already in Scope (`consult.py` track partition, `gazer.py`/`tracker.py` gazed create, `api_jobs.py` serialize) — those are covered. Only the FE href surface is missing.

@Chuckles — please amend AST-1704 ## Scope (and parent Component partition if needed) to name the Job Detail link surfaces, then re-spawn plan-child.

---

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

## Radia review

[code-rubric]

**Ticket:** AST-1704  
**Publish ref:** `211e9e013c3a65b6ede67652d41f87a19968491b` (`origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`)  
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`  
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | X | | Consumer rewire only — no `dispatch_task` claim-shape literals or criteria sourcing changes |
| stat.logging.debug | A | | No new gated `logger.debug`, `print`, or `logger.info("[DEBUG]")`; existing consult loop debug preserved; FE out of statute scope |

## Column diff vs plan stage

(aligned) — Joan graded `patt.entity.batch-criteria` **X** and `stat.logging.debug` **A**; code review matches on both.

## Frame diff

(none) — Description **Acceptance criteria** / **Boundaries** rows already checked; tip satisfies AC4–AC6.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** Three-dot diff vs `origin/dev`  
  **Finding:** Publish ref stacks AST-1701–1703 foundation plus AST-1704 consumer glue. AST-1704 **code** commits touch only `consult.py`, `gazer.py`, `tracker.py` (ingest), `api_jobs.py`, and three FE components + `JobsJobDetail.tsx` (+ tests/bible).  
  **Recommendation:** Expected epic ordering; no resolve-child action on #4 for sibling foundation files.

- **Location:** `merge-tests(AST-1704)`  
  **Finding:** Betty merge-tests carries unrelated sibling test/bible hunks from `origin/tests` alongside AST-1704 coverage.  
  **Recommendation:** Rollup awareness only.

- **Location:** `consult.py` `_entity_state_is_meteorite` (unchanged)  
  **Finding:** Evaluate/rubric override still keys off job **state** prefix, not `source`. Joan flagged this as outside AC4/AC6 narrow fail mode unless UAT shows rubric mis-selection.  
  **Recommendation:** Watch during parent UAT; escalate only if rubric mis-routes meteorite-parent + real employer jobs.

- **Location:** Stage 1 — track predicate duplication  
  **Finding:** `_job_is_meteorite_track` in `consult.py` vs inline `source == SOURCE_ENTITY_TYPE_METEORITE` in `gazer.validate_title_batch` — plan accepts because Scope excludes new shared config helper.  
  **Recommendation:** Optional future extract if a later ticket opens config wiring; not resolve-child for #4.

## What's solid

- **Stage 1 / AC4 + AC6:** `_job_is_meteorite_track` partitions `qualify_job_listings` NEW jobs by `source=meteorite`, not `is_meteorite_company(company)`; `validate_title_batch` skips title screen on meteorite source; `ingest_jobs` writes `source=company`, `source_entity_id=company`, `company_id=company`. Tests: `TestAst1704MeteoriteTrackSoT`, revised `test_gazer`, revised `test_tracker`.
- **Stage 2 / AC5:** `api_jobs.detail` exposes `company_id`, `source`, `source_entity_id` (plus inherited `job_link`); `JobDetailModal` http(s)-only `<a>` else plain text; `RecommendedJobReportHeader` http(s) title href + muted non-http line; `JobAnalysisReportModal` gates `window.open` to http(s); `JobsJobDetail` prefetch prefers `company_id`. Component/API tests cover breadcrumb text visibility without href.
- **Scope:** No `meteorite.py` land/breadcrumb edits, no new config helpers, no schema DDL in AST-1704 commits — matches amended Scope gate.

## Recommended actions (downstream — not Radia lane)

- Chuckles: append artifact, commit `docs(AST-1704): Radia review — clean`, push sub ref, post slim upshot `--as radia`, move to **Review Posted**.
- datt: **PROCEED** → **User Testing**.
- Parent UAT: exercise meteorite-parent + real `company_id` through qualify path and breadcrumb `job_link` chrome end-to-end on epic line after siblings merge.

context_tokens≈62000

---
