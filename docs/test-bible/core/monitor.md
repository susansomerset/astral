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
