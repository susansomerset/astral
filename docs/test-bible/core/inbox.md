# Inbox

**Test module:** `tests/component/core/test_inbox.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/inbox.py` | `tests/component/core/test_inbox.py` | no |

---

### AST-1032 · AST-1031

**Parent:** [AST-1031 — Receive email on gmail account for astral](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral). **Publish:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read`.

Thin core wrapper over `src.external.gmail` list/get: passthrough on success; `logger.warning` then re-raise on failure. No persistence / admin HTTP (AST-1033).

| Area | Source | Component tests |
| --- | --- | --- |
| List passthrough + log/re-raise | `src/core/inbox.py` | `tests/component/core/test_inbox.py` (**`TestListInboxMessages`**) |
| Get HTML passthrough + log/re-raise | `src/core/inbox.py` | `tests/component/core/test_inbox.py` (**`TestGetMessageHtml`**) |

**AST-1032** narrowed run (with external Gmail suite):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_gmail.py \
  tests/component/core/test_inbox.py
```


### AST-1047 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`.

List enrichment: each row gets `candidate_match` (`matched` + `astral_candidate_id`) from From via `get_candidate_id_for_query`. Get HTML path unchanged. Style D per-row when `debug=True`.

| Area | Source | Component tests |
| --- | --- | --- |
| List enrichment + Style D; get unchanged | `src/core/inbox.py` | revised **`TestListInboxMessages`**; **`TestAst1047InboxFromBind`**; **`TestGetMessageHtml`** (unchanged) |

**Broken / obsolete:** **`TestListInboxMessages.test_returns_external_rows`** expected exact external passthrough — product now adds `candidate_match` (revised).

**Integration:** no existing Admin inbox integration scenario — no revision.


### AST-1049 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`.

`strip_extract_email_html` + `create_meteorite_job_from_inbox_message`: rematch From, strip/wrap subject, call `create_meteorite_job`; Style D found→matched→extracted→recorded when `debug=True`.

| Area | Source | Component tests |
| --- | --- | --- |
| Strip + create orchestration | `src/core/inbox.py` | **`TestAst1049StripExtractEmailHtml`**; **`TestAst1049CreateMeteoriteJobFromInboxMessage`** |

**Broken / obsolete:** none — additive orchestration.

**Integration:** none; do not invent new integration coverage.

### AST-1061 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`.

`create_meteorite_job_from_inbox_message` routes through `ingest_meteorite_jobs_from_email_html_sync`; returns `created`/`skipped`/`mode`; Style D step 4 outcome `recorded` or `skipped`.

| Area | Source | Component tests |
| --- | --- | --- |
| Create → gazer ingest | `src/core/inbox.py` | revised **`TestAst1049CreateMeteoriteJobFromInboxMessage`** |

**Broken / obsolete:** AST-1049 mocks of `create_meteorite_job` — product now calls gazer ingest sync (revised).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  -q
```

### AST-1131 · AST-1130

**Parent:** [AST-1130 — Manage Email create button for job lists isn't working](https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working). **Publish:** `origin/sub/AST-1130/AST-1131-normalize-pasted-list-email-html`.

`strip_extract_email_html` calls `normalize_pasted_list_email_html` on the culled body before subject wrap. Primary helper: **`docs/test-bible/utils/formatting.md`** (**AST-1131**).

| Area | Source | Component tests |
| --- | --- | --- |
| Strip + paste normalize | `src/core/inbox.py` | **`TestAst1131StripNormalizePastedList`** |

**Broken / obsolete:** none — additive call; AST-1049 strip assertions still hold.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_inbox.py::TestAst1131StripNormalizePastedList \
  -q
```

### AST-1135 · AST-1128

**Parent:** [AST-1128 — gaze_email — candidate-bound dispatch (redesign)](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign). **Publish:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`.

`count_inbox_bound_by_candidate` / `count_inbox_messages_bound_to_candidate` — one inbox list → bind-filtered counts (Avail source). Admin stamp / AUTO due: **`docs/test-bible/ui/api/api_admin.md`** · **`docs/test-bible/core/dispatcher.md`**. Fake data due retired: **`docs/test-bible/data/database/dispatch_tasks.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Bind-filtered counts | `src/core/inbox.py` | **`TestAst1135InboxBoundCounts`** |

**Broken / obsolete:** none — additive helpers.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_inbox.py::TestAst1135InboxBoundCounts \
  -q
```

### AST-1313 · AST-1308

**Parent:** [AST-1308 — Email bind where email is in the To: field (alone)](https://linear.app/astralcareermatch/issue/AST-1308/email-bind-where-email-is-in-the-to-field-alone). **Publish:** `origin/sub/AST-1308/AST-1313-from-then-to-bind-debug-source`.

From unique hit wins; otherwise To binds only when exactly one remaining address after ignoring `INBOX_BIND_CONFIG["inbox_address"]` (alias of `GAZE_EMAIL_CONFIG["account_address"]`). Same helper for list enrichment and create rematch. Style D `func="inbox_bind"` (`bind_header` / `bind_address`); `candidate_match` stays `{matched, astral_candidate_id}`. Raw To field is **AST-1312**.

| Area | Source | Component tests |
| --- | --- | --- |
| `INBOX_BIND_CONFIG` | `src/utils/config.py` | **`tests/component/utils/test_config.py::TestAst1313InboxBindConfig`** |
| From-then-To list + create rematch + Style D | `src/core/inbox.py` | **`TestAst1313FromThenToBind`**; revised **`TestAst1047InboxFromBind::test_list_debug_emits_style_d`** (`inbox_bind`) |
| Auth unchanged (AC6) | `src/ui/api/api_inbox.py` | existing **`TestAst1033InboxApi`** list/get auth; **`TestAst1049InboxCreateJobApi::test_create_job_requires_auth`**; **`TestAst1141InboxLandMeteoriteApi::test_land_meteorite_requires_auth`** |

**Broken / obsolete:** **`TestAst1047InboxFromBind::test_list_debug_emits_style_d`** asserted `func="inbox_from_bind"` / `from_address=` — product now emits `inbox_bind` + `bind_header` / `bind_address` (revised).

**Integration:** none — no existing inbox bind scenario; do not invent coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1313InboxBindConfig \
  tests/component/core/test_inbox.py::TestAst1047InboxFromBind \
  tests/component/core/test_inbox.py::TestAst1313FromThenToBind \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/ui/api/test_api_inbox.py::TestAst1033InboxApi::test_list_requires_auth \
  tests/component/ui/api/test_api_inbox.py::TestAst1033InboxApi::test_get_requires_auth \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi::test_create_job_requires_auth \
  tests/component/ui/api/test_api_inbox.py::TestAst1141InboxLandMeteoriteApi::test_land_meteorite_requires_auth \
  -q
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness / branch-lock gate.

---

### AST-1495 · AST-1484

**Parent:** [AST-1484 — Create meteorite companies per email address](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address). **Publish:** `origin/sub/AST-1484/AST-1495-email-land-paths-apply-stem-company-attach`.

Email create/land paths: `create_meteorite_job_from_inbox_message` → `land_meteorite` (AST-1472); post-land Style D `company={land.get('company')!r}` when `debug=True`. Core land stem attach: **`docs/test-bible/core/meteorite.md`** (**AST-1495**).

| Area | Source | Component tests |
| --- | --- | --- |
| Create rematch + land + company debug detail | `src/core/inbox.py` | revised **`TestAst1049CreateMeteoriteJobFromInboxMessage`**; revised **`TestAst1313FromThenToBind::test_create_rematch_uses_to_when_from_misses`** |

**Broken / obsolete:** AST-1061 gazer ingest mocks / `mode=body` return shape — revised **AST-1495** to `land_meteorite` + `mode=land_meteorite`.

**Integration:** none revised.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_inbox.py::TestAst1049CreateMeteoriteJobFromInboxMessage \
  tests/component/core/test_inbox.py::TestAst1313FromThenToBind::test_create_rematch_uses_to_when_from_misses \
  -q
```


### AST-1531 · AST-1527

**Parent:** [AST-1527 — Generalize Meteorite Ingress Point](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point). **Publish:** `origin/sub/AST-1527/AST-1531-caller-cutover-mailbox-inbox-contact`.

`_land_bound_inbox_message` / `land_inbox_message_ids` / `run_fetch_email` stage stripped HTML with `source_kind="email"` / `source_id=mid` (empty strip → error, no stage). Legacy `create_meteorite_job_from_inbox_message` still lands directly (out of this cutover). Mailbox: **`docs/test-bible/core/meteorite_email.md`**. Contact: **`docs/test-bible/core/contact.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Strip → stage + empty gate + selected-ids shell | `src/core/inbox.py` | **`TestAst1531InboxStageCutover`** |

**Broken / obsolete:** none in Create strip path this pass.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_inbox.py::TestAst1531InboxStageCutover \
  -q
```


### AST-1537 · AST-1533

**Parent:** [AST-1533 — Manage Email gives HTML for the body of the message, not for the header, and it must include both.](https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header). **Publish:** `origin/sub/AST-1533/AST-1537-email-header-body-html-land-qualify`.

Shared header+body HTML assembly: `strip_extract_email_html` embeds From/To/Subject/Date via `INBOX_CREATE_JOB_CONFIG["subject_html_template"]`; land/create and `get_message_with_assembled_html` share that shape (`html_body` stays raw). Cross-module: **`docs/test-bible/core/meteorite_email.md`**, **`docs/test-bible/external/gmail.md`**, **`docs/test-bible/ui/api/api_inbox.md`**, **`docs/test-bible/utils/config.md`**. Sibling Manage Email React chrome = **AST-1538** (out of scope).

| Area | Source | Component tests |
| --- | --- | --- |
| Header+body strip + escape | `src/core/inbox.py` | revised **`TestAst1049StripExtractEmailHtml`** |
| Assembled get helper | `src/core/inbox.py` | **`TestAst1537AssembledHtmlGet`** |
| Land staged blob includes headers | `src/core/inbox.py` | revised **`TestAst1531InboxStageCutover::test_land_bound_stages_stripped_html`** |

**Broken / obsolete:** subject-only wrap asserts on strip/land — revised for From/To/Date classes + escaping.

**Integration:** none — no existing inbox/email-header integration scenario; do not invent.

## QA test manifest

1. Config template placeholders: `tests/component/utils/test_config.py::TestAst1049InboxCreateJobConfig`
2. Gmail Date on get: `tests/component/external/test_gmail.py::TestGetMessageHtml`
3. Strip header+body: `tests/component/core/test_inbox.py::TestAst1049StripExtractEmailHtml`
4. Assembled get: `tests/component/core/test_inbox.py::TestAst1537AssembledHtmlGet`
5. Inbox land headers: `tests/component/core/test_inbox.py::TestAst1531InboxStageCutover`
6. Mailbox shared strip: `tests/component/core/test_meteorite_email.py::TestAst1531MailboxStageCutover`
7. API get assembled: `tests/component/ui/api/test_api_inbox.py::TestAst1033InboxApi`
8. Paste-normalize still wraps: `tests/component/core/test_inbox.py::TestAst1131StripNormalizePastedList`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1049InboxCreateJobConfig \
  tests/component/external/test_gmail.py::TestGetMessageHtml \
  tests/component/core/test_inbox.py::TestAst1049StripExtractEmailHtml \
  tests/component/core/test_inbox.py::TestAst1537AssembledHtmlGet \
  tests/component/core/test_inbox.py::TestAst1531InboxStageCutover \
  tests/component/core/test_inbox.py::TestAst1131StripNormalizePastedList \
  tests/component/core/test_meteorite_email.py::TestAst1531MailboxStageCutover \
  tests/component/ui/api/test_api_inbox.py::TestAst1033InboxApi \
  -q
```

**Pass criterion:** pytest green on narrowed args — not zero-arg harness / branch-lock gate.
