# AST-1438 — Disable authentication on localhost

<!-- linear-archive: AST-1438 archived 2026-09-09 -->

## Linear archive (AST-1438)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1438/disable-authentication-on-localhost  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Local development currently still talks to Stytch for every protected API call and session refresh. When the Stytch session is missing or belongs to the wrong project, Flask logs `session_not_found` and the SPA demands a login or a token refresh even though the operator is on their own machine. This epic turns authentication off for the existing local deploy env so localhost UAT does not depend on a live Stytch session. Staging and production keep full Stytch auth.

## Functional scope

When the running server's deploy environment value is `local` (the same `ASTRAL_DEPLOY_ENV` already used for the nav footer and local debug), protected APIs do not require a valid Stytch session JWT and do not call Stytch to validate or refresh one.

The local session is a synthetic always-admin operator (not a Stytch user) so admin screens work on localhost without a Google/magic-link login. Identity literals live in auth config, not an inline email list.

The SPA can learn that local auth is off from a public, non-secret read before any login. When that signal is on, the app does not show Login or Log-off for a missing Stytch session, does not run Stytch session extend/refresh, and treats the operator as already authenticated via `/api/me`.

When the deploy environment is anything other than `local` (including unset), missing or invalid credentials still fail closed: 401 on protected APIs, Login / session extend / expired-session log-off unchanged.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: local-operator identity is a named auth-config literal, not an inline set. `pattern.ui.admin-endpoint`: admin routes keep the admin decorator; local passthrough only supplies an admin identity, it does not strip admin checks.
* **New patterns proposed** — `pattern.auth.local-deploy-passthrough`: protected routes keep `@require_auth`; when deploy env is `local`, the decorator (and the SPA gate that honors the same public signal) skip Stytch validation/refresh and synthesize the local operator. Child 1 authors the catalog entry for Archie approval; child 2 reuses it. No other local-auth shortcut.
* **Applicable statutes** — universal set (all active `tier: universal` statutes). Scoped: `astral.idioms.require-auth-on-protected-endpoints` (decorator stays on protected routes; local is internals, not stripped decorators); `astral.config.config-source-of-truth`; `astral.config.secrets-and-env-specific-from-environ` (gate is `ASTRAL_DEPLOY_ENV`); `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`; `astral.layers.import-direction` (utils still does not import external; Stytch stays behind the registered authenticator); `astral.layers.ui-config-driven-business-logic`; `astral.standards.logging-via-utils` (no `session_not_found` warning spam on the local passthrough path).

## Boundaries

Does not disable auth on staging, production, test, or any host whose deploy env is not `local`. Browser hostname (`localhost`) is not the gate.

Does not remove `@require_auth` / `@require_admin` from routes. Does not change `@require_ip` or `ASTRAL_ALLOWED_IPS`. Does not change Stytch Dashboard, live-project JWT validation, session duration policy, or non-local session extend.

Does not change Surfer / extension auth. Does not alter expired-session log-off or SPA-mounted revalidation on non-local deploys (AST-625, AST-1408, AST-1424 / AST-1433).

Does not add a second local-user picker or non-admin impersonation.

## Acceptance criteria

1. With deploy env `local`, opening the app on localhost with no valid Stytch session reaches the app (not Login / Log-off). Protected APIs including `/api/me` and `/api/nav_config` return 200. Admin surfaces are available.
2. Those local requests do not log `Bearer token validation failed` or `Stytch session_not_found`.
3. With deploy env `local`, the SPA does not call Stytch session authenticate, extend, or refresh.
4. With deploy env `staging`, `production`, or unset: missing/invalid Bearer still 401; Login still shows when there is no session; session extend still runs when a Stytch session exists.
5. Every previously protected route still carries `@require_auth` (or `@require_admin`). Intentionally open routes stay open.

## Dependencies and blockers

none. Adjacent in flight (do not regress on non-local): [AST-1408](https://linear.app/astralcareermatch/issue/AST-1408/keep-the-spa-mounted-across-session-revalidation-page-refreshes-and) (SPA mounted across revalidation), [AST-1424](https://linear.app/astralcareermatch/issue/AST-1424/when-i-refresh-from-a-deeplink-on-staging-i-get-an-error) / [AST-1433](https://linear.app/astralcareermatch/issue/AST-1433/expired-session-deeplink-refresh-404-when-i-refresh-from-a-deeplink-on) / [AST-1435](https://linear.app/astralcareermatch/issue/AST-1435/test-gap-ast-1117-candidate-spa-guard-when-i-refresh-from-a-deeplink) (expired-session deeplink refresh).

## Open questions

none.

## Proposed child tickets

#### 1!: **Local API auth passthrough - Ada**

When deploy env is `local`, protected API auth does not validate or refresh a Stytch token; it sets the synthetic always-admin local operator and answers a public non-secret "local auth is off" read the SPA can call before login. Documents the local exception in Code Rules auth and authors `pattern.auth.local-deploy-passthrough` for Archie approval. Does not own React Login, RequireAuth, or session extend (child 2).
**Citations:** `pattern.auth.local-deploy-passthrough` (new), `pattern.config.config-block`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.config.config-source-of-truth`, `astral.config.secrets-and-env-specific-from-environ`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`.
**Estimate: 3**

#### 2: **Local SPA skip login and session refresh - Katherine**

After #1: when the public local-auth signal is on, the SPA does not wait for a Stytch session, does not show Login or Log-off for a missing session, does not run session extend/refresh, and uses `/api/me` as the local operator. Non-local Login / Log-off / extend behavior is unchanged.
**Citations:** `pattern.auth.local-deploy-passthrough`, `astral.idioms.require-auth-on-protected-endpoints`.
**Estimate: 3**

**New patterns:** Child 1 introduces `pattern.auth.local-deploy-passthrough`; child 2 is the SPA consumer of the same gate.

**Monolith check:** Functional scope has four capabilities (API passthrough, local operator, public signal, SPA skip); public signal ships with child 1 because the SPA cannot skip login without it. Two children, not one mega-ticket.

---

## Original brief

When the environment variable is 'local', do not demand token validation or refresh:

```
127.0.0.1 - - [18/Aug/2026 18:22:37] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
Bearer token validation failed: status_code=404 request_id='request-id-test-078b7fcf-692c-4ca2-80ad-918393dcf684' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-test-078b7fcf-692c-4ca2-80ad-918393dcf684', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}
Bearer token validation failed: status_code=404 request_id='request-id-test-a880a444-ec33-4ba4-ac7b-3931862712c8' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-test-a880a444-ec33-4ba4-ac7b-3931862712c8', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}
Stytch session_not_found — verify STYTCH_PROJECT_ID and STYTCH_SECRET match the live project used by VITE_STYTCH_PUBLIC_TOKEN (see env.example AST-831)
Stytch session_not_found — verify STYTCH_PROJECT_ID and STYTCH_SECRET match the live project used by VITE_STYTCH_PUBLIC_TOKEN (see env.example AST-831)
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
