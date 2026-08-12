# Gmail

**Test module:** `tests/component/external/test_gmail.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/gmail.py` | `tests/component/external/test_gmail.py` | yes |

---

### AST-1032 · AST-1031

**Parent:** [AST-1031 — Receive email on gmail account for astral](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral). **Publish:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read`.

Dual-scope OAuth (`gmail.send` + `gmail.readonly`) on shared credentials; `list_inbox_messages` / `get_message_html` raise on API failure; `send_email` keeps bool-never-raise; all three entry points gate via `require_controlled_external_io`.

| Area | Source | Component tests |
| --- | --- | --- |
| Dual-scope send + bool contract | `src/external/gmail.py` | `tests/component/external/test_gmail.py` (**`TestSendEmail`**) |
| Inbox list pagination + metadata | `src/external/gmail.py` | `tests/component/external/test_gmail.py` (**`TestListInboxMessages`**) |
| Message HTML extract (no plain→HTML invent) | `src/external/gmail.py` | `tests/component/external/test_gmail.py` (**`TestGetMessageHtml`**) |
| Helper edge branches | `src/external/gmail.py` | `tests/component/external/test_gmail.py` (**`TestGmailHelpers`**) |
| Controlled external I/O gate | `src/external/gmail.py` | `tests/component/external/test_gmail.py` (**`TestControlledExternalIo`**) |
| Core thin orchestrator | `src/core/inbox.py` | `tests/component/core/test_inbox.py` (see **`docs/test-bible/core/inbox.md`**) |

**AST-1032** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_gmail.py \
  tests/component/core/test_inbox.py
```

**Pass criterion:** pytest green on narrowed args; `src/external/gmail.py` remains **LOCKED_AT_100** branch coverage.


### AST-1049 · AST-1044

**Parent:** [AST-1044 — Bind email to candidate](https://linear.app/astralcareermatch/issue/AST-1044/bind-email-to-candidate). **Publish:** `origin/sub/AST-1044/AST-1049-strip-extract-create-job-matched-email-meteorite`.

`get_message_html` / `GmailMessageHtml` include `subject` + `from_address` from full-message headers (empty strings when missing).

| Area | Source | Component tests |
| --- | --- | --- |
| Subject/From on HTML get | `src/external/gmail.py` | revised **`TestGetMessageHtml`**; **`test_includes_subject_and_from_headers`** |

**Broken / obsolete:** exact-equality asserts on `{id, html_body}` only — revised to include subject/from_address.

**Integration:** none.

### AST-1088 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1088-gaze-email-config-null-candidate-dispatch-shell-gmail-archive-trash`.

Sole OAuth scope `gmail.modify` (replaces send+readonly pair). Public `archive_message` (remove `INBOX`) + `trash_message` (Trash, not permanent delete); both gate via `require_controlled_external_io` and raise on API failure. Config / provision: **`docs/test-bible/utils/config.md`** · **`docs/test-bible/core/dispatcher.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Modify-only scopes | `src/external/gmail.py` | revised **`TestSendEmail::test_send_email_uses_modify_gmail_scope`** (was dual-scope) |
| Archive + trash + raise | `src/external/gmail.py` | **`TestAst1088ArchiveTrash`** |
| Controlled I/O gate | `src/external/gmail.py` | revised **`TestControlledExternalIo`** (archive/trash blocked) |

**Broken / obsolete:** **`test_send_email_uses_dual_gmail_scopes`** — dual-scope asserts superseded by sole `gmail.modify`.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_gmail.py \
  -q
```

**Pass criterion:** pytest green on narrowed args; `src/external/gmail.py` remains **LOCKED_AT_100** branch coverage.

### AST-1090 · AST-1087

**Parent:** [AST-1087 — Add gaze_email as a dispatch task](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task). **Publish:** `origin/sub/AST-1087/AST-1090-gaze-email-runner-bind-route-scrape-dedupe-create-mailbox`.

`GmailInboxMessage.internal_date_ms` from Gmail `internalDate` (0 if missing/unparseable) for unbound retention age. Runner primary: **`docs/test-bible/core/gaze_email.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| internalDate parse + list row field | `src/external/gmail.py` | **`TestAst1090InternalDateMs`**; revised **`TestListInboxMessages`** exact dicts |

**Broken / obsolete:** list/metadata exact-equality asserts missing `internal_date_ms` — revised.

**Integration:** none.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_gmail.py \
  -q
```

### AST-1312 · AST-1308

**Parent:** [AST-1308 — Email bind where email is in the To: field (alone)](https://linear.app/astralcareermatch/issue/AST-1308/email-bind-where-email-is-in-the-to-field-alone). **Publish:** `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`.

Raw `to_address` on `list_inbox_messages` / `get_message_html` (empty string when the To header is missing). List metadata get must request `"To"`. No parse, no inbox-address filter, no From-then-To bind (AST-1313).

| Area | Source | Component tests |
| --- | --- | --- |
| Raw To on list + metadataHeaders | `src/external/gmail.py` | **`TestAst1312ToAddress::test_list_requests_to_and_copies_raw_header`**; revised **`TestListInboxMessages`** exact dicts |
| Raw To on get (or empty) | `src/external/gmail.py` | **`TestAst1312ToAddress::test_get_copies_raw_to_or_empty`**; revised **`TestGetMessageHtml`** (`test_includes_subject_and_from_headers` + exact dicts) |
| From-only bind unchanged | `src/core/inbox.py` | existing **`tests/component/core/test_inbox.py::TestAst1047InboxFromBind`** |

**Broken / obsolete:** exact-equality asserts on list/get dicts missing `to_address` — revised.

**Integration:** none — no existing inbox/gmail scenario to revise; do not invent coverage.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_gmail.py \
  tests/component/core/test_inbox.py::TestAst1047InboxFromBind \
  -q
```

**Pass criterion:** pytest green on narrowed args; `src/external/gmail.py` remains **LOCKED_AT_100** branch coverage.

