# AST-761 — UI Error popups still not using our pretty popup component.

<!-- linear-archive: AST-761 archived 2026-07-22 -->

## Linear archive (AST-761)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-761/ui-error-popups-still-not-using-our-pretty-popup-component  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan hit a jarring native browser alert on Scheduled Actions when a dispatch task could not run (for example, a task_key that is not schedulable). The rest of the admin UI already surfaces API errors through the in-app Toast. This feature closes that gap so error feedback is consistent, readable, and on-brand across the product.

## Functional scope

**Codebase audit — native browser alert call sites (complete):**

| Page | User action | Currently uses native alert |
| -- | -- | -- |
| Scheduled Actions | Toggle AUTO on a row | Yes |
| Scheduled Actions | Run a task manually | Yes |
| Scheduled Actions | Save an edited task (modal) | Yes |
| Scheduled Actions | Create a new task (modal) | Yes |

No other product pages use native browser `alert()` for error feedback. Confirmation dialogs already use the themed UserPrompt dialog (not native confirm) wherever UserPromptProvider wraps the app.

**Capabilities:**

* Replace every native browser alert used for API error feedback with the existing Toast component, showing the server error message when present or a sensible fallback when not.
* Wire Toast on Scheduled Actions using the same state and hook pattern already used on other admin pages.
* Preserve the error text the user would have seen in the alert (for example, `dispatch_task task_key not schedulable: 'vet_inflow_discovery'`).

## Boundaries

* Does not replace confirmation dialogs — those already use UserPromptProvider; test/Storybook fallback to native confirm without a provider stays as-is.
* Does not add new error surfacing on pages that currently swallow failures silently (no alert and no toast).
* Does not change backend error payloads, validation rules, or dispatch scheduling logic.
* Does not redesign or replace the Toast component or introduce a new notification system.
* **ASTRAL_CODE_RULES §2.10** — Toast for errors; Radia **fix-now** on any new or remaining native `alert()` / user-facing `window.confirm()` in touched UI.

## Acceptance criteria

1. A full frontend audit finds no remaining native browser alert dialogs used to show API or action errors to the user.
2. On Scheduled Actions, each of the four audited failure paths above shows an in-app Toast with error styling and the same message the native alert would have shown.
3. Running a non-schedulable task_key (for example `vet_inflow_discovery`) shows that server error text in Toast, not a blocking browser dialog.
4. After an error Toast appears, the page remains immediately usable without dismissing a modal browser alert.
5. Toast and UserPrompt behavior on all other pages is unchanged.

## Dependencies and blockers

* [AST-749](https://linear.app/astralcareermatch/issue/AST-749/admin-dispatch-task-keys-and-scheduled-actions-alignment-task-keys-vs) (Scheduled Actions / dispatch task_key alignment) touches the same page; not a blocker, but both changes may merge close together.
* none.

## Open questions

(none)

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-761](https://linear.app/astralcareermatch/issue/AST-761/ui-error-popups-still-not-using-our-pretty-popup-component) (parent) | ftr/AST-761-ui-error-toast |
| [AST-780](https://linear.app/astralcareermatch/issue/AST-780/scheduled-actions-error-toast-ui-error-popups-still-not-using-our) | sub/AST-761/ast-780-scheduled-actions-error-toast |

**Epic worktree:** `astral-AST-761/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | c41d4c00-8913-4721-8604-8d3c796dbd46 |
| Betty | qa | f7015fd5-001b-47f1-862a-85bfca2a325a |
| Radia | review | 739f8fe3-99e0-47c3-a4ac-5c5bdbd89b72 |

---

## Original brief

Message reads: dispatch_task task_key not schedulable: 'vet_inflow_discovery'

Locate all cases where this type of alert is posted to the user, and revise to use our nice popup component instead.

LIST THEM HERE FIRST, as part of discussion.  Do not assign the search to a dev.

### Comments

#### chuckles — 2026-06-24T03:03:16.496Z
[thread-missing] blocked: Cursor agent transcript for `1bf08327-3ac6-47fa-b35d-51455cd6552f` is not on this host (petrichor). Run this job from **chuckles server (HP ProDesk)** where that conversation exists.

Do **not** `agent create-chat` or `--resume` here — that forks a new thread the other host cannot use.

Watcher rule `datt` on `AST-761`.

— Chuckles

#### chuckles — 2026-06-23T20:01:33.023Z
[check-linear] Discussion — ASTRAL_CODE_RULES §2.10 added (@susan)

#### susan — 2026-06-23T19:54:38.231Z
Please add content to the code rules to make sure radia catches any future variants.

---

_Implementation detail may live in git history on `origin/dev`._
