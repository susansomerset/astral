# Meteorite

**Test module:** `tests/component/core/test_meteorite.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/meteorite.py` | `tests/component/core/test_meteorite.py` | no |

---

### AST-1041 · AST-1034

**Parent:** [AST-1034 — Support meteorite jobs](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs). **Publish:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`.

Lazy-ensure `meteorite-<candidate_id>` from `METEORITE_CONFIG` (IGNORE). Idempotent insert/no-op; Style D debug when `debug=True`. No job create (AST-1042). Leave-in-place (no reaper). Claim exclusion: **`docs/test-bible/data/database/companies.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty id / insert once / no-op / Style D on+off | `src/core/meteorite.py` | **`TestAst1041EnsureMeteoriteCompany`** |

**Broken / obsolete:** none — new module.

**Integration:** no existing scenario asserts meteorite placeholders — no revision; do not invent new integration coverage.

**AST-1041** narrowed run (with config + claim):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/core/test_meteorite.py \
  tests/component/data/database/test_companies.py::TestAst1041MeteoriteClaimExclusion \
  -q
```


---

### AST-1042 · AST-1034

**Parent:** [AST-1034 — Support meteorite jobs](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs). **Publish:** `origin/sub/AST-1034/AST-1042-api-create-job-under-meteorite-from-raw-html`.

`create_meteorite_job`: lazy-ensure + create carve-out insert into `METEORITE_CONFIG["job_create_state"]` (**JD_READY**) with synthetic `latest_score`, HTML under `TRACKER_CONFIG` JD key. No `transition_job_state`. HTTP: **`docs/test-bible/ui/api/api_meteorite.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validation / missing candidate / JD_READY+score+HTML / second job company no-op | `src/core/meteorite.py` | **`TestAst1042CreateMeteoriteJob`** |

**Broken / obsolete:** none — additive create helper on existing module.

**Integration:** no existing scenario asserts meteorite job create — no revision; do not invent new integration coverage.

**AST-1042** narrowed run (with API):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```
