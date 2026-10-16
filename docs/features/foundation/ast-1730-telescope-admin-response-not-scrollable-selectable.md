# AST-1730 — Telescope admin response not scrollable / selectable

<!-- linear-archive: AST-1730 archived 2026-10-02 -->

## Linear archive (AST-1730)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1730/telescope-admin-response-not-scrollable-selectable  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] The output is not in a scrollable/wrapping text field, I can't select all or scroll to see the full response.

## As-is

The admin response display is not a scrollable/wrapping text field, so the operator cannot select-all or scroll to see the full response.

## To-be

The admin response is shown in a scrollable wrapping text field that supports select-all and scrolling through the full payload.

## Suggested engineer

Katherine Johnson

## QA test manifest

**qa-fix bug-repro (board REVISE):** confirmed red on pre-fix AdminTelescope (`<pre>` panes → 0 textareas).

1. `tests/component/frontend/pages/test_AdminTelescope.test.tsx` — `AST-1730: raw response is read-only scrollable wrapping textarea`
2. Same file — `AST-1730: full JSON dump uses the same read-only textarea shape`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx
```

**Pass criterion (test-fix):** AST-1730 nodes flip red→green after make-fix.

**Bible shasum** (`origin/sub/AST-1721/AST-1730-telescope-admin-response-not-scrollable-selectable`):

* `docs/test-bible/frontend/pages.md` — `d51a4539ead855098b0e1f101344cbd23180efac`

## Radia review-fix (AST-1730)

Overall: CLEAN. \[bug-repro\] OK; What must still hold OK. Clean-review → User Testing.

### Comments

#### radia — 2026-09-20T19:23:08.806Z
[code-rubric] PROCEED (Commit: 60eb45661e7699fbd12f7d67d0fa1c4409999575) Admin response pane fix clean

#### betty — 2026-09-20T19:18:58.682Z
[bug-repro]
`origin/sub/AST-1721/AST-1730-telescope-admin-response-not-scrollable-selectable` @ `e2c898a7` · repro lands red, awaits fix

#### joan — 2026-09-20T19:16:18.673Z
[board-joan]  CANON: OK

#### betty — 2026-09-20T19:15:50.912Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md (AdminTelescope) — missing coverage for read-only scrollable wrapping textarea raw/JSON panes (select-all / overflow); AST-1728 vitest only asserts module export

#### katherine — 2026-09-20T19:14:32.968Z
`origin/sub/AST-1721/AST-1730-telescope-admin-response-not-scrollable-selectable` @ `c9002825e2b06c385add59eb13fca67915ee936b` · scrollable textarea plan

---

_Implementation detail may live in git history on `origin/dev`._
