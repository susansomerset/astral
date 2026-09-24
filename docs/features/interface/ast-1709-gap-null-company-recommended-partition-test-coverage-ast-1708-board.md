# AST-1709 — Gap: null-company Recommended partition test coverage (AST-1708 board)

<!-- linear-archive: AST-1709 archived 2026-09-24 -->

## Linear archive (AST-1709)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1709/gap-null-company-recommended-partition-test-coverage-ast-1708-board  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1707 — Recommended Jobs generates an error  
**Blocked by / blocks / related:** parent: AST-1707

### Description

## What this implements

Test/bible gap opened by fix-board on AST-1708: Recommended Jobs meteorite partition never asserts null `company` through `isMeteoriteJob` / sections `useMemo` (fixtures are string-only), so the AST-1707 crash was unreproed in suite.

## Implementation

- [X] Product null-guard present on tip via sync of `origin/ftr/AST-1707-recommended-jobs-startswith-null` (AST-1708): `isMeteoriteJob` uses `(job.company ?? "").startsWith(prefix)` — no further product rewrite
- [X] Betty `[bug-repro]` / bible already on tip — engineer did not edit test-tree
- [X] `[bug-repro]` green on tip after ftr sync (`AST-1708/AST-1709: null company does not throw; stays out of Meteorites`)

## Scope

### Component scope

* `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — **modified** — add coverage that a recommended-list row with null `company` does not throw and partitions correctly (non-meteorite when prefix set).
* `docs/test-bible/frontend/pages.md` — **modified** — record AST-1708/AST-1707 null-company partition coverage under the JobsRecommended / AST-1057 entry.

### Technical scope

* `test_JobsRecommended.test.tsx` — **new test case(s)** under existing JobsRecommended suite: fixture with `company: null` (and meteorite prefix present) must render without throw; assert it does not land in Meteorites section solely via null company.
* `docs/test-bible/frontend/pages.md` — **modified bible entry** naming the new node id / pattern for Betty/qa-fix successors.

## Notes for planning

Sibling of AST-1708 (product null-guard). Board: `[board-betty] TESTS: REVISE` — docs/test-bible/frontend/pages.md (AST-1057 / test_JobsRecommended.test.tsx) — missing coverage — null company through isMeteoriteJob.

### Comments

#### radia — 2026-09-18T04:48:55.822Z
[code-rubric] PROCEED (Commit: b284f800) null-company repro OK

#### betty — 2026-09-18T04:44:35.749Z
[bug-repro]
`origin/sub/AST-1707/AST-1709-null-company-recommended-partition-test` @ `b75382bf` · repro lands red, awaits fix

#### betty — 2026-09-18T04:40:14.176Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md (AST-1057 / test_JobsRecommended.test.tsx) — missing coverage — null-company `isMeteoriteJob` partition case not yet landed (this gap’s Proposed change)

#### joan — 2026-09-18T04:39:48.546Z
[board-joan]  CANON: OK

#### katherine — 2026-09-18T04:38:22.535Z
`origin/sub/AST-1707/AST-1709-null-company-recommended-partition-test` @ `3f8d602f` · null-company partition test gap

---

_Implementation detail may live in git history on `origin/dev`._
