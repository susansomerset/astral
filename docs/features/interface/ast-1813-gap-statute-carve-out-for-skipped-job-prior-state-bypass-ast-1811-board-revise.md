# AST-1813 — gap: statute carve-out for skipped-job prior-state bypass (AST-1811 board REVISE)

<!-- linear-archive: AST-1813 archived 2026-10-07 -->

## Linear archive (AST-1813)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1813/gap-statute-carve-out-for-skipped-job-prior-state-bypass-ast-1811  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1809 — Allow Skipped Job state change to ANY job state, do not filter/validate  
**Blocked by / blocks / related:** parent: AST-1809

### Description

## What this implements

Canon gap from `[board-joan] CANON: REVISE` on AST-1811: record a bounded carve-out in `astral.state.job-prior-states-enforced` for the skipped-job operator edit — only `persist_skipped_job_edits` → `transition_job_state(..., enforce_prior_states=False)` when the job's current state is in `SKIPPED_STATES`; every other caller keeps default enforcement.

## Scope

### Component scope

* `canon/statutes/astral/state/astral.state.job-prior-states-enforced.md` — modified: statute text is universal today; needs the one bounded operator-edit exception (Susan's explicit product call on AST-1809).
* `canon/directives/draft/stat.state.job-prior-states-enforced.md` — modified only if `docs/canon-index.md` § Resolving ids resolves the id through this directive copy; keep the two in agreement.

### Technical scope

* Statute file — modified section: add a carve-out / exception note naming the single allowed bypass (skipped-edit persist path, current state ∈ `SKIPPED_STATES`, target must be a `JOB_STATES` key) and restating that the default enforces for all other callers.
* Draft directive copy — modified section (conditional): mirror the same exception wording.

## Boundaries

No product code (AST-1811) and no tests (sibling test gap). `pattern.state.entity-state-transitions` gets at most an optional cross-reference line, only if plan-fix finds the pattern's `related_statutes` linkage requires it — otherwise untouched.

## Notes for planning

Joan's full triage is appended to `docs/features/interface/ast-1453-persist-skipped-job-field-and-state-edits.md` § Fix-board Joan findings (AST-1811). Not ESCALATE — product intent explicit; this is recording the exception. Patch that same doc with a `## Bug: <this id>` block.

## Git branch (authoritative)

Parent `ftr/AST-1809-skipped-any-state`, child `sub/AST-1809/AST-1813-skipped-any-state-canon`. Created at bug-fix.

### Comments

#### radia — 2026-09-27T01:22:45.715Z
[code-rubric] PROCEED (Commit: a0bc2f0e) statute carve-out clean

#### joan — 2026-09-27T01:19:55.744Z
[board-joan]  CANON: OK

#### betty — 2026-09-27T01:19:39.949Z
[board-betty] TESTS: OK
Canon-only (one statute file). No test or bible entry references `astral.state.job-prior-states-enforced` or its draft copy, and no generic canon validator walks `canon/statutes/` or `canon/directives/draft/`. Behavioural coverage for the carve-out already lives on AST-1812.

#### ada — 2026-09-27T01:18:45.082Z
`origin/sub/AST-1809/AST-1813-skipped-any-state-canon` @ `feebddf2` · statute carve-out plan ready

---

_Implementation detail may live in git history on `origin/dev`._
