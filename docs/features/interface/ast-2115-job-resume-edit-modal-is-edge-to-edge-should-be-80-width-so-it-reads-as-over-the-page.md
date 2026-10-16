# AST-2115 — Job resume edit modal is edge-to-edge; should be 80% width so it reads as over the page

<!-- linear-archive: AST-2115 archived 2026-10-16 -->

## Linear archive (AST-2115)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2115/job-resume-edit-modal-is-edge-to-edge-should-be-80percent-width-so-it  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-2046 — Resume Edit Overhaul  
**Blocked by / blocks / related:** parent: AST-2046

### Description

## Susan's UAT comment (verbatim)

> \[fix\]
>
> When editing a job resume, the modal goes edge-to-edge.  This is great for experienced users, but I would like to have it pop up as more obviously "over" the navigation and content behind it so the user doesn't think they have navigated away.  Better for the modal to be 80% screen width for this one.

## As-is

The job resume edit modal opens full-screen (edge to edge), so it looks like the user has navigated away from the Job Analysis Report.

## To-be

The job resume edit modal opens at 80% of the screen width, visibly over the navigation and the report behind it.

## Suggested engineer

Ada Lovelace. Owner of `JobArtifactEditModal` in [AST-2084](https://linear.app/astralcareermatch/issue/AST-2084). The full-screen `Modal` size is from [AST-2082](https://linear.app/astralcareermatch/issue/AST-2082) (Hedy).

Parent: [AST-2046](https://linear.app/astralcareermatch/issue/AST-2046) (Resume Edit Overhaul).

### Comments

#### radia — 2026-10-10T03:06:43.611Z
[code-rubric] PROCEED (Commit: 9358e516b) 80vw overlay modal

#### ada — 2026-10-10T02:56:38.543Z
`origin/sub/AST-2046/AST-2115-job-modal-80-width` @ `9358e516b` · [bug-repro] green (2/2); manifest 15/15; tsc 0; grep empty. `npm run lint` exits 1 on 29 problems that were already there, all in files AST-2115 does not touch. Modal.tsx and JobArtifactEditModal.tsx lint clean.

#### betty — 2026-10-10T02:38:36.279Z
[bug-repro]
`origin/sub/AST-2046/AST-2115-job-modal-80-width` @ `851301086` · repro lands red, awaits fix

#### joan — 2026-10-10T02:35:45.409Z
[board-joan]  CANON: OK

#### betty — 2026-10-10T02:31:37.908Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-2084 / § AST-2082 — broken test + missing coverage — `test_JobArtifactEditModal` "job resume: stacked full-screen…" asserts `.modal-card` width `100vw` (must become `80vw`, plus 90vh, card border kept, unpadded body); `test_Modal` has no `size="overlay"` case (80vw/90vh, default chrome, FULLSCREEN_BODY), and its AST-2082 fullscreen case must stay 100vw.

#### ada — 2026-10-10T02:24:32.761Z
`origin/sub/AST-2046/AST-2115-job-modal-80-width` @ `e1f78f5da` · new 80vw overlay size

---

_Implementation detail may live in git history on `origin/dev`._
