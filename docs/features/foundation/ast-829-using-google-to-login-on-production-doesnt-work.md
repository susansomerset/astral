# AST-829 — Using Google to login on production doesn't work

<!-- linear-archive: AST-829 archived 2026-07-22 -->

## Linear archive (AST-829)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-829/using-google-to-login-on-production-doesnt-work  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan [still cannot sign in to production (**https://astral.up.railway.app**](<https://astral.up.railway.app>)) with Google OAuth. A first epic wave (**AST-830** SPA `/authenticate` handoff, **AST-831** backend live-project JWT validation) shipped to **origin/dev** and was finish-up'd, but production UAT is not closed — Susan sees Stytch **Login Error** and/or backend `session_not_found` in Railway logs. Stytch live-project **SessionsGet** succeeds for her user while the app does not reach an authenticated shell. This parent re-opens to define whatever product work remains to make production Google OAuth (and magic-link parity) actually work end-to-end after deploy — including ops/deploy verification, not only code.

## Functional scope

* **Production Google OAuth succeeds after deploy.** From [**https://astral.up.railway.app**](<https://astral.up.railway.app>), Google OAuth completes and lands Susan in the authenticated app — not Stytch **Login Error**, not Login bounce, not infinite "Completing sign-in…"[.](<https://astral.up.railway.app>)
* **Production** `/authenticate` **handoff works with live project.** When Stytch records a successful OAuth session, the SPA establishes a client session usable by the app (builds on **AST-830**; reopen only if UAT proves gap remains).
* **Production Bearer validation matches live project.** Fresh Google sign-in yields **200** on `GET /api/me`; no `session_not_found` for that session in server logs (builds on **AST-831**; reopen only if UAT proves gap remains).
* **Railway live-project env alignment verified.** Frontend build-time `VITE_STYTCH_PUBLIC_TOKEN` + `VITE_STYTCH_REDIRECT_URL=https://astral.up.railway.app/authenticate` and backend runtime `STYTCH_PROJECT_ID` + `STYTCH_SECRET` all reference **project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a** on the correct Railway services (build vs runtime). Susan can confirm from deploy logs/startup line without guesswork.
* **Stytch Dashboard live project configured.** Redirect URLs (Login + Sign-up), Authorized environments, and Google OAuth enabled on the **live** project per **AST-613** / `env.example`.
* **Magic link parity on production.** Email magic-link login still works under the same live configuration.
* **Admin behavior unchanged.** Susan retains admin nav/routes/candidate selector after Google OAuth per **AST-611** / **AST-612**.

## Boundaries

* Does **not** replace Stytch or redesign auth (**AST-609**–**613** architecture stands).
* Does **not** re-implement **AST-830** / **AST-831** unless UAT proves specific gaps — prefer **fix-uat** bug children over re-dispatching Done feature children.
* Does **not** change session duration, log-off screen (**AST-624** / **AST-625**), or add OAuth providers.
* Must **not** weaken Bearer validation.
* Does **not** regress local/staging test-project auth flows.

## Acceptance criteria

1. On [**https://astral.up.railway.app**](<https://astral.up.railway.app>) after a production deploy from current **origin/dev**, Google OAuth lands Susan in the authenticated app — not **Login Error** or Login.
2. Immediately after successful Google sign-in, `GET /api/me` returns **200** with correct `user_id`, `name`, and `is_admin`.
3. No `session_not_found` in server logs for that fresh production session.
4. Production startup log shows Stytch live project wiring (e.g. `Stytch auth configured: env=live project_id=project-live-d0218f6b-…`).
5. Email magic-link login on production still succeeds.
6. Non-admin Google sign-in still receives `is_admin: false` and cannot access admin routes.
7. Susan can verify Railway + Stytch Dashboard settings from documented checklist without ad-hoc debugging.

## Dependencies and blockers

* **AST-609**, **AST-610**, **AST-611**, **AST-612**, **AST-613** — auth foundation (Done).
* **AST-830**, **AST-831** — prior ship (Done); baseline on **origin/dev** — not assumed to satisfy AC until Susan confirms post-redeploy UAT.
* Susan / ops: Railway production deploy access, Stytch live Dashboard, ability to redeploy after dev lands.

## Open questions

1. After **finish-up(AST-829)**, did you redeploy [**https://astral.up.railway.app**](<https://astral.up.railway.app>) from latest **origin/dev**? Does Google login still fail today?
2. If still failing, is the UX still Stytch **Login Error**, or something different after redeploy?
3. Does the **current** production startup log include `Stytch auth configured: env=live project_id=project-live-d0218f6b-…`?
4. Are `VITE_STYTCH_PUBLIC_TOKEN` and `VITE_STYTCH_REDIRECT_URL` set on the Railway **frontend build** service (not only backend runtime)?
5. On the Stytch **live** project Dashboard: is Google OAuth enabled, and are redirect URL + authorized environment registered for [**https://astral.up.railway.app**](<https://astral.up.railway.app>)?

---

## Original brief

```
[{"message":"Mounting volume on: /var/lib/containers/railwayapp/bind-mounts/a2243f85-2d9d-4719-89ea-0465ed3fedd5/vol_j9l5s014vettb90c","severity":"info","attributes":{"level":"info"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:14.880184071Z"},{"message":"Starting Container","severity":"info","attributes":{"level":"info"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:15.811724139Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Starting gunicorn 26.0.0","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379466568Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379473165Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Using worker: sync","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379479016Z"},{"message":"[2026-06-26 18:51:15 +0000] [4] [INFO] Booting worker with pid: 4","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379484928Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379490025Z"},{"message":"repo_admin_json applied table=agent rows=6","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379496590Z"},{"message":"repo_admin_json applied table=agent_task rows=37","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379502151Z"},{"message":"Scheduler started — tick every 3min, max_auto_threads=3","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379509790Z"},{"message":"Bearer token validation failed: status_code=404 request_id='request-id-live-9bc1eb2b-c81e-4351-a662-ca64f5f31b1e' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-live-9bc1eb2b-c81e-4351-a662-ca64f5f31b1e', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T19:51:20.072133249Z"},{"message":"Bearer token validation failed: status_code=404 request_id='request-id-live-d6cd0610-f346-4178-830b-6ff59c5ea129' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-live-d6cd0610-f346-4178-830b-6ff59c5ea129', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T19:51:20.072136278Z"},{"message":"Bearer token validation failed: status_code=404 request_id='request-id-live-55017369-61a6-44d3-8e90-ca38671dddf1' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-live-55017369-61a6-44d3-8e90-ca38671dddf1', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T19:51:20.072139871Z"}]
```

Probably some environment variable needs setting, but I do have `STYTCH_PROJECT_ID`, `STYTCH_SECRET`, `VITE_STYTCH_PUBLIC_TOKEN`, and `VITE_STYTCH_REDIRECT_URL` set, all with prefixes of `project-live-…`

Is there a switch I need to flip on the stytch side?

### Comments

#### chuckles — 2026-06-27T21:01:28.991Z
[check-linear] Discussion — console read; redirect-error still Stytch allowlist/build (@susan)

**Noise (ignore):** `ad.doubleclick.net` CSP blocks — Stytch/GTM analytics on their pages, not Astral.

**Signal:** `redirect-error: Not signed in with the identity provider` — you are on Stytch's **redirect-error** page; OAuth redirect URL still not accepted **before** our `/authenticate` runs. One Tap / FedCM / GSI warnings are Stytch widget extras, not the root cause.

**Still verify:**
1. Railway **build** service: `VITE_STYTCH_REDIRECT_URL` (not STITCH) + `VITE_STYTCH_PUBLIC_TOKEN=public-token-live-…` → **full frontend rebuild**.
2. Stytch **Live** → Redirect URLs: **Login** + **Sign-up** both = `https://astral.up.railway.app/authenticate` (exact, no trailing slash).
3. Stytch **Live** → OAuth → Google: enabled; Google Cloud OAuth client linked per Stytch docs (authorized redirect URIs include Stytch callback URLs for **live** project).
4. **Isolate:** try **magic link** on production — if that works but Google fails, problem is OAuth/Dashboard only; if both fail, public token / redirect env still wrong in the SPA bundle.

Paste Network tab: first failed request URL after clicking Google (before redirect-error).

— Chuckles

#### susan — 2026-06-27T21:00:35.417Z
@chuckles

```
Here's the console output as text:

---

**[ERROR]** Connecting to 'https://ad.doubleclick.net/ccm/s/collect?auid=1302955977.1782592292&gtm=45He66o1h1v844823892za200zd844823892xea' violates the following Content Security Policy directive: "connect-src 'self' https://static.stytch.com https://*.hubspot.com https://*.hubapi.com https://forms.hscollectedforms.net https://forms.hsforms.com https://hubspot-forms-static-embed.s3.amazonaws.com https://unifyintent.com https://telemetry.stytch.com https://telemetry.staging.stytch.com https://login.stytch.com https://api.stytch.com https://www.google-analytics.com https://www.googletagmanager.com https://www.google.com https://*.google.com https://google.com/* https://*.google.com/* https://api.stripe.com https://webto.salesforce.com https://*.logs.datadoghq.com https://*.browser-intake-datadoghq.com https://web.stytch.com https://web.stytch.com https://accounts.google.com https://*.launchdarkly.com https://forms.hubspot.com https://api.chilipiper.com https://analytics.twitter.com https://*.reddit.com https://browser-intake-datadoghq.com https://stats.g.doubleclick.net https://analytics.google.com https://px.ads.linkedin.com wss://api.inkeep.com/graphql https://api.inkeep.com https://api.management.inkeep.com/graphql https://stytch.chilipiper.com https://*.sanity.io https://*.trustarc.com". The action has been blocked. `5417-2e8dad5e65f6c643.js:1`

**[ERROR]** Fetch API cannot load https://ad.doubleclick.net/ccm/s/collect?auid=1302955977.1782592292&gtm=45He66o1h1v844823892za200zd844823892xea. Refused to connect because it violates the document's Content Security Policy. `5417-2e8dad5e65f6c643.js:1`

**[WARNING]** [GSI_LOGGER]: Your client application uses one of the Google One Tap prompt UI status methods that may stop functioning when FedCM becomes mandatory. Refer to the migration guide to update your code accordingly and opt-in to FedCM to test your changes. Learn more: https://developers.google.com/identity/gsi/web/guides/fedcm-migration?s=dc#display_moment and https://developers.google.com/identity/gsi/web/guides/fedcm-migration?s=dc#skipped_moment `client:87`

**[ERROR]** Not signed in with the identity provider. `redirect-error:1`

**[ERROR]** [GSI_LOGGER]: FedCM get() rejects with NetworkError: Error retrieving a token. `5417-2e8dad5e65f6c643.js:4`

**[ERROR]** [Stytch] Unable to render One Tap prompt ▶ `{success: false, reason: 'unknown_reason'}` `5417-2e8dad5e65f6c643.js:4`
```

#### chuckles — 2026-06-27T20:58:53.935Z
[check-linear] Discussion — can't read Linear upload attachments headless (@susan)

I can't fetch the screenshot from this pass — please paste the **Console** text (or the red error line) inline.

While you grab that: on production Login → Google, check Console for `VITE_STYTCH_PUBLIC_TOKEN is not set`, Stytch `redirect`, or `public-token-test-` in the bundle (should be `public-token-live-`). Also confirm Railway build service has **`VITE_STYTCH_REDIRECT_URL`** (not STITCH) and trigger a full frontend rebuild after any rename.

— Chuckles

#### susan — 2026-06-27T20:57:36.283Z
Can you see this image:

![Screenshot 2026-06-27 at 1.56.57 PM.png](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/88528fd0-b720-43ae-ac7f-acaa25b44d9f/1c24f794-8464-47f1-90dc-c449cfdf7d2a)

This is the browser log, @chuckles

#### chuckles — 2026-06-27T20:43:58.323Z
[check-linear] Discussion — redirect-error likely Railway env typo (@susan)

Backend deploy **2026-06-27 20:29** looks correct: `Stytch auth configured: env=live project_id=project-live-d0218f6b-…` — AST-831 backend path is live.

**`stytch.com/redirect-error`** is Stytch rejecting the OAuth redirect URL **before** `/authenticate` runs — almost always **frontend build env**, not backend code.

**Likely culprit:** your comment names `VITE_STITCH_REDIRECT_URL` — code reads **`VITE_STYTCH_REDIRECT_URL`** (STYTCH not STITCH). If Railway has the typo, Vite never bakes the redirect URL. Also confirm **`VITE_STYTCH_PUBLIC_TOKEN`** = `public-token-live-…` on the **frontend build** service (same live project), not only backend runtime vars.

**Ops:**
1. Railway **build** service: fix var name → `VITE_STYTCH_REDIRECT_URL=https://astral.up.railway.app/authenticate` + live `VITE_STYTCH_PUBLIC_TOKEN`.
2. **Full frontend rebuild/redeploy** after fix (Vite embeds at build time).
3. DevTools → bundled JS should contain `public-token-live-` (not test).
4. Stytch **Live** Dashboard: **Login** + **Sign-up** redirect types both = `https://astral.up.railway.app/authenticate`; authorized environment = `https://astral.up.railway.app`; Google OAuth enabled.

If redirect-error persists after rebuild, paste the **exact browser URL** at failure.

— Chuckles

#### susan — 2026-06-27T20:42:38.358Z
```
[{"message":"Mounting volume on: /var/lib/containers/railwayapp/bind-mounts/4f1e56ad-bda9-4b74-b211-055cb82ab3a1/vol_j9l5s014vettb90c","severity":"info","attributes":{"level":"info"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:09.100594248Z"},{"message":"Starting Container","severity":"info","attributes":{"level":"info"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.066503353Z"},{"message":"[2026-06-27 20:29:09 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579588762Z"},{"message":"repo_admin_json applied table=agent rows=6","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579595863Z"},{"message":"[2026-06-27 20:29:09 +0000] [1] [INFO] Starting gunicorn 26.0.0","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579612045Z"},{"message":"[2026-06-27 20:29:09 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579646432Z"},{"message":"[2026-06-27 20:29:09 +0000] [1] [INFO] Using worker: sync","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579655049Z"},{"message":"[2026-06-27 20:29:09 +0000] [4] [INFO] Booting worker with pid: 4","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579658930Z"},{"message":"Stytch auth configured: env=live project_id=project-live-d0218f6b-c64a-4fa1-…","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.579662052Z"},{"message":"repo_admin_json applied table=agent_task rows=37","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.618919164Z"},{"message":"Scheduler started — tick every 3min, max_auto_threads=3","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"c23b6df3-4d2a-45c3-9b08-7ff6e071b166","replica":"4f1e56ad-bda9-4b74-b211-055cb82ab3a1"},"timestamp":"2026-06-27T20:29:10.637796495Z"}]
```

Had to restore this ticket to Discussion because it's still misbehaving in production, but I suspect it isn't a code issue.

Here's the deploy logs, which look fine, but now I'm getting directed to this url (same error) [https://stytch.com/redirect-error](<https://stytch.com/redirect-error>)

So, [`https://astral.up.railway.app/authenticate`](<https://astral.up.railway.app/authenticate>) is specified on Stytch for this environment.  I've confirmed [`https://astral.up.railway.app`](<https://astral.up.railway.app>) is the authorized domain for production on the stytch site.

The VITE_STITCH_REDIRECT_URL is set to [`https://astral.up.railway.app/authenticate`](<https://astral.up.railway.app/authenticate>) in production on railway.

What else could it be?  Just reply in this thread, in check-linear, please, @chuckles.

#### chuckles — 2026-06-27T20:38:44.671Z
@susan

1. After finish-up(AST-829), did you redeploy https://astral.up.railway.app from latest origin/dev? Does Google login still fail today?
2. If still failing, same Stytch Login Error UX, or different after redeploy?
3. Does current production startup log show `Stytch auth configured: env=live project_id=project-live-d0218f6b-…`?
4. Are `VITE_STYTCH_PUBLIC_TOKEN` and `VITE_STYTCH_REDIRECT_URL` on the Railway frontend **build** service (not only backend runtime)?
5. Stytch live Dashboard: Google OAuth enabled + redirect URL + authorized environment for https://astral.up.railway.app?

#### chuckles — 2026-06-27T19:45:50.745Z
[check-linear] User Testing — deployment logs confirm AST-831 symptom (@susan)

Yes — those `session_not_found` lines are the backend rejecting the Bearer JWT against the wrong/missing Stytch live session (AST-831). That deploy log is **2026-06-26**, before **prep-uat(AST-829)** landed on **origin/dev** (`e2a807f`).

**After you redeploy production from current dev:**
1. Startup log should include `Stytch auth configured: env=live project_id=project-live-d0218f6b-…` (AST-831).
2. Re-test Google OAuth — SPA handoff fix (AST-830) + remote JWT validation (AST-831) are both on dev now.
3. Still confirm Katherine's Stage 3 checklist on **AST-830** (Stytch live Dashboard redirect URLs + Railway `VITE_*` on the **build** service, `STYTCH_*` on **backend** runtime).

If login still fails after a fresh production deploy, paste the **new** startup line + first `session_not_found` (if any) with timestamp.

#### susan — 2026-06-27T19:36:13.608Z
@chuckles Katherine mentioned I should confirm the deployment logs, and I looked at the deployment from yesterday and likely found our culprit:

```
[{"message":"Mounting volume on: /var/lib/containers/railwayapp/bind-mounts/a2243f85-2d9d-4719-89ea-0465ed3fedd5/vol_j9l5s014vettb90c","severity":"info","attributes":{"level":"info"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:14.880184071Z"},{"message":"Starting Container","severity":"info","attributes":{"level":"info"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:15.811724139Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Starting gunicorn 26.0.0","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379466568Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379473165Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Using worker: sync","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379479016Z"},{"message":"[2026-06-26 18:51:15 +0000] [4] [INFO] Booting worker with pid: 4","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379484928Z"},{"message":"[2026-06-26 18:51:15 +0000] [1] [INFO] Control socket listening at /root/.gunicorn/gunicorn.ctl","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379490025Z"},{"message":"repo_admin_json applied table=agent rows=6","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379496590Z"},{"message":"repo_admin_json applied table=agent_task rows=37","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379502151Z"},{"message":"Scheduler started — tick every 3min, max_auto_threads=3","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T18:51:16.379509790Z"},{"message":"Bearer token validation failed: status_code=404 request_id='request-id-live-9bc1eb2b-c81e-4351-a662-ca64f5f31b1e' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-live-9bc1eb2b-c81e-4351-a662-ca64f5f31b1e', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T19:51:20.072133249Z"},{"message":"Bearer token validation failed: status_code=404 request_id='request-id-live-d6cd0610-f346-4178-830b-6ff59c5ea129' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-live-d6cd0610-f346-4178-830b-6ff59c5ea129', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T19:51:20.072136278Z"},{"message":"Bearer token validation failed: status_code=404 request_id='request-id-live-55017369-61a6-44d3-8e90-ca38671dddf1' error_type='session_not_found' error_message='Session could not be found.' error_url='https://stytch.com/docs/api/errors/404#session_not_found' original_json={'status_code': 404, 'request_id': 'request-id-live-55017369-61a6-44d3-8e90-ca38671dddf1', 'error_type': 'session_not_found', 'error_message': 'Session could not be found.', 'error_url': 'https://stytch.com/docs/api/errors/404#session_not_found'}","severity":"error","attributes":{"level":"error"},"tags":{"project":"4569b7ba-9cbf-45b0-8e4e-aa6872cd977e","environment":"2ce313de-780c-490c-ae5d-ecb7903fc215","service":"9a32040d-1b15-49d7-a215-0011851a5770","deployment":"56b958d6-4246-4502-abd6-a24b54cd5cfb","replica":"a2243f85-2d9d-4719-89ea-0465ed3fedd5"},"timestamp":"2026-06-26T19:51:20.072139871Z"}]
```

#### chuckles — 2026-06-27T19:14:55.403Z
[check-linear] Discussion — definition updated with production repro; open questions cleared (@susan)

#### susan — 2026-06-27T19:12:20.467Z
Answers:

1. 
   > # **Login Error**

   ## **There was an error logging you in. Please try again or contact support.**
2. [https://astral.up.railway.app/authenticate](<https://astral.up.railway.app/authenticate>)
3. Yes.  They've been set through several redeploys, but it hasn't worked yet (I didn't raise it because we were focused on other issues).

Here's the stytch activity log for my production user login:

```
{
  "@timestamp": "2026-06-27T19:10:26.062Z",
  "action": "SessionsGet",
  "event_id": "event-live-6e1f13a1-d1b6-4fba-a577-2baf8edbd07f",
  "http_status_code": 200,
  "project_id": "project-live-d0218f6b-c64a-4fa1-84fe-21997a66593a",
  "request_id": "request-id-live-15b36e59-40d8-4809-82d8-ba07af6ae19e",
  "status": "Success",
  "user_id": "user-live-a43b7723-6b61-4474-94d6-5b0d4a4f65e4"
}
```

#### chuckles — 2026-06-27T19:11:15.526Z
@susan

1. What exactly do you see in the browser when you click Google on production today — Stytch redirect URL error, stuck on "Completing sign-in…", bounce back to Login, or something else?
2. What is the canonical production public URL (hostname) for redirect allowlist verification?
3. After setting the live `VITE_*` vars on Railway, did a full redeploy/rebuild run so the frontend bundle picked up the new public token and redirect URL?

---

_Implementation detail may live in git history on `origin/dev`._
