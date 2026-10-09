# AST-1981 — All Job Titles in UI should trail with an ellipsis after 50 chars

<!-- linear-archive: AST-1981 archived 2026-10-08 -->

## Linear archive (AST-1981)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1981/all-job-titles-in-ui-should-trail-with-an-ellipsis-after-50-chars  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Long job titles stretch the Jobs list tables and the job modal headers. A title like "Senior Staff Software Engineer, Platform Infrastructure & Developer Experience (Remote, US)" pushes every other column off the screen and makes the table hard to scan. This epic shows every job title in the UI as its first 50 characters followed by an ellipsis (`…`). Hovering a shortened title shows the full title in a styled tooltip that wraps onto several lines at a fixed width. The browser's single-line native tooltip doesn't meet that bar. Titles of 50 characters or fewer show exactly as they do today, with no tooltip.

## Functional scope

1. **One title rule.** A job title longer than 50 characters shows as its first 50 characters plus `…`. A title of 50 characters or fewer shows unchanged. The 50 lives in the served UI config (one value), not in page code.
2. **Wrapped full-title tooltip.** Hovering a shortened title shows the full title in a tooltip with a fixed maximum width. The text wraps onto as many lines as it needs and is never clipped by the table's or modal's scroll container. Titles that are not shortened get no tooltip.
3. **Jobs list tables.** The Job Title cell on **Ready**, **Review**, **Processing**, **Skipped** (every table variant), **Applied**, and **Meteorites** follows the rule. On Meteorites this replaces today's generic 30-character native-tooltip truncation for the job title column only. Other Meteorites columns keep the 30-character rule. Sorting and search still use the full title.
4. **Job headers.** The job title in the **Job Detail** modal header, the **Meteorite** modal header (title part only; ` — <employer>` stays whole), and the **Recommended Job Report** header follows the rule.

**Out of scope:** the editable Title input and the read-only **Title** field on the Job Detail Info tab. These stay full, because that field is where the full title is read and edited. Also out of scope: the browser tab title, the extension UI (it renders no job titles), and the generic 30-character truncation on other `ListPage` columns.

**Sequencing:** run this after [AST-1967](https://linear.app/astralcareermatch/issue/AST-1967), [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971), and [AST-1972](https://linear.app/astralcareermatch/issue/AST-1972) land on `dev`. They are in User Testing now and edit the same list pages and the Job Detail modal.

## Component scope

* `src/utils/config.py` — **modified** — `UI_CONFIG` gains the job-title truncate length (50).
* `src/ui/frontend/src/lib/uiConfig.ts` — **modified** — `UiConfig` type gains the key, plus a resolver with a fallback when config isn't loaded yet.
* `src/ui/frontend/src/components/JobTitleText.tsx` — **new** — the one shared renderer: shortens the title per config and shows the wrapped full-title tooltip on hover.
* `src/ui/frontend/src/App.css` — **modified** — tooltip styling (fixed max width, normal wrapping, elevated surface like `.nav-deploy-tickets-tooltip`).
* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — Job Title cell renders through the shared component (serves Ready and Review).
* `src/ui/frontend/src/pages/JobsProcessing.tsx` — **modified** — Job Title cell through the shared component.
* `src/ui/frontend/src/pages/JobsSkipped.tsx` — **modified** — Job Title cell through the shared component.
* `src/ui/frontend/src/pages/JobsApplied.tsx` — **modified** — Job Title cell through the shared component.
* `src/ui/frontend/src/pages/JobsMeteorites.tsx` — **modified** — `job_title` column gets a render through the shared component, so `ListPage`'s 30-char string truncation no longer applies to it.
* `src/ui/frontend/src/components/Modal.tsx` — **modified** — `title` prop widens from string to a renderable node so a header can host the shared component.
* `src/ui/frontend/src/components/JobDetailModal.tsx` — **modified** — modal header title through the shared component.
* `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` — **modified** — header title's job-title part through the shared component; employer suffix unchanged.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified** — report title through the shared component (covers `JobAnalysisReportModal` and the `/jobs/detail/:jobId` deeplink).

No backend route changes. `/api/system/ui_config` already serves `**UI_CONFIG` wholesale. `ListTableTruncatedCell` and `truncateForDisplay` stay unchanged. The new component reuses `truncateForDisplay` for the cut, so there is no second slicing function.

## Technical scope

* `config.py` — new `UI_CONFIG` key holding the job-title truncate length, value 50, with a one-line `AST-1981` comment beside the existing `list_table_*` keys.
* `uiConfig.ts` — `UiConfig` gains the optional key. A new resolver returns it when it's a positive number and otherwise returns the fallback, mirroring `resolveCellTruncateChars`.
* `JobTitleText.tsx` — new component taking the raw title (string or null). It loads UI config the same way `ListPage` does. It cuts via `truncateForDisplay` at the resolved length. When cut, it shows a hover tooltip (`role="tooltip"`) holding the full title, portaled to `document.body` like `Toast` / `TokenTextarea` so table and modal overflow can't clip it, and positioned against the hovered text. When not cut, it renders plain text with no tooltip and no `title` attribute. Empty or null titles keep each caller's existing fallback (`—`, company, etc.). The caller decides the fallback; the component never invents one.
* `App.css` — new tooltip class: fixed `max-width`, `white-space: normal`, word wrapping, and the elevated surface/border/shadow used by `.nav-deploy-tickets-tooltip`.
* `JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, `JobsApplied.tsx` — each Job Title `<td>` content is modified to render the shared component with the same `—` fallback. Sorters, `aria-label`s, and click handlers are unchanged.
* `JobsMeteorites.tsx` — the existing column-mapping `useMemo` gains a `job_title` render branch, beside the `astral_job_id` / `job_state` branches, that returns the shared component (`—` fallback).
* `Modal.tsx` — `ModalProps.title` widens to a React node. The `<h2>` renders it unchanged, and string callers are unaffected.
* `JobDetailModal.tsx` — the `Modal` title expression is modified so the job-title case renders through the shared component. The company / "Job Detail" fallbacks are unchanged.
* `MeteoriteDetailModal.tsx` — `modalTitle` is modified to return a node in which the job-title part renders through the shared component, followed by the untouched ` — <employer>` text. The other fallbacks are unchanged.
* `RecommendedJobReportHeader.tsx` — the `recommended-report-title` span content renders through the shared component.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. Of the 21 in-force directives (`canon_clerk.py index`), the only frontend pattern is `patt.artifact.ui-consistency` (artifact editors). This epic touches no artifact surface. The local precedent it follows without citing as law: config-served display limits (`list_table_cell_truncate_chars` → `resolveCellTruncateChars`) and the existing `truncateForDisplay` cut.
* **New patterns proposed** — none.
* **Applicable statutes** — none. Every file is frontend or a `UI_CONFIG` value. No logging, entity, dispatch, or batch surface is touched, so none of the logging, entity, dispatch, or batch statutes reaches it.

**Canon Scope:** none — locked at Discussion.

## Acceptance criteria

 1. **Long titles cut at 50.** Take a job whose `job_title` is longer than 50 characters, in each list table on Ready, Review, Processing, Skipped (each table variant), Applied, and Meteorites. Its Job Title cell text equals `job_title.slice(0, 50) + "…"`. **Fail:** any other length, a missing `…`, or the full title shown.
 2. **Short titles untouched.** A job whose title is 50 characters or fewer shows its exact title, and hovering it renders no `[role="tooltip"]` element and no `title` attribute. **Fail:** a `…`, a tooltip, or a native title on a short title.
 3. **Tooltip shows full, wrapped, unclipped.** Hovering a cut title renders one `[role="tooltip"]` whose `textContent` equals the full `job_title`. The element is a descendant of `document.body` and is **not** inside the table or modal subtree. Its computed `white-space` is `normal` and its computed `max-width` is a fixed pixel value (not `none`). A title over 100 characters renders on more than one line (element `offsetHeight` > one line-height). Mouse-out removes it. **Fail:** truncated or clipped tooltip text, a native browser tooltip instead, single-line overflow, or a tooltip that stays after mouse-out.
 4. **Meteorites job title at 50, other columns at 30.** On Jobs → Meteorites, a row with a 45-character `job_title` shows the full 45 characters with no `…`. A 60-character title shows 50 characters plus `…`. Any other column value over 30 characters still shows 30 characters plus `…`. **Fail:** job title cut at 30, or other columns changed.
 5. **Headers follow the rule.** With a title over 50 characters: the Job Detail modal `<h2>` text, the Recommended Job Report `.recommended-report-title` text, and the Meteorite modal `<h2>` text before `—` each start with `job_title.slice(0, 50) + "…"`. The Meteorite header's employer suffix is whole. Hovering the title shows the AC-3 tooltip. **Fail:** any full or differently-cut header title, or a cut employer.
 6. **Info-tab Title field stays full.** In the Job Detail modal, the read-only Title field and the edit input both show the complete `job_title`. **Fail:** a `…` or cut value in either.
 7. **One source for 50, one cut function.** `GET /api/system/ui_config` returns the new job-title key with value `50`. Changing it in `UI_CONFIG` to `20` and reloading cuts every in-scope title at 20 (manual check, reverted). `rg -n "job_title.*\.slice\(|\b50\b" src/ui/frontend/src/pages src/ui/frontend/src/components` returns no hit added by this epic, and `rg -n "\.slice\(" src/ui/frontend/src/components/JobTitleText.tsx` returns nothing (it cuts via `truncateForDisplay`). **Fail:** a hardcoded 50 or a second slicing path.
 8. **Every in-scope surface uses the shared component.** `rg -l "JobTitleText" src/ui/frontend/src` lists all of `JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, `JobsApplied.tsx`, `JobsMeteorites.tsx`, `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, and `RecommendedJobReportHeader.tsx`. `rg -n '\{job\.job_title \|\| "\\u2014"\}' src/ui/frontend/src/pages` returns nothing. **Fail:** any file missing, or a raw title cell left.
 9. **Sort and search use the full title.** On Ready, sorting by Job Title orders rows the same as on `origin/dev` at branch point. On Meteorites, searching for a word that appears only after character 50 of a title still returns that row. **Fail:** a changed order or a missed search hit.
10. **Builds clean; no new lint.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem that is absent on `origin/dev` (diff the problem lists). **Fail:** a non-zero exit or any new lint problem.

## Open questions

none

## Proposed child tickets

#### 1!: **Shared job-title renderer + list tables - Ada**

After [AST-1967](https://linear.app/astralcareermatch/issue/AST-1967) and [AST-1971](https://linear.app/astralcareermatch/issue/AST-1971) land. Builds the config-driven 50-character rule and the wrapped, portaled full-title tooltip as one shared component, and applies it to the Job Title cell on Ready, Review, Processing, Skipped, Applied, and Meteorites. Does not touch any modal or report header (#2).
**Citations:** none — frontend and a `UI_CONFIG` value only; no in-force directive reaches these files.
**Scope:** `src/utils/config.py` (new `UI_CONFIG` job-title truncate key, value 50); `src/ui/frontend/src/lib/uiConfig.ts` (type key + resolver with fallback, mirroring `resolveCellTruncateChars`); `src/ui/frontend/src/components/JobTitleText.tsx` (**new** — cuts via `truncateForDisplay` at the resolved length, portaled `role="tooltip"` with the full title only when cut, caller-supplied fallback); `src/ui/frontend/src/App.css` (tooltip class: fixed max-width, normal wrapping, elevated surface); `src/ui/frontend/src/pages/JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, `JobsApplied.tsx` (Job Title `<td>` renders the shared component, `—` fallback; sorters / aria / clicks unchanged); `src/ui/frontend/src/pages/JobsMeteorites.tsx` (`job_title` render branch in the column-mapping `useMemo` returns the shared component).
Estimate: 3

#### 2: **Job headers use the shared renderer - Hedy**

After #1 and [AST-1972](https://linear.app/astralcareermatch/issue/AST-1972) land. Applies the shared component to the Job Detail modal header, the Meteorite modal header (title part only), and the Recommended Job Report header. Widens `Modal`'s title so a header can host it. Leaves the Info-tab Title field and input full. Does not touch list pages, config, or the component itself (#1).
**Citations:** none — frontend only.
**Scope:** `src/ui/frontend/src/components/Modal.tsx` (`title` prop widens to a React node; `<h2>` unchanged); `src/ui/frontend/src/components/JobDetailModal.tsx` (Modal title job-title case through the shared component; fallbacks unchanged); `src/ui/frontend/src/components/MeteoriteDetailModal.tsx` (`modalTitle` returns a node: shared component for the title part + untouched ` — <employer>`); `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` (`recommended-report-title` content through the shared component).
Estimate: 2

**New patterns:** none.

**Monolith check:** Functional scope has 4 items across 2 children. #1 owns the rule, the tooltip, and the list tables (items 1–3). #2 owns the headers (item 4). #2 depends on #1's component, so it runs second.

**Scope partition check:** all 13 Component scope files are claimed exactly once. #1 claims `config.py`, `uiConfig.ts`, `JobTitleText.tsx`, `App.css`, and the five `pages/Jobs*.tsx` files. #2 claims `Modal.tsx`, `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, and `RecommendedJobReportHeader.tsx`. Every Technical scope item maps to the child that owns its file.

---

## Original brief

With a tooltip for the full title, reasonably line-wrapped.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
