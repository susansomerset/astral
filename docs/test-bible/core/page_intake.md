# Page intake

**Test module:** `tests/component/core/test_page_intake.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/page_intake.py` | `tests/component/core/test_page_intake.py` | no |

---

### AST-1227 · AST-1168

**Parent:** [AST-1168 — page_intake — server-side page classification and single-listing ingest](https://linear.app/astralcareermatch/issue/AST-1168/page-intake-server-side-page-classification-and-single-listing-ingest). **Publish:** `origin/sub/AST-1168/AST-1227-listing-to-meteorite-ingest`.

`ingest_recognized_listing`: per-candidate `job_link` / `company_job_id` dedupe → `create_meteorite_job` (`METEORITE_NEW`, `job_link=page_url`); Style D found/recorded / skipped-duplicate when `debug=True`. Exact URL equality for AC2 (no normalization). Classification / HTTP surface: siblings AST-1226 / AST-1228. Create helper: **`docs/test-bible/core/meteorite.md`**. Email parity pattern: **`docs/test-bible/core/gazer.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validation / create+link / known_job_link / known_company_job_id / cross-candidate / Style D on+off | `src/core/page_intake.py` | **`TestAst1227IngestRecognizedListing`** |

**Broken / obsolete:** none — new module.

**Integration:** no existing scenario asserts Surfer page_intake ingest — no revision; do not invent new integration coverage.

**AST-1227** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_page_intake.py::TestAst1227IngestRecognizedListing \
  -q
```
