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
