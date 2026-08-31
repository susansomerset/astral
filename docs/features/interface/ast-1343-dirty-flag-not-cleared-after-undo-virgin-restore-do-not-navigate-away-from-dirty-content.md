# AST-1343 — Dirty flag not cleared after Undo / virgin restore (Do not navigate away from dirty content)

<!-- linear-archive: AST-1343 archived 2026-08-31 -->

## Linear archive (AST-1343)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1343/dirty-flag-not-cleared-after-undo-virgin-restore-do-not-navigate-away  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1315 — Do not navigate away from dirty content  
**Blocked by / blocks / related:** parent: AST-1315

### Description

## Susan's comment (verbatim)

[bug]

Dirty flag does not reset if the users uses Undo, or restores the screen to its virgin state.  It should.

## As-is / to-be

**As-is:** After Undo or restoring Candidate Profile to its virgin/clean values, the dirty flag stays set and leave still prompts to save.
**To-be:** When on-screen values match the virgin/last-saved snapshot again (Undo or manual restore), the dirty flag clears and leave does not prompt.

## Suggested engineer

Katherine Johnson (AST-1336 Candidate Profile dirty-leave wiring — owns dirty vs snapshot on Profile).

## Proposed change

- [X] Add `normalizeProfileEditTreeForDirtyCompare` in `CandidateProfile.tsx` (null/undefined → `""` only).
- [X] Compare `isDirty` via stringify of normalized `values` vs normalized snapshot.
- [X] Do not change `editValuesFromCandidate`, `persistProfile`, PUT body, Cancel, helper wiring, FormFields, or other pages.

## QA test manifest

**Publish:** `origin/sub/AST-1315/AST-1343-dirty-flag-not-cleared-after-undo-virgin-restore` @ `42ed5384` (`merge-tests(AST-1343): origin/tests c7bed34b`)

**\[bug-repro\]** (must flip red→green after make-fix):

* `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — `AST-1343: nullish nested field touch+clear clears dirty (virgin empty)`
* Verified **red** on pre-fix tree: after type+clear Phone loaded as `null`, `isDirty` stayed `true` (expected `false`).
* make-fix: **green** after compare-time normalize.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  --testNamePattern="AST-1343"
```

**Bible:** `docs/test-bible/frontend/pages.md` shasum `c45e5c1ee45520a0808af5ed69225bf9e1ec51e5`

### Comments

#### radia — 2026-08-12T23:47:14.993Z
[code-rubric] PROCEED (Commit: a0adf5ca) virgin dirty clear fix

#### betty — 2026-08-12T23:43:04.677Z
[bug-repro]
`origin/sub/AST-1315/AST-1343-dirty-flag-not-cleared-after-undo-virgin-restore` @ `42ed5384` · repro lands red, awaits fix

#### joan — 2026-08-12T23:41:45.606Z
[board-joan]  CANON: OK

#### betty — 2026-08-12T23:41:22.931Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md (AST-1336 CandidateProfile dirty-leave) — missing coverage — nullish nested field touch+clear/Undo back to virgin empty still leaves isDirty true (raw stringify); Cancel/exact-string cases do not exercise FormFields null↔"" coerce

#### katherine — 2026-08-12T23:40:01.284Z
`origin/sub/AST-1315/AST-1343-dirty-flag-not-cleared-after-undo-virgin-restore` @ `9a8f03529eda44e8051affc8d2246ae3857ae3ed` · Virgin restore dirty plan

---

_Implementation detail may live in git history on `origin/dev`._
