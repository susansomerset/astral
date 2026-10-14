# AST-2005 — dispatch-retry carve-out for empty-token data failures (canon gap for AST-2000)

<!-- linear-archive: AST-2005 archived 2026-10-13 -->

## Linear archive (AST-2005)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2005/dispatch-retry-carve-out-for-empty-token-data-failures-canon-gap-for  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1986 — Tokens are unexpectedly empty.  
**Blocked by / blocks / related:** parent: AST-1986

### Description

## What this implements

Canon gap from fix-board on [AST-2000](https://linear.app/astralcareermatch/issue/AST-2000) (`[board-joan] CANON: REVISE`). `patt.task.dispatch-retry` says it always applies and that a failure never stays in state. Susan decided on [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986) that an empty-token runtime failure skips the retry and goes **straight to the task's** `error_state`**, mid-chain hops included**: "we retry in the event that an agent goofed up, but in this case specifically a retry will not resolve the problem. The problem is with our data, not the agent's response." This child records that carve-out in canon so the AST-2000 fix conforms.

## Citations

`patt.task.dispatch-retry` (the pattern being amended).

## Scope

### Component scope

* `canon/directives/active/patt.task.dispatch-retry.md` — modified: replace "THIS PATTERN ALWAYS APPLIES" in "When this doesn't apply" with a stated exception for pre-provider data failures (empty runtime tokens), which route straight to the configured `error_state` with no `_RETRY` hop. "A failure does not persist in state" still holds.

### Technical scope

* Canon text edit only; no product code, tests or schema.

## Boundaries

* No change to the retry rule for agent-response failures.
* Product routing is AST-2000's; tests are the test-gap sibling's.

## Git branch (authoritative)

Mini-parent `ftr/AST-1986-runtime-empty-token-error`; this child `sub/AST-1986/AST-2005-dispatch-retry-carve-out`. Seeded by bug-fix.

### Comments

#### radia — 2026-10-06T05:51:04.462Z
[code-rubric] PROCEED (Commit: 1f9649c1) dispatch-retry empty_tokens carve-out

#### ada — 2026-10-06T05:50:12.016Z
`origin/sub/AST-1986/AST-2005-dispatch-retry-carve-out` @ `1f9649c1` · lighter check green (qa-fix not run, TESTS: OK)
- `python3 canon/canon_clerk.py expand patt.task.dispatch-retry` → exit 0, serves new `# When this doesn't apply`
- `python3 canon/canon_clerk.py index` → exit 0, unchanged (body-only)
- no `tests/` / `docs/test-bible/` / `scripts/` reference to this directive
- commits: `code(AST-2005)` empty marker (AST-1846 precedent) + `test(AST-2005): docs-acceptance` → validate-sub-log now only awaits `resolve(AST-2005)`

#### joan — 2026-10-06T05:48:01.900Z
[board-joan]  CANON: OK

context_tokens≈32000

#### betty — 2026-10-06T05:47:39.727Z
[board-betty] TESTS: OK
Canon body-only edit to patt.task.dispatch-retry (# When this doesn't apply). No test or bible entry reads this directive: the test_consult.py:2366 hit is a comment, and the only canon-file test (test_ArtifactsBaseResumeContent) reads patt.artifact.ui-consistency. Frontmatter is unchanged, so no clerk index churn. The empty-token routing this carve-out licenses is AST-2000 product, already tested via AST-2006. The meteorite-gap decision has no test impact either way.

#### ada — 2026-10-06T05:46:43.771Z
`origin/sub/AST-1986/AST-2005-dispatch-retry-carve-out` @ `2bc5ae3962c5b0729bad057f65cdf270c26a97d3` · empty-token carve-out planned

---

_Implementation detail may live in git history on `origin/dev`._
