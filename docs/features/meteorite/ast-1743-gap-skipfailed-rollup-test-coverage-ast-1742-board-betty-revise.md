# AST-1743 — gap: skip→failed rollup test coverage (AST-1742 board-betty REVISE)

<!-- linear-archive: AST-1743 archived 2026-09-24 -->

## Linear archive (AST-1743)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1743/gap-skipfailed-rollup-test-coverage-ast-1742-board-betty-revise  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1740 — Meteorites deemed NOT_A_JOB should be Fails  
**Blocked by / blocks / related:** parent: AST-1740

### Description

## What this implements

Test-hole gap from \[board-betty\] TESTS: REVISE on AST-1742 — missing skip→failed coverage for check_email / ingest / \_land_all (NOT_A_JOB).

## Citations

(from AST-1742 plan-fix / Betty board)

## Scope

## Component scope

* `docs/test-bible/core/inbox.md` — modified or new coverage notes for `check_email` skip→failed (NOT_A_JOB / BOT_BLOCKED).
* `docs/test-bible/core/meteorite.md` — modified if ingest `counter="failed"` needs bible mention.
* `docs/test-bible/ui/api/api_inbox.md` — modified if Land `_land_all` `counter="failed"` needs bible mention.
* astral-tests component tests for inbox / meteorite / api_inbox — new or extended nodes asserting skip→failed (Betty-owned).

## Technical scope

* New or modified pytest nodes under astral-tests that fail against pre-fix product (skip still counted passed) and pass once AST-1742 product fix lands — assert `check_email` / ingest / `_land_all` map NOT_A_JOB (and BOT_BLOCKED per parent To-be) to failed, not passed.
* Bible entries updated to name those nodes. No product code in this gap ticket.

## Acceptance criteria

- [X] At least one \[bug-repro\]-style test asserts NOT_A_JOB (skip) increments failed not passed on the scoped rollup path(s).
- [X] Bible entries name the new/extended nodes.
- [X] Does not change product code (that is AST-1742).

## Boundaries

Product counter retarget is AST-1742. This gap is tests + bible only.

## Notes for planning

Betty board What: docs/test-bible/core/inbox.md (+ core/meteorite.md, ui/api/api_inbox.md) — missing coverage — check_email / ingest / \_land_all skip→failed never asserted.

## Git branch (authoritative)

Parent `ftr/AST-1740-meteorites-not-a-job-should-be-fails`. Child ref in epic registry.

### Comments

#### radia — 2026-09-21T01:13:56.484Z
[code-rubric] PROCEED (Commit: b60038b5) skip-fail repros OK

#### katherine — 2026-09-21T01:11:25.073Z
`origin/sub/AST-1740/AST-1743-gap-skip-failed-rollup-tests` @ `b60038b5` · [bug-repro] red@f31756b1 → green after sync AST-1742 product (3/3 + related suites 16 passed)

#### katherine — 2026-09-21T01:11:22.680Z
`origin/sub/AST-1740/AST-1743-gap-skip-failed-rollup-tests` @ `b60038b5` · [bug-repro] 3/3 green vs AST-1742 product

#### betty — 2026-09-21T01:07:25.316Z
[bug-repro]
`origin/sub/AST-1740/AST-1743-gap-skip-failed-rollup-tests` @ `f31756b1f9decc8291f1dda1dcb8cfc0fe571ed9` · skip→failed green vs AST-1742

#### joan — 2026-09-21T01:03:05.198Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:01:44.332Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/inbox.md (+ core/meteorite.md, ui/api/api_inbox.md) — missing coverage — skip→failed nodes for check_email / ingest / _land_all not landed yet; plan names them, bible/tests still lack them

#### betty — 2026-09-21T01:00:26.413Z
`origin/sub/AST-1740/AST-1743-gap-skip-failed-rollup-tests` @ `2359eaf21001e0c23c4d66a831f390c6a21385a5` · skip→failed test gap plan

---

_Implementation detail may live in git history on `origin/dev`._
