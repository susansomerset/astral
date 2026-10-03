# AST-1735 — Telescope head vs body text+links return identical links

<!-- linear-archive: AST-1735 archived 2026-10-02 -->

## Linear archive (AST-1735)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1735/telescope-head-vs-body-textlinks-return-identical-links  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] when I scraped the text for the head element with links and then scraped the text for the body element with links, the links were identical, and I would have expected them to be different.

## As-is

Scraping text for head with links and then body with links returns identical link arrays when they should differ by section.

## To-be

Links returned for a scoped element (head vs body) are only those within that scope — head and body scrapes yield different link sets when the DOM differs.

## Suggested engineer

Ada Lovelace

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1735-telescope-head-vs-body-textlinks-return-identical-links` @ `c31bfded30d472eba67905f397da86e0bb9bb698` (`merge-tests` of `origin/tests` `56ddf130b0e14b8935eae782c96d31ec8f12c7d1`)

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1735_capture_links_body_is_scoped_not_whole_page \
  tests/component/service/test_telescope_capture.py::test_ast1735_capture_links_head_scoped_and_page_stays_whole_document -q
```

Pre-fix: body still whole-page alias (evaluate arity 1); head already scoped; omit/page stay whole-doc.

## Proposed change

- [X] `capture_links`: whole-document path only for omit / `"page"` (drop `"body"` from the gate)
- [X] Explicit `"head"` / `"body"` use scoped evaluate (querySelectorAll + href dedupe)
- [X] Leave `capture_text` / `capture_html` / `app.py` / `src/**` unchanged; comment matches omit/page-only whole-doc path

## Radia review-fix (AST-1735)

Overall: FIX-NOW — restack onto current ftr (include AST-1733 text strip); keep capture_links head/body scoping. Then User Testing.

### Comments

#### ada — 2026-09-21T00:44:46.330Z
`origin/sub/AST-1721/AST-1735-telescope-head-vs-body-textlinks-return-identical-links` @ `c31bfded` · §9a clean · ftr dry-run clean

#### radia — 2026-09-21T00:41:06.160Z
[code-rubric] REVIEW (Commit: 62926046) Restack ftr; 1733 test red

#### betty — 2026-09-21T00:31:51.543Z
[bug-repro]
`origin/sub/AST-1721/AST-1735-telescope-head-vs-body-textlinks-return-identical-links` @ `e0169e492d859aefcd99a13b42a7ca560eeb4455` · repro lands red, awaits fix

#### joan — 2026-09-21T00:29:51.746Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T00:29:03.280Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md / test_telescope_capture.py — missing capture_links("head"|"body") scoped (body not whole-page alias) + body≠page; AST-1732 only covers class selectors

#### ada — 2026-09-21T00:27:55.081Z
`origin/sub/AST-1721/AST-1735-telescope-head-vs-body-textlinks-return-identical-links` @ `3fc33a51` · body alias drops whole-page

---

_Implementation detail may live in git history on `origin/dev`._
