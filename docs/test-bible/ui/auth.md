# Auth

**Test module:** `tests/component/ui/test_auth.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/auth.py` | `tests/component/ui/test_auth.py` | yes |

Helpers: **`docs/test-bible/utils/auth.md`**. Public signal route: **`docs/test-bible/ui/api/api_system.md`**.

### AST-1440 · AST-1438

**Parent:** [AST-1438 — Disable authentication on localhost](https://linear.app/astralcareermatch/issue/AST-1438/disable-authentication-on-localhost). **Publish:** `origin/sub/AST-1438/AST-1440-local-api-auth-passthrough`.

When `ASTRAL_DEPLOY_ENV=local`, `@require_auth` skips Stytch and sets `g.user` from `AUTH_CONFIG["local_operator"]` (always-admin). Non-local (staging / production / unset) stays fail-closed 401. Public `GET /api/auth_passthrough` returns only `{"local_auth_passthrough": <bool>}`. SPA Login / RequireAuth / session extend = sibling **AST-1441**.

UI harness autouse clears `ASTRAL_DEPLOY_ENV` so existing 401 cases (`TestRequireAuth`, `TestSystemAuthRoutes::test_me_requires_bearer`) do not flip to 200 on a local host env. Integration autouse **`setenv("ASTRAL_DEPLOY_ENV", "staging")`** — not `delenv` — so `config.py` `load_dotenv()` cannot restore `local` from the epic worktree `.env` after the fixture runs (`[qa-handoff]` AST-1440).

| Area | Source | Component tests |
| --- | --- | --- |
| Decorator local skip + non-local 401 | `src/ui/auth.py` | **`TestAst1440LocalAuthPassthrough`** |
| Isolation of existing 401 | `tests/component/ui/conftest.py` | autouse `_ui_fail_closed_deploy_env` |
| Operator helpers + AUTH_CONFIG literals | `src/utils/auth.py` / `src/utils/config.py` | **`TestAst1440LocalOperator`** |
| Public signal + `/api/me` `/api/nav_config` | `src/ui/api/api_system.py` | **`TestAst1440AuthPassthroughRoute`** |
| Integration 401 isolation | `tests/integration/conftest.py` | autouse `_integration_fail_closed_deploy_env` (`staging`, dotenv-proof) |

**Broken / obsolete:** `TestRequireAuth` 401 cases (and other UI 401-without-Bearer tests) if process env is `ASTRAL_DEPLOY_ENV=local` — isolated via autouse delenv, not rewritten. Integration `test_unauthenticated_nav_config_returns_401` — **`delenv` was insufficient** (dotenv refill); revised to `setenv staging`. No new integration scenario.

**Integration:** existing nav 401 still valid when deploy env is not `local`. Harness sets `staging` so `.env` `local` cannot win. Map: **`docs/test-bible/integration/README.md`**.

## QA test manifest

1. Decorator local passthrough + staging/production 401: `tests/component/ui/test_auth.py::TestAst1440LocalAuthPassthrough`
2. Existing 401 still fail-closed (harness isolation): `tests/component/ui/test_auth.py::TestRequireAuth::test_missing_bearer_returns_401`
3. Operator helpers + AUTH_CONFIG literals: `tests/component/utils/test_auth.py::TestAst1440LocalOperator`
4. Public `/api/auth_passthrough` + local `/api/me` `/api/nav_config`: `tests/component/ui/api/test_api_system.py::TestAst1440AuthPassthroughRoute`
5. Non-local `/api/me` still 401: `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_me_requires_bearer`
6. Integration unauthenticated nav 401 (existing, env-isolated): `tests/integration/scenarios/test_candidate_nav_api.py::test_unauthenticated_nav_config_returns_401`

**AST-1440** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_auth.py::TestAst1440LocalAuthPassthrough \
  tests/component/ui/test_auth.py::TestRequireAuth::test_missing_bearer_returns_401 \
  tests/component/utils/test_auth.py::TestAst1440LocalOperator \
  tests/component/ui/api/test_api_system.py::TestAst1440AuthPassthroughRoute \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_me_requires_bearer \
  -q
```

```bash
./scripts/testing/run_integration_tests.sh \
  tests/integration/scenarios/test_candidate_nav_api.py::test_unauthenticated_nav_config_returns_401 \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.
