# Stytch

**Test module:** `tests/component/external/test_stytch.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/stytch.py` | `tests/component/external/test_stytch.py` | no |

---

### AST-831 · AST-829

**AST-829 (parent):** Production Google OAuth — Flask Bearer validation logs **`session_not_found`** when backend **`STYTCH_*`** env points at a different Stytch project than frontend **`VITE_STYTCH_PUBLIC_TOKEN`**. **AST-831** forces remote JWT validation via **`max_token_age_seconds=0`**, startup **`log_stytch_project_env()`**, and ops hint on **`session_not_found`** in **`validate_bearer_token`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Remote JWT validation | `src/external/stytch.py` | `tests/component/external/test_stytch.py::TestAuthenticateSessionJwt::test_happy_path_maps_user_id_email_name` (asserts **`max_token_age_seconds=0`**) |
| Startup project env log | `src/external/stytch.py`, `src/core/auth_bootstrap.py` | `tests/component/external/test_stytch.py::TestLogStytchProjectEnv` |
| Ops hint on session_not_found | `src/utils/auth.py` | `tests/component/utils/test_auth.py::TestValidateBearerToken::test_session_not_found_logs_ops_hint` |

**AST-831** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_stytch.py::TestAuthenticateSessionJwt::test_happy_path_maps_user_id_email_name \
  tests/component/external/test_stytch.py::TestLogStytchProjectEnv \
  tests/component/utils/test_auth.py::TestValidateBearerToken::test_session_not_found_logs_ops_hint
```

**Regression guard:** full **`TestAuthenticateSessionJwt`** + **`TestValidateBearerToken`** classes green — AST-610 behavior unchanged aside from revised kwarg and new log lines.
