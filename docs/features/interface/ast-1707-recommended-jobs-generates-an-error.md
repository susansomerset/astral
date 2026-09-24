# AST-1707 — Recommended Jobs generates an error

<!-- linear-archive: AST-1707 archived 2026-09-24 -->

## Linear archive (AST-1707)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1707/recommended-jobs-generates-an-error  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Original report

Recommended Jobs generates an error:

```
Unexpected Application Error!
Cannot read properties of null (reading 'startsWith')
TypeError: Cannot read properties of null (reading 'startsWith')
    at T (…/assets/index-….js)
    at Array.filter (<anonymous>)
    at Object.useMemo (…)
```

(React Router error boundary on the Recommended Jobs surface.)

## As-is

Opening **Recommended Jobs** throws a client-side `TypeError: Cannot read properties of null (reading 'startsWith')` inside an `Array.filter` / `useMemo` path and the page falls to the React Router error boundary instead of rendering the list.

## To-be

Recommended Jobs loads and partitions/renders its sections without throwing when a job row has a null string field that older code assumed was always a string (most likely `company` on the meteorite-prefix partition, or a related http-link helper on the same surface).

## Proposed steps

1. On the Recommended Jobs list render path, find the `.startsWith` call reached from `Array.filter` / `useMemo` (stack matches a filter over jobs, not a one-off modal open).
2. Null-guard the left-hand string before `.startsWith` (treat null/undefined as non-match / empty), especially the meteorite-prefix predicate that AST-1057 documented as `job.company.startsWith(prefix)`.
3. Re-check any sibling Recommended-surface `startsWith` helpers that recently touched listing/meteorite links (AST-1692 / AST-1695 / AST-1704) only if the list-page guard alone does not clear the crash.
4. Confirm a Recommended list that includes a job with null `company` (and/or null link fields) still renders and partitions correctly.

## Component scope

* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — list-page meteorite/section partition filter is the stack-shaped crash site (`filter` + `useMemo`); null-safe the string used for `.startsWith`.
* `src/ui/frontend/src/components/JobMeteoritePane.tsx` — **modified only if** the crash is modal-pane rather than list (AST-1692 `isNavigableHttpLink`); else leave alone.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified only if** title/listing href helpers still call `.startsWith` on a raw null (AST-1695 / AST-1704); else leave alone.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified only if** shared listing/`window.open` helpers on the report path are the throw site; else leave alone.

## Technical scope

* `JobsRecommended.tsx` — **modified function** (meteorite / section membership predicate used inside a memoized filter): stop calling `.startsWith` on a null `company` (or equivalent field); null/empty means “not a meteorite-prefix match,” not a throw.
* `JobMeteoritePane.tsx` / `RecommendedJobReportHeader.tsx` / `JobAnalysisReportModal.tsx` — **modified helper only if** repro shows the throw after list is safe: ensure http(s) link helpers return false/null when input is null before any `.startsWith` (exact helper names are plan-fix’s call).

## Ancestor candidates

- [X] AST-1057 (parent AST-1052) — Recommended page Meteorites section; plan explicitly defines `isMeteoriteJob` as `job.company.startsWith(prefix)` on `JobsRecommended` — best stack match (`filter` + null `company`)
- [ ] AST-1704 (parent AST-1640) — Track routing + Recommended header/detail http(s) `startsWith`; also made `company_id` nullable, which can surface null `company` on rows the AST-1057 predicate never guarded
- [ ] AST-1692 (parent AST-1685) — Meteorite pane on Recommended modal; `isNavigableHttpLink` uses `.startsWith` after trim (guards null in plan — weaker list-crash fit)
- [ ] AST-1695 (parent AST-1686) — Recommended report listing href helpers use `.startsWith` for http(s) (modal/detail surface — weaker list-crash fit)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
