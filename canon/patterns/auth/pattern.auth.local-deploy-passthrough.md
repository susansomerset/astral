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
