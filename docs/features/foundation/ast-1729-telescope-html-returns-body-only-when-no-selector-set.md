# AST-1729 — Telescope HTML returns body-only when no selector set

<!-- linear-archive: AST-1729 archived 2026-10-02 -->

## Linear archive (AST-1729)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1729/telescope-html-returns-body-only-when-no-selector-set  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] The html does not return the full html (only body) where no selector is set.

## As-is

When no selector is set, Telescope HTML responses return only the body fragment, not the full HTML document.

## To-be

With no selector set, Telescope HTML returns the full page HTML (not body-only).

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `capture_html`: `None` / `""` / `"page"` → `document.documentElement.outerHTML`
- [X] Explicit `"body"` still returns body-only
- [X] Other CSS selectors unchanged (first-match outerHTML)
- [X] Stage 3 contract note updated (null = full document)

## QA test manifest

**qa-fix bug-repro (board REVISE):** confirmed red on pre-fix `capture_html` (None/`""` hit body path).

1. `tests/component/service/test_telescope_capture.py::test_capture_html_omitted_selector_uses_document_element` — None/`""` evaluate `documentElement` (not `document.body.outerHTML`)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_capture_html_omitted_selector_uses_document_element -q
```

**Pass criterion (test-fix):** that node flips red→green after make-fix.

## Radia review-fix (AST-1729)

Overall: CLEAN. \[bug-repro\] OK; What must still hold OK. Clean-review → User Testing.

### Comments

#### radia — 2026-09-20T19:23:12.972Z
[code-rubric] PROCEED (Commit: d50e48dfc9d3b594fa656c91584b2cf28a246d8c) Html default full document

#### betty — 2026-09-20T19:17:54.560Z
[bug-repro]
`origin/sub/AST-1721/AST-1729-telescope-html-returns-body-only-when-no-selector-set` @ `82f1a0b1` · repro lands red, awaits fix

#### joan — 2026-09-20T19:16:26.331Z
[board-joan]  CANON: OK

#### betty — 2026-09-20T19:15:56.846Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md / test_telescope_capture.py::test_capture_html_page_vs_body_vs_selector — missing coverage that None/"" default to documentElement (full page), not body — plan Blast radius

#### ada — 2026-09-20T19:14:29.208Z
[check-linear] blocked: publish-ref polluted

`origin/sub/AST-1721/AST-1729-telescope-html-returns-body-only-when-no-selector-set` currently tips at `13943ed3` with AST-1730 history (`7b13f1a4` …) under the plan-fix commit — push ran from the wrong local branch.

Clean tip rebuilt locally (not force-pushed — needs Chuckles): `aa72981ba310766e8b663bb21d63189ecc052639` = `e237adb0` + plan-fix doc only.

Please `git push --force-with-lease origin aa72981ba310766e8b663bb21d63189ecc052639:sub/AST-1721/AST-1729-telescope-html-returns-body-only-when-no-selector-set` (or equivalent). Plan Ready content is correct; tip SHA in prior comment is wrong lineage.

#### ada — 2026-09-20T19:13:42.853Z
`origin/sub/AST-1721/AST-1729-telescope-html-returns-body-only-when-no-selector-set` @ `13943ed3894934a213cf3dac03fea996a40a3713` · html default full doc

---

_Implementation detail may live in git history on `origin/dev`._
