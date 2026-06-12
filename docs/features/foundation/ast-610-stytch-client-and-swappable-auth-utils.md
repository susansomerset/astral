# AST-610 — Stytch client and swappable auth utils (Use stytch for user authentication)

- **Linear (this ticket):** [AST-610](https://linear.app/astralcareermatch/issue/AST-610/stytch-client-and-swappable-auth-utils-use-stytch-for-user)
- **Parent:** [AST-609](https://linear.app/astralcareermatch/issue/AST-609/use-stytch-for-user-authentication)
- **Publish ref:** `origin/sub/AST-609/AST-610-stytch-client-and-auth-utils` (child of AST-609; not Linear `gitBranchName`)
- **Blocks:** [AST-611](https://linear.app/astralcareermatch/issue/AST-611/flask-stytch-auth-admin-role-and-api-enforcement-use-stytch-for-user) (Flask decorator wiring)

## Summary

Add a **Stytch B2C Consumer SDK wrapper** in `src/external/stytch.py` and a **provider-agnostic auth helper** in `src/utils/auth.py` so authentication can be swapped later without rewriting Flask or React. This ticket delivers config/env documentation, the external client, normalized `g.user`-ready user dicts (`user_id`, `name`, `is_admin`), and admin resolution from config — **not** Flask decorators, API routes, or React login (siblings **AST-611** / **AST-612**).

## Layer contract (mandatory — do not violate in build)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/external/stytch.py` | Stytch SDK calls only | May import `utils` only |
| `src/utils/auth.py` | Normalize user + admin check + `validate_bearer_token` orchestration | **Must not** import `external`, `core`, or `data` |
| `src/ui/auth.py` | **Out of scope** (AST-611) | UI may import `core` + `utils` only — never `external` |

Because `utils` cannot import `external` and `ui` cannot import `external`, **`utils/auth.py` uses a registerable token authenticator**:

1. `external/stytch.py` exposes `authenticate_session_jwt(session_jwt: str) -> dict` (raw Stytch session payload).
2. `utils/auth.py` exposes `register_token_authenticator(fn)` and `validate_bearer_token(token) -> dict | None` which calls the registered `fn`, then `normalize_user(...)`.
3. **AST-611** calls `register_token_authenticator(stytch.authenticate_session_jwt)` at Flask startup (or first `require_auth` use) — **not in this ticket**.

⚠️ **Decision:** Stytch **B2C Consumer** `Client` with `sessions.authenticate_jwt()` — local JWKS validation with API fallback when JWT is expired. React SPA sends `Authorization: Bearer <session_jwt>` (AST-612); opaque `session_token` is not the primary path.

⚠️ **Decision:** Admin is config-driven via `AUTH_CONFIG` (`ASTRAL_ADMIN_USER_IDS`, `ASTRAL_ADMIN_EMAILS` env vars). No hardcoded `"susan"` in product code.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| `src/ui/auth.py` `@require_auth` / `@require_admin` / IP cutover | **AST-611** (Hedy) |
| React login, token storage, nav admin filtering | **AST-612** |
| `register_token_authenticator(...)` call at server startup | **AST-611** |
| Committing under `tests/` or `docs/ASTRAL_TEST_BIBLE.md` | **Betty** (`qa-child`) — engineer pre-commit hook blocks these paths |
| Removing `ASTRAL_ALLOWED_IPS` behavior | **AST-611** |

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `requirements.txt` | Add `stytch` Python SDK pin | deps | Ada (build) |
| `env.example` | Document Stytch + admin env vars | docs | Ada (build) |
| `src/utils/config.py` | Add `AUTH_CONFIG` + `get_auth_config()` | utils | Ada (build) |
| `src/external/stytch.py` | New Stytch B2C client wrapper | external | Ada (build) |
| `src/utils/auth.py` | New provider-agnostic auth helper | utils | Ada (build) |
| `tests/component/external/test_stytch.py` | Component tests for external wrapper | tests | Betty (qa-child) |
| `tests/component/utils/test_auth.py` | Component tests for utils auth (mock authenticator) | tests | Betty (qa-child) |

## Stage 1: Config, env, and dependency

**Done when:** `AUTH_CONFIG` is readable from `config.py`; `env.example` documents all new vars; `stytch` is listed in `requirements.txt`; `pip install -r requirements.txt` succeeds.

1. In `requirements.txt`, add a line `stytch` after the other API client packages (no version pin unless install fails — then pin to the version that installs cleanly on Railway nixpacks).

2. In `env.example`, after the `ASTRAL_ALLOWED_IPS` block, add:

```
# Stytch B2C Consumer authentication (required once AST-611 enables auth)
# Dashboard: https://stytch.com/dashboard
STYTCH_PROJECT_ID=project-test-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
STYTCH_SECRET=secret-test-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=

# Admin users (comma-separated, no spaces around commas). Match Stytch user_id and/or email.
# Susan's Stytch login must appear here before AST-611 cutover.
ASTRAL_ADMIN_USER_IDS=
ASTRAL_ADMIN_EMAILS=susan@susansomerset.com
```

3. In `src/utils/config.py`, after the `ADMIN_CONFIG` block (around line 2160), add:

```python
# ---------------------------------------------------------------------------
# AUTH_CONFIG: Authentication and admin role resolution (AST-609 / AST-610).
# Consumed by src/utils/auth.py. Admin lists are env-driven — never hardcode
# Susan in Flask decorators.
# ---------------------------------------------------------------------------
def _parse_csv_env(name: str) -> frozenset[str]:
    raw = os.environ.get(name, "")
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


AUTH_CONFIG = {
    "admin_user_ids": _parse_csv_env("ASTRAL_ADMIN_USER_IDS"),
    "admin_emails": frozenset(
        e.lower() for e in _parse_csv_env("ASTRAL_ADMIN_EMAILS")
    ),
    "stytch_project_id": os.environ.get("STYTCH_PROJECT_ID", ""),
    "stytch_secret": os.environ.get("STYTCH_SECRET", ""),
}


def get_auth_config() -> Dict[str, Any]:
    """Return AUTH_CONFIG (shallow copy safe for read-only callers)."""
    return dict(AUTH_CONFIG)
```

4. Update the module docstring **Config sections** bullet list at the top of `config.py` to include `AUTH_CONFIG`.

5. Do **not** add `validate_stytch_environment()` or fail server startup on missing Stytch vars in this ticket — AST-611 owns cutover timing; missing vars should surface when `authenticate_session_jwt` is first called.

## Stage 2: Stytch external client (`src/external/stytch.py`)

**Done when:** Module imports cleanly; `authenticate_session_jwt` returns a normalized raw session dict on success; raises `StytchAuthError` on invalid/expired tokens; follows lazy-client pattern like `anthropic.py`.

1. Create `src/external/stytch.py` with module docstring matching other externals (purpose, public API, required env vars).

2. Define exception class:

```python
class StytchAuthError(Exception):
    """Raised when Stytch rejects a session JWT."""
```

3. Implement lazy client (do **not** validate env at import time — unlike `gmail.py`):

```python
_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    from stytch import Client  # lazy import
    project_id = AUTH_CONFIG["stytch_project_id"]
    secret = AUTH_CONFIG["stytch_secret"]
    if not project_id or not secret:
        raise StytchAuthError("STYTCH_PROJECT_ID and STYTCH_SECRET must be set")
    _client = Client(project_id=project_id, secret=secret)
    return _client
```

Import `AUTH_CONFIG` from `src.utils.config` only.

4. Implement `authenticate_session_jwt(session_jwt: str) -> dict`:

   - Strip whitespace from `session_jwt`; if empty, raise `StytchAuthError("missing session JWT")`.
   - Call `_get_client().sessions.authenticate_jwt(session_jwt=session_jwt)`.
   - On any SDK exception, wrap/re-raise as `StytchAuthError` with the original message preserved (`raise StytchAuthError(str(exc)) from exc`).
   - Return a **plain dict** (not SDK object) with keys:
     - `user_id`: `str` — from `resp.user.user_id`
     - `email`: `str | None` — primary email: first entry in `resp.user.emails` with `.verified is True`, else first email, else `None`; use `.email` field lowercased
     - `name`: `str` — `f"{first} {last}".strip()` from `resp.user.name` when present; else `email`; else `user_id`
   - Do **not** set `is_admin` here — that is `utils/auth.py` responsibility.

5. Set `__all__ = ["authenticate_session_jwt", "StytchAuthError"]`.

## Stage 3: Swappable auth utils (`src/utils/auth.py`)

**Done when:** `normalize_user`, `is_admin`, `register_token_authenticator`, and `validate_bearer_token` exist; return shape matches §2.9 / AST-611 contract; no imports from `external`, `core`, or `data`.

1. Create `src/utils/auth.py` with module docstring explaining the registerable-authenticator pattern and AST-611 wiring obligation.

2. Define module-level registry:

```python
from typing import Any, Callable, Mapping

TokenAuthenticator = Callable[[str], Mapping[str, Any]]
_authenticate: TokenAuthenticator | None = None
```

3. Implement `register_token_authenticator(fn: TokenAuthenticator) -> None`:
   - Set global `_authenticate = fn`.
   - Allow re-registration (idempotent for tests).

4. Implement `is_admin(*, user_id: str, email: str | None) -> bool`:
   - Read `AUTH_CONFIG` from `src.utils.config`.
   - Return `True` if `user_id in AUTH_CONFIG["admin_user_ids"]` OR (`email` is not None and `email.lower() in AUTH_CONFIG["admin_emails"]`).
   - Otherwise `False`.

5. Implement `normalize_user(*, user_id: str, name: str, email: str | None) -> dict`:
   - Return exactly:
     ```python
     {
         "user_id": user_id,
         "name": name,
         "is_admin": is_admin(user_id=user_id, email=email),
     }
     ```
   - `user_id` and `name` must be non-empty strings; if `name` is blank after strip, use `email or user_id`.

6. Implement `validate_bearer_token(raw_token: str) -> dict | None`:
   - Strip `raw_token`; if empty, return `None`.
   - If `_authenticate is None`, return `None` (AST-611 has not wired provider yet).
   - Try:
     - `session = _authenticate(raw_token)` — must be a mapping with `user_id`, `name`, `email` keys (as returned by `stytch.authenticate_session_jwt`).
     - Return `normalize_user(user_id=str(session["user_id"]), name=str(session.get("name") or ""), email=session.get("email"))`.
   - On **any** exception from `_authenticate`, return `None` (do not leak Stytch errors to callers — AST-611 maps `None` to 401).

7. Set `__all__ = ["register_token_authenticator", "validate_bearer_token", "normalize_user", "is_admin", "TokenAuthenticator"]`.

## Stage 4: Build verification and Code Complete

**Done when:** `python -m compileall src/external/stytch.py src/utils/auth.py` passes; no edits under `tests/`; Linear status moves to **Code Complete** with comment listing shipped files.

1. Run compile check on new/changed Python modules.

2. Confirm `src/ui/auth.py` is **unchanged** (still stub — AST-611).

3. Post **Code Complete** comment on AST-610 listing:
   - New modules and config block
   - `g.user` shape produced by `normalize_user`
   - Instruction for AST-611: `register_token_authenticator(stytch.authenticate_session_jwt)` before auth checks
   - Betty: implement QA manifest per **QA test specification** below

4. Do **not** commit test files in this ticket's build commits.

## QA test specification (Betty — `qa-child`, not Ada commits)

Betty delivers `tests/component/external/test_stytch.py` and `tests/component/utils/test_auth.py` via `push-tests(AST-610)` before **Tests Ready**.

### `tests/component/utils/test_auth.py`

Mock `TokenAuthenticator` — no live Stytch.

| Test class | Cases |
|------------|-------|
| `TestIsAdmin` | user_id in `ASTRAL_ADMIN_USER_IDS` → True; email in `ASTRAL_ADMIN_EMAILS` (case-insensitive) → True; neither → False |
| `TestNormalizeUser` | returns `user_id`, `name`, `is_admin`; blank name falls back to email |
| `TestValidateBearerToken` | `None` when token empty; `None` when no authenticator registered; happy path with mock returning `{user_id, name, email}`; `None` when mock raises |

### `tests/component/external/test_stytch.py`

Mock `stytch.Client` / `sessions.authenticate_jwt`.

| Test class | Cases |
|------------|-------|
| `TestAuthenticateSessionJwt` | happy path maps user_id, email, name from SDK response object; empty JWT raises `StytchAuthError`; SDK exception wraps to `StytchAuthError`; missing env vars on `_get_client` raises `StytchAuthError` |

## Self-Assessment

**Scope:** `scope-Single-Component` — Two new modules (`external/stytch.py`, `utils/auth.py`) plus a small `AUTH_CONFIG` block and `env.example`/`requirements.txt` edits; no Flask, React, or route changes.

**Conf:** `conf-high` — Mirrors existing external lazy-client and utils pure-function patterns; Stytch `authenticate_jwt` is documented; registerable authenticator resolves layer import constraints explicitly.

**Risk:** `risk-Medium` — Wrong `g.user` shape or admin resolution would break AST-611 enforcement, but this ticket does not change live auth behavior until AST-611 wires the decorator.

## Self-review against ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §3.3 imports — external → utils only; utils → utils only | **Pass** — registry pattern avoids utils→external import |
| §2.1 config — env-driven admin lists in `AUTH_CONFIG` | **Pass** |
| §2.9 auth — `normalize_user` returns `user_id`, `name`, `is_admin` for `g.user` | **Pass** |
| §3.5 naming — snake_case modules/functions | **Pass** |
| §1.3 DRY — single normalize path; Stytch mapping only in external | **Pass** |
| UI must not import external | **Pass** — deferred to AST-611 via registry |

No `conf-!!-NONE` conflicts.
