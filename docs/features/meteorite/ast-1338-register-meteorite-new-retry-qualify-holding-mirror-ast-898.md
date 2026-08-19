# AST-1338 — Register METEORITE_NEW_RETRY qualify holding (mirror AST-898)

<!-- linear-archive: AST-1338 archived 2026-08-19 -->

## Linear archive (AST-1338)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1338/register-meteorite-new-retry-qualify-holding-mirror-ast-898  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1319 — Implement _RETRY for new meteorite states  
**Blocked by / blocks / related:** parent: AST-1319

### Description

## What this implements

Mirror AST-898's `NEW` → `NEW_RETRY` → `ERROR_QUALIFY_JOB_LISTINGS` pattern for meteorite qualify: register **METEORITE_NEW_RETRY**, route recoverable first-attempt `qualify_meteorite` failures from **METEORITE_NEW** to that holding (not straight to **METEORITE_ERROR_QUALIFY**), companion-claim **METEORITE_NEW**+**METEORITE_NEW_RETRY** on the qualify dispatch row, and second-strike from the holding to **METEORITE_ERROR_QUALIFY**.

## Citations

Ancestor pattern: AST-898 (`docs/features/consult/ast-898-new-retry-qualify-holding.md`). Parent bug: AST-1319.

## Acceptance criteria

1. [x] Recoverable first-attempt `qualify_meteorite` failure from **METEORITE_NEW** lands on **METEORITE_NEW_RETRY**, not **METEORITE_ERROR_QUALIFY**.
2. [x] **METEORITE_NEW_RETRY** is claimable when the Scheduled Action trigger is **METEORITE_NEW**.
3. [x] Recoverable failure already on **METEORITE_NEW_RETRY** goes to **METEORITE_ERROR_QUALIFY** (no retry loop).
4. [x] Clean second-attempt succeed/fail from the holding reaches the same pass/fail outcomes as a first attempt.
5. [x] Admin/UI job state lists include **METEORITE_NEW_RETRY** with a clear label.

## Proposed change (make-fix)

1. [x] `METEORITE_NEW.retry_state` → **METEORITE_NEW_RETRY**
2. [x] Register **METEORITE_NEW_RETRY** (`prior_states`: **METEORITE_NEW**; no nested retry)
3. [x] Extend priors: **METEORITE_QUALIFIED** / **METEORITE_FAILED_QUALIFY** / **METEORITE_ERROR_QUALIFY** / **BOT_BLOCKED**
4. [x] `IN_REVIEW_STATES` + `JOBS_IN_REVIEW_UI_SECTIONS` ("Meteorite New (retry)")
5. [x] No `JOBS_IN_REVIEW_GRADE_FIELD` entry; no Skipped Retry map edit; no DB companion row; no `consult.py` product delta

## Boundaries

Does not re-open archived AST-898. Does not change regular `NEW_RETRY` / `qualify_job_listings`. Does not own Skipped operator Retry maps (AST-1156). Tests owned by gap AST-1339.

## Notes for planning

* As-is: meteorite qualify errors go straight to METEORITE_ERROR_QUALIFY with no retry holding.
* To-be: METEORITE_NEW → METEORITE_NEW_RETRY (first strike) → METEORITE_ERROR_QUALIFY (second strike), twin of AST-898.
* Seed from ancestor doc content in plan-fix prompt.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1319-implement-retry-for-new-meteorite-states`,
child `sub/AST-1319/<child-segment>`. Created at bug-fix dispatch.

### Comments

#### radia — 2026-08-12T15:03:56.299Z
[code-rubric] PROCEED (Commit: 62c6764e) METEORITE_NEW_RETRY registry

CLEAN — config-only AST-898 twin for meteorite qualify. No fix-now. Tests/bible on sibling AST-1339.

#### betty — 2026-08-12T14:57:34.652Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/config.md (+ core/consult.md) — missing METEORITE_NEW→METEORITE_NEW_RETRY fail-dest/claim coverage (repro not in TestConsultBatchFailDest / no AST-898 twin); Blast radius breaks TestAst1053MeteoriteGdlJobStates priors/UI + BOT_BLOCKED prior equality

#### joan — 2026-08-12T14:57:15.817Z
[board-joan]  CANON: OK

context_tokens≈12000

#### hedy — 2026-08-12T14:56:03.794Z
`origin/sub/AST-1319/AST-1338-register-meteorite-new-retry-qualify-holding` @ `1f6ae4a9` · METEORITE_NEW_RETRY holding plan

---

_Implementation detail may live in git history on `origin/dev`._
