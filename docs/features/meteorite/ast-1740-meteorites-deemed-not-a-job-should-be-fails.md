# AST-1740 — Meteorites deemed NOT_A_JOB should be Fails

<!-- linear-archive: AST-1740 archived 2026-09-24 -->

## Linear archive (AST-1740)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1740/meteorites-deemed-not-a-job-should-be-fails  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1558

### Description

Meteorites deemed NOT_A_JOB should be Fails.

Only pass jobs that are READY or SCRAPE, and all ERROR states should be counted as Errors.

## As-is

Mailbox / stage rollups treat a successful `NOT_A_JOB` (classify skip) the same as a successful job save: archive succeeds and the summary increments `total_passed` (or the ingest `_row` counter `"passed"`). `total_failed` stays unused (0) on the `check_email` path. Operator dashboards therefore show not-a-job meteorites as passes.

## To-be

Only rows that land in `READY` or `SCRAPE_LINK` (SCRAPE) count as passes. `NOT_A_JOB` or `BOT_BLOCKED` counts as fails. Every ERROR-family meteorite state (`NEW_EMAIL_ERROR`, `SCRAPE_ERROR`, and any other `*_ERROR` / ERROR outcome on that path) counts as errors — not passes.

## Proposed steps

1. Retarget `check_email` (and any sibling ingest/selected-ids rollup that still marks skip as passed) so outcome → counter is: `READY` / `SCRAPE_LINK` → passed; `NOT_A_JOB` / `BOT_BLOCKED`→ failed; ERROR-family states / stage `error` → errors.
2. Keep archive behavior for skip (still archive after insert); only the summary counters change.
3. Align any matching ingest `_row(..., counter="passed")` on skipped / `NOT_A_JOB` with the same rule.
4. Confirm tests / bible expectations that assert skip-as-passed for meteorite mailbox rolls flip to fail/error as appropriate.

## Component scope

* `src/core/inbox.py` — modified: `check_email` (and any helper it uses) currently increments `passed` for skipped / `NOT_A_JOB` and leaves `total_failed` at 0; that is the primary operator-facing rollup.
* `src/core/meteorite.py` — modified: `ingest_candidate_email_message` (and any `_row` counter mapping for skip / `NOT_A_JOB`) still returns `counter="passed"` on skip; same counting contract if that path still feeds UI/dispatch summaries.
* Tests under the meteorite mailbox / stage suites (astral-tests, Betty-owned) — modified only if existing assertions lock skip-as-passed; plan-fix / fix-board decide.
* `src/ui/api/api_inbox.py` — modified: Manage Email Land `_land_all` must honor ingest `counter="failed"` (today only special-cases `passed`/`error`; other values fall through to skip_outcomes → passed).

## Technical scope

* `src/core/inbox.py` — modified function(s) in the `check_email` loop: change the branch that today counts archive-success after skip / job-save as `passed` so it branches on meteorite state / stage outcome (`READY`/`SCRAPE_LINK` → passed, `NOT_A_JOB` → failed, ERROR-family / `stage["error"]` → errors). No new tables or fields.
* `src/core/meteorite.py` — modified function `ingest_candidate_email_message` (and/or its `_row` helper usage): stop mapping skip / `NOT_A_JOB` to `counter="passed"`; map to failed (and ERROR outcomes to errors) to match the inbox rollup. No schema change.
* `src/ui/api/api_inbox.py` — modified function `_land_all`: add an `elif counter == "failed"` branch that sets `is_passed = False` so NOT_A_JOB / BOT_BLOCKED land rollups count as fails after ingest retarget. No new tables or fields.

## Ancestor candidates

- [X] [AST-1714](https://linear.app/astralcareermatch/issue/AST-1714/inboxcheck-email-runner-rework-meteorite-email) — inbox `check_email` runner: plan explicitly counts skipped / `NOT_A_JOB` as `passed` and leaves `total_failed` at 0
- [ ] [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email) — `stage_meteorite` / ingest: skip path returns `_row(..., counter="passed")` after archiving a `NOT_A_JOB` insert
- [ ] [AST-1558](https://linear.app/astralcareermatch/issue/AST-1558/inbox-candidate-verbs-manage-email-filter-meteorite-ingress-staging) — inbox candidate verbs / selected-ids: skip-as-passed counting for `skip_outcomes`
- [ ] AST-1531 — mailbox cutover: `run_fetch_email` / `land_inbox_message_ids` treat skipped / `skip_outcomes` as passed

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
