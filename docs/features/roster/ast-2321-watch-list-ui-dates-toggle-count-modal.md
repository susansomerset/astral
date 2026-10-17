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
