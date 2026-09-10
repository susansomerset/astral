# AST-1553 — gap: Toast dismiss-without-copy tests + bible (Close button on error toast copies error)

<!-- linear-archive: AST-1553 archived 2026-09-09 -->

## Linear archive (AST-1553)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1553/gap-toast-dismiss-without-copy-tests-bible-close-button-on-error-toast  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1543 — Close button on error toast copies error  
**Blocked by / blocks / related:** parent: AST-1543

### Description

## What this implements

Test/bible gap sibling for AST-1549: update `test_Toast.test.tsx` / `docs/test-bible/frontend/components.md` for dismiss-without-copy, and retarget existing click-copy + ✗ glyph cases that assume root `.toast-error-clickable` / `\u2717` so they match AST-1549’s split dismiss vs copy hit targets.

## Scope

### Component scope

* `docs/test-bible/frontend/components.md` — modified: AST-779 / Toast entries for dismiss-without-copy and updated click-copy / glyph expectations.
* Frontend Toast component tests under `astral-tests` that cover click-to-copy and the error glyph (named by `[board-betty]`) — modified/extended for dismiss-without-copy and retargeted selectors under the Proposed change.

### Technical scope

* Bible markdown — modified entries: add dismiss-without-copy coverage; rewrite root `.toast-error-clickable` / `\u2717` assumptions to match AST-1549.
* Matching Toast component tests — modified/new assertions: dismiss does not copy; copy still works from message/hint; glyph/affordance expectations aligned with product fix.

## Acceptance criteria

- [X] A repro exists that fails if dismiss copies diagnostics or fails to dismiss.
- [X] Existing click-to-copy / glyph tests match AST-1549’s hit targets and icon choice.
- [X] Bible frontend components entries stay honest with those tests.

## Proposed change

- [X] Betty qa-fix: retarget glyph + copy-target click; add dismiss-without-copy repro.
- [X] Radia discuss addressed: product UI (`Toast.tsx` / `App.css`) removed from this gap sub — belongs only on sibling AST-1549. Tip is tests/bible (+ plan doc) only.

## Boundaries

Does **not** carry product UI on this publish ref (AST-1549 owns Toast.tsx / App.css). Does **not** expand beyond Toast component/bible coverage.

## Notes for planning

Sibling of AST-1549. Filed from `[board-betty] TESTS: REVISE` on orphaned mini-parent AST-1543 (gap child instead of inline qa-fix).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at bug-fix gap dispatch.

### Comments

#### radia — 2026-08-31T21:10:43.153Z
[code-rubric] REVIEW (Commit: 9df1c7b1) Product stacked on gap ticket

Discuss: drop AST-1549 product UI from AST-1553 sub (tests/bible only) — sibling AST-1549 already owns product. Then User Testing.

#### betty — 2026-08-31T21:05:05.083Z
[bug-repro]
`origin/sub/AST-1543/AST-1553-gap-toast-dismiss-without-copy-tests` @ `1ef37344` · repro lands red, awaits fix

#### joan — 2026-08-31T21:01:35.950Z
[board-joan] CANON: OK

Test/bible-only gap; icon-control dismiss selectors conform. No statute/pattern rewrite.

#### betty — 2026-08-31T21:01:12.590Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md (AST-779 / test_Toast.test.tsx) — retarget glyph + copy-target click; add dismiss-without-copy (no clipboard, onDone after 300ms) — gap this ticket owns

#### katherine — 2026-08-31T21:00:24.255Z
`origin/sub/AST-1543/AST-1553-gap-toast-dismiss-without-copy-tests` @ `3127a13ab0f33d8f2f7b3e933da74a40206e46b5` · test/bible gap plan

---

_Implementation detail may live in git history on `origin/dev`._
