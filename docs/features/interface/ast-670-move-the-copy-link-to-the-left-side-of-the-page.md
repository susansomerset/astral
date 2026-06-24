# AST-670 — Move the "copy" link to the left side of the page

<!-- linear-archive: AST-670 archived 2026-06-23 -->

## Linear archive (AST-670)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-670/move-the-copy-link-to-the-left-side-of-the-page  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On **Execution History** (`/admin/performance`), expanding a batch row opens an inline log panel with a **Copy** control that copies log lines to the clipboard. That control sits on the **right** side of the log toolbar. The main ledger table is wide (many columns plus per-item and cost links), so Susan must horizontal-scroll to reach **Copy** when inspecting logs — friction during dispatch debugging and UAT. This enhancement keeps the same copy behavior but places the control on the **left**, visible without hunting at the far edge of a wide table.

## Functional scope

* **Execution History expanded log panel:** Reposition the existing **Copy logs to clipboard** control (the button labeled **Copy** / **Copied** after use) from the right side of the expanded batch log toolbar to the **left** side of that toolbar, within the same expanded row panel users already see when they click a ledger row.
* **No behavior change to copy:** Clicking the control still copies all log entries for the expanded batch to the clipboard in the same text format as today; only placement changes.
* **Visible without horizontal scroll for the control itself:** With a typical expanded row on Execution History, the **Copy** control is reachable at the left edge of the viewport (or left edge of the log panel) without scrolling horizontally solely to find the button — even when the ledger table requires horizontal scroll for far-right columns.

## Boundaries

* **Execution History only** — does not relocate copy controls on Agent Timesheets, Scheduled Actions, modals, or other admin screens.
* **Does not change** log fetch, log table columns, batch expand/collapse, batch_id link, Agent Data modal, candidate filter ([AST-628](https://linear.app/astralcareermatch/issue/AST-628) / [AST-656](https://linear.app/astralcareermatch/issue/AST-656)), frozen-column table layout ([AST-633](https://linear.app/astralcareermatch/issue/AST-633)), or ledger column set.
* **Does not add** new copy targets (e.g. copy batch_id, copy single log line) or change clipboard payload format.
* **No backend or debug-logging work** — UI placement only.

## Acceptance criteria

1. On Execution History, expand any batch row that has log entries; the **Copy** control appears on the **left** side of the log panel toolbar (not right-aligned).
2. Without horizontal scrolling, the **Copy** control is visible when the expanded log panel is in view (Susan can click it from the left side of the page).
3. Clicking **Copy** still copies the full log text for that batch to the clipboard; content matches pre-change behavior for the same batch.
4. After copy, transient **Copied** feedback still appears on the control as today.
5. Collapsed rows, empty log state, and loading log state are unchanged except that any **Copy** control shown uses left placement when present.
6. No regressions to row expand/collapse, sorting, filters, or navigation to Agent Timesheets via cost link.

## Dependencies and blockers

None. Adjacent Execution History work ([AST-656](https://linear.app/astralcareermatch/issue/AST-656) candidate dropdown) is in User Testing but does not block this layout change.

## Open questions

None.

---

## Original brief

When I open the Execution History page, the copy link appears to the right of the page, I want it to the left of the page so I don't have to horizontal scroll to find it.

### Comments

#### chuckles — 2026-06-15T17:18:35.149Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-670 (parent) | ftr/AST-670-move-the-copy-link-to-the-left-side-of-the-page |
| AST-672 | sub/AST-670/AST-672-execution-history-copy-left |

**Epic worktree:** `astral-AST-670/` — one active sub checked out at a time.

**Parent:** AST-670

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
