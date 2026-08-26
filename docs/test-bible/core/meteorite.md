# Meteorite

**Test module:** `tests/component/core/test_meteorite.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/meteorite.py` | `tests/component/core/test_meteorite.py` | no |

---

### AST-1041 · AST-1034

**Parent:** [AST-1034 — Support meteorite jobs](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs). **Publish:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`.

Lazy-ensure `meteorite-<candidate_id>` from `METEORITE_CONFIG` (**METEORITE** after **AST-1493**; was IGNORE). Idempotent insert/no-op; Style D debug when `debug=True`. No job create (AST-1042). Leave-in-place (no reaper). Claim exclusion: **`docs/test-bible/data/database/companies.md`**. Config: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty id / insert once / no-op / Style D on+off | `src/core/meteorite.py` | **`TestAst1041EnsureMeteoriteCompany`** (Style D multi-detail revised **AST-1493**) |

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

`create_meteorite_job`: lazy-ensure + create carve-out insert into `METEORITE_CONFIG["job_create_state"]` (**METEORITE_NEW** after **AST-1056**; was **JD_READY** at AST-1042) with synthetic `latest_score`, HTML under `TRACKER_CONFIG` JD key. No `transition_job_state`. HTTP: **`docs/test-bible/ui/api/api_meteorite.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Validation / missing candidate / config landing+score+HTML / second job company no-op | `src/core/meteorite.py` | **`TestAst1042CreateMeteoriteJob`** (landing assert revised **AST-1056**) |

**Broken / obsolete:** none — additive create helper on existing module.

**Integration:** no existing scenario asserts meteorite job create — no revision; do not invent new integration coverage.

**AST-1042** narrowed run (with API):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  -q
```

---

### AST-1056 · AST-1052

**Parent:** [AST-1052 — Processing meteorites](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites). **Publish:** `origin/sub/AST-1052/AST-1056-create-lands-meteorite-jobs-in-meteorite-new`.

Config retarget only: create insert lands in **METEORITE_NEW**. Runtime body already read `job_create_state`; docstring honesty in product. Config primary: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Insert state from config | `src/core/meteorite.py` | revised **`TestAst1042CreateMeteoriteJob`** |

**Broken / obsolete:** hardcoded **JD_READY** create asserts in AST-1042.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1056MeteoriteCreateLanding \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  tests/component/ui/api/test_api_meteorite.py \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx
```

### AST-1061 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`.

Optional `job_link=` on `create_meteorite_job` for link-sourced ingest; `company_job_id` stays `None`.

| Area | Source | Component tests |
| --- | --- | --- |
| Optional job_link persist | `src/core/meteorite.py` | revised **`TestAst1042CreateMeteoriteJob`** (`test_optional_job_link_persists_company_job_id_none`) |

**Broken / obsolete:** none — additive kwarg.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  -q
```

---

### AST-1493 · AST-1484

**Parent:** [AST-1484 — Create meteorite companies per email address](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address). **Publish:** `origin/sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track`.

Stem-keyed `ensure_meteorite_company(stem=)` into **METEORITE**; leave-in-place for legacy IGNORE `meteorite-{candidate}` rows; `is_meteorite_company` = prefix **or** company state METEORITE; Style D includes `stem=`. Config: **`docs/test-bible/utils/config.md`** (**AST-1493**). Ruth/inbox stem wiring = siblings AST-1494 / AST-1495.

| Area | Source | Component tests |
| --- | --- | --- |
| Email / self / slug / default stem ensure + leave-in-place + track predicate + Style D stem | `src/core/meteorite.py` | **`TestAst1493StemEnsureAndTrack`** |
| Default ensure / Style D multi-detail (stem + company_state) | `src/core/meteorite.py` | revised **`TestAst1041EnsureMeteoriteCompany`** |
| Create path company state honesty | `src/core/meteorite.py` | revised **`TestAst1042CreateMeteoriteJob`** (IGNORE → METEORITE) |

**Broken / obsolete:** AST-1041 Style D last-`call_args` `candidate_id=` (product now emits multiple `debug_detail` lines ending in `stem=` / `company_state=`); AST-1042 hard `state == "IGNORE"` on ensured company.

**Integration:** no existing scenario asserts ensure/track — none revised; do not invent new integration coverage.

**AST-1493** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1041MeteoriteConfig \
  tests/component/utils/test_config.py::TestAst1493MeteoriteCompanyStateConfig \
  tests/component/core/test_meteorite.py::TestAst1041EnsureMeteoriteCompany \
  tests/component/core/test_meteorite.py::TestAst1493StemEnsureAndTrack \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob \
  -q
```
