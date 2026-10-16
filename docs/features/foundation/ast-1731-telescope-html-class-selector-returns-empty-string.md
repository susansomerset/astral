# AST-1731 — Telescope HTML class selector returns empty string

<!-- linear-archive: AST-1731 archived 2026-10-02 -->

## Linear archive (AST-1731)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1731/telescope-html-class-selector-returns-empty-string  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] scraping HTML, Specifying a class name `points-container` from [https://www.bing.com](<https://www.bing.com>) returns an empty HTML string, though I know the container exists because it was explicitly seen in the body element.

## As-is

Scraping HTML with class name `points-container` (e.g. [bing.com](<http://bing.com>)) returns an empty HTML string even though that container exists in the body.

## To-be

Specifying a class selector that matches rendered content returns an array of elements, regardless of element type (div, span, td, etc.) with that class name, just as it does for span etc.

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `service/telescope/capture.py` — bare CSS identifier → `.{sel}` retry when zero tag hits; `capture_html` multi-match `""` / `str` / `list[str]`; same retry on `capture_text`
- [X] `service/telescope/app.py` — list-safe `html_len` on `/telescope/html`
- [X] `src/external/telescope.py` — list-safe html log; cull maps list; `_ensure_html` unwraps first match
- [X] `src/ui/frontend/src/pages/AdminTelescope.tsx` — display multi-match html like text (`\n---\n`)
- [X] Restack onto `origin/ftr/AST-1721-astral-telescope-stateless-headless-scraping`; restore AST-1729 empty/`page` → documentElement, explicit `body` → body-only; keep AST-1730 scrollable AdminTelescope panes

## QA test manifest

**qa-fix bug-repro (board REVISE):** confirmed red on pre-fix `capture.py` (querySelector-only html; no bare→`.class` retry).

1. `tests/component/service/test_telescope_capture.py::test_capture_html_bare_class_token_retries_as_class` — bare `points-container` must not return `""`
2. `tests/component/service/test_telescope_capture.py::test_capture_html_multi_match_returns_list` — `.job` with 2 hits → `list[str]`
3. `tests/component/service/test_telescope_capture.py::test_capture_text_bare_class_token_retries_as_class` — same bare→class retry on `capture_text`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_capture_html_bare_class_token_retries_as_class \
  tests/component/service/test_telescope_capture.py::test_capture_html_multi_match_returns_list \
  tests/component/service/test_telescope_capture.py::test_capture_text_bare_class_token_retries_as_class -q
```

**Pass criterion (test-fix):** AST-1731 nodes flip red→green after make-fix.

**Bible shasum** (`origin/sub/AST-1721/AST-1731-telescope-html-class-selector-returns-empty-string`):

* `docs/test-bible/service/telescope.md` — `8bbfbc52e7efeaee3a8c9a6f080860379783b967`

### Comments

#### radia — 2026-09-20T19:32:49.416Z
[code-rubric] REVIEW (Commit: 67fd3bf5) AST-1729+1730 regressions

#### betty — 2026-09-20T19:23:51.144Z
[bug-repro]
`origin/sub/AST-1721/AST-1731-telescope-html-class-selector-returns-empty-string` @ `8044c000` · repro lands red, awaits fix

#### joan — 2026-09-20T19:19:22.698Z
[board-joan]  CANON: OK

#### betty — 2026-09-20T19:18:27.518Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md / test_telescope_capture.py — missing bare class token (e.g. points-container → .class) + multi-match html list asserts; AST-1725 only covers #main / page / body

#### ada — 2026-09-20T19:17:41.507Z
`origin/sub/AST-1721/AST-1731-telescope-html-class-selector-returns-empty-string` @ `cbe2a25874f11045451d129d7ae5d71b6bc62633` · class selector HTML plan

---

_Implementation detail may live in git history on `origin/dev`._
