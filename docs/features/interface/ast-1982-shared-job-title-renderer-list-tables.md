<!-- linear-archive: AST-1982 archived 2026-10-08 -->

## Linear archive (AST-1982)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1982/shared-job-title-renderer-list-tables-all-job-titles-in-ui-should  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1981 — All Job Titles in UI should trail with an ellipsis after 50 chars  
**Blocked by / blocks / related:** parent: AST-1981; blocks: AST-1983; related: AST-1971; related: AST-1967

### Description

## What this implements

After [AST-1967](https://linear.app/astralcareermatch/issue/AST-1967) and [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971) land. Builds the config-driven 50-character rule and the wrapped, portaled full-title tooltip as one shared component, and applies it to the Job Title cell on Ready, Review, Processing, Skipped, Applied, and Meteorites. Does not touch any modal or report header ([AST-1983](https://linear.app/astralcareermatch/issue/AST-1983)).

## Citations

none — frontend and a `UI_CONFIG` value only; no in-force directive reaches these files.

## Scope

`src/utils/config.py` (new `UI_CONFIG` job-title truncate key, value 50); `src/ui/frontend/src/lib/uiConfig.ts` (type key + resolver with fallback, mirroring `resolveCellTruncateChars`); `src/ui/frontend/src/components/JobTitleText.tsx` (**new** — cuts via `truncateForDisplay` at the resolved length, portaled `role="tooltip"` with the full title only when cut, caller-supplied fallback); `src/ui/frontend/src/App.css` (tooltip class: fixed max-width, normal wrapping, elevated surface); `src/ui/frontend/src/pages/JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, `JobsApplied.tsx` (Job Title `<td>` renders the shared component, `—` fallback; sorters / aria / clicks unchanged); `src/ui/frontend/src/pages/JobsMeteorites.tsx` (`job_title` render branch in the column-mapping `useMemo` returns the shared component).

## Acceptance criteria

1. **Long titles cut at 50.** Take a job whose `job_title` is longer than 50 characters, in each list table on Ready, Review, Processing, Skipped (each table variant), Applied, and Meteorites. Its Job Title cell text equals `job_title.slice(0, 50) + "…"`. **Fail:** any other length, a missing `…`, or the full title shown.
2. **Short titles untouched.** A job whose title is 50 characters or fewer shows its exact title, and hovering it renders no `[role="tooltip"]` element and no `title` attribute. **Fail:** a `…`, a tooltip, or a native title on a short title.
3. **Tooltip shows full, wrapped, unclipped.** Hovering a cut title renders one `[role="tooltip"]` whose `textContent` equals the full `job_title`. The element is a descendant of `document.body` and is **not** inside the table or modal subtree. Its computed `white-space` is `normal` and its computed `max-width` is a fixed pixel value (not `none`). A title over 100 characters renders on more than one line (element `offsetHeight` > one line-height). Mouse-out removes it. **Fail:** truncated or clipped tooltip text, a native browser tooltip instead, single-line overflow, or a tooltip that stays after mouse-out.
4. **Meteorites job title at 50, other columns at 30.** On Jobs → Meteorites, a row with a 45-character `job_title` shows the full 45 characters with no `…`. A 60-character title shows 50 characters plus `…`. Any other column value over 30 characters still shows 30 characters plus `…`. **Fail:** job title cut at 30, or other columns changed.
5. **One source for 50, one cut function.** `GET /api/system/ui_config` returns the new job-title key with value `50`. Changing it in `UI_CONFIG` to `20` and reloading cuts every in-scope title at 20 (manual check, reverted). `rg -n "job_title.*\.slice\(|\b50\b" src/ui/frontend/src/pages src/ui/frontend/src/components` returns no hit added by this epic, and `rg -n "\.slice\(" src/ui/frontend/src/components/JobTitleText.tsx` returns nothing (it cuts via `truncateForDisplay`). **Fail:** a hardcoded 50 or a second slicing path.
6. **Every in-scope surface uses the shared component** (this child's files). `rg -l "JobTitleText" src/ui/frontend/src` lists `JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, `JobsApplied.tsx`, and `JobsMeteorites.tsx`. `rg -n '\{job\.job_title \|\| "\\u2014"\}' src/ui/frontend/src/pages` returns nothing. **Fail:** any file missing, or a raw title cell left.
7. **Sort and search use the full title.** On Ready, sorting by Job Title orders rows the same as on `origin/dev` at branch point. On Meteorites, searching for a word that appears only after character 50 of a title still returns that row. **Fail:** a changed order or a missed search hit.
8. **Builds clean; no new lint.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists). **Fail:** a non-zero exit or any new lint problem.

## Boundaries

Does not touch `Modal.tsx`, `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, or `RecommendedJobReportHeader.tsx` — those headers are [AST-1983](https://linear.app/astralcareermatch/issue/AST-1983), which consumes this child's component. Does not change `ListTableTruncatedCell`, `truncateForDisplay`, or the generic 30-character truncation on other `ListPage` columns.

## Notes for planning

Citations: none. [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971) (PR #227, Created column) edits the same four list pages and `config.py` and had not yet landed on `dev` at dispatch — expect adjacent-line merges on sync.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T22:12:35.339Z
[code-rubric] PROCEED (Commit: 01a29571b) Clean list-title cut

#### betty — 2026-10-04T22:10:26.054Z
`origin/sub/AST-1981/AST-1982-job-title-renderer` @ `01a29571b` · manifest in components.md bible

#### joan — 2026-10-04T22:01:47.664Z
[plan-rubric] PROCEED (Commit: 5f4b9bf) List tables plan ready

#### ada — 2026-10-04T22:00:07.103Z
`origin/sub/AST-1981/AST-1982-job-title-renderer` @ `5f4b9bf00ba81d86679534e4361437f859d21b1b` · plan ready

---

# AST-1982 — Shared job-title renderer + list tables (All Job Titles in UI should trail with an ellipsis after 50 chars)

- **Parent:** [AST-1981](https://linear.app/astralcareermatch/issue/AST-1981) — All Job Titles in UI should trail with an ellipsis after 50 chars
- **Ticket:** [AST-1982](https://linear.app/astralcareermatch/issue/AST-1982)
- **Publish ref:** `origin/sub/AST-1981/AST-1982-job-title-renderer`
- **Canon Scope:** none (locked at Discussion). No directive applies to these files.

Long job titles stretch the Jobs list tables. This ticket adds one served config value (`UI_CONFIG["job_title_truncate_chars"] = 50`), a resolver for it, and one shared component, `JobTitleText`. The component cuts a title through the existing `truncateForDisplay`. When it cuts, hovering shows the full title in a wrapped tooltip that is portaled to `document.body`, so table overflow can't clip it. The ticket then uses that component for the Job Title cell on Ready and Review (`JobsRecommended`), Processing, Skipped, Applied, and Meteorites. Modal and report headers belong to [AST-1983](https://linear.app/astralcareermatch/issue/AST-1983), which consumes this component. This plan does not touch them.

## Codebase facts the plan relies on (verified at branch tip `3a78a9640`)

- `UI_CONFIG` is in `src/utils/config.py` at line ~5569. `"list_table_cell_truncate_chars": 30,` sits at line ~5580 under the `# AST-647` comment.
- `GET /api/system/ui_config` (`src/ui/api/api_system.py:198`) returns `{**UI_CONFIG, ...}`, so a new top-level key is served without any API change.
- `resolveCellTruncateChars` and `truncateForDisplay` are in `src/ui/frontend/src/lib/listTableLayout.ts`, not in `uiConfig.ts`. Per Scope, the new resolver goes in `uiConfig.ts`. It copies the shape of `resolveCellTruncateChars` and does not modify that function.
- `truncateForDisplay(text, maxChars)` returns `{ display, full }`. `display === full` when `text.length <= maxChars`. Otherwise `display` is `text.slice(0, maxChars) + "\u2026"`.
- `ListPage.renderCellContent` re-truncates a `render` result only when it is a **string**. A React element is returned as-is. So a Meteorites `job_title` render that returns `<JobTitleText …/>` escapes the 30-character cut, and other columns keep it.
- In `ListPage`, search (`filtered`, around line 206) and sort (`sorted`, around line 217) read raw `row[col.key]`. In the four hand-built pages, sort compares `a.job_title`. Neither path reads rendered text, so AC 7 holds without changes.
- Each in-scope page has exactly one raw title cell:
  - `JobsRecommended.tsx:301`: `<td>{job.job_title || "\u2014"}</td>`
  - `JobsProcessing.tsx:253`: `<td>{job.job_title || "\u2014"}</td>`
  - `JobsSkipped.tsx:363`: `<td onClick={() => setViewingId(job.astral_job_id)}>{job.job_title || "\u2014"}</td>`. This cell renders inside the section loop, so it covers every Skipped table variant.
  - `JobsApplied.tsx:153`: `<td>{job.job_title || "\u2014"}</td>`
- The Meteorites column key is `job_title` (`src/utils/config.py:3498`).
- Modal overlays use `z-index` 1000 and 2000 (stacked), and `UserPrompt` uses 2100. The portaled `TokenTextarea` menu uses `zIndex: 3000`. The tooltip uses 3000 so it stays above modals when AST-1983 hosts it in headers.
- [AST-1967](https://linear.app/astralcareermatch/issue/AST-1967) is on `origin/dev`. [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971) (Created column) is in User Testing and **not** on `origin/dev` yet. It edits the same four pages and `config.py`. If it lands before build, `sync-child.sh` may produce adjacent-line conflicts. Resolve them by keeping both sides (AST-1971's column plus this plan's cell change). If a conflict touches the title `<td>` itself in a way this plan's steps no longer match, stop and comment (execution contract).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `UI_CONFIG["job_title_truncate_chars"] = 50` with an `AST-1981` comment | utils |
| `src/ui/frontend/src/lib/uiConfig.ts` | `UiConfig.job_title_truncate_chars?`; new `resolveJobTitleTruncateChars` | ui (lib) |
| `src/ui/frontend/src/components/JobTitleText.tsx` | **New** shared renderer: cut + portaled wrapped tooltip | ui (component) |
| `src/ui/frontend/src/App.css` | New `.job-title-tooltip` class | ui (style) |
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Job Title `<td>` uses `JobTitleText` (serves Ready + Review) | ui (page) |
| `src/ui/frontend/src/pages/JobsProcessing.tsx` | Job Title `<td>` uses `JobTitleText` | ui (page) |
| `src/ui/frontend/src/pages/JobsSkipped.tsx` | Job Title `<td>` uses `JobTitleText` | ui (page) |
| `src/ui/frontend/src/pages/JobsApplied.tsx` | Job Title `<td>` uses `JobTitleText` | ui (page) |
| `src/ui/frontend/src/pages/JobsMeteorites.tsx` | `job_title` render branch in column `useMemo` returns `JobTitleText` | ui (page) |

**Scope gate:** every row above is named in this ticket's `## Scope`, and each change is the kind Scope describes. No other files. `ListTableTruncatedCell`, `truncateForDisplay`, `resolveCellTruncateChars`, `ListPage`, and all modal/header files stay untouched.

## Stage 0: Lint baseline (no commit)

**Done when:** `debug/spikes/ast-1982/lint-before.txt` holds the `npm run lint` output from the synced tree, before any edits.

1. In `src/ui/frontend`, run `mkdir -p ../../../debug/spikes/ast-1982 && npm run lint > ../../../debug/spikes/ast-1982/lint-before.txt 2>&1; true`. `debug/` is gitignored, so do not commit this file.

## Stage 1: Config value, resolver, shared component, tooltip style

**Done when:** `python -c "import src.utils.config"` exits 0, `npm run build` exits 0, and `JobTitleText` exists. No page uses it yet.

1. In `src/utils/config.py`, directly after the line `    "list_table_cell_truncate_chars": 30,`, insert:

   ```python
       # AST-1981: job-title display cut (JobTitleText) — longer titles show the first N chars + "…" with a full-title tooltip.
       "job_title_truncate_chars": 50,
   ```

2. In `src/ui/frontend/src/lib/uiConfig.ts`, add the field to `UiConfig` after `list_table_cell_truncate_chars?: number`:

   ```ts
     /** AST-1981: job-title display cut served from UI_CONFIG; read via resolveJobTitleTruncateChars. */
     job_title_truncate_chars?: number
   ```

3. In the same file, append at the end:

   ```ts
   /** Job-title cut length; falls back to 50 until UI config loads (mirrors resolveCellTruncateChars). */
   export function resolveJobTitleTruncateChars(ui: UiConfig | null): number {
     const n = ui?.job_title_truncate_chars
     return typeof n === "number" && n > 0 ? n : 50
   }
   ```

   ⚠️ **Decision:** The fallback `50` lives in `lib/uiConfig.ts`. That path is outside the `pages`/`components` directories AC 5's `rg` checks. Mirroring `resolveCellTruncateChars` (fallback equals the configured value) means titles don't flash uncut and then re-cut on first load.

4. Create `src/ui/frontend/src/components/JobTitleText.tsx` with exactly:

   ```tsx
   import { useEffect, useState, type ReactNode } from "react"
   import { createPortal } from "react-dom"
   import { truncateForDisplay } from "../lib/listTableLayout"
   import { getUiConfig, loadUiConfig, resolveJobTitleTruncateChars } from "../lib/uiConfig"

   const TOOLTIP_GAP_PX = 4

   /** AST-1981: shared job-title renderer — cuts at UI_CONFIG job_title_truncate_chars; full title in a portaled, wrapped tooltip only when cut. */
   export default function JobTitleText({ title, fallback }: { title: string | null | undefined; fallback: ReactNode }) {
     const [, forceUpdate] = useState(0)
     // Same module-level UI config cache as ListPage; re-render once it resolves.
     useEffect(() => { loadUiConfig(() => forceUpdate(n => n + 1)) }, [])
     // Viewport coords of the open tooltip; null = closed.
     const [pos, setPos] = useState<{ top: number; left: number } | null>(null)
     // position:fixed would detach from the text on scroll — close instead (capture catches table/modal scrollers).
     useEffect(() => {
       if (!pos) return
       const close = () => setPos(null)
       window.addEventListener("scroll", close, true)
       return () => window.removeEventListener("scroll", close, true)
     }, [pos])

     // Caller owns the empty-title fallback ("—", company, …); never invented here.
     if (!title) return <>{fallback}</>
     const { display, full } = truncateForDisplay(title, resolveJobTitleTruncateChars(getUiConfig()))
     // Short title: plain text — no wrapper, no tooltip, no native title attribute.
     if (display === full) return <>{full}</>
     return (
       <>
         <span
           onMouseEnter={e => {
             const r = e.currentTarget.getBoundingClientRect()
             setPos({ top: r.bottom + TOOLTIP_GAP_PX, left: r.left })
           }}
           onMouseLeave={() => setPos(null)}
         >
           {display}
         </span>
         {/* Portaled to body so table / modal overflow can't clip it. */}
         {pos && createPortal(
           <div role="tooltip" className="job-title-tooltip" style={{ top: pos.top, left: pos.left }}>{full}</div>,
           document.body,
         )}
       </>
     )
   }
   ```

   ⚠️ **Decision:** The tooltip is placed at the hovered span's bottom-left, with no viewport-edge clamping or flipping. Susan's rule is no heuristics without approval, and the Job Title column sits at the left of every in-scope table. If UAT shows edge overflow, that is a follow-up.
   ⚠️ **Decision:** The tooltip closes on any scroll (capture listener). A `position: fixed` tooltip would otherwise float away from its text while the table scrolls under a still pointer. This is the only behavior beyond AC 3's mouse-out rule. Joan or Susan can strike it, which deletes the second `useEffect`.
   ⚠️ **Decision:** `fallback` is a **required** prop, so every caller must state its own fallback. This enforces "the component never invents one."

5. In `src/ui/frontend/src/App.css`, directly after the `.nav-deploy-tickets-tooltip-line { white-space: nowrap; }` block (around line 433–435), insert:

   ```css
   /* AST-1981: JobTitleText full-title tooltip — portaled to body (position: fixed); z-index above modal stacks (1000/2000/2100). */
   .job-title-tooltip {
     position: fixed;
     z-index: 3000;
     max-width: 320px;
     padding: 6px 8px;
     background: var(--bg-elevated, var(--bg-deep));
     border: 1px solid var(--border);
     border-radius: 4px;
     box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
     font-size: 12px;
     line-height: 1.45;
     color: var(--text-primary);
     white-space: normal;
     overflow-wrap: anywhere;
     pointer-events: none;
   }
   ```

   ⚠️ **Decision:** `max-width: 320px` is a fixed pixel value, so AC 3's computed `max-width` is not `none`. At 12px, a title over 100 characters wraps to at least two lines. `pointer-events: none` keeps the tooltip from stealing the hover and blinking.

6. Compile: `python -c "import src.utils.config"` from the repo root, then `npm run build` in `src/ui/frontend`. Both must exit 0.
7. Commit: `code(AST-1982): JobTitleText shared renderer + job_title_truncate_chars UI config`, then publish per build-child.

## Stage 2: Apply to list tables

**Done when:** all five pages render titles through `JobTitleText`. `rg -l "JobTitleText" src/ui/frontend/src` lists all five pages. `rg -n '\{job\.job_title \|\| "\\u2014"\}' src/ui/frontend/src/pages` returns nothing. Build and lint are clean against the Stage 0 baseline.

1. In each of `JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, and `JobsApplied.tsx`, add `import JobTitleText from "../components/JobTitleText"` on its own line, directly after the **last** `import … from "../components/…"` line in that file.
2. `JobsRecommended.tsx`: replace `<td>{job.job_title || "\u2014"}</td>` with `<td><JobTitleText title={job.job_title} fallback={"\u2014"} /></td>`.
3. `JobsProcessing.tsx`: same replacement as step 2.
4. `JobsApplied.tsx`: same replacement as step 2.
5. `JobsSkipped.tsx`: replace `<td onClick={() => setViewingId(job.astral_job_id)}>{job.job_title || "\u2014"}</td>` with `<td onClick={() => setViewingId(job.astral_job_id)}><JobTitleText title={job.job_title} fallback={"\u2014"} /></td>`. The `onClick` is unchanged.
6. Sorters, `aria-label`s (for example `JobsRecommended.tsx:287` `Select ${job.job_title || job.astral_job_id}`), and row/cell click handlers stay as they are on all four pages.
7. `JobsMeteorites.tsx`:
   - Add `import JobTitleText from "../components/JobTitleText"` after `import JobAnalysisReportModal from "../components/JobAnalysisReportModal"`.
   - In the `columns` `useMemo`, directly after the `if (c.key === "job_state") { … }` block and before `return col`, insert:

     ```tsx
             // AST-1981: job title cut at the job-title length (not ListPage's 30) — element render bypasses ListPage string truncation.
             if (c.key === "job_title") {
               col.render = value => <JobTitleText title={typeof value === "string" ? value : null} fallback="—" />
             }
     ```

     The `"—"` literal matches the sibling `astral_job_id` / `job_state` branches in this file.
8. Verify:
   - `python -c "import src.utils.config"` exits 0.
   - In `src/ui/frontend`, `npm run build` exits 0.
   - `npm run lint > ../../../debug/spikes/ast-1982/lint-after.txt 2>&1; true`, then compare problems with line:col stripped (so line shifts in edited files don't count as new): `S=../../../debug/spikes/ast-1982; diff <(rg "^\s+\d+:\d+" $S/lint-before.txt | sed -E 's/^\s+[0-9]+:[0-9]+\s+//' | sort) <(rg "^\s+\d+:\d+" $S/lint-after.txt | sed -E 's/^\s+[0-9]+:[0-9]+\s+//' | sort)` must show no `>` line. Also confirm no problem appears under the `JobTitleText.tsx` file heading in `lint-after.txt`.
   - `rg -n "\.slice\(" src/ui/frontend/src/components/JobTitleText.tsx` returns nothing.
   - `rg -n "job_title.*\.slice\(|\b50\b" src/ui/frontend/src/pages src/ui/frontend/src/components` returns no line added by this ticket. Check with `git diff origin/dev -- src/ui/frontend/src/pages src/ui/frontend/src/components | rg "^\+.*(\b50\b|job_title.*\.slice\()"`, which must return nothing.
9. Commit: `code(AST-1982): Job Title cells on Ready/Review/Processing/Skipped/Applied/Meteorites use JobTitleText`, then publish per build-child.

## Acceptance criteria map

| AC | Satisfied by |
|----|--------------|
| 1 Long titles cut at 50 | S1.1 config + S1.3 resolver + S1.4 `truncateForDisplay`; S2 applies to all six surfaces |
| 2 Short titles untouched | S1.4 short branch returns bare text (no span, tooltip, or `title`) |
| 3 Tooltip full/wrapped/unclipped | S1.4 portal to `document.body` + mouse-out close; S1.5 `white-space: normal`, `max-width: 320px` |
| 4 Meteorites 50 vs 30 | S2.7 element render bypasses `ListPage` string cut; other columns untouched |
| 5 One source, one cut | S1.1 single config value; S1.4 cuts only through `truncateForDisplay`; S2.8 `rg` checks |
| 6 Every surface uses component | S2.2–S2.7; S2.8 `rg` checks |
| 7 Sort/search full title | No sorter or search change (raw values; see Codebase facts) |
| 8 Build/lint clean | S0 baseline + S1.6 / S2.8 |

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]

**Ticket:** AST-1982  
**Overall:** APPROVED  
**Corpus:** e1f2699fad  
**Publish ref:** `5f4b9bf00ba81d86679534e4361437f859d21b1b`

## Canon scores

Frozen list is empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not an §4a list-missing ESCALATE because the parent explicitly declared an empty scope with rationale.

## Traceability

AC1–8 → Stages 0–2 and **Acceptance criteria map** (parent AC5 headers / AC6 info-tab Title → N/A this child per **Boundaries** and AST-1983; parent AC7–10 align with child AC5–8).

### Findings

**discuss** | Plan **Codebase facts** header (`verified at branch tip 3a78a9640`)  
Stale vs publish tip `5f4b9bf`; facts still match the tree (ListPage string re-truncate bypass, line cites). Refresh the cited tip on the next plan edit so execution doesn’t chase the wrong SHA.

**acceptable** | Stage 1 resolver fallback `50` in `uiConfig.ts`  
Mirrors `resolveCellTruncateChars` / 30; AC5 `rg` scope is pages/components only; config key remains source of truth after load.

**acceptable** | Tooltip scroll-close `useEffect`  
Beyond AC3 mouse-out only; documented ⚠️ Decision; does not contradict AC3.

**acceptable** | Empty canon list vs `astral.config.config-source-of-truth` / `astral.ui.frontend-file-placement`  
Plan follows those conventions (UI_CONFIG key, `components/JobTitleText.tsx`); parent locked **none** at Discussion — not rescored here per §4b.

### R6 (summary)

Definition fidelity: implements child **Scope** only; no modal/header files; scope gate honored. DRY: reuses `truncateForDisplay` / `loadUiConfig` precedent; no duplicate slice path. No sibling creep (AST-1983 explicit). Stages are executable with cited line anchors and verification commands. Estimate confirm present; no `!!-NONE` conf block (optional convention only per recent plan-child direction).

**Identity:** Plan Ready, assignee Joan Clarke — OK. No `[plan-discuss]` rounds.

context_tokens≈22000

---

[plan-rubric] PROCEED (Commit: 5f4b9bf) List tables plan ready

## Review

- **Branch:** `origin/sub/AST-1981/AST-1982-job-title-renderer`
- **Build commits:** `f13a4ec7d` (Stage 1 `JobTitleText` + `job_title_truncate_chars` UI config + resolver + `.job-title-tooltip`), `2d9f84400` (Stage 2 Job Title cells on Recommended / Processing / Skipped / Applied / Meteorites)
- **Build notes:** `python -c "import src.utils.config"` exits 0 (`UI_CONFIG["job_title_truncate_chars"] == 50`); `npx tsc -b --noEmit` and `npm run build` exit 0. `npm run lint` before/after: 31 problems both, line:col-stripped diff empty, none in `JobTitleText.tsx`. AC 5/6 `rg` checks: five pages list `JobTitleText`; no raw `{job.job_title || "\u2014"}` cell; no `.slice(` in the component; no added `50` / `job_title…slice(` under `pages` / `components`.
- **Deviation:** none in product code. Environment only: the epic worktree had no `node_modules`, so `npm ci` ran from the lockfile before the Stage 0 baseline (no tracked changes). `validate-sub-log.sh --stage=build` was scoped with `dev` instead of `ftr/AST-1981`, because `origin/ftr/AST-1981` does not exist yet (no sibling merged, so the range is the same). Joan's "stale tip" note: the codebase facts still matched at build tip `4a0dac401`.
- **For QA:** AC 3 tooltip checks (portal under `document.body`, `white-space: normal`, `max-width: 320px`, multi-line over 100 chars, removed on mouse-out) and AC 4 Meteorites 50-vs-30 need a browser. No manual smoke run in this headless build. The tooltip also closes on any scroll (plan Stage 1 Decision).


## Radia review

[code-rubric]

**Ticket:** AST-1982  
**Publish ref:** `01a29571bebc7d1b22776d005100f9b2a7759998` (`origin/sub/AST-1981/AST-1982-job-title-renderer`, tip `merge-tests(AST-1982): origin/tests 5f39a89a9` atop `f13a4ec7d` + `2d9f84400` product commits)  
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (`canon/` tree at publish tip; no `docs/canon-index.md` on ref; frozen list empty — no id resolution run)  
**Overall:** CLEAN  

## Canon scores

Frozen list empty (child **Citations:** none; parent **Canon Scope:** none — locked at Discussion). No directive rows to score; not a §5.3 ESCALATE (parent rationale: no directive applies to these files). Joan plan-stage: same.

## Column diff vs plan stage

(aligned) — Joan recorded an empty frozen list with no per-id grades; code review adds no canon rows.

## Frame diff

(none) — Product diff matches the plan **Files Changed** table and scope gate; no new Description checklist rows required beyond what `resolve-child` already validates against parent AC1–8 / child AC map.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **sibling test carry:** `tests/component/frontend/pages/created-column.ts` and Created-column assertions merged into page tests (AST-1979); `tests/component/data/database/test_jobs.py` (`TestAst1980MeteoriteJobCreatedAt`); `tests/component/utils/test_config.py` (`test_meteorites_columns_gain_created_before_state_changed_ast1980`); `tests/component/ui/api/test_api_admin.py`, `test_api_meteorite.py`, `test_AdminTaskPrompts.test.tsx` — expected `merge-tests` carry; no sibling **product** paths in `src/**` beyond this ticket’s planned set.
- **tooltip a11y:** Hover-only full title (no keyboard focus path) matches plan AC3 and documented decisions; UAT may still want a follow-up if keyboard users need parity — out of scope for this child unless parent scope changes.
- **Corpus line vs Joan validate:** Joan cited `e1f2699fad` at plan time; publish tip canon tree is `bd68954…` — immaterial here because the frozen canon list is empty.

## What's solid

- **Plan fidelity:** `UI_CONFIG["job_title_truncate_chars"] = 50`, `resolveJobTitleTruncateChars`, `JobTitleText` (truncate via `truncateForDisplay`, portaled `.job-title-tooltip`, scroll-close, required `fallback`), `.job-title-tooltip` CSS, and all five list surfaces wired as specified; `ListPage` / modal headers untouched (AST-1983).
- **AC coverage in tests:** `test_JobTitleText.test.tsx` (cut boundary, portal, mouse-out, scroll-close, config-driven length, CSS contract read from `App.css`); shared `job-title-cell.ts` on four hand-built pages; Ready full-title sort + Meteorites 50-vs-30 + Zanzibar search; `test_api_system` + `test_uiConfig` for served key/resolver.
- **Estimate footprint:** Confirmed **3** — scope stays UI config + one component + five page touch points + tests/bible; no API or schema churn.

## Recommended actions (Chuckles — not Radia)

- Append this block to `docs/features/interface/ast-1982-shared-job-title-renderer-list-tables.md`, commit `docs(AST-1982): Radia review — clean`, push publish ref.
- Post slim upshot below via `linear_proxy.py --as radia save-comment`; move **Tests Passed** → **Review Posted**; datt **§3h** → **PROCEED** path toward **User Testing** (no `resolve-child` unless Susan/Chuckles override).

context_tokens≈28000

---

```
[code-rubric] PROCEED (Commit: 01a29571b) Clean list-title cut
```
