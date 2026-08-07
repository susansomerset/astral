# Extension scaffold

**Test tree:** `tests/component/extension/`  
**Sources:** `src/ui/extension/` (WXT package — not served by Flask)

Empty Manifest V3 shell home: placement amendment, WXT toolchain, gitignore, load-unpacked docs, Vitest `include` for this tree. Auth / capture / toast are sibling tickets (**AST-1255** / **AST-1256**). Lib helpers: **[`lib.md`](lib.md)**.

### AST-1254 · AST-1170

**Parent:** [AST-1170 — Extension shell — Manifest V3 scaffold and authenticated single-page capture](https://linear.app/astralcareermatch/issue/AST-1170/extension-shell-manifest-v3-scaffold-and-authenticated-single-page). **Publish:** `origin/sub/AST-1170/AST-1254-extension-placement-and-mv3-scaffold`.

Settles second client surface at `src/ui/extension/` (§3.5 + `astral.ui.frontend-file-placement`), WXT MV3 empty background, gitignore for `node_modules` / `.output` / `.wxt` / `*.pem`, README load-unpacked + Firefox build, Vitest project whose `include` is `tests/component/extension/`. Migrates prior Surfer lib specs from `tests/component/frontend/lib/test_surfer*.test.ts` into `tests/component/extension/lib/` (see **lib.md**). Zero-arg `./scripts/testing/run_component_tests.sh` also runs `cd src/ui/extension && npm run test:component`.

| Area | Source | Component tests |
| --- | --- | --- |
| Package scripts / WXT pin / firefox target | `package.json`, `wxt.config.ts` | **`test_scaffold.test.ts`** |
| Gitignore + README load-unpacked | `.gitignore`, `README.md` | same |
| Empty background (no network) | `src/entrypoints/background.ts` | same |
| Flask never serves `.output` (AC3) | `src/ui/server.py` `_DIST` | same |
| Placement docs / statute | `docs/ASTRAL_CODE_RULES.md`, `canon/statutes/astral/ui/astral.ui.frontend-file-placement.md` | same |
| Migrated Surfer libs | `src/ui/extension/src/lib/*` | **`lib/test_surfer*.test.ts`** (AST-1236–1239) |

**Broken / obsolete:** `tests/component/frontend/lib/test_surfer*.test.ts` — moved to `tests/component/extension/lib/` (frontend Vitest `include` no longer collects them). **Return pass:** delete residual `tests/component/frontend/lib/test_surferFanOut.test.ts` if still present on a tip (byte-identical orphan after first `merge-tests`). Bible blocks for AST-1236–1239 live under **`docs/test-bible/extension/lib.md`**.

**Product harness (landed on tip by Ada `test(AST-1254)`):** `server.fs.allow: [repoRoot]` in `vitest.config.ts` + `jsdom` `devDependency` — required for repo-root specs under WXT Vitest.

**Integration:** no existing scenario asserts extension load-unpacked or Flask non-serve of `.output` — no revision; do not invent.

**Manual (AC1):** Chrome load-unpacked from `.output/chrome-mv3`; rebuild + Reload — ID stable via pinned `key` (not automated here).

```bash
cd src/ui/extension && npm ci && npm run test:component -- \
  ../../../tests/component/extension/test_scaffold.test.ts \
  ../../../tests/component/extension/lib/test_surferPacingConfig.test.ts \
  ../../../tests/component/extension/lib/test_surferConsent.test.ts \
  ../../../tests/component/extension/lib/test_surferConsentGate.test.ts \
  ../../../tests/component/extension/lib/test_surferFanOut.test.ts
```
