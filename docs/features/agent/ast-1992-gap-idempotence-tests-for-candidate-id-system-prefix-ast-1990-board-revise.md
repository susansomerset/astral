# AST-1992 — gap: idempotence tests for candidate-id system prefix (AST-1990 board REVISE)

<!-- linear-archive: AST-1992 archived 2026-10-13 -->

## Linear archive (AST-1992)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1992/gap-idempotence-tests-for-candidate-id-system-prefix-ast-1990-board  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1985 — Do not duplicate the candidate prefix when already present.  
**Blocked by / blocks / related:** parent: AST-1985

### Description

## What this implements

Test gap from `[board-betty] TESTS: REVISE` on AST-1990: `TestAst1639CandidateIdSystemPrefix` has no idempotence coverage for `_system_text_with_candidate_prefix`. Add cases proving already-prefixed input collapses to exactly one `[astral-<cid>]`, and keep the bible honest.

## Scope

### Component scope

* `tests/component/core/test_agent.py` — modified: new idempotence cases in `TestAst1639CandidateIdSystemPrefix`.
* `docs/test-bible/core/agent.md` — modified: § AST-1639 entries gain the idempotence nodes.

### Technical scope

* `test_agent.py` — new test functions: already-prefixed input → one marker; 5×-stacked input (AST-1985 sample) → one marker; other-id leading marker → replaced by current cid (Susan-approved any-marker strip); blank/missing id still raises `ValueError` even when the body already carries a marker; un-prefixed body output unchanged.
* Bible — modified entries documenting those nodes.

## Boundaries

Product code stays on [AST-1990](https://linear.app/astralcareermatch/issue/AST-1990). Test tree / bible only (Betty). Canon: Joan CANON: OK — no canon gap.

## Notes for planning

Board: `[board-betty] TESTS: REVISE` on AST-1990 (full text in that comment). Plan: `docs/features/agent/ast-1639-candidate-id-system-prompt-prefix.md` `## Bug: AST-1990` (Repro asserts there are the exact fixtures).

## Git branch (authoritative)

Parent `ftr/AST-1985-candidate-prefix-dedupe`, child `sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-06T04:32:35.297Z
[code-rubric] PROCEED (Commit: 149518fb) bug-repro idempotence tests clean

#### ada — 2026-10-06T04:31:20.621Z
`origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests` @ `9c13b3b82` · [bug-repro] flipped red→green

- RED (pre-fix `src/core/agent.py` @ `cc256733f`): 4 repro nodes failed, 9 passed (guards green).
- GREEN (synced tip, AST-1990 `2b0b74f00` via ftr): 4/4 repro nodes; full `TestAst1639CandidateIdSystemPrefix` 13 passed.

#### betty — 2026-10-06T04:25:28.369Z
[bug-repro]
`origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests` @ `149518fb1` · repro lands red, awaits fix

---

_Implementation detail may live in git history on `origin/dev`._
