# AST-609 — Use stytch for user authentication

<!-- linear-archive: AST-609 archived 2026-06-23 -->

## Linear archive (AST-609)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-609/use-stytch-for-user-authentication  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Up to this point we have been using loud IP's that were set as environment variables for astral to be allowed to run on railway.

It is time to implement proper user authentication and I want to use the STYTCH platform for this purpose. We need to be careful because we don't know for sure if the platform will be available in perpetuity so we want to do the similar thing of having an auth.py component (in utils?) and a stytch.py in externals.

I also need for my login to be an admin user, where non admin users cannot change selected candidate and cannot see any of the admin features in the ui.

### Comments

#### chuckles — 2026-06-13T00:08:34.390Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-613** | Stytch magic link and Google OAuth redirect URL mismatch (Use stytch for user authentication) |
| **AST-614** | Local Vite dev fails — @stytch/react not installed (Use stytch for user authentication) |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-12T23:52:31.061Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-609 (parent) | ftr/ast-609-use-stytch-for-user-authentication |
| AST-610 | sub/AST-609/AST-610-stytch-client-and-auth-utils |
| AST-611 | sub/AST-609/AST-611-flask-stytch-auth-and-admin |
| AST-612 | sub/AST-609/AST-612-react-login-and-admin-ui |
| AST-613 | sub/AST-609/AST-613-stytch-login-redirect-urls |
| AST-614 | sub/AST-609/AST-614-vite-stytch-npm-install |

**Epic worktree:** `astral-AST-609/` — one active sub checked out at a time.

**Parent:** AST-609

— Chuckles

#### susan — 2026-06-12T23:50:37.803Z
612:

* Error when entering my email "susan@susansomerset.com": The magic_link_url in the request did not match any redirect URLs set for this project. Please visit [https://stytch.com/dashboard/redirect-urls](<https://stytch.com/dashboard/redirect-urls>) to update the redirect URLs for this project. For more information on why this validation is necessary please visit [https://stytch.com/docs/api/url-validation](<https://stytch.com/docs/api/url-validation>)
* Error when I click on Google SSO: `{"status_code":400,"request_id":"request-id-test-ba8da5e8-e4ab-4a33-a196-3e1d09b682d0","error_type":"no_match_for_provided_oauth_url","error_message":"The oauth redirect url in the request did not match any redirect URLs set for this project. Please visit https://stytch.com/dashboard/redirect-urls to update the redirect URLs for this project. For more information on why this validation is necessary please visit https://stytch.com/docs/api/url-validation","error_url":"https://stytch.com/docs/api/errors/400#no_match_for_provided_oauth_url"}`
* Error when running from localhost on vite:

```
[plugin:vite:import-analysis] Failed to resolve import "@stytch/react" from "src/App.tsx". Does the file exist?
```

```
/Users/susan/chuckles/astral/src/ui/frontend/src/App.tsx:2:31
```

```
2  |  var _s = $RefreshSig$();
3  |  import { BrowserRouter, useRoutes } from "react-router-dom";
4  |  import { StytchProvider } from "@stytch/react";
   |                                  ^
5  |  import { AuthProvider } from "./contexts/AuthContext";
6  |  import { stytchClient } from "./lib/stytchClient";
```

```
    at TransformPluginContext._formatLog (file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:42528:41)
    at TransformPluginContext.error (file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:42525:16)
    at normalizeUrl (file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:40504:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:40623:37
    at async Promise.all (index 2)
    at async TransformPluginContext.transform (file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:40550:7)
    at async EnvironmentPluginContainer.transform (file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:42323:18)
    at async loadAndTransform (file:///Users/susan/chuckles/astral/src/ui/frontend/node_modules/vite/dist/node/chunks/dep-D4NMHUTW.js:35739:27
```

#### chuckles — 2026-06-12T23:20:49.641Z
## Manual test steps

**Tree:** `origin/ftr/ast-609-use-stytch-for-user-authentication` @ **`41861908`** · local **`dev`** fast-forward merged · **`origin/dev`** pushed for Railway staging. Restart **`launch.sh`** (or redeploy) if already running.

**Prerequisites (Railway + local):**

1. **Stytch Dashboard** — B2C Consumer project with Email Magic Links and/or Google OAuth enabled.
2. **Redirect URLs** (Login + Sign-up): `http://localhost:5173/authenticate` and `https://<staging-host>/authenticate`.
3. **Authorized environments:** same origins as redirect URLs (no trailing path).
4. **Backend env:** `STYTCH_PROJECT_ID`, `STYTCH_SECRET`, `ASTRAL_ADMIN_EMAILS=susan@susansomerset.com` (and/or your Stytch `user_id` in `ASTRAL_ADMIN_USER_IDS`).
5. **Frontend build env:** `VITE_STYTCH_PUBLIC_TOKEN` (Stytch public token) — required at Vite build time on Railway.
6. **`ASTRAL_ALLOWED_IPS`** is no longer the SPA gate; unauthenticated API calls return **401**.

### AST-612 — Login + Bearer on API

1. Open the app in a private window → **Login** page (Stytch UI), not the main shell.
2. Sign in with Susan's email (magic link or OAuth) → lands on `/authenticate` then the app.
3. DevTools → Network: API calls include **`Authorization: Bearer …`** (session JWT).
4. **`GET /api/me`** returns `{ user_id, name, is_admin: true }` for Susan.

### AST-611 — Admin API enforcement

5. As Susan (admin): open **Admin** nav sections (Manage Tasks, Scheduled Actions, etc.) — pages load (**200**).
6. As Susan: change **selected candidate** in the nav dropdown — succeeds.
7. **Non-admin check** (second Stytch user *not* in admin lists): sign in → **`/api/me`** shows **`is_admin: false`**; **`GET /api/admin/...`** returns **403**; candidate create/delete/state mutations return **403**.

### AST-612 — Admin UI gating + candidate lock (non-admin)

8. Non-admin: **Admin** items absent from nav (server-filtered `/api/nav_config`).
9. Non-admin: direct URL to `/admin/tasks` (or any `/admin/*`) → redirected away from admin shell.
10. Non-admin: candidate **`<select>`** disabled / cannot switch candidate in UI.

### AST-610 — Substrate (smoke)

11. Invalid or missing Bearer on a protected route → **401** (not IP **403**).
12. Valid Bearer with wrong/expired JWT → **401**.

**Children on this tree:** AST-610 (utils + external client), AST-611 (Flask decorators + admin routes), AST-612 (React login + UI gating).

— Chuckles

#### chuckles — 2026-06-12T22:30:02.629Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-609 (parent) | ftr/ast-609-use-stytch-for-user-authentication |
| AST-610 | sub/AST-609/AST-610-stytch-client-and-auth-utils |
| AST-611 | sub/AST-609/AST-611-flask-stytch-auth-and-admin |
| AST-612 | sub/AST-609/AST-612-react-login-and-admin-ui |

**Epic worktree:** `astral-AST-609/` — one active sub checked out at a time.

**Parent:** AST-609

— Chuckles

#### susan — 2026-06-12T22:29:13.891Z
Sorry, Chuckles! I meant to keep this in the backlog, not queue it for datt!

---

_Implementation detail may live in git history on `origin/dev`._
