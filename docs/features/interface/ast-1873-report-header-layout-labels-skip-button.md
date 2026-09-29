# AST-1873 — Report header layout, labels, job-link line, Skip button (Recommended Job Modal Changes)

- **Linear:** [AST-1873](https://linear.app/astralcareermatch/issue/AST-1873) · parent [AST-1862](https://linear.app/astralcareermatch/issue/AST-1862) — Recommended Job Modal Changes
- **Publish ref:** `sub/AST-1862/AST-1873-report-header-layout-labels-skip-button` (origin only)
- **Canon Scope:** `astral.standards.dry-and-focused-functions`

This ticket covers the presentation layer of the Recommended Job Report header. The copy buttons move onto the job-title row: the title column wraps, and the button column does not shrink. The title becomes plain text, with a small job-link line directly below it. That line is hyperlinked in a new tab only when an http(s) href is present. **Copy Link** / **Copy** become **Copy Job Link** / **Copy Job JSON**. A new optional skip callback renders **Skip this Job** as the last button in the row. The modal's company-name title bar gets a smaller font and a tighter gap, and that change applies to this modal only. Wiring data or the skip action into `JobAnalysisReportModal.tsx` belongs to AST-1874 (#3). Config and API work belongs to AST-1872 (#1).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Title-row layout (title block + button row in one row), plain title, job-link line (display text + optional http href), renamed labels, optional `onSkip` / `skipBusy` → **Skip this Job** | ui |
| `src/ui/frontend/src/App.css` | Two-column title row, title-block wrap rule, job-link-line rule, non-shrinking button column, report-modal-scoped title bar font + tighter gap | ui |

No other file is touched. `JobAnalysisReportModal.tsx`, `Modal.tsx`, and every `tests/` / `docs/test-bible/` file are out of scope.

## Stage 1: Header component

**Done when:** `RecommendedJobReportHeader` renders the title as plain text, with the job-link line directly below it. The copy/skip button row sits inside `.recommended-report-header-row`, the same container as the title. Labels read **Copy Job Link** / **Copy Job JSON** and still switch to **Copied**. **Skip this Job** renders last among the buttons only when `onSkip` is passed. `npm run build` and `npm run lint` pass with `JobAnalysisReportModal.tsx` unedited.

⚠️ **Decision: keep the existing `jobLink` prop and add an optional `jobLinkText`. Do not rename to a new text/href pair.** `JobAnalysisReportModal.tsx` belongs to #3, and it currently passes `jobLink={httpListingHref(job.listing_href)}`. Renaming or removing `jobLink` would break `tsc -b` on this branch until #3 lands. With this design, `jobLink` stays the href source: it is hyperlinked only when it is http(s), matching today's AST-1694/AST-1704 contract. `jobLinkText` is the display text #3 will pass: `listing_href` when it is http(s), else the raw `job_link`. When `jobLinkText` is absent, the display text falls back to `jobLink`. Until #3 wires it, the modal shows the http `listing_href` as a linked URL under the title. The two alternatives were rejected. Renaming the props needs a modal edit, which is out of scope. Deriving `job_link` inside the header would push data logic into the presentational component, which is #3's scope.

⚠️ **Decision: order in the title block is title, then the job-link line, then company.** Parent functional scope #6 says the link appears "directly below" the title.

1. Update the `Props` interface in `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`:
   - Replace the `jobLink` doc comment with `/** AST-1694 listing_href — hyperlink target for the job-link line; only http(s) values are linked. */`. Keep the type `string | null`.
   - Add `jobLinkText?: string | null` directly after `jobLink`, with the doc comment `/** Job-link line display text (AST-1873); falls back to jobLink when absent. */`.
   - Add `onSkip?: () => void` and `skipBusy?: boolean` directly after `snapshotCopying?: boolean`.
2. Add `jobLinkText`, `onSkip`, and `skipBusy` to the destructured parameters, in the same positions as in the interface.
3. Replace the `link` / `httpLink` block (current lines 44–48) with:

   ```tsx
   // Display text prefers the caller's jobLinkText; the href is jobLink only when http(s).
   const link = jobLinkText?.trim() || jobLink?.trim() || null
   const rawHref = jobLink?.trim() ?? ""
   const href = /^https?:\/\//i.test(rawHref) ? rawHref : null
   ```

4. Replace the whole returned JSX up to, but not including, the `{(showPrintResume || showPrintCover) && (` print-actions block with this structure. The print-actions block and the closing `</div>` stay byte-identical.

   ```tsx
   <div className="recommended-report-header">
     {/* Title block (left, wraps) and button row (right, no shrink) share one row. */}
     <div className="recommended-report-header-row">
       <div className="recommended-report-title-block">
         <span className="recommended-report-title">{jobTitle}</span>
         {link && (
           <div className="recommended-report-job-link-text">
             {href ? (
               <a href={href} target="_blank" rel="noopener noreferrer">
                 {link}
               </a>
             ) : (
               link
             )}
           </div>
         )}
         {companyWebsite ? (
           /* existing company <a className="recommended-report-company-link"> — unchanged */
         ) : (
           /* existing <span className="recommended-report-company"> — unchanged */
         )}
       </div>
       {(onCopyDetailLink || onCopySnapshot || applicationEmail || linkedInUrl || onSkip) && (
         <div className="recommended-report-links">
           {/* Copy Job Link button: existing, label -> {detailLinkCopied ? "Copied" : "Copy Job Link"} */}
           {/* Copy Job JSON button: existing, label -> {snapshotCopied ? "Copied" : "Copy Job JSON"} */}
           {/* Copy Application Email button: unchanged */}
           {/* Copy LinkedIn Profile button: unchanged */}
           {onSkip && (
             <button
               type="button"
               className="btn secondary"
               onClick={() => onSkip()}
               disabled={skipBusy}
             >
               Skip this Job
             </button>
           )}
           {/* copyFeedback span: unchanged, stays after Skip (not a button) */}
         </div>
       )}
     </div>
     {/* print-actions block unchanged */}
   </div>
   ```

   - The title is always `<span className="recommended-report-title">`. The `<a className="recommended-report-title-link">` title branch is deleted. Keep the `.recommended-report-title-link` CSS rule, because `JobMeteoritePane.tsx` and `MeteoriteDetailModal.tsx` still use it.
   - The old standalone `{link && !httpLink && (<div className="recommended-report-job-link-text">…)}` line below the row is deleted. The new link line in the title block replaces it, and the class name is reused.
   - The copy buttons keep their existing `onClick`, `disabled`, and `title` attributes. Only the two label strings change.
5. Update the component doc comment to `/** Sticky Recommended Job Report header — title row with copy/skip buttons, job-link line, print (AST-948, AST-1873). */`.
6. Validate in `src/ui/frontend/`. Run `npm ci` first only if `node_modules/` is absent; never commit it. Then run `npm run build` and `npm run lint`, and both must pass.
7. Self-check greps, run from the repo root. Both must return nothing:
   - `grep -n '"Copy Link"\|>Copy<\|"Copy"' src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`
   - `grep -n "CANDIDATE_REVIEW\|REVIEW_LIKE" src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`
8. Commit `code(AST-1873): header title row, job-link line, copy labels, Skip button`, then publish with `git push origin HEAD:sub/AST-1862/AST-1873-report-header-layout-labels-skip-button`.

Existing component tests that assert the title `<a>`, **Copy Link** / **Copy**, or the old link-line position are expected to fail after this stage. They belong to Betty's `qa-child`, per the parent's Component scope note. Do not edit `tests/`.

## Stage 2: CSS

**Done when:** in the Recommended report, the buttons sit right of the title on one row, and a long title wraps without pushing under or clipping them. The job-link line is small secondary text. The company-name title bar is 15px, with a tighter gap above the job title. The Company and Job Detail modals are unchanged. `git diff origin/dev -- src/ui/frontend/src/App.css` shows no edits inside the existing `.modal-title`, `.modal-header`, or `.modal-body` blocks.

⚠️ **Decision: scope the title bar with `.modal-card:has(.recommended-report-shell)`.** `Modal.tsx` renders `.modal-header` / `.modal-title` without any per-caller class hook. `Modal.tsx` is out of scope for the parent, and `JobAnalysisReportModal.tsx` belongs to #3. That makes a content-scoped selector the only in-scope way to target this modal. `.recommended-report-shell` is rendered only by `JobAnalysisReportModal.tsx`. `.modal-card--wide` was rejected because other wide modals share it. Stacked modals portal to their own `.modal-overlay`, so they never match. `:has()` is supported in current Chrome, Safari, and Firefox.

⚠️ **Decision: gap numbers.** The ticket assumes 16px header bottom padding, plus 20px body top padding, plus 12px report header top padding. On this modal, `.modal-card--wide .modal-body` (App.css ~line 2160) already sets `padding: 0`, so the real gap is 16 + 0 + 12 = 28px. The plan cuts the header bottom padding to 8px and the report header top padding to 6px, for a 14px total. It also trims the header top padding to 10px. The title font goes from 18px to 15px.

1. In `src/ui/frontend/src/App.css`, section `/* === 8d. Recommended Job Report (AST-565) === */`, insert these rules directly after the `.recommended-report-chrome { … }` block:

   ```css
   /* AST-1873: report-modal-only title bar. Modal.tsx has no class hook, so scope by content. */
   .modal-card:has(.recommended-report-shell) .modal-header {
     padding-top: 10px;
     padding-bottom: 8px;
   }

   .modal-card:has(.recommended-report-shell) .modal-title {
     font-size: 15px;
   }
   ```

2. In `.recommended-report-header`, change `padding: 12px 16px 14px;` to `padding: 6px 16px 14px;`. This class is rendered only by `RecommendedJobReportHeader`.
3. Replace the `.recommended-report-header-row` block with the block below, then add `.recommended-report-title-block` immediately after it:

   ```css
   .recommended-report-header-row {
     display: flex;
     flex-direction: row;
     align-items: flex-start;
     justify-content: space-between;
     gap: 12px;
     margin-bottom: 6px;
   }

   /* Title/link/company column: shrinks and wraps so long titles never slide under the buttons. */
   .recommended-report-title-block {
     display: flex;
     flex-direction: column;
     align-items: flex-start;
     gap: 4px;
     flex: 1 1 auto;
     min-width: 0;
     overflow-wrap: anywhere;
     word-break: break-word;
   }
   ```

4. Insert these rules directly after the `.recommended-report-company-link:hover` block:

   ```css
   .recommended-report-job-link-text {
     font-size: 12px;
     color: var(--text-secondary);
   }

   .recommended-report-job-link-text a {
     color: inherit;
     text-decoration: underline;
   }

   .recommended-report-job-link-text a:hover {
     color: var(--accent-gold);
   }
   ```

5. In the `.recommended-report-links` block, change `margin-top: 8px;` to `margin-top: 0;`. Add `justify-content: flex-end;` and `flex-shrink: 0;`. Leave the other declarations unchanged.
6. Do not edit the `.modal-header`, `.modal-title`, `.modal-body`, `.modal-card--wide .modal-body`, `.recommended-report-title`, or `.recommended-report-title-link` blocks.
7. Validate in `src/ui/frontend/` with `npm run build` and `npm run lint`, and both must pass. Then check `git diff origin/dev -- src/ui/frontend/src/App.css`: no hunk may sit inside the existing `.modal-title`, `.modal-header`, or `.modal-body` rule blocks.
8. Commit `code(AST-1873): report header title-row CSS and scoped title bar`, then publish with `git push origin HEAD:sub/AST-1862/AST-1873-report-header-layout-labels-skip-button`.

## Canon check

- `astral.standards.dry-and-focused-functions`: the single job-link line replaces the old duplicate title-link and crumb-text branches. The href test is one inline check, and no new helpers are needed at this size. The Skip button follows the existing `.btn secondary` idiom, and no duplicate button component is introduced.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1873
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1862/AST-1873-report-header-layout-labels-skip-button` @ `d818add5b32340b6fcc683b896deeab4f04698bc`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.standards.dry-and-focused-functions | A | | |

## Traceability

AC6→Stage1 (header `onSkip`/last-in-row; modal flag wiring N/A—AST-1874); AC7→Stage1; AC8→Stages1+2; AC9→Stage1 (`jobLink`/`jobLinkText`); AC10→Stage2 (`:has(.recommended-report-shell)` + padding/font).

### Findings

- **discuss** — Child **AC6** / `## Traceability` · Finding: AC6 text still names `test_JobAnalysisReportModal.test.tsx` skip visibility, but this child’s boundaries correctly defer modal wiring to #3; Stage 1 only supplies props/UI. · Recommendation: Ensure Betty’s `qa-child` manifest for AST-1873 scopes AC6 modal asserts to #3 (or stubs) so this ticket is not blocked on skip-legality wiring not in Files Changed.

- **acceptable** — Plan **Stage 1** interim UX · Finding: Until #3 passes `jobLinkText`, the link line shows http `listing_href` only (documented decision). · Recommendation: None for this plan; matches partition with #3.

- **acceptable** — Plan **Canon check** · Finding: Self-assessment names concrete DRY wins (merged title/link branches, no duplicate button component). · Recommendation: None.

context_tokens≈18500

## Review

- **Code commits on `origin/sub/AST-1862/AST-1873-report-header-layout-labels-skip-button`:** `a54c6d9f` (Stage 1, header component) and `1d8e84ca` (Stage 2, CSS).
- **Diff:** 2 files, both listed in Files Changed. `JobAnalysisReportModal.tsx` and `Modal.tsx` were not edited. There are no deviations from the plan.
- **Checks:** `npm run build` (`tsc -b` plus vite) is clean. `eslint` is clean on `RecommendedJobReportHeader.tsx`. Full `npm run lint` reports 32 problems, and the pre-build tree reports the same 32, so none are new. Both Stage 1 greps return nothing. The built CSS keeps both `.modal-card:has(.recommended-report-shell)` selectors. Every `App.css` hunk falls within lines 774–880, clear of the shared `.modal-*` blocks at line 966 and below.
- **Existing tests (read-only run, for Betty's `qa-child`):** `test_RecommendedJobReportHeader` plus `test_JobAnalysisReportModal` have 16 failures. Three also fail on the pre-build tree: AST-1546 Print Resume success, AST-1350 Print Resume unsupported toast, and AST-1704 modal breadcrumb. The other 13 are expected revisions: they assert the old **Copy Link** / **Copy** labels or the linked title `<a>` (AST-948, AST-1421, AST-1695, AST-1696, AST-1704 header).
- **Sub-log validator:** `validate-sub-log --stage=build` blocks on `075c3d78 Merge remote-tracking branch 'origin/dev' into tmp-refresh-AST-1853…`. That commit comes from origin/dev (AST-1853 PR #189) through the mandatory `sync(dev)`, and it isn't on `origin/ftr/AST-1862` yet. The plan commit `d818add5` is already on ftr, which puts it outside the range the validator checks. Both clear once ftr absorbs current dev.
