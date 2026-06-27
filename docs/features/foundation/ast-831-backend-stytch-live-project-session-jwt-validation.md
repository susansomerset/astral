# AST-831 — Backend Stytch live-project session JWT validation

- **Linear (this ticket):** [AST-831](https://linear.app/astralcareermatch/issue/AST-831/backend-stytch-live-project-session-jwt-validation-using-google-to-login-on)
- **Parent:** [AST-829](https://linear.app/astralcareermatch/issue/AST-829/using-google-to-login-on-production-doesnt-work)
- **Publish ref:** `origin/sub/AST-829/AST-831-backend-stytch-live-project-session-jwt-validation`
- **Sibling (frontend — out of scope):** [AST-830](https://linear.app/astralcareermatch/issue/AST-830/production-google-oauth-spa-authenticate-handoff) — SPA `/authenticate` handoff; if OAuth UI succeeds but `/api/me` still 401, this ticket owns the fix.

## Summary

Production Google OAuth on `https://astral.up.railway.app` creates Stytch sessions in the **live** project (`project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a`), but Flask Bearer validation logs `session_not_found` and returns **401** on `GET /api/me`. AST-610/611 shipped `src/external/stytch.py` → `authenticate_session_jwt` → `sessions.authenticate_jwt()` with default local JWKS validation; a JWT minted by the frontend live project fails remote lookup when backend `STYTCH_PROJECT_ID` / `STYTCH_SECRET` point at a **different** Stytch project (or stale credentials), even when all env vars share a `project-live-` / `public-token-live-` prefix. This ticket hardens backend JWT validation to always confirm the session against the configured Stytch project, adds startup visibility for which project env is wired, documents Railway production backend env alignment, and restores **200** on `/api/me` after a fresh Google sign-in — without weakening invalid-token **401** behavior or changing admin resolution.

## Layer contract (mandatory)

| Layer | This ticket | Import rule |
|-------|-------------|-------------|
| `src/external/stytch.py` | JWT validation hardening + project-env logging | external → utils only |
| `src/core/auth_bootstrap.py` | Startup log after wiring authenticator | core → external + utils |
| `src/utils/auth.py` | Richer `session_not_found` log hint only | utils only — no external import |
| `env.example` | Backend live-project verification checklist | docs |
| `src/ui/auth.py`, `src/ui/frontend/**` | **Out of scope** — **AST-830** | do not modify |
| `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, `docs/test-bible/**` | **Betty** (`qa-child`) | do not commit |

⚠️ **Decision:** Pass `max_token_age_seconds=0` to `sessions.authenticate_jwt()` so every Bearer validation hits the Stytch API for the **backend-configured** project instead of trusting local JWKS-only validation. This catches project-mismatch JWTs that might otherwise decode locally with wrong keys and surfaces `session_not_found` only when the session truly does not exist in the configured project. Auth latency increases slightly; correctness on the auth path takes priority over micro-optimization.

⚠️ **Decision:** Log Stytch project env (`test` / `live` / `unknown`) and a truncated `STYTCH_PROJECT_ID` once at Flask startup via `wire_stytch_token_authenticator()` — never log secrets. Gives Railway log readers immediate signal when production runs test credentials.

⚠️ **Decision:** If Susan ops confirms Railway backend vars already match the live project and `session_not_found` persists after Stage 2 code lands, **stop** and comment on parent **AST-829** with Railway log excerpt + Stytch request_id — do not add fallback auth paths or bypass validation. Likely remaining cause is frontend sending a stale JWT (AST-830) or secret rotation not redeployed.

⚠️ **Decision:** Do **not** add a public diagnostic endpoint. Ops visibility stays in startup logs + `env.example` only.

## Out of scope (explicit)

| Item | Owner |
|------|-------|
| React `/authenticate` handoff, `authenticateByUrl` double-invoke | **AST-830** |
| Stytch Dashboard clicks, Railway frontend build env | Susan ops (AST-830 Stage 3 checklist) + docs here for backend vars |
| Admin role rules, `@require_auth` decorator shape | **AST-611** (unchanged) |
| Session duration / log-off screen | **AST-624** / **AST-625** |
| Component tests / bible rows | **Betty** |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/stytch.py` | `max_token_age_seconds=0`; project-env helper; `log_stytch_project_env()` | external |
| `src/core/auth_bootstrap.py` | Call `log_stytch_project_env()` after register | core |
| `src/utils/auth.py` | Append ops hint when log message contains `session_not_found` | utils |
| `env.example` | Backend live-project verification block (AST-831) | docs |
| `tests/component/external/test_stytch.py` | Betty — assert `max_token_age_seconds=0` kwarg | tests (Betty) |

## Stage 1: Production env verification docs (`env.example`)

**Done when:** `env.example` documents how to verify backend `STYTCH_*` vars align with the frontend live public token and names the canonical production project id; no Python changes in this stage.

1. In `env.example`, after the existing Stytch blocks (including any **Production live project (AST-829 / AST-830)** section added by sibling **AST-830** on `origin/ftr/AST-829-production-google-oauth-stytch-live`), append:

```
# --- Backend JWT validation — production live (AST-831) ---
# Symptom when misaligned: Stytch Dashboard shows SessionsGet 200 after Google login,
# but Flask logs: Bearer token validation failed: ... error_type='session_not_found'
#
# Canonical production live project:
#   project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a
#
# Railway PRODUCTION backend runtime (gunicorn service — not the Vite build step):
#   STYTCH_PROJECT_ID=project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a
#   STYTCH_SECRET=secret-live-…   (API Keys → Secret for the SAME project)
#
# Alignment rule (all must reference ONE Stytch project):
#   VITE_STYTCH_PUBLIC_TOKEN  →  public-token-live-…  (frontend build)
#   STYTCH_PROJECT_ID         →  project-live-d0218f6b-…
#   STYTCH_SECRET             →  secret-live-…
# Dashboard check: Stytch → switch to LIVE → Project Settings → Project ID must equal STYTCH_PROJECT_ID.
# After any secret rotation: redeploy the backend service (runtime env), not just the frontend build.
```

2. Do **not** paste real secrets or live token values — placeholders only.

3. If **AST-830** has not yet landed its production block on the merged ftr line when you start, include the full production host + project id lines above anyway (duplicate host lines are acceptable; do not remove AST-830 content if already present).

## Stage 2: Harden `authenticate_session_jwt` and startup visibility

**Done when:** `python -m compileall src/external/stytch.py src/core/auth_bootstrap.py src/utils/auth.py` passes; `authenticate_jwt` is invoked with `max_token_age_seconds=0`; Flask startup logs one line naming Stytch project env + truncated project id (or warns when unset).

1. In `src/external/stytch.py`, add module-level helper (after imports, before `_client`):

```python
def _stytch_project_env(project_id: str) -> str:
    pid = (project_id or "").strip()
    if pid.startswith("project-live-"):
        return "live"
    if pid.startswith("project-test-"):
        return "test"
    return "unknown"
```

2. In the same file, add public startup helper:

```python
def log_stytch_project_env() -> None:
    """Log configured Stytch project env once at startup (no secrets)."""
    import logging

    _log = logging.getLogger(__name__)
    project_id = AUTH_CONFIG["stytch_project_id"]
    if not project_id:
        _log.warning("STYTCH_PROJECT_ID is unset — Bearer auth will fail until configured")
        return
    env = _stytch_project_env(project_id)
    short_id = project_id if len(project_id) <= 32 else f"{project_id[:32]}…"
    _log.info("Stytch auth configured: env=%s project_id=%s", env, short_id)
```

Add `"log_stytch_project_env"` to `__all__`.

3. In `authenticate_session_jwt`, change the SDK call from:

```python
resp = client.sessions.authenticate_jwt(session_jwt=token)
```

to:

```python
resp = client.sessions.authenticate_jwt(
    session_jwt=token,
    max_token_age_seconds=0,
)
```

Keep existing user-resolution logic (direct `resp.user` or `users.get(session.user_id)` fallback) unchanged.

4. In `src/core/auth_bootstrap.py`, after `register_token_authenticator(stytch.authenticate_session_jwt)`, add:

```python
stytch.log_stytch_project_env()
```

5. In `src/utils/auth.py`, inside `validate_bearer_token` except block (where `_log.warning("Bearer token validation failed: %s", exc)` already runs), when `str(exc)` contains `session_not_found`, append a second warning line:

```python
_log.warning(
    "Stytch session_not_found — verify STYTCH_PROJECT_ID and STYTCH_SECRET "
    "match the live project used by VITE_STYTCH_PUBLIC_TOKEN (see env.example AST-831)"
)
```

Do **not** change return behavior — still return `None` → **401**.

## Stage 3: Susan ops — Railway production backend verification

**Done when:** Susan confirms (Linear comment on **AST-831**) that Railway **backend runtime** env vars match the live project. Engineer posts the checklist below when Stages 1–2 land; do **not** move to **Code Complete** until Susan confirms or explicitly defers with evidence that vars were already correct.

**Susan checklist (backend runtime on `https://astral.up.railway.app`):**

1. Open Railway → production **backend** service (gunicorn, not the Vite build job) → Variables.
2. `STYTCH_PROJECT_ID` is exactly `project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a`.
3. `STYTCH_SECRET` is the **Secret** from Stytch Dashboard → **Live** project → API Keys (not the public token, not a test secret).
4. Prefix sanity: `STYTCH_PROJECT_ID` starts with `project-live-`; `STYTCH_SECRET` starts with `secret-live-`.
5. Cross-check: Stytch Dashboard **Live** → API Keys → Public token matches Railway frontend `VITE_STYTCH_PUBLIC_TOKEN` on the **build** service.
6. If any secret or project id changed: **redeploy backend** (runtime), then retry Google login.
7. After deploy, confirm Railway logs show startup line: `Stytch auth configured: env=live project_id=project-live-d0218f6b-c64a-4fa1-8…`.

**Manual repro (Susan, production — after AST-830 OAuth UI fix if needed):**

1. Clean browser profile → `https://astral.up.railway.app` → Login → **Google** → complete OAuth → reach authenticated Astral shell.
2. Open DevTools → Network → confirm `GET /api/me` returns **200** with `user_id`, `name`, `is_admin: true` for Susan.
3. Confirm Railway logs do **not** show `session_not_found` for that session window.
4. Email magic-link login still returns **200** on `/api/me` (same live project).
5. Non-admin Google user: `/api/me` returns **200** with `is_admin: false`; admin API routes return **403**.

If step 2 fails with **401** and logs still show `session_not_found` after Susan confirms checklist items 1–7, comment on **AST-829** with Stytch `request_id` from the log line and **stop** — do not weaken validation.

## Stage 4: Code Complete

**Done when:** Stages 1–2 committed and published; Stage 3 Susan confirmation recorded (or documented blocker); Linear **Code Complete** with production `/api/me` repro summary.

1. Post Linear comment on **AST-831** summarizing:
   - `max_token_age_seconds=0` rationale
   - Startup log sample from Railway (truncated project id only)
   - Stage 3 checklist status
   - `/api/me` **200** repro after Google login (or blocker with request_id)
2. Move **AST-831** to **Code Complete** (keep assignee Ada).

## QA test specification (Betty — `qa-child`, not Ada commits)

Betty extends `tests/component/external/test_stytch.py` via `merge-tests(AST-831)` before **Tests Ready**.

| Test | Assertion |
|------|-----------|
| `TestAuthenticateSessionJwt::test_happy_path_maps_user_id_email_name` | Update mock assert: `authenticate_jwt(session_jwt="jwt-here", max_token_age_seconds=0)` |
| `TestAuthenticateSessionJwt::test_local_jwt_response_fetches_user_by_session_user_id` | Same kwarg assert |
| `TestLogStytchProjectEnv::test_logs_live_prefix` | Mock `AUTH_CONFIG`, call `log_stytch_project_env()`, caplog contains `env=live` |
| `TestLogStytchProjectEnv::test_warns_when_project_id_unset` | Empty project id → warning log |

No changes to `tests/component/ui/test_auth.py` unless Betty finds regressions — UI auth tests use mock authenticator, not live Stytch.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_stytch.py
```

## Self-Assessment

**Scope:** `Single-Component` — touches `src/external/stytch.py`, `src/core/auth_bootstrap.py`, a log hint in `src/utils/auth.py`, and `env.example`; no React or Flask decorator changes.

**Conf:** `Medium` — Stytch `authenticate_jwt` + `max_token_age_seconds=0` is documented SDK behavior and matches the production `session_not_found` symptom when backend project credentials diverge from the frontend; Susan must still confirm Railway backend vars in Stage 3.

**Risk:** `HIGH` — auth validation path for every Bearer request; a mistake here 401s all users or could mask misconfiguration — mitigated by keeping `None` → **401** contract unchanged and forcing remote validation only.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing `authenticate_session_jwt` + `wire_stytch_token_authenticator` pattern from AST-610/611 |
| §2.1 Config | Reads `AUTH_CONFIG["stytch_project_id"]` only; no new config block; env docs in `env.example` |
| §2.4 Batch | N/A |
| §2.6 State machine | N/A |
| §3.3 Imports | `auth_bootstrap` (core) imports external — established AST-611 exception; utils still does not import external |
| §3.5 Naming | `log_stytch_project_env` mirrors existing module-level Stytch helpers |

No conflicts requiring plan revision.

## Review (build)

**Built @ `b4a312a`** — `origin/sub/AST-829/AST-831-backend-stytch-live-project-session-jwt-validation`

- Stage 1: `env.example` backend live-project verification block (AST-831)
- Stage 2: `max_token_age_seconds=0` on `authenticate_jwt`; `log_stytch_project_env()` at startup; `session_not_found` ops hint in `validate_bearer_token`
- Stage 3 (Susan ops): pending — Railway backend `STYTCH_*` alignment checklist in plan §Stage 3

---

## Radia review (2026-06-27)

**Diff:** `origin/dev...origin/sub/AST-829/AST-831-backend-stytch-live-project-session-jwt-validation` (`1be0852`)

**Session:** `fa43d223-42ec-491f-af77-c0f209a3e4d9`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–2: `max_token_age_seconds=0` on `authenticate_jwt`; `log_stytch_project_env()` wired from `auth_bootstrap`; `session_not_found` ops hint in `validate_bearer_token` (still `None` → 401); `env.example` backend live-project checklist. |
| Auth contract | User-resolution path unchanged; invalid JWT still swallowed to 401 via existing `validate_bearer_token` except block — no weakened validation. |
| Layering (§3.3) | Utils does not import external; core → external wiring matches AST-611 pattern; no React / Flask decorator changes. |
| Tests / bible | Betty manifest asserts `max_token_age_seconds=0` on happy path, `TestLogStytchProjectEnv` (live/test/truncate/unset), `test_session_not_found_logs_ops_hint`; bible rows in `external/stytch.md` + `utils/auth.md`. |
| Scope boundary | AST-830 frontend handoff out of product diff — sibling split respected in product code. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | Branch diff vs `origin/dev` | **AST-832** + **AST-830** artifacts on publish ref (`test_consult.py`, frontend Vitest files, sibling bible rows) — outside AST-831 layer contract; likely ftr rollup. Confirm merge-child narrative. |
| **discuss** | Plan Stage 3 | Susan Railway backend `STYTCH_*` confirmation pending — production `/api/me` **200** after Google login depends on ops alignment + **AST-830** SPA handoff. |
| **discuss** | `src/external/stytch.py` `log_stytch_project_env` | §3.2 says external modules do not log — plan **Decision** explicitly requires startup project-env visibility here; justified layer bend via approved plan, not ad hoc. |
| **advisory** | `src/external/stytch.py` | Uses `logging.getLogger(__name__)` — peer `playwright.py` uses `get_logger`; align on touch if logging in external is retained. |
| **advisory** | `test_stytch.py::test_local_jwt_response_fetches_user_by_session_user_id` | Plan QA table asked for `max_token_age_seconds=0` assert on this test too; only happy-path test asserts kwarg — low gap, remote validation still covered by product path. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child`. |
| discuss | Stage 3 Susan backend checklist before production sign-off; if `session_not_found` persists after ops confirm, stop per plan with Stytch `request_id`. |
| discuss | ftr rollup siblings on publish ref — acceptable at merge-child or split for clarity. |
| advisory | Optional: `get_logger` in `stytch.py`; optional kwarg assert on local-JWT fallback test. |

**Publish tip:** `1be0852` (product `b4a312a` + env `6b0cf47` + tests `1be0852`)

## Resolution (2026-06-27)

**Review @ `74cdcea`** — Radia **fix-now: none**. No product commits required.

| Item | Resolution |
|------|------------|
| fix-now | N/A — shipped Stages 1–2 unchanged. |
| discuss — ftr rollup siblings on publish ref | Expected epic-worktree merge history; **AST-831** product delta is `env.example`, `stytch.py`, `auth_bootstrap.py`, `auth.py` only. Sibling test rows (**AST-830**, **AST-832**) ride merge history until **merge-child**. |
| discuss — Stage 3 Susan Railway `STYTCH_*` | Remains manual UAT prerequisite on parent **AST-829**; not blocking **User Testing** on this child. |
| discuss — `log_stytch_project_env` logging in external | Plan **Decision** stands; no code change. |
| advisory — `get_logger` / extra kwarg assert | Deferred; not required for sign-off. |

**§9a dry-run:** `origin/sub/AST-829/AST-831-backend-stytch-live-project-session-jwt-validation` → `origin/dev` **clean**; → `origin/ftr/AST-829-production-google-oauth-stytch-live` **clean**.
