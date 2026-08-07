# AST-1255 — Extension auth session path

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1255/extension-auth-session-path-extension-shell-manifest-v3  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1170/extension-shell-manifest-v3-scaffold-and-authenticated-single-page  

**Publish ref (origin):** `sub/AST-1170/AST-1255-extension-auth-session-path`  
**Parent integration ref:** `ftr/AST-1170-extension-shell-manifest-v3-scaffold-and-authenticated-single-page-capture`

Wires the **AST-1167** decision (extension-owned Stytch B2C on the same project; Bearer JWT from background storage; no backend CORS/cookie deltas) into the **AST-1254** WXT shell so every Astral network call from the extension carries a valid session — or the candidate gets a clear sign-in path when the session is absent/expired. Does **not** own icon-click page capture, shadow-root toast, or `page_intake` POST (**AST-1256**). Does **not** change the web app login flow.

⚠️ **Decision — consume AST-1167 as written (no re-litigation):** Extension-owned Stytch B2C; `session_jwt` → `browser.storage.session`; `session_token` → `browser.storage.local`; refresh via Stytch `sessions.authenticate`; on refresh failure clear tokens and open sign-in; Bearer on every Astral call; **no** cookie/CORS/backend changes.

⚠️ **Decision — sign-in surface is an extension page (not toast, not `default_popup`):** Toast is **AST-1256**. A persistent `action.default_popup` would swallow `action.onClicked` and block capture. This ticket opens a **WXT unlisted page** (`sign-in.html`) in a new tab when the icon is clicked and no valid session exists. That page hosts Stytch UI + short copy telling the candidate to sign in. When a session **does** exist, icon click is a no-op for capture (AST-1256 fills that branch).

⚠️ **Decision — background owns Astral HTTP; sign-in page owns Stytch UI only:** `astralFetch` / token refresh live in `src/lib/` and run from the background context. The sign-in page may call Stytch SDK APIs (same-extension origin / Stytch hosts) to mint a session, then writes tokens into `browser.storage.*` for the background to read. No content script issues any cross-origin request (AC7).

⚠️ **Decision — build-time public env only (no secrets in the bundle):** `WXT_STYTCH_PUBLIC_TOKEN` and `WXT_ASTRAL_API_BASE` via WXT/`import.meta.env` (same role as frontend `VITE_STYTCH_PUBLIC_TOKEN`). Document in `env.example` + extension README. Never commit tokens or bake `STYTCH_SECRET`.

⚠️ **Decision — permissions this ticket adds:** `storage` + `host_permissions` for the Astral API origin and Stytch API hosts required by `@stytch/vanilla-js`. Do **not** add `scripting` / `activeTab` / `tabs` beyond what opening a tab needs — use `browser.tabs.create` which requires the `tabs` permission **or** open via `browser.runtime.getURL` + `browser.tabs.create` (Chrome allows `tabs.create` to extension pages without `tabs` permission). Prefer **no `tabs` permission**: `browser.tabs.create({ url: browser.runtime.getURL('/sign-in.html') })` works without declaring `tabs`. Leave `alarms` for later.

⚠️ **Decision — no Python / Flask / web-app edits:** Backend already accepts Bearer (`src/ui/auth.py`). Frontend login stays untouched. Engineer does **not** edit `tests/` or `docs/test-bible/**` — Betty revises the AST-1254 scaffold assertions that currently forbid `storage` / `host_permissions` after Code Complete.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/extension/package.json` | Add runtime dep `@stytch/vanilla-js` (pin compatible with frontend `^19` line — install current `19.x` and lock) | ui |
| `src/ui/extension/package-lock.json` | Lockfile after `npm install` | ui |
| `src/ui/extension/wxt.config.ts` | Add `permissions: ['storage']`; `host_permissions` from `WXT_ASTRAL_API_BASE` + Stytch hosts | ui |
| `src/ui/extension/src/lib/extensionConfig.ts` | Read `WXT_STYTCH_PUBLIC_TOKEN` + `WXT_ASTRAL_API_BASE`; throw/log clearly when missing | ui |
| `src/ui/extension/src/lib/sessionTokens.ts` | Get/set/clear `session_jwt` (storage.session) + `session_token` (storage.local); fixed key strings | ui |
| `src/ui/extension/src/lib/sessionRefresh.ts` | Headless Stytch `sessions.authenticate` using stored `session_token`; update both tokens or clear on failure | ui |
| `src/ui/extension/src/lib/astralFetch.ts` | Background Astral `fetch` with Bearer; one refresh retry on 401; exports `astralGetJson` / `astralPutJson` matching sibling injected-fetch shape | ui |
| `src/ui/extension/src/lib/ensureSession.ts` | `ensureSession(): Promise<EnsureSessionResult>` — valid jwt / refresh / `sign_in_required` with fixed candidate-facing copy constant | ui |
| `src/ui/extension/src/entrypoints/background.ts` | Wire `browser.action.onClicked`: `ensureSession`; if `sign_in_required` → open sign-in page; if ok → no-op (capture = AST-1256) | ui |
| `src/ui/extension/src/entrypoints/sign-in.html` + `sign-in.ts` (WXT unlisted / html entry) | Plain DOM + `@stytch/vanilla-js` `StytchUIClient` login; on session → persist tokens via `sessionTokens`; short “Sign in to Astral Surfer” copy | ui |
| `src/ui/extension/README.md` | Env vars, Stytch Dashboard allowlist for `chrome-extension://<id>/sign-in.html`, load-unpacked auth smoke | ui |
| `env.example` | Document `WXT_STYTCH_PUBLIC_TOKEN` + `WXT_ASTRAL_API_BASE` for the extension package | docs |
| `src/ui/extension/src/vite-env.d.ts` (or ambient) | Type `ImportMetaEnv` for the two `WXT_*` keys | ui |

**No changes expected:** `src/ui/auth.py`, `src/ui/frontend/**`, `src/ui/server.py`, `src/utils/config.py` (Python), existing `src/ui/extension/src/lib/surfer*.ts` / `dwell.ts` / `fanOut.ts` / `pacingConfig.ts` (callers pass `astralGetJson` later), `tests/**`, bible.

---

## Stage 1: Config, tokens, authenticated fetch

**Done when:** `extensionConfig`, `sessionTokens`, `sessionRefresh`, and `astralFetch` modules exist; unit-testable pure storage helpers use injectable `browser.storage` seams (or WXT `browser` with Vitest-friendly exports); `astralGetJson` attaches `Authorization: Bearer <jwt>` to `${apiBase}${path}`; missing env fails loudly at module read; no background wiring yet.

1. Add `@stytch/vanilla-js` to `src/ui/extension/package.json` `dependencies` (not `devDependencies`). Run `npm install` in `src/ui/extension/` and commit the lockfile. Prefer the same major as `src/ui/frontend` (`@stytch/react` ^19 → vanilla-js 19.x).

2. Create `src/ui/extension/src/lib/extensionConfig.ts`:

```ts
export function getStytchPublicToken(): string
export function getAstralApiBase(): string  // no trailing slash
```

- Read `import.meta.env.WXT_STYTCH_PUBLIC_TOKEN` and `import.meta.env.WXT_ASTRAL_API_BASE`.
- Trim; strip one trailing `/` from the API base.
- If either is empty: `console.error` a one-line message naming the missing var; `getAstralApiBase` / `getStytchPublicToken` throw `Error` with that same message when called (fail closed — no silent empty Bearer).

3. Create `src/ui/extension/src/lib/sessionTokens.ts` with fixed keys:

| Storage | Key | Value |
|---------|-----|-------|
| `browser.storage.session` | `astral_session_jwt` | string JWT |
| `browser.storage.local` | `astral_session_token` | string opaque session_token |

Exports (all async):

- `getSessionJwt(): Promise<string | null>`
- `getSessionToken(): Promise<string | null>`
- `setSessionTokens(jwt: string, sessionToken: string): Promise<void>` — writes both areas
- `clearSessionTokens(): Promise<void>` — removes both keys

Use WXT `browser` from `wxt/browser` (promise API). Do not use `chrome.*` callbacks.

4. Create `src/ui/extension/src/lib/sessionRefresh.ts`:

- `refreshSessionTokens(): Promise<boolean>` — if no `session_token`, return `false`. Else construct `@stytch/vanilla-js/headless` `StytchClient` with `getStytchPublicToken()`, call `sessions.authenticate({ session_token, session_duration_minutes: 60 })` (or the SDK’s equivalent that returns fresh `session_jwt` + `session_token`). On success `setSessionTokens`; on failure `clearSessionTokens` and return `false`.

⚠️ **Decision — headless client in refresh only:** Background / refresh path must not mount Stytch UI. Login UI uses `StytchUIClient` on the sign-in page (Stage 2).

5. Create `src/ui/extension/src/lib/astralFetch.ts`:

- `astralFetch(path: string, init?: RequestInit): Promise<Response>` — resolves URL as `${getAstralApiBase()}${path.startsWith('/') ? path : '/' + path}`; clones headers; sets `Authorization: Bearer ${jwt}` when jwt present; `credentials: 'omit'` (Bearer only — no cookies).
- Before the first attempt: if no jwt, try `refreshSessionTokens()` once; if still no jwt, return a synthetic-like path — actually **throw** or return a Response? Prefer: call `ensureSession` from callers for gate; `astralFetch` assumes caller wants a network attempt — if still no jwt after refresh, throw `Error('sign_in_required')` with that exact message string so callers can branch.
- On HTTP 401: one `refreshSessionTokens()` + retry with the new jwt; if refresh fails or second response is 401, `clearSessionTokens` and throw `Error('sign_in_required')`.
- `astralGetJson<T>(path: string): Promise<T>` — `astralFetch` GET, `res.json()`, throw on non-OK with status in message.
- `astralPutJson<T>(path: string, body: unknown): Promise<T>` — PUT JSON body, same error rules.

These two helpers are the injection surface siblings already expect (`fetchPacingConfig(getJson)`, `fetchSurferConsent(..., getJson)`).

6. Create `src/ui/extension/src/lib/ensureSession.ts`:

```ts
export const SIGN_IN_COPY =
  'Sign in to Astral Surfer to capture pages. Use the sign-in tab that just opened — same Astral account as the website.'

export type EnsureSessionResult =
  | { ok: true; jwt: string }
  | { ok: false; reason: 'sign_in_required'; message: typeof SIGN_IN_COPY }

export async function ensureSession(): Promise<EnsureSessionResult>
```

Algorithm: read jwt → if present return ok; else refresh → if jwt present return ok; else return `{ ok: false, reason: 'sign_in_required', message: SIGN_IN_COPY }`.

**Ritual:** `code(AST-1255): session tokens + astral Bearer fetch`

---

## Stage 2: Sign-in page + background icon path

**Done when:** Icon click with no session opens the extension sign-in page showing Stytch login + `SIGN_IN_COPY` (or equivalent visible heading); completing Stytch login persists both tokens; a subsequent `ensureSession()` returns `ok: true`; with a stored jwt, icon click does not open sign-in and does not capture; `npm run build` and `npm run build:firefox` succeed; README + `env.example` document env + Dashboard allowlist; no content-script network code added.

1. Update `wxt.config.ts` `manifest`:

```ts
permissions: ['storage'],
host_permissions: [
  // Built from env at config-eval time — fail the build if WXT_ASTRAL_API_BASE unset
  `${apiBase}/*`,
  'https://*.stytch.com/*',
  'https://api.stytch.com/*',
],
```

Resolve `apiBase` via `process.env.WXT_ASTRAL_API_BASE` (trim, no trailing slash) inside `wxt.config.ts`. If missing during `wxt build`, throw so the unpacked build cannot ship a silent empty host list. Keep existing `key` + gecko id. Do **not** set `action.default_popup`.

2. Add WXT HTML entrypoint for sign-in (file names per WXT 0.21 unlisted/html convention — use `src/entrypoints/sign-in.html` paired with `sign-in.ts` if that is the framework’s documented pattern for this version; if WXT requires `sign-in/index.html`, use that — **do not** invent a second HTML router). Page contents:

- Heading: `Sign in to Astral Surfer`
- One short paragraph: the `SIGN_IN_COPY` string (or the same words without the “tab that just opened” clause — use: `Sign in with your Astral account to capture job pages. This is the same login as the Astral website.`)
- Mount `StytchUIClient` / Stytch login UI (`Products.emailMagicLinks` + OAuth Google if the web app Login enables them — mirror `src/ui/frontend/src/pages/Login.tsx` product list only; do not invent new auth products).
- Redirect/complete URL for Stytch: `browser.runtime.getURL('/sign-in.html')` (exact string must be allowlisted in Stytch Dashboard — document in README).
- On authenticated session (Stytch session present): read `session_jwt` + `session_token` from the client (`getTokens()` or equivalent), call `setSessionTokens`, show a one-line “You’re signed in — you can close this tab.” Do **not** call Astral APIs from this page for the happy path (background owns Astral HTTP). Optional: `GET ${apiBase}/api/me` **must not** be added here — keep AC7 / background-only Astral calls strict; prove Bearer in a later manual smoke from background if needed.

3. Replace `src/ui/extension/src/entrypoints/background.ts` body:

```ts
import { defineBackground } from 'wxt/utils/define-background';
import { browser } from 'wxt/browser';
import { ensureSession } from '../lib/ensureSession';

export default defineBackground(() => {
  browser.action.onClicked.addListener(async () => {
    const session = await ensureSession();
    if (session.ok) {
      // Capture + toast: AST-1256
      return;
    }
    await browser.tabs.create({
      url: browser.runtime.getURL('/sign-in.html'),
    });
  });
});
```

No `fetch(` to Astral in this file beyond what `ensureSession` → refresh may do against **Stytch** (not Astral). Do not add content-script entrypoints.

4. Ambient types: add `src/ui/extension/src/vite-env.d.ts` (or extend existing) declaring `WXT_STYTCH_PUBLIC_TOKEN` and `WXT_ASTRAL_API_BASE` on `ImportMetaEnv`.

5. `env.example` — after the existing `VITE_STYTCH_*` block, add:

```bash
# Astral Surfer extension (WXT build — src/ui/extension/)
# Same Stytch project as the web app. Public token only.
WXT_STYTCH_PUBLIC_TOKEN=public-token-test-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Astral API origin the background will call (no trailing slash). Local Flask:
WXT_ASTRAL_API_BASE=http://localhost:5001
# Staging proof host (AST-1167): https://astral-staging.up.railway.app
```

6. Update `src/ui/extension/README.md`:

- Required env vars for build/dev.
- Stytch Dashboard: add Redirect URL (Login + Sign-up) for `chrome-extension://<stable-id>/sign-in.html` (stable id from pinned `manifest.key` — document how to read the id from `chrome://extensions` after first load-unpacked).
- Authorized environment / origin for the extension id if Stytch requires it.
- Manual smoke: load unpacked → click icon with empty storage → sign-in tab opens → complete login → click icon again → no sign-in tab (session present). Capture still absent until AST-1256.

7. Build gate (builder runs locally):

```bash
cd src/ui/extension
# export WXT_* first
npm run build
npm run build:firefox
```

Both must exit 0. Confirm `.output/chrome-mv3/manifest.json` lists `storage` and the expected `host_permissions`.

**Ritual:** `code(AST-1255): sign-in page + icon session gate`

---

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- When the codebase has drifted from what the plan assumes — **stops and comments.**
- Completes a stage on the epic worktree, commits, publishes to `origin/sub/AST-1170/AST-1255-extension-auth-session-path`.

Blocking comment format (parent AST-1170):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** Single-Component — extension client only (`src/ui/extension/**` + `env.example` + README); no Python, no SPA, no tests/bible.

**Conf:** high — AST-1167 decision is Done and explicit; AST-1254 shell + empty background are in place; Bearer path already exists in `src/ui/auth.py`; sibling libs already expect an injected authenticated `getJson`.

**Risk:** Medium — wrong token home or a `default_popup` would break AST-1256’s icon-click capture; Stytch Dashboard allowlist for `chrome-extension://` redirects is an ops dependency for magic-link/OAuth UAT (documented, not code). A bug in refresh/clear could strand the candidate without a sign-in path.

---

## Rules check (§8)

| Rule | Plan stance |
|------|-------------|
| §1.3 DRY | Single token module + single `astralFetch`; siblings keep injected-fetch pattern |
| §2.1 / secrets-from-environ | Public token + API base from `WXT_*` env; no secrets in repo |
| §2.4 batch | N/A — no Python batch work |
| §2.6 state machine | N/A |
| §2.9 require-auth | Honored client-side via Bearer; no anonymous Astral posts |
| §3.3 imports | TS client — outside Python import table (AST-1254) |
| §3.5 naming / extension layout | Libs under `src/lib/`; entrypoints under `src/entrypoints/`; plain DOM sign-in (no React) |
| Engineer test-tree ban | No `tests/` or bible edits; note Betty must relax AST-1254 scaffold asserts on `storage` / `host_permissions` |
