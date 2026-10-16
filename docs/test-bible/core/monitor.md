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
| Exact subject + body lines, `to` = admin (was support_email until **AST-2214**), `list_log_entries` not called | `provider_balance_outage` | **`tests/component/core/test_monitor.py::TestAst1867ProviderBalanceOutage::test_subject_names_provider_and_body_is_short`** |
| `held == 0` → no `Held` line | same | **`…::test_held_line_omitted_when_zero`** |
| `send_email` False → logged, no raise | same | **`…::test_logs_when_send_email_returns_false`** |
| Unexpected exception swallowed, no send | same | **`…::test_swallows_unexpected_errors`** |

Dispatcher routing (outage alert vs `auto_run_error`): **`docs/test-bible/core/dispatcher.md`** § AST-1867 · AST-1870 (manifest there covers these nodes + `TestAutoRunError`).

**Bible shasum (record after publish):** `git show origin/sub/AST-1860/AST-1870-provider-balance-outage-tests:docs/test-bible/core/monitor.md | shasum`

### AST-1880 · AST-1851 (pointer)

`provider_balance_outage` labels the alert with `get_llm_server(task_llm_server_id(task_key))["label"]`, the refused task's own server, not a global setting. `TestAst1867ProviderBalanceOutage` stubs `task_llm_server_id`, so the expected subject and body read `DeepSeek`. New `test_provider_label_resolved_from_refused_task` checks the task key reaches the resolver and the label is `OpenRouter`. The swallow test raises from the resolver. Manifest: [`../ui/api/api_admin.md`](../ui/api/api_admin.md) § AST-1880.

### AST-2214 · AST-2207

**Parent:** [AST-2207 — Update error reporting from production](https://linear.app/astralcareermatch/issue/AST-2207). **Publish:** `origin/sub/AST-2207/AST-2214-alert-header-log-attachment`. Depends on **AST-2213** `send_email(..., attachments=...)` ([`../external/gmail.md`](../external/gmail.md) § AST-2213).

`auto_run_error` body = six-line metadata header (`Deploy:` / `Candidate:` / `Task:` / `Batch:` / `Status:` / one-line counts, `-` for missing values) + a fenced WARNING/ERROR-only block (or `(no WARNING or ERROR entries for this batch)`, no fence). The full log at every level, oldest first, goes as `{"<batch_id>.txt": …}` from one `list_log_entries` fetch. `_format_log_body` is replaced by `_format_log_line` / `_format_full_log` / `_format_warning_error_block` + `_format_alert_header`. `provider_balance_outage` sends to `", ".join(sorted(AUTH_CONFIG["admin_emails"]))`, no attachment, no log fetch; with no admins it logs one WARNING and skips the send. Subject line unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| Header before fence, WARNING/ERROR-only body, full-log attachment (AC 1/2/4) | `auto_run_error` | **`TestAutoRunError::test_sends_header_filtered_body_and_full_log_attachment`** |
| Empty-filter notice, no fence (AC 3) | `auto_run_error` / `_format_warning_error_block` | **`TestAst2214AlertShape::test_info_only_rows_give_notice_not_empty_fence`** |
| No rows → placeholder attachment still sent | `_format_full_log` | **`TestAst2214AlertShape::test_no_rows_still_attaches_placeholder`** |
| Header `-` defaults; bare candidate id | `_format_alert_header` | **`TestAst2214AlertShape::test_header_dashes_for_missing_values`**, **`…::test_header_bare_candidate_id_without_last_name`** |
| Fence outruns inner backticks (was `TestFormatLogBody`) | `_format_warning_error_block` | **`TestAst2214AlertShape::test_fence_outruns_backticks_inside_the_logs`** |
| Admin recipient, no attachment, no log fetch (AC 5) | `provider_balance_outage` | revised **`TestAst1867ProviderBalanceOutage::test_subject_names_provider_and_body_is_short`** |
| Empty admin → one WARNING, no send (AC 5) | same | **`TestAst1867ProviderBalanceOutage::test_no_admin_configured_warns_once_and_skips_send`** |
| Multi-admin sorted join | same | **`TestAst1867ProviderBalanceOutage::test_multiple_admins_joined_in_sorted_order`** |

**Broken / obsolete:**
- `TestAutoRunError::test_sends_alert_with_log_body` (asserted a body that was only a fence) is replaced by the header/attachment test above.
- `TestFormatLogBody` (3 tests on the removed `_format_log_body`) is retired; its fence case moved to `TestAst2214AlertShape`.
- `TestAst1867ProviderBalanceOutage._stub` now patches `AUTH_CONFIG["admin_emails"]`. Without it, every send-path test early-returned on the empty test-env admin set.
- `TestAutoRunErrorSubjectPrefix` `get_candidate` stubs nested the last name under `candidate_data.profile`. **AST-1014** moved it to the top-level `last` column, so 3 tests were red on `ftr` before this ticket. The stubs now return `{"last": …}`.

**Integration:** none. No scenario exercises monitor; dispatcher tests mock `auto_run_error` / `provider_balance_outage` whole.

**AC 6** (live forced AUTO error on the test deploy) is parent UAT, not pytest.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_monitor.py \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_auto_run_error_on_auto_failures \
  tests/component/core/test_dispatcher.py::TestAst1867ProviderBalanceOutage \
  -q
```

**Pass criterion:** pytest green on narrowed args; `src/core/monitor.py` remains **LOCKED_AT_100** branch coverage.
