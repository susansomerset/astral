# AST-1342 — Print button placement: put next to Regenerate, match page chrome

<!-- linear-archive: AST-1342 archived 2026-08-31 -->

## Linear archive (AST-1342)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1342/print-button-placement-put-next-to-regenerate-match-page-chrome  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1314 — Add a Print button to Base Resume Content  
**Blocked by / blocks / related:** parent: AST-1314

### Description

## Susan report (verbatim)

[bug]

When adding buttons to a page, or any UI additions or changes, consider in the planning process the appropriate location, if not specified, to make that change or to put that button.   In this case, the button was placed at the top of the screen, unstyled like the others, etc.

Meanwhile, put the Print button next to the Regenerate button, please.

## As-is

The Print control sits at the top of Base Resume Content and does not match the placement/styling of the page’s other primary controls.

## To-be

Print sits next to the Regenerate control, visually consistent with the existing Base Resume Content chrome (same control family/placement expectations as sibling buttons on that page).

## Proposed change

- [X] Optional `headerActions` on `ArtifactEditor` rendered in `dep-actions` after Generate/Regenerate
- [X] Base Resume Content Print moved into `headerActions` (`btn secondary`); orphan page-level row removed
- [X] On-page `printError` kept above editor; Print fetch/validate/blob behavior unchanged

## Suggested engineer

Katherine

### Comments

#### radia — 2026-08-12T23:27:35.807Z
[code-rubric] PROCEED (after ftr rebase) Print next to Regenerate

CLEAN — placement-only `headerActions` / dep-actions fix. Prior REVIEW was polluted sub history (meteorite); Chuckles rebuilt onto ftr. No fix-now remaining.

#### betty — 2026-08-12T23:22:16.614Z
[bug-repro]
`origin/sub/AST-1314/AST-1342-print-button-placement-next-to-regenerate` @ `5b5351aa` · repro lands red, awaits fix

#### betty — 2026-08-12T23:20:31.512Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md (AST-1337 suite) — broken no-candidate Print disabled (headerActions dies with ArtifactEditor early return) + missing dep-actions/next-to-Regenerate placement assert for this repro

#### joan — 2026-08-12T23:20:26.696Z
[board-joan]  CANON: OK

#### katherine — 2026-08-12T23:19:30.375Z
`origin/sub/AST-1314/AST-1342-print-button-placement-next-to-regenerate` @ `9abb45870452ed52d1bf43f01be45d0dc1d5a063` · plan-fix ready

---

_Implementation detail may live in git history on `origin/dev`._
