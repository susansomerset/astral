# AST-1989 — Stamp candidate_id on dispatch logs + job_context for anticipate_scan (Candidate ID is not populating in the log output)

<!-- linear-archive: AST-1989 archived 2026-10-13 -->

## Linear archive (AST-1989)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1989/stamp-candidate-id-on-dispatch-logs-job-context-for-anticipate-scan  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1986 — Tokens are unexpectedly empty.  
**Blocked by / blocks / related:** parent: AST-1986; blocks: AST-1993

### Description

## What this implements

Fix for [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986) — wire the `log_candidate_id` contextvar (defined by AST-1598, never set) so log rows/lines inside candidate-scoped runs carry the candidate id; and, per AST-1986 To-be #2, restore a populated `job_context` for `anticipate_scan` so job-source tokens are not all empty. As-is / To-be / open question live on the bug's Description.

## Citations

`astral.standards.logging-via-utils`, `astral.standards.utils-data-late-import-only` (from ancestor AST-1598).

## Scope

### Component scope

* `src/core/dispatcher.py` — modified: the four entity-run blocks that set/reset `log_batch_id` also need to set/reset `log_candidate_id`.
* `src/core/agent.py` — modified: `do_task` / hop paths that set `log_batch_id` set `log_candidate_id` too; and (if symptom 2 is in scope) the single-job scoping that gates `job_context`.
* `src/core/candidate.py` — modified: candidate-side batch runs that set `log_batch_id` (around the two existing `log_batch_id.set` blocks) set `log_candidate_id` too.
* `src/core/intake.py` — modified: intake batch runs that set `log_batch_id` stamp candidate when one is known.
* `src/core/meteorite.py` — modified: its `log_batch_id` setter helper stamps candidate when one is known.
* `src/utils/logging.py` — modified only if Susan wants candidate id in the console line: formatter change (DB stamp already works).

### Technical scope

* `src/core/dispatcher.py` — modified functions: the dispatch entity-run branches set `log_candidate_id` from the task's candidate id at run start and clear it in the existing `finally` reset, so every log in that run is stamped.
* `src/core/agent.py` — modified functions: `do_task` batch/hop setup sets and clears `log_candidate_id` alongside `log_batch_id`; possibly a modified `_single_job_in_scope` / `_job_context_for_call` (or the caller that builds `ctx`) so the chain-head hop gets a single-job context.
* `src/core/candidate.py`, `src/core/intake.py`, `src/core/meteorite.py` — modified functions: same set/clear pairing wherever a candidate-scoped run sets `log_batch_id`.
* `src/utils/logging.py` — modified formatter(s) (conditional): include the contextvar candidate id in console output; no schema change (`app_log.candidate_id` already exists, nullable).

## Boundaries

* No `app_log` / `job` schema change — `candidate_id` columns already exist (AST-1598).
* Does not add non-admin candidate filtering of logs.

## Notes for planning

Approved ancestor: AST-1598 (`docs/features/candidate/ast-1598-job-and-app-log-candidate-id.md`). Mirror the `log_batch_id` set/reset shape.

## Git branch (authoritative)

Mini-parent `ftr/AST-1986-log-candidate-id`; this child `sub/AST-1986/AST-1989-log-candidate-id`. Seeded by bug-fix.

### Comments

#### radia — 2026-10-06T04:37:12.868Z
[code-rubric] REVIEW (Commit: f0606c31) pre-try contextvar on ledger fail

#### hedy — 2026-10-06T04:35:09.997Z
`origin/sub/AST-1986/AST-1989-log-candidate-id` @ `f0606c318` · lighter check (no qa-fix manifest)

- py_compile clean on the 6 touched files.
- Component suites run in a clean detached worktree: test_debug_logging, test_logging_batch, test_dispatcher, test_agent, test_agent_ast1448, test_agent_ast1879, test_candidate, test_intake, test_meteorite.
  - Pre-fix (`cc256733f`): 77 / 76 failed. Post-fix (`f0606c318`): 77 / 77 failed. **0 new failures.**
  - Logging suites fully green.
- Pre-existing, not this fix (for AST-1993 / Betty): `test_meteorite_email.py` fails at collection (`src.core.meteorite_email` does not exist). The 77 baseline failures are spread across agent / candidate / dispatcher / meteorite.
- Env note: the epic worktree's ignored `data/astral.db` changes results (for example `TestAst1881…merges_into_response_and_stash` returns 409 there and passes in a clean tree). Run comparisons in a clean tree.

#### joan — 2026-10-06T04:24:12.831Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T04:23:39.133Z
[board-betty] TESTS: REVISE
What: no bible entry (docs/test-bible/utils/logging_batch.md says "No dispatcher set sites"; utils/debug_logging.md has no candidate-set console case) — missing coverage — repro has no test: need red-first asserts that dispatcher._dispatch_one, agent do_task (_with_log_debug incl. run_next hop), intake._run_intake_task/validate_preamble_answer, candidate.run_candidate_artifact_generation, and meteorite _hold_log_batch callers stamp app_log.candidate_id and restore the prior contextvar value on exit, plus "name [cid]: message" on both _CONSOLE_FORMATTER and _RailwayJsonFormatter when set. Existing tests (test_debug_logging unset-format + formatter identity, test_logging_batch AST-1598 stamp) not broken by Blast radius. D3 (symptom 2) is product scope, not a test question — no test asked for it.

#### hedy — 2026-10-06T04:22:08.352Z
`origin/sub/AST-1986/AST-1989-log-candidate-id` @ `cf77ec40f9d21443a36ef65e091a2977746b20f9` · plan ready, D3 needs Susan

---

_Implementation detail may live in git history on `origin/dev`._
