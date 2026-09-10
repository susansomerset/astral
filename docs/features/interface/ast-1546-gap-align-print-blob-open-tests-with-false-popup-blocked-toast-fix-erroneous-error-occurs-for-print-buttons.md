# AST-1546 — gap: align Print blob-open tests with false popup-blocked toast fix (Erroneous error occurs for print buttons)

<!-- linear-archive: AST-1546 archived 2026-09-09 -->

## Linear archive (AST-1546)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1546/gap-align-print-blob-open-tests-with-false-popup-blocked-toast-fix  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1542 — Erroneous error occurs for print buttons  
**Blocked by / blocks / related:** parent: AST-1542

### Description

## What this implements

Test/bible gap sibling for AST-1545: update frontend component/pages coverage that still asserts `window.open(..., "noopener,noreferrer")` on the four validate-then-blob Print / Open HTML sites, and add repro coverage that a successful blob open does **not** show `Popup blocked — allow popups to open the HTML tab.`

## Scope

### Component scope

* `docs/test-bible/frontend/components.md` — modified: bible entries for JAR / Print blob-open assertions that currently require the `noopener,noreferrer` features string.
* `docs/test-bible/frontend/pages.md` — modified: bible entries for Base Resume / Session Open HTML blob-open assertions with the same features-string expectation.
* Frontend component/page tests under `astral-tests` that assert `window.open` third-arg `"noopener,noreferrer"` on the four blob sites named by `[board-betty]` — modified to match AST-1545's open-without-features + `opener = null` shape, and to cover success without the popup-blocked toast.

### Technical scope

- [X] Bible markdown — modified entries: drop or rewrite the `noopener,noreferrer` third-arg requirement for the four blob-open sites; record success-path no-blocked-toast expectation. (Betty qa-fix)
- [X] Matching component/page tests — modified assertions: align `window.open` call shape with AST-1545; add or adjust a repro that fails if the blocked toast fires when the tab opened. (Betty qa-fix)
- [X] Radia discuss: product UI removed from this gap sub — AST-1545 owns product only.

## Acceptance criteria

- [X] Tests that previously required `window.open(..., "noopener,noreferrer")` on the four blob sites match the AST-1545 open shape.
- [X] A repro exists that fails if success still toasts `Popup blocked — allow popups to open the HTML tab.`
- [X] Bible frontend components/pages entries stay honest with those tests.

## Boundaries

Does **not** change product UI files (AST-1545 owns those). Does **not** expand into non-blob `window.open` paths.

## Notes for planning

Sibling of AST-1545. Filed from `[board-betty] TESTS: REVISE` on orphaned mini-parent AST-1542 (gap child instead of inline qa-fix).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at bug-fix gap dispatch.

### Comments

#### radia — 2026-08-31T20:24:59.300Z
[code-rubric] REVIEW (Commit: c930a53b) Product stacked on gap ticket

Discuss: drop AST-1545 product UI from AST-1546 sub (tests/bible only) — sibling AST-1545 already owns product. Then User Testing.

#### hedy — 2026-08-31T20:20:58.750Z
`origin/sub/AST-1542/AST-1546-gap-align-print-blob-open-tests` @ `c930a53b2827cf9c63da90876a8f2dbef16c9ccf`

#### betty — 2026-08-31T20:18:59.447Z
[bug-repro]
`origin/sub/AST-1542/AST-1546-gap-align-print-blob-open-tests` @ `d00f094c` · repro lands red, awaits fix

#### joan — 2026-08-31T20:10:29.196Z
[board-joan] CANON: OK

Test/bible-only gap; no canon impact. Betty corpus owns the delta.

#### betty — 2026-08-31T20:10:08.719Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/components.md + pages.md — missing success no-blocked-toast repro; four blob sites still assert noopener third arg

#### hedy — 2026-08-31T20:08:59.098Z
`origin/sub/AST-1542/AST-1546-gap-align-print-blob-open-tests` @ `bfa5a7a1197afb273591d7d0d739df18b18e990f` · test bible blob-open gap

---

_Implementation detail may live in git history on `origin/dev`._
