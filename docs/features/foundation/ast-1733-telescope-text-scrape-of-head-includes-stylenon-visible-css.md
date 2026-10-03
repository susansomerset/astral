# AST-1733 — Telescope text scrape of head includes style/non-visible CSS

<!-- linear-archive: AST-1733 archived 2026-10-02 -->

## Linear archive (AST-1733)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1733/telescope-text-scrape-of-head-includes-stylenon-visible-css  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] selecting text from the head section of the url returns style content and other non-visible text, such as:

```
div[data-rewards-widget].medallion .firework,
.firework::before,
.firework::after {
  position: absolute;
  top: 16px;
  left: 16px;
  transform: translate(-50%, -50%);
  width: 0vmin;
  aspect-ratio: 1;
  background: radial-gradient(circle, #7fdbff 0.4vmin, rgba(245, 245, 245, 0) 0 0) 50% 0%,
    radial-gradient(circle, #39cccc 0.4vmin, rgba(245, 245, 245, 0) 0 0) 0% 50%,
```

## As-is

Selecting text from the head section returns style/CSS and other non-visible text (e.g. firework keyframes) mixed into the text payload.

## To-be

Text scrape returns visible/meaningful text content only — style sheets and other non-visible head machinery are excluded.

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `service/telescope/capture.py` — selector-path `_QUERY_TEXT_JS` clones each match, strips `style`/`script`/`noscript` + hidden-attribute set, then `innerText` (no header/footer/nav chrome strip)
- [X] Leave `capture_html`, `capture_links`, auth, pool, Dockerfile, `src/**`, admin UI, Railway/CI untouched

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1733-telescope-text-head-includes-style-css` @ `f725794c` (`code` after qa-fix `f3e437e2`)

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_capture.py::test_ast1733_capture_text_selector_strips_style_script_noscript -q
```

Post-fix: green — selector path clone-and-strips style/script/noscript before innerText.

## Radia review-fix (AST-1733)

Overall: CLEAN (discuss: cross-ticket merge noise only). \[bug-repro\] OK; What must still hold OK. Clean-review → User Testing.

### Comments

#### radia — 2026-09-21T00:35:26.692Z
[code-rubric] REVIEW (Commit: f725794c) clean fix; merge noise discuss

#### betty — 2026-09-21T00:28:10.161Z
[bug-repro]
`origin/sub/AST-1721/AST-1733-telescope-text-head-includes-style-css` @ `f3e437e2` · repro lands red, awaits fix

#### joan — 2026-09-21T00:27:03.945Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T00:26:14.200Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md / test_telescope_capture.py — missing capture_text(selector) clone-and-strip for style/script/noscript (e.g. "head"); existing test_capture_text_body_selector_uses_visible_text_js covers page/body path only

#### ada — 2026-09-21T00:25:01.502Z
`origin/sub/AST-1721/AST-1733-telescope-text-head-includes-style-css` @ `5945a891c973eb68223158c71a2d2e8e093b0761` · strip head style text

---

_Implementation detail may live in git history on `origin/dev`._
