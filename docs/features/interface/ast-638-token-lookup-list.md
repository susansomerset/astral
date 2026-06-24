# AST-638 — Token lookup list

<!-- linear-archive: AST-638 archived 2026-06-23 -->

## Linear archive (AST-638)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-638/token-lookup-list  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators authoring prompt templates type `{$TOKEN}` placeholders in shared `TokenTextarea` fields across Manage Tasks, Manage Agents, and Anthropic Ad Hoc. The token lookup dropdown currently opens pinned to the top of the textarea and covers the text being edited, forcing guesswork while typing partial token names. This is a usability bug on a shared component — fixing placement once restores readable autocomplete everywhere that component is used.

## Functional scope

1. **Trigger-adjacent placement** — When the token lookup list is visible, it appears below the in-text position where the active `{$` trigger starts (the partial token being typed), not over the top of the textarea. The operator can read what they have typed while the list is open.
2. **Shared component fix** — The correction lives in the shared token-autocomplete textarea component so every current and future screen that uses it inherits the behavior without per-page duplication.
3. **Dismissal unchanged** — The list continues to open on a valid partial `{$…` entry, filter matches as today, and close when: the token is closed with `}`, the operator picks a token, presses Escape, clicks outside, or enters characters that invalidate the partial match. Keyboard navigation (arrow keys, Enter, Tab) and mouse selection behave as they do now.
4. **Viewport edge case** — When there is not enough room below the trigger line (e.g. cursor on the last visible line inside a modal), the list should remain usable — prefer flipping above the trigger rather than clipping off-screen or covering the typed text.

## Boundaries

* Does not change which tokens appear in the list, token registry, or any admin API endpoints.
* Does not alter token insertion format (`{$TOKEN_NAME}`) or preview/resolve behavior on parent screens.
* Does not add autocomplete to new surfaces — only fixes placement of the existing dropdown.
* Does not change textarea styling, row counts, or modal layout outside what is required for dropdown positioning.
* No backend or debug-logging work (UI-only per Code Rules).

## Acceptance criteria

1. On Manage Tasks, open any task's edit modal, type `{$` in any prompt segment — the lookup list appears below the trigger line and the partial token text in the textarea remains visible while typing.
2. Typing `}` to close a token manually dismisses the lookup list without requiring Escape or a click.
3. Manage Agents (Add and Edit modals) and Anthropic Ad Hoc (User, Cache, NoCache prompt tabs) show the same corrected placement when triggering autocomplete.
4. Selecting a token from the list or via keyboard still inserts the full `{$TOKEN}` and dismisses the list, with cursor restored as today.
5. Existing `TokenTextarea` component tests pass; tests cover that the dropdown no longer overlays the textarea origin when open.

## Dependencies and blockers

None.

## Open questions

None.

---

## Original brief

The token lookup list dropdown should appear below where {$ appears, and disappear after } is entered.  Right now it covers the text input and makes it fun to try to guess what I'm typing for the prompt token.

### Comments

#### chuckles — 2026-06-14T20:40:46.805Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-638 (parent) | ftr/ast-638 |
| AST-643 | sub/AST-638/AST-643-trigger-adjacent-token-lookup-placement |

**Epic worktree:** `astral-AST-638/` — one active sub checked out at a time.

**Parent:** AST-638

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
