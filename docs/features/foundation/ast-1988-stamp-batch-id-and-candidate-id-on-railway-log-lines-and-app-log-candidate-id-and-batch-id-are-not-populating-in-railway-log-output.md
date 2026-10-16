# AST-1988 — Stamp batch_id and candidate_id on Railway log lines and app_log (Candidate_id and batch_id are not populating in Railway log output)

<!-- linear-archive: AST-1988 archived 2026-10-13 -->

## Linear archive (AST-1988)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1988/stamp-batch-id-and-candidate-id-on-railway-log-lines-and-app-log  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1987 — Candidate_id and batch_id are not populating in Railway log output  
**Blocked by / blocks / related:** parent: AST-1987; blocks: AST-1991

### Description

## What this implements

Railway log lines and `app_log` rows carry the run's correlation ids. Today `_RailwayJsonFormatter` in `src/utils/logging.py` (AST-1778) emits only `level` + `message`, so Railway lines have no `batch_id` / `candidate_id`. And `log_candidate_id` (AST-1598) is defined and stamped on DB flush, but no code ever sets it, so every `app_log.candidate_id` is `NULL`, even for candidate-owned runs like `check_job_resume`.

## Scope

### Component scope

* `src/utils/logging.py` — modified: the Railway JSON formatter must read the batch and candidate contextvars it currently ignores; module docstring's "dispatcher/UI wiring is out of scope" note goes stale.
* `src/core/dispatcher.py` — modified: the four dispatcher entity-run blocks set `log_batch_id` with `candidate_id` already in scope but never set `log_candidate_id`, and must clear it on teardown.
* `src/core/agent.py` — modified: the hop batch start and the ad-hoc/catalog batch start set `log_batch_id` with `candidate_id` in scope (this is the path that produced the `check_job_resume` rows in the report); same set/clear pairing needed.
* `src/core/candidate.py` — modified: the candidate-entity batch start sets `log_batch_id` with `candidate_id` in scope; same set/clear pairing. The "session" sentinel batch stays unstamped.
* `src/core/meteorite.py` — modified only if needed: `_hold_log_batch` sets its own batch when no parent dispatch batch exists; plan-fix confirms whether a candidate id is available there or whether it always runs under a dispatcher batch that already stamped one.

### Technical scope

* `src/utils/logging.py` — modified function `_RailwayJsonFormatter.format`: add the two contextvar values to the emitted JSON object so Railway lines carry the same correlation keys the `app_log` rows do. Docstring updated to drop the "set sites out of scope" caveat.
* `src/core/dispatcher.py` — modified functions (the entity-run dispatch blocks around each `log_batch_id.set(entity_batch_id)`): add a paired `log_candidate_id` set at batch start and clear in the matching `finally`, so every dispatched candidate-owned run is stamped.
* `src/core/agent.py` — modified functions (hop batch opener and the catalog/ad-hoc batch opener, plus their teardown): same paired set/clear, so LLM-call logs (`src.core.agent`, `src.external.openrouter`, `src.external.llm_compat`) get the candidate.
* `src/core/candidate.py` — modified function (candidate-entity batch opener and its teardown): same paired set/clear.
* `src/core/meteorite.py` — possibly a modified function `_hold_log_batch` (and its reset sites): pair a candidate stamp only if a candidate id is reachable there; otherwise no change.
* No new tables or fields — `app_log.candidate_id` already exists (AST-1598).

## Acceptance criteria

1. With `RAILWAY_ENVIRONMENT` set, a log line emitted inside a dispatched batch is one JSON object carrying `batch_id` (and `candidate_id` when the run is candidate-owned) as top-level fields alongside `level` / `message`.
2. A log line emitted outside any batch (contextvars unset) has the same JSON shape as today: no `batch_id` / `candidate_id` keys, or null. Plan-fix picks one and says why.
3. `app_log` rows written during a candidate-owned run (e.g. `check_job_resume`) have `candidate_id` populated. Rows from the `candidate.py` "session" sentinel batch stay `NULL`.
4. A candidate stamp never leaks into the next run on the same thread/context: every `log_candidate_id` set is paired with a clear at the same teardown that clears `log_batch_id`.
5. The off-Railway plain console format (`LEVEL name: message`) is unchanged.

## Boundaries

No new tables or columns (`app_log.candidate_id` exists). No UI / Execution History filter changes. No change to `log_debug` gating or to the level map. No Telescope / gunicorn console changes.

## Notes for planning

No ancestor was checked by Susan. Context only, from bug-find: AST-1598 (`docs/features/candidate/ast-1598-job-and-app-log-candidate-id.md`) added `log_candidate_id` + the DB stamp and explicitly deferred the `.set(...)` sites ("no dispatcher `log_candidate_id.set(...)` sites"). AST-1778 (`docs/features/foundation/ast-1778-railway-faithful-console-transport-in-get-logger.md`) built `_RailwayJsonFormatter` with "at least" `level` + `message`. Full as-is/to-be is in the mini-parent AST-1987 Description.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1987-railway-log-batch-candidate-ids`, child `sub/AST-1987/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-10-06T04:30:04.384Z
[code-rubric] PROCEED (Commit: f9b447782) Plan matches stamp pairing

#### joan — 2026-10-06T04:20:05.165Z
[board-joan]  CANON: OK

context_tokens≈14000

#### betty — 2026-10-06T04:19:47.099Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/debug_logging.md (AST-1778) + docs/test-bible/utils/logging_batch.md (AST-1598) — missing coverage — no test checks the repro: Railway JSON `batch_id`/`candidate_id` added when set and left out when unset (batch-less line byte-identical), or that the dispatcher/agent/candidate/meteorite openers set and clear `log_candidate_id` together with `log_batch_id` (incl. `_hold_log_batch` no-op under a parent batch and the tuple reset).

Existing tests stay green: `TestAst1778RailwayConsoleTransport` asserts `level`/`message` by key with no contextvars set; `TestAst1598LogCandidateId` sets the var directly; no test references `_hold_log_batch` or patches meteorite's `log_batch_id`. Product-scope note for Chuckles: the `src/core/intake.py` gap in Blast radius (preamble + `_run_intake_task`) is a scope call for @susan, not a test call.

#### hedy — 2026-10-06T04:18:18.444Z
`origin/sub/AST-1987/AST-1988-stamp-log-batch-candidate-ids` @ `6fcadfb5` · plan ready, intake gap flagged

---

_Implementation detail may live in git history on `origin/dev`._
