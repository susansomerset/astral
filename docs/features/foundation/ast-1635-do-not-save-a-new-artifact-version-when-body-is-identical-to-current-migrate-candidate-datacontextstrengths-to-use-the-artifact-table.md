# AST-1635 — Do not save a new artifact version when body is identical to current (Migrate candidate_data.context.strengths to use the artifact table)

<!-- linear-archive: AST-1635 archived 2026-09-24 -->

## Linear archive (AST-1635)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1635/do-not-save-a-new-artifact-version-when-body-is-identical-to-current  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1629 — Migrate candidate_data.context.strengths to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1629

### Description

## Susan UAT comment (verbatim)

\[bug\]

Do not save a new version of the artifact if it is identical to the current version.

## As-is

Operative Strengths save (and the shared write-operative path it uses) always retires the prior `current` row and inserts a new artifact version even when the new body is byte-for-byte identical to the current version.

## To-be

If the body being saved is identical to the current artifact version for that catalog key, do not create a new version — leave the existing `current` row in place (no retire+insert).

## Suggested engineer

Hedy Lamarr (sibling AST-1633 — operative save / hydrate / blob retirement)

## Proposed change (done)

- [X] In `save_candidate_data` str-path: after validate, compare to `get_current_artifact`; if `artifact_data == blob`, return existing `artifact_uuid` without `save_artifact`.
- [X] No Strengths entity info log on no-op path; real inserts unchanged.
- [X] `database.py` / API / React untouched.

### Comments

#### radia — 2026-09-15T00:50:04.653Z
[code-rubric] PROCEED (Commit: 8aa1291cca79) identical save no-op clean

#### betty — 2026-09-15T00:46:34.575Z
[bug-repro]
`origin/sub/AST-1629/AST-1635-no-identical-artifact-version` @ `15cc208ddb1c52f76f18ea834bc9ed1e557e4da1` · repro lands red, awaits fix

#### joan — 2026-09-15T00:44:52.608Z
[validate-plan fix-mode] LANDED — patt.artifact.write-operative identical-to-current no-op before invoke (return existing artifact_uuid; no save_artifact).

#### joan — 2026-09-15T00:43:55.832Z
[board-joan]  CANON: REVISE
What: patt.artifact.write-operative — add identical-to-current no-op before invoke (return existing artifact_uuid; no save_artifact; not in-place UPDATE) — Abstract/Arc currently imply always retire+insert

#### betty — 2026-09-15T00:43:34.681Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md § AST-1633 — missing identical-body no-op (same strengths string → same uuid; existing second-save tests only use changed body)

#### hedy — 2026-09-15T00:41:56.702Z
`origin/sub/AST-1629/AST-1635-no-identical-artifact-version` @ `4f8469f3d8410a415cbc8a76ac80978a8d90bf42` · plan-fix ready

---

_Implementation detail may live in git history on `origin/dev`._
