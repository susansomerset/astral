# AST-1254 — Extension placement and MV3 scaffold

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1254/extension-placement-and-mv3-scaffold-extension-shell-manifest-v3  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1170/extension-shell-manifest-v3-scaffold-and-authenticated-single-page  

**Publish ref (origin):** `sub/AST-1170/AST-1254-extension-placement-and-mv3-scaffold`  
**Parent integration ref:** `ftr/AST-1170-extension-shell-manifest-v3-scaffold-and-authenticated-single-page-capture`

Settles the second client surface at `src/ui/extension/` (narrow code-rules / statute amendment), scaffolds a WXT Manifest V3 TypeScript package around the **already-landed** Surfer `src/lib/` helpers from sibling epics, gitignores `node_modules` / build output, documents load-unpacked Chrome build/reload, wires a Vitest project whose `include` is `tests/component/extension/`, and proves a Firefox build target from the same source. Delivers an **installable empty shell** — no session wiring, no toast, no page POST (siblings **AST-1255** / **AST-1256**).

Boundaries (do **not** implement): auth / Stytch / Bearer storage (**AST-1255**); icon-click capture, shadow-root toast, `page_intake` POST, two-phase messaging (**AST-1256**); fan-out / progress / culling / consent UI wiring beyond preserving existing `src/lib/` files; store packaging (**AST-1187**); Railway / `build_railway.sh` extension build; any `tests/` or bible files (Betty after Code Complete).

⚠️ **Decision — wrap existing `src/lib/`, do not relocate:** Sibling Surfer lines already committed `src/ui/extension/src/lib/{dwell,pacingConfig,fanOut,surferConsent*}.ts`. Keep that path. Enable WXT with `srcDir: 'src'` so entrypoints land at `src/entrypoints/` beside `src/lib/`. Do **not** rename `lib/` → WXT's default `utils/`, do **not** move libs into `entrypoints/`, and do **not** delete or rewrite those modules in this ticket.

⚠️ **Decision — WXT (settled on parent):** Do not re-litigate `@crxjs/vite-plugin`. Pin `wxt@^0.21.3` (current stable at plan time); lock via `package-lock.json`. Chrome is the required target; Firefox is a build-only portability check.

⚠️ **Decision — empty shell permissions:** Request **no** `host_permissions`, `scripting`, `activeTab`, `tabs`, `storage`, or `alarms` in this ticket. Sibling capture/auth tickets add permissions when they need them. Manifest carries name/version/MV3 + background entry + pinned Chrome `key` + Firefox gecko id only.

⚠️ **Decision — Vitest home without engineer-owned tests:** Wire `vitest.config.ts` so `include` is repo-root `tests/component/extension/**/*.test.{ts,tsx}`. Do **not** create, move, or edit any file under `tests/` (engineer test-tree ban). Existing Surfer lib tests under `tests/component/frontend/lib/test_surfer*.test.ts` keep running via the **frontend** Vitest project until Betty migrates them. After Code Complete, Betty owns the first files in `tests/component/extension/`.

⚠️ **Decision — Flask never serves the extension:** AC3 means the Flask catch-all must continue to serve **only** `src/ui/frontend/dist`. Do **not** add a route, symlink, or static mount for `.output/`. Verify by inspection of `src/ui/server.py` (`_DIST`); no `server.py` edit required unless a one-line clarifying comment is needed — prefer no edit.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/ASTRAL_CODE_RULES.md` | Amend §3.1 tree + §3.5: second client surface `src/ui/extension/`; Python import-direction governs Python only | docs |
| `canon/statutes/astral/ui/astral.ui.frontend-file-placement.md` | Extend statement + `applies_when.paths` for `src/ui/extension/**`; note WXT layout vs SPA flat rules | docs/statute |
| `.gitignore` | Ignore `src/ui/extension/node_modules/`, `.output/`, `.wxt/`, coverage dir if used | root |
| `src/ui/extension/package.json` | New WXT package: scripts `dev`, `dev:firefox`, `build`, `build:firefox`, `postinstall` (`wxt prepare`), `test:component` | ui |
| `src/ui/extension/package-lock.json` | Lockfile from `npm install` | ui |
| `src/ui/extension/wxt.config.ts` | `srcDir: 'src'`, MV3, pinned `manifest.key`, gecko id, `imports: false`, minimal manifest | ui |
| `src/ui/extension/tsconfig.json` | Extends `.wxt/tsconfig.json` after prepare | ui |
| `src/ui/extension/vitest.config.ts` | `WxtVitest()`; `include` → `tests/component/extension/**` | ui |
| `src/ui/extension/src/entrypoints/background.ts` | Empty-shell background via `defineBackground` — no network, no messaging handlers beyond noop | ui |
| `src/ui/extension/README.md` | Load-unpacked Chrome build/reload + Firefox build commands | ui |
| `src/ui/extension/public/` (optional icon) | Optional 128px placeholder icon referenced by `action.default_icon` so Chrome shows a toolbar button; skip if parent prefers text-only action | ui |

**Preserve unchanged:** every existing file under `src/ui/extension/src/lib/`.  
**No changes expected:** `src/ui/server.py` (verify only), `scripts/build_railway.sh`, `src/ui/frontend/**`, auth/capture modules, `tests/**`, bible.

---

## Stage 1: Placement amendment (code rules + statute)

**Done when:** `docs/ASTRAL_CODE_RULES.md` §3.1 shows `ui/extension/` as a sibling of `ui/frontend/`; §3.5 names the second client surface and states that the Python import-direction table (§3.3) governs **Python only** (`frontend/` and `extension/` are TypeScript clients outside that table); the statute file matches; `rg` finds both paths in the statute `applies_when`.

1. In `docs/ASTRAL_CODE_RULES.md` §3.1 Directory Layout, under `ui/`, immediately after the `frontend/` tree block (before `├── scripts/`), insert a sibling tree for the extension (abbreviated — do not invent product entrypoints beyond scaffold):

```
│       └── extension/         # WXT + TypeScript (Manifest V3) — not served by Flask
│           ├── src/
│           │   ├── entrypoints/   # WXT file-based entrypoints (background, later content)
│           │   └── lib/           # Shared non-entrypoint modules (pacing, consent, …)
│           ├── .output/           # Build output (gitignored) — load-unpacked from here
│           ├── package.json
│           ├── wxt.config.ts
│           └── vitest.config.ts
```

Also change the `ui/` comment from `# Web UI (Flask + React)` to `# Web UI (Flask + React) + browser extension client`.

2. In §3.5 UI Stack and Deployment, after the existing **Frontend file placement** table, add a subsection **Extension client (`src/ui/extension/`)** with this exact substance:

- Second client surface under `src/ui/`, sibling to `frontend/` (Susan / AST-1170).
- Own `package.json`, `wxt.config.ts`, `tsconfig`, Vitest config; build output under `.output/` (gitignored); **not** mounted by Flask.
- Layout: WXT `src/entrypoints/` for runtime entrypoints; `src/lib/` for shared modules (same role as `frontend/src/lib/`).
- Injected UI (toast / progress later) is plain DOM in a shadow root — **no React** for host-page surfaces.
- Prefer promise-based `browser.*` (WXT) over raw `chrome.*` callbacks; do not hard-code `ServiceWorkerGlobalScope` — background is the "background context" abstraction (Chrome SW / Firefox event page via WXT).
- **Python import-direction (§3.3) applies to Python only.** `src/ui/frontend/` and `src/ui/extension/` are TypeScript clients; they do not participate in the ui→core→data import table. Cross-contamination still forbids inventing a top-level `extension/` outside `src/ui/`.

3. In `canon/statutes/astral/ui/astral.ui.frontend-file-placement.md`:

- Add `src/ui/extension/**` to `applies_when.paths` (keep `src/ui/frontend/**`).
- Extend **Statement** so it covers both clients: SPA keeps the existing flat rules; extension uses WXT `entrypoints/` + `lib/` as above; neither lives outside `src/ui/`.
- Add a conforming example: `src/ui/extension/src/entrypoints/background.ts`.
- Add a violating example: repo-root `extension/` or `src/extension/`.

**Ritual:** `code(AST-1254): placement — code rules + statute`

---

## Stage 2: WXT package, gitignore, empty background, README

**Done when:** `cd src/ui/extension && npm ci && npm run build` exits 0; `.output/chrome-mv3/manifest.json` exists with `"manifest_version": 3` and a stable `key`; `npm run build:firefox` exits 0 and produces a Firefox output directory with a generated manifest (no hand-written second manifest); existing `src/lib/*.ts` files are untouched; README documents load-unpacked + reload.

1. Append to repo-root `.gitignore` (next to the existing frontend block):

```
# Astral Surfer extension (WXT) build artifacts
src/ui/extension/node_modules/
src/ui/extension/.output/
src/ui/extension/.wxt/
```

2. Create `src/ui/extension/package.json`:

```json
{
  "name": "astral-extension",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "wxt",
    "dev:firefox": "wxt -b firefox",
    "build": "wxt build",
    "build:firefox": "wxt build -b firefox",
    "postinstall": "wxt prepare",
    "test:component": "vitest run --config vitest.config.ts"
  },
  "devDependencies": {
    "typescript": "~5.9.3",
    "vite": "^6.3.5",
    "vitest": "^3.2.4",
    "wxt": "^0.21.3"
  }
}
```

⚠️ **Decision — zero runtime dependencies:** Parent target. No React, no `@stytch/*` on this ticket. Auth deps land on **AST-1255** if needed.

3. Create `src/ui/extension/wxt.config.ts`:

```ts
import { defineConfig } from 'wxt';

// Pinned Chrome extension public key (base64) — stable ID across load-unpacked rebuilds.
// Generated once in Stage 2 step 4; do not regenerate on later builds.
const CHROME_EXTENSION_KEY = '<PASTE_BASE64_PUBLIC_KEY>';

export default defineConfig({
  srcDir: 'src',
  imports: false,
  manifest: {
    name: 'Astral Surfer',
    description: 'Capture job pages you are already viewing into Astral.',
    version: '0.0.0',
    key: CHROME_EXTENSION_KEY,
    browser_specific_settings: {
      gecko: {
        id: 'surfer@astralcareermatch.com',
        strict_min_version: '109.0',
      },
    },
  },
});
```

4. Generate the Chrome public key **once** and paste into `CHROME_EXTENSION_KEY` (do not commit the private key):

```bash
cd src/ui/extension
openssl genrsa 2048 | openssl rsa -pubout -outform DER 2>/dev/null | base64 -w0
# On macOS use: … | base64
```

Store only the base64 public key string in `wxt.config.ts`. If a private PEM is written to disk during generation, delete it or keep it **outside** the repo (never commit `*.pem` under `src/ui/extension/`).

5. Create `src/ui/extension/src/entrypoints/background.ts`:

```ts
export default defineBackground(() => {
  // Empty shell (AST-1254): no network, no messaging, no capture.
  // AST-1255 / AST-1256 own session + icon-click paths on this background context.
});
```

Use WXT's auto `defineBackground` types from `.wxt/` after `wxt prepare`. Prefer `browser` from `wxt/browser` in later tickets; this stub needs no API calls.

6. Create `src/ui/extension/tsconfig.json`:

```json
{
  "extends": "./.wxt/tsconfig.json",
  "compilerOptions": {
    "strict": true
  }
}
```

7. Run install + prepare + builds from `src/ui/extension/`:

```bash
cd src/ui/extension
npm install
npm run build
npm run build:firefox
test -f .output/chrome-mv3/manifest.json
test -f .output/firefox-mv3/manifest.json || test -f .output/firefox-mv2/manifest.json
```

⚠️ **Decision — accept whichever Firefox MV folder WXT emits:** Portability AC is "same source, no second hand-written manifest." If WXT emits `firefox-mv3` or `firefox-mv2`, either satisfies this ticket; record the actual path in README. Do not hand-edit the generated Firefox manifest.

8. Create `src/ui/extension/README.md` with these sections (commands exact):

- **Install:** `cd src/ui/extension && npm install`
- **Chrome load-unpacked:** `npm run build`, then Chrome → `chrome://extensions` → Developer mode → Load unpacked → select `src/ui/extension/.output/chrome-mv3`
- **Reload after edit:** rebuild (`npm run build`) then click Reload on the card — **or** run `npm run dev` (WXT watches and reloads; no reinstall)
- **Firefox build (portability only):** `npm run build:firefox` → output under `.output/firefox-mv*` — not required for UAT
- **Not served by Flask:** extension `.output/` is never a URL on `:5001`
- **Tests (Betty):** `npm run test:component` looks at `tests/component/extension/` (populated after Code Complete)

9. Confirm `git status` does **not** show modifications under `src/ui/extension/src/lib/`.

**Ritual:** `code(AST-1254): WXT MV3 empty shell + gitignore + README`

---

## Stage 3: Vitest project home + AC verification

**Done when:** `vitest.config.ts` exists and `include` resolves to `tests/component/extension/**/*.test.{ts,tsx}`; `npm run test:component` exits 0 with **zero** tests (empty include is OK — or Vitest reports no test files without failing; if Vitest fails on zero files, set `passWithNoTests: true`); Chrome build still loadable; Flask `_DIST` still points only at `frontend/dist`.

1. Create `src/ui/extension/vitest.config.ts`:

```ts
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';
import { WxtVitest } from 'wxt/testing/vitest-plugin';

const extensionRoot = fileURLToPath(new URL('.', import.meta.url));
const repoRoot = path.resolve(extensionRoot, '../../..');

export default defineConfig({
  plugins: [WxtVitest()],
  test: {
    environment: 'node',
    include: [path.join(repoRoot, 'tests/component/extension/**/*.test.{ts,tsx}')],
    passWithNoTests: true,
  },
});
```

⚠️ **Decision — `environment: 'node'` for the empty home:** Lib/DOM tests Betty adds later may switch to `happy-dom`/`jsdom` per case; this ticket only establishes the project path. Do not copy frontend's React Testing Library setup.

2. Verify:

```bash
cd src/ui/extension
npm run test:component
npm run build
# Flask non-serve (read-only check — expect only frontend/dist):
rg -n "_DIST|extension" src/ui/server.py
# Expect _DIST → frontend/dist; no path into extension/.output
```

3. Manual Chrome check (builder, once): Load unpacked from `.output/chrome-mv3`; confirm the extension appears; touch `src/entrypoints/background.ts` (whitespace), `npm run build`, Reload on the card — extension ID must **not** change (pinned `key`).

**Ritual:** `code(AST-1254): vitest home + AC verify`

---

## Self-Assessment

**Scope:** `Single-Component` — one new WXT client package under `src/ui/extension/` plus a narrow docs/statute placement amendment; no Python product logic, no sibling capture/auth behavior.

**Conf:** `high` — parent settled WXT + `src/ui/extension/`; siblings already proved the `src/lib/` path; WXT docs give exact scaffold/build/firefox/vitest shapes; Flask non-serve is already true by `_DIST` pointing at frontend only.

**Risk:** `low` — empty shell cannot break intake or the SPA; main failure modes are gitignore misses or accidental `lib/` churn, both gated by explicit preserve steps.

---

## Code-rules self-review

- **§1.3 DRY:** Background stub has no duplicated helpers; libs stay shared under `src/lib/`.
- **§2.1 config:** No new behavior-driving literals in the extension beyond manifest name/version/key (packaging identity). Endpoint base / timeouts land with **AST-1255** / **AST-1256** via config + GET patterns already used by pacing.
- **§2.4 / §2.6:** N/A (no batch/state machine).
- **§3.3 imports:** Amendment explicitly scopes Python import-direction to Python; TS clients stay outside the table without inventing a top-level package (avoids `no-cross-contamination` exemption).
- **§3.5 naming / placement:** Statute + table extended rather than bypassed; WXT `entrypoints/` + `lib/` documented.
- **§3.6:** No spike promotion from `debug/`; production home is `src/ui/extension/` only.
- **Test-tree ban:** No `tests/` writes on this tip.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1170/AST-1254-extension-placement-and-mv3-scaffold`
**Plan path:** `docs/features/surfer/ast-1254-extension-placement-and-mv3-scaffold.md`

**Built tip:** `fffccd43d8fa08e5f89934aabd4f7413eadc570b` (`fffccd43`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `513e99f7` | placement — code rules + statute |
| 2 | `d2986bff` | WXT MV3 empty shell + gitignore + README |
| 3 | `fffccd43` | vitest home + AC verify |

---

## Radia review

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1254
**Publish ref:** `origin/sub/AST-1170/AST-1254-extension-placement-and-mv3-scaffold` @ `ff5a7d0e`
**Overall:** DISCUSS

Full active-statute corpus (64 leaves under `canon/statutes/**`, `status: active`, harness files skipped) scored in-session per the Full-set sweep algorithm — no `violates`. Universal set (18 `orch.*`) all `conforms` except the two noted below. Scoped set (46 `astral.*`) matched-and-scored where diff layers/paths intersected (`ui`, `docs`, `scripts`); everything else `not-applicable` on layer/path predicate (core/data/external/batch/agent/state/seed families — no Python product touched this tip). No `## Statutes checked` table pasted per review-child §5.0.3 / AGENTS.md.

### Plan adherence

- Files Changed table matches the diff almost exactly; optional `public/` icon row correctly dropped per Joan's plan-rubric recommendation (no `action` key added).
- All three prior Joan `discuss` findings resolved on this tip: `background.ts` now explicitly imports `defineBackground` (consistent with `imports: false`); statute `approved_at` refreshed to `2026-08-07`; `*.pem` added to `.gitignore`.
- `src/ui/extension/src/lib/**` untouched; `src/ui/server.py` untouched — both verified.

### Findings

- **discuss** — `tests/component/frontend/lib/test_surferFanOut.test.ts` is still present on this tip, byte-identical to the new `tests/component/extension/lib/test_surferFanOut.test.ts`. Betty's own QA comment already flagged this as "known merge residue" requiring a `[qa-handoff]` to remove; that handoff hasn't happened. The frontend Vitest project will keep collecting the orphaned copy. Not a fix-now for the engineer (test-tree ban) — routes to Betty.
- **discuss** — `orch.git.commit-vocabulary`: commit `ff5a7d0e` (`test(AST-1254): vitest fs.allow + jsdom for extension suite`) touches only product files (`src/ui/extension/{package.json,package-lock.json,vitest.config.ts}`), not the test tree. Betty's manifest comment allowed either `test(...)` or `code(...)` for this preflight fix, so not blocking, but `code(AST-1254):` would keep rollup-log ownership attribution unambiguous.
- **discuss** — `orch.roles.engineer-assignee-through-resolve`: Linear assignee is already Radia at `Tests Passed` rather than the implementing engineer. Observation only — no diff impact, no action taken (assignee changes are outside review-child's authority).

### Pattern conformance

`pattern.config.config-block` (cited in description) — conforms: no new behavior-driving literals; manifest `name`/`version`/`key`/gecko `id` are packaging identity, not config-driven business state.

### What's solid

Placement amendment is narrow and exact; WXT scaffold matches the plan's exact snippets; empty-shell background has zero network/messaging surface; Firefox portability build documented without a hand-written second manifest; bible reorg (`docs/test-bible/extension/{scaffold,lib}.md`) is clean and cross-references correctly.

### Recommended actions

File `[qa-handoff]` to Betty for the orphaned `tests/component/frontend/lib/test_surferFanOut.test.ts` before the parent rolls up, so the frontend Vitest project stops double-collecting the migrated spec.

## Frame diff

(none) — description checklist already matches the shipped diff; no adds/moves needed.

context_tokens≈70000

— Radia

---

## Resolution

**Date:** 2026-08-07  
**Review tip:** `244da6cf` (`docs(AST-1254): Radia review — findings`)  
**Product tip:** `ff5a7d0e`

**fix-now:** none.

**discuss — orphaned `tests/component/frontend/lib/test_surferFanOut.test.ts`:** No product change (engineer test-tree ban). Filing `[qa-handoff]` @Betty White to delete the residue so frontend Vitest stops double-collecting the migrated extension copy. Staying **Review Posted** with assignee Betty until she delivers and reassigns.

**discuss — `test(AST-1254):` vocabulary on product preflight `ff5a7d0e`:** Acknowledged; Betty's manifest allowed `test(...)` or `code(...)`. No rewrite of history. Future product-only preflights use `code(<ticket>):`.

**discuss — assignee at Tests Passed:** Observation only; assignee is Ada for this resolve pass.

**Advisory / other:** none.

