---
id: pattern.ui.shared-button-roles
name: Shared labeled-button roles
status: approved
proposed_in: AST-1166
approved_by: Archie
approved_at: "2026-08-11"
canonical_refs:
  - path: src/ui/frontend/src/App.css
    symbol: ".btn.primary"
  - path: src/ui/frontend/src/App.css
    symbol: ".btn.secondary"
  - path: src/ui/frontend/src/App.css
    symbol: ".btn.danger"
  - path: src/ui/frontend/src/App.css
    symbol: ".btn.primary.in-flight"
  - path: src/ui/frontend/src/App.css
    symbol: ".btn.in-row"
related_statutes:
  - astral.ui.frontend-file-placement
  - astral.ui.naming-conventions
  - astral.standards.dry-and-focused-functions
  - astral.standards.names-not-ticket-ids
  - astral.standards.no-hardcoded-sets
supersedes: null
superseded_by: null
---

# Problem

Operators meet several labeled-button looks for the same roles (commit, cancel, destroy, busy). Parallel families (`modal-btn`, `dep-btn`, `list-page-bulk-btn`, toolbar element selectors, one-off inline backgrounds) force a re-learn on every screen and block a single remediations pass. Full-size labeled buttons also stretch data-table rows when the same roles sit in a cell.

# Solution shape

Use one labeled-button class family in `App.css` (pointers in `canonical_refs`):

- Always pair base `btn` with exactly one role: `primary` | `secondary` | `danger`. Bare `btn` is incomplete.
- `btn primary` — affirmative / commit (Save, Continue, Land Meteorite, Run, Generate idle, Add, Export, Retry, Select all when framed as a page action). Green (`--cta-green`).
- `btn secondary` — cancel / neutral alternate (Cancel, Clear selection, Start over, non-destructive dismiss, Preview when not the commit). Muted elevated + border.
- `btn danger` — destructive (Delete / kill / destructive confirm). Red (`--danger`).
- `btn primary` + `in-flight` — the same primary control while a slow action runs. Gold (`--accent-gold`). Do not put `in-flight` on `secondary` or `danger`.
- Optional size modifier `in-row` — never a fifth role. Always pair with exactly one role: `btn primary in-row`, `btn secondary in-row`, `btn danger in-row`, and `btn primary in-flight in-row` when that control is already the in-flight primary. About 60% the height of the full labeled button (cut vertical padding; keep the 14px label; do not scale type to icon-control size). Use only on labeled shared-role buttons that sit in a data-table row.
- Markup: `className="btn primary"`, `className="btn secondary"`, `className="btn danger"`, `className="btn primary in-flight"`, `className="btn primary in-row"`, `className="btn secondary in-row"`, `className="btn danger in-row"`, `className="btn primary in-flight in-row"` (space-separated; not BEM `btn--primary`).
- Styles live only in `src/ui/frontend/src/App.css`. Do not add a second stylesheet or a wrapper component as a substitute for these classes.
- Do not invent a fifth labeled role or a parallel family (`dep-btn`, `modal-btn`, gold-vs-green as two systems, inline `style={{ background }}` on these actions).
- Do not change what the control does (API, enablement, label meaning) when applying this pattern — presentation only.

## When not to use

- Icon-only compact actions (list row Skip/Edit/View, modal ×, chevrons) — use `pattern.ui.icon-control`.
- Nav links, side-tab / section chrome, rubric text links, checkbox/radio inputs — not buttons.
- Page, toolbar, modal-footer, or card-footer labeled buttons — keep the full `.btn` size; do not add `in-row`.
- Replacing leftover families on a screen this ticket does not own — remediations are a separate change.

## Notes

Proposed in parent AST-1166 Architectural definition. Archie Todo on that Description is approval to treat this id as catalog law. Shared CSS landed with AST-1300; labeled call-site remediations are AST-1301. In-row size amendment: AST-1309 / AST-1317 (Archie Todo on AST-1309 is approval to treat `in-row` as catalog law). Call-site apply of `in-row` is AST-1318. Do not reopen AST-1166 roles.
