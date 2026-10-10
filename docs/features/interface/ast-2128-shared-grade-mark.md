# Shared grade mark

- **Ticket:** [AST-2128](https://linear.app/astralcareermatch/issue/AST-2128) — child of [AST-2101](https://linear.app/astralcareermatch/issue/AST-2101) (Add "Shapes - Light" and "Shapes - Dark" themes)
- **Publish ref:** `origin/sub/AST-2101/AST-2128-shared-grade-mark`
- **Canon Scope:** none (parent Architectural definition — no in-force pattern or statute governs frontend display components).

Every grade mark in the UI moves onto one shared `GradeMark` component. It renders today's `grade-dot dot-<g>` (+ `grade-dot-letterless`) span and letter unchanged, gives the span an image role whose accessible name is the grade letter, and carries an inline, assistive-tech-hidden SVG holding that grade's shape path from the parent brief. The SVG ships **not displayed** on every theme — this ticket adds no CSS, so there is **zero visual change**. Sibling [AST-2129](https://linear.app/astralcareermatch/issue/AST-2129) (Shapes themes, Ada) later adds the `App.css` rules that reveal the shape in the two Shapes themes only.

## Scope gate

Every row below is a file this ticket's `## Scope` names; every change is the kind its Technical scope describes (new display component; four call sites swap their local span/helper for the shared mark with the same props). The test file and `components.md` in Scope belong to Betty (`qa-child`) — engineers do not touch `tests/` or `docs/test-bible/**`, so they are **not** in Files Changed.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/GradeMark.tsx` | **New.** `GradeMark` component + private `GRADE_SHAPE_PATHS` geometry map | ui (frontend component) |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Delete local `gradeDot` helper; 3 call sites render `<GradeMark>` | ui (frontend lib) |
| `src/ui/frontend/src/components/AgentAnalysisHeader.tsx` | Inline grade-dot span → `<GradeMark>` | ui (frontend component) |
| `src/ui/frontend/src/pages/JobsProcessing.tsx` | Delete local `gradeDot` helper; 1 call site renders `<GradeMark>` | ui (frontend page) |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Delete local `gradeDot` helper; 1 call site renders `<GradeMark>` | ui (frontend page) |

No `App.css`, `config.py`, registry, context, or `uiConfig.ts` change (Boundaries + Susan's option **(A)**).

## Stage 1: Shared `GradeMark` component

**Done when:** `src/ui/frontend/src/components/GradeMark.tsx` exists, exports `GradeMark`, and `npx tsc --noEmit` in `src/ui/frontend` exits 0. No call site uses it yet.

1. Create `src/ui/frontend/src/components/GradeMark.tsx` with **exactly** this content (named export, matching sibling `ConfidenceBullets.tsx`):

   ```tsx
   /** AST-2128: the one grade mark every page renders. Accessible name = grade letter on every
    *  layout; the shape SVG ships undisplayed until the Shapes themes' CSS (AST-2129) reveals it. */

   // Parent-brief geometry on a 0 0 100 100 viewBox, keyed by grade letter.
   // X is a stroke-only cross — the theme CSS strokes it; the path itself has no fill intent.
   const GRADE_SHAPE_PATHS: Record<string, string> = {
     A: "M50 6a44 44 0 1 0 0.01 0Z", // circle
     B: "M50 3L97 50L50 97L3 50Z", // diamond
     C: "M18 9H82Q91 9 91 18V82Q91 91 82 91H18Q9 91 9 82V18Q9 9 18 9Z", // rounded square
     D: "M50 6L96 90H4Z", // up triangle
     F: "M4 10H96L50 94Z", // down triangle
     X: "M20 20L80 80M80 20L20 80", // cross
   }

   export function GradeMark({
     grade,
     tooltip,
     letterless = false,
   }: {
     grade: string
     tooltip?: string
     /** Compact colour-only mark (AST-1968): no visible letter, name still the grade. */
     letterless?: boolean
   }) {
     const shape = GRADE_SHAPE_PATHS[grade.toUpperCase()]
     return (
       <span
         className={`grade-dot dot-${grade.toLowerCase()}${letterless ? " grade-dot-letterless" : ""}`}
         title={tooltip || undefined}
         role="img"
         aria-label={grade}
       >
         {/* display="none" is an SVG presentation attribute, so any App.css rule outranks it —
             Shapes themes show the SVG with plain CSS; every other theme keeps today's circle. */}
         {shape && (
           <svg viewBox="0 0 100 100" aria-hidden display="none">
             <path d={shape} />
           </svg>
         )}
         {letterless ? null : grade}
       </span>
     )
   }
   ```

   ⚠️ **Decision — hiding the SVG without CSS:** Boundaries forbid any `App.css` rule here, yet an unstyled inline `<svg>` renders at the browser default (300×150) and would wreck every mark. Use the SVG **`display="none"` presentation attribute**: it hides the SVG on every theme today, and because presentation attributes sit below every author CSS rule, AST-2129's Shapes rules reveal it with an ordinary `display` declaration. Rejected: inline `style={{ display: "none" }}` (AST-2129 would need `!important`); `width="0" height="0"` (SVG stays a flex item, subtler, still needs CSS to hide on Light/Dark per parent AC 9).

   ⚠️ **Decision — letter stays a direct text node of the span:** wrapping it in a child element would move `getByText("<g>")` matches and change what existing call-site tests see. Direct text keeps `textContent` = the single letter (or `""` when letterless) — AC 7. The SVG contains only a `<path>` (no text nodes), and the JSX comment emits nothing, so it adds no text content. Letter centroid placement / hiding on X is AST-2129's CSS concern.

   ⚠️ **Decision — map lookup:** keyed by uppercase letter (`grade.toUpperCase()`); `className` keeps today's `grade.toLowerCase()`, and the visible text and `aria-label` keep `grade` exactly as passed (today's behaviour). A grade with no map entry renders the span with no SVG — today's span still renders, never a crash. `GRADE_SHAPE_PATHS` is **not** exported (no other consumer; Betty's test asserts against the brief's literal paths).

   ⚠️ **Decision — accessible name via `role="img"` + `aria-label`:** the image role makes the span's children presentational, so screen readers read exactly the grade letter for lettered **and** letterless marks (AC 6); `title` stays the hover tooltip and does not override `aria-label`. Checked: the only button that wraps grade dots (`formatPhaseTabNavLabel` / `buildPhaseTabGradeDots`) has no caller, and no existing test queries a role by a name that includes a grade mark.

2. In `src/ui/frontend` (run `npm ci` first if `node_modules/` is absent in the epic worktree): `npx tsc --noEmit` exits 0, and `npx eslint src/components/GradeMark.tsx` reports 0 problems.

## Stage 2: Swap every call site onto `GradeMark`

**Done when:** `git grep -n 'grade-dot dot-' -- src/ui/frontend/src` returns only `src/ui/frontend/src/components/GradeMark.tsx` (AC 8); `npx tsc --noEmit` in `src/ui/frontend` exits 0 and the touched files add no lint findings over baseline (step 5); the six AC 7 suites pass unedited.

1. `src/ui/frontend/src/lib/recommendedJobReport.tsx`:
   - Add `import { GradeMark } from "../components/GradeMark"` directly below the existing `import { ConfidenceBullets } from "../components/ConfidenceBullets"` line.
   - Delete the `// letterless: list rows show colour only (AST-1968); modal keeps the letter.` comment and the whole `function gradeDot(grade: string, tooltip: string, letterless = false) { … }` (currently lines 163–173).
   - In `buildPhaseTabGradeDots`: `return gradeDot(grade, gradeTooltip)` → `return <GradeMark grade={grade} tooltip={gradeTooltip} />`. Do **not** add a `key` (today's element has none; no other behaviour change).
   - In `buildPhaseSectionGradeConfidenceRow`: `{gradeDot(c.grade, c.tooltip)}` → `<GradeMark grade={c.grade} tooltip={c.tooltip} />`.
   - In `buildPhaseListGradeRow`: `{gradeDot(c.grade, c.tooltip, true)}` → `<GradeMark grade={c.grade} tooltip={c.tooltip} letterless />`. Keep the wrapping `<span key={c.key}>` as-is.
2. `src/ui/frontend/src/components/AgentAnalysisHeader.tsx`:
   - Add `import { GradeMark } from "./GradeMark"` directly below `import { ConfidenceBullets } from "./ConfidenceBullets"`.
   - Replace `<span className={`grade-dot dot-${g.grade.toLowerCase()}`}>{g.grade}</span>` (inside `.analysis-grade-block`) with `<GradeMark grade={g.grade} />` — no tooltip today, none added.
3. `src/ui/frontend/src/pages/JobsProcessing.tsx`:
   - Add `import { GradeMark } from "../components/GradeMark"` directly below `import { ConfidenceBullets } from "../components/ConfidenceBullets"`.
   - Delete `function gradeDot(grade: string, tooltip: string) { … }` (currently lines 37–39) and the blank line after it.
   - `{gradeDot(cell.grade, cell.gradeTooltip)}` → `<GradeMark grade={cell.grade} tooltip={cell.gradeTooltip} />`.
4. `src/ui/frontend/src/pages/JobsSkipped.tsx`:
   - Add `import { GradeMark } from "../components/GradeMark"` directly below `import { ConfidenceBullets } from "../components/ConfidenceBullets"`.
   - Delete `function gradeDot(grade: string, tooltip: string) { … }` (currently lines 43–45) and the blank line after it.
   - `{gradeDot(cell.grade, cell.gradeTooltip)}` → `<GradeMark grade={cell.grade} tooltip={cell.gradeTooltip} />`.
5. Verify (all from repo root unless noted):
   - `git grep -n 'grade-dot dot-' -- src/ui/frontend/src` → hits only in `GradeMark.tsx`.
   - `git grep -n 'gradeDot(' -- src/ui/frontend/src` → no hits.
   - In `src/ui/frontend`: `npx tsc --noEmit` exits 0.
   - In `src/ui/frontend`: `npx eslint src/components/GradeMark.tsx src/lib/recommendedJobReport.tsx src/components/AgentAnalysisHeader.tsx src/pages/JobsProcessing.tsx src/pages/JobsSkipped.tsx` reports **exactly 1 problem**: the pre-existing `react-hooks/set-state-in-effect` error on the `actions.error` effect in `JobsSkipped.tsx` (baseline on this branch before any change — not fixed here, out of scope). Any other finding is new and must be fixed in this stage. (Whole-project `npm run lint` already fails on the baseline with 29 problems, so it is not the gate.)
   - In `src/ui/frontend`: `npx vitest run --config vite.config.ts` on `test_recommendedJobReport`, `test_JobsProcessing`, `test_JobsSkipped`, `test_JobsRecommended`, `test_JobAnalysisReportModal`, `test_JobDetailModal`, `test_AgentAnalysisHeader` — all pass **unedited**. A failure here is a product bug in this stage, not a test edit.
   - `python -c "import src.utils.config"` exits 0 (AC 9; untouched file, sanity only).

## Integration notes (reference only — not this ticket's work)

- **AST-2129 (Ada):** the mark DOM is `span.grade-dot.dot-<g>[.grade-dot-letterless][role=img][aria-label=<G>] > svg[viewBox="0 0 100 100"][aria-hidden][display=none] > path[d]`, followed by the letter as a bare text node (lettered only). Shapes rules reveal the SVG with a plain `display` declaration on `.grade-dot > svg`; no `!important` needed. The letter has no wrapper element, so centroid placement and hiding on X go on the span itself.
- **Betty (`qa-child`):** `test_GradeMark.test.tsx` + `docs/test-bible/frontend/components.md` per AC 6/7. jsdom ignores the `display` presentation attribute, so the SVG reads as present in the DOM — assert `aria-hidden="true"` and the path `d`, not visibility.

## Estimate

Confirm Chuckles estimate: 3 — revise to 2 because it is one component slice on a known pattern (one ~40-line display component plus four mechanical call-site swaps, no CSS/registry/API change), and the test work is a straightforward per-grade table.


## Joan validate

[plan-rubric]
**Ticket:** AST-2128
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (canon tree at publish tip; `docs/canon-index.md` absent on ref)
**Publish ref:** `origin/sub/AST-2101/AST-2128-shared-grade-mark` @ `6c8984b73e9e5cf7709fea2444fe606511abfb13`

## Canon scores

_(empty — child **Citations:** none; parent **Canon Scope:** none — locked at Discussion. No directive ids to score; not §4a ESCALATE — explicit empty scope, same as AST-2123 Joan validate.)_

## Traceability

AC6→Stage 1 (`GradeMark` `role="img"` / `aria-label` / `aria-hidden` SVG) + Betty `test_GradeMark` (Scope, not Files Changed); AC7→Stage 2 (four call-site swaps + listed Vitest suites, unedited); AC8→Stage 2 (`git grep` gates); AC9→Stage 1–2 (`tsc`, scoped `eslint`, `import src.utils.config`; `test_AppCss` / `test_config` untouched — pass implied at tip, not named in Stage 2 verify).

## Findings

### fix-now

(none)

### discuss

- **Location:** Canon Scope vs `GradeMark.tsx` in `components/`
- **Finding:** `astral.ui.frontend-file-placement` plainly governs the new file; it is not on the frozen list (explicit **none**). Plan placement matches the statute (flat `components/`).
- **Recommendation:** Archie may leave **none** as-is; no plan change required for approval.

- **Location:** Stage 2 verify vs child AC 9
- **Finding:** AC 9 names `test_AppCss.test.tsx` and `test_config.py::TestAst2047ThemeRegistry`; engineer stages verify `tsc`, `eslint`, six AC-7 Vitest files, and `python -c "import src.utils.config"` only.
- **Recommendation:** Optional one-liner in Stage 2 step 5 for regression sanity on unmodified tests; Betty’s manifest still owns formal proof.

- **Location:** `display="none"` SVG presentation attribute (Stage 1 decision block)
- **Finding:** Correct for zero CSS this ticket and AST-2129 override path; jsdom visibility caveat is documented for Betty.
- **Recommendation:** None.

### acceptable

- **Location:** Scope gate; Files Changed vs `## Scope` test/bible rows
- **Finding:** Engineer/Betty split matches parent partition and `plan-child` boundary (no `tests/` or bible in Files Changed).
- **Recommendation:** None.

- **Location:** DRY — three `gradeDot` helpers → one `GradeMark`
- **Finding:** Matches child Technical scope; `astral.standards.dry-and-focused-functions` not on list (scope-gap note only if Archie widens canon later).
- **Recommendation:** None.

- **Location:** `test_AgentAnalysisHeader` in Stage 2 Vitest list vs AC 7’s six named suites
- **Finding:** Extra regression coverage for a modified file; not scope creep.
- **Recommendation:** None.

- **Location:** Estimate / complexity
- **Finding:** No formal `!!-CONF` self-assessment block; staged work matches estimate 2 (single component + mechanical swaps).
- **Recommendation:** None.

context_tokens≈28000

## Review

- **Branch:** `origin/sub/AST-2101/AST-2128-shared-grade-mark`
- **Stage 1:** `c101f9489` — `GradeMark.tsx`
- **Stage 2:** `a31045b7b` — four call sites on `GradeMark`; trailing blank line dropped from `GradeMark.tsx` (plan code block extraction artifact)
- **Verify:** `grade-dot dot-` hits only `GradeMark.tsx`; no `gradeDot(` left; `tsc -b --noEmit` OK; scoped eslint = the 1 baseline `JobsSkipped.tsx` `set-state-in-effect` error; `import src.utils.config` OK; `TestAst2047ThemeRegistry` 5 passed.
- **Vitest:** 197/200 across the AC 7 suites + `test_AgentAnalysisHeader` + `test_AppCss`. The 3 failures fail identically on the pre-change tip `9a267a790` (baseline, not this ticket): `test_AppCss` "no hex or non-black rgba outside token blocks… (AC5)" and "AST-2049: no hex in .ts/.tsx source… (AC9)", and `test_JobDetailModal` "AST-1695 … null listing_href → no Link <a>". Flag for Betty: child AC 9 names `test_AppCss.test.tsx` as passing.
