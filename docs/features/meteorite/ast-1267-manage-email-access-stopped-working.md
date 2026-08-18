# AST-1267 — Manage Email access stopped working

<!-- linear-archive: AST-1267 archived 2026-08-17 -->

## Linear archive (AST-1267)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1267/manage-email-access-stopped-working  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Manage Email (and every other live caller of the shared Astral Gmail OAuth client) is failing on **both** local and Railway with Google `invalid_grant: Token has been expired or revoked`. Operators cannot list or open inbox mail, so meteorite intake from the admin surface is blocked. Repo survey of the last two days does **not** show a Manage Email / Gmail credential-path regression — the working hypothesis is Google OAuth **Testing**-mode refresh-token invalidation (short clock), landing ~seven days after the AST-1088 `gmail.modify` credential contract. This epic restores a working modify-capable refresh token on both hosts and decides whether to leave the client in Testing (another short cliff) or move it toward Production.

## Functional scope

* Restore authenticated **Manage Email** inbox list and message-body access for the configured Astral mailbox on **local and Railway** so operators can use the screen without `invalid_grant` / refresh failures.
* Keep **one** shared environ OAuth client for Gmail send, inbox read, archive, and trash — same modify-capable contract (`gmail.modify`) — installed in **both** environments (no host left on the revoked value).
* After restore, prove the shared token still supports monitor **send** and mailbox **archive/trash** (not only list/get).
* Capture the investigation outcome in the epic record: no product-code change is assumed required unless live verify after remint still fails for a reason other than credentials.
* Decide and execute the OAuth consent **publishing** posture (stay Testing vs move toward Production) so this does not silently recur on Google’s Testing refresh clock.

## Architectural definition

* **Patterns to reuse**
  * `pattern.layers.import-discipline` — Gmail I/O stays in external; core orchestrates; UI stays thin over admin inbox APIs.
  * `pattern.ui.admin-endpoint` — Manage Email remains an auth-gated admin surface; no new public Gmail routes.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.config.secrets-and-env-specific-from-environ` — `GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (optional `GOOGLE_TOKEN_URI`) remain environ-only; no secrets in config.
  * `astral.layers.core-vs-external-bright-line` — token refresh / Gmail API calls stay external.
  * `astral.layers.import-direction` — ui → core → external; no ui→external.
  * `astral.patterns.require-auth-on-protected-endpoints` — Manage Email / inbox admin APIs stay protected.
  * `astral.standards.in-scope-only` — no OAuth-reconnect product, IMAP/SMTP, CSE credential reuse, or Manage Email feature redesign unless Archie expands scope.
  * `universal` set for any product-code change on this epic (none expected for remint-only restore).

## Boundaries

* Does **not** treat this as a Manage Email UI / Land Meteorite / Create / gaze_email routing bug unless remint+verify proves otherwise. Adjacent gaze_email children ([AST-1088](https://linear.app/astralcareermatch/issue/AST-1088/gaze-email-config-null-candidate-dispatch-shell-gmail-archivetrash-add) / [AST-1089](https://linear.app/astralcareermatch/issue/AST-1089/ruth-little-brain-meteorite-email-parse-task-add-gaze-email-as-a) / [AST-1090](https://linear.app/astralcareermatch/issue/AST-1090/gaze-email-runner-bind-route-scrape-dedupe-create-mailbox-outcomes-add)) share the credential and stay on their own UAT track.
* Does **not** change CSE env vars (`GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ID`) or treat them as Gmail OAuth.
* Does **not** add in-app Google OAuth consent / reconnect UI in this epic.
* Does **not** permanently delete mail or broaden Gmail scopes beyond the existing modify-capable contract.
* Must not break monitor alert send once the reminted token is installed.
* Reminting / installing secrets and Google Cloud publishing-status changes are **ops** (Archie); engineers verify live paths after install.

## Acceptance criteria

1. An authenticated admin can open **Manage Email** on local **and** Railway and see the live inbox list without `invalid_grant` / refresh errors.
2. Clicking a listed message still opens that message’s HTML body (existing Manage Email behavior).
3. The same installed `GOOGLE_REFRESH_TOKEN` successfully performs monitor send and at least one mailbox mutate path (archive or trash) on both restored hosts.
4. Unauthenticated callers still cannot access Manage Email / inbox admin APIs.
5. Archie has an explicit publishing decision recorded (stay Testing vs move toward Production), and the reminted token matches that posture.

## Dependencies and blockers

* **Ops (blocking live restore):** Archie remints a `GOOGLE_REFRESH_TOKEN` whose granted scopes satisfy the product’s modify-capable Gmail client (`https://www.googleapis.com/auth/gmail.modify`) and installs it into **local and Railway** as `GOOGLE_REFRESH_TOKEN` (same `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`).
* **Remint cheat-sheet (URLs):**
  1. Consent / publishing + test users: [https://console.cloud.google.com/auth/audience](<https://console.cloud.google.com/auth/audience>) (or [https://console.cloud.google.com/apis/credentials/consent](<https://console.cloud.google.com/apis/credentials/consent>)) — confirm Testing vs Production; mailbox user must be a test user while Testing.
  2. OAuth client id/secret + redirect: [https://console.cloud.google.com/apis/credentials](<https://console.cloud.google.com/apis/credentials>) — open the **Web** OAuth client already backing Astral; add authorized redirect URI `https://developers.google.com/oauthplayground` (required for Playground remint).
  3. Gmail API enabled: [https://console.cloud.google.com/apis/library/gmail.googleapis.com](<https://console.cloud.google.com/apis/library/gmail.googleapis.com>)
  4. Mint refresh token: [https://developers.google.com/oauthplayground/](<https://developers.google.com/oauthplayground/>) — gear → **Use your own OAuth credentials** (paste that client id/secret; do **not** use Playground defaults or the token dies in ~24h) → authorize scope `https://www.googleapis.com/auth/gmail.modify` while signed in as the Astral mailbox (`GMAIL_USER`) → **Exchange authorization code for tokens** → copy **Refresh token** into local + Railway `GOOGLE_REFRESH_TOKEN`.
  5. Optional revoke old grants: [https://myaccount.google.com/permissions](<https://myaccount.google.com/permissions>) (as the mailbox Google account).
* **Investigation already done (not a blocker):** On `origin/dev`, `src/external/gmail.py` last changed **2026-07-31** (`gmail.modify` sole scope — AST-1088). No Manage Email / inbox API / `gmail.py` credential-path commits in the last two days. The only recent `gaze_email` touch (AST-1213, 2026-08-06) is Ruth live payload text/links — not OAuth refresh. Archie confirmed: no recent client-secret rotation, password change, or app-access revoke; OAuth client is still **Testing** (and shows active).
* **Adjacent:** gaze_email UT siblings share this credential — restore unblocks their live UAT; they do not own remint.

## Open questions

1. Remint only and stay on **Testing** (accept another short refresh-token cliff), or remint **and** move the OAuth client toward **Production** (may imply Google verification for sensitive Gmail scopes)?

## Proposed child tickets

#### 1: **Remint install verify — shared Gmail credential - Ada**

After Archie remints/installs a modify-capable `GOOGLE_REFRESH_TOKEN` on local and Railway (and answers publishing posture in Open question 1): prove Manage Email list/get works on both hosts; prove shared send + archive/trash succeed on the same token. If verify still fails after a good remint for a non-credential reason, file the product defect from that evidence — do not invent a Manage Email redesign up front. Does **not** own Google Cloud consent clicks or publishing-status changes (ops).
**Citations:** `pattern.layers.import-discipline`; `pattern.ui.admin-endpoint`; `astral.config.secrets-and-env-specific-from-environ`; `astral.layers.core-vs-external-bright-line`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope is one restore/verify slice across two hosts plus an ops publishing decision — single child is intentional; no second engineer ticket until verify proves a code defect.

---

## Original brief

('invalid_grant: Token has been expired or revoked.', {'error': 'invalid_grant', 'error_description': 'Token has been expired or revoked.'})

The token isn't old enough to expire.

### Comments

#### chuckles — 2026-08-07T23:04:56.462Z
@susan

Remint lives in **OAuth Playground** with **your** Cloud OAuth client — not a magic “Remint” button in Cloud Console. Cheat-sheet is also under **Dependencies** on the Description.

1. Consent / Testing vs Production + test users: https://console.cloud.google.com/auth/audience (alt: https://console.cloud.google.com/apis/credentials/consent)
2. OAuth client id/secret + add redirect `https://developers.google.com/oauthplayground`: https://console.cloud.google.com/apis/credentials
3. Gmail API on: https://console.cloud.google.com/apis/library/gmail.googleapis.com
4. Mint token: https://developers.google.com/oauthplayground/ — gear → **Use your own OAuth credentials** → scope `https://www.googleapis.com/auth/gmail.modify` → sign in as `GMAIL_USER` → Exchange → copy **Refresh token** into local + Railway `GOOGLE_REFRESH_TOKEN`
5. Optional revoke old app access: https://myaccount.google.com/permissions

Still open: remint and stay **Testing**, or remint **and** move toward **Production**?

— Chuckles

#### susan — 2026-08-07T23:03:01.416Z
I hate the google interface.  Where can I actually remint?  URLs please.

#### chuckles — 2026-08-07T22:58:55.351Z
@susan

Code survey (last two days / Manage Email + Gmail credential path): no OAuth regression found — `gmail.py` last changed 2026-07-31 (`gmail.modify`); only recent `gaze_email` touch is AST-1213 Ruth payload text/links. Both hosts failing + Testing consent + ~7 days since that contract points at Google’s Testing refresh-token clock, not a Manage Email code change. Definition updated with that finding.

1. Remint only and stay **Testing**, or remint **and** move toward **Production** (may imply Google verification for sensitive Gmail scopes)?

— Chuckles

#### chuckles — 2026-08-07T22:43:12.470Z
@susan

1. Which host(s) show the failure — local only, Railway staging only, or both?
2. In Google Cloud Console, is the OAuth client still on **Testing** publishing status?
3. Was the OAuth client secret rotated, the Astral Google account password / security settings changed, or app access revoked recently?
4. Product scope: **(A)** ops remint + install + verify only, or **(B)** also clearer Manage Email / API messaging when refresh is dead?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
