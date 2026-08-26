# Api Companies

**Test module:** `tests/component/ui/api/test_api_companies.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_companies.py` | `tests/component/ui/api/test_api_companies.py` | yes |

---

### AST-1495 · AST-1484

**Parent:** [AST-1484 — Create meteorite companies per email address](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address). **Publish:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`.

`GET /api/companies?view=meteorite_list` filters **METEORITE** state; counts key `/companies/meteorite_list`. Page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| meteorite_list view + counts badge key | `src/ui/api/api_companies.py` | revised **`TestCompaniesRoutes`** |

**Broken / obsolete:** none — additive view branch.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes \
  -q
```
