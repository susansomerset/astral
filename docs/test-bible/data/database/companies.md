# Companies

**Test module:** `tests/component/data/database/test_companies.py`

| Area | Sources | Tests |
| --- | --- | --- |
| save / update / list | `src/data/database.py` | `TestSaveCompany`, `TestUpdateCompany`, `TestListCompanies` |

---

### AST-877 · AST-864

**Originating search term on discovered companies:** nullable `company.originating_search_term` (denormalized CSE string, not a FK). `save_company` stamps on insert and **preserves** when the caller omits the arg. `update_company` / vet-ignore transitions leave the column untouched (`_UPDATE_COMPANY_ALLOWED` excludes it). Discovery CSE loop keeps `(term, hit)` and stamps via `record_inflow_discovery_hit` / `ingest_new_companies`. Debug working detail includes `originating_search_term=…`. New/Inactive/Ignored list shapes + CompanyDetailModal read-only Summary row for UAT.

| # | Scenario | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Column store + INSERT OR REPLACE preserve + state update leaves term + non-CSE null | `src/data/database.py` | `tests/component/data/database/test_companies.py::TestAst877OriginatingSearchTerm` |
| 2 | Record/ingest stamp; retain after VET_FAILED; batch stamps CSE term; debug detail | `src/core/roster.py` | `tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm` |
| 3 | New/Inactive/Ignored shapes include column; watch shapes omit | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst877OriginatingSearchTermShapes` |
| 4 | Detail modal shows term / em dash; PUT body excludes column | `CompanyDetailModal.tsx` | `tests/component/frontend/components/test_CompanyDetailModal.test.tsx` |

**Broken / obsolete (Betty revision):** `test_CompanyDetailModal.test.tsx` — api mock lacked `setAuthTokenGetter` / `setUnauthorizedHandler` and `/api/state_ui_manifest` (State UI substrate); rewired via `pages/page-mocks` `installBaseApiMocks`. Existing AST-505/775 record + batch tests still green (term optional).

**AST-877** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_companies.py::TestAst877OriginatingSearchTerm \
  tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm \
  tests/component/utils/test_config.py::TestAst877OriginatingSearchTermShapes \
  -q
```

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CompanyDetailModal.test.tsx
```

**Pass criterion:** pytest green on items 1–3 + Vitest green on item 4 — not zero-arg harness / branch-lock gate.
