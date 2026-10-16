# AST-2233 — Report header chrome and triage actions (Updates to recommended job modal)

- **Linear:** [AST-2233](https://linear.app/astralcareermatch/issue/AST-2233) · parent [AST-2226](https://linear.app/astralcareermatch/issue/AST-2226)
- **Publish ref:** `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions`
- **Assignee:** Hedy

Presentational Recommended Job Report header + report-scoped CSS: strip every Copy control and header Print Resume/Cover; show `company_name` with `created_at` as `m/d/yy`; website URL on its own line under the job-link line; lifecycle date strip; Skip / Applied / conditional Generate in the former print action row; responsive stacking at ≤1023px; CSS class hooks for thermometers, total+gradable, and Discussion typography that AST-2234 mounts. Does not wire modal data, callbacks, or pane bodies — that is AST-2234 (#3). Prop names match the sibling #2 contract Ada’s plan already documents.

## UAT fitness

- **AC restored:** Parent AST-2226 functional scope this child owns: (1) remove every Copy control from the Recommended report header; (2) replace header Print Resume / Print Cover Letter with **Skip This Job** and **Applied to this Job** in the former print action row; (7) header shows `company_name` (never short_name alone) and job `created_at` as `m/d/yy`, with hyperlinked company website URL on its own line below the job-link line; (8) date strip shows discovered / recommended / applied (applied only when non-null); (9) phone-ready header stacks/wraps so title, dates, links, and Skip/Applied stay usable. Child AC 1–3 map to (1)(2)(9). CSS also lands thermometer / total-gradable / Discussion hooks for parent (13)/(5) chrome that #3 mounts.
- **Correct outcome:** On a Recommended report, the header has no Copy and no Print Resume/Cover; Skip and Applied (and Generate when the caller passes it) sit in `.recommended-report-header-actions`; company label is `companyName` with a `m/d/yy` date; website is a separate linked URL line under the job link; the date strip shows discovered + recommended always when props are set, and applied only when `appliedAt` is non-null; at ≤1023px Skip/Applied remain on-screen via wrap/stack (no horizontal clip).
- **Sibling check:** #1 (AST-2232) owns detail field shapes (`company_name`, `company_website`, lifecycle dates, `can_skip` / `can_apply`) — this ticket only accepts props with those shapes, no API. #3 (AST-2234) owns modal wiring and must pass the prop names in **Sibling prop contract** below; this ticket does not edit `JobAnalysisReportModal.tsx`. Verified by Files Changed listing only the two Scope files.
- **Not sufficient:** Hiding Copy behind CSS, leaving Print props unused but still in the header file, or stacking without also moving Skip/Applied into the action row.
- **Wrong fix rejected:** Keeping Copy/Print prop names as unused optionals so `JobAnalysisReportModal` keeps typechecking (child AC1/AC2 greps forbid those names in the header file); linking `companyName` to the website (today’s pattern) instead of a separate website URL line; hard-coding skip/apply legality inside the header (caller passes callbacks only when legal).

## Explicit scope gate

Ticket **## Scope** (only surfaces this plan may touch):

| File | Kind of change Scope allows |
|------|-----------------------------|
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | **modified** — drop all Copy controls and header Print Resume/Cover; show company_name + created_at; website line under job link; date strip; Skip / Applied / conditional Generate; responsive stacking |
| `src/ui/frontend/src/App.css` | **modified** — report-scoped header responsive rules, date strip, thermometer track/fill (green on neutral), Analysis total+gradable row, Discussion header typography as needed. No shared `.modal-title` / `.modal-header` / `.modal-body` contract break for unrelated modals |

Every **Files Changed** row and Stage step names only those files / that kind of change. No modal, no lib helpers, no backend, no `tests/`.

## Canon Scope (patterns read at plan)

Ticket Citations: **none** — pure presentational React/CSS. No pattern bodies to expand at plan. Placement stays inside the two Scope files above.

Every other directive id stays **id-only** until build-child §8 (none listed).

## Sibling prop contract (Hedy implements; Ada calls)

Frozen names for AST-2234. Do not invent alternate names.

| Prop | Rule |
|------|------|
| `jobTitle`, `jobLink`, `jobLinkText` | unchanged (job-link line behavior from AST-1873) |
| `companyName` | display label; never derive from website |
| `companyWebsite` | when non-empty, render as its own `<a target="_blank" rel="noopener noreferrer">` **below** the job-link line; link text = the URL string |
| `discoveredAt`, `recommendedAt`, `appliedAt` | `string \| null` (ISO or parseable); format each present value as `m/d/yy` via `Intl.DateTimeFormat("en-US", { year: "2-digit", month: "numeric", day: "numeric" })` with no forced timeZone (header has no candidate context). `discoveredAt` also supplies the company-line date (parent AC7 `created_at` = discovered). Omit applied strip line when `appliedAt` is null/empty |
| `onSkip` / `skipBusy` | **Skip This Job** in action row only when `onSkip` is passed |
| `onApplied` / `appliedBusy` | **Applied to this Job** in action row only when `onApplied` is passed |
| `onGenerateArtifacts` / `generateBusy` | **Generate Artifacts** in action row only when `onGenerateArtifacts` is passed |
| **Omit from file** | every Copy prop/control (`onCopyDetailLink`, `onCopySnapshot`, `onCopyApplicationEmail`, `onCopyLinkedIn`, `applicationEmail`, `linkedInUrl`, `copyFeedback`, `detailLinkCopied`, `snapshotCopied`, `snapshotCopying`) and every header Print prop (`showPrintResume`, `showPrintCover`, `onPrintResume`, `onPrintCover`) |

CSS class hooks #3 mounts (styles in this ticket’s `App.css`):

- `recommended-report-thermometer`, `recommended-report-thermometer-track`, `recommended-report-thermometer-fill`
- `recommended-report-total-gradable`
- Discussion: style `.recommended-report-section-list` / section label typography under the report shell as needed (no new component)

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Replace Props/JSX: no Copy/Print; company + date; website line; date strip; Skip/Applied/Generate action row | ui |
| `src/ui/frontend/src/App.css` | Header responsive + date strip; thermometer green-on-neutral; total-gradable row; Discussion typography; no edits inside shared `.modal-title` / `.modal-header` / `.modal-body` rule blocks | ui |

**Out of scope (do not touch):** `JobAnalysisReportModal.tsx`, `recommendedJobReport.tsx`, `JobDiscussionPane.tsx`, backend, `tests/`, `docs/test-bible/`.

⚠️ **Decision:** Removing Copy/Print props from the header interface will make the existing `JobAnalysisReportModal` call site fail `tsc -b` / `npm run build` until AST-2234 updates that call site. Do **not** edit the modal to silence it (Boundaries / Scope). Stage Done-when uses AC greps + header-file soundness + CSS diffs — not a green full-package frontend build. If a pre-commit hook blocks the product commit solely on that modal type error, stop and comment on AST-2233 (process blocker), do not expand Files Changed.

---

## Stage 1: Header component — chrome and triage actions

**Done when:** `RecommendedJobReportHeader.tsx` has no Copy or header Print controls/props (AC greps below return nothing); action row shows **Skip This Job** / **Applied to this Job** / optional **Generate Artifacts** when those callbacks are passed; title block order is title → job-link line → website URL line (when `companyWebsite`) → company name + `discoveredAt` as `m/d/yy`; date strip shows Discovered / Recommended / Applied (Applied only when `appliedAt` set). File has no TypeScript errors of its own.

1. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`, replace the `Props` interface with exactly:

   ```tsx
   interface Props {
     jobTitle: string
     /** AST-1694 listing_href — hyperlink target for the job-link line; only http(s) values are linked. */
     jobLink: string | null
     /** Job-link line display text (AST-1873); falls back to jobLink when absent. */
     jobLinkText?: string | null
     companyName: string
     companyWebsite: string | null
     /** Job created_at / date discovered (ISO). Also used for the company-line m/d/yy. */
     discoveredAt?: string | null
     recommendedAt?: string | null
     appliedAt?: string | null
     onSkip?: () => void
     skipBusy?: boolean
     onApplied?: () => void
     appliedBusy?: boolean
     onGenerateArtifacts?: () => void
     generateBusy?: boolean
   }
   ```

2. Add a tiny local helper in the same file (above the component):

   ```tsx
   function formatReportDate(value: string | null | undefined): string | null {
     const raw = value?.trim()
     if (!raw) return null
     const d = new Date(raw)
     if (Number.isNaN(d.getTime())) return null
     return new Intl.DateTimeFormat("en-US", {
       year: "2-digit",
       month: "numeric",
       day: "numeric",
     }).format(d)
   }
   ```

3. Replace the component body: keep the existing `link` / `href` job-link logic; destructure only the new Props; return this structure (class names fixed):

   ```tsx
   <div className="recommended-report-header">
     <div className="recommended-report-header-row">
       <div className="recommended-report-title-block">
         <span className="recommended-report-title"><JobTitleText title={jobTitle} fallback={jobTitle} /></span>
         {/* job-link line — same http(s) link vs plain text as today */}
         {/* website line: if companyWebsite trimmed, <div className="recommended-report-website-line"><a className="recommended-report-website-link" href=… target="_blank" rel="noopener noreferrer">{url}</a></div> */}
         {/* company line: <div className="recommended-report-company-line"><span className="recommended-report-company">{companyName}</span>{discovered formatted ? <span className="recommended-report-company-date"> · {date}</span> : null}</div> */}
       </div>
     </div>
     {(onSkip || onApplied || onGenerateArtifacts) && (
       <div className="recommended-report-header-actions">
         {onSkip && (
           <button type="button" className="btn secondary" onClick={() => onSkip()} disabled={skipBusy}>
             Skip This Job
           </button>
         )}
         {onApplied && (
           <button type="button" className="btn secondary" onClick={() => onApplied()} disabled={appliedBusy}>
             Applied to this Job
           </button>
         )}
         {onGenerateArtifacts && (
           <button type="button" className="btn secondary" onClick={() => onGenerateArtifacts()} disabled={generateBusy}>
             Generate Artifacts
           </button>
         )}
       </div>
     )}
     {(formatReportDate(discoveredAt) || formatReportDate(recommendedAt) || formatReportDate(appliedAt)) && (
       <div className="recommended-report-date-strip">
         {/* each present date as <span className="recommended-report-date-strip-item">Date discovered {d}</span> etc.; Applied item only when appliedAt formats */}
       </div>
     )}
   </div>
   ```

4. Delete the old `.recommended-report-links` Copy row and the Print Resume/Cover block entirely. Delete every unused import if any.

5. Update the file doc comment to mention AST-2233 (triage actions, no Copy/Print).

6. Self-check greps from repo root — both must return **nothing**:

   ```bash
   grep -nE 'Copy Job Link|Copy Job JSON|Copy Application Email|Copy LinkedIn|onCopyDetailLink|onCopySnapshot|onCopyApplicationEmail|onCopyLinkedIn' src/ui/frontend/src/components/RecommendedJobReportHeader.tsx
   grep -n 'Print Resume\|Print Cover' src/ui/frontend/src/components/RecommendedJobReportHeader.tsx
   ```

7. Commit: `code(AST-2233): header triage actions, no Copy/Print`. Publish to `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions`.

⚠️ **Decision:** Company line is plain `companyName` + optional ` · m/d/yy` from `discoveredAt`. Website is never the company-name link (replaces today’s `companyWebsite ? <a>{companyName}</a>` pattern). Button labels use parent Title Case (**Skip This Job**).

Existing component tests that assert Copy/Print/company-as-website-link are expected to fail until Betty’s `qa-child`. Do not edit `tests/`.

---

## Stage 2: Report-scoped CSS — responsive header + pane hooks

**Done when:** At `max-width: 1023px`, `.recommended-report-header-row` stacks and `.recommended-report-header-actions` wraps so Skip/Applied stay reachable; date strip and website line have report-scoped rules; thermometer is green fill on neutral track; total-gradable and Discussion typography hooks exist; `git diff origin/dev -- src/ui/frontend/src/App.css` shows no edits inside the existing shared `.modal-title`, `.modal-header`, or `.modal-body` rule **blocks** (report-scoped `:has(.recommended-report-shell)` rules may remain as today).

1. In `src/ui/frontend/src/App.css`, near the existing `.recommended-report-header*` rules (~1010+):

   - Add `.recommended-report-website-line` / `.recommended-report-website-link` (secondary text size like job-link; underline link).
   - Add `.recommended-report-company-line` / `.recommended-report-company-date` (date secondary).
   - Add `.recommended-report-date-strip` + `.recommended-report-date-strip-item` (compact row, wrap, gap, secondary font ~12px).
   - Keep `.recommended-report-header-actions` as flex wrap; ensure `gap` ≥ 8px.
   - Inside the existing `@media (max-width: 1023px)` block (or a new report-scoped nested media under header rules), set:
     - `.recommended-report-header-row { flex-direction: column; align-items: stretch; }`
     - `.recommended-report-header-actions { width: 100%; justify-content: flex-start; }`
     - `.recommended-report-links` may stay unused; no need to delete the rule.

2. Add thermometer + total-gradable (green on neutral — use theme tokens, not raw purple/glow):

   ```css
   .recommended-report-thermometer { /* block under phase header; full width of pane column */ }
   .recommended-report-thermometer-track {
     height: 8px;
     border-radius: 4px;
     background: var(--border-subtle, var(--border));
     overflow: hidden;
   }
   .recommended-report-thermometer-fill {
     height: 100%;
     background: var(--success, #3d8f5a); /* green; fall back if token missing */
     border-radius: 4px;
   }
   .recommended-report-total-gradable {
     display: flex;
     flex-wrap: wrap;
     align-items: baseline;
     gap: 8px;
     margin: 8px 0;
     font-weight: 600;
   }
   ```

   ⚠️ **Decision:** Prefer an existing success/green token if one is already used in `App.css` for positive scores; only then use the hex fallback. Do not introduce a new purple accent.

3. Discussion typography: under the report shell, ensure section labels in `.recommended-report-section-list` (or the class `JobDiscussionPane` / `ReportSectionList` already emit) are readable at ~13–14px weight 600, with enough line-height for long `agent_name's task @ stamp` strings. Do not change shared modal chrome blocks.

4. Confirm with:

   ```bash
   git diff origin/dev -- src/ui/frontend/src/App.css | grep -E '^\+.*\.(modal-title|modal-header|modal-body)\s*\{' || true
   ```

   That must print nothing for **unscoped** shared blocks. Report-scoped selectors like `.modal-card:has(.recommended-report-shell) .modal-title` may already exist from AST-1873 — leave them; do not edit the bare `.modal-title {…}` block body.

5. Commit: `code(AST-2233): report header responsive + thermometer CSS`. Publish to `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions`.

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files outside **Files Changed**.
- When a step is ambiguous or the codebase has drifted — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, then `git push origin HEAD:sub/AST-2226/AST-2233-report-header-chrome-triage-actions`.

## Estimate

Confirm Chuckles estimate: 3 — agree
