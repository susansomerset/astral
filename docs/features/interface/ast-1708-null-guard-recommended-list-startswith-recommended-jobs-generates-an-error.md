# AST-1708 — Null-guard Recommended list startsWith (Recommended Jobs generates an error)

<!-- linear-archive: AST-1708 archived 2026-09-24 -->

## Linear archive (AST-1708)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1708/null-guard-recommended-list-startswith-recommended-jobs-generates-an  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1707 — Recommended Jobs generates an error  
**Blocked by / blocks / related:** parent: AST-1707

### Description

## What this implements

Null-guard the Recommended Jobs list partition so a null `company` (or equivalent string field) cannot throw `Cannot read properties of null (reading 'startsWith')` inside the memoized filter path.

## Implementation

- [X] `JobsRecommended.tsx` `isMeteoriteJob`: `(job.company ?? "").startsWith(prefix)` — null/empty is not a meteorite-prefix match
- [X] Leave `JobMeteoritePane` / `RecommendedJobReportHeader` / `JobAnalysisReportModal` alone (already null-safe; stack was list partition)

## Scope

### Component scope

* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — list-page meteorite/section partition filter is the stack-shaped crash site (`filter` + `useMemo`); null-safe the string used for `.startsWith`.
* `src/ui/frontend/src/components/JobMeteoritePane.tsx` — **modified only if** the crash is modal-pane rather than list (AST-1692 `isNavigableHttpLink`); else leave alone.
* `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` — **modified only if** title/listing href helpers still call `.startsWith` on a raw null (AST-1695 / AST-1704); else leave alone.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` — **modified only if** shared listing/`window.open` helpers on the report path are the throw site; else leave alone.

### Technical scope

* `JobsRecommended.tsx` — **modified function** (meteorite / section membership predicate used inside a memoized filter): stop calling `.startsWith` on a null `company` (or equivalent field); null/empty means “not a meteorite-prefix match,” not a throw.
* `JobMeteoritePane.tsx` / `RecommendedJobReportHeader.tsx` / `JobAnalysisReportModal.tsx` — **modified helper only if** repro shows the throw after list is safe: ensure http(s) link helpers return false/null when input is null before any `.startsWith` (exact helper names are plan-fix’s call).

## Notes for planning

Approved ancestor (archived): AST-1057 — `docs/features/meteorite/ast-1057-recommended-page-meteorites-section.md` (`isMeteoriteJob` / `job.company.startsWith(prefix)`). Parent mini-epic: AST-1707.

### Comments

#### radia — 2026-09-18T04:39:22.602Z
[code-rubric] REVIEW (Commit: 4e8a88bd) missing bug-repro test

Product null-guard matches plan. fix-now: board TESTS:REVISE bar not on tip — orphaned path spun coverage to sibling gap AST-1709 (in flight). discuss: no frozen Canon Scope on bug ticket. advisory: company sort localeCompare still null-unsafe (out of AST-1708 scope).

#### betty — 2026-09-18T04:31:50.101Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md (AST-1057 / test_JobsRecommended.test.tsx) — missing coverage — null `company` through `isMeteoriteJob` / sections partition never asserted (fixtures are string-only)

#### joan — 2026-09-18T04:31:46.218Z
[board-joan]  CANON: OK

#### katherine — 2026-09-18T04:30:27.169Z
`origin/sub/AST-1707/AST-1708-null-guard-recommended-startswith` @ `1ddb3353` · null-guard company startsWith

---

_Implementation detail may live in git history on `origin/dev`._
