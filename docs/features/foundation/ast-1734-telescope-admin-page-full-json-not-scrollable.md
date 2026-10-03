# AST-1734 — Telescope admin page / full JSON not scrollable

<!-- linear-archive: AST-1734 archived 2026-10-02 -->

## Linear archive (AST-1734)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1734/telescope-admin-page-full-json-not-scrollable  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] the actual Telescope page isn't scrollable, so when we view the full JSON, In can see only one line of it at a time.

## As-is

The Telescope admin page itself is not scrollable, so viewing full JSON shows only one line at a time.

## To-be

The admin page (and full JSON view) scrolls so the operator can see and navigate the entire payload.

## Suggested engineer

Katherine Johnson

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1734-telescope-admin-page-full-json-not-scrollable` @ `5bac32ec` (`merge-tests` of `origin/tests` `c8c42c80`)

**Bug-repro (must flip red→green after make-fix):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx -t 'AST-1734'
```

Pre-fix: root `.list-page` has empty inline height/overflow (CSS clips). To-be: `height: auto` + `overflow: visible` (or free-flow shell without list-page).

## Proposed change

- [X] Root `.list-page` uses `style={{ height: "auto", overflow: "visible" }}` so `.content` can scroll
- [X] AST-1730 `RESPONSE_PANE_STYLE` textareas unchanged (inner scroll / select-all preserved)
- [X] No global `App.css` `.list-page` change; no API / service changes

## Radia review-fix (AST-1734)

Overall: FIX-NOW — drop stray `data/admin/agent_task.json` (AST-1722) from publish ref; core AdminTelescope page-scroll fix is solid. Then User Testing.

### Comments

#### radia — 2026-09-21T00:35:32.206Z
[code-rubric] REVIEW (Commit: 880d96ef) AST-1722 stub on branch

#### betty — 2026-09-21T00:29:27.284Z
[bug-repro]
`origin/sub/AST-1721/AST-1734-telescope-admin-page-full-json-not-scrollable` @ `5bac32ec` · repro lands red, awaits fix

#### joan — 2026-09-21T00:27:29.936Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T00:26:35.680Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md / test_AdminTelescope.test.tsx — missing root list-page height:auto/overflow:visible (or free-flow shell) for page scroll; AST-1730 only asserts textarea inner scroll

#### katherine — 2026-09-21T00:25:38.286Z
`origin/sub/AST-1721/AST-1734-telescope-admin-page-full-json-not-scrollable` @ `e19c26ff3642986492e4a9edb309130066c36661` · page scroll unlock

---

_Implementation detail may live in git history on `origin/dev`._
