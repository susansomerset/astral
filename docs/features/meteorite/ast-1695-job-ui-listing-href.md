# AST-1695 — All job UI surfaces use listing href

**Linear:** [AST-1695](https://linear.app/astralcareermatch/issue/AST-1695/all-job-ui-surfaces-use-listing-href-hyperlink-to-job-with-meteorite)  
**Parent:** [AST-1686](https://linear.app/astralcareermatch/issue/AST-1686/hyperlink-to-job-with-meteorite-http-link) — Hyperlink to job with meteorite http link  
**Publish ref:** `sub/AST-1686/AST-1695-job-ui-listing-href`

Recommended Job Report title + CLIENT Apply, and Job Detail’s listing control, open the resolved http(s) listing URL from `GET /api/jobs/<id>` (`listing_href`, AST-1694). Does not own API/writers (AST-1694 / AST-1693). Non-http values stay non-navigable.

## Explicit scope gate

This ticket’s **## Scope** names only:

- `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`
- `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`
- `src/ui/frontend/src/components/JobDetailModal.tsx`

Technical: shared href for title/Apply/detail listing; non-http → not navigable. Stages below stay inside those three files and that change kind.

**Citations:** none (presentational / client open only) — no canon patterns to expand at plan or build.

**Field contract (locked by AST-1694):** `listing_href` on the job detail JSON — http(s) string or `null`. Prefer that field for every navigable open on these surfaces; do **not** invent a second resolve path in React (no meteorite client fetch).

**Depends on:** AST-1694 (`listing_href` on detail). After `sync-child.sh`, if `detail()` in `api_jobs.py` does not attach `listing_href`, **stop** and comment on AST-1695 — do not re-implement the API here. AST-1693 writers are required for UAT of bot-blocked rows that carry `job_link`; not a code dependency for this UI pass.

**Out of scope:** `api_jobs.py`, `database.py`, meteorite/consult/tracker writers, `JOBS_RECOMMENDED_PRIMARY_ACTIONS` config (CLIENT Apply keeps `path_suffix: "job_link"` — unused by the CLIENT branch), tests/bible.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Type + pass `listing_href`; CLIENT Apply + header use it | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Title `<a>` / plain title from resolved listing prop | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | Read-only (and editable companion) listing control from `listing_href` | ui |

## Stages

### Stage 1: Recommended report — title + Apply share `listing_href`

**Done when:** Opening a Recommended Job Report whose detail JSON has `listing_href: "https://…"` shows the job title as `<a href="https://…">` and Apply (`CANDIDATE_REVIEW` CLIENT) opens that same URL in a new tab. When `listing_href` is `null`/absent/non-http, the title is a plain `<span>` and Apply does not call `window.open`. No API or config files changed.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, on the `JobDetail` interface, add:

```ts
listing_href?: string | null
```

   Keep existing `job_link` on the type (still present on the payload; other code may read it later — this ticket simply stops using it for navigation).

2. In the same file, above the component (module scope), add:

```ts
/** Navigable listing URL only — mirrors AST-1694 http(s) rule; non-http → null. */
function httpListingHref(raw: string | null | undefined): string | null {
  if (raw == null) return null
  const s = String(raw).trim()
  if (s.startsWith("http://") || s.startsWith("https://")) return s
  return null
}
```

3. In `runPrimaryAction`, replace the CLIENT branch body so it opens `listing_href` only:

```ts
if (action.method === "CLIENT") {
  const href = httpListingHref(job.listing_href)
  if (href) window.open(href, "_blank", "noopener,noreferrer")
  return
}
```

   Do **not** fall back to `job.job_link` (non-http breadcrumbs must not open).

4. Where `RecommendedJobReportHeader` is rendered, change the listing prop from `job.job_link` to the resolved href:

```tsx
jobLink={httpListingHref(job.listing_href)}
```

   (Prop name stays `jobLink` on the header — single caller; value is the resolved listing URL or `null`.)

5. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, keep the existing title branch: trimmed truthy `jobLink` → `<a href={link} target="_blank" rel="noopener noreferrer" className="recommended-report-title-link">{jobTitle}</a>`; else plain `<span className="recommended-report-title">{jobTitle}</span>`. No other prop or layout changes. Comment at the `jobLink` prop: callers pass AST-1694 `listing_href` (http(s) or null), not raw `job_link`.

⚠️ **Decision:** Keep header prop name `jobLink` (only caller is this modal) and pass the already-filtered `listing_href`. Renaming the prop is churn without a second consumer; the comment + Stage 1 step 4 lock the contract.

⚠️ **Decision:** Client re-checks http(s) via `httpListingHref` even though the API already filters — belt-and-suspenders for stale clients / partial payloads; still no meteorite lookup in the UI.

### Stage 2: Job Detail listing control uses `listing_href`

**Done when:** Opening Job Detail for a job whose detail JSON has http(s) `listing_href` shows a clickable Link row (or Open listing control when fields are editable) to that URL. When `listing_href` is null/non-http, there is no navigable listing control (do not wrap raw non-http `job_link` in `<a>`). Editable mode still edits the `job_link` column via the existing input; save path unchanged.

1. In `src/ui/frontend/src/components/JobDetailModal.tsx`, on the `JobDetail` interface, add:

```ts
listing_href?: string | null
```

2. In the same file, add the same `httpListingHref` helper as Stage 1 (duplicate the four-line function — new shared util files are out of Scope).

3. In the Summary panel Link block (today: editable `draft.job_link` input vs read-only `<a href={job.job_link}>`), replace with:

   - Compute once in the summary render path: `const listingHref = httpListingHref(job.listing_href)`.
   - **When `fieldsEditable && draft`:** keep the existing labeled **Link** text input bound to `draft.job_link` / `onDraftChange({ job_link })` (column edit — out of scope to change). Immediately after that input row, if `listingHref` is non-null, render a second row:

     ```tsx
     <div className="modal-detail-row">
       <span className="modal-detail-label">Open listing</span>
       <span>
         <a href={listingHref} target="_blank" rel="noopener noreferrer">{listingHref}</a>
       </span>
     </div>
     ```

   - **When not editable:** if `listingHref` is non-null, render:

     ```tsx
     <div className="modal-detail-row">
       <span className="modal-detail-label">Link</span>
       <span>
         <a href={listingHref} target="_blank" rel="noreferrer">{listingHref}</a>
       </span>
     </div>
     ```

     If `listingHref` is null, render **no** Link row (do not fall back to `job.job_link` as an `<a>`).

⚠️ **Decision:** Editable mode keeps the `job_link` input (write path) and adds a separate **Open listing** control from `listing_href` so BOT_BLOCKED / In Review / Skipped rows that are `fields_editable` still satisfy AC6 when the resolved URL exists but differs from (or is clearer than) the raw column. Read-only mode shows only the resolved navigable URL.

⚠️ **Decision:** Display text of the `<a>` is the `listingHref` string itself (same as today’s `job.job_link` display) — no new label copy beyond the **Open listing** row label in editable mode.

## Estimate

Confirm Chuckles estimate: 2 — agree

## AC → stage map

| AC (this child / parent) | Stage |
|--------------------------|-------|
| AC5 Recommended title `<a href="{listing}">` + Apply opens same URL | Stage 1 |
| AC6 Job Detail navigable listing for BOT_BLOCKED (and peers) when http(s) present | Stage 2 |
| Non-http → not navigable | Stage 1 + 2 (`httpListingHref`; no `job_link` fallback for open) |

Parent AC1–4 → AST-1693 / AST-1694. Out of scope here.

## Review

- **Publish ref:** `origin/sub/AST-1686/AST-1695-job-ui-listing-href`
- **Tip:** `92b13d2896d2aa755c90d34c3c7a0439a9b3c87d`
- **Stages:** 1 Recommended title+Apply `listing_href` · 2 Job Detail listing control

## Joan validate

[plan-rubric]
**Ticket:** AST-1695
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1686/AST-1695-job-ui-listing-href` @ `f269a1e5afdd3967657246b89a04d15717aaad6d`

### Canon scores

(no directives on frozen Canon Scope — parent partition: presentational / client-only; nothing to score)

### Traceability

AC5 → Stage 1 (`listing_href` on title `<a>` + CLIENT Apply `window.open` same URL); AC6 → Stage 2 (Job Detail read-only Link row + editable **Open listing** from `listing_href`); non-http → not navigable → Stage 1 + 2 (`httpListingHref`; no `job_link` fallback for open). Parent AC1–4 → AST-1693 / AST-1694 — N/A out of child Scope. Parent AC7 → satisfied by omission (no meteorite client resolve; consumes API field only).

### Findings

#### acceptable
- **Location:** Stage 2 — read-only `<a rel="noreferrer">`
- **Finding:** Read-only Job Detail link omits `noopener`; Stage 1 / header use `noopener noreferrer`.
- **Recommendation:** Align `rel` on implement if trivial; not blocking.

#### acceptable
- **Location:** Stages 1–2 — duplicate `httpListingHref`
- **Finding:** Same four-line helper copied into two files; no shared util per explicit scope gate.
- **Recommendation:** Accept for this child; extract later only if a third consumer appears.

### R6 checklist (summary)

- Definition fidelity: three Files Changed rows match ticket Scope exactly; no API/database/meteorite writer creep.
- AC coverage: AC5/AC6 mapped with done-when gates; AST-1694 `listing_href` dependency gated (stop comment if field missing post-sync).
- DRY / scope: no second React resolve path; no sibling scope bleed; belt-and-suspenders http filter at open sites only.
- Self-assessment: Estimate 2 — agree; stages are minimal and specific.

context_tokens≈52000

## Radia review

[code-rubric]

**Ticket:** AST-1695  
**Publish ref:** `eaafa9ed2a08b74da37048f02b029f1032fdfc28` (`origin/sub/AST-1686/AST-1695-job-ui-listing-href`)  
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`  
**Overall:** CLEAN

## Canon scores

(empty frozen Canon Scope — no directives to score; presentational / client-open only per issue doc and Joan validate)

## Column diff vs plan stage

no plan-stage canon scores attached (Joan: empty Canon Scope — aligned)

## Frame diff

(none)

## Findings

### discuss — sibling product code on publish ref (epic sync, not AST-1695 scope)

**Location:** `git diff origin/dev...origin/sub/AST-1686/AST-1695-job-ui-listing-href` — `src/core/consult.py`, `src/core/meteorite.py`, `src/core/tracker.py`, `src/data/database.py`, `src/ui/api/api_jobs.py`  
**Finding:** AST-1695 scope gate names only the three frontend components. This sub tip also carries merged sibling product work (AST-1693 writers, AST-1694 `listing_href` API) from `sync(ftr)` / epic integration. That is expected for UAT of `listing_href` on detail, but it is not AST-1695’s deliverable — attribute those files to their sibling tickets at `ftr` merge, not this child.  
**Recommendation:** Chuckles/downstream: partition sibling attribution in issue docs; AST-1695 review verdict applies to the three frontend files only.

### discuss — sibling test/doc nodes via `merge-tests`

**Location:** Diff includes AST-1692 Meteorite tab tests, AST-1696 Copy Link tests, AST-1691 `related_meteorite` API tests, sibling bible nodes, etc.  
**Finding:** Betty’s AST-1695 manifest (`docs/test-bible/frontend/components.md` § AST-1695) is correctly narrow (three component test files, `AST-1695` name pattern). **Tests Passed** is consistent. Full-module runs of merged sibling test suites may fail or assert product not on this ref until siblings land together on `ftr`.  
**Recommendation:** Keep manifest narrow at merge; reconcile sibling test nodes when siblings merge.

### advisory — duplicate `httpListingHref` helper

**Location:** `JobAnalysisReportModal.tsx`, `JobDetailModal.tsx`  
**Finding:** Same four-line helper copied per explicit scope gate (no shared util). Joan flagged acceptable at plan.  
**Recommendation:** None for this child; extract only if a third consumer appears.

### advisory — CLIENT `window.open` path not spy-tested

**Location:** `JobAnalysisReportModal.tsx` `runPrimaryAction` CLIENT branch; tests cover title `<a>` from `listing_href`  
**Finding:** Code correctly opens `httpListingHref(job.listing_href)` only (no `job_link` fallback). AST-1695 tests exercise title deeplink and null/non-http cases; no dedicated `window.open` spy when a CLIENT primary action is visible (many fixtures filter Apply from Artifacts). Low risk given mirrored `httpListingHref` and title coverage.  
**Recommendation:** Optional `resolve-child` or Betty follow-up if a state still surfaces Apply as CLIENT — not blocking.

### advisory — issue doc tip SHA stale

**Location:** `docs/features/meteorite/ast-1695-job-ui-listing-href.md` § Review  
**Finding:** Doc lists tip `92b13d28`; publish tip under review is `eaafa9ed` (`merge-tests`).  
**Recommendation:** Chuckles updates tip line when appending this review.

## What's solid

- **Stage 1:** `listing_href` on `JobDetail` type; `httpListingHref` helper; CLIENT branch opens filtered `listing_href` only; `RecommendedJobReportHeader` receives `httpListingHref(job.listing_href)`; prop comment documents AST-1694 contract; no `job_link` navigation fallback.
- **Stage 2:** `listingHref` from `listing_href`; read-only Link row only when http(s); editable mode keeps `job_link` input + optional **Open listing** row; no raw `job_link` `<a>` wrap.
- **Joan plan gap closed:** read-only Job Detail `<a>` now uses `rel="noopener noreferrer"` (was `noreferrer` only at plan).
- **AC7 / no second resolve:** no meteorite client fetch or `related_meteorite` logic in the three scoped components.
- **Dependency:** `listing_href` attach on `GET /api/jobs/<id>` present on tip (`api_jobs.py`) — AST-1694 dependency satisfied for UAT.
- **Tests:** AST-1695 nodes cover title prefer `listing_href` over stale `job_link`, null/non-http → plain title, Job Detail read-only BOT_BLOCKED, editable Open listing, header unit test; revised AST-948 fixtures use `listing_href`.
- **Estimate footprint:** Confirmed 2 — ~57 lines across three component files; proportionate.

## Recommended actions (downstream only — not executed here)

1. Chuckles: append artifact to issue doc, push `docs(AST-1695): Radia review — clean`, post slim upshot, move to **Review Posted**.
2. At `ftr` merge: attribute sibling `src/**` changes to AST-1693/AST-1694, not AST-1695.
3. Optional: CLIENT `window.open` spy test if a manifest state still exposes Apply (advisory).

context_tokens≈36000

---

```
[code-rubric] PROCEED (Commit: eaafa9ed) listing_href UI clean
```
