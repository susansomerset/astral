# Api Inbox

**Test module:** `tests/component/ui/api/test_api_inbox.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/api/api_inbox.py` | `tests/component/ui/api/test_api_inbox.py` | no |

---

### AST-1033 · AST-1031

**Parent:** [AST-1031 — Receive email on gmail account for astral](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral). **Publish:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen`.

Thin `@require_admin` Flask wrappers over `src.core.inbox` — list/get JSON; upstream failures → 502; blank message id → 400. Page §6c: **`docs/test-bible/frontend/pages.md`**. Nav: **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| List/get + auth + 502/400 | `src/ui/api/api_inbox.py` | `tests/component/ui/api/test_api_inbox.py` (**`TestAst1033InboxApi`**) |

**AST-1033** narrowed run (API + nav; frontend separate):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py \
  tests/component/utils/test_config.py::TestAst1033ReadEmailNav
```


### AST-1047 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1047-reusable-get-candidate-string-lookup-from-bind`.

`inbox_list_messages` passes `ui_llm_debug(...)` into `list_inbox_messages(debug=…)` for From→candidate_match enrichment.

| Area | Source | Component tests |
| --- | --- | --- |
| List debug flag wiring | `src/ui/api/api_inbox.py` | revised **`TestAst1033InboxApi.test_list_messages_ok`**; **`test_list_passes_ui_llm_debug`** |

**Broken / obsolete:** none beyond asserting `debug=` call kwargs on list.

**Integration:** no existing scenario — no revision.


### AST-1049 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`.

`POST /api/admin/inbox/messages/<id>/create-job` (`@require_admin`, `ui_llm_debug`): 201 job payload; ValueError→400; upstream→502.

| Area | Source | Component tests |
| --- | --- | --- |
| Create-job route | `src/ui/api/api_inbox.py` | **`TestAst1049InboxCreateJobApi`** |

**Broken / obsolete:** none — additive route.

**Integration:** none.

### AST-1061 · AST-1058

**Parent:** [AST-1058 — Qualify Meteorite](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite). **Publish:** `origin/sub/AST-1058/AST-1061-gazer-email-meteorite-jobs-playwright-dedupe`.

Create-job JSON includes `created`/`skipped`/`mode`; **201** when any created, **200** when only skips.

| Area | Source | Component tests |
| --- | --- | --- |
| Multi-result create-job | `src/ui/api/api_inbox.py` | revised **`TestAst1049InboxCreateJobApi`** (+ all-skipped 200) |

**Broken / obsolete:** single-job-only payload assumptions (revised).

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py::TestAst1049InboxCreateJobApi \
  -q
```

### AST-1141 · AST-1129

**Parent:** [AST-1129 — Manage Email — select inbox messages and Land Meteorite](https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite). **Publish:** `origin/sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids`. **Blocked by:** AST-1140.

`POST /api/admin/inbox/land-meteorite` (`@require_admin`, `ui_llm_debug`): non-empty stripped `message_ids` → `asyncio.run(run_gaze_email_selected_ids(...))` → **200** pass-through (`results` + totals); missing/non-list/empty → **400**; ValueError → **400**; upstream → **502**; never calls `create_meteorite_job_from_inbox_message`. Core entrypoint: **`docs/test-bible/core/gaze_email.md`** (**AST-1140**). React consumer: **`docs/test-bible/frontend/pages.md`** (**AST-1142**).

| Area | Source | Component tests |
| --- | --- | --- |
| Land Meteorite route + auth + empty reject + Create ban | `src/ui/api/api_inbox.py` | **`TestAst1141InboxLandMeteoriteApi`** |

**Broken / obsolete:** none — additive route; create-job remains until AST-1142.

**Integration:** none — no existing scenario asserts Land Meteorite HTTP; do not invent new coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py::TestAst1141InboxLandMeteoriteApi \
  -q
```


### AST-1537 · AST-1533

**Parent:** [AST-1533 — Manage Email gives HTML for the body of the message, not for the header, and it must include both.](https://linear.app/astralcareermatch/issue/AST-1533/manage-email-gives-html-for-the-body-of-the-message-not-for-the-header). **Publish:** `origin/sub/AST-1533/AST-1537-email-header-body-html-land-qualify`.

`GET /api/admin/inbox/messages/<id>` returns `get_message_with_assembled_html` (includes `assembled_html` + raw fields). Primary map: **`docs/test-bible/core/inbox.md`** (**AST-1537**). React render/copy = **AST-1538**.

| Area | Source | Component tests |
| --- | --- | --- |
| Get → assembled payload | `src/ui/api/api_inbox.py` | revised **`TestAst1033InboxApi`** (`get_message_with_assembled_html` mocks) |

**Broken / obsolete:** get mocks of `get_message_html` — product no longer imports that name in `api_inbox`.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py::TestAst1033InboxApi \
  -q
```

### AST-1558 · AST-1555

**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation). **Publish:** `origin/sub/AST-1555/AST-1558-inbox-candidate-verbs-manage-email-filter`.

`GET /messages` All vs `candidate_id` → aliases → `fetch_candidate_email`; get uses `get_message_with_assembled_html`; `POST /land-meteorite` requires `candidate_id` and calls `stage_meteorite`; create-job route retired (404). Core verbs: **`docs/test-bible/core/inbox.md`** § AST-1558. React: **`docs/test-bible/frontend/pages.md`** § AST-1558.

| Area | Source | Component tests |
| --- | --- | --- |
| All list + candidate_id filter + assembled get | `src/ui/api/api_inbox.py` | revised **`TestAst1033InboxApi`** (+ **`test_list_with_candidate_id`**) |
| create-job retired | same | **`TestAst1049InboxCreateJobApiRetired`** |
| Land requires candidate_id → stage_meteorite | same | **`TestAst1558InboxLandMeteoriteApi`** |

**Broken / obsolete:** **`TestAst1049InboxCreateJobApi`** (route gone); **`TestAst1141InboxLandMeteoriteApi`** (`run_meteorite_email_selected_ids` / no `candidate_id`) — replaced by AST-1558 classes.

**Integration:** none — do not invent.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_inbox.py \
  -q
```
