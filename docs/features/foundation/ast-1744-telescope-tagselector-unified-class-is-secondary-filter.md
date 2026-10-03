# AST-1744 — Telescope tag/selector unified; class is secondary filter

<!-- linear-archive: AST-1744 archived 2026-10-02 -->

## Linear archive (AST-1744)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1744/telescope-tagselector-unified-class-is-secondary-filter  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] Tag and Selector should be the same thing (html, div, span, body, head, ul). class name should be secondary filter (elements within the tag with `class="<classname>"`

## As-is

Tag and selector are treated as separate concepts for element filtering (html/div/span/body/head/ul), which confuses operators.

## To-be

Tag and selector are the same thing (element tag names); class name is a secondary filter for elements within that tag with class="<classname>".

## Suggested engineer

Ada Lovelace

## Proposed change

- [X] `service/telescope/capture.py` — unify tag/selector primary; class_name secondary → `{tag}.{class}` / `.{class}`; drop XOR
- [X] `service/telescope/app.py` — Field docs + primary(+class) logging; CaptureQueryError → 400
- [X] `AdminTelescope.tsx` — single Tag primary + Class always enabled; remove Selector slot
- [X] Platform pass-through unchanged (`telescope.py` / `api_admin.py` already forward fields)
- [X] Radia fix-now: restack onto ftr; Betty stripped AST-1746-only tests/bible; keep unify product

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1744-telescope-tag-selector-unified-class-secondary-filter`

**Bug-repro:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/service/test_telescope_app.py::TestTelescopeRoutes::test_ast1744_bare_primary_plus_class_name_resolves_to_tag_class -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTelescope.test.tsx -t 'AST-1744'
```

Also: `test_ast1744_tag_plus_class_name_resolves_to_tag_class`, `test_ast1744_complex_selector_plus_class_name_still_400`.

### Comments

#### betty — 2026-09-21T02:07:03.160Z
merge-tests(AST-1744) is singular on origin/sub/AST-1721/AST-1744-telescope-tag-selector-unified-class-secondary-filter @ 90de2330 (rebuild onto ftr+product; validate-sub-log ok).

#### chuckles — 2026-09-21T02:01:43.045Z
[merge-child] blocked: duplicate merge-tests(AST-1744) on sub — count=3 (amend on tests, one merge-tests only). @Betty White please collapse to a single merge-tests(AST-1744) on origin/sub/AST-1721/AST-1744-telescope-tag-selector-unified-class-secondary-filter (keep AST-1744 repros + strip of 1746; drop the extra merge-tests commits). Then reassign Ada.

#### betty — 2026-09-21T01:52:04.592Z
[qa-handoff]
AST-1746-only tests/bible stripped from publish tip @ `360faa07`. AST-1744 repros kept. Ready for resolve-child.

#### ada — 2026-09-21T01:50:02.963Z
[qa-handoff]
@Betty White

Product restack for Radia fix-now is on `origin/sub/AST-1721/AST-1744-telescope-tag-selector-unified-class-secondary-filter` @ `b37da2bc593edc814556861d5160706eacef0137` (`sync(ftr)` + `resolve(AST-1744)`). Kept AST-1744 unify tag/selector + class secondary; Admin Tag+Class only.

Engineer hook blocks `tests/**` and `docs/test-bible/**`, so I cannot land the sibling strip. Please remove AST-1746-only coverage from this publish tip (do not touch AST-1744 repros):

1. `tests/component/service/test_telescope_app.py` — delete `test_ast1746_html_id_resolves_to_hash_id` and `test_ast1746_selector_plus_id_returns_400`
2. `tests/component/frontend/pages/test_AdminTelescope.test.tsx` — delete `AST-1746: AdminTelescope exposes optional Id filter control`
3. `docs/test-bible/service/telescope.md` — delete `### AST-1746 · … optional id filter` section
4. `docs/test-bible/frontend/pages.md` — delete `### AST-1746 · … AdminTelescope Id control` section

Stay Review Posted until that lands and you reassign Ada.

#### radia — 2026-09-21T01:40:30.491Z
[code-rubric] REVIEW (Commit: 6da4a681) Restack; drop sibling scope

#### betty — 2026-09-21T01:30:00.246Z
[bug-repro]
`origin/sub/AST-1721/AST-1744-telescope-tag-selector-unified-class-secondary-filter` @ `6e0f6760` · repro lands red, awaits fix

#### joan — 2026-09-21T01:27:22.684Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:26:21.449Z
[board-betty] TESTS: REVISE
What: docs/test-bible/service/telescope.md (+ AdminTelescope) — rewrite test_ast1736_selector_plus_class_name_returns_400 (bare tag+class now legal→tag.class); missing tag+class_name combine + Admin single-primary asserts

#### ada — 2026-09-21T01:25:17.990Z
`origin/sub/AST-1721/AST-1744-telescope-tag-selector-unified-class-secondary-filter` @ `079dd68f94a7a2ee49d02e71062cf9e95506c7bc` · unify tag/selector primary

---

_Implementation detail may live in git history on `origin/dev`._
