# AST-2089 — fix: qualify_job_listings — one listing without a job ID must not fail the whole batch

<!-- linear-archive: AST-2089 archived 2026-10-16 -->

## Linear archive (AST-2089)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2089/fix-qualify-job-listings-one-listing-without-a-job-id-must-not-fail  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2015 — [✅/Somerset] qualify_job_listings COMPLETED: 14 error(s) / 16 processed | qualify_job_listings-67d036c7-5729-4c3e-87e5-96800cea4e45  
**Blocked by / blocks / related:** parent: AST-2015; blocks: AST-2090

### Description

## What this implements

`qualify_job_listings`: one listing the model can't fully process (e.g. no company job ID) must not fail the whole batch. Two layers: (1) prompt — the company job ID is best-effort per listing; omit `company_job_id` on that line and keep grading; a single-listing gap never justifies an envelope-level `agent_performance: failure`. (2) code guard — on an encoded batch task, an envelope `failure` must not wipe out per-line results that decoded cleanly; only the affected entity routes to its fail destination (retry holding / error), and the rest go to pass/fail normally — same isolation shape as AST-1996's per-line decode slip.

## Scope

## Component scope

* `data/admin/agent_task.json` (modified): `qualify_job_listings` row, `cache_prompt` text. This is where the instruction that makes the ID mandatory lives.
* `src/core/agent.py` (modified **only if** step 3 is approved): the AST-1839 rubric-encoded envelope-failure branch in `do_task`, which currently turns one listing's note into a whole-batch `agent_failure`.
* `src/core/consult.py` (modified **only if** step 3 is approved): the `do_task`-failed branch of `_run_batch_consult`, which would route only the named listing to its fail destination and process the rest.

## Technical scope

* `data/admin/agent_task.json`: prompt text change only, no schema change. `company_job_id` is already optional in `TASK_CONFIG["qualify_job_listings"]["response_schema"]`.
* `src/core/agent.py` (conditional): modified function. The encoded-batch envelope-failure path would keep the parsed payload, so per-line results survive, instead of returning `parsed_response: None`.
* `src/core/consult.py` (conditional): modified function. `_run_batch_consult` would split the batch, sending the failed line to retry/error and the surviving lines to pass/fail, reusing `_transition_batch_consult_failures` for the subset.

Susan checked the AST-1155 / AST-1884 / AST-1996 ancestor ("isolation precedent for step 3") on AST-2015, so the conditional `src/core/agent.py` / `src/core/consult.py` lines above are **in scope** for this ticket.

## Boundaries

Does not change `response_schema` (`company_job_id` already optional). Does not add a `company_job_id` fallback for `qualify_job_listings` (AST-1119's UUID-from-`job_link` stays `qualify_meteorite`-only). Does not change retry-holding routing semantics (AST-898 / AST-1839) — only which entities a failed batch routes. Does not reset the 14 stranded `ERROR_QUALIFY_JOB_LISTINGS` jobs in code — that is a one-off data step Susan runs (AST-2015 Proposed step 4), not a migration. Tests / bible are Betty's (fix-board decides whether a gap child is needed).

## Notes for planning

AST-2015 Description (As-is / To-be / Proposed steps) is authoritative. Approved ancestor: `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md` § `## Bug: AST-1996` (Hedy) — per-line isolation of malformed encoded grade lines → per-entity retry, not hop error. Patch that same doc with a `## Bug: <this id>` block. Check `git log -p data/admin/agent_task.json` for whether the 2026-10-07 03:51 prompt edit dropped wording that used to cover a missing job ID (Proposed step 2).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-2015-qualify-listing-isolation`, child `sub/AST-2015/AST-2089-qualify-listing-isolation`. Created at bug-fix.

### Comments

#### radia — 2026-10-09T02:17:02.880Z
[code-rubric] PROCEED (Commit: f3897829d) Salvage matches plan; tests on 2090

#### joan — 2026-10-09T02:11:09.984Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:10:46.230Z
[board-betty] TESTS: REVISE
What: no bible entry (core/agent.md + core/consult.md) — missing coverage — AST-2089 repro has no node: do_task rubric envelope failure + batch_entities + decodable lines → salvaged_response (and None on undecodable/schema-invalid payload), and _run_batch_consult splitting on salvaged (J0 → PASSED_JOBLIST, J1 → FAILED_JOBLIST, J2 → NEW_RETRY with "Agent failure: …" reason, agent_failure/errors/success return shape). Existing TestAst1846DoTaskAgentFailureFlag + consult envelope-failure nodes stay green (parsed_response None holds; mocks lack salvaged_response) — no broken tests.

#### hedy — 2026-10-09T02:09:38.346Z
`origin/sub/AST-2015/AST-2089-qualify-listing-isolation` @ `09d114aee` · prompt fix + salvage clean lines

---

_Implementation detail may live in git history on `origin/dev`._
