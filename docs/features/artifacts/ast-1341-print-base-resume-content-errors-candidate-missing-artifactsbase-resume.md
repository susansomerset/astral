# AST-1341 — Print Base Resume Content errors: Candidate missing artifacts.base_resume

<!-- linear-archive: AST-1341 archived 2026-08-31 -->

## Linear archive (AST-1341)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1341/print-base-resume-content-errors-candidate-missing-artifactsbase  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1314 — Add a Print button to Base Resume Content  
**Blocked by / blocks / related:** parent: AST-1314

### Description

## Susan report (verbatim)

[bug]

Clicking the button while looking at the base_resume I'm looking at generates an error:

```
Astral error diagnostic
timestamp: 2026-08-12T17:40:04.654Z
message: Candidate missing artifacts.base_resume
route: /artifacts/base_resume_content
astral_candidate_id: abrams
```

## As-is

On Base Resume Content for candidate abrams, Print fails with `Candidate missing artifacts.base_resume` instead of opening print HTML.

## To-be

Print opens print-ready HTML for the selected candidate’s base resume (or a clear content-missing message that does not look like a hard crash), without that false-missing error when the operator is already viewing base resume content.

## Proposed change

- [X] `build_base_resume` ingests list/dict via `ingest_legacy_label_content_base_resume` before emit
- [X] Empty/unusable content raises `No printable base resume content for this candidate` (not key-path missing)
- [X] Base Resume Content Print maps that (and legacy missing) to the same operator sentence; no blank tab

## Suggested engineer

Katherine

### Comments

#### radia — 2026-08-12T23:29:43.242Z
[code-rubric] PROCEED (Commit: b1dc009b) list-shaped base_resume Print

CLEAN after Chuckles rebuilt sub onto ftr (1341-only). Ingest + operator error copy. No fix-now remaining. [bug-repro] pins list-shaped print.

#### betty — 2026-08-12T23:24:29.485Z
[bug-repro]
`origin/sub/AST-1314/AST-1341-print-base-resume-missing-artifacts-error` @ `c709cabe` · repro lands red, awaits fix

#### betty — 2026-08-12T23:22:18.944Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/builder.md (TestBuildBaseResume) — missing list-shaped base_resume print success + broken match on Candidate missing artifacts.base_resume (new empty copy); AST-1337 page error assert may need same text

#### joan — 2026-08-12T23:22:13.881Z
[board-joan]  CANON: OK

#### katherine — 2026-08-12T23:21:34.956Z
`origin/sub/AST-1314/AST-1341-print-base-resume-missing-artifacts-error` @ `bc88510050dba4a6eccc2432156c213378779c35` · plan-fix ready

---

_Implementation detail may live in git history on `origin/dev`._
