# Deploy Status

**Test module:** `tests/component/utils/test_deploy_status.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/deploy_status.py` | `tests/component/utils/test_deploy_status.py` | no |

---

### AST-667 · AST-646

**`get_deploy_label()`** (AST-667): stripped non-empty `ASTRAL_DEPLOY_ENV` verbatim or `"Astral"` when unset/whitespace — used by AUTO alert subject prefix in monitor (AST-660 child).

| Behavior | Tests |
| --- | --- |
| Env set → raw label | `TestGetDeployLabel::test_returns_env_when_set` |
| Unset / whitespace → `Astral` | `TestGetDeployLabel::test_returns_astral_when_unset`, `test_returns_astral_when_whitespace_only` |
