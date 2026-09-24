# AST-1614 — gap: string-JSON prepare/land repro coverage (Job artifacts are not persisting)

<!-- linear-archive: AST-1614 archived 2026-09-22 -->

## Linear archive (AST-1614)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1614/gap-string-json-prepareland-repro-coverage-job-artifacts-are-not  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1610 — Job artifacts are not persisting  
**Blocked by / blocks / related:** parent: AST-1610

### Description

## What this implements

gap (tests): add repro coverage for finalize-shaped string JSON through prepare/land so `prepare_empty` is exercised — per [board-betty] on AST-1613.

## Scope

### Component scope

* `tests/component/core/test_tracker.py` — modified/new — repro that feeds finalize-shaped string JSON (`agent_payload.resume`) through `_prepare_job_replica_body` / land path.
* `tests/component/core/test_agent.py` — modified/new — do_task catalog-land with string `parsed` (not mocked dict) so prepare_empty→coerce→save is covered.
* `docs/test-bible/core/tracker.md` — modified — bible note for the new coverage.
* `docs/test-bible/core/agent.md` — modified — bible note for the new coverage.

### Technical scope

* `tests/component/core/test_tracker.py` — new or extended test(s): string JSON payload shaped like finalize_job_resume must coerce and prepare a landable body (or document the agent-side coerce contract).
* `tests/component/core/test_agent.py` — new or extended test(s): catalog-land branch with string `parsed` lands via prepare→save_job_artifact (repro for AST-1613 root cause).
* Bible entries — record the new nodes under tracker.md / agent.md.

## Board source

[board-betty] TESTS: REVISE — docs/test-bible/core/tracker.md + agent.md — missing coverage — no test feeds finalize-shaped string JSON through prepare/land.

### Comments

#### radia — 2026-09-09T22:53:44.605Z
[code-rubric] PROCEED (Commit: f5acd78d) String JSON repro OK

#### hedy — 2026-09-09T22:51:27.474Z
`origin/sub/AST-1610/AST-1614-gap-string-json-prepare-land-repro` @ `f5acd78d9d9e792e161132698f548448e68b640e` · bug-repro green (sync+ftr)

#### betty — 2026-09-09T22:50:25.135Z
[bug-repro]
`origin/sub/AST-1610/AST-1614-gap-string-json-prepare-land-repro` @ `94370fca` · TestAst1614StringJsonPrepare + TestAst1614DoTaskStringParsedCatalogLand

#### joan — 2026-09-09T22:47:19.922Z
[board-joan]  CANON: OK

Tests and bible only — no product or canon touch; repro asserts AST-1613 coerce behavior already covered by existing artifact statutes/patterns.

#### betty — 2026-09-09T22:46:47.837Z
[board-betty] TESTS: OK

#### hedy — 2026-09-09T22:46:05.866Z
`origin/sub/AST-1610/AST-1614-gap-string-json-prepare-land-repro` @ `cf4cec9843606a6d96163df1ee44ee1e3ba5e972` · string-JSON repro plan

---

_Implementation detail may live in git history on `origin/dev`._
