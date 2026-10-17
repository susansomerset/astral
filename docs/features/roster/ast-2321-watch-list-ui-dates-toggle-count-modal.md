# AST-2321 — Watch List UI, dates toggle, count modal

- **Linear:** [AST-2321](https://linear.app/astralcareermatch/issue/AST-2321)
- **Parent:** [AST-2318](https://linear.app/astralcareermatch/issue/AST-2318)
- **Publish ref:** `sub/AST-2318/AST-2321-watch-list-ui-dates-toggle-count-modal`

Candidate Watch List consumes AST-2320’s enriched `view=watch_list` payload and shapes: dates toggle formats count cells as `N (m/d/yy)`, count columns stay numeric for ListPage sort, clicking a named count opens a filtered jobs modal that opens existing `JobDetailModal`, bulk is Ignore-only (Retry Scrape removed). Does not own aggregates/shapes API (AST-2320), TEST_WATCH (AST-2319), or add-company / Ignored restore (AST-2322).

**Depends on:** AST-2320 payload + shapes (`scan_start`, `best_fit_*`, `jobs`, `jl`…`applied`, `*_newest_at`, `GET /api/companies/<short_name>/jobs?bucket=`). Build after that tip is on the epic line (or mergeable).

## Explicit scope gate

Ticket **Scope** names exactly these files/kinds:

| File | Allowed kind |
|------|----------------|
| `src/ui/frontend/src/pages/CompaniesWatchList.tsx` | Modified page: shapes, dates toggle, sort (via existing ListPage), count clicks, ignore action; drop Retry Scrape |
| `src/ui/frontend/src/components/CompanyWatchJobsModal.tsx` | **New** filtered job table + open `JobDetailModal` |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Modified **only if** a thin open/close (or stack) hook is required |
| `src/ui/frontend/src/components/ListPage.tsx` | Modified **only if** shared clickable-cell API is required after page-local attempt |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/CompaniesWatchList.tsx` | Dates toggle in `actions`; map shapes → columns with count/`best_fit` renders; Ignore-only bulk; wire jobs modal | ui |
| `src/ui/frontend/src/components/CompanyWatchJobsModal.tsx` | New modal: fetch bucket jobs, table, open stacked job detail | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Optional `stacked?: boolean` passed through to `Modal` (thin stacking hook) | ui |

⚠️ **Decision:** Do **not** modify `ListPage.tsx`. Count display uses page-local `Column.render` while row values stay numeric ints so existing `cmpValues(…, { numeric: true })` satisfies AC6. Clickable counts use `stopPropagation` (same pattern as `JobsMeteorites` `astral_job_id` button).

## Stages

### Stage 1: `JobDetailModal` stacked prop + `CompanyWatchJobsModal`

**Done when:** `CompanyWatchJobsModal` opens for `(shortName, bucket, candidateId)`, loads `GET /api/companies/<short_name>/jobs?bucket=<bucket>&candidate_id=<id>`, lists those jobs, and a row click opens `JobDetailModal` with `stacked` so it layers over the jobs modal. Closing job detail returns to the jobs list. Empty bucket shows an empty-state line, not an error toast.

1. In `src/ui/frontend/src/components/JobDetailModal.tsx`, extend `Props` with optional `stacked?: boolean` (default unset/`false`). Pass `stacked={stacked}` into the existing `<Modal …>` call. Do not change fetch, tabs, or save behavior.

2. Create `src/ui/frontend/src/components/CompanyWatchJobsModal.tsx`:

   ```tsx
   interface Props {
     shortName: string | null
     bucket: string | null       // WATCH_LIST key: jl | jd | … | applied
     bucketLabel: string         // shape label for title, e.g. "ACTIVE"
     candidateId: string | null
     onClose: () => void
   }
   ```

   - `open` when `shortName` and `bucket` and `candidateId` are all non-null/non-empty.
   - On open/change of those three: `api(\`/api/companies/${encodeURIComponent(shortName)}/jobs?bucket=${encodeURIComponent(bucket)}&candidate_id=${encodeURIComponent(candidateId)}\`)`, store job array (or `[]` on non-OK).
   - Use `<Modal open={…} onClose={onClose} title={\`${bucketLabel} — ${shortName}\`} showFooter={false}>` (no Save).
   - Body: loading line while fetching; else a simple `<table>` with columns **Title** (`job_title` or "—"), **State** (`state`), **Changed** (`state_changed_at` via existing `<Time value={…} />` or `formatCell(…, "datetime")`). Each data row `className="clickable"` → `setJobId(row.astral_job_id)`.
   - Render `<JobDetailModal jobId={jobId} onClose={() => setJobId(null)} stacked />` beside the Modal (sibling, not nested inside Modal children — same portal pattern `JobDetailModal` already documents for its own nested modals).

⚠️ **Decision:** Jobs modal owns `JobDetailModal` state. Parent Watch List does not also mount a second job modal.

### Stage 2: Watch List page — columns, dates toggle, ignore-only, wire modal

**Done when:** Watch List shows AST-2320 shape columns; Best Fit cell is `LABEL` or `LABEL (m/d/yy)` with no `FAILED_` substring; dates toggle off → count cells show `N` only; toggle on and count ≥1 → `N (m/d/yy)` from `{key}_newest_at`; clicking a count with N≥1 opens `CompanyWatchJobsModal` for that company+bucket without opening company detail; header sort on a count column orders numerically (`10` after `9`); bulk bar has **Set to Ignore** only (no Retry Scrape); Ignore still posts `watch_list_ignore_to_state` from the manifest. `npm run build` and `npm run lint` in `src/ui/frontend` are clean vs this change set (AC9).

1. In `src/ui/frontend/src/pages/CompaniesWatchList.tsx`, add state:

   - `showDates: boolean` — default `false` (not persisted).
   - `jobsModal: { shortName: string; bucket: string; label: string } | null`.
   - Keep `viewing` for `CompanyDetailModal`.

2. Define the clickable count keys as a const array (must match AST-2320 bucket keys, not including `jobs`):

   ```ts
   const COUNT_BUCKET_KEYS = ["jl", "jd", "do", "get", "like", "active", "skipped", "applied"] as const
   ```

3. Add a tiny local date helper (file-local function, not a new util module):

   - Input: ISO/`YYYY-MM-DD HH:MM:SS` string (or null).
   - Output: `m/d/yy` via the same approach as `formatCell(…, "date")` (reuse `formatCell` from `../lib/fmt` — date token already yields the date portion of `fmtTime`).
   - Null/invalid → do not append a date clause.

4. After shapes load, build columns with `useMemo` depending on `[apiColumns, showDates]` (or rebuild inside the load `.then` plus a second `useMemo` that maps `columns`/`showDates`):

   - Start from `shapes.list.watch_list` (array of `{key,label,sortable?,type?,defaultDesc?}`).
   - **Omit** shape key `best_fit_at` from the ListPage column list (date rides on the Best Fit cell).
   - For `best_fit_label`: `render = (_v, row) => { const label = String(row.best_fit_label ?? ""); if (!label) return "—"; const at = row.best_fit_at; if (!at) return label; return \`${label} (${shortDate(String(at))})\`; }` — never print raw `FAILED_*` states (API already sends UI labels).
   - For each key in `COUNT_BUCKET_KEYS`: keep `type: "int"` / sortable from shape; `render = (value, row) => { const n = Number(value) || 0; const text = showDates && n >= 1 ? \`${n} (${shortDate(String(row[\`${key}_newest_at\`] ?? "")) || "—"})\` : String(n); /* if shortDate empty when toggle on, fall back to String(n) only */ … }`. When `n >= 1`, wrap `text` in `<button type="button" className="dispatch-batch-link" onClick={e => { e.stopPropagation(); setJobsModal({ shortName: row.short_name, bucket: key, label: col.label }); }}>{text}</button>`. When `n === 0`, render plain text (not a button).
   - Leave `company_name`, `scan_start`, `last_scan_at`, `jobs` as shape defaults (no click handler on `jobs`).

   Do **not** overwrite row field values with formatted strings — sort must read numeric `row.jl` etc.

5. Pass `actions={…}` to `ListPage` (same slot as New List Import):

   ```tsx
   <label className="recommended-analysis-toggle">  {/* reuse existing toggle class from Jobs Recommended */}
     <input type="checkbox" checked={showDates} onChange={e => setShowDates(e.target.checked)} />
     Show dates
   </label>
   ```

6. Bulk actions: only

   ```ts
   [{ label: "Set to Ignore", onClick: ids => handleBulk("ignore", ids), variant: "danger" }]
   ```

   Rewrite `handleBulk` so it only handles ignore: `to_state = manifest.company.bulk_transitions.watch_list_ignore_to_state`. Delete any read of `watch_list_ack_to_state` / Retry Scrape path.

7. Mount:

   ```tsx
   <CompanyWatchJobsModal
     shortName={jobsModal?.shortName ?? null}
     bucket={jobsModal?.bucket ?? null}
     bucketLabel={jobsModal?.label ?? ""}
     candidateId={selectedId}
     onClose={() => setJobsModal(null)}
   />
   ```

   Keep `CompanyDetailModal` on row click as today.

8. In `src/ui/frontend`, run `npm run build` and `npm run lint`. Fix only issues introduced by this ticket’s files (AC9).

⚠️ **Decision:** Dates toggle is session-local React state (default off), matching Jobs Recommended analysis toggle — not localStorage.

⚠️ **Decision:** Only the eight named count columns are clickable; **Jobs** total is display/sort only.

⚠️ **Decision:** Prefer page-local `Column.render` over ListPage API changes (Notes for planning). ListPage stays untouched.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

```text
[plan-rubric]
**Ticket:** AST-2321
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2318/AST-2321-watch-list-ui-dates-toggle-count-modal` @ `1a77858fb55de6f23b32db7fa6bebf963a81d5ca`

## Canon scores

(no directive ids on the ticket’s frozen Citations list — explicit “none beyond parent”; nothing to score in R3)

## Traceability

AC 5 → Stage 2 (dates toggle + count `Column.render` using `{key}_newest_at`); AC 6 → Stage 2 (numeric row fields + ListPage sort on `row[key]`); AC 7 → Stage 1 (`CompanyWatchJobsModal` + bucket jobs API + stacked `JobDetailModal`); AC 8 → Stage 2 (Ignore-only bulk, drop Retry Scrape / `watch_list_ack_to_state`); AC 9 → Stage 2 (`npm run build` / `npm run lint`). Parent AC 1–4, 10–12 N/A (aggregates API, add/restore, TEST_WATCH, backend). Child AC 8 end-to-end ignore needs `watch_list_ignore_to_state` + `bulk_state` from siblings — assumed on epic line per Depends.

## Findings

**discuss** — Linear assignee is Ada, not Joan; Chuckles should assign Joan before validate-plan handoff per skill §1 (review proceeded on spawn instruction).

**acceptable** — Explicit scope gate matches ticket Scope; decision not to touch `ListPage.tsx` after page-local `render` + `stopPropagation` matches precedent (`JobsMeteorites`).

**acceptable** — Sort reads raw `row.jl`…`applied` ints while display formats in `render` — satisfies AC6 without ListPage API changes.

**discuss** — Plan prose cites `cmpValues(…, { numeric: true })`; `ListPage`’s `cmpValues` has no options arg (always uses `localeCompare` with `numeric: true`). Behavior for numeric row fields is still fine — implementers should follow actual `ListPage.tsx`, not the shorthand in the plan.

**discuss** — Best Fit cell always appends date when `best_fit_at` is set, independent of the dates toggle — aligns with parent functional scope (“Best Fit always carries its date”); AC5 only governs count columns.

**discuss** — `CompaniesWatchList.tsx` `actions` slot will also gain add-company UI in AST-2322; merge/build order should keep both affordances without dropping the dates toggle.

context_tokens≈85000
```

## Review

- **Publish ref:** `sub/AST-2318/AST-2321-watch-list-ui-dates-toggle-count-modal`
- **Tip:** `269aacb2a` — `code(AST-2321): Watch List dates toggle, count clicks, ignore-only`

## Radia review

```text
[code-rubric]
**Ticket:** AST-2321
**Publish ref:** `269aacb2a084d1bb978375046fb37f285281553b`
**Overall:** CLEAN
## Findings
### fix-now
(none)
### discuss
(none)
context_tokens≈48000
```

## Bug: AST-2326 — Watch List job popup + count/date polish

### As-is

Gaze Roster Watch List job popup (`CompanyWatchJobsModal`) rows use a bare `clickable` table with Title / State / Changed — they do not read as interactive list items, omit rubric analysis dots (API drops `job_data` before grades can render), and expose a State column candidates do not need. Count cells show `0` for empty buckets; Scan Start / Last Scan use full datetime; count cells follow default int right-align. The **Jobs** total column is display-only (no popup). There is no Scan count column — only job totals / bucket counts.

### To-be

Popup rows look clickable, show `PhaseAnalysisLines` when phase grades exist, and still open `JobDetailModal` on row click; State column removed. **Jobs** opens a modal of all company jobs grouped by State (group headers = title case with `_` → spaces). Watch List shows a **Scan** count (number of `company_job_scan` rows for that company). Empty count cells render `-` (sort still uses numeric 0). Scan Start / Last Scan show date-only with a tooltip of the full timestamp. Count columns (Scan, Jobs, JL…APPLIED) are center-aligned.

### Repro

1. Open Gaze Roster Watch List for a candidate with at least one WATCH company that has jobs in ACTIVE and at least one empty bucket; company should have ≥1 gazer scan row in `company_job_scan` and ≥1 job with phase grades in `job_data`.
2. Observe empty bucket cells show `0`; Scan Start / Last Scan include clock time; count cells are right-aligned; no Scan column; Jobs is not clickable.
3. Click an ACTIVE count → modal shows State column, plain title rows without analysis dots; row affords little click cue beyond default cursor.

### Root cause

AST-2321 shipped a minimal jobs modal and count renders against the AST-2320 slim payload: `_WATCH_JOB_LIST_DROP_KEYS` removes `job_data` (so no grades for `PhaseAnalysisLines`), State is listed as a column, empty counts stringify `0`, datetime shape type drives full timestamps, int type right-aligns counts, Jobs was intentionally non-clickable, and Scan was never part of the watch_list shape/enrichment.

### Proposed change

1. **`src/data/database.py`** — add `count_company_job_scans(company_ids: List[str]) -> Dict[str, int]`: one `SELECT short_name, COUNT(*) FROM company_job_scan WHERE short_name IN (…) GROUP BY short_name` (empty input → `{}`). No schema change.

2. **`src/core/roster.py`** — thin facade `get_companies_scan_counts(company_ids)`; in `enrich_watch_list_company` (or the watch_list enrich loop in the API) set `scan_count` from that map (missing → `0`).

3. **`src/utils/config.py`** — in `DATA_SHAPES["companies"]["list"]["watch_list"]`, insert `{key: "scan_count", label: "Scan", sortable: True, type: "int"}` immediately before the `jobs` column. Keep existing count keys.

4. **`src/ui/api/api_companies.py`**
   - Watch_list enrichment: attach `scan_count` via the new roster/DB helper for the same short_name batch.
   - `company_jobs_by_bucket`: accept `bucket=all` (literal) meaning **no** state `IN` filter — return all jobs for `company_id` + `candidate_id`. Keep existing named buckets unchanged.
   - Before dropping blobs, flatten grades the same way `api_jobs._slim_list_row` does: call `api_jobs._flatten_grades` (import from `ui.api.api_jobs` or move the helper to a shared import the companies route already may use — prefer importing `_flatten_grades` / mirroring the lift of `*_grades`/`*_score`/`*_rubric` keys, then pop `job_data` and `state_history`). Result must still open JobDetailModal by id (detail fetch remains full).

5. **`src/ui/frontend/src/components/ListPage.tsx`** — add optional `align?: "left" | "right" | "center"` on `Column`; when set, `colAlign` uses it instead of `column_types[type].align` (header + cells). No other ListPage behavior change.

6. **`src/ui/frontend/src/components/CompanyWatchJobsModal.tsx`**
   - Props: add `mode: "bucket" | "all"` (or derive: when `bucket === "all"` → all-jobs mode). Title: bucket label as today, or `Jobs — {shortName}` for all.
   - Fetch: same URL with `bucket` query (`all` or named key).
   - Remove State column. Rows: `className="clickable"` plus visible affordance (e.g. reuse `recommended-analysis-row` / underline title via `dispatch-batch-link` styling on the title cell so rows read as interactive).
   - Body columns: **Title** (+ `PhaseAnalysisLines` under the title when the slim job carries any phase grades — same component as Jobs Recommended; pass the job row dict), **Changed** (`<Time />` or date+tooltip).
   - **All mode only:** group rows by `state`; render a non-clickable group header row whose text is title-cased `state.replaceAll("_", " ")` (e.g. `FAILED_JOBLIST` → `Failed Joblist`); jobs under each group still open JobDetailModal. Sort groups by state string ascending; within group keep API order.
   - Empty list copy unchanged in spirit (“No jobs…”).

7. **`src/ui/frontend/src/pages/CompaniesWatchList.tsx`**
   - Count keys for `-` / center / click: `scan_count`, `jobs`, and existing `COUNT_BUCKET_KEYS`.
   - Empty display: when `Number(value) || 0 === 0`, render `-` (not a button); sort still uses numeric `0` on the row.
   - `jobs` click (n ≥ 1): open `CompanyWatchJobsModal` with `bucket: "all"` / label `"Jobs"`.
   - Named buckets unchanged except empty → `-` and centered text.
   - `scan_start` / `last_scan_at` column renders: visible text = `formatCell(raw, "date")`; wrap in `<span title={formatCell(raw, "datetime")}>` (or equivalent full timestamp string). Missing → `—`.
   - Apply `align: "center"` on Scan / Jobs / JL…APPLIED columns when mapping shapes.
   - Do not regress Add Company, Show dates toggle, Ignore-only bulk, or Best Fit combined label+date.

⚠️ **Decision:** Scan count = `COUNT(*)` of `company_job_scan` rows for the company (not last-scan `total_found`). “Jobs found” remains the existing `jobs` total; Scan is the missing scan-history tally Susan asked for beside it.

⚠️ **Decision:** `bucket=all` extends the existing jobs-by-bucket route rather than a second path — modal + page already speak bucket keys.

### Blast radius

- Watch List shapes/payload consumers (AST-2321 UI, any tests asserting shape keys or `0` empty cells).
- `GET /api/companies/<short_name>/jobs` clients (only Watch List modal today); `bucket=all` must not break named buckets.
- ListPage `align` is additive — other pages unchanged unless they set it.
- `PhaseAnalysisLines` / grade flatten share paths with Jobs Recommended list slim rows.
- AST-2322 Add Company on the same page must keep working in the `actions` slot.

### What must still hold

- AST-2320/2321 AC: named bucket counts match state sets; Scan Start = first WATCH history; Best Fit ladder labels without `FAILED_`; dates toggle still expands count cells to `N (m/d/yy)` when on and N≥1; count header sort remains numeric; Ignore-only bulk; no Retry Scrape; Add Company (AST-2322) still posts to `/api/companies/add`.
- Job detail still loads via `GET /api/jobs/<id>` from the stacked modal; popup does not need full `job_data` blob after grade flatten.
- Idempotent GETs still do not emit `stat.logging.info.api` completion lines.

## Radia review (AST-2326)

[code-rubric]
**Ticket:** AST-2326
**Publish ref:** `64a23512839d1dcbcbe1e6758c87acb50ff715a8` (`origin/sub/AST-2318/AST-2326-watch-list-job-popup-count-date-polish`)
**Diff base:** `origin/ftr/AST-2318-company-roster-list-updates...origin/sub/AST-2318/AST-2326-watch-list-job-popup-count-date-polish`
**Parent shape:** Normal (merge via epic `ftr`, not orphaned)
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Overall:** FIX-NOW

## Canon scores

(no frozen directive ids on this bug ticket — nothing to score)

## Column diff vs plan stage

no plan-stage canon scores attached (fix-lane `plan-fix` patch only)

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** OK — repro tests pin AST-2326 to-be behavior (not tautologies): `scan_count` shape order; `bucket=all` grade flatten + `states` unfiltered; empty counts `-` + Jobs → `bucket=all` modal; modal without State column + `.grade-dot` when `jd_grades` present; all-mode group headers `Failed Joblist` / `Recommended`.

**## What must still hold** OK — against plan-fix list: named buckets + enrichment path intact; `bucket=all` additive; dates toggle / numeric sort / ignore-only / Add Company / stacked job detail unchanged on Watch List paths; no new `logger.info` on the GET jobs route in this diff.

## Findings

### fix-now

- **Cross-ticket product scope on fix sub** — `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` and `tests/component/frontend/components/test_MeteoriteDetailModal.test.tsx` ([bug-repro] AST-2325 profile `dep-*` chrome) are **not** in AST-2326 `## Proposed change` / blast radius (Watch List + jobs modal + scan_count only). Shipping them on `sub/AST-2318/AST-2326-…` couples an unrelated meteorite fix to this bug branch and confuses fix-lane review/merge. **Default for resolve-child:** drop meteorite (+ its tests) from this publish ref; land AST-2325 under its own `sub/*` (or split commit) before User Testing.

### discuss

(none)

### advisory

- **Doc carry unrelated to AST-2326:** `docs/features/agent/ast-2224-meteorite-modal-edit-form.md`, `docs/features/team-chuckles/ast-2325-…` appear in the ftr…sub diff — note for Chuckles if those commits should ride this sub or a different ref.
- **Private API import:** `company_jobs_by_bucket` imports `ui.api.api_jobs._flatten_grades` — matches plan (“prefer importing `_flatten_grades`”); acceptable but couples companies route to jobs module internals (already called out in plan).

## What's solid

- `count_company_job_scans` + watch_list enrichment → `scan_count` before `jobs` in shape.
- `bucket=all` on existing jobs route; grades flattened before blob drop; named buckets unchanged.
- `ListPage` optional `align`; Watch List centered counts, `-` for zero, Jobs opens all-jobs modal, scan/last-scan date + tooltip.
- `CompanyWatchJobsModal`: no State column; `recommended-analysis-row` + grade dots; all-mode grouping with title-cased headers.

## Recommended actions (Chuckles)

| Gate | Parent | Next |
|------|--------|------|
| **REVIEW** | Normal | → **Review Posted** → **resolve-child** (strip meteorite scope from sub, re-run manifest) → **User Testing** when clean |
| After clean **PROCEED** | Normal | → **Review Posted** → fix-lane clean shortcut → **User Testing** (skip resolve-child) |

Do **not** treat meteorite changes as part of AST-2326 acceptance until scope is split or Susan explicitly approves bundling.
