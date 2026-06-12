# AST-611 — Flask Stytch auth, admin role, and API enforcement (Use stytch for user authentication)

- **Linear (this ticket):** [AST-611](https://linear.app/astralcareermatch/issue/AST-611/flask-stytch-auth-admin-role-and-api-enforcement-use-stytch-for-user)
- **Parent:** [AST-609](https://linear.app/astralcareermatch/issue/AST-609/use-stytch-for-user-authentication)
- **Publish ref:** `origin/sub/AST-609/AST-611-flask-stytch-auth-and-admin`
- **Depends on:** [AST-610](https://linear.app/astralcareermatch/issue/AST-610/stytch-client-and-swappable-auth-utils-use-stytch-for-user) on `origin/ftr/ast-609-use-stytch-for-user-authentication` (`register_token_authenticator`, `validate_bearer_token`, `AUTH_CONFIG`)

## Summary

Replace the IP-allowlist + Auth0 stub in `src/ui/auth.py` with real Stytch session JWT validation via `src/utils/auth.py` (wired at startup through a thin **core** bootstrap so UI never imports `external`). Add `@require_admin` for `/api/admin/*` and candidate-management mutations. Expose `is_admin` on `/api/me` via `g.user`. Filter Admin nav from `/api/nav_config` for non-admins. Demote IP allowlist to **`@require_ip` script endpoints only** so the React SPA can load before login (**AST-612**).

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/core/auth_bootstrap.py` | One function: register Stytch authenticator | core → external + utils ✓ |
| `src/ui/auth.py` | `@require_auth`, `@require_admin`, IP helpers | ui → utils only (calls `validate_bearer_token`) |
| `src/ui/server.py` | Call bootstrap at startup; remove SPA IP gate | ui → core + utils |
| `src/ui/api/api_admin.py` | Swap `@require_auth` → `@require_admin` | unchanged |
| `src/external/stytch.py`, `src/utils/auth.py` | **Read-only** — shipped in AST-610 | do not modify |

⚠️ **Decision:** Stytch wiring lives in **`src/core/auth_bootstrap.py`**, not `server.py` direct `external` import — preserves §3.3 (ui never imports external). `server.py` calls `wire_stytch_token_authenticator()` once before blueprint traffic.

⚠️ **Decision:** **`@require_auth` no longer checks IP.** Stytch Bearer JWT is the primary gate for authenticated API routes. **`ASTRAL_ALLOWED_IPS`** applies only to `@require_ip` routes (admin script/data helpers in `api_admin.py`). Empty allowlist = open for `@require_ip` (same as today). Document in `auth.py` module docstring.

⚠️ **Decision:** **`serve_react` removes IP blocking** — static React app always serves (403 contact page removed). Unauthorized API use still returns 401; AST-612 adds login UI client-side.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| React login, token storage, nav dropdown gating | **AST-612** |
| Changes to `src/external/stytch.py` or `src/utils/auth.py` | **AST-610** (already User Testing) |
| `tests/` commits | **Betty** (`qa-child`) |
| `docs/ASTRAL_CODE_RULES.md` §2.9 stub wording update | **Radia** (optional doc pass at review) |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/auth_bootstrap.py` | **New** — `wire_stytch_token_authenticator()` | core |
| `src/ui/auth.py` | Real `@require_auth`, new `@require_admin`, IP doc/behavior | ui |
| `src/ui/server.py` | Call bootstrap; drop SPA IP gate | ui |
| `src/ui/api/api_admin.py` | `@require_auth` → `@require_admin` on Bearer routes; keep `@require_ip` on 3 script routes | ui |
| `src/ui/api/api_candidate.py` | Admin guards on create/delete and admin-only PUT fields | ui |
| `src/ui/api/api_system.py` | Omit Admin nav group for non-admin in `nav_config` | ui |
| `tests/component/ui/test_auth.py` | Extend for Stytch stub + admin decorator | tests (Betty) |

## Stage 1: Core bootstrap + auth decorators

**Done when:** `wire_stytch_token_authenticator()` registers Stytch; `@require_auth` sets `g.user` from `validate_bearer_token`; `@require_admin` returns 403 when `is_admin` is false; `python -m compileall src/core/auth_bootstrap.py src/ui/auth.py` passes.

1. Create `src/core/auth_bootstrap.py`:

```python
"""One-time auth provider wiring (AST-611). Core may import external."""

from src.external import stytch
from src.utils.auth import register_token_authenticator


def wire_stytch_token_authenticator() -> None:
    register_token_authenticator(stytch.authenticate_session_jwt)
```

Set `__all__ = ["wire_stytch_token_authenticator"]`.

2. Rewrite `src/ui/auth.py` module docstring to describe: Stytch Bearer auth via utils; `@require_ip` for script callers; IP allowlist scope.

3. Keep existing helpers `_load_allowed_ips`, `get_client_ip`, `is_ip_allowed`, `require_ip` — **no behavior change** on `require_ip`.

4. Replace `require_auth` implementation:

```python
from src.utils.auth import validate_bearer_token

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header[7:].strip()
        user = validate_bearer_token(token)
        if user is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated
```

Remove IP check from `require_auth`. Remove Auth0 TODO and hardcoded `g.user = {"user_id": "susan", ...}`.

5. Add `require_admin` **below** `require_auth`:

```python
def require_admin(f):
    @require_auth
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.user.get("is_admin"):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated
```

Export `require_admin` — update module docstring list of public decorators.

6. In `src/ui/server.py`, **after** `app = Flask(...)` and **before** blueprint imports, add:

```python
from src.core.auth_bootstrap import wire_stytch_token_authenticator
wire_stytch_token_authenticator()
```

7. In `serve_react`, delete the `if not is_ip_allowed(): return _BLOCKED_HTML, 403` branch — always serve static files. Leave `_BLOCKED_HTML` in file (unused) or delete constant + dead import of `is_ip_allowed` if nothing else in server.py uses it; if `is_ip_allowed` import becomes unused, remove it.

## Stage 2: Admin blueprint enforcement

**Done when:** Every `/api/admin/*` route that today uses `@require_auth` uses `@require_admin` instead; the three `@require_ip` data/script routes unchanged; non-admin Bearer token gets 403 on e.g. `GET /api/admin/config`.

1. In `src/ui/api/api_admin.py`, change import:

```python
from ui.auth import require_admin, require_ip
```

Remove `require_auth` from import.

2. Replace **every** `@require_auth` decorator in this file with `@require_admin` (42 routes per current file).

3. Do **not** change these three routes — keep `@require_ip` only (no Bearer):

   - `GET /api/admin/data/tables`
   - `GET /api/admin/data/table/<table_name>`
   - `GET /api/admin/data/download`

4. Manually verify no `@require_auth` remains in `api_admin.py`.

## Stage 3: Candidate admin mutations + nav filtering

**Done when:** Non-admin gets 403 on candidate create/delete and on PUT with `state` or `api_key`; `/api/nav_config` omits the Admin group for non-admin; `/api/me` returns `{user_id, name, is_admin}`.

### 3a — Candidate API

1. In `src/ui/api/api_candidate.py`, extend import:

```python
from ui.auth import require_auth, require_admin
```

2. Add helper after blueprint creation:

```python
def _forbid_non_admin_candidate_mutation() -> tuple | None:
    """Return (jsonify_response, status) when non-admin attempts admin-only candidate ops."""
    from flask import g
    if g.user.get("is_admin"):
        return None
    return jsonify({"error": "Admin access required"}), 403
```

3. Change decorators:

   - `create_candidate` (POST ``): replace `@require_auth` with `@require_admin`.
   - `delete_candidate` (DELETE `/<candidate_id>`): replace `@require_auth` with `@require_admin`.

4. In `update_candidate_data`, **after** parsing `body` and **before** processing, add:

```python
state_override = body.pop("state", None)
api_key = body.pop("api_key", None)
if not g.user.get("is_admin") and (state_override is not None or api_key is not None):
    return jsonify({"error": "Admin access required"}), 403
```

(Adjust if `state`/`api_key` already popped — ensure non-admin cannot pass either field.)

⚠️ **Decision:** Client-side “selected candidate” (localStorage in `CandidateContext.tsx`) has **no server selection API**. Server enforcement for “changing candidate” in this ticket means **admin-only candidate lifecycle mutations** (create, delete, state override, api_key). Non-admins may still read/update `candidate_data` for any existing candidate id they request — AST-612 gates the UI selector; future ticket may add per-user candidate scoping if needed.

### 3b — Nav config

1. In `src/ui/api/api_system.py`, add helper:

```python
def _nav_config_for_user(candidate_state: str, candidate_id: Optional[str]) -> list:
    nav = _resolve_nav(candidate_state, candidate_id)
    if g.user.get("is_admin"):
        return nav
    return [group for group in nav if group.get("label") != "Admin"]
```

2. In `nav_config()` endpoint, replace `return jsonify(_resolve_nav(...))` with `return jsonify(_nav_config_for_user(candidate_state, candidate_id or None))`.

3. Confirm `/api/me` still returns `jsonify(g.user)` — no code change needed if Stage 1 sets full normalized user dict including `is_admin`.

## Stage 4: Build verification and Code Complete

**Done when:** compileall passes on all touched modules; spot-check with Flask test client (manual or Betty tests); Linear **Code Complete** comment lists behavior changes and Betty QA spec.

1. Run:

```bash
python -m compileall src/core/auth_bootstrap.py src/ui/auth.py src/ui/server.py src/ui/api/api_admin.py src/ui/api/api_candidate.py src/ui/api/api_system.py
```

2. Confirm **no** edits under `tests/` in build commits.

3. Post **Code Complete** comment on AST-611 with:

   - Stytch wired via `wire_stytch_token_authenticator()`
   - IP allowlist scope (`@require_ip` only)
   - Admin enforcement surfaces
   - Betty: QA manifest below

## QA test specification (Betty — `qa-child`, not Hedy commits)

Extend `tests/component/ui/test_auth.py` (replace AST-394 stub-era cases that assume IP gate on `@require_auth`).

### Setup fixture

Add autouse fixture registering a mock authenticator:

```python
@pytest.fixture(autouse=True)
def _register_mock_auth(monkeypatch):
    from src.utils import auth as utils_auth
    def _mock(token: str):
        if token == "good-jwt":
            return {"user_id": "u1", "name": "Test User", "email": "test@example.com"}
        raise ValueError("bad")
    utils_auth.register_token_authenticator(_mock)
```

Patch `AUTH_CONFIG` admin lists per test as needed.

### `TestRequireAuth` (update/replace `TestAuthDecorators`)

| Case | Expect |
|------|--------|
| Missing Bearer | 401 |
| Invalid token (`Bearer bad`) | 401 |
| Valid token (`Bearer good-jwt`) | 200; `g.user` has `user_id`, `name`, `is_admin` |
| `@require_auth` does **not** block on IP when allowlist set and IP wrong | 200 with valid Bearer (proves IP removed from require_auth) |

### `TestRequireAdmin`

| Case | Expect |
|------|--------|
| Non-admin user (`is_admin` False via mock + AUTH_CONFIG) | 403 on `@require_admin` route |
| Admin user | 200 |

Implement with minimal Flask app routes mirroring decorators (same pattern as existing test file).

### Integration smoke (optional in same file)

| Case | Expect |
|------|--------|
| `GET /api/me` with admin mock | 200 JSON includes `"is_admin": true/false` |
| `GET /api/nav_config` non-admin | response groups have no `"label": "Admin"` |

Use `ui.server.app` test client with monkeypatched authenticator + AUTH_CONFIG.

Manifest for **Tests Ready**:

```
tests/component/ui/test_auth.py::TestRequireAuth
tests/component/ui/test_auth.py::TestRequireAdmin
```

## Self-Assessment

**Scope:** `scope-MAJOR-CHANGE` — Rewrites the auth decorator stack, adds core bootstrap, swaps decorators on ~42 admin routes, and adds candidate + nav enforcement across three API modules.

**Conf:** `conf-Medium` — AST-610 defines the utils contract and registry pattern clearly; remaining work is systematic route replacement and IP cutover behavior that must match the documented dev/Railway expectations.

**Risk:** `risk-HIGH` — Incorrect auth wiring would 401 all users or expose admin endpoints; this touches every protected API route’s entry path.

## Self-review against ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §3.3 imports — ui → core/utils; Stytch via core bootstrap | **Pass** |
| §2.9 auth — `g.user` shape `{user_id, name, is_admin}` from `validate_bearer_token` | **Pass** |
| §2.1 config — admin lists stay in `AUTH_CONFIG`; no hardcoded Susan | **Pass** |
| §3.5 naming — snake_case decorators and helpers | **Pass** |
| §1.3 DRY — single `require_admin`; nav filter in one helper | **Pass** |
| UI business logic in API layer — nav admin filter in `api_system.py` | **Pass** |

No `conf-!!-NONE` conflicts.
