# Extension lib

**Test tree:** `tests/component/extension/lib/`  
**Sources:** `src/ui/extension/src/lib/`

Surfer helpers that live in the extension package (not SPA `frontend/src/lib/`). Run via the WXT Vitest project:

```bash
cd src/ui/extension && npm run test:component -- \
  ../../../tests/component/extension/lib/<file>.test.ts
```

Scaffold / placement: **[`scaffold.md`](scaffold.md)**. SPA pages still map under **`docs/test-bible/frontend/pages.md`**.

### AST-1236 · AST-1174

**Parent:** [AST-1174 — Human-paced fan-out over the batch worklist](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist). **Publish:** `origin/sub/AST-1174/AST-1236-pacing-config`.

`fetchPacingConfig` / cache, shared `dwell()` (ordinary `setTimeout`, MV3 ceiling from config), `createTabBudget` slot transfer so `max_tabs` cannot be exceeded under interleaved acquire/release. Config + GET: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_surfer.md`**. §6c N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Cache + fetch injection | `src/ui/extension/src/lib/pacingConfig.ts` | **`test_surferPacingConfig.test.ts`** |
| Randomized dwell + MV3 reject | `src/ui/extension/src/lib/dwell.ts` | same |
| One-at-a-time slot transfer | `createTabBudget` in `pacingConfig.ts` | same |

**Broken / obsolete:** none.

**Integration:** none revised.

```bash
cd src/ui/extension && npm run test:component -- \
  ../../../tests/component/extension/lib/test_surferPacingConfig.test.ts
```

### AST-1237 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`.

`needsDisclosure` / `fetchSurferConsent` / `optInSurferConsent` (injected fetch); `mountSurferDisclosure` plain-DOM panel (shadow root when available; affirmative + decline handlers; no network). Spec uses `// @vitest-environment jsdom`. Web page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| needsDisclosure + injected GET/PUT | `surferConsent.ts` | **`test_surferConsent.test.ts`** |
| DOM mount / handlers / unmount | `surferDisclosureDom.ts` | same |

**Broken / obsolete:** none.

**Integration:** none.

```bash
cd src/ui/extension && npm run test:component -- \
  ../../../tests/component/extension/lib/test_surferConsent.test.ts
```

### AST-1238 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1238-off-switch-and-pre-consent-no-op`.

`mayCapture` / `fetchConsent` / `assertMayCapture` (`surferConsentGate.ts`); `optOutSurfer` (`surferOffSwitch.ts`). Wire notes: `docs/features/surfer/ast-1238-extension-consent-wiring.md`. Web off-switch page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Gate + assertMayCapture | `surferConsentGate.ts` | **`test_surferConsentGate.test.ts`** |
| Opt-out PUT | `surferOffSwitch.ts` | same |

**Broken / obsolete:** none.

**Integration:** none (capture route not yet present).

```bash
cd src/ui/extension && npm run test:component -- \
  ../../../tests/component/extension/lib/test_surferConsentGate.test.ts
```

### AST-1239 · AST-1174

**Parent:** [AST-1174 — Human-paced fan-out over the batch worklist](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist). **Publish:** `origin/sub/AST-1174/AST-1239-sequential-paced-fan-out`.

`runPacedFanOut` sequential loop under `fanOut.ts`: re-asks server remaining every iteration; fresh open→wait→`dwell()`→capture→post/fail→close; `createTabBudget` around each page; per-run `recordedThisRun` → `no_progress` if server re-offers a recorded URL; exits on empty remaining (`exhausted` / `empty_batch`) — does **not** await batch `COMPLETED`. Pacing: **AST-1236** above. §6c N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Happy path order + delivery-only post | `fanOut.ts` | **`test_surferFanOut.test.ts`** |
| empty_capture / page_error / no_progress / empty_batch | same | same |
| closeTab failure does not abort | same | same |

**Broken / obsolete:** none. Existing AST-1236 pacing tests still apply.

**Integration:** none revised (do not invent).

```bash
cd src/ui/extension && npm run test:component -- \
  ../../../tests/component/extension/lib/test_surferFanOut.test.ts \
  ../../../tests/component/extension/lib/test_surferPacingConfig.test.ts
```
