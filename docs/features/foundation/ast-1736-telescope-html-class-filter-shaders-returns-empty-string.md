# AST-1736 — Telescope HTML class filter (shaders) returns empty string

<!-- linear-archive: AST-1736 archived 2026-10-02 -->

## Linear archive (AST-1736)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1736/telescope-html-class-filter-shaders-returns-empty-string  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] when I put a class name in the filter (`shaders`) the html scrape does not recognize that I'm talking about a class name and returns an empty string.  Perhaps this should be a separate parameter?  Like, filter by element tag and then filter by class name?

## As-is

Putting a class name like `shaders` in the filter is not recognized as a class and the HTML scrape returns an empty string.

## To-be

Class-name filters match elements with that class (or a clear tag vs class parameter splits the filter) and return the matching HTML when nodes exist.

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `service/telescope/capture.py` — `resolve_capture_query` (tag/class_name → CSS; ambiguous with selector → error); `_BARE_CLASS_RETRY` on `capture_links` scoped path
- [X] `service/telescope/app.py` — optional `tag` / `class_name` on both request models; resolve before capture; 400 on ambiguity
- [X] `src/external/telescope.py` — pass-through `tag` / `class_name` on `_post_telescope`, `_post_telescope_html`, `admin_telescope_scrape`
- [X] `src/ui/api/api_admin.py` — forward `tag` / `class_name` from admin body
- [X] `src/ui/frontend/src/pages/AdminTelescope.tsx` — Tag + Class name fields; mutually exclusive with Selector

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1736-telescope-html-class-filter-shaders-returns-empty` @ `efc11c26` (`merge-tests` of `origin/tests` `2125fd70`)

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1736_html_class_name_resolves_to_dot_class \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1736_selector_plus_class_name_returns_400 \
  tests/component/service/test_telescope_capture.py::test_ast1736_capture_links_bare_class_retries_as_class -q
```

Pre-fix: class_name ignored (selector stays None/omit); selector+class_name returns 200; capture_links scoped JS has no bare→.class retry.

## Radia review-fix (AST-1736)

Overall: CLEAN. PROCEED → User Testing (resolve skipped).

### Comments

#### radia — 2026-09-21T00:40:21.392Z
[code-rubric] PROCEED (Commit: c7e2af6b) tag class filter fix

#### ada — 2026-09-21T00:37:17.271Z
`origin/sub/AST-1721/AST-1736-telescope-html-class-filter-shaders-returns-empty` @ `c7e2af6b1d5dc96f8dbabe1cec42fd24df680026`

#### betty — 2026-09-21T00:32:41.342Z
[bug-repro]
`origin/sub/AST-1721/AST-1736-telescope-html-class-filter-shaders-returns-empty` @ `efc11c26` · repro lands red, awaits fix

#### joan — 2026-09-21T00:30:29.716Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T00:29:35.850Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md (+ AdminTelescope bible) — missing class_name:"shaders"→non-empty html, selector+class_name→400, capture_links bare-class retry; AST-1731 only covers bare selector heuristic

#### ada — 2026-09-21T00:28:40.293Z
`origin/sub/AST-1721/AST-1736-telescope-html-class-filter-shaders-returns-empty` @ `1a79e38c466e569588c3b8f3b1d3c92e9fcc2d63` · tag/class filter plan

---

_Implementation detail may live in git history on `origin/dev`._
