# AST-1742 — fix: NOT_A_JOB / BOT_BLOCKED rollup counts as fails (Meteorites deemed NOT_A_JOB should be Fails)

<!-- linear-archive: AST-1742 archived 2026-09-24 -->

## Linear archive (AST-1742)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1742/fix-not-a-job-bot-blocked-rollup-counts-as-fails-meteorites-deemed-not  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1740 — Meteorites deemed NOT_A_JOB should be Fails  
**Blocked by / blocks / related:** parent: AST-1740

### Description

## What this implements

Retarget meteorite mailbox / stage rollup counters so only `READY` / `SCRAPE_LINK` count as passes; `NOT_A_JOB` / `BOT_BLOCKED` count as fails; ERROR-family states count as errors. Approved ancestor: AST-1714.

## Citations

(from AST-1714 / bug Description — plan-fix freezes canon)

## Scope

## Component scope

* `src/core/inbox.py` — modified: `check_email` (and any helper it uses) currently increments `passed` for skipped / `NOT_A_JOB` and leaves `total_failed` at 0; that is the primary operator-facing rollup.
* `src/core/meteorite.py` — modified: `ingest_candidate_email_message` (and any `_row` counter mapping for skip / `NOT_A_JOB`) still returns `counter="passed"` on skip; same counting contract if that path still feeds UI/dispatch summaries.
* Tests under the meteorite mailbox / stage suites (astral-tests, Betty-owned) — modified only if existing assertions lock skip-as-passed; plan-fix / fix-board decide.
* `src/ui/api/api_inbox.py` — modified: Manage Email Land `_land_all` must honor ingest `counter="failed"` (today only special-cases `passed`/`error`; other values fall through to skip_outcomes → passed).

## Technical scope

* `src/core/inbox.py` — modified function(s) in the `check_email` loop: change the branch that today counts archive-success after skip / job-save as `passed` so it branches on meteorite state / stage outcome (`READY`/`SCRAPE_LINK` → passed, `NOT_A_JOB` → failed, ERROR-family / `stage["error"]` → errors). No new tables or fields.
* `src/core/meteorite.py` — modified function `ingest_candidate_email_message` (and/or its `_row` helper usage): stop mapping skip / `NOT_A_JOB` to `counter="passed"`; map to failed (and ERROR outcomes to errors) to match the inbox rollup. No schema change.
* `src/ui/api/api_inbox.py` — modified function `_land_all`: add an `elif counter == "failed"` branch that sets `is_passed = False` so NOT_A_JOB / BOT_BLOCKED land rollups count as fails after ingest retarget. No new tables or fields.

## Acceptance criteria

- [X] `NOT_A_JOB` (and `BOT_BLOCKED` per parent To-be) increments failed, not passed, on the `check_email` / ingest rollup paths in Scope.
- [X] Only `READY` and `SCRAPE_LINK` increment passed.
- [X] ERROR-family outcomes (`NEW_EMAIL_ERROR`, `SCRAPE_ERROR`, stage `error`) increment errors.
- [X] Archive-after-skip behavior unchanged; only counters change.

## Proposed change (make-fix)

- [X] `src/core/inbox.py` — `check_email`: skip → failed, landable → passed after archive
- [X] `src/core/meteorite.py` — ingest skip → `counter="failed"`
- [X] `src/ui/api/api_inbox.py` — `_land_all` `elif counter == "failed"`

## Boundaries

Does not change classify / row-state selection. Does not resurrect AST-1714's ftr. Scope is explicit above — plan-fix plans against it.

## Notes for planning

Parent AST-1740 Description has As-is / To-be / Proposed steps. Seed context from docs/features/meteorite/ast-1714-inbox-check-email-runner.md.

## Git branch (authoritative)

Parent `ftr/AST-1740-meteorites-not-a-job-should-be-fails`. Child ref recorded in epic registry at bug-fix dispatch.

### Comments

#### radia — 2026-09-21T01:08:20.318Z
[code-rubric] REVIEW (Commit: c32117ad) missing bug-repro tests

Sibling gap AST-1743 since landed [bug-repro] nodes @ f31756b1. Product retarget OK. Restack/merge note for Chuckles at merge-child.

#### katherine — 2026-09-21T00:59:23.329Z
`origin/sub/AST-1740/AST-1742-fix-not-a-job-rollup-counts` @ `c32117ad` · code complete

#### joan — 2026-09-21T00:56:17.385Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T00:56:06.620Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/inbox.md (+ core/meteorite.md, ui/api/api_inbox.md) — missing coverage — check_email / ingest / _land_all skip→failed (NOT_A_JOB) never asserted; TestAst1714CheckEmail only landable/error/dedup; no ingest counter=failed or Land counter=failed node

#### katherine — 2026-09-21T00:54:29.905Z
`origin/sub/AST-1740/AST-1742-fix-not-a-job-rollup-counts` @ `950c0bd0cd09d49216e760b314adc83fe73b0a7e` · plan-fix Plan Ready

#### katherine — 2026-09-21T00:52:38.431Z
[scope-gate] cleared — Scope amended (AST-1742 + AST-1740) to include `src/ui/api/api_inbox.py` (`_land_all` `counter=="failed"`). Proposed change finalized; Plan Ready.

#### katherine — 2026-09-21T00:52:37.409Z
`origin/sub/AST-1740/AST-1742-fix-not-a-job-rollup-counts` @ `1f45cb43104bf8fd9ee565efbe59c8fe09124134` · plan-fix scope-gate

---

_Implementation detail may live in git history on `origin/dev`._
