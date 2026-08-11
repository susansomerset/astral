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

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1300
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns` @ `03ad36c5e4cc51de40ea0068072c487460785b6a`

## Traceability
Child AC1→S1–2; parent AC1→S1–2; parent AC2–7→N/A (AST-1301/AST-1302 boundaries)

## Findings

### discuss — Direct `approved` landing (skip `proposed` intermediate)
**Location:** Stage 2 decisions; `canon/patterns/AUTHORING.md` lifecycle
**Finding:** AUTHORING default is propose → Archie approve. Plan lands both patterns as `status: approved` in one pass, citing parent Architectural definition (“Archie approval of this Description (Todo) is approval to treat these as catalog law”).
**Recommendation:** Acceptable for this epic — parent Todo lock is the approval signal. Builder should keep `proposed_in: AST-1166` and `approved_by: Archie` / `approved_at: "2026-08-11"` exactly as staged. Non-blocking.

### R5 — Traceability (full)

| Parent / child AC | Plan stage(s) | Notes |
|---|---|---|
| Child AC1 — canon contains both pattern ids matching Discussion catalog | S1–2 | Pattern bodies mirror parent Button class catalog tables |
| Parent AC1 (same) | S1–2 | `canonical_refs` → `App.css` selectors |
| Parent AC2 — full labeled-button inventory | N/A | AST-1301 |
| Parent AC3 — toolbar/modal/detail/export on shared classes | N/A | AST-1301 |
| Parent AC4 — retire duplicate families | N/A | AST-1301/1302 delete old rules after migration |
| Parent AC5 — list row icon-controls only | N/A | AST-1302 |
| Parent AC6 — unified in-flight gold | S1 | `.btn.primary.in-flight` copies `.modal-btn.save.in-flight` |
| Parent AC7 — no enablement regression | N/A | No JSX touched this ticket |
| Parent Purpose — codify before call-site rewrites | S1–2 | CSS + approved patterns land first |
| Parent Functional scope 1 (catalog locked) | — | Plan does not reopen |
| Parent Functional scope 2 (codify as patterns) | S1–2 | |
| Parent Functional scope 3–6 | N/A | Siblings |

| Plan stage | Parent mapping |
|---|---|
| S1 — `App.css` `.btn` / `.icon-control` | AC1 canonical implementation; parent catalog visual baselines |
| S2 — pattern files + README/HARVEST index rows | AC1; parent Architectural “new patterns proposed” |
| Execution contract / self-review | Orchestration discipline only |

No orphan stages. No unmapped child AC.

### R6 — Adversarial checklist (summary)

| Check | Result |
|---|---|
| Definition fidelity — codify only, no sweep | Pass |
| Boundaries — no JSX, no React wrapper, no CODE_RULES amend, no test tree | Pass |
| Layer / import — `App.css` + `canon/patterns/**` only | Pass |
| Config — no `config.py`; `:root` tokens reused | Pass |
| File placement — styles in `App.css` TOC 14–15; patterns in `canon/patterns/ui/` | Pass |
| Pattern SCHEMA / AUTHORING — required keys, body order, ≥1 `canonical_refs` each | Pass |
| CSS baseline fidelity — compared tip `.modal-btn.*` / `.job-list-icon-btn` | Pass (literal copy + `font-family: inherit` on icon-control) |
| DRY — temporary duplicate families left in place, not aliased | Pass (intentional; siblings own deletion) |
| Self-assessment — Single-Component / high / low | Honest |

### R1–R3 — Statute matching (plan Files Changed)

**Plan layers:** `ui`, `docs`
**Plan paths:** `src/ui/frontend/src/App.css`, `canon/patterns/ui/*.md`, `canon/patterns/README.md`, `canon/patterns/HARVEST.md`
**Change types:** `add`, `modify`

**Considered (39):** all universal orchestration statutes (17) + scoped matches including `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.names-not-ticket-ids`, `astral.standards.no-cross-contamination`, `astral.standards.no-hardcoded-sets`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.ui.single-gunicorn-worker`, `astral.docs.features-single-file-per-ticket`, `astral.layers.ui-config-driven-business-logic`, `astral.layers.import-direction`, `astral.git.betty-no-src-or-features`, `orch.pipeline.plan-is-bible`, `orch.roles.archie-approves-statutes`, and other `src/**` / `docs/**` scoped standards whose predicates match.

**Excluded (29) sample reasons:** `astral.git.engineer-test-tree-ban` (no test paths); `astral.agent.*` / `astral.batch.*` (no core/data); `astral.config.*` (no config.py); `astral.seed.*` (no seed tables); `astral.idioms.require-auth-on-protected-endpoints` (no API).

**Per-statute verdicts (key cited on child):**

| Statute | Verdict | One-line |
|---|---|---|
| `astral.standards.in-scope-only` | conforms | CSS + pattern corpus only; no JSX sweep |
| `astral.standards.dry-and-focused-functions` | conforms | One labeled + one icon family; old families left for siblings |
| `astral.ui.frontend-file-placement` | conforms | `App.css` only; flat `canon/patterns/ui/` |
| `astral.ui.naming-conventions` | conforms | Domain class names, not ticket ids |
| `astral.standards.names-not-ticket-ids` | conforms | `btn`, `icon-control`, pattern slugs |
| `astral.standards.no-cross-contamination` | conforms | Stays in UI CSS + pattern tree |
| `astral.standards.no-hardcoded-sets` | conforms | Reuses `:root` tokens; `#fff` on danger copied from existing `.modal-btn.danger` |
| `astral.layers.ui-config-driven-business-logic` | conforms | Presentation classes only |
| `astral.docs.features-single-file-per-ticket` | conforms | Single plan under `docs/features/interface/` |
| `orch.pipeline.plan-is-bible` | conforms | Stages are binding; README/HARVEST index steps explicit |
| All other considered universals / scoped | conforms | No pipeline/git/test-tree violations in plan shape |

No `violates` / `needs-discussion` statute scores.

### Pattern compliance (R6)

| Pattern | Status | Match to `# Solution shape` |
|---|---|---|
| `pattern.ui.shared-button-roles` (new, to land `approved`) | Pass | Four roles + `in-flight` on primary only; `App.css` canonical_refs; no fifth family |
| `pattern.ui.icon-control` (new, to land `approved`) | Pass | Glyph-only; separate from `btn`; `title`/`aria-label` guidance |
| Parent “reuse themed confirm / modal shell” | Pass | No second confirm system introduced |

The plan is a tight vertical slice for child #1: land unused `.btn` / `.icon-control` CSS (verified against existing `.modal-btn` / `.job-list-icon-btn` on tip) and two approved pattern files with README/HARVEST index updates, without touching JSX or sibling remediation scope. Child AC1 and parent AC1 trace cleanly to Stages 1–2; parent AC2–7 are correctly deferred to AST-1301/AST-1302.

context_tokens≈78000
— Joan

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns`  
**Product commits:** `8135c228` (shared `.btn` / `.icon-control` CSS), `d8221e08` (approved pattern files + README/HARVEST index)

## Radia review

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1300
**Publish ref:** `origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns` @ `51d38a4c8450a4b02dc06b378d38ba130bd76357`
**Overall:** DISCUSS

## Statutes checked

Diff change set: paths `canon/patterns/**`, `docs/features/interface/ast-1300-codify-button-icon-control-patterns.md`, `docs/test-bible/frontend/root.md`, `src/ui/frontend/src/App.css`; layers `docs`, `ui`; change_types `add`, `modify`. **64** active statutes scored in-session (registry cites 65; `SCHEMA.md` harness excluded).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | `merge-tests(AST-1300)` merges Betty bible SHA onto sub tip — expected Tests Passed shape |
| `orch.git.commit-vocabulary` | universal | conforms | `code()` / `docs()` commits use standard vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work lands on `sub/AST-1166/AST-1300-*`, not direct-to-dev |
| `orch.git.ftr-sub-topology` | universal | conforms | Child publish ref under `sub/<parent>/…` |
| `orch.git.merge-on-checkout` | universal | conforms | No rebase-of-dev signal in diff |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No forbidden git ops in artifact |
| `orch.git.no-dev-agent-branches` | universal | conforms | Branch name is ticket-scoped sub ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | AST-1166 epic worktree pattern |
| `orch.git.three-permanent-branches` | universal | conforms | Sub branch off ftr/dev topology |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Catalog locked on parent; no product reopen |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 executed per binding plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Interface child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Review at Tests Passed gate |
| `orch.roles.archie-approves-statutes` | universal | conforms | Patterns cite `approved_by: Archie` per parent lock |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Bible edit is Betty-owned path via qa-child |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | N/A to diff content |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada remains implementer through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path commit signal |
| `astral.agent.confidence-bounds` | scoped | not-applicable | no `src/core/**` diff |
| `astral.agent.do-task-delegation` | scoped | not-applicable | no agent/dispatcher diff |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | no agent grading diff |
| `astral.batch.batch-id-first` | scoped | not-applicable | no batch paths |
| `astral.batch.batch-id-format` | scoped | not-applicable | no batch paths |
| `astral.batch.claim-process-release` | scoped | not-applicable | no batch paths |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | no batch paths |
| `astral.config.config-source-of-truth` | scoped | not-applicable | no `config.py` diff |
| `astral.config.pass-threshold-vs-score-floor` | scoped | not-applicable | no config/dispatch diff |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | not-applicable | no secrets/env diff |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | no debug artifact paths |
| `astral.debug.spikes-under-debug-dir` | scoped | not-applicable | no spike paths |
| `astral.dispatch.seed-auto-false` | scoped | not-applicable | no dispatch diff |
| `astral.dispatch.run-next-is-chain-authority` | scoped | not-applicable | no dispatch diff |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single `docs/features/interface/ast-1300-*.md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty bible commit touches only `docs/test-bible/**` |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Engineer commits (`8135c228`, `d8221e08`) did not touch test-tree; bible is Betty merge |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | no core/external diff |
| `astral.layers.import-direction` | scoped | conforms | CSS-only ui change; no new imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | no scripts diff |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Presentation classes only; no state strings |
| `astral.idioms.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.idioms.render-verdict-orchestrates-consult` | scoped | not-applicable | no render-verdict paths |
| `astral.idioms.require-auth-on-protected-endpoints` | scoped | not-applicable | no API diff |
| `astral.patterns.coat-check-never-store-empty` | scoped | not-applicable | no coat-check paths |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | not-applicable | no render-verdict paths |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | no API diff |
| `astral.seed.agent-tables-in-repo-json` | scoped | not-applicable | no seed JSON diff |
| `astral.seed.archie-catalog-wins` | scoped | not-applicable | no seed catalog diff |
| `astral.seed.boot-only-not-hot-path` | scoped | not-applicable | no seed boot diff |
| `astral.seed.define-approved` | scoped | not-applicable | no seed define diff |
| `astral.seed.operator-rows-stay-deleted` | scoped | not-applicable | no seed operator diff |
| `astral.seed.other-via-coverage-join` | scoped | not-applicable | no seed coverage diff |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | no data layer diff |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no database/migration diff |
| `astral.standards.debug-contract-gated` | scoped | not-applicable | no debug logging diff |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | One shared `.btn` + `.icon-control` family; intentional parallel leftovers |
| `astral.standards.in-scope-only` | scoped | conforms | Codify only; no JSX sweep or sibling inventory |
| `astral.standards.logging-via-utils` | scoped | not-applicable | no runtime logging diff |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `btn`, `icon-control`, pattern slugs — no ticket ids in code |
| `astral.standards.no-cross-contamination` | scoped | conforms | UI CSS + pattern corpus only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Reuses `:root` tokens; `#fff` on danger copies existing `.modal-btn.danger` |
| `astral.standards.public-then-helpers` | scoped | not-applicable | no Python module diff |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | no utils diff |
| `astral.state.core-decides-transitions` | scoped | not-applicable | no state machine diff |
| `astral.state.job-prior-states-enforced` | scoped | not-applicable | no job state diff |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | no run-chain diff |
| `astral.ui.frontend-file-placement` | scoped | conforms | Styles appended to `App.css`; patterns in `canon/patterns/ui/` |
| `astral.ui.naming-conventions` | scoped | conforms | Domain class names; flat pattern domain folder |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | no server/worker diff |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.ui.shared-button-roles` | conforms | Approved entry + `canonical_refs` match landed `.btn.*` selectors; four roles + `in-flight` on primary only |
| `pattern.ui.icon-control` | conforms | Approved entry + `.icon-control` CSS; glyph-only guidance; separate from `btn` family |

No pre-existing catalog patterns cited for reuse (`none cited` beyond the two new entries this ticket lands).

## Plan adherence

Stages 1–2 match the binding plan: TOC **14–15** in `App.css`; unused `.btn` / `.icon-control` rules are a literal copy of `.modal-btn.*` / `.job-list-icon-btn` baselines (including `font-family: inherit` on icon-control); two `status: approved` pattern files with SCHEMA body order and ≥1 `canonical_refs` each; `README.md` count **Nine** approved + HARVEST supporting-package and Crosswalk rows after `pattern.ui.admin-endpoint`. Engineer commits did not touch TSX, `tests/**`, `Button.tsx`, or retire legacy families. Self-Assessment **Single-Component** / **high** / **low** still matches the footprint. Betty `docs/test-bible/frontend/root.md` manifest + `merge-tests` are expected qa-child artifacts, not engineer scope creep.

## Findings

### discuss — Straggler: plan excluded test-tree, diff includes Betty bible
**Location:** Joan R1–R3 Excluded `astral.git.engineer-test-tree-ban`; diff adds `docs/test-bible/frontend/root.md`
**Finding:** Joan excluded the statute because the plan listed no test-tree paths. The publish tip three-dot diff now includes Betty’s bible manifest (`d84a27f9`) merged via `merge-tests`. Statute sweep scores the bible path in-scope; engineer product commits did not touch it.
**Recommendation:** No engineer action. Expected Betty/qa-child + merge-tests shape at Tests Passed. Note for traceability only.

### advisory — `#fff` on `.btn.danger`
**Location:** `src/ui/frontend/src/App.css` (`.btn.danger { color: #fff; }`)
**Finding:** Literal copy from `.modal-btn.danger` per plan Decision; not a new design choice.
**Recommendation:** Optional future token (`--text-on-danger`) when siblings retire legacy families — not blocking AST-1300.

## What's solid

- CSS fidelity: new `.btn` base matches `.modal-btn` base; role colors and in-flight gold align with existing modal/dep rules; `.icon-control` matches `.job-list-icon-btn` + `font-family: inherit`.
- Scope gate verified: no TSX `className` uses catalog `btn primary|secondary|danger` or `icon-control`; legacy families remain untouched.
- Pattern SCHEMA/AUTHORING: required frontmatter keys, body order, approved-set discovery via README/HARVEST, direct `approved` landing per parent Architectural lock (Joan discuss item accepted).
- Cross-ticket boundaries: no AST-1301 labeled sweep or AST-1302 icon remediation in this diff.

## Frame diff

| Planned (Stages 1–2 product) | Actual on tip |
|------------------------------|---------------|
| `App.css` TOC 14–15 + selectors | Present (`8135c228`) |
| Two `canon/patterns/ui/*.md` + README/HARVEST | Present (`d8221e08`) |
| No TSX / tests / bible (engineer) | Engineer commits: CSS + canon only |
| — | `+docs/test-bible/frontend/root.md` via Betty qa-child (`d84a27f9` + merge-tests) — expected, not plan drift |
| — | `docs/features/interface/ast-1300-*.md` on branch (issue doc) — normal |

`(none)` product footprint drift.

## Notes

Joan plan-rubric verdict attached (`revision=1`, APPROVED). No statute `violates` rows. C7 artifact complete for Chuckles doc append + Linear upshot.

context_tokens≈52000
— Radia

## Resolution

**Date:** 2026-08-11  
**Publish ref:** `origin/sub/AST-1166/AST-1300-codify-button-icon-control-patterns`

| Finding | Action |
|---------|--------|
| **discuss** — plan excluded test-tree; tip includes Betty `docs/test-bible/frontend/root.md` via `merge-tests` | Closed — no product change. Engineer commits stay CSS + canon; bible is Betty’s expected Tests Passed shape (`d84a27f9` + `51d38a4c`). |
| **advisory** — `#fff` on `.btn.danger` | Deferred — literal copy of `.modal-btn.danger` per plan Decision. Optional `--text-on-danger` belongs with AST-1301/AST-1302 when leftover families retire, not this ticket. |

No fix-now items. No TSX / API / config change on resolve.
