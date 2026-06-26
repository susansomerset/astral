# AST-640 — Show environment and up time as read-only at the bottom of nav for admin view only.

<!-- linear-archive: AST-640 archived 2026-06-23 -->

## Linear archive (AST-640)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-640/show-environment-and-up-time-as-read-only-at-the-bottom-of-nav-for  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Administrators operate Astral across local dev, automated test runs, Railway staging, and production. When something looks wrong — stale deploy, wrong database, "did my push land?" — there is no at-a-glance signal in the UI today. This feature adds a read-only status strip at the bottom of the left navigation so admins immediately see which environment they are in, which commit the server is running, and how long that server process has been up. It reduces mistaken operations on the wrong deploy and speeds up deploy verification without opening Railway or shelling into the host.

## Functional scope

1. **Admin-only nav footer** — When the signed-in user is an administrator, a compact read-only status line appears pinned to the bottom of the left sidebar (below nav groups, above the content area). Non-admin users never see it on any route.
2. **Environment label** — Display exactly one of: `local`, `test`, `staging`, or `production`. The label reflects the running server's deployment context, not the browser hostname alone.
3. **Commit tip** — Display the git commit identifier for the code the server process is running (deploy tip). Shown as read-only text alongside the environment label.
4. **Server uptime** — Display how long the current server process has been running, in a compact human-readable duration. Format rules (from Susan's brief):
   * Sub-minute: `<1m`
   * Minutes only when under one hour: e.g. `5m`, `24m`
   * Hours and minutes when under one day: e.g. `1h15m`
   * Days, hours, and minutes when one day or more: e.g. `3d22h07m` (minutes zero-padded to two digits when days are shown)
5. **Server-sourced truth** — Environment, commit, and uptime values come from an authenticated API response; the frontend renders what the API returns and does not infer environment from the URL or build metadata alone.
6. **Non-interactive** — No links, buttons, copy actions, or tooltips required unless Susan adds them in a follow-up. Purely informational.

## Boundaries

* **Not for candidates or non-admin users** — Same gating as Admin nav visibility; footer hidden when `is_admin` is false.
* **Not a health dashboard** — Does not replace Performance Monitor, scheduler status, or `/health`; no batch/dispatch/DB metrics.
* **Not client-side uptime** — Measures server process uptime since boot/restart, not browser session length or time since login.
* **No secrets** — Must not expose env vars, API keys, internal URLs, or full Railway metadata blobs.
* **No frontend business logic duplication** — Environment resolution and uptime calculation live on the server per Interface project rules; the nav footer only displays resolved fields.
* **Authenticate/login screen** — Out of scope if the nav shell is not mounted; no standalone banner on unauthenticated pages.
* **Backend debug logging** — Out of scope (UI readout only; no `debug=` contract).

## Acceptance criteria

1. Sign in as an admin on local dev → bottom of left nav shows `local`, a commit identifier, and an uptime string in the compact format above.
2. Sign in as an admin on Railway staging → label reads `staging` with that deploy's commit tip and uptime.
3. Sign in as an admin on Railway production → label reads `production` with matching commit and uptime.
4. Sign in as a non-admin user on the same deploy → nav footer is absent; layout unchanged aside from missing footer.
5. Uptime strings match the format rules: `<1m` under one minute; minute-only under one hour; `XhYm` under one day; `XdYhZZm` at one day+ with two-digit minutes.
6. After a server restart/deploy, the displayed commit and uptime reflect the new process within one normal API refresh cycle (no stale pre-restart uptime persisting indefinitely).
7. Footer remains read-only: no user action changes environment, commit, or uptime display.

## Dependencies and blockers

none.

## Open questions

1. **Environment mapping** — Susan listed four labels (`local`, `test`, `staging`, `production`). What signal distinguishes `test` from `local` and from `staging`? (e.g. a named env var on Railway preview/CI, pytest harness only, or a dedicated Railway service?)
   1. Yes, let's name an env var for it, and fail gracefully if it isn't found (just show the tip SHA and uptime
2. **Commit display** — Short hash (e.g. 7 characters) or full 40-character SHA in the footer?
   1. Short hash display, tool tip with commit description.
3. **Uptime refresh** — Should the displayed uptime advance between server polls (client-side tick from last fetch), or only update when the API is re-fetched?
   1. Whatever you think is best.  I can see arguments for either case.

---

## Original brief

Recognize which environment is running (local/test/staging/production), the commit tip running and how long it has been (<1m, 5m, 24m, 1h15m, 3d22h07m) up.

### Comments

#### chuckles — 2026-06-15T00:08:59.073Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-653** | auto debug=true for UI AI calls when deploy env is local |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### susan — 2026-06-14T23:59:04.459Z
You reassigned this ticket to me before the child ticket was finished?

#### chuckles — 2026-06-14T23:56:58.759Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-640 (parent) | ftr/AST-640 |
| AST-646 | sub/AST-640/AST-646-deploy-status-api-and-admin-nav-footer |
| AST-651 | sub/AST-640/AST-651-uat-show-raw-astral-deploy-env-without-allowlist-validation |
| AST-653 | sub/AST-640/AST-653-uat-auto-debugtrue-for-ui-ai-calls-when-deploy-env-is-local |

**Epic worktree:** `astral-AST-640/`

— Chuckles

#### susan — 2026-06-14T23:55:05.838Z
Please add one little tweak here, that if the deploy environment is local, then all the UI generated AI calls are considered as Debug = true.  We are not getting enough output on what happens to the results of the content.

#### chuckles — 2026-06-14T23:23:39.600Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-651** | show raw ASTRAL_DEPLOY_ENV without allowlist validation |

Local `dev` merged via prep-uat. Re-run the **Manual test steps** from the latest prep-uat comment on this ticket; pay extra attention to the bugs above.

— Chuckles

#### chuckles — 2026-06-14T23:15:45.899Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-640 (parent) | ftr/AST-640 |
| AST-646 | sub/AST-640/AST-646-deploy-status-api-and-admin-nav-footer |
| AST-651 | sub/AST-640/AST-651-uat-show-raw-astral-deploy-env-without-allowlist-validation |

**Epic worktree:** `astral-AST-640/`

— Chuckles

#### susan — 2026-06-14T23:14:39.975Z
`Take out the data validation for the options there.  We may deploy on different continents, so just print the text for ASTRAL_DEPLOY_ENV if it's available.`

#### chuckles — 2026-06-14T21:17:39.494Z
[check-linear] blocked: merge conflict in `docs/ASTRAL_TEST_BIBLE.md` on AST-646 epic worktree — @Betty White

— Chuckles

#### chuckles — 2026-06-14T21:03:39.482Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-640 (parent) | ftr/AST-640 |
| AST-646 | sub/AST-640/AST-646-deploy-status-api-and-admin-nav-footer |

**Epic worktree:** `astral-AST-640/` — one active sub checked out at a time.

**Parent:** AST-640

— Chuckles

#### chuckles — 2026-06-14T19:05:46.689Z
@susan — three open questions before dispatch:

1. **Environment mapping** — What signal distinguishes `test` from `local` and from `staging`?
2. **Commit display** — Short hash (e.g. 7 chars) or full SHA in the footer?
3. **Uptime refresh** — Client-side tick between API polls, or update only on re-fetch?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
