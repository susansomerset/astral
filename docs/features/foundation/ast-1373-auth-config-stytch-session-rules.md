# AUTH_CONFIG Stytch session rules + SPA-readable policy

**Linear:** [AST-1373](https://linear.app/astralcareermatch/issue/AST-1373)
**Parent:** [AST-1372](https://linear.app/astralcareermatch/issue/AST-1372) — Extend Stytch sessions
**Publish ref:** `sub/AST-1372/AST-1373-auth-config-stytch-session-rules`

Put Stytch client session lifetime and activity-extension cadence in `AUTH_CONFIG` as non-secret literals, and expose only those values on a deliberately public Flask endpoint so the SPA (sibling AST-1374) can read the same policy before Bearer login on authenticate handoff and after login for the extend loop.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `session_duration_minutes` / `activity_extension_interval_minutes` to `AUTH_CONFIG`; add `get_auth_session_policy()` that returns only those two ints | utils |
| `src/ui/api/api_system.py` | New open (no `@require_auth`) `GET /api/auth_session_policy` returning the policy JSON | ui |

**Out of this ticket (do not touch):** React authenticate / extend call sites (`stytchAuthenticateHandoff.ts`, `AuthContext.tsx`, etc.) — sibling **AST-1374**. Stytch Dashboard, JWT validation (`src/external/stytch.py`), admin lists, `/api/me`, log-off UX.

## Stage 1: AUTH_CONFIG session literals + SPA-safe helper

**Done when:** `AUTH_CONFIG` contains `session_duration_minutes: 20` and `activity_extension_interval_minutes: 10` as plain int literals (not `os.environ`); `get_auth_session_policy()` returns exactly those two keys as ints and never includes secrets or admin lists.

1. In `src/utils/config.py`, update the module header inventory line for `AUTH_CONFIG` so it mentions session duration / activity-extension cadence (AST-1373) in addition to Stytch credentials and admin lists.
2. In the `AUTH_CONFIG` block (after the existing `stytch_project_id` / `stytch_secret` entries), add exactly these keys as **plain literals** (not env lookups — they are not secrets and not environment-specific):
   - `"session_duration_minutes": 20`
   - `"activity_extension_interval_minutes": 10`
3. Keep existing keys and `_parse_csv_env` / `os.environ.get` behavior for admin lists and Stytch credentials unchanged.
4. Immediately after `get_auth_config()`, add:

```python
def get_auth_session_policy() -> Dict[str, int]:
    """Non-secret Stytch session policy for SPA (AST-1373). Never include secrets."""
    return {
        "session_duration_minutes": int(AUTH_CONFIG["session_duration_minutes"]),
        "activity_extension_interval_minutes": int(
            AUTH_CONFIG["activity_extension_interval_minutes"]
        ),
    }
```

5. Do **not** change `get_auth_config()` return shape beyond the new keys appearing when callers copy the full dict (existing callers that only read admin/stytch keys remain valid).

⚠️ **Decision:** Defaults are **20** (session lifetime minutes) and **10** (extend cadence minutes) per parent AST-1372 brief / child AC. Cadence must stay shorter than duration; if a future UAT pass retunes, change only these two literals.

⚠️ **Decision:** Policy lives on `AUTH_CONFIG` itself (not a nested sub-dict) so callers keep the existing flat-block pattern (`pattern.config.config-block`). Key names are explicit enough without nesting.

## Stage 2: Public session-policy API for pre-login SPA reads

**Done when:** Unauthenticated `GET /api/auth_session_policy` returns HTTP 200 JSON `{"session_duration_minutes": 20, "activity_extension_interval_minutes": 10}` (or whatever the config literals currently are); response never contains `stytch_secret`, `stytch_project_id`, admin emails/ids, or other AUTH_CONFIG secrets; existing `@require_auth` endpoints are unchanged.

1. In `src/ui/api/api_system.py`, import `get_auth_session_policy` from `src.utils.config` (add to the existing `src.utils.config` import list).
2. Under the comment `# --- Open endpoints (no auth) ---` (immediately after the existing `health` route, still **before** `# --- Authenticated endpoints ---`), add:

```python
@system_bp.route("/auth_session_policy")
def auth_session_policy():
    """Non-secret session duration + extend cadence for SPA (AST-1373). Public on purpose."""
    return jsonify(get_auth_session_policy())
```

3. Do **not** decorate this route with `@require_auth` or `@require_admin`.
4. Do **not** fold this payload into `GET /api/ui_config` (that route stays authenticated). Authenticate handoff must be able to fetch policy with no Bearer token.
5. Do **not** log the response body or AUTH_CONFIG contents from this handler.

⚠️ **Decision:** Dedicated open route `GET /api/auth_session_policy` rather than stripping auth from `/api/ui_config`. Statute `astral.idioms.require-auth-on-protected-endpoints` allows an explicitly public non-secret read; a dedicated route keeps the exception obvious and avoids leaking the rest of `UI_CONFIG` pre-login.

### Contract for sibling AST-1374 (do not implement here)

| Field | Type | Meaning |
|-------|------|---------|
| `session_duration_minutes` | int | Pass to Stytch `authenticateByUrl` / `session.authenticate` as `session_duration_minutes` |
| `activity_extension_interval_minutes` | int | SPA timer cadence between successful extends while a client session exists |

SPA must replace the hardcoded `SESSION_DURATION_MINUTES = 60` in `stytchAuthenticateHandoff.ts` by reading this endpoint — that replacement is **AST-1374**, not this ticket.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1373
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1372/AST-1373-auth-config-stytch-session-rules` @ `2fa02d7869802800436a5ddbed3d0ade95d16160`

## Traceability
AC1→Stage 1; AC2→Stage 1 (+ dedicated helper); AC3→Stage 2 — parent authenticate/extend/regression AC deferred to AST-1374 per child boundaries.

## Findings

### acceptable — missing `## Self-Assessment`
**Location:** plan doc tail  
**Finding:** No formal self-assessment block (scope/conf axes).  
**Recommendation:** Optional at this footprint; engineer may add at build if Betty/Radia need it — not blocking.

context_tokens≈18500

---

[plan-rubric] PROCEED (Commit: 2fa02d78) Config policy API ready

AST-1373 plan approved.

---

**Gate check:** Plan Ready, assignee Joan — OK. No `[plan-discuss]` rounds.

**R5 / definition fidelity:** Two-file footprint (`config.py`, `api_system.py`) matches child scope. All three child AC map to Stages 1–2. Parent functional items for authenticate handoff, activity extend, and regression are explicitly out-of-scope (AST-1374). Boundaries honored (no React, Stytch Dashboard, JWT, log-off UX).

**R6 highlights:** Layer imports clean (`ui` → `utils` only). Session literals are plain ints in `AUTH_CONFIG`, not env lookups (`astral.config.secrets-and-env-specific-from-environ`). Dedicated public `GET /api/auth_session_policy` with no `@require_auth` is an explicit, documented exception (`astral.idioms.require-auth-on-protected-endpoints`); does not strip auth from `/api/ui_config`. `get_auth_session_policy()` returns only the two non-secret ints. `pattern.config.config-block` shape matches flat `AUTH_CONFIG` extension. Sibling contract table documents AST-1374 consumption.

**In-session R3/R4 (slim R7):** 14 universal orchestration statutes — all `conforms` (plan is docs-shaped workflow; no git/test-tree violations). Scoped considered: `astral.config.config-source-of-truth`, `astral.config.secrets-and-env-specific-from-environ`, `astral.layers.ui-config-driven-business-logic`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.in-scope-only`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.standards.public-then-helpers`, `astral.standards.dry-and-focused-functions`, `astral.standards.no-cross-contamination`, `astral.standards.names-not-ticket-ids`, `astral.ui.naming-conventions` — all `conforms`. Representative exclusions: `astral.standards.database-header-inventory` (no `data` layer); `astral.batch.*` / `astral.agent.*` / `astral.state.*` (no batch/agent/state touch); `astral.ui.frontend-file-placement` (no `frontend/` paths).
