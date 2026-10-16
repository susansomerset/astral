# AST-1746 — Telescope add optional id filter parameter

<!-- linear-archive: AST-1746 archived 2026-10-02 -->

## Linear archive (AST-1746)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1746/telescope-add-optional-id-filter-parameter  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] Please add "id" as an optional parameter. This would be similar to class, but would look for `id="<idstring>"` Update the description of the parent ticket to include the scope, and issue a bug ticket.

## As-is

There is no optional id parameter to filter elements by id="<idstring>".

## To-be

An optional id parameter (like class) filters by id="<idstring>"; parent Component/Technical scope includes this surface; admin UI exposes the control.

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `service/telescope/capture.py` — `resolve_capture_query` accepts optional `id` → `#id` / tag+class combinations; selector+id → 400
- [X] `service/telescope/app.py` — optional `id` on request models; wire into resolve + filter-mode log
- [X] `src/external/telescope.py` + `src/ui/api/api_admin.py` — pass-through `id`
- [X] `src/ui/frontend/src/pages/AdminTelescope.tsx` — Id control in secondary-filter group with Tag/Class

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1746-telescope-add-optional-id-filter-parameter` @ `0611289f` (`code` after qa-fix \[bug-repro\])

**Bug-repro (must flip red→green after make-fix):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1746_html_id_resolves_to_hash_id \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1746_selector_plus_id_returns_400 -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx -t AST-1746
```

Pre-fix: `id` ignored (selector stays omit/default); selector+id returns 200; Admin has Class name but no Id control.
Post-fix: all three \[bug-repro\] assertions green.

## Radia review-fix (AST-1746)

Overall: CLEAN / PROCEED — optional `id` filter delivered; \[bug-repro\] OK; What must still hold OK. Advisories only (publish-ref carry, optional links assert, Citations). → User Testing (resolve-child skipped).

### Comments

#### radia — 2026-09-21T01:45:19.373Z
[code-rubric] PROCEED (Commit: 0611289f) optional id filter clean

#### betty — 2026-09-21T01:28:26.772Z
[bug-repro]
`origin/sub/AST-1721/AST-1746-telescope-add-optional-id-filter-parameter` @ `b9d40129` · repro lands red, awaits fix

#### joan — 2026-09-21T01:27:01.645Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:26:18.441Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md (+ AdminTelescope) — missing id:"hero"→#hero resolve into capture, selector+id→400, Admin Id control; AST-1736 only covers class_name

#### ada — 2026-09-21T01:25:00.402Z
`origin/sub/AST-1721/AST-1746-telescope-add-optional-id-filter-parameter` @ `7748df56` · optional id filter planned

---

_Implementation detail may live in git history on `origin/dev`._
