# AST-1732 — Telescope links not scoped to class selector

<!-- linear-archive: AST-1732 archived 2026-10-02 -->

## Linear archive (AST-1732)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1732/telescope-links-not-scoped-to-class-selector  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] when a class name is specified, the links array includes links on the whole page, not just within the class name

## As-is

When a class name selector is specified, the links array still includes links from the whole page, not only within the selected class.

## To-be

When any filtering selector is set, the links array only includes links inside that scoped element.  If multiple matches are found, the links array is the deduped list of links found within any matching content.

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `capture_links(page, selector=None)` — whole-page for omit/`page`/`body`; scoped + href dedupe otherwise
- [X] `POST /telescope` passes `body.selector` into `capture_links`
- [X] Restacked onto `origin/ftr/AST-1721` — AST-1729 documentElement default + AST-1731 bare-class/multi-match present; link scoping kept
- [X] Full `tests/component/service/test_telescope_capture.py` green (12 passed)

## QA test manifest

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1732_capture_links_scoped_to_selector \
  tests/component/service/test_telescope_capture.py::test_ast1732_capture_links_multi_match_dedupes_by_href \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1732_post_telescope_passes_selector_to_capture_links -q
```

### Comments

#### ada — 2026-09-20T19:35:18.531Z
`origin/sub/AST-1721/AST-1732-telescope-links-not-scoped-to-class-selector` @ `00972367c3696e36849b3bb86275a433e4ff127d` · §9a ftr clean

#### radia — 2026-09-20T19:32:46.821Z
[code-rubric] REVIEW (Commit: fd3a49315edcaab5f30999af06c330740b3358ba) Restack before UT — 1729 regression

#### betty — 2026-09-20T19:24:04.290Z
[bug-repro]
`origin/sub/AST-1721/AST-1732-telescope-links-not-scoped-to-class-selector` @ `deca28c2` · repro lands red, awaits fix

#### joan — 2026-09-20T19:20:25.306Z
[board-joan]  CANON: OK

#### betty — 2026-09-20T19:20:06.592Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md / test_telescope_capture.py — missing scoped capture_links(selector) + multi-match href dedupe asserts; existing test_capture_links_filters_http is whole-page only; app never passes body.selector

#### ada — 2026-09-20T19:19:11.393Z
`origin/sub/AST-1721/AST-1732-telescope-links-not-scoped-to-class-selector` @ `ca6fd51302fb0c57742045b7b0f1e4e0b58c7560` · scope links to selector

---

_Implementation detail may live in git history on `origin/dev`._
