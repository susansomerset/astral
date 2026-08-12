# AST-1143 — UAT: parse_meteorite_email rejects jobs[].metadata dict (expects str)

<!-- linear-archive: AST-1143 archived 2026-08-11 -->

## Linear archive (AST-1143)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1143/uat-parse-meteorite-email-rejects-jobsmetadata-dict-expects-str  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1128 — gaze_email — candidate-bound dispatch (redesign)  
**Blocked by / blocks / related:** parent: AST-1128

### Description

<!-- uat-validate: stacktrace -->

## What failed

Running candidate-bound `gaze_email` for somerset on a bound html_links inbox message, Ruth `parse_meteorite_email` returned jobs with `metadata` as objects (`{"company":…,"location":…}`). Validation failed:

`do_task validation failed. task_key='parse_meteorite_email' error=jobs[0]: Field 'metadata' must be str, got dict`

Runner logged `ruth_fail=…` and `gaze_email.run … -> error` with `total_errors=1`, `total_passed=0` — no METEORITE_NEW create / archive for that message.

Susan also asked: why wasn’t this caught by test coverage?

## Expected

Bound html_links mail whose Ruth parse yields job links (with optional company/location metadata) validates, scrapes/creates **METEORITE_NEW** (or per-candidate dedupe skip), and archives — same AST-1087 ingest outcomes under the candidate-bound runner.

## Repro

1. Ensure somerset has a `gaze_email` dispatch row and an inbox message From-bound to somerset whose body is HTML with Dice (or similar) job links.
2. Run that somerset `gaze_email` row with debug on.
3. Observe `parse_meteorite_email` validation error on `jobs[].metadata` dict vs str, and message left unprocessed / error outcome.

## Parent AC (quoted inline)

> Bound in-scope message shapes still produce the AST-1087 ingest outcomes for that candidate (**METEORITE_NEW** / archive / ignore rules as already established for bound mail); a single run does not advance jobs into qualify/GDL.

> With `debug=True`, each candidate run, each considered message, and each create/skip/archive/trash/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.

## Diagnosis

* **Hypothesis:** `TASK_CONFIG["parse_meteorite_email"]` schema types `jobs[].metadata` as `str`, but the live Ruth prompt / model returns structured `metadata` objects (company/location). Validation rejects the payload before the runner can scrape/create. Coverage likely asserts config shape only, not a realistic Ruth payload with dict metadata through do_task/gaze_email.
* **Correct outcome:** html_links parse with job links + company/location metadata succeeds end-to-end into METEORITE_NEW (or all-duplicate archive) for that candidate; debug shows found + recorded, not ruth_fail validation.
* **Wrong fix to avoid:** swallow the validation error and continue with empty jobs; delete/loosen all schema checks; leave message forever without fixing the contract; “no more stacktrace” without successful ingest when links are present.
* **Related siblings / contracts:** AST-1136 runner; AST-1089 `parse_meteorite_email` schema/prompt; Betty must add a failing-shape → fixed-shape regression so dict metadata cannot regress silently.

## Boundaries

* This bug does **not** change: From→candidate bind rules, Avail count wiring, unbound retention policy, Manage Email Land Meteorite (AST-1129), qualify/GDL hops.
* "No more stacktrace / no more error" alone is **not** done — Parent AC + Correct outcome must hold.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
