---
id: pattern.ui.icon-control
name: Icon-only compact controls
status: approved
proposed_in: AST-1166
approved_by: Archie
approved_at: "2026-08-11"
canonical_refs:
  - path: src/ui/frontend/src/App.css
    symbol: ".icon-control"
related_statutes:
  - astral.ui.frontend-file-placement
  - astral.ui.naming-conventions
  - astral.standards.dry-and-focused-functions
  - astral.standards.names-not-ticket-ids
supersedes: null
superseded_by: null
---

# Problem

List row actions and other compact glyph controls are implemented as cramped labeled mini-text, one-off icon button classes, or unstyled chrome. Operators cannot tell icon actions from labeled buttons, and tiny text (e.g. list Skip as "Sk") fails as a control.

# Solution shape

Use one icon-control class in `App.css` (pointer in `canonical_refs`):

- Markup: `className="icon-control"` on a `<button type="button">`.
- Content is a glyph or a single initial only — not a word label. Visible text like "Skip" / "Edit" / "View" on a list row action is wrong; use `title` and `aria-label` for the accessible name.
- Use for: list row actions (Skip, Edit, View, Resurrect, pipeline state moves), modal × dismiss, chevron expand/collapse.
- Do not combine with `btn primary` / `secondary` / `danger`. This is a separate family, not a size variant of labeled buttons.
- Styles live only in `src/ui/frontend/src/App.css`. Do not add a second stylesheet or a wrapper component as a substitute for this class.
- Do not restyle a single call site with extra `font-size` / `padding` / inline color that recreates a third family.
- Do not change what the control does (API, enablement) when applying this pattern — presentation only.

## When not to use

- Labeled text actions (Save, Cancel, Delete, modal "Skip This Job") — use `pattern.ui.shared-button-roles`.
- Nav links, side-tab / section chrome, rubric text links, checkbox/radio inputs.
- Replacing leftover icon/mini-text classes on a screen this ticket does not own — remediations are a separate change.

## Notes

Proposed in parent AST-1166 Architectural definition. Archie Todo on that Description is approval to treat this id as catalog law. Shared CSS landed with AST-1300; list/icon call-site remediations are AST-1302. Modal labeled Skip stays a labeled `btn`, not an icon-control.
