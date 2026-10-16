# AST-1799 — gap: tests suffix-always claim asserts (AST-1798 board REVISE)

<!-- linear-archive: AST-1799 archived 2026-10-02 -->

## Linear archive (AST-1799)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1799/gap-tests-suffix-always-claim-asserts-ast-1798-board-revise  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1797 — _RETRY suffix issues  
**Blocked by / blocks / related:** parent: AST-1797

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1798 — flip claim-state asserts (TestAst882/641/898 and bible) from cross-name companions to suffix-always pairing.

## Proposed change

- [X] `tests/component/utils/test_config.py` — TestAst882 / TestAst641 / TestAst898 claim asserts + sibling ACTIVE_SEARCH / meteorite claim asserts → suffix-always
- [X] `docs/test-bible/utils/config.md` — AST-641 / AST-882 / AST-898 claim-contract prose → suffix-always (routing `retry_state` unchanged)

## Scope

### Component scope

* `docs/test-bible/utils/config.md` — modified: claim-state / AST-882/641/898 expectations encode cross-name companions; must document suffix-always.
* `tests/component/utils/test_config.py` — modified: TestAst882 / TestAst641 / TestAst898 (and any sibling claim asserts) must expect `[ts, f"{ts}_RETRY"]` always, never `HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY`.

### Technical scope

* Bible section for utils/config claim helpers — revise documented contracts to match AST-1798 suffix-always pairing (companion need not exist in registry).
* TestAst882 / TestAst641 / TestAst898 claim-state cases — flip assertions from registry-`retry_state` / cross-name companions to always `[primary, primary_RETRY]`.

## Boundaries

Product code for the fix stays on AST-1798. This gap is test/bible only (Betty).

## Notes for planning

Board: \[board-betty\] TESTS: REVISE — flip claim-state asserts.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1797-retry-suffix-claim`, child `sub/AST-1797/AST-1799-retry-suffix-claim-tests`. Created at bug-fix.

### Comments

#### radia — 2026-09-25T17:22:14.932Z
[code-rubric] PROCEED (Commit: 8b055369) suffix claim test gap; advisory dispatcher assert follow-up out of scope

#### joan — 2026-09-25T17:15:32.859Z
[board-joan]  CANON: OK

Test/bible-only gap — flip claim asserts to suffix-always; no product or canon edits. F3 not triggered.

context_tokens≈14000

#### betty — 2026-09-25T17:14:04.074Z
[board-betty] TESTS: OK

#### ada — 2026-09-25T17:12:57.451Z
`origin/sub/AST-1797/AST-1799-retry-suffix-claim-tests` @ `cc950b5fe20013d5bbe8b9465eb403433af434fb` · test gap plan

---

_Implementation detail may live in git history on `origin/dev`._
