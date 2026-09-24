# AST-1612 — gap revise discussion tests for anticipate_scan and empty headers (artifacts discussion is incomplete)

<!-- linear-archive: AST-1612 archived 2026-09-22 -->

## Linear archive (AST-1612)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1612/gap-revise-discussion-tests-for-anticipate-scan-and-empty-headers  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1607 — artifacts discussion is incomplete  
**Blocked by / blocks / related:** parent: AST-1607

### Description

## What this implements

Test gap from [board-betty] on AST-1609: revise broken AST-1550/AST-1551 discussion tests and add repro coverage for the unique-parent hop walk (~anticipate_scan) and RESPONSE-only Discussion headers.

## Citations

AST-1609 fix-board Betty REVISE; docs/test-bible/utils/config.md § AST-1550; docs/test-bible/frontend/components.md § AST-1551.

## Scope

## Component scope

* `docs/test-bible/utils/config.md` — modified: AST-1550 hop-key expectations (no longer assert anticipate_scan excluded; unique-parent walk ~10).
* `docs/test-bible/frontend/components.md` — modified: AST-1551 Discussion pane / JAR expectations (filter-to-RESPONSE; 0 headers when agentStory=[]).
* Tests under astral-tests mirroring those bible entries (component tests for `TestAst1550DiscussionHopKeys`, JobDiscussionPane / JAR AST-1551) — modified/new as needed for the REVISE what-line.

## Technical scope

* Bible + component tests — modified assertions: unique-parent walk includes the live parent of `first_task_key` when exactly one; pane shows 0 headers when `agentStory=[]`; covers anticipate_scan when story has RESPONSE.
* No product `src/` changes in this gap child (those belong to AST-1609).

## Acceptance criteria

1. Existing tests that asserted anticipate_scan excluded / nine empty-story headers are revised to match AST-1609 to-be.
2. Coverage exists for anticipate_scan when story has RESPONSE and for empty agentStory → no Discussion headers.

## Boundaries

Does not implement the product hop-walk or pane filter (AST-1609). Does not change canon.

## Notes for planning

Sibling gap of AST-1609 under orphaned mini-parent AST-1607. Betty REVISE what-line is the brief.

## Git branch (authoritative)

Parent `ftr/AST-1607-artifacts-discussion-incomplete`; child `sub/AST-1607/<this-id>-…`.

## Radia review-fix (AST-1612)

**Overall:** DISCUSS — gap tip carries AST-1609 product (`3807d54c`) because ftr lacked 1609; AST-1611 inbox bleed on ancestry. Test/bible deliverables conform; [bug-repro] OK.

**Chuckles routing:** land AST-1609 on ftr first, then close gap (accept bundle or slim tip); confirm AST-1611 co-ship vs strip.

### Comments

#### radia — 2026-09-09T22:40:37.404Z
[review-fix] DISCUSS — AST-1612 tip bundles AST-1609 product (ftr lacked 8e6b7074) + AST-1611 inbox bleed. Gap test/bible OK; [bug-repro] OK. Land AST-1609 on ftr first; then slim or accept bundle before UT.

#### ada — 2026-09-09T22:38:05.294Z
`origin/sub/AST-1607/AST-1612-gap-revise-discussion-tests` @ `3807d54c` · [bug-repro] red→green after merge AST-1609; hop keys + Discussion vitest green

#### betty — 2026-09-09T22:35:48.447Z
[bug-repro]
`origin/sub/AST-1607/AST-1612-gap-revise-discussion-tests` @ `59966904` · repro lands red, awaits fix

#### ada — 2026-09-09T22:30:22.632Z
make-fix blocked — entire AST-1612 ## Scope is `docs/test-bible/**` + astral-tests component tests (`TestAst1550DiscussionHopKeys`, JobDiscussionPane / JAR AST-1551). Ada/make-fix must not edit `tests/` or `docs/test-bible/**` (test-tree ban; qa-fix owns bible/tests). No product `src/` work remains on this gap (AST-1609 already owns hop walk + pane filter).

@chuckles — hand to Betty / qa-fix on astral-tests to land the plan-fix Proposed change @ `origin/sub/AST-1607/AST-1612-gap-revise-discussion-tests` `f65f0f5d` (feature docs already patched). Leaving status **Plan Approved**; not moving to Code Complete with an empty product commit.

#### betty — 2026-09-09T22:29:35.010Z
[board-betty] TESTS: OK

#### joan — 2026-09-09T22:29:09.098Z
[board-joan]  CANON: OK

#### ada — 2026-09-09T22:28:39.926Z
`origin/sub/AST-1607/AST-1612-gap-revise-discussion-tests` @ `f65f0f5d` · test gap plan

#### ada — 2026-09-09T22:28:29.921Z
@ `f65f0f5d` · test gap plan

---

_Implementation detail may live in git history on `origin/dev`._
