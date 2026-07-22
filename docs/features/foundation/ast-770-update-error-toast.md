# AST-770 — Update error toast

<!-- linear-archive: AST-770 archived 2026-07-22 -->

## Linear archive (AST-770)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-770/update-error-toast  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators often see a brief error toast and lose the detail before they can report it in Linear. The shared toast is the primary in-app error surface across admin and candidate flows; it currently auto-dismisses in a few seconds and shows only a short message. This epic improves error-toast usability so Susan and the team can capture enough context to file actionable bugs without hunting logs first.

## Functional scope

* **Longer error visibility:** Error-variant toasts stay on screen for **15 seconds** before auto-dismiss (app-wide, via the shared toast component). Success and info toasts keep their current shorter duration.
* **Click-to-copy diagnostics:** Error toasts are clickable. A click copies a **multi-line diagnostic bundle** to the clipboard suitable for pasting into a Linear issue.
* **Minimum copy payload:** Always include the user-visible error message and a timestamp. When available from the error source, also include: page or route context, API path or operation, HTTP status, server error body text, and **selected candidate or other entity identifiers** when the UI has them.
* **Backend enrichment:** When readily available, backend JSON error responses should include **all context helpful for troubleshooting and confirming resolution** (e.g. exception type, stack trace or traceback summary, request identifiers). The toast copy path assembles client-side context plus any enriched fields returned by the API.
* **Copy feedback:** After a successful copy, the user gets brief in-toast confirmation (e.g. copied state or label) without losing the remaining display time.
* **Affordance:** Error toasts visually indicate they are interactive (e.g. pointer cursor and/or copy hint) so operators discover click-to-copy.

## Boundaries

* **Error toasts only** for the 15-second duration and click-to-copy behavior; success and info toasts unchanged.
* Does **not** replace the Admin Performance Monitor or other log viewers — this is a lightweight clipboard shortcut from the toast.
* Does **not** add AST-538 debug-logging contract requirements on backend batch/dispatch paths; API error enrichment for toast copy is in scope where readily available.
* Does **not** introduce a second notification system — extend the existing shared toast.
* Must **not** break existing toast usage on pages that only pass a short error string today.
* Must **not** expose secrets (tokens, session values) in copied text.

## Acceptance criteria

1. Any error toast triggered from a representative admin page and a representative candidate page remains visible for approximately **15 seconds** before dismissing.
2. Success and info toasts still auto-dismiss on their **current** shorter schedule (unchanged).
3. Clicking an error toast puts a multi-line string on the clipboard that includes at least the visible error message and enough request/context detail to identify where the failure occurred.
4. When the page has a selected candidate or other entity, the copied bundle includes that identifier.
5. When the backend returns enriched error fields (e.g. exception type, stack trace), those fields appear in the copied bundle.
6. After click-copy, the user sees clear confirmation that copy succeeded.
7. Error toasts are visually distinguishable as clickable before interaction.
8. Existing toast component tests pass with updates for the new error-toast behavior.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-770 (parent) | ftr/AST-770-update-error-toast |
| AST-779 | sub/AST-770/AST-779-error-toast-diagnostics |

**Epic worktree:** `astral-AST-770/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |

---

## Original brief

Definitely extend the toast appearance to 15 seconds.

If possible, let the user click on the toast and copy to the clipboard the stacktrace or other helpful details about origin or basis of the error so it can be copied into a linear issue for review.

### Comments

#### chuckles — 2026-06-23T20:29:50.709Z
@susan

1. For diagnostics beyond the visible message: should this epic **extend backend JSON error responses** with technical fields (e.g. exception type, stack trace) for copy, or is a **client-assembled bundle** (message + route + status + API path + server error body when already returned) sufficient for v1?
2. When the UI has a **selected candidate or other entity**, should the copied bundle always include that identifier when available?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
