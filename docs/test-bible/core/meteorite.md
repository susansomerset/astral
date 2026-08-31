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

---

### AST-1495 · AST-1484

**Parent:** [AST-1484 — Create meteorite companies per email address](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address). **Publish:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`.

`land_meteorite`: enrich-first (no pre-enrich default); per-row Ruth `company_stem` → `ensure_meteorite_company(stem=…)` → `save_meteorite_job(company=…)`; empty stem → `default_stem`; enrich failure → `company: None`. `create_meteorite_job` optional `stem=`. Inbox email paths: post-land Style D `company=`. Optional METEORITE companies list: **`docs/test-bible/ui/api/api_companies.md`**, **`docs/test-bible/frontend/pages.md`**, NAV **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Per-row stem attach + default stem + enrich-fail company None + land debug stem/company | `src/core/meteorite.py` | **`TestAst1495LandStemAttach`**; revised **`TestAst1470LandMeteorite`** |
| Optional `stem=` on create | `src/core/meteorite.py` | revised **`TestAst1042CreateMeteoriteJob`** (`test_optional_stem_forwards_to_ensure`) |
| Inbox create → land + post-land `company=` debug | `src/core/inbox.py` | revised **`TestAst1049CreateMeteoriteJobFromInboxMessage`**; revised **`TestAst1313FromThenToBind::test_create_rematch_uses_to_when_from_misses`** |

**Broken / obsolete:** AST-1470 enrich-failure asserted pre-enrich default `company` (revised **AST-1495**); AST-1049/1061 mocks of `ingest_meteorite_jobs_from_email_html_sync` / `mode=body` (product **AST-1472**/**AST-1495** uses `land_meteorite` + `mode=land_meteorite`).

**Integration:** no existing scenario asserts stem attach — none revised; do not invent new integration coverage.

**AST-1495** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1495LandStemAttach \
  tests/component/core/test_meteorite.py::TestAst1470LandMeteorite \
  tests/component/core/test_meteorite.py::TestAst1042CreateMeteoriteJob::test_optional_stem_forwards_to_ensure \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/core/test_inbox.py::TestAst1313FromThenToBind::test_create_rematch_uses_to_when_from_misses \
  tests/component/ui/api/test_api_companies.py::TestCompaniesRoutes \
  tests/component/utils/test_config.py::TestAst1495MeteoriteCompaniesNav \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CompaniesMeteorite.test.tsx
```

---

### AST-1517 · AST-1414

**Parent:** [AST-1414 — Estelle needs to be able to use our endpoints](https://linear.app/astralcareermatch/issue/AST-1414/estelle-needs-to-be-able-to-use-our-endpoints). **Publish:** `origin/sub/AST-1414/AST-1517-create-contact-meteorite`.

`create_contact_meteorite`: URL detector (`_contact_param_looks_like_url`); link mode → `contact_task_gazer_scrape` then `create_meteorite_job` with `job_link`; text mode → direct create; soft returns for scrape fail / empty visible text; Style D on `debug=True`. Markup/dispatch: **`docs/test-bible/core/contact.md`** (AST-1515, revised AST-1517).

| Area | Source | Component tests |
| --- | --- | --- |
| URL detector + create path + scrape soft-fail + Style D | `src/core/meteorite.py` | **`TestAst1517CreateContactMeteorite`** |

**Broken / obsolete:** AST-1515 **`TestAst1515ContactTaskMarkup`** / **`TestAst1515ContactEstelleTurnMarkup`** — `handler_unavailable` fixtures revised to mock `_resolve_contact_task_handler` → `None` (all six handlers now resolve).

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1517CreateContactMeteorite \
  tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup \
  tests/component/core/test_contact.py::TestAst1515ContactEstelleTurnMarkup \
  -q
```

---

### AST-1530 · AST-1527

**Parent:** [AST-1527 — Generalize Meteorite Ingress Point](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point). **Publish:** `origin/sub/AST-1527/AST-1530-core-stage-scrap-land`.

Public `stage_meteorite`: blob + source handle → `invoke_stage_meteorite` → classify outcome + `jobs[]` only (**AST-1560** retires inline scrap map / land on the table path). Skip outcomes return `skipped=True` with empty `jobs`. Catalog/config: **`docs/test-bible/utils/config.md`** (**AST-1529**). Invoke helper: **`docs/test-bible/core/consult.md`**. Table transitions: **AST-1560** dispatch runners.

| Area | Source | Component tests |
| --- | --- | --- |
| Classify-only stage gates / skip / Style D | `src/core/meteorite.py` | **`TestAst1530StageMeteorite`** (revised AST-1560) |

**Broken / obsolete (AST-1560):** `_map_stage_jobs_to_scraps` tests and land-via-`stage_meteorite` assertions — removed; classify-only contract.

**Integration:** none — do not invent new integration coverage.

## QA test manifest

1. `tests/component/core/test_meteorite.py::TestAst1530StageMeteorite`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1530StageMeteorite \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1560 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1560-stage-scrape-land-transitions`.

Dispatcher-driven table transition runners: `run_stage_meteorite` (NEW → SCRAPE_LINK | READY), `run_scrape_meteorite` (Playwright → READY | BOT_BLOCKED | ERROR), `run_land_meteorite` (READY → `METEORITE_NEW` job + LANDED, no enrich-in-front). Always-on row-transition monitoring via `log_meteorite_row_transition`. Config/dispatcher wiring: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/core/dispatcher.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Stage / scrape / land runners + monitoring | `src/core/meteorite.py` | **`TestAst1560RunStageMeteorite`**, **`TestAst1560RunScrapeMeteorite`**, **`TestAst1560RunLandMeteorite`** |
| Revised classify-only public stage | `src/core/meteorite.py` | **`TestAst1530StageMeteorite`** |

**Broken / obsolete:** **`TestAst1530StageMeteorite`** scrap-map / land-via-stage tests (AST-1560).

**Integration:** none revised.

## QA test manifest

1. `tests/component/core/test_meteorite.py::TestAst1530StageMeteorite`
2. `tests/component/core/test_meteorite.py::TestAst1560RunStageMeteorite`
3. `tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite`
4. `tests/component/core/test_meteorite.py::TestAst1560RunLandMeteorite`
5. `tests/component/core/test_dispatcher.py::TestAst1560IngressTransitionDispatchOne`
6. `tests/component/utils/test_config.py::TestAst1560IngressDispatchConfig`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1530StageMeteorite \
  tests/component/core/test_meteorite.py::TestAst1560RunStageMeteorite \
  tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite \
  tests/component/core/test_meteorite.py::TestAst1560RunLandMeteorite \
  tests/component/core/test_dispatcher.py::TestAst1560IngressTransitionDispatchOne \
  tests/component/utils/test_config.py::TestAst1560IngressDispatchConfig \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1562 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1562-retention-sweep-delete-meteorite-email`.

Scheduled `run_meteorite_retention`: batched purge of old `LANDED` rows + always-on info lines for stale `ERROR` / `BOT_BLOCKED` / `ABANDONED` (no deletes in transition runners). Deletes `src/core/meteorite_email.py`; retires unbound/selected-ids mailbox literals. Config/dispatcher: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/core/dispatcher.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Retention runner | `src/core/meteorite.py` | **`TestAst1562RunMeteoriteRetention`** |
| Retention config + seed | `src/utils/config.py` | **`TestAst1562RetentionConfig`** |
| Dispatcher retention branch | `src/core/dispatcher.py` | **`TestAst1562RetentionDispatchOne`** |
| Module retirement inventory | — | revised **`TestAst1467GazeEmailRetired`**; **`test_meteorite_email.py`** module skip |

**Broken / obsolete:** **`TestAst1140GazeEmailSelectedConfig`** (auto-skips — selected-ids keys gone); **`test_meteorite_email.py`** entire module (module deleted); revised **`TestAst1088GazeEmailConfig`**, **`TestAst1090GazeEmailRunnerConfig`**.

**Integration:** none revised.

## QA test manifest

1. `tests/component/core/test_meteorite.py::TestAst1562RunMeteoriteRetention`
2. `tests/component/utils/test_config.py::TestAst1562RetentionConfig`
3. `tests/component/core/test_dispatcher.py::TestAst1562RetentionDispatchOne`
4. `tests/component/core/test_ast1467_gaze_email_retire.py::TestAst1467GazeEmailRetired`
5. Revised: `TestAst1088GazeEmailConfig`, `TestAst1090GazeEmailRunnerConfig`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1562RunMeteoriteRetention \
  tests/component/utils/test_config.py::TestAst1562RetentionConfig \
  tests/component/core/test_dispatcher.py::TestAst1562RetentionDispatchOne \
  tests/component/core/test_ast1467_gaze_email_retire.py::TestAst1467GazeEmailRetired \
  tests/component/utils/test_config.py::TestAst1088GazeEmailConfig \
  tests/component/utils/test_config.py::TestAst1090GazeEmailRunnerConfig \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1561 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste`.

`apply_paste` (`BOT_BLOCKED` → `READY`, no classify); lookup helpers; `run_notify_meteorite_bot_blocked` (Estelle DM + nag → `ABANDONED`). Config/dispatcher: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/core/dispatcher.md`**. Contact paste routing: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| apply_paste + lookups + notify runner | `src/core/meteorite.py` | **`TestAst1561ApplyPaste`**, **`TestAst1561BotBlockedLookup`**, **`TestAst1561RunNotifyBotBlocked`** |
| Slack paste hook | `src/core/contact.py` | **`TestAst1561ContactPasteRouting`** |
| Notify config + seed | `src/utils/config.py` | **`TestAst1561BotBlockedNotifyConfig`** |
| Dispatcher notify branch | `src/core/dispatcher.py` | **`TestAst1561BotBlockedNotifyDispatchOne`** |

**Broken / obsolete:** none — additive on AST-1560 `BOT_BLOCKED` scrape path.

**Integration:** none revised.

## QA test manifest

1. `tests/component/core/test_meteorite.py::TestAst1561ApplyPaste`
2. `tests/component/core/test_meteorite.py::TestAst1561BotBlockedLookup`
3. `tests/component/core/test_meteorite.py::TestAst1561RunNotifyBotBlocked`
4. `tests/component/core/test_contact.py::TestAst1561ContactPasteRouting`
5. `tests/component/utils/test_config.py::TestAst1561BotBlockedNotifyConfig`
6. `tests/component/core/test_dispatcher.py::TestAst1561BotBlockedNotifyDispatchOne`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1561ApplyPaste \
  tests/component/core/test_meteorite.py::TestAst1561BotBlockedLookup \
  tests/component/core/test_meteorite.py::TestAst1561RunNotifyBotBlocked \
  tests/component/core/test_contact.py::TestAst1561ContactPasteRouting \
  tests/component/utils/test_config.py::TestAst1561BotBlockedNotifyConfig \
  tests/component/core/test_dispatcher.py::TestAst1561BotBlockedNotifyDispatchOne \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1559 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1559-check-inbox-monitoring-log`.

`check_inbox` fan-out + monitoring + archive; dispatcher repoint. See **`docs/test-bible/utils/config.md`**, **`docs/test-bible/core/candidate.md`**, **`docs/test-bible/core/dispatcher.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| check_inbox | `src/core/meteorite.py` | **`TestAst1559CheckInbox`** |
| Email aliases | `src/core/candidate.py` | **`TestAst1559EmailAliasesForCandidate`** |
| Monitoring config | `src/utils/config.py` | **`TestAst1559MonitoringConfig`**; revised **`TestAst1090GazeEmailRunnerConfig`**, **`TestAst1140GazeEmailSelectedConfig`** |
| Dispatcher | `src/core/dispatcher.py` | revised **`TestAst1090GazeEmailDispatchOne`** |

**Broken / obsolete:** `meteorite_email.run` config/dispatcher asserts; **`TestAst1140RunMeteoriteEmailSelectedIds`** create spy (**AST-1558**).

**Integration:** none revised.

## QA test manifest

1. `tests/component/core/test_meteorite.py::TestAst1559CheckInbox`
2. `tests/component/core/test_candidate.py::TestAst1559EmailAliasesForCandidate`
3. `tests/component/utils/test_config.py::TestAst1559MonitoringConfig`
4. `tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne`
5. Revised: `TestAst1090GazeEmailRunnerConfig`, `TestAst1140GazeEmailSelectedConfig`, `TestAst1140RunMeteoriteEmailSelectedIds`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1559CheckInbox \
  tests/component/core/test_candidate.py::TestAst1559EmailAliasesForCandidate \
  tests/component/utils/test_config.py::TestAst1559MonitoringConfig \
  tests/component/core/test_dispatcher.py::TestAst1090GazeEmailDispatchOne \
  tests/component/core/test_meteorite_email.py::TestAst1140RunMeteoriteEmailSelectedIds \
  -q
```
