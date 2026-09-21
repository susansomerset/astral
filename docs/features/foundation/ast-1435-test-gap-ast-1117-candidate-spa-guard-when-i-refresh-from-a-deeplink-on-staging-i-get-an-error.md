# AST-1435 — Test gap: AST-1117 candidate SPA guard (When I refresh from a deeplink on staging I get an error)

<!-- linear-archive: AST-1435 archived 2026-09-09 -->

## Linear archive (AST-1435)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1435/test-gap-ast-1117-candidate-spa-guard-when-i-refresh-from-a-deeplink  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1424 — When I refresh from a deeplink on staging I get an error  
**Blocked by / blocks / related:** parent: AST-1424

### Description

## What this implements

Test hole named by AST-1433 fix-board: rewrite `TestAst1117CandidateSpaGuard` / `TestAst1117ViteCandidateProxy` (they assert blanket `/candidate` 404 + Vite proxy) and add GET `/candidate/backstory` → 200 `index.html`. Bible: `docs/test-bible/ui/server.md`. Product change stays on AST-1433; this child only lands the tests (qa-fix repro-first).

## Citations

none — sibling gap of AST-1433; original coverage AST-1117.

## Acceptance criteria

* Existing AST-1117 candidate SPA guard tests no longer assume every `/candidate` path JSON-404s.
* Repro GET `/candidate/backstory` is covered (200 `index.html` after the product fix; red on the pre-fix tree).
* Print-prefix unmatched paths still JSON 404; Vite still proxies `/candidate/resume` and `/candidate/cover`.

## Boundaries

* Does not implement the `serve_react` / Vite proxy product change (AST-1433).
* Does not change AST-625 frontend auth tests.

## Notes for planning

Board: `[board-betty] TESTS: REVISE` on AST-1433. Drive via qa-fix (F4), not a new plan doc.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1424-refresh-from-deeplink-error`, child `sub/AST-1424/<this-id>-test-gap-candidate-spa-guard`.

## QA test manifest

`origin/sub/AST-1424/AST-1435-test-gap-candidate-spa-guard` @ `f5d78297` (`merge-tests(AST-1435): origin/tests 9f36f133f4b3ac6443487dc64458d65e14349022`)

### 1. Existing coverage (bible-backed)

none for this gap — AST-1117 assertions were the pre-fix contract.

### 2. Broken / obsolete (rewritten this pass)

1. `tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard::test_candidate_prefix_returns_404_json_not_spa`
2. `tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard::test_candidate_exact_path_returns_404_json`
3. `tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy::test_vite_config_proxies_candidate_to_flask`

### 3. Gaps (new this pass)

1. **\[bug-repro\]** `tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard::test_candidate_backstory_serves_index` — GET `/candidate/backstory` → 200 `index.html` (red on pre-fix: 404 JSON)
2. `test_candidate_prefix_spa_routes_serve_index` / `test_candidate_exact_path_serves_index`
3. `test_unmatched_print_resume_prefix_returns_404_json` / `test_unmatched_print_cover_prefix_returns_404_json`
4. `TestAst1117ViteCandidateProxy::test_vite_config_proxies_print_html_not_candidate_spa`

**Bible shasum** (on publish tip):

* `docs/test-bible/ui/server.md` `9989b368ae1a14bff048df004182499329d5ce39`

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_server.py::TestAst1117CandidateSpaGuard \
  tests/component/ui/test_server.py::TestAst1117ViteCandidateProxy \
  -q
```

### Comments

#### betty — 2026-08-19T00:40:55.795Z
[bug-repro]
`origin/sub/AST-1424/AST-1435-test-gap-candidate-spa-guard` @ `f5d78297` · repro lands red, awaits fix

#### chuckles — 2026-08-19T00:32:52.186Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/server.md — broken test — TestAst1117CandidateSpaGuard/ViteCandidateProxy assert blanket /candidate 404+proxy; repro GET /candidate/backstory → 200 index.html uncovered.
Copied from AST-1433 board so qa-fix on this gap child can see the named scope. Product fix is AST-1433.

---

_Implementation detail may live in git history on `origin/dev`._
