<!-- linear-archive: AST-1983 archived 2026-10-08 -->

## Linear archive (AST-1983)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1983/job-headers-use-the-shared-renderer-all-job-titles-in-ui-should-trail  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1981 — All Job Titles in UI should trail with an ellipsis after 50 chars  
**Blocked by / blocks / related:** parent: AST-1981; related: AST-1972

### Description

## What this implements

After [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982) and [AST-1972](https://linear.app/astralcareermatch/issue/AST-1972) land. Applies the shared component to the Job Detail modal header, the Meteorite modal header (title part only), and the Recommended Job Report header. Widens `Modal`'s title so a header can host it. Leaves the Info-tab Title field and input full. Does not touch list pages, config, or the component itself ([AST-1982](https://linear.app/astralcareermatch/issue/AST-1982)).

## Citations

none — frontend only.

## Scope

`src/ui/frontend/src/components/Modal.tsx` (`title` prop widens to a React node; `<h2>` unchanged); `src/ui/frontend/src/components/JobDetailModal.tsx` (Modal title job-title case through the shared component; fallbacks unchanged); `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` (`modalTitle` returns a node: shared component for the title part + untouched ` — <employer>`); `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` (`recommended-report-title` content through the shared component).

## Acceptance criteria

5. **Headers follow the rule.** With a title over 50 characters: the Job Detail modal `<h2>` text, the Recommended Job Report `.recommended-report-title` text, and the Meteorite modal `<h2>` text before `—` each start with `job_title.slice(0, 50) + "…"`. The Meteorite header's employer suffix is whole. Hovering the title shows the AC-3 tooltip. **Fail:** any full or differently-cut header title, or a cut employer.
6. **Info-tab Title field stays full.** In the Job Detail modal, the read-only Title field and the edit input both show the complete `job_title`. **Fail:** a `…` or cut value in either.
7. **Every in-scope surface uses the shared component** (this child's files). `rg -l "JobTitleText" src/ui/frontend/src` lists `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, and `RecommendedJobReportHeader.tsx`. **Fail:** any file missing.
8. **Builds clean; no new lint.** In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists). **Fail:** a non-zero exit or any new lint problem.

## Boundaries

Does not touch `config.py`, `uiConfig.ts`, `JobTitleText.tsx`, `App.css`, or any `pages/Jobs*.tsx` — all [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982). Does not truncate the Info-tab Title field or edit input.

## Notes for planning

Citations: none. Consumes [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982)'s shared component as-is; any change it needs goes back through [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982)'s scope, not this child.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T22:24:09.936Z
[code-rubric] PROCEED (Commit: 7dc68e85d) Headers use JobTitleText

#### betty — 2026-10-04T22:22:09.237Z
`origin/sub/AST-1981/AST-1983-job-title-headers` @ `7dc68e85d` · manifest in components.md bible

#### joan — 2026-10-04T22:16:55.768Z
[plan-rubric] PROCEED (Commit: cb0d69b) Header renderer plan ready

#### hedy — 2026-10-04T22:15:43.627Z
`origin/sub/AST-1981/AST-1983-job-title-headers` @ `cb0d69b06` · headers plan ready

---

# AST-1983 — Job headers use the shared renderer (All Job Titles in UI should trail with an ellipsis after 50 chars)

- **Parent:** [AST-1981](https://linear.app/astralcareermatch/issue/AST-1981) — All Job Titles in UI should trail with an ellipsis after 50 chars
- **Ticket:** [AST-1983](https://linear.app/astralcareermatch/issue/AST-1983)
- **Publish ref:** `origin/sub/AST-1981/AST-1983-job-title-headers`
- **Canon Scope:** none (locked at Discussion). No directive applies to these files.

Long job titles also stretch the modal and report headers. [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982) built the shared `JobTitleText` component, which cuts at the served `job_title_truncate_chars` (50) and shows a portaled, wrapped full-title tooltip when it cuts. This ticket uses that component, unchanged, in three headers: the Job Detail modal, the Meteorite modal (title part only; ` — <employer>` stays whole), and the Recommended Job Report header. `Modal`'s `title` prop widens from `string` to `ReactNode` so a header can host the component. The Info-tab Title field and its edit input stay full. List pages, config, `uiConfig.ts`, `JobTitleText.tsx`, and `App.css` are not touched (all AST-1982).

## Codebase facts the plan relies on (verified at sync tip `2237a05c0`; the plan commit sits directly on it)

- **Sync command:** the parent ref is `origin/ftr/AST-1981-job-title-ellipsis`. Run `sync-child.sh sub/AST-1981/AST-1983-job-title-headers --ftr AST-1981-job-title-ellipsis --worktree /home/susan/astral-AST-1981/`. With `--ftr AST-1981`, the script prints `ftr/AST-1981 not found on origin — skipping` and does not merge the parent, which leaves `JobTitleText` missing.
- [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982) is merged into `origin/ftr/AST-1981-job-title-ellipsis`, so `src/ui/frontend/src/components/JobTitleText.tsx` exists on this branch. Signature: `JobTitleText({ title, fallback }: { title: string | null | undefined; fallback: ReactNode })`. If `!title`, it renders `fallback`. If the title is at or under the limit, it renders bare text. Otherwise it renders `<span>{display}</span>` plus a `role="tooltip"` element portaled to `document.body` while hovered.
- [AST-1972](https://linear.app/astralcareermatch/issue/AST-1972) is on `origin/dev` (`26ad90af8`), so its `JobDetailModal.tsx` changes (the `PhaseAnalysisLines` import and Info-tab analysis) are already in this tree.
- `Modal.tsx:8`: `  title: string`. `ReactNode` is already imported (`import { useRef, useCallback, useContext, type ReactNode } from "react"`). `Modal.tsx:49` renders `<h2 className="modal-title">{title}</h2>`, which needs no change for a node. `ModalProps` is referenced only inside `Modal.tsx`, so widening the type breaks no caller. Every existing caller passes a string, which is still a valid `ReactNode`.
- `JobDetailModal.tsx:244`: `        title={job?.job_title || job?.company || "Job Detail"}`. The last `./` import is `import Time from "./Time"` (line 8). The Info-tab Title field (lines 307–316: `draft.job_title` input / `<span>{job.job_title || "—"}</span>`) is **not** touched.
- `MeteoriteDetailModal.tsx:102–110`: `function modalTitle(m: MeteoriteDetail | null, id: number): string { … }` returns `` `${title} — ${employer}` ``, `title`, `employer`, or `` `Meteorite ${id}` ``. `title` and `employer` come from `nonEmptyTrimmed(...)`, so they are non-empty strings or falsy. `modalTitle` is called only at line 82, and its result is used only as `<Modal title={title}>` (line 85). `ReactNode` is already imported on line 1. Imports: `./Modal` (line 3), `./ReportSectionList` (line 4).
- `RecommendedJobReportHeader.tsx:61`: `          <span className="recommended-report-title">{jobTitle}</span>`. The prop is `jobTitle: string`. The file has no imports today. Its only caller, `JobAnalysisReportModal.tsx:705`, passes `job?.job_title?.trim() || job?.company || "Recommended Job Report"`. That means the fallback is already resolved before the header sees it (see the Decision in Stage 1 step 5). `JobAnalysisReportModal.tsx` is out of scope and not touched.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/Modal.tsx` | `ModalProps.title` widens `string` → `ReactNode`; `<h2>` unchanged | ui (component) |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | `Modal` title job-title case renders `JobTitleText`; company / "Job Detail" fallbacks unchanged | ui (component) |
| `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` | `modalTitle` returns `ReactNode`: `JobTitleText` for the title part plus untouched `` ` — ${employer}` `` | ui (component) |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | `.recommended-report-title` content renders `JobTitleText` | ui (component) |

**Scope gate:** every row above is named in this ticket's `## Scope`, and each change is the kind Scope describes. No other files. `JobTitleText.tsx`, `uiConfig.ts`, `config.py`, `App.css`, `pages/Jobs*.tsx`, and `JobAnalysisReportModal.tsx` stay untouched.

## Stage 0: Lint baseline (no commit)

**Done when:** `debug/spikes/ast-1983/lint-before.txt` holds the `npm run lint` output from the synced tree, before any edits.

1. If `src/ui/frontend/node_modules` is missing, run `npm ci` in `src/ui/frontend` (lockfile only; no tracked changes).
2. In `src/ui/frontend`, run `mkdir -p ../../../debug/spikes/ast-1983 && npm run lint > ../../../debug/spikes/ast-1983/lint-before.txt 2>&1; true`. `debug/` is gitignored, so do not commit this file.

## Stage 1: Widen Modal title; three headers through JobTitleText

**Done when:** `npm run build` exits 0. `rg -l "JobTitleText" src/ui/frontend/src` lists `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, and `RecommendedJobReportHeader.tsx`. The diff of `JobDetailModal.tsx` touches only the import and the `Modal` `title=` line. Lint shows nothing new against the Stage 0 baseline.

1. `Modal.tsx`: replace line 8, `  title: string`, with:

   ```tsx
     /** AST-1981: node, not string — headers host JobTitleText (cut + tooltip). Plain strings still work. */
     title: ReactNode
   ```

   Change nothing else in the file.

2. `JobDetailModal.tsx`:
   - Directly after `import Time from "./Time"`, add `import JobTitleText from "./JobTitleText"`.
   - Replace `        title={job?.job_title || job?.company || "Job Detail"}` with:

     ```tsx
             title={<JobTitleText title={job?.job_title} fallback={job?.company || "Job Detail"} />}
     ```

     This keeps the same chain. `JobTitleText` renders `fallback` for a null or empty `job_title`, and `fallback` is the original `company || "Job Detail"` tail.
   - Do **not** touch the Info-tab Title row (the `draft.job_title` input and `<span>{job.job_title || "—"}</span>`). Parent AC 6 requires both to stay full.

3. `MeteoriteDetailModal.tsx`:
   - Directly after `import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"`, add `import JobTitleText from "./JobTitleText"`.
   - Replace the whole `modalTitle` function (lines 102–110) with:

     ```tsx
     function modalTitle(m: MeteoriteDetail | null, id: number): ReactNode {
       if (!m) return `Meteorite ${id}`
       const title = nonEmptyTrimmed(m.job_title)
       const employer = nonEmptyTrimmed(m.employer_name)
       // AST-1981: only the job-title part is cut (JobTitleText); the employer suffix stays whole.
       // fallback={null} is never reached — title is non-empty in both branches.
       if (title && employer) return <><JobTitleText title={title} fallback={null} />{` — ${employer}`}</>
       if (title) return <JobTitleText title={title} fallback={null} />
       if (employer) return employer
       return `Meteorite ${id}`
     }
     ```

     The suffix is one template-literal text node (`` ` — ${employer}` ``). JSX whitespace rules can't drop the spaces around `—` that way, and the `<h2>` text reads `<cut title> — <employer>`.
   - The call site (`const title = modalTitle(meteorite, meteoriteId)` / `<Modal open title={title} …>`) is unchanged.

4. `RecommendedJobReportHeader.tsx`:
   - Insert `import JobTitleText from "./JobTitleText"` as line 1, followed by one blank line before `interface Props {`.
   - Replace `          <span className="recommended-report-title">{jobTitle}</span>` with:

     ```tsx
               <span className="recommended-report-title"><JobTitleText title={jobTitle} fallback={jobTitle} /></span>
     ```

5. ⚠️ **Decision:** The header passes its `jobTitle` prop as both `title` and `fallback`. The prop arrives already resolved (`job_title || company || "Recommended Job Report"`, from `JobAnalysisReportModal.tsx:705`, which is out of scope). Two results follow:
   - An empty `jobTitle` renders `""`, the same as today.
   - When the job has no title and the **company** fallback is over 50 characters, that company name is also cut, with a tooltip. The header can't tell a title from its fallback without a new raw-title prop. Adding that prop means editing `JobAnalysisReportModal.tsx`, which is outside this ticket's Scope.

   The AC 5 path (a real title over 50) is exact either way. If Susan or Joan wants company fallbacks never cut, the scope has to be amended to add that caller. Do not improvise it at build.

6. Verify:
   - In `src/ui/frontend`, `npm run build` exits 0.
   - `npm run lint > ../../../debug/spikes/ast-1983/lint-after.txt 2>&1; true`, then compare problems with line:col stripped: `S=../../../debug/spikes/ast-1983; diff <(rg "^\s+\d+:\d+" $S/lint-before.txt | sed -E 's/^\s+[0-9]+:[0-9]+\s+//' | sort) <(rg "^\s+\d+:\d+" $S/lint-after.txt | sed -E 's/^\s+[0-9]+:[0-9]+\s+//' | sort)` must show no `>` line.
   - From the repo root, `rg -l "JobTitleText" src/ui/frontend/src` includes `components/JobDetailModal.tsx`, `components/MeteoriteDetailModal.tsx`, and `components/RecommendedJobReportHeader.tsx`.
   - `git diff origin/ftr/AST-1981-job-title-ellipsis -- src/ui/frontend/src/components/JobDetailModal.tsx` shows exactly two `+` code lines (the import and the `title=` line). No Info-tab line changes.
   - `git diff origin/ftr/AST-1981-job-title-ellipsis --name-only` lists only the four Files Changed paths, plus this plan doc.
   - `git diff origin/ftr/AST-1981-job-title-ellipsis -- src/ui/frontend/src | rg "^\+.*(\b50\b|\.slice\()"` returns nothing.
7. Commit: `code(AST-1983): Job Detail / Meteorite / Recommended Report headers use JobTitleText; Modal title accepts a node`, then publish per build-child.

## Acceptance criteria map

| AC | Satisfied by |
|----|--------------|
| 5 Headers follow the rule | S1.2 Job Detail `<h2>`; S1.3 Meteorite title part with the employer suffix as a separate whole text node; S1.4 `.recommended-report-title`. The tooltip comes from AST-1982's `JobTitleText` unchanged. |
| 6 Info-tab Title stays full | S1.2 leaves the Info-tab row alone; S1.6 diff check |
| 7 Every in-scope surface uses the component | S1.2–S1.4; S1.6 `rg -l` |
| 8 Build/lint clean | S0 baseline; S1.6 build + lint diff |

**For QA ([AST-1983](https://linear.app/astralcareermatch/issue/AST-1983) → Betty):** existing component tests that assert a modal or report header's **full** text with a title over 50 characters will now see the cut text. Short-title assertions are unaffected. `Modal` callers that pass strings behave the same as before.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]

**Ticket:** AST-1983  
**Overall:** APPROVED  
**Corpus:** e1f2699fad  
**Publish ref:** `cb0d69b0641865e0447578e9db84557c5e06eff4`

## Canon scores

Frozen list is empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score.

## Traceability

AC5–8 → Stage 0–1 and **Acceptance criteria map** (parent AC1–4 / list tables / config / sort → N/A — AST-1982 and out of **Boundaries**; parent AC9–10 not in this child’s AC set).

### Findings

**discuss** | Stage 1 step 5 (Recommended Job Report header)  
When `jobTitle` is the caller-resolved company string (no `job_title`), `JobTitleText` still cuts at 50 because `title` and `fallback` are the same non-empty string. Parent AC5 is written around a long **job** title; this path is documented and bounded (no `JobAnalysisReportModal` change). If product wants company-only report titles never cut, scope must widen — not a silent build change.

**discuss** | **Codebase facts** sync tip `2237a05c0` vs publish `cb0d69b`  
Cosmetic; line anchors checked against current tree (`Modal.tsx:8`, `JobDetailModal.tsx:244`, `modalTitle` 102–110, report header line 61) and match.

**acceptable** | Prerequisite **AST-1982** on `origin/ftr/AST-1981-job-title-ellipsis`  
Plan states correct `sync-child.sh --ftr AST-1981-job-title-ellipsis`; wrong `--ftr AST-1981` skips parent merge. `JobTitleText` is present on the epic worktree with the expected API.

**acceptable** | **JobDetailModal** `title={…}` vs Info-tab Title row  
`JobTitleText` with `title={job?.job_title}` leaves company / “Job Detail” uncut when `job_title` is empty (`!title` → fallback only). Info-tab input and read-only span untouched — AC6.

**acceptable** | **Meteorite** `modalTitle` → `ReactNode`  
Employer suffix as a sibling text node preserves whole ` — <employer>`; AC5 employer clause satisfied.

### R6 (summary)

Definition fidelity: four scoped files only; no AST-1982 surface edits; `Modal` widen is minimal. DRY: consumes `JobTitleText` as-is. Dependency and sync instructions are explicit. Betty note on header test expectations is helpful. Estimate confirm present. Plan Ready, assignee Joan Clarke; no `[plan-discuss]` rounds.

context_tokens≈24000

## Review

- **Branch:** `origin/sub/AST-1981/AST-1983-job-title-headers`
- **Build commit:** `6c6e1cb17` (Stage 1: `Modal.title` → `ReactNode`; Job Detail / Meteorite / Recommended Report headers render `JobTitleText`)
- **Build notes:** `npx tsc -b --noEmit` and `npm run build` exit 0. `npm run lint` before/after: 31 problems both, line:col-stripped diff empty. `rg -l "JobTitleText"` lists `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, `RecommendedJobReportHeader.tsx`. `JobDetailModal.tsx` diff is the import + `title=` line only (Info-tab Title row untouched). Diff vs `origin/ftr/AST-1981-job-title-ellipsis` names only the four planned files + this doc; no added `50` / `.slice(`.
- **Deviation:** none.
- **For QA:** header cut/tooltip (AC 5) and the Meteorite whole-employer suffix need a rendered DOM; no manual browser smoke in this headless build. Existing tests that assert a header's full text with a title over 50 chars will now see the cut text. Company-only report titles over 50 chars are also cut (plan Stage 1 step 5 Decision; Joan discuss).

## Radia review

[code-rubric]

**Ticket:** AST-1983  
**Publish ref:** `7dc68e85d867b86e1da77f78258b473435e8c744` (`origin/sub/AST-1981/AST-1983-job-title-headers`; product commit `6c6e1cb17` + `merge-tests(AST-1983): origin/tests 77c372511`)  
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (`canon/` at publish tip; no `docs/canon-index.md` on ref; frozen list empty)  
**Overall:** CLEAN  

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not §5.3 ESCALATE (same rationale as Joan plan-stage).

## Column diff vs plan stage

(aligned) — Joan recorded an empty frozen list; code review adds no canon rows.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Recommended Job Report header — company-only fallback over 50 chars** (`RecommendedJobReportHeader.tsx`: `title={jobTitle} fallback={jobTitle}`)  
  When the caller passes a resolved company string (no `job_title`), `JobTitleText` still truncates at 50 because `title` and `fallback` are the same non-empty string. Plan Stage 1 step 5 and Joan validate document this; tests cover a real long **job** title, not a long company-only `jobTitle`.  
  **Question @susan:** Should company-only report headers stay full while job titles cut?  
  **Default:** Ship as implemented (no `JobAnalysisReportModal` change) unless scope is amended before **User Testing** — smaller, reversible, matches approved plan.

### advisory

- **Epic composite vs `origin/dev`:** The three-dot diff includes the full AST-1982 stack (list tables, `JobTitleText`, config, CSS) because this publish ref builds on that work. AST-1983’s **product** delta is exactly the four scoped files in `6c6e1cb17`; scope gate for this ticket is honored.
- **sibling test carry:** Same `merge-tests` bundle as AST-1982 (Created column, Meteorites `job_created_at`, admin/meteorite API tests, etc.) — expected; not scored against AST-1983 product scope.
- **`expectFullTitleTooltip`** in `job-title-cell.ts` (refactor shared by list + header tests) — sensible DRY for AC3/AC5 tooltip assertions.

## What's solid

- **Plan fidelity:** `ModalProps.title` → `ReactNode` only; `JobDetailModal` import + `title=` with preserved fallback chain; `MeteoriteDetailModal` `modalTitle` → `ReactNode` with title-only cut and whole `` ` — ${employer}` `` suffix; `RecommendedJobReportHeader` wraps `.recommended-report-title` in `JobTitleText`. No edits to `JobTitleText.tsx`, pages, config, `App.css`, or `JobAnalysisReportModal.tsx`.
- **AC6:** Info-tab Title input/read-only span unchanged in `JobDetailModal.tsx`; tests assert full `LONG_TITLE` in Info (read-only and editable input) while the `<h2>` shows `CUT_TITLE`.
- **AC5 Meteorite:** Tests assert `${CUT_TITLE} — ${LONG_EMPLOYER}` with employer whole and tooltip on the title span only; employer-only header uncut.
- **Estimate:** Confirmed **2** — four small component touch points + header-focused tests; footprint matches.

## Recommended actions (Chuckles — not Radia)

- Append this block to `docs/features/interface/ast-1983-job-headers-use-the-shared-renderer.md`, commit `docs(AST-1983): Radia review — clean`, push publish ref.
- Post slim upshot via `linear_proxy.py --as radia save-comment`; **Tests Passed** → **Review Posted**; datt **§3h** **PROCEED** toward **User Testing** unless Susan answers the company-fallback discuss with a scope widen.

context_tokens≈22000

## Resolution

2026-10-04 — resolve against Radia review `0b4350f9f` (publish tip at review `7dc68e85d`).

- **fix-now:** none.
- **discuss — company-only Recommended Job Report header over 50 chars:** no direction from Susan in the thread, so took Radia's **Default: ship as implemented**. `RecommendedJobReportHeader` keeps `title={jobTitle} fallback={jobTitle}`; `JobAnalysisReportModal.tsx` is unchanged (outside Scope). To reverse, amend Scope to add that caller, pass the raw `job_title` as a new header prop, and keep `company || "Recommended Job Report"` as the fallback.
- **advisory:** no action. The epic composite diff and sibling test carry are expected; `expectFullTitleTooltip` is Betty's.
- **Product delta:** none in this pass. Build commit `6c6e1cb17` stands.
