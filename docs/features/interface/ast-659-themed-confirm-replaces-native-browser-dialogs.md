# Themed confirm replaces native browser dialogs

**Linear:** [AST-659](https://linear.app/astralcareermatch/issue/AST-659/themed-confirm-replaces-native-browser-dialogs-upsert-modal-is-still)  
**Parent:** [AST-639](https://linear.app/astralcareermatch/issue/AST-639/upsert-modal-is-still-using-the-browser-confirmation-popup-instead-of)  
**Publish ref:** `sub/AST-639/AST-659-themed-confirm-native-browser`

Susan reported that admin flows still pop browser-native `window.confirm` chrome while the app already ships a themed confirm dialog via `UserPromptProvider` / `useUserConfirm`. This ticket migrates the three known production call sites (Data Management upsert apply, Manage Candidates logical delete, Manage Candidates clear API key) to the shared hook, updates component tests to exercise the themed dialog, and delivers an audit summary at Code Complete confirming no other production `window.confirm` remains outside documented infrastructure fallbacks.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminDataManagement.tsx` | Replace upsert-apply `window.confirm` with `useUserConfirm` | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | Replace delete + clear-key `window.confirm` with `useUserConfirm` | ui |
| `tests/component/frontend/pages/test_AdminDataManagement.test.tsx` | Remove `window.confirm` mock; assert themed dialog on upsert confirm path | tests |
| `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` | Remove `window.confirm` mock; assert themed dialog on delete + clear-key paths | tests |

**Out of scope (preserve as-is):** `src/ui/frontend/src/components/UserPrompt.tsx` and `src/ui/frontend/src/components/Modal.tsx` test-only `window.confirm` fallbacks when `ConfirmContext` is absent.

**QA manifest (Betty — optional extension, not engineer commits unless tests fail):** No new test files required; engineer updates existing page tests in Stage 3. Betty may extend manifest if she wants explicit cancel-path coverage.

## Stage 1: Data Management — upsert apply confirm

**Done when:** Clicking Save on the Table Upsert modal with valid JSON shows the themed `alertdialog` (not `window.confirm`); Cancel leaves modal + JSON intact and does not POST; Confirm POSTs `/api/admin/data/table_copy_upsert` and preserves existing toast behavior.

1. In `src/ui/frontend/src/pages/AdminDataManagement.tsx`, add import:
   ```ts
   import { useUserConfirm } from "../components/UserPrompt"
   ```
2. Inside `export default function DataManagement()`, after existing hooks (~line 57), add:
   ```ts
   const confirm = useUserConfirm()
   ```
3. In `handleUpsertApply` (~line 79), replace the synchronous guard:
   ```ts
   if (!window.confirm(`Apply JSON upsert into table "${table}"? Unrelated rows remain untouched.`)) return
   ```
   with:
   ```ts
   const ok = await confirm(
     `Apply JSON upsert into table "${table}"? Unrelated rows remain untouched.`,
     { title: "Apply upsert", confirmLabel: "Apply" },
   )
   if (!ok) return
   ```
4. Do **not** change validation order: empty JSON toast, `upsertPosting` guard, API call body, success toast text, error handling, or modal close behavior after success.
5. Do **not** add `variant: "danger"` — upsert is irreversible but not a delete; keep default confirm styling (same as intake start-over informational confirms).

⚠️ **Decision:** Title **"Apply upsert"** and confirm label **"Apply"** mirror the modal's Save intent without implying delete semantics.

## Stage 2: Manage Candidates — delete and clear API key confirms

**Done when:** Logical delete and Clear API key each open the themed confirm dialog with danger styling on the confirm button; Cancel aborts with no API call / no `clearKey` state change; Confirm performs the same actions as today.

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, add import:
   ```ts
   import { useUserConfirm } from "../components/UserPrompt"
   ```
2. Inside the page component (after `useCandidate()` / state hooks), add:
   ```ts
   const confirm = useUserConfirm()
   ```
3. Change `handleDelete` (~line 204) from a sync function to async:
   ```ts
   async function handleDelete(c: Candidate) {
     const ok = await confirm(
       `Delete candidate "${c.astral_candidate_id}"? This is a logical delete (state → DELETED).`,
       { title: "Delete candidate", confirmLabel: "Delete", variant: "danger" },
     )
     if (!ok) return
     // existing api DELETE + toast + loadAll + refresh unchanged
   }
   ```
4. Replace the Clear button `onClick` (~lines 355–360) inline handler with an async IIFE pattern:
   ```ts
   onClick={() => {
     void (async () => {
       const ok = await confirm(
         "Clear this candidate's API key? They won't be able to run tasks until a new key is set.",
         { title: "Clear API key", confirmLabel: "Clear key", variant: "danger" },
       )
       if (!ok) return
       setClearKey(true)
       setToast({ text: "Key will be cleared on save", variant: "info" })
     })()
   }}
   ```
5. Do **not** change delete API route, edit-save payload for `clearKey`, toast copy, or list/modal structure.

⚠️ **Decision:** Destructive actions use `variant: "danger"` on the confirm button, matching `Modal.tsx` dirty-discard confirm (~line 34) and `UserPrompt` danger class on the primary button.

## Stage 3: Component tests — themed dialog instead of `window.confirm` mock

**Done when:** Both page test files pass without `vi.spyOn(window, "confirm")`; upsert/delete/clear flows click through the themed `alertdialog`; existing assertions on API outcomes and toasts remain green.

Reference pattern: `tests/component/frontend/pages/test_CandidateIntake.test.tsx` — `screen.findByRole("alertdialog", { name: "<title>" })` then `within(dialog).getByRole("button", { name: "<confirmLabel>" })`.

1. In `tests/component/frontend/pages/test_AdminDataManagement.test.tsx`:
   - Remove `vi.spyOn(window, "confirm").mockReturnValue(true)` from `beforeEach`.
   - In test **"runs sql, copies output, browses schema, and completes table upsert from modal"** (~line 82): after clicking Save, add:
     ```ts
     const dialog = await screen.findByRole("alertdialog", { name: "Apply upsert" })
     await userEvent.click(within(dialog).getByRole("button", { name: "Apply" }))
     ```
     before the existing `waitFor` on upsert success toast.
   - In test **"toasts when upsert paste is empty and when API reports ok:false"**:
     - First Save (empty JSON): no confirm dialog — keep asserting **"Paste JSON rows first."** immediately.
     - Second Save (with `[]`): after Save click, confirm via alertdialog **"Apply upsert"** → **"Apply"**, then assert **"bad payload"** toast.
   - Add `import { within } from "@testing-library/react"` if not already present.

2. In `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx`:
   - Remove `vi.spyOn(window, "confirm").mockReturnValue(true)` from `beforeEach`.
   - In test **"renders candidates and supports add, view, edit, and delete"**:
     - After clicking Clear (~line 99): insert themed confirm step before Save:
       ```ts
       const clearDialog = await screen.findByRole("alertdialog", { name: "Clear API key" })
       await userEvent.click(within(clearDialog).getByRole("button", { name: "Clear key" }))
       ```
     - Before Delete click (~line 103): after click, themed confirm:
       ```ts
       await userEvent.click(screen.getByRole("button", { name: "Delete" }))
       const deleteDialog = await screen.findByRole("alertdialog", { name: "Delete candidate" })
       await userEvent.click(within(deleteDialog).getByRole("button", { name: "Delete" }))
       ```
       (Adjust so Delete button click opens dialog, then confirm — do not expect delete toast until after confirm.)
   - Skipped tests: leave `.skip` as-is; no changes required.

3. Run targeted component tests before stage commit:
   ```bash
   npm run test -- tests/component/frontend/pages/test_AdminDataManagement.test.tsx tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
   ```
   Fix product code only if failures are in migrated confirm wiring (not test manifest disputes — those get `[qa-handoff]` per workflow).

## Stage 4: Audit summary and Code Complete handoff

**Done when:** `rg 'window\.confirm' src/ui/frontend` shows only `UserPrompt.tsx` and `Modal.tsx` fallbacks; Linear comment on **AST-659** lists each former site and migration status; ticket moves to **Code Complete**.

1. Run audit command from repo root:
   ```bash
   rg 'window\.confirm' src/ui/frontend
   ```
   Expected matches:
   - `UserPrompt.tsx` — documented provider-absent fallback
   - `Modal.tsx` — documented provider-absent fallback for dirty discard
   - **No matches** in `pages/AdminDataManagement.tsx`, `pages/AdminManageCandidates.tsx`, or any other `pages/*.tsx`

2. Post Linear comment on **AST-659** (not parent) with audit table:

   | Former site | Action guarded | Status |
   |-------------|----------------|--------|
   | `AdminDataManagement.tsx` handleUpsertApply | Apply JSON upsert | → `useUserConfirm` ("Apply upsert") |
   | `AdminManageCandidates.tsx` handleDelete | Logical delete | → `useUserConfirm` ("Delete candidate", danger) |
   | `AdminManageCandidates.tsx` Clear button | Clear API key | → `useUserConfirm` ("Clear API key", danger) |
   | `UserPrompt.tsx` / `Modal.tsx` | Test-only fallback | Excluded per ticket boundaries |

3. Do **not** modify intake, intake chat, or other existing `useUserConfirm` consumers — AC5 is satisfied by leaving them untouched and relying on existing `test_CandidateIntake.test.tsx` coverage in CI.

## Self-Assessment

**Scope:** `Single-Component` — Four frontend files only (two admin pages + two Vitest page specs); no API, data, or config layers.

**Conf:** `high` — `useUserConfirm` is already wired app-wide via `renderWithProviders` / `NavigationShell`; this ticket copies established patterns from `CandidateIntake.tsx` and `IntakeChatModal.tsx`.

**Risk:** `low` — Confirm/cancel gating only; upsert/delete/clear-key API payloads and toast copy stay identical, so a wiring mistake surfaces in component tests without cross-feature blast radius.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses shared `useUserConfirm` / `UserPromptProvider`; no duplicate confirm UI. |
| §2.1 config | No new config keys or state strings. |
| §2.4 batch | N/A — no batch processing. |
| §2.6 state machine | N/A — no workflow state changes. |
| §3.3 imports | Frontend-only; pages import from `../components/UserPrompt` only. |
| §3.5 naming | No new files; existing flat `pages/` names preserved. |

No conflicts — plan is safe to implement as written.

## Review (build)

**Branch:** `origin/sub/AST-639/AST-659-themed-confirm-native-browser`  
**Tip:** `36ada25c`  
**Built:** Stage 1 — `AdminDataManagement.tsx` upsert apply → `useUserConfirm` ("Apply upsert"). Stage 2 — `AdminManageCandidates.tsx` delete + clear-key with danger variant. Stage 3 — page Vitest specs click through `alertdialog` instead of `window.confirm` mock. Stage 4 — audit: only `UserPrompt.tsx` / `Modal.tsx` fallbacks remain in `src/ui/frontend`.

**Betty manifest (Code Complete):** run `test_AdminDataManagement.test.tsx` + `test_AdminManageCandidates.test.tsx` per plan Stage 3; extend cancel-path coverage if desired.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-639/AST-659-themed-confirm-native-browser` @ `5b55ccc8`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | All three production `window.confirm` sites migrated: upsert apply (`"Apply upsert"` / `"Apply"`), logical delete and clear API key (`variant: "danger"`). Validation order and API/toast behavior unchanged. |
| Audit (AC3) | `rg window.confirm src/ui/frontend/pages` — zero matches; only `UserPrompt.tsx` / `Modal.tsx` documented fallbacks remain. |
| Tests (in-scope) | `test_AdminDataManagement` and `test_AdminManageCandidates` click through `alertdialog` per plan; `test_CandidateIntake` api-mock stubs only (AC5 regression). |
| §3.3 imports | Pages import `useUserConfirm` from `../components/UserPrompt` at module top; no layer violations. |
| Self-assessment | Conf/risk accurate for the themed-confirm work; implementation matches `Single-Component` intent for the two admin pages. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `tests/component/frontend/lib/test_listTableLayout.test.ts` (AST-657 cases) | Imports `mergeWidthsForSticky`, `measureListTableColumnWidths`; calls `stickyLeftPx(..., checkboxWidthPx)` 6-arg form. **None of these exist** on `listTableLayout.ts` at this publish ref. Verified: **3 failed / 4 passed** when this file runs. |
| **fix-now** | `tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx` (`AST-657: frozen data columns get cumulative sticky left offsets after measure`) | Expects post-measure sticky offsets; `useListTableColumnMeasure` / measured-width product not on this branch. Out of AST-659 scope. |
| **discuss** | Cross-ticket boundary (§5d) | Plan scope = two admin pages + two page specs. Diff also adds **AST-657** list-table tests + bible row (`§7.13zzy` adjacent AST-657 entry) with **no** AST-657 product in the three-dot diff. Narrowed AST-659 manifest does not run the broken files — full suite / `test_listTableLayout.test.ts` will fail. Revert AST-657 hunks from this sub-branch or land them only with AST-657 product on `sub/AST-639/AST-657-*`. |

### Recommended actions

| # | Action | Owner |
|---|--------|-------|
| 1 | Revert AST-657 test additions in `test_listTableLayout.test.ts` and `test_ListPage_listTableLayout.test.tsx` on this publish ref (keep AST-659 page-test changes). | `resolve-child` |
| 2 | If bible AST-657 row must stay, ensure it documents tests that match product on the same ref; otherwise trim to AST-659 §7.13zzx only. | Betty / engineer per handoff |
| 3 | No product changes required for themed confirm — admin page wiring is correct as built. | — |

## Resolution (2026-06-15)

**Radia review:** `eeeb1a4f` — themed confirm product solid; fix-now was cross-ticket AST-657 test/bible contamination on this `sub/*`.

**Resolved:**

- Reverted `test_listTableLayout.test.ts` and `test_ListPage_listTableLayout.test.tsx` to `origin/dev` (removed AST-657 cases that referenced product not on this branch).
- Removed **AST-657** bible row from §7.13zzt; **AST-659** §7.13zzx manifest unchanged.
- No product code changes — admin `useUserConfirm` wiring shipped as built.

**Verify:** Betty manifest (29 passed, 2 skipped); `test_listTableLayout.test.ts` no longer fails on missing exports at this ref.
