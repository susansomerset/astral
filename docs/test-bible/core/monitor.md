# Monitor

**Test module:** `tests/component/core/test_monitor.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/monitor.py` | `tests/component/core/test_monitor.py` | yes |

---

### AST-667 · AST-660

**Parent:** [AST-660 — Include ASTRAL_DEPLOY_ENV in email alert header](https://linear.app/astralcareermatch/issue/AST-660/include-astral-deploy-env-in-email-alert-header). **Publish:** `origin/sub/AST-660/AST-667-deploy-env-candidate-in-auto-alert-subject`.

AUTO error alert subject replaces hardcoded `[Astral]` with `[{deploy_label}]` or `[{deploy_label}/{last_name}]` from `get_deploy_label()` (`ASTRAL_DEPLOY_ENV` verbatim or `Astral` fallback) and dispatch task `candidate_id` → `candidate_data.profile.last`. Email body, recipient, and AUTO/`total_errors > 0` trigger unchanged (AST-344).

| Area | Source | Component tests |
| --- | --- | --- |
| Deploy label helper | `src/utils/deploy_status.py` | `tests/component/utils/test_deploy_status.py` (**`TestGetDeployLabel`**) |
| Subject prefix + last name | `src/core/monitor.py` | `tests/component/core/test_monitor.py` (**`TestAutoRunErrorSubjectPrefix`**) |
| Dispatcher passes `candidate_id` | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py` (**`TestDispatchOne::test_auto_run_error_on_auto_failures`**) |

**AST-667** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_monitor.py \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures \
  tests/component/utils/test_deploy_status.py::TestGetDeployLabel
```

---

### AST-1867 · AST-1870

**Parent:** [AST-1860](https://linear.app/astralcareermatch/issue/AST-1860) (orphaned-bug mini-parent). Product: **AST-1867** (`144b8850`, not yet on ftr); test/bible delivery on gap sibling **AST-1870**. New `provider_balance_outage(task_key, batch_id, accumulated, outage, candidate_id="")`: subject `"{prefix} {provider} insufficient balance — {task_key} stopped | {batch_id}"` (provider from `get_active_llm_provider()`); short body (provider, refusal, task/batch, counts, `Held (state unchanged): N` only when `held > 0`, resume line) — **no** batch log dump; never raises. AUTO error alert (`auto_run_error`) unchanged. Nodes patch `get_deploy_label` / `_resolve_candidate_last_name` directly to stay clear of the pre-existing `TestAutoRunErrorSubjectPrefix` drift.

| Area | Source | Component tests |
| --- | --- | --- |
| Exact subject + body lines, `to` = support_email, `list_log_entries` not called | `provider_balance_outage` | **`tests/component/core/test_monitor.py::TestAst1867ProviderBalanceOutage::test_subject_names_provider_and_body_is_short`** |
| `held == 0` → no `Held` line | same | **`…::test_held_line_omitted_when_zero`** |
| `send_email` False → logged, no raise | same | **`…::test_logs_when_send_email_returns_false`** |
| Unexpected exception swallowed, no send | same | **`…::test_swallows_unexpected_errors`** |

Dispatcher routing (outage alert vs `auto_run_error`): **`docs/test-bible/core/dispatcher.md`** § AST-1867 · AST-1870 (manifest there covers these nodes + `TestAutoRunError`).

**Bible shasum (record after publish):** `git show origin/sub/AST-1860/AST-1870-provider-balance-outage-tests:docs/test-bible/core/monitor.md | shasum`

### AST-1880 · AST-1851 (pointer)

`provider_balance_outage` labels the alert with `get_llm_server(task_llm_server_id(task_key))["label"]`, the refused task's own server, not a global setting. `TestAst1867ProviderBalanceOutage` stubs `task_llm_server_id`, so the expected subject and body read `DeepSeek`. New `test_provider_label_resolved_from_refused_task` checks the task key reaches the resolver and the label is `OpenRouter`. The swallow test raises from the resolver. Manifest: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1880.
