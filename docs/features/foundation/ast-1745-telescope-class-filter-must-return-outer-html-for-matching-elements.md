# AST-1745 — Telescope class filter must return outer HTML for matching elements

<!-- linear-archive: AST-1745 archived 2026-10-02 -->

## Linear archive (AST-1745)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1745/telescope-class-filter-must-return-outer-html-for-matching-elements  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] when I specify a class name, e.g. `logo`, it should return the outer HTML for the element(s) of that class:

```
<svg id="bLogo" role="img" class="logo" viewBox="0 0 24 24" aria-label="Microsoft Logo Image" filter="none" tabindex="0"><g class="squares"><path fill="#f26522" d="M11.4 0H0v11.4h11.4z"></path><path fill="#8dc63f" d="M23.9 0H12.5v11.4H24z"></path><path fill="#00aeef" d="M11.4 12.5H0V24h11.4z"></path><path fill="#ffc20e" d="M23.9 12.5H12.5V24H24z"></path></g></svg>
```

## As-is

Specifying a class name (e.g. logo) does not return the outer HTML for matching element(s).

## To-be

A class-name filter returns the outer HTML for the element(s) with that class (as in the svg.logo example).

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `src/external/telescope.py` — `_cull_html` preserves top-level root `<svg>` fragments (and descendants); nested svg under non-svg roots still stripped
- [X] `src/ui/frontend/src/pages/AdminTelescope.tsx` — Class name hint: outer HTML when Response type is html
- [X] Service `capture_html` outerHTML contract unchanged (verify only)

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1745-telescope-class-filter-must-return-outer-html` @ `2961b00b` (`merge-tests` of `origin/tests` `ca61b293`)

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_telescope.py::TestAst1745CullPreservesRootSvgLogo::test_cull_html_preserves_root_svg_logo_outerhtml -q
```

Pre-fix: `_cull_html` decomposes all `svg` → empty string on a root `svg.logo` fragment. Hold: nested svg under page content still stripped.

### Comments

#### radia — 2026-09-21T01:43:44.383Z
[code-rubric] PROCEED (Commit: a830d0f087279ba363fcbddc858c55b2d3a4d3da) Cull preserves root svg.logo

#### ada — 2026-09-21T01:36:48.878Z
`origin/sub/AST-1721/AST-1745-telescope-class-filter-must-return-outer-html` @ `a830d0f087279ba363fcbddc858c55b2d3a4d3da`

#### betty — 2026-09-21T01:32:11.246Z
[bug-repro]
`origin/sub/AST-1721/AST-1745-telescope-class-filter-must-return-outer-html` @ `2961b00b` · repro lands red, awaits fix

#### joan — 2026-09-21T01:30:09.681Z
[plan-rubric] PROCEED (Commit: e2b605fc) board CANON OK — cull SVG root preservation is code not canon.

#### joan — 2026-09-21T01:30:04.930Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:29:35.684Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/telescope.md / test_telescope.py — missing _cull_html preserves root svg.logo outerHTML on class-scoped fragment; AST-1731/1736 cover capture resolve only, not platform cull erase

#### ada — 2026-09-21T01:28:04.950Z
`origin/sub/AST-1721/AST-1745-telescope-class-filter-must-return-outer-html` @ `e2b605fc6e0a7a59dad420baf5aee8265098d1aa` · class outerHTML cull fix

---

_Implementation detail may live in git history on `origin/dev`._
