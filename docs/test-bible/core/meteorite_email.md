# meteorite_email (mailbox runner)

**Test module:** `tests/component/core/test_meteorite_email.py`

> **AST-1467 / AST-1466:** `docs/test-bible/core/gaze_email.md` retired — folded here. Legacy `gaze_email` product identity is gone; candidate-bound mailbox + Land Meteorite selected-ids live under `meteorite_email` / `METEORITE_EMAIL_MAILBOX_CONFIG`. Inventory gate: `tests/component/core/test_ast1467_gaze_email_retire.py`.

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/meteorite_email.py` | `tests/component/core/test_meteorite_email.py` | no |

---

### AST-1090 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`.

Null-candidate mailbox runner: From-bind → unbound age→Trash → bound shapes (ignore / subject URL / html_links / subject_body) → Ruth parse + Playwright scrape → **per-candidate** `job_link_exists_for_candidate` dedupe → `create_meteorite_job` → archive on create or all-duplicate skip; Style D when `debug=True`. Wiring: **`docs/test-bible/core/dispatcher.md`** · config/data/gmail: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/data/database/dispatch_tasks.md`** · **`docs/test-bible/data/database.md`** / jobs cluster · **`docs/test-bible/external/gmail.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Subject URL + unbound stale helpers | `src/core/meteorite_email.py` | **`TestAst1090SubjectIsUrl`**, **`TestAst1090UnboundStale`** |
| Runner outcomes (trash/ignore/create/archive/Style D) | `src/core/meteorite_email.py` | **`TestAst1090RunMeteoriteEmail`** |

**Broken / obsolete:** none for this new module.

**Integration:** no existing scenarios assert `gaze_email` runner — none revised (do not invent new integration coverage).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py \
  -q
```


### AST-1136 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`.

Candidate-bound `run_meteorite_email`: requires row `candidate_id`; filters From→A; unbound leave/Trash hygiene; stamps `update_candidate_last_email_check` after completed run (incl. zero matches); Style D `run-start` / per-message / `run-complete`. Public `process_meteorite_email_messages` for AST-1129 (bound ingest only — no list/Trash/stamp). Config comment-only. Provision/Avail: siblings **AST-1134** / **AST-1135**.

| Area | Source | Component tests |
| --- | --- | --- |
| Bound filter + stamp + process_ helper | `src/core/meteorite_email.py` | **`TestAst1136CandidateBoundMeteoriteEmail`**; revised **`TestAst1090RunMeteoriteEmail`** |

**Broken / obsolete (Betty revision):** null-shell `run_meteorite_email({})` calls (now require `candidate_id`); stamp stub required on runner tests. **AST-1140 return:** `_handle_bound` mock returns must be 5-tuple when tip includes selected-ids outcome string.

**Integration:** none — no existing scenario asserts candidate-bound gaze runner; do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py::TestAst1090RunMeteoriteEmail \
  tests/component/core/test_meteorite_email.py::TestAst1136CandidateBoundMeteoriteEmail \
  -q
```

### AST-1140 · AST-1129

**Parent:** [AST-1129 — Manage Email — select inbox messages and Land Meteorite](https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite). **Publish:** `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`.

`run_meteorite_email_selected_ids` ingests only explicit Astral inbox ids through shared `_handle_bound` (bind / route / scrape / dedupe / METEORITE_NEW / archive); skip outcomes for missing / unbound / unmatched; no `last_email_check` stamp, no Create strip/extract, no unbound Trash. Style D via `debug_func_selected` when `debug=True`. Config: **`docs/test-bible/utils/config.md`**. Admin HTTP: **`docs/test-bible/ui/api/api_inbox.md`** (**AST-1141**); React = sibling **AST-1142**.

| Area | Source | Component tests |
| --- | --- | --- |
| Selected-ids skips + bound ingest + forbidden call sites + debug gate | `src/core/meteorite_email.py` | **`TestAst1140RunMeteoriteEmailSelectedIds`** |
| Selected-ids config vocabulary | `src/utils/config.py` | **`TestAst1140GazeEmailSelectedConfig`** |
| Candidate-bound runner + process_ helper (AST-1136 on tip) | `src/core/meteorite_email.py` | **`TestAst1136CandidateBoundMeteoriteEmail`**; revised **`TestAst1090RunMeteoriteEmail`** |

**Broken / obsolete (Betty return pass — resolve `origin/dev` merge):** AST-1136 `_handle_bound` mocks must return 5-tuple `(processed, passed, failed, errors, outcome)` after AST-1140 helper change; sub tip must carry AST-1136 + AST-1140 test/bible surface from `origin/tests` / `origin/dev`.

**Integration:** none — no existing scenario asserts Land Meteorite selected-ids; do not invent new coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py::TestAst1140RunMeteoriteEmailSelectedIds \
  tests/component/utils/test_config.py::TestAst1140GazeEmailSelectedConfig \
  tests/component/core/test_meteorite_email.py::TestAst1090RunMeteoriteEmail \
  tests/component/core/test_meteorite_email.py::TestAst1136CandidateBoundMeteoriteEmail \
  -q
```

### AST-1144 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`.

html_links Ruth payload with dict `jobs[].metadata` still scrapes/creates/archives (runner uses `job_link` only). Schema fix: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Dict metadata ingest path | `src/core/meteorite_email.py` | **`TestAst1090RunMeteoriteEmail::test_html_links_dict_metadata_still_creates`** |

**Broken / obsolete:** none — additive case on existing class.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py::TestAst1090RunMeteoriteEmail::test_html_links_dict_metadata_still_creates \
  -q
```


### AST-1213 · AST-1182

**Parent:** [AST-1182 — Rename task to meteorite_email + AI payload as visible text/links](https://linear.app/astralcareermatch/issue/AST-1182/rename-task-to-meteorite-email-ai-payload-as-visible-textlinks). **Publish:** `origin/sub/AST-1182/AST-1213-ai-payload-as-visible-text-and-links`.

Ruth `live_content` for `html_links` / `subject_body` is visible text + optional `--- LINKS ---` (not raw HTML). Link walk uses `ruth_payload_link_exclude_substrings` (keeps click-tracking wrappers). Config: **`docs/test-bible/utils/config.md`**. Prompts: **`docs/test-bible/core/repo_admin_json.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Ruth payload link-exclude config | `src/utils/config.py` | **`TestAst1213RuthPayloadLinkExcludes`** |
| Visible-text prompts | `data/admin/agent_task.json` | **`TestAst1213MeteoriteEmailVisibleTextPrompts`** |

**Broken / obsolete (AST-1522 return):** **`TestAst1213RuthLivePayload`** removed — `_ruth_live_parts` / `_format_ruth_live_body` deleted with Ruth-first `_handle_bound` (AST-1521).

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1213RuthPayloadLinkExcludes \
  tests/component/core/test_repo_admin_json.py::TestAst1213MeteoriteEmailVisibleTextPrompts \
  -q
```

### AST-1294 · AST-1290

**Parent:** [AST-1290 — Only 32 of 34 jobs were loaded by parse_meteorite_email](https://linear.app/astralcareermatch/issue/AST-1290/only-32-of-34-jobs-were-loaded-by-parse-meteorite-email). **Publish:** `origin/sub/AST-1290/AST-1294-html-links-completeness-all-payload-job-links-land`.

Post-parse `_ensure_html_links_jobs_complete` on the `html_links` branch: every Ruth `--- LINKS ---` payload href lands in the jobs list used for ingest (stub `job_title: None` when Ruth omits the link). Match via `normalize_link`. Style D found/recorded/missing path-tail ids when `debug=True` and incomplete; silence when complete or `debug=False`. No `subject_url` / `subject_body` redesign; no Avail/coerce (AST-1282 / AST-1289).

| Area | Source | Component tests |
| --- | --- | --- |
| Helper UAT 34→34 + normalize + Style D + junk/extras | `src/core/meteorite_email.py` | **`TestAst1294HtmlLinksJobsComplete`** |
| html_links call site ingests stubs | `src/core/meteorite_email.py` | **`TestAst1294HtmlLinksJobsComplete::test_html_links_call_site_ingests_stubbed_links`** |

**Broken / obsolete (Betty revision):** AST-1213 live_content Style D cases that mocked `_ingest_link` — retired with **`TestAst1213RuthLivePayload`** (AST-1522). Entire **`TestAst1294HtmlLinksJobsComplete`** removed when Ruth-first html_links path dropped (AST-1521 / AST-1522).

**Integration:** no existing scenarios assert html_links completeness / gaze_email reconcile — none revised; do not invent new integration coverage.

```bash
# AST-1294 suite retired — no live pytest node; historical note only.
```


### AST-1467 · AST-1363

**Parent:** [AST-1363 — Clean up agent_task so that only the right meteorite email intake task is run](https://linear.app/astralcareermatch/issue/AST-1363/clean-up-agent-task-so-that-only-the-right-meteorite-email-intake-task). **Publish:** `origin/sub/AST-1363/AST-1467-gap-gaze-email-test-coverage-for-retire`. **Fix:** AST-1466.

Retire `gaze_email` test/bible identity; retarget mailbox runner + config/dispatcher/inbox/admin/repo_admin asserts to `meteorite_email`. Inventory `[bug-repro]` fails while legacy gaze identity still ships.

| Area | Source | Component tests |
| --- | --- | --- |
| Seed/config/module/dispatcher inventory | catalog + config + dispatcher | **`TestAst1467GazeEmailRetired`** |
| Mailbox runner (rehomed) | `src/core/meteorite_email.py` | **`test_meteorite_email.py`** (skip until module lands) |
| Config / admin / inbox / dispatch retargets | various | revised AST-1088/1090/1140/1134/1135/1141/1106 classes |

**Broken / obsolete (Betty):** `tests/component/core/test_gaze_email.py` deleted; `docs/test-bible/core/gaze_email.md` retired into this file. **Return (Review Posted):** bible `run_component_tests` blocks retargeted to `test_meteorite_email.py`; `test_AdminScheduledActions_AST1106.test.tsx` retired (gaze carve-out obsolete — see `docs/test-bible/frontend/pages.md` § AST-1106).

**Integration:** none — no existing scenario asserts gaze_email retirement; do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_ast1467_gaze_email_retire.py \
  -q
```


### AST-1522 · AST-1520

**Parent:** [AST-1520 — Emailed job description parsed as HTML](https://linear.app/astralcareermatch/issue/AST-1520/emailed-job-description-parsed-as-html). **Publish:** `origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests`. **Fix:** AST-1521.

`[bug-repro]` no-subject plain JD body → `land_meteorite(text=visible)` + Gmail archive (not Ruth `html_links` / `ignored-empty` pass-without-ingest). Green after AST-1521 make-fix.

| Area | Source | Component tests |
| --- | --- | --- |
| No-subject JD → land + archive | `src/core/meteorite_email.py` | **`TestAst1522NoSubjectJdLandsAndArchives::test_no_subject_jd_text_lands_and_archives`** |
| Selected-ids bound land (retarget) | `src/core/meteorite_email.py` | revised **`TestAst1140RunMeteoriteEmailSelectedIds`** (`land_meteorite`) |

**Broken / obsolete (this pass + return):** Ruth `html_links` / `subject_body` / `_ingest_link` / `ignored-empty` runner expectations — removed `TestAst1090` subject_url+html_links create cases, entire **`TestAst1213RuthLivePayload`**, entire **`TestAst1294HtmlLinksJobsComplete`**. **Return (Review Posted):** `TestAst1140` create→`land_meteorite`; bible AST-1213/1294 rows cleaned.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py::TestAst1522NoSubjectJdLandsAndArchives::test_no_subject_jd_text_lands_and_archives \
  tests/component/core/test_meteorite_email.py::TestAst1140RunMeteoriteEmailSelectedIds \
  -q
```


### AST-1531 · AST-1527

**Parent:** [AST-1527 — Generalize Meteorite Ingress Point](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point). **Publish:** `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact`.

Mailbox `_handle_bound` → `stage_meteorite(source_kind="email", source_id=mid)` on subject+html blob; archive via `_stage_archive_token` (land created / all-skip). Mechanical subject/href classify (`_subject_is_url`, scrape helpers) retired. Inbox / Contact cutover: **`docs/test-bible/core/inbox.md`**, **`docs/test-bible/core/contact.md`**. Stage core: **`docs/test-bible/core/meteorite.md`** (**AST-1530**).

| Area | Source | Component tests |
| --- | --- | --- |
| Bound stage land + skip-archive + archive token | `src/core/meteorite_email.py` | **`TestAst1531MailboxStageCutover`**; revised **`TestAst1090RunMeteoriteEmail::test_bound_stage_skip_archives`** |
| Empty-subject JD → stage + archive | `src/core/meteorite_email.py` | revised **`TestAst1522NoSubjectJdLandsAndArchives`** (`stage_meteorite`) |
| Selected-ids bound → stage | `src/core/meteorite_email.py` | revised **`TestAst1140RunMeteoriteEmailSelectedIds`** (`stage_meteorite`) |

**Broken / obsolete:** **`TestAst1090SubjectIsUrl`** skipped (helper deleted). Create/land mechanical mocks replaced with `stage_meteorite`.

**Integration:** none — do not invent new integration coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py::TestAst1531MailboxStageCutover \
  tests/component/core/test_meteorite_email.py::TestAst1522NoSubjectJdLandsAndArchives \
  tests/component/core/test_meteorite_email.py::TestAst1140RunMeteoriteEmailSelectedIds \
  tests/component/core/test_meteorite_email.py::TestAst1090RunMeteoriteEmail::test_bound_stage_skip_archives \
  -q
```
