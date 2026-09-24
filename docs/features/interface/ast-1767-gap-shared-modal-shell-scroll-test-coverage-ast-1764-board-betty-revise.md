# AST-1767 — gap: shared Modal shell scroll test coverage (AST-1764 board-betty REVISE)

<!-- linear-archive: AST-1767 archived 2026-09-24 -->

## Linear archive (AST-1767)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1767/gap-shared-modal-shell-scroll-test-coverage-ast-1764-board-betty  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1754 — All modals must be vertically scrollable  
**Blocked by / blocks / related:** parent: AST-1754

### Description

## What this implements

Test-hole gap from \[board-betty\] TESTS: REVISE on AST-1764 — missing shared Modal shell scroll coverage (AST-1511 only covers Show Differences call-site wrapper).

## Scope

## Component scope

* `docs/test-bible/frontend/components.md` — modified: § Modal missing shared wide Modal shell scroll for tall direct children.
* astral-tests `tests/component/frontend/components/test_Modal.test.tsx` (or existing Modal component suite) — new or extended node asserting tall direct children in `size="wide"` Modal are reachable via scroll (Betty-owned).

## Technical scope

* New or modified component-test node(s) that fail against pre-fix product (wide Modal clips tall direct children) and pass once AST-1764 shell scroll lands — assert a below-fold marker is reachable after scroll on shared Modal, not only RepoJsonDivergenceBanner.
* Bible entry updated to name those nodes. No product code in this gap ticket (product is AST-1764).

## Acceptance criteria

- [X] At least one \[bug-repro\]-style test asserts tall direct children in a wide shared Modal are scroll-reachable.
- [X] Bible § Modal names the new/extended node(s).
- [X] Does not change product code (that is AST-1764).

## Boundaries

Product shell scroll is AST-1764. This gap is tests + bible only.

## Notes for planning

Betty board: docs/test-bible/frontend/components.md § Modal / test_Modal.test.tsx — missing shared wide Modal shell scroll for tall direct children.

## Git branch (authoritative)

Parent `ftr/AST-1754-all-modals-must-be-vertically-scrollable`. Child ref recorded in epic registry at bug-fix dispatch.

### Comments

#### katherine — 2026-09-22T00:28:09.615Z
`origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests` @ `b6537e79` · §9a clean · ftr dry-run clean

#### betty — 2026-09-22T00:27:04.869Z
[qa-handoff]
@Katherine Johnson — trim landed. `origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests` @ `e8188bb3` · ftr…sub is only the three AST-1767-owned paths (plan + bible § Modal + `test_Modal` `[bug-repro]`). Non-owned merge-tests creep restored to ftr; `test_CandidateWritingPreferences.test.tsx` removed. `[bug-repro]` green against AST-1764 shell CSS. Status left Review Posted for your resolve → UT.

#### katherine — 2026-09-22T00:25:09.221Z
[qa-handoff]
@Betty White — Radia fix-now on AST-1767: trim publish tip.

`merge-tests(AST-1767)` @ `2033f32a` pulled ~45 unrelated `origin/tests` paths onto `origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests`. Engineer pre-commit bans Katherine from committing `tests/**` / `docs/test-bible/**` (even restores-to-ftr).

Please republish that sub so:
`origin/ftr/AST-1754-all-modals-must-be-vertically-scrollable...origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests`
contains **only**:
- `docs/features/agent/ast-1511-show-differences-modal-does-not-scroll.md`
- `docs/test-bible/frontend/components.md`
- `tests/component/frontend/components/test_Modal.test.tsx`

Restore every other path in the current ftr…sub diff to the ftr tip (remove `test_CandidateWritingPreferences.test.tsx` if not on ftr). Keep `[bug-repro] AST-1767` green. Plan Resolution is on tip @ `f424c7caa9655ba778e9332bd65918e3b73ac752`. Reassign Katherine when done.

#### radia — 2026-09-22T00:22:48.860Z
[code-rubric] REVIEW (Commit: 2033f32a) merge-tests scope creep — [bug-repro] OK; fix-now: trim publish tip so ftr...sub is only AST-1767-owned paths (+ plan doc), not the full origin/tests merge.

#### betty — 2026-09-22T00:19:00.950Z
[bug-repro]
`origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests` @ `2033f32a` · repro lands red, awaits fix

#### joan — 2026-09-22T00:14:50.417Z
[board-joan] CANON: OK — test/bible gap only; no product or active canon impact.

#### betty — 2026-09-22T00:14:23.459Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § Modal / test_Modal.test.tsx — missing shared wide Modal shell scroll [bug-repro] (gap ticket owns landing it; AST-1511 remains call-site only)

#### joan — 2026-09-22T00:14:12.469Z
[board-joan]  CANON: OK

context_tokens≈14000

#### katherine — 2026-09-22T00:13:15.377Z
`origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests` @ `1a6ec1124498dd3df1a03a2a80b165bebfb725e9` · shell scroll test gap

---

_Implementation detail may live in git history on `origin/dev`._
