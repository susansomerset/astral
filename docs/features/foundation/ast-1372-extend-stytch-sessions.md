# AST-1372 — Extend Stytch sessions

<!-- linear-archive: AST-1372 archived 2026-08-31 -->

## Linear archive (AST-1372)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1372/extend-stytch-sessions  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Stytch client sessions today use a hardcoded login duration and do not extend when someone keeps working in the app, so active users still get bounced to the log-off path on a fixed clock. This epic puts session lifetime and activity-based extension rules in `AUTH_CONFIG` and wires the SPA to honor them, so friends-and-family use stays logged in while they are actively using Astral and still expires cleanly when they are not.

## Functional scope

* **Config-owned session rules.** Session duration and the activity-extension cadence live as non-secret literals in `AUTH_CONFIG` (defaults matching the brief: 20-minute session lifetime; extension cadence shorter than that lifetime, e.g. every 10 minutes). Changing those values does not require hunting hardcoded SPA constants.
* **SPA can read session policy before and after login.** The React app obtains the configured session duration and extension cadence from the product (config-backed API surface), including on the authenticate handoff path where a Bearer session may not exist yet — so login and extend use the same numbers.
* **Login / authenticate uses configured duration.** Magic-link and OAuth authenticate handoff pass the configured `session_duration_minutes` into Stytch (replacing the current hardcoded 60-minute client constant).
* **Activity-based session extend.** While a Stytch client session exists, the SPA periodically calls Stytch session authenticate with the configured duration so an active tab resets expiry; when extends stop (tab closed / idle past duration), the existing log-off / expired-session UX still applies.

## Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — extend `AUTH_CONFIG` for session duration and extension cadence; callers read config, do not redefine literals inline.
* **New patterns proposed**
  * none
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — session rules are behavior-driving literals in config, not scattered module constants.
  * `astral.standards.no-hardcoded-sets` — remove the SPA hardcoded session-duration constant in favor of config-backed values.
  * `astral.layers.ui-config-driven-business-logic` — SPA renders/applies policy resolved from config via the UI API; does not invent a second source of truth.
  * `astral.config.secrets-and-env-specific-from-environ` — session duration/cadence are not secrets and must not be env lookups; Stytch credentials stay env-driven as today.
  * `astral.standards.in-scope-only` — touch only auth session policy surfaces named by this definition.
  * `astral.idioms.require-auth-on-protected-endpoints` — any new authenticated API stays decorated; a deliberately public non-secret session-policy read (if needed for pre-login authenticate) must stay free of secrets and stay explicitly open.

## Boundaries

* Does **not** change Stytch Dashboard project settings, redirect URLs, or OAuth/magic-link provider setup (AST-613 / AST-830 territory stays as-is aside from duration passed at authenticate).
* Does **not** redesign the log-off / expired-session screen (AST-624 / AST-625) — only requires that expiry after the new duration still lands there correctly.
* Does **not** change Flask JWT validation policy, admin gating, `/api/me` shape, or candidate-selector locks (AST-610 / AST-611 / AST-831).
* Does **not** add manual sign-out UX, MFA, password login, or account/session management screens.
* Does **not** alter backend `debug=` logging contracts (frontend-led session lifecycle; no new backend debug requirements).

## Acceptance criteria

* `AUTH_CONFIG` (or a clearly named sub-block under it) holds session duration minutes and activity-extension interval; defaults are 20 and an interval shorter than 20 (brief example: 10).
* Authenticate handoff (magic-link and Google OAuth) creates a Stytch session whose lifetime matches the configured duration — not a leftover hardcoded 60.
* With a valid session and the SPA open, session expiry is reset on the configured extension cadence via Stytch session authenticate using that same duration.
* If the user stops using the app long enough that no successful extend keeps the session alive, they see the existing log-off / timeout path rather than a silent broken shell.
* Changing only the config literals (no SPA constant edits) is enough for an engineer to retune duration/cadence for a later UAT pass.
* No regression to login, Bearer API calls, admin gating, or first-time visitor Login vs log-off distinction.

## Dependencies and blockers

none

## Open questions

none

## Proposed child tickets

#### 1!: **AUTH_CONFIG Stytch session rules + SPA-readable policy - Ada**

Owns adding session duration and activity-extension cadence to `AUTH_CONFIG`, and exposing those non-secret values to the SPA (including a path usable before Bearer login for authenticate handoff). Does **not** own the React extend loop or authenticate call sites (child 2).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.config.secrets-and-env-specific-from-environ`; `astral.layers.ui-config-driven-business-logic`; `astral.idioms.require-auth-on-protected-endpoints`
**Estimate: 2**

#### 2: **SPA authenticate duration + activity session extend - Katherine**

Owns wiring login/authenticate handoff and in-app activity extension to the config-backed policy (Stytch authenticate with configured duration on cadence while a session exists); removes the hardcoded client session-duration constant. Does **not** own inventing the config keys or policy API (after #1). Must keep AST-624/625 log-off behavior intact when the session finally expires.
**Citations:** `astral.standards.no-hardcoded-sets`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`
**Estimate: 3**

**Monolith check:** Functional scope has 4 capabilities; 2 children — config/API vs SPA lifecycle — intentional split across layers.

---

## Original brief

Update [config.py](<http://config.py>) to manage stytch session rules.

````
Here's how to handle both requirements:

**1. Set session duration to 20 minutes**

Pass `session_duration_minutes: 20` when initiating or authenticating a session.

**2. Auto-refresh with activity**

The JWT token refreshes automatically every 5 minutes (that's its fixed expiry), but the *session lifetime* does **not** extend automatically. To keep users logged in with activity, call `session.authenticate()` with `session_duration_minutes: 20` periodically or on user actions:

```javascript
const extendSession = () => {
  if (stytch.session.getSync()) {
    stytch.session.authenticate({ session_duration_minutes: 20 });
  }
};
// e.g., extend every 10 minutes
setInterval(extendSession, 600000);
```

Each call resets the expiry to 20 minutes from that moment.

```suggestions
(Extend or expire a session)[/consumer-auth/manage-sessions/lifecycle/extend-or-expire-session]
(Session JWTs and tokens)[/multi-tenant-auth/manage-sessions/jwts-and-tokens]
```
````

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
