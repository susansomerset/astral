# AST-1424 — When I refresh from a deeplink on staging I get an error

<!-- linear-archive: AST-1424 archived 2026-09-09 -->

## Linear archive (AST-1424)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1424/when-i-refresh-from-a-deeplink-on-staging-i-get-an-error  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

When the Stytch session has expired, a refresh or direct navigation to an in-app path (e.g. `/candidate/backstory` on staging) returns a white page whose body is `{"error":"Not found"}`. The SPA never appears, so neither login nor the log-off screen runs.

## To-be

An expired (or missing) session on any in-app URL always lands on an auth page — login, or the existing log-off screen if they had a session — never a JSON 404. After they sign in, they should be able to reach the app again (returning to the original path is nicer, not required for the first cut).

## Proposed steps

1. Confirm the white-screen JSON is Flask answering the HTML navigation (SPA never boots), vs a client route that 404s after load.
2. For unauthenticated document requests to client paths, serve the SPA (or redirect to login) instead of `{"error":"Not found"}`.
3. Once the SPA loads without a session, reuse the AST-625 / AST-612 gate: log-off if they had a session, Login otherwise.
4. After authenticate, send them into the app (original path if cheap).

## Original report

When my user session has expired, if I refresh or navigate to [https://astral-staging.up.railway.app/candidate/backstory,](<https://astral-staging.up.railway.app/candidate/backstory,>) for example, I get a white screen with {"error":"Not found"}.  I should always be redirected to a login page.

### Comments

#### susan — 2026-08-19T00:18:32.478Z
625

#### chuckles — 2026-08-18T23:54:35.151Z
Ancestor candidates (pick one, ask about one, or reject the lot):

1. AST-625 — Session log-off / expired-session detection (`docs/features/foundation/ast-625-session-logoff-screen-and-expired-session-detection.md`). Closest: expired Stytch session must not dump into an empty shell. Archived Done under AST-624; frontend-only, so a hard refresh of a deep URL never hits it.
2. AST-624 — Log-off screen (`docs/features/foundation/ast-624-log-off-screen.md`). Parent epic of #1; same expired-session UX.
3. AST-612 — React Stytch login + admin UI gating (`docs/features/foundation/ast-612-react-stytch-login-and-admin-ui-gating.md`). `RequireAuth` / unauthenticated users see login. The gate a deep-link SPA load should hit — if Flask 404s first, it never runs.
4. AST-609 — Use Stytch for user authentication (`docs/features/foundation/ast-609-use-stytch-for-user-authentication.md`). Parent of #3; broader auth epic, weaker fit than 625/612.

---

_Implementation detail may live in git history on `origin/dev`._
