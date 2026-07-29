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
