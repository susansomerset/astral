# AST-624 — Log-off screen

<!-- linear-archive: AST-624 archived 2026-06-23 -->

## Linear archive (AST-624)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-624/log-off-screen  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

After Stytch authentication shipped (AST-609), an expired session currently drops the user back into the standard login flow with no explanation. That feels like a bug or data loss when someone returns after being idle. This feature adds a dedicated, calm log-off screen that tells the user their session ended and how to get back in — so session loss is understandable instead of confusing.

## Functional scope

* When the app detects that a previously authenticated Stytch session is no longer valid, show a dedicated **log-off screen** instead of the normal login page.
* The screen uses **reason-specific copy** so the user understands why they were logged off:
  * **Inactivity / session timeout** — session expired from idle or Stytch client expiry.
  * **Server rejection (401)** — an API call returned unauthorized while the user was using the app.
* Both reasons use the same log-off screen layout; only the messaging differs.
* The screen instructs the user to refresh the page to sign in again and return to the site.
* The screen includes a visible **Refresh** control (button or equivalent) that reloads the page — not instructions alone.
* The screen uses existing app shell styling (same visual family as Login and other full-page auth states) so it feels intentional, not like a broken page.
* Detection runs in the React SPA only — no new backend endpoints required unless a child plan proves one is necessary for reliable detection.

## Boundaries

* Does **not** change Stytch session duration, idle timeout policy, or Dashboard configuration — those remain as configured today (e.g. 60-minute session at authenticate).
* Does **not** add manual “Sign out” UX, account settings, or session management controls.
* Does **not** build MFA, password login, or broad session-refresh error handling beyond this log-off screen (AST-612 deferred that scope).
* Does **not** alter Flask auth decorators, `/api/me`, or admin gating from AST-611.
* First-time visitors who were never authenticated continue to see the existing Login page — this screen is only for users who **had** a session and lost it.
* No backend debug-logging requirements (UI-only feature).

## Acceptance criteria

* With a valid session, using the app normally works unchanged.
* After Stytch session expiry or inactivity logout (simulated or real), the user sees the log-off screen with **inactivity/timeout** messaging — not the Stytch login widget and not an empty shell.
* After an API 401 while authenticated, the user sees the same log-off screen with **server rejection** messaging (wording distinct from the timeout case).
* The log-off screen includes copy that the user should refresh to log in again, plus a working Refresh control that reloads the page.
* After refresh, the standard Login flow appears and the user can authenticate and reach the app.
* A user who opens the site without ever having logged in still sees the existing Login page, not the log-off screen.
* No regression to magic-link/OAuth login (AST-612/613) or admin UI gating.

## Dependencies and blockers

* **AST-609** (Use Stytch for user authentication) — **Done**. Required foundation; no further blockers.

## Open questions

None.

---

## Original brief

We need a simple screen to show that the stytch account has been logged off from inactivity and tell them to refresh the page to log in and return to the site.

### Comments

#### chuckles — 2026-06-14T05:31:51.698Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-624 (parent) | ftr/ast-624-log-off-screen |
| AST-625 | sub/AST-624/AST-625-session-logoff-screen |

**Epic worktree:** `astral-AST-624/` — one active sub checked out at a time.

**Parent:** AST-624

— Chuckles

#### chuckles — 2026-06-14T05:26:17.478Z
@susan Two open questions in the Description need your call before dispatch:

1. Should the log-off screen offer only “refresh the page” instructions, or also a visible control (e.g. “Refresh now” button or link) that performs the same action?
2. If the user loses session because of an API 401 (server rejected token) rather than Stytch client idle expiry, should they see the same log-off screen or stay on Login?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
