# Local API auth passthrough

**Linear:** [AST-1440](https://linear.app/astralcareermatch/issue/AST-1440/local-api-auth-passthrough-disable-authentication-on-localhost)
**Parent:** [AST-1438](https://linear.app/astralcareermatch/issue/AST-1438/disable-authentication-on-localhost) — Disable authentication on localhost
**Publish ref:** `sub/AST-1438/AST-1440-local-api-auth-passthrough`

When `ASTRAL_DEPLOY_ENV` is `local` (same helper as the nav footer / local debug), Flask `@require_auth` / `@require_admin` skip Stytch JWT validation and set `g.user` to a synthetic always-admin operator from `AUTH_CONFIG`. A public non-secret `GET /api/auth_passthrough` tells the SPA (sibling AST-1441) that local auth is off before login. Staging, production, `test`, unset, and any other deploy env stay fail-closed 401. Protected routes keep their decorators.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/patterns/auth/pattern.auth.local-deploy-passthrough.md` | New catalog entry, `status: proposed`, `proposed_in: AST-1438` | canon |
| `docs/ASTRAL_CODE_RULES.md` | Document local-deploy exception in §2.9; add `AUTH_CONFIG` to §2.1 catalog | docs |
| `src/utils/config.py` | Add `local_operator` identity literals to `AUTH_CONFIG`; header inventory | utils |
| `src/utils/auth.py` | Add `local_operator_user()` and `local_auth_passthrough_payload()` | utils |
| `src/ui/auth.py` | `@require_auth` early-return on `is_local_deploy_env()` before any token/Stytch work | ui |
| `src/ui/api/api_system.py` | Open `GET /api/auth_passthrough` returning the non-secret boolean payload | ui |
| `env.example` | Document that `ASTRAL_DEPLOY_ENV=local` skips Stytch on protected APIs | docs |

**Out of this ticket (do not touch):** React Login / `RequireAuth` / `AuthContext` / session extend (`src/ui/frontend/**`) — sibling **AST-1441**. `@require_ip`, `ASTRAL_ALLOWED_IPS`, `src/external/stytch.py`, `src/core/auth_bootstrap.py`, Stytch Dashboard, session duration literals, `/api/auth_session_policy` field set, Surfer / extension auth. Do not remove `@require_auth` / `@require_admin` from any route. Do not edit `tests/` or `docs/test-bible/**`.

## Stage 1: Pattern catalog + Code Rules auth exception

**Done when:** `canon/patterns/auth/pattern.auth.local-deploy-passthrough.md` exists with SCHEMA-valid frontmatter `status: proposed`; `docs/ASTRAL_CODE_RULES.md` §2.9 describes Stytch decorator internals plus the local-deploy exception; §2.1 lists `AUTH_CONFIG`. No product code yet.

1. Create directory `canon/patterns/auth/` if it does not exist. Create file `canon/patterns/auth/pattern.auth.local-deploy-passthrough.md` with **exactly** this content (YAML frontmatter + body, SCHEMA section order):

```markdown
---
id: pattern.auth.local-deploy-passthrough
name: Local deploy auth passthrough
status: proposed
proposed_in: AST-1438
approved_by: null
approved_at: null
canonical_refs:
  - path: src/ui/auth.py
    symbol: require_auth
  - path: src/utils/auth.py
    symbol: local_operator_user
  - path: src/utils/config.py
    symbol: AUTH_CONFIG
  - path: src/ui/api/api_system.py
    symbol: auth_passthrough
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.9"
related_statutes:
  - astral.idioms.require-auth-on-protected-endpoints
  - astral.config.config-source-of-truth
  - astral.config.secrets-and-env-specific-from-environ
  - astral.standards.no-hardcoded-sets
  - astral.layers.import-direction
supersedes: null
superseded_by: null
---

# Problem

Local development still validates Stytch session JWTs on every protected API call. A missing or wrong-project session logs `session_not_found` and 401s the operator on their own machine even though `ASTRAL_DEPLOY_ENV=local` already names that deploy.

# Solution shape

Keep `@require_auth` / `@require_admin` on every previously protected route. When `is_local_deploy_env()` is true, decorator internals skip Bearer/cookie extraction and Stytch validation, set `g.user` to the synthetic always-admin operator from `AUTH_CONFIG["local_operator"]`, and do not log `Bearer token validation failed` or `Stytch session_not_found`. Identity literals live in `AUTH_CONFIG`, not inline in the decorator. Gate is `ASTRAL_DEPLOY_ENV` via `is_local_deploy_env()` — not browser hostname. Expose the same gate as a public non-secret `GET /api/auth_passthrough` boolean so the SPA can read it before login. Non-local deploys (including unset) stay fail-closed 401. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Deploy env is not `local` (staging, production, test, unset, or any other label).
- Stripping `@require_auth` / `@require_admin` from routes, or treating hostname `localhost` as the gate.
- Surfer / extension auth, `@require_ip`, or Stytch Dashboard / live-project JWT / session-duration changes.
- A second local-user picker or non-admin impersonation.
- Depending on this pattern id for implementation until `status: approved` (AUTHORING).
```

2. Do **not** set `status: approved`. Archie approves later. Do **not** edit `canon/patterns/README.md` or `canon/patterns/HARVEST.md`.

3. In `docs/ASTRAL_CODE_RULES.md` §2.1 **Config blocks** list (the bullet list under `**Config blocks:**`), add this bullet immediately after the existing `RAILWAY_CONFIG` bullet:

```
- **AUTH_CONFIG**: Authentication. Stytch credentials and admin user-id/email sets from env; non-secret session duration / activity-extension literals; `local_operator` identity literals for the local-deploy passthrough (§2.9).
```

4. Replace the entire `### 2.9 Authentication Decorator` section (from the `### 2.9` heading through the React-side paragraph, stopping before `## 3. Codebase Structure`) with:

```
### 2.9 Authentication Decorator

**Statute:** `astral.idioms.require-auth-on-protected-endpoints`
**Pattern:** `pattern.auth.local-deploy-passthrough` (proposed AST-1438)

UI API endpoints use `@require_auth` to enforce authentication. The decorator reads the Stytch session JWT from `Authorization: Bearer` or the `stytch_session_jwt` cookie, validates it via the registered authenticator (`src/utils/auth.py` → `src/external/stytch.py`), and sets `g.user` to `{user_id, name, is_admin}`. Endpoints without the decorator are open (e.g. health, `GET /api/auth_session_policy`, `GET /api/auth_passthrough`).

**Pattern:**

- `@require_auth` = protected. Returns 401 if credentials are missing or invalid — **except** the local-deploy passthrough below.
- `@require_admin` = `@require_auth` plus `g.user["is_admin"]`; 403 when the authenticated user is not admin. Local passthrough supplies an always-admin identity; it does not strip this decorator.
- No decorator = open. No auth check.
- Authenticated user available via `flask.g.user` inside the endpoint function.

**Local-deploy passthrough:** When `is_local_deploy_env()` is true (`ASTRAL_DEPLOY_ENV` stripped, case-insensitive `"local"`), `@require_auth` does not read or validate a Stytch token, does not call the authenticator, and sets `g.user` from `AUTH_CONFIG["local_operator"]` with `is_admin: True`. That path must not log `Bearer token validation failed` or `Stytch session_not_found`. Browser hostname is not the gate. When deploy env is anything other than `local` (including unset), missing/invalid Bearer still 401.

**Public signal:** `GET /api/auth_passthrough` is open on purpose and returns only `{"local_auth_passthrough": <bool>}` from the same `is_local_deploy_env()` gate. It must not include secrets, admin lists, or Stytch credentials. SPA consumption of that signal is a separate ticket.

**React side:** Authenticated API calls go through the shared `api()` client (`src/ui/frontend/src/lib/api.ts`) that injects the `Authorization` header when a Stytch session JWT exists.
```

⚠️ **Decision:** Pattern lands `proposed` (parent AST-1438 proposed it; Archie approves). Product code in later stages implements the behavior; it does not import or look up the pattern id at runtime (AUTHORING: implementation must not depend on the id until approved).

⚠️ **Decision:** Rewrite the stale §2.9 Auth0/stub sentences. They contradict live Stytch wiring and would make the local exception unreadable. Do not expand §2.9 into SPA Login / session-extend behavior (AST-1441).

## Stage 2: AUTH_CONFIG local operator + utils helpers

**Done when:** `AUTH_CONFIG["local_operator"]` has `user_id` / `name` literals; `local_operator_user()` returns `{user_id, name, is_admin: True}` from those literals; `local_auth_passthrough_payload()` returns `{"local_auth_passthrough": is_local_deploy_env()}` and never includes secrets. `python3 -m py_compile src/utils/config.py src/utils/auth.py` passes.

1. In `src/utils/config.py`, update the module-header inventory line for `AUTH_CONFIG` (currently Stytch credentials, admin lists, session duration) so it also names `local_operator` identity literals.

2. In the `AUTH_CONFIG` dict, after `"activity_extension_interval_minutes": 10,`, add exactly:

```python
    # Synthetic operator for local-deploy API passthrough. Not a Stytch user.
    "local_operator": {
        "user_id": "local-operator",
        "name": "Local Operator",
    },
```

These are plain literals (not `os.environ`). Do not add email. Do not put Susan's identity here. Do not add a parallel boolean flag in `AUTH_CONFIG` — the gate is `ASTRAL_DEPLOY_ENV` via `is_local_deploy_env()`.

3. Keep existing `AUTH_CONFIG` keys and `_parse_csv_env` / `os.environ.get` behavior for admin lists and Stytch credentials unchanged. Do not change `get_auth_session_policy()`.

4. In `src/utils/auth.py`:
   - Update the module docstring to mention the local-deploy operator helper (do not put a ticket id in a function **name**).
   - Add `from src.utils.deploy_status import is_local_deploy_env` with the existing `src.utils.config` import (intra-utils import is allowed).
   - Add `"local_operator_user"` and `"local_auth_passthrough_payload"` to `__all__`.
   - After `normalize_user` (still in the public-function section, before `validate_bearer_token`), add:

```python
def local_operator_user() -> dict:
    """Synthetic always-admin g.user for local-deploy passthrough. Not a Stytch user."""
    op = AUTH_CONFIG["local_operator"]
    return {
        "user_id": str(op["user_id"]),
        "name": str(op["name"]),
        "is_admin": True,
    }


def local_auth_passthrough_payload() -> dict:
    """Public non-secret SPA signal. Never include secrets or admin lists."""
    return {"local_auth_passthrough": is_local_deploy_env()}
```

5. Do **not** route `local_operator_user()` through `normalize_user` / `is_admin()`. Always-admin must not depend on `ASTRAL_ADMIN_USER_IDS` / `ASTRAL_ADMIN_EMAILS` being set in local `.env`.

6. Do **not** change `validate_bearer_token`, `register_token_authenticator`, or the `logging.getLogger` warning lines. Those warnings stay on the Stytch-validation failure path only.

⚠️ **Decision:** `user_id` `local-operator` / name `Local Operator` — stable, non-secret, not a real Stytch user and not an inline admin-email list. `is_admin: True` is an invariant of the passthrough, not an admin-list lookup.

⚠️ **Decision:** Payload helper lives in `src/utils/auth.py` (auth contract) and reads `is_local_deploy_env()` (existing env gate). Do not duplicate the env parse in `auth.py` or `config.py`.

## Stage 3: Decorator passthrough + public signal

**Done when:** With `ASTRAL_DEPLOY_ENV=local`, `GET /api/me` and `GET /api/nav_config` return 200 with no Bearer (and `g.user.is_admin` is true); those requests do not call `validate_bearer_token` / Stytch. Unauthenticated `GET /api/auth_passthrough` returns `{"local_auth_passthrough": true}`. With deploy env `staging`, `production`, or unset: missing Bearer still 401 on `/api/me`; `GET /api/auth_passthrough` returns `{"local_auth_passthrough": false}`. Every previously protected route still has `@require_auth` or `@require_admin`. `python3 -m py_compile src/ui/auth.py src/ui/api/api_system.py` passes.

1. In `src/ui/auth.py`:
   - Change `from src.utils.auth import validate_bearer_token` to `from src.utils.auth import local_operator_user, validate_bearer_token`.
   - Add `from src.utils.deploy_status import is_local_deploy_env`.
   - Update the module docstring so `@require_auth` is described as Stytch JWT validation **unless** local-deploy passthrough applies.
   - Replace the body of `require_auth`'s `decorated` with this order — local check **first**, before `_session_jwt_from_request` and `validate_bearer_token`:

```python
        if is_local_deploy_env():
            g.user = local_operator_user()
            return f(*args, **kwargs)
        token = _session_jwt_from_request()
        if not token:
            return jsonify({"error": "Missing or invalid session credentials"}), 401
        user = validate_bearer_token(token)
        if user is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.user = user
        return f(*args, **kwargs)
```

   - Do not log on the local branch. Do not read Bearer or the Stytch cookie on the local branch (a present token is ignored, not validated).
   - Do not change `require_admin`, `require_ip`, `_session_jwt_from_request`, or IP helpers. `require_admin` keeps wrapping `@require_auth`; local identity is already admin so admin routes succeed.

2. In `src/ui/api/api_system.py`:
   - Add `local_auth_passthrough_payload` to a new import: `from src.utils.auth import local_auth_passthrough_payload` (ui → utils is allowed). Do not import `src.external` or `src.data`.
   - Under `# --- Open endpoints (no auth) ---`, immediately **after** the existing `auth_session_policy` route and still **before** `# --- Authenticated endpoints ---`, add:

```python
@system_bp.route("/auth_passthrough")
def auth_passthrough():
    """Public non-secret local-auth signal for SPA. Public on purpose."""
    return jsonify(local_auth_passthrough_payload())
```

   - Do **not** decorate this route with `@require_auth` or `@require_admin`.
   - Do **not** fold this boolean into `GET /api/auth_session_policy` (that payload stays the two session-policy ints; sibling AST-1441 already has a typed consumer that validates those ints).
   - Do **not** log the response body.
   - Do **not** add, remove, or move `@require_auth` / `@require_admin` on any other route in this file (or any other blueprint).

3. In `env.example`, immediately after the existing `ASTRAL_DEPLOY_ENV=local` line and its current comments, add these two comment lines (keep the assignment `ASTRAL_DEPLOY_ENV=local`):

```
# local: skip Stytch JWT validation on @require_auth / @require_admin (synthetic always-admin operator).
# Any other value (staging, production, test, unset) keeps full Stytch auth. Hostname is not the gate.
```

4. Do **not** skip `wire_stytch_token_authenticator()` at process start. Startup may still register the authenticator; per-request validation is what local skips.

⚠️ **Decision:** Dedicated open route `GET /api/auth_passthrough` rather than adding a field to `/api/auth_session_policy`. Session-policy JSON is two positive ints consumed by AST-1374; mixing a boolean would force AST-1441 to widen that type and risk breaking the existing int validation. Same exception shape as AST-1373's public policy route (`astral.idioms.require-auth-on-protected-endpoints` allows an explicitly public non-secret read).

⚠️ **Decision:** Ignore a present Bearer/cookie on local rather than validating it. Parent: protected APIs do not validate or refresh a Stytch token when deploy env is `local`. Validating a stale/wrong-project JWT would still log `session_not_found`.

### Contract for sibling AST-1441 (do not implement here)

| Field | Type | Meaning |
|-------|------|---------|
| `local_auth_passthrough` | bool | `true` only when `is_local_deploy_env()`; SPA may skip Login / Log-off / Stytch extend and treat `GET /api/me` as the local operator. `false` (staging, production, test, unset, other labels): existing Login / 401 / extend unchanged. |

SPA must fetch this with raw `fetch` (not `api()`), same as `/api/auth_session_policy` — that fetch and all React Login / `RequireAuth` / session-extend changes are **AST-1441**, not this ticket.

### Hand verify (builder, after Stage 3)

From the epic worktree with the Flask API on `:5001`:

1. `ASTRAL_DEPLOY_ENV=local`: `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5001/api/me` → `200`. Same for `/api/nav_config`. `curl -s http://127.0.0.1:5001/api/auth_passthrough` → `{"local_auth_passthrough": true}`. Response `is_admin` on `/api/me` is `true`. Server log for those requests must not contain `Bearer token validation failed` or `Stytch session_not_found`.
2. Temporarily `ASTRAL_DEPLOY_ENV=staging` (or unset) and restart: `curl` `/api/me` without Bearer → `401`. `curl` `/api/auth_passthrough` → `{"local_auth_passthrough": false}`. Restore `local` after.
3. Grep: no route that currently has `@require_auth` or `@require_admin` lost that decorator. `/health` and `/api/auth_session_policy` stay undecorated.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1440
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1438/AST-1440-local-api-auth-passthrough` @ `a0891a19fb496e7206f7a51e63c0296055d1afb6`

## Traceability
AC1→S2+S3; AC2→S3; AC3→S3; AC4→S3 (S1 authors proposed `pattern.auth.local-deploy-passthrough` + §2.9 exception). Parent AC1 SPA Login / AC3 / AC4 Login-extend → N/A — “Does not own React Login, RequireAuth, or session extend (sibling 2).”

## Notes
Files Changed layer `canon` mapped to `docs` (unrecognized layer).

No `fix-now` or `discuss` findings. Plan matches parent API passthrough, synthetic always-admin `AUTH_CONFIG["local_operator"]`, public `GET /api/auth_passthrough`, fail-closed non-`local`, decorators kept; SPA skip stays AST-1441. Reuses `is_local_deploy_env()` / `pattern.config.config-block`; `pattern.ui.admin-endpoint` honored by not stripping `@require_admin`. Pattern lands `proposed` without runtime id lookup (AUTHORING). Test isolation deferred to Betty.

context_tokens≈32000

## Betty / test-tree (do not implement)

Existing `tests/component/ui/test_auth.py::TestRequireAuth` 401 cases will 200 if the process env is `ASTRAL_DEPLOY_ENV=local` (common on this host). Betty owns isolating those tests (monkeypatch env off `local`) plus new coverage for the passthrough / public route. Engineers do not edit `tests/` or `docs/test-bible/**`.

## Review (build)

**Built @ `399e648c`** — `origin/sub/AST-1438/AST-1440-local-api-auth-passthrough`

- Stage 1: `pattern.auth.local-deploy-passthrough` proposed; Code Rules §2.9 local exception + §2.1 `AUTH_CONFIG`
- Stage 2: `AUTH_CONFIG["local_operator"]`; `local_operator_user()` / `local_auth_passthrough_payload()`
- Stage 3: `@require_auth` local early-return; open `GET /api/auth_passthrough`; `env.example`

## Radia review

[code-rubric] revision=2  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1440  
**Publish ref:** `origin/sub/AST-1438/AST-1440-local-api-auth-passthrough` @ `8f04677299acd2d66b7177b27d7133ca7c6aadfe`  
**Overall:** CLEAN  
**Internal grade:** CLEAN

## Frame diff

- **Diff paths:** `canon/patterns/auth/pattern.auth.local-deploy-passthrough.md` (A); `docs/ASTRAL_CODE_RULES.md`; `docs/features/foundation/ast-1440-local-api-auth-passthrough.md` (A); `docs/test-bible/integration/README.md`; `docs/test-bible/ui/api/api_system.md`; `docs/test-bible/ui/auth.md`; `docs/test-bible/utils/auth.md`; `env.example`; `src/ui/api/api_system.py`; `src/ui/auth.py`; `src/utils/auth.py`; `src/utils/config.py`; `tests/component/ui/api/test_api_system.py`; `tests/component/ui/conftest.py`; `tests/component/ui/test_auth.py`; `tests/component/utils/test_auth.py`; `tests/integration/conftest.py`
- **Diff layers:** `docs` (canon/docs/env.example), `ui`, `utils`; test-tree paths are Betty-owned (no product layer)
- **Diff change_types:** `add`, `modify`

## Statutes checked

Harvested active set (registry table; retired skipped). 64 ids.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | `config.py` touched; no confidence/bounds literals |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no `src/core/**` |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no `src/core/**` |
| `astral.batch.batch-id-first` | scoped | not-applicable | no `src/data/**` / `src/core/**` |
| `astral.batch.batch-id-format` | scoped | not-applicable | no `src/data/**` / `src/core/**` |
| `astral.batch.claim-process-release` | scoped | not-applicable | no `src/data/**` / `src/core/**` |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no `src/data/**` / `src/core/**` |
| `astral.config.config-source-of-truth` | scoped | conforms | `local_operator` lives in `AUTH_CONFIG`; decorator reads helpers |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | identity literals are non-secret; gate remains `ASTRAL_DEPLOY_ENV` via `is_local_deploy_env()` |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no `artifacts/**` / `scripts/spikes/**` |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | `docs/features/**` hit; added plan file is not a spike |
| `astral.dispatch.seed-auto-false` | scoped | conforms | `config.py` touched; no `seed_auto` change |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | `config.py` touched; no `run_next` change |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | single `docs/features/foundation/ast-1440-…` file |
| `astral.git.betty-no-src-or-features` | scoped | conforms | `test()` / `merge-tests` commits stay off `src/` and `docs/features/` |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test-tree only on `test()` / `merge-tests`; `code()` is product/docs |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no `src/core/**` / `src/external/**` |
| `astral.layers.import-direction` | scoped | conforms | ui→utils; utils→utils; no new ui→data/external |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no `scripts/**` |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | operator identity from `AUTH_CONFIG`; no React rule duplication |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no `src/core/**` |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no `src/core/**` |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | conforms | `@require_auth` / `@require_admin` kept; `/auth_passthrough` is an explicit public non-secret read |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | `config.py` touched; no agent JSON / bootstrap change |
| `astral.seed.archie-catalog-wins` | scoped | conforms | `config.py` touched; no catalog override |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | no seed/boot work on the request path |
| `astral.seed.define-approved` | scoped | conforms | no seed-catalog define |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | `config.py` touched; no operator-row restore |
| `astral.seed.other-via-coverage-join` | scoped | conforms | `config.py` touched; no coverage-join change |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no data-layer logging; new route returns JSON only |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no `src/data/**` |
| `astral.standards.debug-contract-gated` | scoped | conforms | no debug-contract emission; local branch does not log |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | two small helpers; decorator early-return only |
| `astral.standards.in-scope-only` | scoped | conforms | no SPA / Stytch / `@require_ip` / decorator stripping |
| `astral.standards.logging-via-utils` | scoped | conforms | no new `print` / `getLogger`; pre-existing utils `logging` warnings untouched |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `local_operator_user` / `auth_passthrough`; no AST in new symbols |
| `astral.standards.no-cross-contamination` | scoped | conforms | stays in ui/utils; no out-of-layer imports |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | identity literals in `AUTH_CONFIG`; `is_admin: True` is the planned passthrough invariant |
| `astral.standards.public-then-helpers` | scoped | conforms | new publics sit with `normalize_user` as the plan specified |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no utils→data import |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no `src/core/**` / `src/data/**` |
| `astral.state.job-prior-states-enforced` | scoped | conforms | `config.py` touched; no `JOB_STATES` change |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no `src/core/**` |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | no `src/ui/frontend/**` |
| `astral.ui.naming-conventions` | scoped | conforms | `/auth_passthrough` snake_case |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | ui/config touched; no worker count change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | one `merge-tests(AST-1440)`; later `test()` is follow-up, not a second merge-tests |
| `orch.git.commit-vocabulary` | universal | conforms | `code()` / `docs()` / `test()` / `merge-tests()` |
| `orch.git.flow-direction-inviolable` | universal | conforms | child work on `origin/sub/…`; not landed on `dev` |
| `orch.git.ftr-sub-topology` | universal | conforms | `sub/AST-1438/AST-1440-local-api-auth-passthrough` |
| `orch.git.merge-on-checkout` | universal | conforms | no rebase of `origin/dev` onto the sub |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | linear commits plus one merge-tests merge |
| `orch.git.no-dev-agent-branches` | universal | conforms | publish ref is `sub/…`, not `dev-<agent>` |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review tree `astral-AST-1438` |
| `orch.git.three-permanent-branches` | universal | conforms | no extra permanent branch |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | product calls already in the Joan-approved plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match the plan snippets |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Foundation child AST-1440 |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed is the correct review entry |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute file edits; pattern lands `proposed` per AUTHORING |
| `orch.roles.betty-owns-test-tree` | universal | conforms | bible/tests on `test()` / `merge-tests` |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Ada Lovelace |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | implementer remains assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer `code()` did not touch test-tree |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.auth.local-deploy-passthrough` | conforms | authored `proposed` (plan/AUTHORING); product matches Solution shape; no runtime id lookup |
| `pattern.config.config-block` | conforms | `AUTH_CONFIG["local_operator"]`; callers read config, not inline decorator literals |
| `pattern.ui.admin-endpoint` | conforms | `@require_admin` kept; new route is a public non-secret signal, not an open admin mutator |

C5 letter (“unapproved citation → fix-now”) is not applied as a finding: the child plan’s job is to **author** this id as `proposed`, Joan APPROVED that, and implementation follows the plan bible rather than depending on the catalog id.

## Plan adherence

Stage 1: proposed catalog entry + §2.1 `AUTH_CONFIG` bullet + rewritten §2.9. Stage 2: `local_operator` literals; `local_operator_user()` / `local_auth_passthrough_payload()`; not routed through `normalize_user` / admin lists. Stage 3: `is_local_deploy_env()` first in `@require_auth` (Bearer ignored, no Stytch, no log); open `GET /api/auth_passthrough`; `env.example` comments; session-policy payload unchanged. Out of scope held: no `src/ui/frontend/**`, no `stytch.py` / `auth_bootstrap.py` / `@require_ip`, no decorator removal. Sibling AST-1441 owns SPA Login / `RequireAuth` / extend. Estimate 3 matches the footprint.

C6 §5a–§5g: top-level imports; ui→utils only on the new line; no swallowed exceptions; no `debug=` / LLM-external surfaces. Fail-closed: `is_local_deploy_env()` is stripped case-insensitive `"local"` only (unset/staging/production/test stay 401).

## Findings

(none)

## C4

Joan `## Joan validate` is attached (APPROVED). No Excluded statute table in that attachment — no straggler rows.

## What’s solid

Decorator kept; gate is deploy env not hostname; synthetic always-admin from `AUTH_CONFIG`; public boolean payload has no secrets; Betty isolated 401s from dotenv `local` and covered the new path.

## Notes (Chuckles writeback only — not extra agent work)

- Full verdict belongs in the issue doc; Linear gets the slim line only (no `revision=N`).
- Pattern stays `proposed` until Archie approves on the parent catalog — parent follow-up, not a child fix-now.
- Review tip is `origin/sub/…` @ `8f046772`; local worktree HEAD `5d8713f3` is a sync commit on a different tracking branch.
- Registry prose says “65 active”; harvested table on this tree has **64** ids — all 64 scored.

## Recommended actions (Chuckles)

1. Append this artifact to `docs/features/foundation/ast-1440-local-api-auth-passthrough.md`.
2. `docs(AST-1440): Radia review — clean` on the publish ref; push.
3. `linear_proxy.py --as radia save-comment` with the slim upshot.
4. Tests Passed → Review Posted; datt §3h PROCEED → User Testing (skip resolve-child).

context_tokens≈48000
