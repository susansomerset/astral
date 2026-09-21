# AST-1511 — Show Differences modal does not scroll

<!-- linear-archive: AST-1511 archived 2026-09-09 -->

## Linear archive (AST-1511)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1511/show-differences-modal-does-not-scroll  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1455 — Add "Show Differences" and "Update file with table version"  
**Blocked by / blocks / related:** parent: AST-1455

### Description

[bug]

The modal screen does not scroll, so I can only see the first three differences.

## As-is

- [X] The Show Differences modal on Manage Agents / Manage Tasks does not scroll, so only the first few row/field differences are visible (Susan saw three).

## To-be

- [X] The Show Differences modal scrolls (or otherwise shows all differences) so the operator can review every added/removed/changed row and field.

## Suggested engineer

Katherine Johnson (AST-1506 — Show Differences banner/modal UI)

### Comments

#### katherine — 2026-08-27T12:53:15.377Z
origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `b612660d` · §9a clean · ftr dry-run clean

#### radia — 2026-08-27T12:50:41.760Z
[code-rubric] PROCEED (Commit: 46870882) modal scroll wrapper fixed

#### chuckles — 2026-08-27T03:58:29.922Z
[check-linear] Tests Passed — not UAT yet; fix lane still needs review-fix, then User Testing, then merge into parent ftr. Parent prep-uat waits until AST-1511 is UT with AST-1505/AST-1506.

#### susan — 2026-08-27T03:57:28.404Z
@chuckles What's next? Is this ready for uat?

#### katherine — 2026-08-27T00:55:02.251Z
origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `46870882` · modal scrolls

#### betty — 2026-08-27T00:52:00.453Z
[bug-repro]
`origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `dbc44800` · repro lands red, awaits fix

#### betty — 2026-08-27T00:51:49.593Z
[bug-repro]
`origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll` @ `PENDING` · repro lands red, awaits fix

#### joan — 2026-08-27T00:50:38.295Z
[board-joan]  CANON: OK

#### betty — 2026-08-27T00:42:08.608Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md § AST-1506 — missing modal scroll reachability — extend test_RepoJsonDivergenceBanner.test.tsx with ≥4 changed_rows and assert 4th row_key reachable after scroll (plan-fix § Repro)

#### katherine — 2026-08-27T00:25:52.403Z
origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll @ `daaef3d1829adc9f1c19a076f69a94eafa8728b8` · modal scroll wrapper

---

_Implementation detail may live in git history on `origin/dev`._
