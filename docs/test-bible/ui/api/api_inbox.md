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
