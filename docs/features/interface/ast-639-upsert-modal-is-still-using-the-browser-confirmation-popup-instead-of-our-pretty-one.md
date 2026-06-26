# AST-639 — Upsert modal is still using the browser confirmation popup instead of our pretty one.

<!-- linear-archive: AST-639 archived 2026-06-23 -->

## Linear archive (AST-639)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-639/upsert-modal-is-still-using-the-browser-confirmation-popup-instead-of  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Native browser confirmation dialogs break visual consistency with the rest of Astral's admin and candidate UI. Susan noticed the Data Management JSON upsert flow still pops the browser chrome when applying pasted rows, even though the product already ships a themed confirm dialog (`UserPrompt` / `useUserConfirm`) wired through the main navigation shell. This feature eliminates remaining production uses of `window.confirm` so destructive and irreversible actions feel the same everywhere operators and candidates interact with the app.

## Functional scope

1. **Audit** — Inventory every production call to native browser confirmation (`window.confirm`) in the React frontend. Record each call site and the user action it guards (e.g. apply upsert, delete candidate, clear API key).
2. **Data Management upsert apply** — When an administrator clicks Save on the Table Upsert modal with valid JSON pasted, show the themed confirm dialog (not the browser popup) before posting the upsert. Preserve the existing message intent: confirm table name and that unrelated rows remain untouched. Cancel leaves the modal open with JSON intact; confirm proceeds with the upsert and existing success/error toast behavior.
3. **Manage Candidates destructive actions** — Replace native confirms on logical candidate delete and on clear-API-key with the themed confirm dialog. Use appropriate titles, button labels, and danger styling where the action is destructive or hard to undo, consistent with other delete flows in the product (e.g. board search delete).
4. **Themed dialog contract** — All migrated confirms use the shared `useUserConfirm` hook so they inherit Astral modal styling (overlay, card, titled header, Cancel / confirm buttons). Message text may be refined for clarity but must not weaken the warning meaning Susan approved in the original brief.
5. **Verification artifact** — Deliver a short audit summary (in the dev plan or a Linear comment at Code Complete) listing each former `window.confirm` site and confirming it now uses the themed dialog or documenting why it remains excluded.

## Boundaries

* **In scope:** Production UI paths only — pages and components rendered inside the authenticated app shell where `UserPromptProvider` is available.
* **Out of scope:** Changing upsert API semantics, validation, or toast copy beyond what confirm/cancel requires; adding new confirmation steps where none existed; `window.alert` or `window.prompt` unless discovered during audit and Susan explicitly expands scope; backend or debug logging.
* **Excluded by design:** `UserPrompt` and `Modal` internal fallbacks to `window.confirm` when no provider is present (unit tests and isolated Storybook renders). Do not remove those fallbacks — tests depend on them.
* **Must not break:** Existing Modal dirty-state discard flow (already uses themed confirm when provider is present); flows already on `useUserConfirm` (intake, board searches, intake chat); Data Management upsert success/error handling after confirm.

## Acceptance criteria

1. On Data Management → Table Upsert: paste JSON, choose a table, click Save — Susan sees the Astral-themed confirm dialog, not the browser-native popup. Cancel dismisses the dialog and does not post; confirm runs the upsert and shows the same outcome toasts as today.
2. On Manage Candidates: logical delete and clear API key each show the themed confirm dialog with clear action labels; cancel aborts; confirm performs the same API action as today.
3. A frontend audit finds no remaining `window.confirm` in production page/components code except documented test-only fallbacks in shared modal/prompt infrastructure.
4. Component tests that mocked or asserted `window.confirm` for migrated flows are updated so CI passes without relying on native browser dialogs in wrapped test trees (provider present).
5. No regression in pages already using `useUserConfirm` (intake resume/start-over, board search delete/mode switch).

## Dependencies and blockers

none.

## Open questions

none.

---

## Original brief

Please do a quick audit where any such browser confirmations are used and confirm they are using our pretty one.

### Comments

#### chuckles — 2026-06-15T01:44:32.083Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-639 (parent) | ftr/AST-639-themed-confirm-dialog |
| AST-659 | sub/AST-639/AST-659-themed-confirm-native-browser |

**Epic worktree:** `astral-AST-639/` — one active sub checked out at a time.

**Parent:** AST-639

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
