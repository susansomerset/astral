# AST-1317 — Codify in-row labeled-button size (Add a button style for in-row buttons)

- **Linear:** [AST-1317](https://linear.app/astralcareermatch/issue/AST-1317/codify-in-row-labeled-button-size-add-a-button-style-for-in-row-buttons)
- **Parent:** [AST-1309](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons)
- **Publish ref:** `sub/AST-1309/AST-1317-codify-in-row-labeled-button-size`

Amend the approved `pattern.ui.shared-button-roles` catalog with the parent-locked optional `in-row` size modifier, and land the unused shared `.btn.in-row` style in `App.css`, so AST-1318 can add the class on table-row labeled buttons. Does not switch any JSX call site, does not restyle icon-controls, and does not reopen AST-1166 roles.

## Traceability

| Parent / child item | This plan |
|---------------------|-----------|
| Purpose — compact in-row size on the existing labeled family | Stages 1–2 |
| Functional scope 1 — in-row size on the labeled family | Stages 1–2 |
| Functional scope 2 — apply on table-row labeled buttons | N/A — AST-1318 |
| Functional scope 3 — leave full-size and icon-only alone | Stages 1–2 (no TSX; no `.icon-control` CSS edit) |
| Child AC1 / parent AC1 — catalog documents `in-row` (roles unchanged; always paired with a role) | Stage 2 (body) + Stage 1 (`canonical_refs`) |
| Parent AC2–6 — row apply, SA Run/Stop, full-size unchanged, icon-controls, enablement | N/A — AST-1318 / boundaries (this ticket does not switch call sites) |
| In-row size lock (token, height, not a fifth role, not icon-control) | Stage 1 CSS + Stage 2 catalog text |
| Architectural — amend `pattern.ui.shared-button-roles`; reuse `pattern.ui.icon-control` as boundary | Stage 2; icon-control file not rewritten |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/App.css` | Append `.btn.in-row` size rule at the end of section 14 (exact CSS below) | ui |
| `canon/patterns/ui/pattern.ui.shared-button-roles.md` | Amend in place — add `in-row` to Solution shape / When not to use / Notes; add `.btn.in-row` `canonical_refs` item; add `astral.standards.no-hardcoded-sets` to `related_statutes`; refresh `approved_at` | docs |
| `canon/patterns/HARVEST.md` | Update the existing `pattern.ui.shared-button-roles` Crosswalk notes cell only | docs |

**Do not touch:** any `src/ui/frontend/src/**/*.{tsx,ts}` (including `AdminScheduledActions.tsx` Run / Stop); `canon/patterns/ui/pattern.ui.icon-control.md`; `canon/patterns/README.md`; `canon/patterns/SCHEMA.md`; `canon/patterns/AUTHORING.md`; `src/ui/api/**`; `src/utils/config.py`; `docs/ASTRAL_CODE_RULES.md`; `tests/**`; `docs/test-bible/**`; existing `.btn` / `.btn.primary` / `.btn.secondary` / `.btn.danger` / `.btn.primary.in-flight` / `.icon-control` declarations (do not change their values).

**Do not add:** `Button.tsx`, a second stylesheet, a `:root` token for padding, a `config.py` size enum, a fifth role class, or a wrapper component.

---

## Stage 1: Unused `.btn.in-row` size in `App.css`

**Done when:** `App.css` section 14 defines `.btn.in-row` with the exact declarations below, after the existing `.btn.danger:disabled` rule and before `/* === 15. Icon control === */`. Existing screens look unchanged because no TSX `className` gains `in-row`. `rg -n 'in-row' src/ui/frontend/src --glob '*.tsx'` still finds no matches.

1. In `src/ui/frontend/src/App.css`, do **not** change the TOC. Section **14. Shared button roles** already exists.

2. Immediately after the existing `.btn.danger:disabled` block (currently `opacity: 0.4;`) and immediately before `/* === 15. Icon control === */`, insert exactly this rule — copy, do not restyle, do not add `min-height` / `font-size` / new hex / hover variants:

```css
.btn.in-row {
  padding: 3px 20px;
  line-height: 1.2;
}
```

3. Do **not** edit `.btn { padding: 8px 20px; … }` or any role / in-flight / disabled rule. Full-size labeled buttons stay `8px 20px` / inherited `line-height: 1.5`.

4. Do **not** change any TSX `className`. Do **not** alias `.icon-control` onto `.btn.in-row`.

⚠️ **Decision:** `in-row` is a size modifier on the existing `.btn` family, not a fifth role and not a parallel class system. One selector (`.btn.in-row`) overrides only padding and line-height; role colors and `in-flight` gold stay on `.btn.primary` / `.secondary` / `.danger` / `.primary.in-flight`. Markup AST-1318 will use is space-separated: `btn primary in-row`, `btn secondary in-row`, `btn danger in-row`, `btn primary in-flight in-row`.

⚠️ **Decision:** Height lock. Current `.btn` is `padding: 8px 20px` + inherited body `line-height: 1.5` + `font-size: 14px` → content ≈ 21px, box ≈ 37px. 60% of 37px ≈ 22px. `.btn.in-row` keeps `font-size: 14px` from `.btn` (do not drop to `.icon-control`’s 11px), sets `line-height: 1.2` (content ≈ 16.8px) and `padding: 3px 20px` → box ≈ 22.8px (~62%). Horizontal padding stays `20px` because the parent lock is height only. Do not invent `min-height`.

⚠️ **Decision:** CSS lives only in `App.css` (`astral.ui.frontend-file-placement`). No `styles/buttons.css`, no React wrapper, no `:root` padding token, no `config.py` size set. Size lives in this one shared rule (`astral.standards.no-hardcoded-sets`).

---

## Stage 2: Amend `pattern.ui.shared-button-roles` + HARVEST note

**Done when:** `canon/patterns/ui/pattern.ui.shared-button-roles.md` is the exact file below (`status: approved`, `proposed_in: AST-1166`, `approved_by: Archie`, `approved_at: "2026-08-11"`, `canonical_refs` includes `.btn.in-row` plus the four existing role selectors, SCHEMA-required keys only). `canon/patterns/HARVEST.md` Crosswalk notes for that id mention the in-row amendment. `canon/patterns/README.md` is unchanged (no new pattern id). Body section order remains `# Problem`, `# Solution shape`, `## When not to use`, `## Notes`.

1. Replace the entire contents of `canon/patterns/ui/pattern.ui.shared-button-roles.md` with **exactly** this file (do not leave the old Solution-shape bullets beside the new ones):

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
```

2. In `canon/patterns/HARVEST.md`, in the Crosswalk table, change **only** the notes cell on the existing `pattern.ui.shared-button-roles` row. Current cell:

```
approved — labeled `btn` roles; CSS in `App.css`
```

Replace that cell with:

```
approved — labeled `btn` roles + `in-row` size (AST-1317); CSS in `App.css`
```

Do not add a second Crosswalk row. Do not edit the Supporting-package table. Do not edit `README.md`.

3. Do **not** edit `canon/patterns/ui/pattern.ui.icon-control.md`. Its existing “separate family, not a size variant of labeled buttons” / “Labeled text actions — use `pattern.ui.shared-button-roles`” bullets already are the boundary. Restyling icon-control CSS is out of scope.

⚠️ **Decision:** AUTHORING **Amend** keeps the same `id` / path. Stay `status: approved` (do not bounce through `proposed`). Keep `proposed_in: AST-1166` (lineage). Refresh `approved_at` to `"2026-08-11"` (same calendar day as the original approve; Archie Todo on AST-1309 is the amendment approval). Do not invent undeclared frontmatter.

⚠️ **Decision:** Add `astral.standards.no-hardcoded-sets` to `related_statutes` because the parent Architectural definition cites it for this amendment (size lives in the shared style, not per call site). Do not add a new pattern id.

---

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree; publish each stage to `origin/sub/AST-1309/AST-1317-codify-in-row-labeled-button-size`. Do not edit JSX call sites, `tests/`, or `docs/test-bible/**`. On ambiguity or codebase drift, stop and comment on the **parent** [AST-1309](https://linear.app/astralcareermatch/issue/AST-1309/add-a-button-style-for-in-row-buttons) with the Stage blocked format from plan-child.

## Self-Assessment

**Scope:** `Single-Component` — one unused CSS modifier plus an in-place amend of one approved pattern file and its HARVEST notes cell; no TSX, API, or config.

**Conf:** `high` — parent In-row size lock names the token, pairings, ~60% height, and “not a fifth role / not icon-control”; AUTHORING Amend + SCHEMA lock file shape; Stage 1 CSS is a two-declaration override of existing `.btn` padding.

**Risk:** `low` — new selector is unused until AST-1318 adds `in-row` to `className`; existing `.btn` / `.icon-control` values stay; a docs typo would block citations, not runtime.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.1 / `astral.standards.in-scope-only` | Catalog + unused CSS only; no JSX apply (AST-1318); no icon-control restyle; no AST-1166 role reopen |
| §1.3 DRY | One `.btn.in-row` modifier; roles stay on existing selectors |
| §1.4 / `astral.standards.no-hardcoded-sets` | Size in shared `App.css` rule, not per call site; no `config.py` enum |
| §2.1 config | No `config.py`; no new `:root` token |
| §2.4 / §2.6 | N/A — no batch or state machine |
| §3.3 imports | No new imports |
| §3.5 / `astral.ui.frontend-file-placement` | Style only in `App.css` section 14; no second CSS file; no wrapper component |
| `astral.ui.naming-conventions` | Token is `in-row` (domain language, not a ticket id) |
| `astral.standards.names-not-ticket-ids` | No `ast-1317` in selectors or pattern slugs |
| `astral.layers.ui-config-driven-business-logic` | Presentation only; enablement/API unchanged |
| Pattern SCHEMA / AUTHORING | Amend same id; required keys; body order; `approved_at` refresh; no undeclared frontmatter |
| `orch.roles.archie-approves-statutes` | Archie Todo on AST-1309 Description is amendment approval |
| `pattern.ui.icon-control` (boundary) | File and CSS untouched; catalog When-not-to-use still points labeled actions at this family |
| Test-tree ban | No `tests/` or bible edits |

No unresolved rule conflicts.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1317
**Overall:** APPROVED
**Publish ref:** `sub/AST-1309/AST-1317-codify-in-row-labeled-button-size` @ `949171e0`

## Traceability
Child AC1 (catalog documents `in-row` size modifier; roles unchanged; always paired with a role) → Stage 1 (`.btn.in-row` in `App.css`) + Stage 2 (pattern `canonical_refs`, Solution shape, When not to use). Parent AC2–6 and functional scope 2 (table-row apply, SA Run/Stop, full-size unchanged, icon-controls, enablement) → N/A per child boundaries and explicit AST-1318 deferral; Stages 1–2 map to parent purpose / functional scope 1 / in-row size lock only.

**Considered:** Universal orch.* set + scoped `astral.ui.frontend-file-placement`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.ui.naming-conventions`, `astral.standards.names-not-ticket-ids`, `astral.layers.ui-config-driven-business-logic` — all `conforms` (in-session; no statute-table rows required).

context_tokens≈38000
```

**Gate summary:** AST-1317 is **Plan Ready**, assignee Joan, publish tip `949171e0`. Child scope matches parent child #1 only: unused `.btn.in-row` CSS + in-place `pattern.ui.shared-button-roles` amend + HARVEST notes cell — no JSX, no icon-control restyle, no call-site switch (AST-1318).

**R5 / R6:** Traceability is bidirectional and honest; parent AC2–6 are explicitly deferred, not orphaned. Insertion point in `App.css` (after `.btn.danger:disabled`, before section 15) matches the worktree. Height math (~62% of full labeled button) satisfies the parent “about 60%” lock without scaling type to icon-control size. AUTHORING **Amend** path (`approved_at` refresh, same `id`, `no-hardcoded-sets` in `related_statutes`) aligns with parent architectural definition and `pattern.ui.icon-control` boundary. Self-assessment (`Single-Component`, high conf, low risk) matches footprint. No `fix-now` or blocking `discuss` findings. Plan Discuss round count: 0 (first pass from Plan Ready).

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1309/AST-1317-codify-in-row-labeled-button-size`  
**Product commits:** `a0979ffc` (unused `.btn.in-row` CSS), `26eef718` (pattern amend + HARVEST notes)

## Radia review

# Radia review — AST-1317

**Status gate:** Tests Passed (spawn prompt; trusted)  
**Baseline:** `origin/dev`  
**Publish ref:** `origin/sub/AST-1309/AST-1317-codify-in-row-labeled-button-size` @ `ae69743e0063f33befca8b5e39c2367e13f395f1`  
**Diff change set:** layers `ui` + `docs`; paths `src/ui/frontend/src/App.css`, `canon/patterns/ui/pattern.ui.shared-button-roles.md`, `canon/patterns/HARVEST.md`, `docs/features/interface/ast-1317-codify-in-row-labeled-button-size.md`, `docs/test-bible/frontend/root.md`; change_types `modify` + issue-doc `add`.

Engineer product commits (`a0979ffc`, `26eef718`) touch only `App.css` and pattern canon. `docs/test-bible/frontend/root.md` arrives via Betty `merge-tests` (`3992b26a`) — expected pipeline, not engineer test-tree violation.

---

```
[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1317
**Publish ref:** origin/sub/AST-1309/AST-1317-codify-in-row-labeled-button-size @ ae69743e
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent-layer diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent-layer diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent-layer diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-layer diff |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-layer diff |
| astral.batch.claim-process-release | scoped | not-applicable | no batch-layer diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch-layer diff |
| astral.config.config-source-of-truth | scoped | not-applicable | no config-layer diff |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no config/secrets diff |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug-artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug/ spike paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch-layer diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatch-layer diff |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | predicate paths `docs/features/**` not in diff set |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Betty merge-tests commit, not engineer src/features edit |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits exclude `tests/` and `docs/test-bible/**`; bible via Betty merge |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no core/external diff |
| astral.layers.import-direction | scoped | not-applicable | CSS/docs only; no Python imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts-layer diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | presentation-only CSS + catalog; no enablement/state strings |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no data/coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render/consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth paths |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed/json diff |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed/catalog conflict |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed/boot paths |
| astral.seed.define-approved | scoped | not-applicable | no define/seed paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed/data diff |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer diff |
| astral.standards.database-header-inventory | scoped | not-applicable | no database/migration diff |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug logging diff |
| astral.standards.dry-and-focused-functions | scoped | conforms | single `.btn.in-row` modifier; roles unchanged on existing selectors |
| astral.standards.in-scope-only | scoped | conforms | unused CSS + catalog amend only; no TSX/icon-control/config creep |
| astral.standards.logging-via-utils | scoped | not-applicable | no logging diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | token `in-row`; no ticket id in selectors or slugs |
| astral.standards.no-cross-contamination | scoped | conforms | no unrelated module edits |
| astral.standards.no-hardcoded-sets | scoped | conforms | size in shared `App.css` rule per approved pattern amend (not per-call-site inline) |
| astral.standards.public-then-helpers | scoped | not-applicable | no Python module structure diff |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils/data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no state-machine diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job-state diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no run/dispatcher diff |
| astral.ui.frontend-file-placement | scoped | conforms | style only in `App.css` section 14; no second stylesheet or wrapper |
| astral.ui.naming-conventions | scoped | conforms | domain-language `in-row` modifier |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server/worker config diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1317)` present on publish tip |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`merge-tests` commits follow vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | sub-branch publish; no dev/main direct product push |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/AST-1309/AST-1317-…` |
| orch.git.merge-on-checkout | universal | conforms | no merge/checkout violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear stage commits |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches in diff |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1309` worktree |
| orch.git.three-permanent-branches | universal | conforms | no fourth permanent branch introduced |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 executed per binding plan |
| orch.pipeline.project-scoped-queues | universal | conforms | child scope matches AST-1309 child #1 |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed gate |
| orch.roles.archie-approves-statutes | universal | conforms | in-place pattern amend; `approved_at` refresh; AST-1309 approval chain documented |
| orch.roles.betty-owns-test-tree | universal | conforms | test-bible edit via Betty merge, not engineer |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a to diff content |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee; product commits engineer-scoped |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer commits avoid banned test-tree paths |

**Straggler (C4):** Joan APPROVED attachment lists no Excluded statutes — no straggler rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.ui.shared-button-roles | conforms | `in-row` documented as optional size modifier (never fifth role); pairings, ~60% height, `canonical_refs` + `.btn.in-row` CSS match Solution shape |
| pattern.ui.icon-control | conforms (boundary) | file and CSS untouched; When-not-to-use boundary preserved |

## Plan adherence

- **Stage 1:** `.btn.in-row { padding: 3px 20px; line-height: 1.2; }` inserted after `.btn.danger:disabled`, before section 15 — exact match to plan.
- **Stage 2:** `pattern.ui.shared-button-roles.md` matches plan template (frontmatter, body order, `approved_at: "2026-08-11"`, `no-hardcoded-sets` in `related_statutes`); HARVEST Crosswalk notes cell updated only.
- **Boundaries:** `rg 'in-row' …/*.tsx` empty; no `Button.tsx`; no `.icon-control` / role selector value changes; parent AC2–6 correctly deferred to AST-1318.
- **Estimate (2):** footprint matches — two-declaration CSS + in-place catalog amend + HARVEST cell (+ Betty bible row via merge).
- **C6 aids (§5a–§5g):** N/A — CSS/docs-only diff; no imports, logging, debug contract, external layer, batch, or API surfaces touched.

## Findings

**fix-now:** none  

**discuss:** none  

**advisory:** CSS does not structurally enforce “always pair `in-row` with a role” — pairing is catalog law for AST-1318 markup apply. Acceptable for this codify ticket.

## What’s solid

- Tight, plan-faithful diff: unused modifier + catalog amendment only; zero runtime surface change until AST-1318.
- Height lock math (~62% of full labeled button) implemented without shrinking label to icon-control size.
- Clear sibling boundaries (AST-1318 apply, icon-control untouched, AST-1166 roles not reopened).

## Frame diff

(none) — no JSX/page frame or routing changes; only unused shared CSS and canon docs.

## Notes

Joan plan-rubric verdict attached (APPROVED @ `949171e0`). Betty test-bible manifest aligns with docs-acceptance grep/read gates on publish tip.

context_tokens≈52000

