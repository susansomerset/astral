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

## Joan validate

[plan-rubric]
**Ticket:** AST-2233
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91 (tree `canon/` at publish tip; no `docs/canon-index.md` on ref)
**Publish ref:** `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions` @ `024831014356a99c9536ceff3da1ca43129cb80c`

## Canon scores

_(Frozen Citations: none — no directive ids to score; Radia column is intentionally vacuous for this child.)_

## Traceability

AC 1 → Stage 1 (Props/JSX purge Copy; AC greps); AC 2 → Stage 1 (Skip/Applied/Generate action row; no Print Resume/Cover in header file); AC 3 → Stage 2 (≤1023px stack/wrap on `.recommended-report-header-*`). Parent functional (1)(2) → Stages 1–2; (7)(8) company line + website line + date strip → Stage 1 markup + Stage 2 CSS; (9) phone-ready header → Stage 2. Parent (13) thermometer / Discussion chrome hooks → Stage 2 CSS only (#3 mounts DOM). Wiring / `can_*` gating N/A — AST-2234.

## Findings

**acceptable** — Explicit scope gate, UAT fitness, sibling prop contract (frozen for AST-2234), and AC grep done-when match child Scope and Boundaries; two-stage split (header then CSS) is executable against current `RecommendedJobReportHeader.tsx` Copy/Print surface.

**acceptable** — Documented decision that full-package `tsc`/build may fail until AST-2234 updates `JobAnalysisReportModal` call site; Stage done-when does not require green modal compile — stop-and-comment if hooks block commit only on that mismatch.

**discuss** — Frozen canon list is explicitly empty (`Citations: none`); `astral.ui.frontend-file-placement` plainly governs new report-scoped rules in `App.css` but is not on the list — Archie may amend at Discussion; not scored here.

**discuss** — `formatReportDate` uses `Intl` without candidate `timeZone` (plan documents no candidate context in header); aligns with child AC 1–3 and parent AC7 `m/d/yy` on `created_at`/discovered prop — if Susan wants strip dates in candidate TZ, that is a product call for #2 or #3, not blocked by this plan text.

**discuss** — Execution contract stop comment targets parent AST-2226 while sibling plans use the child id; minor inconsistency only.

**Definition fidelity (R6):** Files Changed = two Scope files only; no modal/lib/backend. Estimate confirm present. Plan Discuss rounds on thread: 0.

context_tokens≈52000

## Review

- **Publish ref:** `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions`
- **Code tip:** `b4dba8d4a3a42bc92ef441ce7aabe65aefc44fd9`
- **Stages:** `code(AST-2233): header triage actions, no Copy/Print` · `code(AST-2233): report header responsive + thermometer CSS`
- **Notes:** Header Props drop Copy/Print; Skip/Applied/Generate in `.recommended-report-header-actions`; company + website line + date strip. CSS: ≤1023px stack, thermometer/total-gradable/Discussion hooks. Full-package `tsc` fails only on `JobAnalysisReportModal` excess props until AST-2234 (plan Decision).

## Radia review

[code-rubric]
**Ticket:** AST-2233
**Publish ref:** `origin/sub/AST-2226/AST-2233-report-header-chrome-triage-actions` @ `582cdfc7caa99d816f4df52ee7e6b3dbc7a5ed67`
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066`
**Overall:** CLEAN

## Canon scores

_(Frozen Citations: none — ticket Description lists no directive ids; nothing to score.)_

## Column diff vs plan stage

(vacuous — aligned) Joan recorded no canon rows at plan (`Frozen Citations: none`); code review has no canon column to diverge.

## Frame diff

(none)

## Findings

**fix-now**

(none)

**discuss**

- **Skipped modal Print Resume tests** — `test_JobAnalysisReportModal.test.tsx` marks AST-1546 / AST-1350 / AST-2084 Print Resume cases `.skip` while the header no longer exposes Print. @susan: Should those scenarios move to AST-2234’s manifest (modal-owned print path) rather than stay skipped on this sub?
  **Default:** Leave skipped until AST-2234 lands wiring; 2234 qa-child re-enables or replaces with modal-scoped asserts.

**advisory**

- **sibling product carry (AST-2232):** Three-dot diff vs `origin/dev` still includes `data/admin/agent.json`, `src/utils/config.py`, `src/core/{agent,tracker}.py`, `src/data/database.py`, `src/ui/api/api_jobs.py` from merged ftr lineage. AST-2233 **code** commits are only `RecommendedJobReportHeader.tsx` + `App.css` (`985861ff`, `b4dba8d4a`). UAT for this child should sign off header/CSS, not re-audit 2232 backend.
- **sibling test carry:** `tests/**` + `docs/test-bible/**` include Betty work for AST-2232 and AST-2233; `test_JobAnalysisReportModal.test.tsx` updates integration expectations for the new header chrome without editing `JobAnalysisReportModal.tsx` (plan boundary held).
- **Canon Scope (Archie):** Empty frozen list is intentional; `astral.ui.frontend-file-placement` / report-scoped `App.css` rules plainly apply but were not cited (Joan plan discuss) — not scored.
- **Corpus pin:** Joan plan corpus `65a2864…`; clerk at review tip `b7ab2203…` (`corpus_dirty: false`). Reproducible at current `canon/` tree.

## Plan fidelity (§5.4)

- **Scope gate:** Product diff for this ticket is the two Scope files only; no `JobAnalysisReportModal.tsx`, backend, or lib helpers.
- **AC 1–2:** Publish-ref header has no Copy/Print props or controls; Skip / Applied / Generate live in `.recommended-report-header-actions` with correct labels; `.recommended-report-links` removed.
- **AC 7–8:** Website is a separate URL line (`recommended-report-website-link`); `companyName` is plain text; `discoveredAt` formats on the company line and date strip; `appliedAt` omitted from strip when null.
- **AC 3 / Stage 2:** `@media (max-width: 1023px)` stacks `.recommended-report-header-row`; date strip, thermometer, total-gradable, and Discussion label typography hooks added without edits inside shared `.modal-title` / `.modal-header` / `.modal-body` rule blocks in this diff.
- **Sibling contract:** Prop names match the frozen table for AST-2234; `formatReportDate` uses documented `Intl.DateTimeFormat("en-US", …)` without `timeZone`.
- **Estimate 3:** Footprint matches (presentational header + scoped CSS + Betty tests).

## What's solid

- Header refactor reuses existing job-link http(s) logic and keeps triage callbacks optional (row omitted when no handlers).
- Component tests (`test_RecommendedJobReportHeader.test.tsx`) encode AC1–AC2 greps and website-vs-company separation clearly.
- Documented expectation that full-package `tsc` may fail on modal excess props until AST-2234 — engineer did not expand Files Changed to silence the modal.

## Recommended actions (downstream only — not taken in this session)

- Chuckles: append artifact, `docs(AST-2233): Radia review — clean`, push sub ref, post slim upshot `--as radia`, **Review Posted**.
- datt: **PROCEED** → **User Testing** for header/CSS; spawn **AST-2234** for modal wiring + build green.
- Betty (optional, 2234): Pick up skipped Print Resume modal tests per discuss Default.

## Bug: AST-2268 — Modal header identity, links, date labels

Items 5–7 only. Items 1–4 are in `docs/features/interface/ast-2234-modal-panes-and-wiring.md`.

### As-is

The modal chrome title falls back to the literal `Recommended Job Report`, and the report header's primary line is the job title (same fallback) instead of `company_name` plus job `created_at`. The job-link line and company website line are absent when `listing_href` is not http(s) even if `job_link` or `company_website` is set. The date strip reads `Date discovered` / `Date recommended` without the labels `Discovered:` and `Recommended:`.

### To-be

The modal title and the header identity show `company_name` and the job created date as `m/d/yy`. The job link and the company website are each their own line under that identity when those URLs exist. The date strip items read `Discovered: m/d/yy` and `Recommended: m/d/yy` (and `Applied: m/d/yy` only when applied).

### Repro

Open a Recommended job whose detail has `company_name` set, `discovered_at` / `created_at` set, `job_link` an http(s) URL, `listing_href` null or non-http, and `company_website` set. Modal `<h2 class="modal-title">` is `Recommended Job Report` or the job title, not `company_name` plus `m/d/yy`. No job-link `<a>` and no `.recommended-report-website-link`. Date strip text is `Date discovered …` rather than `Discovered: …`.

### Root cause

`JobAnalysisReportModal` sets `title={companyNameDisplay || "Recommended Job Report"}` and `jobTitle={job_title || company || "Recommended Job Report"}`, so a missing `company_name` or missing `job_title` surfaces that placeholder instead of `company_name` + created date. `jobLink` is only `httpListingHref(listing_href)`, so a usable `job_link` never becomes the href. The header date strip hard-codes `Date discovered` / `Date recommended` / `Date applied`.

### Proposed change

1. In `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, stop using the literal `Recommended Job Report` for the modal title and for `jobTitle`. Modal `title` is `` `${companyNameDisplay}${discoveredLabel ? ` · ${discoveredLabel}` : ""}` `` where `companyNameDisplay` is `job.company_name.trim()` when non-empty, else `job.company`, and `discoveredLabel` is the same `m/d/yy` formatting the header uses for `discovered_at` (en-US numeric month/day/2-digit year; invalid/empty → omit the date). Pass `jobTitle={job.job_title?.trim() || ""}` so the header does not invent `Recommended Job Report`. `jobLink` is `httpListingHref(job.listing_href) ?? httpListingHref(job.job_link)`. `jobLinkText` is that href, else the raw `job.job_link` or `listing_href` string when non-empty. `companyWebsite` stays `job.company_website` trimmed, or null.

2. In `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`:
   - Primary identity line (`.recommended-report-title`): `companyName`, and when `formatReportDate(discoveredAt)` is non-null append ` · ` plus that date. Do not put `jobTitle` on that line. If `jobTitle` is non-empty, render it as a secondary line under the identity (existing title size is the identity; secondary uses the job-link text size).
   - Job-link line: if `jobLink` is not http(s) but `jobLinkText` is, use `jobLinkText` as the `<a href>`. Still render non-http text when there is no http(s) href.
   - Website line: when `companyWebsite` is non-empty, keep it on its own line under the job link. If the value does not start with `http://` or `https://`, href is `https://` plus the trimmed value; visible text stays the given string.
   - Date strip: replace the prefixes with `Discovered: `, `Recommended: `, and `Applied: ` (colon, then the formatted date). Still omit a row when its timestamp is null. Applied stays omitted when `appliedAt` is null.

3. Do not edit shared `.modal-title` / `.modal-header` / `.modal-body` rules. Report-scoped header rules only if a new secondary job-title line needs a class: add `.recommended-report-job-title-secondary` next to the existing title rules (font-size 12px, color `--text-secondary`). No other CSS.

### Blast radius

Skip / Applied / Generate callbacks and labels stay. Copy and header Print stay gone. `formatReportDate` stays local to the header (modal may duplicate the three-option `Intl.DateTimeFormat` call rather than import a new helper). Betty header tests that expect `Date discovered` or the job title as `.recommended-report-title` will go red; do not edit `tests/` here. AST-2234 Analysis/Discussion/Artifacts behavior is unchanged by this section.

### What must still hold

Parent AC 1–2: no Copy controls and no Print Resume/Cover in the header; Skip and Applied still render only when their callbacks are passed. Parent AC 7: `company_name` is the company label (not short_name alone when `company_name` is non-empty); website is an `<a target="_blank">` on its own line under the job-link line. Parent AC 8: discovered = `discoveredAt`, recommended = `recommendedAt`, applied only when non-null. Parent AC 9: at ≤1023px Skip/Applied still wrap instead of clipping.

```


## Joan board AST-2268

[board-joan] CANON: OK

Plan-fix for AST-2268 is a UAT regression restore: header identity/links/date labels (2233 patch) and Analysis labels, mobile grade dots, show-rubric content preference (2234 patch). No statute or pattern text change, carve-out, or new directive. Rubric resolution still uses existing API/read paths; it only fixes empty live row winning over job-carried content. Report-scoped CSS stays inside the AST-2233 boundary (no shared .modal-title / .modal-header / .modal-body edits). Parent AST-2226 canon scope does not require an amendment for this shape.

## Radia review AST-2268

[code-rubric]
**Ticket:** AST-2268
**Publish ref:** `origin/sub/AST-2226/AST-2268-recommended-modal-header-score-labels-and-show-rubric-miss-uat` @ `b53ef9c267200fd3ac4100acc436f716ac61da80`
**Diff base:** `origin/ftr/AST-2226-updates-to-recommended-job-modal` @ `c58774be6a5dec062fef3c5f58fe671a58f8ef5f` (three-dot vs sub includes stacked merges from other work; **canon + fix review scoped to** `cf7439838..b53ef9c26` — 10 files, AST-2268 product + tests + bible)
**Corpus:** _(no frozen directive ids on ticket; Joan board CANON: OK)_
**Overall:** CLEAN

## Canon scores

_(Frozen Citations: none — Joan `[board-joan] CANON: OK`; no statute/pattern ids to score.)_

## Column diff vs plan stage

no plan-stage canon scores attached (board-only CANON: OK)

## Frame diff

(none)

## Fix-specific checks

**[bug-repro]** OK — Two tagged tests pin concrete **To-be** behavior (not tautologies):
- `test_JobAnalysisReportModal.test.tsx` — `[bug-repro] AST-2268 JD header is score and gradable percent` asserts `JD Analysis - 3.7 (83% gradable)`, rejects earned/possible template, and `Total Score:` in `.recommended-report-total-gradable` (items 1–2).
- `test_AgentAnalysisHeader.test.tsx` — `[bug-repro] AST-2268: job-carried rubric content beats a blank live row` mocks live detail row without usable `content`, job-carried `rubricItems` with `Job carried body`; expects body text and not `No rubric found for this vector.` (item 4). Would fail pre-fix preference order.

**## What must still hold** — OK (both plan-fix patches):
- **2233 patch:** No Copy/Print props or controls reintroduced; Skip/Applied/Generate still callback-gated; `company_name` drives identity; website remains separate `<a target="_blank">` with `https://` prefix when needed; date strip uses `discoveredAt` / `recommendedAt` / `appliedAt` with applied omitted when null; report-scoped CSS only (`.recommended-report-job-title-secondary`, phase-grade `nowrap` media query) — no shared `.modal-title` / `.modal-header` / `.modal-body` rule edits.
- **2234 patch:** `jobGradablePercent` still feeds total parenthetical; phase titles use breakdown `possible/max` (not job-level %); thermometer block untouched in diff; `buildPhaseSectionGradeConfidenceRow(..., isMobile)` adds letterless dots at ≤1023px; rubric still uses existing GET + `RubricModal` loading gate; Skip/`can_*`, tab filter, JD pane, Artifacts/mobile paths not removed in fix commits.

## Findings

**fix-now**

(none)

**discuss**

- **Duplicate company block:** After AST-2268, `.recommended-report-title` and `.recommended-report-company-line` both show `companyName` (+ date on each). Plan-fix primary identity moved to `.recommended-report-title` but did not drop the older company line. @susan — intentional double line or follow-up cosmetic trim? **Default:** leave for UAT; remove `.recommended-report-company-line` duplicate in a tiny follow-up if Susan flags it.
- **Empty modal title:** When `company_name` and `company` are both empty, `modalTitle` is `""` (no `Recommended Job Report` fallback). **Default:** accept over the wrong literal; only revisit if empty `<h2>` is worse in practice.

**advisory**

- **Diff base width:** `ftr...sub` three-dot stat is huge (other epics merged onto sub); scoring used AST-2268 commits only — expected for fix-lane sub stacked above advancing `ftr`.
- **Item 3 (mobile dots):** Implemented via `letterless` + CSS `flex-wrap: nowrap`; no dedicated `[bug-repro]` — coverage is code + CSS, not a viewport assertion (Betty manifest lists modal/header tests).
- **Engineer thread:** `b53ef9c26` notes two Generate-hidden asserts stale — header on this tip is AST-2233-shaped; optional Betty tidy, not merge-blocking.

## Plan fidelity (§5.4)

- Items 1–7 map to `JobAnalysisReportModal`, `RecommendedJobReportHeader`, `AgentAnalysisHeader`, `RubricModal`, `recommendedJobReport.tsx`, `App.css` — matches amended scope (including `AgentAnalysisHeader` / `RubricModal` after `[scope-gate]`).
- `jobLink` / `jobLinkText` fall back to `job_link` when `listing_href` is not http(s); modal title `company · m/d/yy`; show-rubric job-before-blank-live content order per plan.

## What's solid

- `rubricContentFor` matches plan resolution (usable job content first; live only when job missing/blank).
- `RubricModal` trims before not-found string.
- Revised AST-1695/1704/1983/2233 tests align with company-primary identity.

## Chuckles (read-only — you do not act)

| Gate | Parent | Next |
|------|--------|------|
| **PROCEED** (clean, C7 complete) | AST-2226 live | → **Review Posted** → fix-lane clean shortcut → **User Testing** (`resolve-child` skipped) |

```
[code-rubric] PROCEED (Commit: b53ef9c26) UAT regressions restored
```

context_tokens≈24000
