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
