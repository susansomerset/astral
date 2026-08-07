# AST-1255 — Extension auth session path

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1255/extension-auth-session-path-extension-shell-manifest-v3  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1170/extension-shell-manifest-v3-scaffold-and-authenticated-single-page  

**Publish ref (origin):** `sub/AST-1170/AST-1255-extension-auth-session-path`  
**Parent integration ref:** `ftr/AST-1170-extension-shell-manifest-v3-scaffold-and-authenticated-single-page-capture`

Wires the **AST-1167** decision (extension-owned Stytch B2C on the same project; Bearer JWT from background storage; no backend CORS/cookie deltas) into the **AST-1254** WXT shell so every Astral network call from the extension carries a valid session — or the candidate gets a clear sign-in path when the session is absent/expired. Does **not** own icon-click page capture, shadow-root toast, or `page_intake` POST (**AST-1256**). Does **not** change the web app login flow.

⚠️ **Decision — consume AST-1167 as written (no re-litigation):** Extension-owned Stytch B2C; `session_jwt` → `browser.storage.session`; `session_token` → `browser.storage.local`; refresh via Stytch `session.authenticate` after hydrate; on refresh failure clear tokens and open sign-in; Bearer on every Astral call; **no** cookie/CORS/backend changes.

⚠️ **Decision — sign-in surface is an extension page (not toast, not `default_popup`):** Toast is **AST-1256**. A persistent `action.default_popup` would swallow `action.onClicked` and block capture. This ticket opens a **WXT HTML entrypoint** at `src/entrypoints/sign-in.html` in a new tab when the icon is clicked and no valid session exists. That page hosts Stytch UI + short copy telling the candidate to sign in. When a session **does** exist, icon click is a no-op for capture (AST-1256 fills that branch).

⚠️ **Decision — Stytch SDK only in DOM contexts; Astral HTTP only in background:** `@stytch/vanilla-js` (`StytchHeadlessClient` / `StytchUIClient`) calls `checkNotSSR` and throws when `window` is undefined — an MV3 service worker has no `window`, so the SDK **must not** be constructed in `defineBackground`. Sign-in page (login UI) and an **offscreen document** (token refresh) are the only places that construct the SDK. Background owns every **Astral** `fetch` (`astralFetch`) and orchestrates refresh by messaging the offscreen document. No content script issues any cross-origin request (AC7). Parent “background owns every network call” is satisfied for **Astral** traffic; Stytch SDK calls from extension pages / offscreen are allowed (extension origin, not a content script).

⚠️ **Decision — refresh home = offscreen document (Joan option 1):** Rejected hand-rolled Stytch REST (unsupported) and backend `session_token` Bearer (contradicts AST-1167 “backend deltas: none” + this ticket’s exclusion of `src/ui/auth.py`). Add manifest permission `offscreen`. Background ensures one offscreen document exists, messages it to hydrate + `session.authenticate`, receives fresh tokens, writes them via `sessionTokens`. Consent epic (**AST-1173**) will need to disclose `offscreen` — note that in README; do not invent consent UI here.

⚠️ **Decision — bare `action: {}` required for `onClicked`:** AST-1254 ships no `action` key. Chrome / WXT require `action: {}` in the manifest to use `browser.action.onClicked` without a popup. Omitting it throws at background top level and disables the extension. Do **not** set `default_popup` or `default_icon` unless already present from AST-1254.

⚠️ **Decision — build-time public env only (no secrets in the bundle):** `WXT_STYTCH_PUBLIC_TOKEN` and `WXT_ASTRAL_API_BASE` via WXT/`import.meta.env` (same role as frontend `VITE_STYTCH_PUBLIC_TOKEN`). Document in `env.example` + extension README. Never commit tokens or bake `STYTCH_SECRET`.

⚠️ **Decision — permissions this ticket adds:** `storage`, `offscreen`, and `host_permissions` for `${WXT_ASTRAL_API_BASE}/*` and `https://*.stytch.com/*` only (do **not** also list `https://api.stytch.com/*` — covered by the wildcard). Prefer **no `tabs` permission**: `browser.tabs.create({ url: browser.runtime.getURL('/sign-in.html') })` works without declaring `tabs`. Leave `scripting` / `activeTab` / `alarms` for later.

⚠️ **Decision — `SIGN_IN_COPY` is client-invented and allowed:** Parent “server-supplied messaging” / AC7 apply to **intake outcomes**. Parent AC6 (no-session sign-in guidance) has no authenticated intake response to quote — the missing session *is* the problem — so one fixed client string is required. Do not invent additional candidate-facing strings beyond `SIGN_IN_COPY` and the signed-in confirmation line in Stage 2.

⚠️ **Decision — no Python / Flask / web-app edits:** Backend already accepts Bearer JWT (`src/ui/auth.py` → `authenticate_session_jwt`). Frontend login stays untouched. Engineer does **not** edit `tests/` or `docs/test-bible/**`. After Code Complete, Betty owns first extension Vitest coverage and must **not** re-assert the empty-shell ban on `storage` / `host_permissions` / `offscreen` / `action` (AST-1254 scaffold tests that forbid those were product of the empty shell; auth ticket supersedes them).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/extension/package.json` | Add runtime dep `@stytch/vanilla-js` (19.x, same major as frontend `@stytch/react` ^19) | ui |
| `src/ui/extension/package-lock.json` | Lockfile after `npm install` | ui |
| `src/ui/extension/wxt.config.ts` | `action: {}`; `permissions: ['storage', 'offscreen']`; `host_permissions` from env + `https://*.stytch.com/*` | ui |
| `src/ui/extension/src/lib/extensionConfig.ts` | Read `WXT_STYTCH_PUBLIC_TOKEN` + `WXT_ASTRAL_API_BASE`; throw when missing | ui |
| `src/ui/extension/src/lib/sessionTokens.ts` | Get/set/clear jwt (storage.session) + session_token (storage.local) | ui |
| `src/ui/extension/src/lib/sessionRefresh.ts` | Ensure offscreen doc; message it to refresh; write tokens or clear on failure | ui |
| `src/ui/extension/src/lib/astralFetch.ts` | Background Astral `fetch` with Bearer; one refresh retry on 401; `astralGetJson` / `astralPutJson` | ui |
| `src/ui/extension/src/lib/ensureSession.ts` | `ensureSession()` + `SIGN_IN_COPY` constant | ui |
| `src/ui/extension/src/entrypoints/offscreen.html` (+ co-located script) | DOM context: construct `StytchHeadlessClient`, hydrate, `session.authenticate`, reply with tokens | ui |
| `src/ui/extension/src/entrypoints/background.ts` | `action.onClicked` → `ensureSession` → open sign-in or no-op | ui |
| `src/ui/extension/src/entrypoints/sign-in.html` (+ co-located script) | Plain DOM + `StytchUIClient` login; persist tokens via `getTokens()` + `setSessionTokens` | ui |
| `src/ui/extension/README.md` | Env vars, Dashboard allowlist, offscreen permission note, load-unpacked auth smoke | ui |
| `env.example` | Document `WXT_STYTCH_PUBLIC_TOKEN` + `WXT_ASTRAL_API_BASE` | docs |
| `src/ui/extension/src/vite-env.d.ts` | `ImportMetaEnv` for the two `WXT_*` keys | ui |

**No changes expected:** `src/ui/auth.py`, `src/ui/frontend/**`, `src/ui/server.py`, `src/utils/config.py` (Python), existing `src/ui/extension/src/lib/surfer*.ts` / `dwell.ts` / `fanOut.ts` / `pacingConfig.ts`, `tests/**`, bible.

---

## Stage 1: Config, tokens, offscreen refresh, authenticated fetch

**Done when:** `extensionConfig`, `sessionTokens`, `sessionRefresh` (offscreen-backed), offscreen entrypoint, and `astralFetch` exist; `astralGetJson` attaches `Authorization: Bearer <jwt>`; missing env throws; no icon-click / sign-in page yet.

1. Add `@stytch/vanilla-js` to `src/ui/extension/package.json` `dependencies`. Run `npm install` in `src/ui/extension/` and commit the lockfile. Pin 19.x (frontend `@stytch/react` is `^19.0.0`).

2. Create `src/ui/extension/src/lib/extensionConfig.ts`:

```ts
export function getStytchPublicToken(): string
export function getAstralApiBase(): string  // no trailing slash
```

- Read `import.meta.env.WXT_STYTCH_PUBLIC_TOKEN` and `import.meta.env.WXT_ASTRAL_API_BASE`.
- Trim; strip one trailing `/` from the API base.
- If either is empty: `console.error` naming the missing var; the getter throws `Error` with that same message (fail closed).

3. Create `src/ui/extension/src/lib/sessionTokens.ts` with fixed keys:

| Storage | Key | Value |
|---------|-----|-------|
| `browser.storage.session` | `astral_session_jwt` | string JWT |
| `browser.storage.local` | `astral_session_token` | string opaque session_token |

Exports (all async, WXT `browser` from `wxt/browser` — no `chrome.*` callbacks):

- `getSessionJwt(): Promise<string | null>`
- `getSessionToken(): Promise<string | null>`
- `setSessionTokens(jwt: string, sessionToken: string): Promise<void>`
- `clearSessionTokens(): Promise<void>`

4. Create `src/ui/extension/src/entrypoints/offscreen.html` (WXT HTML entrypoint; co-located `.ts` if WXT pairs script that way for this version — one HTML entry named `offscreen`, no second router). On load, register `browser.runtime.onMessage` handler for message type exactly `astral_stytch_refresh`:

```ts
// Pseudocode — implement literally this sequence:
import { StytchHeadlessClient } from '@stytch/vanilla-js/headless'
import { getStytchPublicToken } from '../lib/extensionConfig'

const SESSION_DURATION_MINUTES = 60  // named constant; min SDK value is 5

// payload: { type: 'astral_stytch_refresh', session_token: string, session_jwt: string }
const client = new StytchHeadlessClient(getStytchPublicToken())
client.session.updateSession({
  session_token: payload.session_token,
  session_jwt: payload.session_jwt,
})
await client.session.authenticate({ session_duration_minutes: SESSION_DURATION_MINUTES })
const tokens = client.session.getTokens()
// reply: { ok: true, session_jwt, session_token } or { ok: false }
```

If `getTokens()` returns `null` or either field is missing → reply `{ ok: false }`. Do not call Astral APIs from offscreen.

5. Create `src/ui/extension/src/lib/sessionRefresh.ts`:

- `refreshSessionTokens(): Promise<boolean>`
- If `getSessionToken()` is null → return `false` (do not open offscreen).
- If `getSessionJwt()` is null → `clearSessionTokens()` and return `false` (`updateSession` requires both token fields).
- Ensure offscreen document:
  - `const existing = await browser.runtime.getContexts({ contextTypes: ['OFFSCREEN_DOCUMENT'], documentUrls: [browser.runtime.getURL('/offscreen.html')] })` (or the Chromium-equivalent WXT/browser API available in this MV3 target).
  - If none: `await browser.offscreen.createDocument({ url: browser.runtime.getURL('/offscreen.html'), reasons: ['LOCAL_STORAGE'], justification: 'Stytch session refresh requires a DOM context (SDK checkNotSSR)' })`.
- `browser.runtime.sendMessage({ type: 'astral_stytch_refresh', session_token, session_jwt })` and await the reply.
- On `{ ok: true, session_jwt, session_token }` → `setSessionTokens` → return `true`.
- On failure / throw → `clearSessionTokens()` → return `false`.

6. Create `src/ui/extension/src/lib/astralFetch.ts`:

- `astralFetch(path: string, init?: RequestInit): Promise<Response>` — URL = `${getAstralApiBase()}${path.startsWith('/') ? path : '/' + path}`; set `Authorization: Bearer ${jwt}` when jwt present; `credentials: 'omit'`.
- Before first attempt: if no jwt, call `refreshSessionTokens()` once. If still no jwt → throw `Error('sign_in_required')` (exact message string).
- On HTTP 401: one `refreshSessionTokens()` + retry with new jwt; if refresh fails or second response is 401 → `clearSessionTokens()` and throw `Error('sign_in_required')`.
- `astralGetJson<T>(path: string): Promise<T>` — GET, `res.json()`, throw on non-OK with status in message.
- `astralPutJson<T>(path: string, body: unknown): Promise<T>` — PUT JSON, same error rules.

These two helpers are the injection surface siblings already expect (`fetchPacingConfig(getJson)`, `fetchSurferConsent(..., getJson)`).

7. Create `src/ui/extension/src/lib/ensureSession.ts`:

```ts
export const SIGN_IN_COPY =
  'Sign in with your Astral account to capture job pages. This is the same login as the Astral website.'

export type EnsureSessionResult =
  | { ok: true; jwt: string }
  | { ok: false; reason: 'sign_in_required'; message: string }

export async function ensureSession(): Promise<EnsureSessionResult>
```

Algorithm: read jwt → if present return `{ ok: true, jwt }` → else `refreshSessionTokens()` → if jwt present return ok → else return `{ ok: false, reason: 'sign_in_required', message: SIGN_IN_COPY }`.

**Ritual:** `code(AST-1255): session tokens + offscreen refresh + astral Bearer fetch`

---

## Stage 2: Manifest action, sign-in page, icon path

**Done when:** `.output/chrome-mv3/manifest.json` contains an `action` key (empty object / no `default_popup`), lists `storage` + `offscreen` + expected `host_permissions`; icon click with no session opens the sign-in page showing Stytch login + `SIGN_IN_COPY`; completing Stytch login persists both tokens via `getTokens()`; a subsequent `ensureSession()` returns `ok: true`; with a stored jwt, icon click does not open sign-in and does not capture; `npm run build` and `npm run build:firefox` succeed; README + `env.example` document env + Dashboard allowlist + offscreen; no content-script network code added.

**Early check (before wiring the rest of the sign-in page UI polish):** After the HTML entrypoint mounts `StytchUIClient` with the mirrored Login products, complete **one** magic-link login on the load-unpacked extension page and confirm `stytch.session.getTokens()` returns both `session_jwt` and `session_token` on this `chrome-extension://` origin. If that fails (Dashboard origin / redirect / cookie behavior), **stop** and comment on parent AST-1170 with the exact Stytch / console error — do not proceed to polish or icon wiring. AST-1167 proved Bearer from an extension context; it did **not** prove login UI on `chrome-extension://`.

1. Update `wxt.config.ts` `manifest`:

```ts
action: {},  // required for browser.action.onClicked; no default_popup
permissions: ['storage', 'offscreen'],
host_permissions: [
  `${apiBase}/*`,
  'https://*.stytch.com/*',
],
```

Resolve `apiBase` via `process.env.WXT_ASTRAL_API_BASE` (trim, no trailing slash). If missing during `wxt build`, throw. Keep existing `key` + gecko id. Do **not** set `action.default_popup`.

2. Add `src/entrypoints/sign-in.html` (WXT HTML entrypoint; co-located script). Page contents:

- Heading: `Sign in to Astral Surfer`
- One short paragraph: exactly `SIGN_IN_COPY` (import the constant from `ensureSession.ts` — do not duplicate a second string).
- Mount `StytchUIClient` with products mirroring `src/ui/frontend/src/pages/Login.tsx`: `[Products.emailMagicLinks, Products.oauth]` only — no new auth products.
- Stytch redirect / magic-link URL: `browser.runtime.getURL('/sign-in.html')` (allowlist this exact string in Stytch Dashboard — document in README).
- On authenticated session: `const tokens = stytch.session.getTokens()` — same call site pattern as `AuthContext.tsx` (`stytch.session.getTokens()?.session_jwt`). If `tokens?.session_jwt` and `tokens?.session_token` are both non-empty strings, `await setSessionTokens(tokens.session_jwt, tokens.session_token)` and show exactly: `You're signed in — you can close this tab.` Do **not** call Astral APIs from this page.

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

Do not construct Stytch clients here. Do not add content-script entrypoints.

4. Add `src/ui/extension/src/vite-env.d.ts` declaring `WXT_STYTCH_PUBLIC_TOKEN` and `WXT_ASTRAL_API_BASE` on `ImportMetaEnv`.

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

- Required `WXT_*` env vars for build/dev.
- Stytch Dashboard: Redirect URL (Login + Sign-up) for `chrome-extension://<stable-id>/sign-in.html` (stable id from pinned `manifest.key` — read id from `chrome://extensions` after first load-unpacked).
- Note that `offscreen` is requested for Stytch refresh and will need disclosure under **AST-1173**.
- Manual smoke: load unpacked → click icon with empty storage → sign-in tab opens → complete login → click icon again → no sign-in tab (session present). Capture still absent until AST-1256.

7. Build gate:

```bash
cd src/ui/extension
# export WXT_* first
npm run build
npm run build:firefox
```

Both exit 0. Confirm `.output/chrome-mv3/manifest.json` contains: `action` key, `storage`, `offscreen`, and the expected `host_permissions`.

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

**Conf:** Medium — AST-1167 + Bearer path are settled; offscreen refresh is the correct SDK-safe home but is new machinery for this shell (and adds a permission AST-1173 must later disclose).

**Risk:** Medium — missing `action: {}` disables the extension; refresh-in-SW would throw on every post-5-minute capture; Stytch login UI on `chrome-extension://` remains an early Stage 2 proof risk (Dashboard allowlist + SDK origin behavior).

---

## Rules check (§8)

| Rule | Plan stance |
|------|-------------|
| §1.3 DRY | Single token module + single `astralFetch`; siblings keep injected-fetch pattern; one `SIGN_IN_COPY` |
| §2.1 / secrets-from-environ | Public token + API base from `WXT_*` env; no secrets in repo |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §2.9 require-auth | Honored client-side via Bearer JWT; no anonymous Astral posts |
| §3.3 imports | TS client — outside Python import table (AST-1254) |
| §3.5 naming / extension layout | Libs under `src/lib/`; entrypoints under `src/entrypoints/`; plain DOM sign-in + offscreen (no React) |
| Engineer test-tree ban | No `tests/` or bible edits; Betty owns extension Vitest after Code Complete |

---

## Revisions

Revision 1 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE) — fix-now: missing `action: {}`; Stytch SDK cannot run in SW; plus discuss hedges / SIGN_IN_COPY / early chrome-extension login proof.  
Changes: Chose offscreen document as refresh home; require `action: {}` + `offscreen` permission; moved SDK construction out of background; resolved throw-vs-Response / entrypoint / `getTokens()` / `session.authenticate` hedges; justified client `SIGN_IN_COPY`; added Stage 2 early magic-link proof; dropped redundant `api.stytch.com` host; named `SESSION_DURATION_MINUTES`; corrected Betty test-tense; Conf → Medium.
