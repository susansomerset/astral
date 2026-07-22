<!-- linear-archive: AST-780 archived 2026-07-22 -->

## Linear archive (AST-780)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-780/scheduled-actions-error-toast-ui-error-popups-still-not-using-our  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-761 — UI Error popups still not using our pretty popup component.  
**Blocked by / blocks / related:** parent: AST-761

### Description

## What this implements

Replace all four native browser alert() error paths on Scheduled Actions with the existing Toast component, matching the state/hook pattern used on other admin pages. Preserve server error text (for example non-schedulable task_key messages).

## Acceptance criteria

1. A full frontend audit finds no remaining native browser alert dialogs used to show API or action errors to the user.
2. On Scheduled Actions, each of the four audited failure paths shows an in-app Toast with error styling and the same message the native alert would have shown.
3. Running a non-schedulable task_key (for example vet_inflow_discovery) shows that server error text in Toast, not a blocking browser dialog.
4. After an error Toast appears, the page remains immediately usable without dismissing a modal browser alert.
5. Toast and UserPrompt behavior on all other pages is unchanged.

## Boundaries

* Does not replace confirmation dialogs (UserPromptProvider).
* Does not add error surfacing where failures are currently silent.
* Does not change backend error payloads or dispatch scheduling logic.
* Does not redesign Toast.

## Notes for planning

* Primary file: AdminScheduledActions.tsx (four alert() call sites).
* Follow Toast pattern from AdminTaskPrompts.tsx / AdminManageCandidates.tsx.
* ASTRAL_CODE_RULES §2.10 — Radia fix-now on any remaining native alert in touched UI.

## Git branch (authoritative)

Per orientation § Branch law: parent ftr/AST-761-ui-error-toast, child sub/AST-761/<child-segment>.

### Comments

#### radia — 2026-06-24T21:24:18.716Z
### Radia review — AST-780

**Diff:** `origin/dev...origin/sub/AST-761/ast-780-scheduled-actions-error-toast` @ `fa06058`
**Doc:** `docs/features/interface/ast-780-scheduled-actions-error-toast.md` (Review section)

**Plan fidelity:** Stage 1 complete — four `alert()` paths in `AdminScheduledActions.tsx` (`toggleAutoMode`, `handleRun`, edit/add `handleSave`) replaced with `readApiError` + `errorToastFromApiError`; `toastDiagnostics` import added; existing load-failure and AUTO edit-guard toasts unchanged.

**Audit:** `rg '\balert\(' src/ui/frontend/src/pages/` → zero matches on branch tip.

**Tests:** Betty manifest satisfied — `AST-780 error toast replaces alert` describe (3 cases) asserts toast text + `window.alert` not called; test-bible entry documents narrowed run.

**Rules (§1.3 DRY, §3.3 imports, parent Toast-for-errors):** Clean — reuses established AST-779 / Manage Agents pattern; frontend-only; no layer, config, batch, or debug-logging violations.

**fix-now:** none
**discuss:** none

#### betty — 2026-06-24T21:21:47.711Z
**QA test manifest** — `origin/sub/AST-761/ast-780-scheduled-actions-error-toast` @ `47414cc` (`merge-tests(AST-780): origin/tests c425793`)

1. **Vitest — Scheduled Actions error toast (required)**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  --testNamePattern="AST-780|AST-785"
```
Expect **`AST-780 error toast replaces alert`** (auto toggle + run, edit PUT, add POST) — visible error toast text from server `error` field; **`window.alert` not called**. Re-run **`AST-785 dispatch_tasks list UX`** load-failure toast regression.

2. **Routed page (§6c):** `AdminScheduledActions.tsx` — manifest item 1 satisfies first-paint + failure-path coverage on the page.

**Revised (this pass):** Replaced three legacy `window.alert` spy tests with error-toast assertions; added **`selectAllCandidatesFilter()`** + **`taskKeysPayload`** so table rows mount under **AST-785** auto-open behavior.

**Existing coverage:** **AST-779** Toast diagnostics — no duplicate Toast component manifest.

**Bible shasum:** `docs/test-bible/frontend/pages.md` → `8c6a6aee0958ea4b0bb8fd3705b8924e7b74fe49` on publish ref.

— Betty

#### katherine — 2026-06-24T21:16:03.002Z
**Plan:** [https://github.com/susansomerset/astral/blob/sub/AST-761/ast-780-scheduled-actions-error-toast/docs/features/interface/ast-780-scheduled-actions-error-toast.md](https://github.com/susansomerset/astral/blob/sub/AST-761/ast-780-scheduled-actions-error-toast/docs/features/interface/ast-780-scheduled-actions-error-toast.md) @ `b96d6c4`

Single stage: replace four `alert()` handlers in `AdminScheduledActions.tsx` (`toggleAutoMode`, `handleRun`, `handleSave` PUT/POST) with `readApiError` + `errorToastFromApiError`; repo audit confirms no other product-page `alert()` call sites. Betty manifest covers migrating four Vitest specs off `window.alert` spies.

**Self-assessment**
- **Scope:** `Single-Component` — one admin page, four error-handler edits; no backend or Toast component changes.
- **Conf:** `high` — Toast already wired on this page; same API-error pattern as `AdminAgentPrompts.tsx`.
- **Risk:** `low` — error-path UX only; success and scheduler behavior unchanged.

---

# Scheduled Actions error Toast (UI Error popups still not using our pretty popup component.)

**Linear:** [AST-780](https://linear.app/astralcareermatch/issue/AST-780/scheduled-actions-error-toast-ui-error-popups-still-not-using-our-pretty)
**Parent:** [AST-761](https://linear.app/astralcareermatch/issue/AST-761/ui-error-popups-still-not-using-our-pretty-popup-component)
**Publish ref:** `sub/AST-761/ast-780-scheduled-actions-error-toast`

Susan hit a blocking native `alert()` on Scheduled Actions when a dispatch task could not run (for example `dispatch_task task_key not schedulable: 'vet_inflow_discovery'`). The page already renders `<Toast>` for some paths (load failure, AUTO-row edit guard) but four API failure handlers still call `alert()`. This ticket replaces those four call sites with the shared error toast, preserving server error text and wiring `readApiError` / `errorToastFromApiError` so click-to-copy diagnostics from AST-779 work on these failures too.

## Audit baseline (parent AST-761 — complete)

| Page | User action | Native `alert()` before this ticket |
|------|-------------|-------------------------------------|
| Scheduled Actions | Toggle AUTO on a row | Yes (`toggleAutoMode`) |
| Scheduled Actions | Run a task manually | Yes (`handleRun`) |
| Scheduled Actions | Save an edited task (modal) | Yes (`handleSave` PUT branch) |
| Scheduled Actions | Create a new task (modal) | Yes (`handleSave` POST branch) |

Repo-wide product audit at plan time: `rg '\balert\(' src/ui/frontend/src/pages/` returns **only** those four lines in `AdminScheduledActions.tsx`. No other product pages use native `alert()` for API error feedback.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Replace four `alert()` error paths with `setToast` + `readApiError` / `errorToastFromApiError`; add `toastDiagnostics` import | ui |

**Out of scope (this ticket):** `Toast.tsx`, `toastDiagnostics.ts`, backend routes, confirmation modals (`UserPromptProvider`), silent failure paths (`toggleDebug`, `handleStop`, `handleKillAll`), `tests/**` (Betty manifest below).

**QA manifest (Betty — not engineer commits):** Update `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx`:

1. Replace the four tests that spy on `window.alert` (`"alerts on auto toggle failure and run failure"`, `"alerts when edit save PUT fails"`, `"alerts when add save POST fails"`) with assertions that error toast text appears in the document (same pattern as existing `"shows toast when dispatch_tasks fetch fails"` — visible `.toast-text` or message string).
2. Assert `window.alert` is **not** called on those failure paths (optional `alert` spy expecting zero calls).
3. Keep existing toast test for load failure and all non-error behavior tests green.

## Stage 1: Replace four `alert()` paths with error Toast

**Done when:** `rg '\balert\(' src/ui/frontend/src/pages/AdminScheduledActions.tsx` returns no matches; each of the four audited failure paths shows an in-app error toast with the same visible message the `alert()` would have shown (server `error` field when present, status fallback otherwise); `npm run build` in `src/ui/frontend` passes; repo-wide pages audit still finds zero product `alert()` call sites.

1. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`, add import after the existing `Toast` import (~line 12):

   ```ts
   import { ApiError, errorToastFromApiError, readApiError } from "../lib/toastDiagnostics"
   ```

   (`ToastMessage` type stays imported from `../components/Toast` — do not duplicate.)

2. In `toggleAutoMode` (~lines 476–487), replace the `if (!res.ok)` block:

   - Remove `const err = await res.json().catch(...)` and `alert(...)`.
   - When `!res.ok`, wrap in `try/catch`:
     - `await readApiError(res, `/api/admin/dispatch_tasks/${row.id}`, "PUT")`
     - In `catch`: `setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: `Update failed (${res.status})`, variant: "error" })`
     - `return` (do not call `loadData()` on failure).

3. In `handleRun` (~lines 499–507), replace the `if (!res.ok)` block the same way:

   - `readApiError(res, `/api/admin/dispatch_tasks/${row.id}/run`, "POST")`
   - Fallback message: `` `Run failed (${res.status})` ``

4. In `handleSave`, **edit branch** (~lines 580–583), replace the `if (!res.ok)` block:

   - `readApiError(res, `/api/admin/dispatch_tasks/${editRow.id}`, "PUT")`
   - Fallback message: `` `Save failed (${res.status})` ``

5. In `handleSave`, **add branch** (~lines 601–604), replace the `if (!res.ok)` block:

   - `readApiError(res, "/api/admin/dispatch_tasks", "POST")`
   - Fallback message: `` `Save failed (${res.status})` ``

   ⚠️ **Decision:** Use `readApiError` + `errorToastFromApiError` (same as `AdminAgentPrompts.tsx`) rather than bare `{ text: err.error, variant: "error" }` — visible toast text still comes from `body.error` when the server sends it (AC 2–3), and click-to-copy gets API path/method/status in the diagnostic bundle (AST-779) without changing the Toast component.

6. Do **not** change existing toast paths already on this page (`loadData` fetch failure ~line 329, AUTO edit guard ~line 539), modal UX, run/stop handlers, or `<Toast message={toast} onDone={clearToast} />` at page bottom.

7. Run audit from repo root:

   ```bash
   rg '\balert\(' src/ui/frontend/src/pages/
   ```

   Expect **no matches**. If any match appears outside this ticket's scope, stop and post 🛑 on parent **AST-761** — do not fix other pages in this ticket.

8. Run build:

   ```bash
   cd src/ui/frontend && npm run build
   ```

   Must exit 0 before stage commit.

---

## Self-Assessment

**Scope:** `Single-Component` — one React admin page only; four localized error-handler edits plus an import; no backend or shared component changes.

**Conf:** `high` — Toast state and `<Toast>` are already wired on this page; `readApiError` pattern is established on `AdminAgentPrompts.tsx` and `CandidateProfile.tsx`; audit and line numbers are verified on `origin/dev` merge base.

**Risk:** `low` — failure-path UX only; success paths, scheduler run/stop, and modal save-on-success behavior unchanged; wrong wiring would only affect error feedback on Scheduled Actions.

## Code rules check

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing `readApiError` / `errorToastFromApiError` helpers and page-local `toast` state — no new error helper. |
| §2.1 config | No config or state-machine changes. |
| §2.4 batch | No dispatch/batch logic touched. |
| §2.6 state machine | No entity state transitions. |
| §3.3 imports | Frontend-only; `toastDiagnostics` is an approved frontend lib module. |
| §3.5 naming | Follows existing admin page toast patterns. |
| Parent §2.10 (Toast for errors) | Removes remaining native `alert()` on touched UI; Radia fix-now satisfied for Scheduled Actions. |

No conflicts requiring plan revision.

## Execution contract

Binding per **plan-child**: **Stage 1** only; **one commit** on epic worktree during **build-child**, publish to **`origin/sub/AST-761/ast-780-scheduled-actions-error-toast`**. Do not edit `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`. On ambiguity — **`🛑 Stage 1 blocked`** on parent **AST-761**; stop.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-761/ast-780-scheduled-actions-error-toast` @ `47414cc`

### What's solid

- **Plan fidelity:** Stage 1 complete — four `alert()` call sites in `toggleAutoMode`, `handleRun`, and both `handleSave` branches replaced with `readApiError` + `errorToastFromApiError`; import from `toastDiagnostics` added; existing load-failure and AUTO edit-guard toasts untouched.
- **Audit:** `rg '\balert\(' src/ui/frontend/src/pages/` returns zero matches on the branch tip.
- **Pattern:** Matches established **AST-779** / `AdminAgentPrompts.tsx` error-toast wiring; server `error` text surfaces in `<Toast>` and diagnostics bundle attaches on failure.
- **Scope:** Single-component footprint matches Self-Assessment (`AdminScheduledActions.tsx` only in product code); Betty manifest honored — three AST-780 component tests replace alert spies; test-bible entry documents narrowed run.
- **Rules:** Frontend-only; no layer violations, config/state-machine, or debug-logging surfaces touched.

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

None — ready for **resolve-child** / UAT on Scheduled Actions error paths.

---

## Resolution

**2026-06-24 — Katherine (`resolve-child`)**

Radia posted **Review Posted** with **fix-now: none** and **discuss: none**. No product changes required beyond the shipped `code(AST-780)` @ `523abff` and Betty `merge-tests` @ `47414cc`.

**§9a dry-run:** `origin/sub/AST-761/ast-780-scheduled-actions-error-toast` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-761-ui-error-toast`**.

**Outcome:** Ticket advanced to **User Testing** for Susan UAT on Scheduled Actions error paths (AUTO toggle failure, manual Run failure, edit/add save failures — toast not blocking `alert()`).
