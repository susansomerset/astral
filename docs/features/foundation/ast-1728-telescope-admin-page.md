# AST-1728 — Telescope Admin page

<!-- linear-archive: AST-1728 archived 2026-10-02 -->

## Linear archive (AST-1728)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1728/telescope-admin-page  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

@Susan Somerset said in [AST-1721](https://linear.app/astralcareermatch/issue/AST-1721/astral-telescope-stateless-headless-scraping-microservice-per-url#comment-f72d216a):

> we need to add an admin screen for using telescope.  A screen with a url and response type (html vs text) and toggles for each optional parameter, and a display window to show the raw response from the telescope service.  I expect the response to include the string contents, as well as Meta data about the scrape, such as if it was bot blocked or cookies, or some other issue that prevented it from properly scraping the page as expected.

## As-is

No admin screen exists to call Telescope with a URL, response type, and option toggles, or to inspect raw scrape payload/metadata.

## To-be

An admin screen lets an operator enter a URL, choose html vs text, toggle optional Telescope parameters, and see the raw response including content plus scrape metadata (bot-block / cookies / other scrape failures).

## Suggested engineer

Katherine Johnson

## Proposed change (make-fix)

- [X] `service/telescope/interact.py` — `dismiss_cookies` returns bool
- [X] `service/telescope/meta.py` — `build_scrape_meta`
- [X] `service/telescope/app.py` — attach additive `scrape_meta` on `/telescope` and `/telescope/html`
- [X] `src/external/telescope.py` — `admin_telescope_scrape` (+ pass-through meta)
- [X] `src/ui/api/api_admin.py` — `POST /api/admin/telescope` `@require_admin`
- [X] `src/ui/frontend/src/pages/AdminTelescope.tsx` + routes + NAV Tools "Telescope"
- [X] `scripts/migrations/backfill_culture_links.py` — playwright→telescope so `api_admin` imports (module-load blocker after AST-1726)

## QA test manifest

**qa-fix bug-repro (board REVISE):** confirmed red on pre-fix tree @ publish tip before merge-tests.

1. `tests/component/service/test_telescope_app.py::TestAst1728ScrapeMeta` — `scrape_meta` (+ keys) on `/telescope` and `/telescope/html`
2. `tests/component/ui/api/test_api_admin_telescope.py::TestAst1728AdminTelescopeRepro` — AdminTelescope.tsx exists; `routes.tsx` `admin/telescope`; NAV Tools Telescope; `admin_telescope_scrape`; POST `/api/admin/telescope` ≠ 404
3. `tests/component/frontend/pages/test_AdminTelescope.test.tsx` — **AST-1728: AdminTelescope page module exports a component** (§6c)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestAst1728ScrapeMeta \
  tests/component/ui/api/test_api_admin_telescope.py \
  -q
# Vitest (frontend package):
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx
```

**Pass criterion (test-fix):** repro nodes flip red→green after make-fix; then rest of manifest green.

## Radia review-fix (AST-1728)

Overall: CLEAN. \[bug-repro\] OK; What must still hold OK. Advisories only (admin route structural assert; metadata panel omits requested_url; no frozen Citations on bug). Recommended: Review Posted → User Testing (resolve skipped).

### Comments

#### radia — 2026-09-20T16:32:14.439Z
[code-rubric] PROCEED (Commit: fd3031d3fd12dea4ae0c738fade7446114ba07b0) Admin Telescope fix clean

#### katherine — 2026-09-20T16:29:06.302Z
`origin/sub/AST-1721/AST-1728-telescope-admin-page` @ `fd3031d3` · [bug-repro] green; TestTelescopeRoutes exact-html assert still needs Betty additive scrape_meta (board REVISE leftover)

#### betty — 2026-09-20T16:24:22.929Z
[bug-repro]
`origin/sub/AST-1721/AST-1728-telescope-admin-page` @ `90773dc5` · repro lands red, awaits fix

#### joan — 2026-09-20T16:21:58.826Z
[board-joan]  CANON: OK

#### betty — 2026-09-20T16:21:32.891Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md (+ no AdminTelescope bible entry) — AST-1725 TestTelescopeRoutes need additive scrape_meta asserts; new AdminTelescope page (§6c) + POST /api/admin/telescope + admin_telescope_scrape have no coverage for the repro path

#### katherine — 2026-09-20T16:19:33.407Z
`origin/sub/AST-1721/AST-1728-telescope-admin-page` @ `90ad53fdf90ffb9937352e14105877033100df49` · plan-fix admin page

#### chuckles — 2026-09-20T16:10:27.691Z
[check-linear] Plan Discuss — parent scope already amended; next is Katherine re-run plan-fix (fix lane F1) to leave Plan Discuss

#### susan — 2026-09-20T16:09:35.558Z
@chuckles what needs to happen for this to continue?

#### chuckles — 2026-09-20T15:58:56.329Z
[check-linear] Plan Discuss — AST-1721 Component/Technical scope + AC amended for Telescope admin UI/API + scrape metadata; Katherine can re-run plan-fix

#### susan — 2026-09-20T15:56:40.901Z
@chuckles please amend the original description of the parent ticket to accommodate the additional tickets functionality so that Katherine can proceed.

#### katherine — 2026-09-20T14:41:56.260Z
[scope-gate] Admin UI is outside AST-1721 Component/Technical scope.

Need (kind of change not covered):
- Admin frontend page under `src/ui/frontend/` (URL, html|text, option toggles, raw response + scrape-metadata display)
- Admin-authenticated API route under `src/ui/api/` that proxies to Telescope / returns content + metadata
- Possibly contract fields on `service/telescope/` and/or `src/external/telescope.py` for scrape metadata (bot-block, cookies, other scrape failures) — parent AC/contract today is `final_url` + text|html|links only

Parent Component scope covers only: `service/telescope/` (+ Dockerfile/requirements/railway.toml), `src/external/telescope.py`, delete `playwright.py`, import-path-only rewires in `roster`/`gazer`/`meteorite`, `src/utils/config.py`, root `requirements.txt`, CI import fence. No `src/ui/**` / frontend rows; Technical scope has the same set.

Cannot Plan Ready / patch a sibling plan (1725–1727) without inventing UI files those docs never owned. Please amend parent (or this bug) Scope for the admin surface + metadata contract, or confirm a different approach — @susan

---

_Implementation detail may live in git history on `origin/dev`._
