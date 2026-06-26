# AST-635 — When the Generate button is clicked, make it yellow while it's running.

<!-- linear-archive: AST-635 archived 2026-06-23 -->

## Linear archive (AST-635)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-635/when-the-generate-button-is-clicked-make-it-yellow-while-its-running  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Craft **Generate** on artifact criterion pages kicks off a slow LLM call. Today the control stays green (`dep-btn save`) and only the label changes to **Generating…**, which is easy to miss. Susan wants a clear yellow in-flight state so operators immediately see that generation is running and the control is temporarily unavailable.

## Functional scope

1. **Artifact craft Generate / Regenerate** — On every Artifacts screen that uses the shared artifact editor Generate control (criteria tabs, base resume content where Generate is shown) and on **Company Search Terms**, while an in-flight generate request runs after the user clicks **Generate** or **Regenerate**, the button background uses the product yellow/gold accent (same family as the existing gold accent in the UI).
2. **In-flight window** — Yellow from click until the generate call completes (success or failure) and the UI returns to idle (not while the regenerate confirmation modal is open waiting for confirm).
3. **Disabled while running** — Button remains disabled during generation as today; yellow applies in the disabled generating state.
4. **Label** — Continue showing **Generating…** text while running (existing behavior).

## Boundaries

* Does not change **Generate Artifacts**, **Generate Profile**, **Preview Materials**, **Save**, **Cancel**, dispatch Run/Stop, or other non-craft generate actions unless Susan expands scope (see open questions).
* No backend, API, or manifest changes.
* No new loading indicators beyond button color.
* Does not alter confirm-regenerate modal styling except the confirm button already uses red for destructive confirm.
* Must not change green **Save** buttons elsewhere on the same pages.

## Acceptance criteria

1. On an artifact criterion page with **Generate** visible, click **Generate**: from click until the request finishes, the button background is visibly yellow/gold (not green).
2. On a page with existing artifact content, click **Regenerate** and confirm: same yellow/gold while generating.
3. **Company Search Terms** **Generate** / **Regenerate** follows the same rule.
4. After success or error toast, the button returns to default green styling and the correct label (**Generate** / **Regenerate**).
5. **Save** and **Cancel** button colors on those pages are unchanged.

## Dependencies and blockers

none.

## Open questions

1. Should **Generate Artifacts** on the Recommended Job Report (and its **Working…** in-flight state) use the same yellow styling, or only artifact-menu **Generate** / **Regenerate** buttons?
   1. UI-call-to-AI should use the same button component.  Yellow when active, green when ready.

### Comments

#### chuckles — 2026-06-14T20:59:14.487Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-635 (parent) | ftr/ast-635 |
| AST-645 | sub/AST-635/AST-645-yellow-in-flight-ai-generate-buttons |

**Epic worktree:** `astral-AST-635/` — one active sub checked out at a time.

**Parent:** AST-635

— Chuckles

#### chuckles — 2026-06-14T18:30:37.445Z
@susan Open questions on AST-635:

1. Should **Generate Artifacts** on the Recommended Job Report (and its **Working…** in-flight state) use the same yellow styling, or only artifact-menu **Generate** / **Regenerate** buttons?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
