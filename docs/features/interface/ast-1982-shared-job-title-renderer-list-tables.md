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
