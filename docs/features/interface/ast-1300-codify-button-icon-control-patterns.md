# AST-1300 — Codify button + icon-control patterns (Button consistency)

- **Linear:** [AST-1300](https://linear.app/astralcareermatch/issue/AST-1300/codify-button-icon-control-patterns-button-consistency)
- **Parent:** [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency)
- **Publish ref:** `sub/AST-1166/AST-1300-codify-button-icon-control-patterns`

Land the parent Discussion-locked button catalog as two approved `canon/patterns/ui/` entries, plus the shared `App.css` classes those entries point at, so AST-1301 / AST-1302 can consume the ids and class names. Does not remediates any JSX call site and does not delete today’s `modal-btn` / `dep-btn` / `list-page-bulk-btn` / peer families.

## Traceability

| Parent item | This plan |
|-------------|-----------|
| Purpose — lock catalog, then codify as patterns before call-site rewrites | Stages 1–2 |
| Functional scope 1 (Discussion-locked catalog) | Already locked on parent Description — do not reopen |
| Functional scope 2 (codify as patterns) | Stages 1–2 |
| Functional scope 3–6 (inventory, labeled sweep, list icons, exception register) | N/A — AST-1301 / AST-1302 |
| AC1 — canon contains `pattern.ui.shared-button-roles` and `pattern.ui.icon-control` matching the Discussion catalog | Stage 2 (files) + Stage 1 (canonical_refs) |
| AC2–7 | N/A — sibling boundaries (labeled sweep / icon-control sweep / exception register) |
| Child AC (same sentence as parent AC1) | Stages 1–2 |
| Child “shared styles/contract implementers will consume” | Stage 1 |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.css` | TOC entries 14–15; append `.btn` role rules and `.icon-control` rules (exact CSS below) | ui |
| `canon/patterns/ui/pattern.ui.shared-button-roles.md` | New — `status: approved` catalog entry | docs |
| `canon/patterns/ui/pattern.ui.icon-control.md` | New — `status: approved` catalog entry | docs |
| `canon/patterns/README.md` | Approved-set count + harvested-corpus rows for the two new ids | docs |
| `canon/patterns/HARVEST.md` | Supporting-package rows + Crosswalk rows only (not the define-parent AC cite map) | docs |

**Do not touch:** any `src/ui/frontend/src/**/*.{tsx,ts}` call site; `src/ui/api/**`; `src/utils/config.py`; `docs/ASTRAL_CODE_RULES.md`; `tests/**`; `docs/test-bible/**`; existing `.modal-btn` / `.dep-btn` / `.list-page-bulk-btn` / `.timesheet-export-btn` / `.manage-email-toolbar button` / `.entity-skip-btn` / `.job-list-icon-btn` / `.modal-close` / `.collapsible-panel-chevron-btn` / `.sql-hist-btn` / `.dispatch-log-copy-btn` / `.list-page-edit-btn` rules (leave them in place for siblings to retire).

**Do not add:** `Button.tsx`, `IconControl.tsx`, a second stylesheet, or a `config.py` color/enum block.

---

## Stage 1: Shared CSS classes in `App.css`

**Done when:** `App.css` defines unused (no JSX switch yet) classes `.btn.primary`, `.btn.secondary`, `.btn.danger`, `.btn.primary.in-flight`, and `.icon-control` with the exact declarations below. Existing screens look unchanged because no call site is edited. `rg -n 'className=.*\\bbtn\\b|className=.*icon-control' src/ui/frontend/src` still finds no TSX consumers.

1. In `src/ui/frontend/src/App.css`, in the TOC comment at the top of the file, append these two lines after the existing `13. Execution History` line (do not renumber 1–13):

```
 * 14. Shared button roles
 * 15. Icon control
```

2. At the **end** of `App.css` (after the last existing rule, currently `.intake-topic-menu-list`), append exactly this block — copy, do not restyle, do not add `min-width` / `min-height` / extra shadows / new hex colors. Tokens already exist on `:root` (`--cta-green`, `--cta-green-hover`, `--accent-gold`, `--accent-gold-hover`, `--bg-elevated`, `--bg-deep`, `--border`, `--text-secondary`, `--text-primary`, `--danger`, `--danger-hover`).

```css
/* === 14. Shared button roles === */

.btn {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn.primary {
  background: var(--cta-green);
  border: none;
  color: var(--bg-deep);
}

.btn.primary:hover:not(:disabled) {
  background: var(--cta-green-hover);
}

.btn.primary.in-flight,
.btn.primary.in-flight:disabled {
  background: var(--accent-gold);
  border: none;
  color: var(--bg-deep);
}

.btn.primary.in-flight:hover:not(:disabled) {
  background: var(--accent-gold-hover);
}

.btn.secondary {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.btn.secondary:hover:not(:disabled) {
  background: var(--border);
  color: var(--text-primary);
}

.btn.danger {
  background: var(--danger);
  border: none;
  color: #fff;
}

.btn.danger:hover:not(:disabled) {
  background: var(--danger-hover);
}

.btn:disabled {
  cursor: not-allowed;
}

.btn.danger:disabled {
  opacity: 0.4;
}

/* === 15. Icon control === */

.icon-control {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  line-height: 1.2;
  font-family: inherit;
}

.icon-control:hover:not(:disabled) {
  color: var(--text-primary);
  border-color: var(--accent-gold);
}

.icon-control:disabled {
  opacity: 0.45;
  cursor: default;
}
```

3. Do **not** alias old families onto these selectors (` .modal-btn.save { }` stays as it is). Do **not** change any TSX `className`.

⚠️ **Decision:** CSS lives only in `App.css` (§3.5 / `astral.ui.frontend-file-placement`). No `styles/buttons.css`, no React wrapper. Parent locked **class names**, not a component API — siblings remediates by swapping `className` strings.

⚠️ **Decision:** Visual values are a literal copy of today’s intentional baselines: `.btn.primary` / `.secondary` / `.danger` / `.primary.in-flight` match `.modal-btn.save` / `.cancel` / `.danger` / `.save.in-flight` (same declarations as `.dep-btn.*`). `.icon-control` matches `.job-list-icon-btn` plus `font-family: inherit`. Disabled habits match `.dep-btn.danger:disabled` (opacity 0.4) and leave in-flight gold at full opacity (no extra `.btn:disabled { opacity }` that would dim busy primaries). `#fff` on danger is copied from the existing rules, not a new hex.

⚠️ **Decision:** Do not invent hit-target `min-width` / `min-height` on `.icon-control`. Parent did not specify a new size; siblings apply the class as-is.

---

## Stage 2: Approved pattern files + catalog indexes

**Done when:** `canon/patterns/ui/pattern.ui.shared-button-roles.md` and `canon/patterns/ui/pattern.ui.icon-control.md` exist with the exact frontmatter + body below (`status: approved`, `proposed_in: AST-1166`, `approved_by: Archie`, `approved_at: "2026-08-11"`, ≥1 `canonical_refs` each pointing at Stage 1 selectors). `canon/patterns/README.md` lists both as approved. `canon/patterns/HARVEST.md` has supporting-package + Crosswalk rows. SCHEMA-required keys only — no undeclared frontmatter. Body section order is `# Problem`, `# Solution shape`, `## When not to use`, `## Notes`.

1. Create `canon/patterns/ui/pattern.ui.shared-button-roles.md` with **exactly** this content:

```markdown
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
related_statutes:
  - astral.ui.frontend-file-placement
  - astral.ui.naming-conventions
  - astral.standards.dry-and-focused-functions
  - astral.standards.names-not-ticket-ids
supersedes: null
superseded_by: null
---

# Problem

Operators meet several labeled-button looks for the same roles (commit, cancel, destroy, busy). Parallel families (`modal-btn`, `dep-btn`, `list-page-bulk-btn`, toolbar element selectors, one-off inline backgrounds) force a re-learn on every screen and block a single remediations pass.

# Solution shape

Use one labeled-button class family in `App.css` (pointers in `canonical_refs`):

- Always pair base `btn` with exactly one role: `primary` | `secondary` | `danger`. Bare `btn` is incomplete.
- `btn primary` — affirmative / commit (Save, Continue, Land Meteorite, Run, Generate idle, Add, Export, Retry, Select all when framed as a page action). Green (`--cta-green`).
- `btn secondary` — cancel / neutral alternate (Cancel, Clear selection, Start over, non-destructive dismiss, Preview when not the commit). Muted elevated + border.
- `btn danger` — destructive (Delete / kill / destructive confirm). Red (`--danger`).
- `btn primary` + `in-flight` — the same primary control while a slow action runs. Gold (`--accent-gold`). Do not put `in-flight` on `secondary` or `danger`.
- Markup: `className="btn primary"`, `className="btn secondary"`, `className="btn danger"`, `className="btn primary in-flight"` (space-separated; not BEM `btn--primary`).
- Styles live only in `src/ui/frontend/src/App.css`. Do not add a second stylesheet or a wrapper component as a substitute for these classes.
- Do not invent a fifth labeled role or a parallel family (`dep-btn`, `modal-btn`, gold-vs-green as two systems, inline `style={{ background }}` on these actions).
- Do not change what the control does (API, enablement, label meaning) when applying this pattern — presentation only.

## When not to use

- Icon-only compact actions (list row Skip/Edit/View, modal ×, chevrons) — use `pattern.ui.icon-control`.
- Nav links, side-tab / section chrome, rubric text links, checkbox/radio inputs — not buttons.
- Replacing today’s unused leftover families on a screen this ticket does not own — remediations are a separate change.

## Notes

Proposed in parent AST-1166 Architectural definition. Archie Todo on that Description is approval to treat this id as catalog law. Shared CSS landed with AST-1300; call-site remediations are AST-1301.
```

2. Create `canon/patterns/ui/pattern.ui.icon-control.md` with **exactly** this content:

```markdown
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
```

3. In `canon/patterns/README.md`, in the **Harvested corpus** intro sentence, change `Seven catalog entries below are \`status: approved\`` to `Nine catalog entries below are \`status: approved\`` (keep `; one is \`status: proposed\``).

4. In the same harvested-corpus table, immediately after the `pattern.ui.admin-endpoint` row, insert:

```
| `pattern.ui.shared-button-roles` | approved | `ui/pattern.ui.shared-button-roles.md` |
| `pattern.ui.icon-control` | approved | `ui/pattern.ui.icon-control.md` |
```

Do not edit the Exemplars table.

5. In `canon/patterns/HARVEST.md`, under **Supporting harvest packages**, append:

```
| labeled button roles | `pattern.ui.shared-button-roles` |
| icon-only compact control | `pattern.ui.icon-control` |
```

6. In `canon/patterns/HARVEST.md` **Crosswalk** table, append (do **not** add rows to the define-parent **AC → pattern cite map**):

```
| create (AST-1300) | `pattern.ui.shared-button-roles` | ui | `ui/pattern.ui.shared-button-roles.md` | AST-1166 catalog | approved — labeled `btn` roles; CSS in `App.css` |
| create (AST-1300) | `pattern.ui.icon-control` | ui | `ui/pattern.ui.icon-control.md` | AST-1166 catalog | approved — icon-only compact actions; CSS in `App.css` |
```

⚠️ **Decision:** Land both files as `status: approved` (not `proposed`). Parent Architectural definition: “Archie approval of this Description (Todo) is approval to treat these as catalog law for the epic.” AUTHORING forbids implementers depending on `proposed` ids; AST-1301 / AST-1302 cite these ids. Skip the in-repo proposed intermediate. `proposed_in` stays `AST-1166`. `approved_at` is the catalog-land date `2026-08-11`.

⚠️ **Decision:** Do not add a `docs/ASTRAL_CODE_RULES.md` §2.x. Patterns are the canon home; CODE_RULES has no existing button section to amend (unlike `pattern.dispatch.score-floor`).

⚠️ **Decision:** Do not add HARVEST **AC cite map** rows. “New labeled button” is not a define-parent change-shape in that table; inventing one would force every future parent to cite these ids. Supporting-package + Crosswalk keep the register complete.

---

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree; publish each stage to `origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns`. Do not edit JSX call sites, `tests/`, or `docs/test-bible/**`. On ambiguity or codebase drift, stop and comment on the **parent** [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency) with the Stage blocked format from plan-child.

## Self-Assessment

**Scope:** `Single-Component` — `App.css` plus two `canon/patterns/ui/` files and their README/HARVEST index rows; no TSX, API, or config.

**Conf:** `high` — parent catalog tables lock class names and visual baselines; SCHEMA/AUTHORING lock file shape; CSS is a copy of existing `.modal-btn.*` / `.job-list-icon-btn` declarations.

**Risk:** `low` — new selectors are unused until siblings switch `className`; existing families stay; a docs typo would block citations, not runtime.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.1 / `astral.standards.in-scope-only` | No JSX remediations; no sibling inventory; no CODE_RULES rewrite |
| §1.3 DRY | One shared family; old families left in place (temporary duplicate until AST-1301/1302 delete them) — not aliased, so this ticket does not silently restyle live screens |
| §1.4 / §2.1 config | No `config.py`; colors reuse existing `:root` tokens; no new enum |
| §2.4 / §2.6 | N/A — no batch or state machine |
| §3.3 imports | No new imports |
| §3.5 placement / naming | Styles only in `App.css` with TOC 14–15; no new component file; class names are domain language (`btn`, `icon-control`) |
| `astral.standards.names-not-ticket-ids` | No `ast-1300` in selectors or pattern slugs |
| `astral.layers.ui-config-driven-business-logic` | Presentation only; enablement/API unchanged |
| `astral.ui.frontend-file-placement` | No second CSS file; no nested component dir |
| Pattern SCHEMA / AUTHORING | Required keys, body order, approved-set discovery via `status: approved` |
| Test-tree ban | No `tests/` or bible edits |

No unresolved rule conflicts. Temporary CSS duplication with `.modal-btn` / `.dep-btn` is intentional and owned by the siblings who will delete the old rules after they migrate call sites.
