# AST-1696 — Copy detail deeplink from report header

- **Linear:** [AST-1696](https://linear.app/astralcareermatch/issue/AST-1696/copy-detail-deeplink-from-report-header-copy-single-page-access-link)
- **Parent:** [AST-1687](https://linear.app/astralcareermatch/issue/AST-1687/copy-single-page-access-link-from-recommended-job-modal) — Copy single page access link from recommended job modal
- **Publish ref:** `sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header`

Adds a labeled **Copy Link** control on the Recommended Job Report header that copies the absolute authenticated detail URL (`origin` + `/jobs/detail/<jobId>`) for the open modal job to the clipboard, with the same brief **Copied** feedback used by the existing diagnostic Copy control. Reuses the shipped AST-1463 / AST-1481 deeplink host — does not add routes, change auth, or alter other header copy/print actions.

## UAT fitness

- **AC restored:** Parent AST-1687 AC 1–5 (mirrored on this child): (1) with modal open for job `J`, link-copy puts absolute URL whose path is exactly `/jobs/detail/J` on the clipboard; (2) control reads Copied briefly then idle label; (3) opening that URL while authenticated opens the same Recommended Job Report modal (existing AST-1463 behavior); (4) Diagnostic Copy, Copy Application Email, Copy LinkedIn Profile, Print Resume, and Print Cover Letter still appear and behave as before when their data is present; (5) no new unauthenticated/public job-report route beyond existing `/jobs/detail/:jobId`.
- **Correct outcome:** Operator opens a Recommended Job Report, clicks **Copy Link**, pastes an absolute same-origin URL ending in `/jobs/detail/<that job's id>`, and that URL reopens the same report modal when authenticated.
- **Sibling check:** AST-1481 `JobsJobDetail` deeplink host and `routes.tsx` `jobs/detail/:jobId` stay untouched — verified by not listing them in Files Changed and by AC 3 relying on existing behavior. Existing header copy/print controls (AST-1421 snapshot Copy; email / LinkedIn; print) keep their labels, handlers, and conditional visibility — new control is additive.
- **Not sufficient:** Removing an error / adding a dead button that does not write the absolute `/jobs/detail/<id>` URL, or only showing a relative path.
- **Wrong fix rejected:** Inventing a second public/detail route or touching `JobsJobDetail.tsx` / auth return-path; replacing or relabeling Diagnostic Copy / email / LinkedIn as the link control; exposing a new path string in `config.py` when the frontend already stays in SYNC with `JOBS_DETAIL_ROUTE_PREFIX` via the literal `/jobs/detail/` used by `routes.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Add optional link-copy callback + copied-state props; render `.btn secondary` **Copy Link** in `recommended-report-links`; include the new callback in the row visibility condition | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Assemble absolute detail URL from open `jobId`; clipboard write + 2s Copied state; pass props into the header; reset copied state when `jobId` changes | ui |

**Do not touch:** `src/ui/frontend/src/pages/JobsJobDetail.tsx`; `src/ui/frontend/src/routes.tsx`; `src/utils/config.py`; `RequireAuth` / auth return-path; Diagnostic Copy / email / LinkedIn / print handlers or labels (except coexistence); report tabs / load / primary actions; `tests/**`; `docs/test-bible/**`.

## Stage 1: Header Copy Link control

**Done when:** `RecommendedJobReportHeader` accepts optional `onCopyDetailLink` and `detailLinkCopied` props, renders a `.btn secondary` labeled **Copy Link** (reads **Copied** when `detailLinkCopied` is true) inside the existing `recommended-report-links` row, and the links row is visible whenever `onCopyDetailLink` is provided even if snapshot / email / LinkedIn are absent.

1. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, extend `Props` with:
   - `onCopyDetailLink?: () => void`
   - `detailLinkCopied?: boolean`
2. Destructure those props in the component signature (same style as `onCopySnapshot` / `snapshotCopied`).
3. Change the links-row visibility condition from `(onCopySnapshot || applicationEmail || linkedInUrl)` to `(onCopyDetailLink || onCopySnapshot || applicationEmail || linkedInUrl)` so the new control can stand alone.
4. Inside `recommended-report-links`, **before** the diagnostic Copy button, render:

```tsx
{onCopyDetailLink && (
  <button
    type="button"
    className="btn secondary"
    onClick={() => onCopyDetailLink()}
  >
    {detailLinkCopied ? "Copied" : "Copy Link"}
  </button>
)}
```

⚠️ **Decision:** Idle label is **Copy Link** (parent Component scope “Copy Link (or equivalent)”). Feedback label is **Copied**, matching the snapshot Copy control — not the separate `copyFeedback` span used by email/LinkedIn.

5. Do not change title/company links, print actions, email/LinkedIn buttons, snapshot Copy button, or the `copyFeedback` span.

## Stage 2: Modal URL assembly and clipboard wiring

**Done when:** With `JobAnalysisReportModal` open for a non-null `jobId`, clicking **Copy Link** writes `window.location.origin + "/jobs/detail/" + encodeURIComponent(jobId)` to the clipboard, the header shows **Copied** for ~2 seconds then **Copy Link** again, and a failed clipboard write leaves the label unchanged (no toast). Existing header actions still receive the same props as today.

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, add state next to `snapshotCopied`:

```tsx
const [detailLinkCopied, setDetailLinkCopied] = useState(false)
```

2. Add a reset effect beside the existing `setSnapshotCopied(false)` on `jobId` change:

```tsx
useEffect(() => { setDetailLinkCopied(false) }, [jobId])
```

3. Add handler (near `handleCopySnapshot` / email / LinkedIn handlers):

```tsx
function handleCopyDetailLink() {
  if (!jobId) return
  const url =
    `${window.location.origin}/jobs/detail/${encodeURIComponent(jobId)}`
  navigator.clipboard.writeText(url).then(() => {
    setDetailLinkCopied(true)
    window.setTimeout(() => setDetailLinkCopied(false), 2000)
  })
}
```

⚠️ **Decision:** Use the open modal’s `jobId` prop (already the deeplink id) and the literal path prefix `/jobs/detail/` — same string as `routes.tsx` / `JOBS_DETAIL_ROUTE_PREFIX`. Do **not** edit `config.py` or invent a second path. Clipboard rejection is silent (no `.catch` toast) per parent Functional scope.

4. On the `<RecommendedJobReportHeader … />` call site, pass:
   - `onCopyDetailLink={handleCopyDetailLink}`
   - `detailLinkCopied={detailLinkCopied}`
   Leave every other header prop unchanged.

5. Do not change report load, tabs, primary actions, snapshot/email/LinkedIn/print handlers, or navigate/route tables.

## Estimate

Confirm Chuckles estimate: 2 — agree
