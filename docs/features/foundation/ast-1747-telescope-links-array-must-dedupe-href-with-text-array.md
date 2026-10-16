# AST-1747 — Telescope links array must dedupe href with text array

<!-- linear-archive: AST-1747 archived 2026-10-02 -->

## Linear archive (AST-1747)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1747/telescope-links-array-must-dedupe-href-with-text-array  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] the link array must be deduped.  Multiple cases of the same link with different text should support an array of text per link.

## As-is

The links array can contain multiple entries for the same href with different text.

## To-be

Links are deduped by href; multiple texts for the same link are a deduped array of text values on that link object.

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `_dedupe_links_by_href` — one object per href; `text` is deduped `list[str]` (first-seen order)
- [X] Whole-page `capture_links` path folds raw anchors through that helper
- [X] Scoped `_QUERY_LINKS_JS` emits every http(s) anchor (no first-wins `seen`); fold via helper
- [X] `capture_links` return annotation reflects `text: list[str]`
- [X] Stage 3 plan contract example updated to `text: ["...", "..."]`

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1747-telescope-links-array-must-dedupe-href-with-text-array` @ `279c9ce7` (`code` make-fix; prior `merge-tests` of `origin/tests` `e76dca13`)

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1747_capture_links_dedupes_href_with_text_array \
  tests/component/service/test_telescope_capture.py::test_capture_links_filters_http \
  tests/component/service/test_telescope_capture.py::test_ast1732_capture_links_multi_match_dedupes_by_href -q
```

Pre-fix: raw evaluate list returned as-is (string `text`, duplicate hrefs). To-be: one object per href with `text: list[str]`. Rewrote AST-1732 first-wins/`seen` asserts.

## Radia review-fix (AST-1747)

Overall: CLEAN / PROCEED — `_dedupe_links_by_href` matches plan; \[bug-repro\] OK; What must still hold OK. Advisories only (app-route mock string text; parent AC3 wording). → User Testing (resolve-child skipped).

### Comments

#### radia — 2026-09-21T01:43:51.400Z
[code-rubric] PROCEED (Commit: 279c9ce7) Href dedupe text[] clean

#### betty — 2026-09-21T01:34:43.918Z
[bug-repro]
`origin/sub/AST-1721/AST-1747-telescope-links-array-must-dedupe-href-with-text-array` @ `3919b252` · repro lands red, awaits fix

#### joan — 2026-09-21T01:32:51.464Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:31:55.608Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md / test_telescope_capture.py — missing href-dedupe with text[] (e.g. ["Software Engineer","View role"]); AST-1732 string-text + seen/first-wins asserts will break

#### ada — 2026-09-21T01:30:27.121Z
`origin/sub/AST-1721/AST-1747-telescope-links-array-must-dedupe-href-with-text-array` @ `7b5dc2718195006ba2f3e4e0e8fc098f8ee68a08` · href dedupe + text[]

---

_Implementation detail may live in git history on `origin/dev`._
