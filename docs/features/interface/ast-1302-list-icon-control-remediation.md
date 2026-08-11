# AST-1302 — List icon-control remediation (Button consistency)

- **Linear:** [AST-1302](https://linear.app/astralcareermatch/issue/AST-1302/list-icon-control-remediation-button-consistency)
- **Parent:** [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency)
- **Publish ref:** `sub/AST-1166/AST-1302-list-icon-control-remediation`

Bring list row actions and the parent-catalog peer icon-only controls (modal × dismiss, CollapsiblePanel chevron) onto the already-landed `pattern.ui.icon-control` class. Replace cramped two-letter row labels (Skip as `Sk`, and the same family) with a single initial or an existing SVG glyph. Do not land pattern docs (AST-1300). Do not remediate labeled buttons (AST-1301).

## Traceability

| Parent / child item | This plan |
|---------------------|-----------|
| Functional scope 5 — list row actions → icon-control; fix tiny text (Skip as "Sk") | Stages 1–2 |
| Parent catalog — icon-control also for modal × dismiss and chevron expand/collapse | Stage 3 |
| Child AC5 — list row action columns use icon-controls only; Skip/Edit/View-style are not cramped labeled text | Stages 1–2 |
| Child AC6 — no regression in enablement/actions on touched flows | Stages 1–3 keep onClick / disabled / handlers; Land Meteorite is not in Files Changed |
| Child boundary — does not land pattern docs | No `canon/patterns/**` edits |
| Child boundary — does not own the labeled-button sweep | No `btn primary` / `secondary` / `danger` / `in-flight`; no `dep-btn` / `modal-btn` / `list-page-bulk-btn` / `entity-skip-btn` remediations except the one labeled control that sits inside a row-action column (Stage 2, Set dispatch tasks) |

## Inventory (closed — do not expand)

Tip surveyed: `origin/ftr/AST-1166-button-consistency` @ `9a23b68d` (AST-1300 User Testing; `.icon-control` unused by TSX).

| Surface | File | Today | This ticket |
|---------|------|-------|-------------|
| Job list Skip / Jr / Re / In / X / Gh | `components/CandidateJobRowActions.tsx` | `job-list-icon-btn` + two-letter text | Stage 1 — `icon-control` + single initial |
| Manage Candidates View / Edit / Delete | `pages/AdminManageCandidates.tsx` `_actions` | `list-page-edit-btn` + existing SVG | Stage 2 — `icon-control`, keep SVG |
| Manage Candidates Set dispatch tasks | same `_actions` column | labeled `dep-btn` | Stage 2 — `icon-control` + `T` (column must be icon-only) |
| Manage Agents row Delete | `pages/AdminAgentPrompts.tsx` `rowActions` | labeled `dep-btn danger` "Delete" | Stage 2 — `icon-control` + `D` |
| Modal header × | `components/Modal.tsx` | `modal-close` | Stage 3 — `icon-control` |
| Scheduled Actions custom modal × (×2) | `pages/AdminScheduledActions.tsx` | `modal-close` | Stage 3 — `icon-control` only on those two × buttons |
| CollapsiblePanel chevron | `components/CollapsiblePanel.tsx` | `collapsible-panel-chevron-btn` | Stage 3 — `icon-control` |
| Modal labeled Skip This Job | `components/JobDetailModal.tsx` | `entity-skip-btn` | **Exclude** — sibling AST-1301 |
| List bulk / toolbar (Retry, Add Task, Stop All, …) | `ListPage.tsx`, `JobsSkipped.tsx`, `AdminScheduledActions.tsx` header | `list-page-bulk-btn` | **Exclude** — AST-1301 |
| Scheduled Actions row Run / Stop / Draining | `AdminScheduledActions.tsx` | labeled `list-page-bulk-btn` + in-flight overlay | **Exclude** — labeled dispatch controls; AST-1301 (`pattern.ui.shared-button-roles` + `in-flight`) |
| AUTO / Debug ON·OFF | `AdminScheduledActions.tsx` | `dispatch-status-badge` | **Exclude** — toggle badge, not catalog |
| Land Meteorite | `pages/AdminManageEmail.tsx` | labeled toolbar | **Exclude** — AST-1301; do not open this file |
| SQL history ▲▼ | `pages/AdminDataManagement.tsx` | `sql-hist-btn` | **Exclude** — not a list row / modal × / collapsible chevron |
| Side-tab ▲▼× / ArtifactEditor tab chrome | `SideTabPanel.tsx`, `ArtifactEditor.tsx` | bare buttons | **Exclude** — parent: side-tab chrome not in catalog |
| Nav group chevron | `NavigationShell.tsx` | `nav-group-chevron` span | **Exclude** — nav chrome |
| JobsInReview section header | `pages/JobsInReview.tsx` | full-width labeled header + chevron span | **Exclude** — section chrome; extracting a separate icon button would redesign the header |
| Card Edit / Activate / Delete | `pages/AdminScheduledQueries.tsx` | labeled `dep-btn` | **Exclude** — AST-1301 |
| `ListPage` more/less | `components/ListPage.tsx` | `expand-toggle` labeled | **Exclude** — cell chrome, not a row-action column |

`JobsRecommended.tsx` and `JobsSkipped.tsx` consume `CandidateJobRowActions` and are **not** edited.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/CandidateJobRowActions.tsx` | `job-list-icon-btn` → `icon-control`; two-letter children → single initials (table in Stage 1) | ui |
| `src/ui/frontend/src/pages/AdminManageCandidates.tsx` | View/Edit/Delete `list-page-edit-btn` → `icon-control`; drop Delete inline danger color; Set dispatch tasks → `icon-control` + `T` | ui |
| `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | `rowActions` Delete → `icon-control` + `D` | ui |
| `src/ui/frontend/src/components/Modal.tsx` | header × `modal-close` → `icon-control` | ui |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | two header × `modal-close` → `icon-control`; do not touch Run/Stop/`list-page-bulk-btn`/`modal-btn` | ui |
| `src/ui/frontend/src/components/CollapsiblePanel.tsx` | chevron `collapsible-panel-chevron-btn` → `icon-control` | ui |
| `src/ui/frontend/src/App.css` | delete leftover `.job-list-icon-btn` / `.list-page-edit-btn` / `.modal-close` / `.collapsible-panel-chevron-btn` rules; add layout-only `.collapsible-panel-header .icon-control { flex: 0 0 auto; }` | ui |

**Do not touch:** `canon/patterns/**`; `docs/ASTRAL_CODE_RULES.md`; `tests/**`; `docs/test-bible/**`; `src/ui/api/**`; `src/utils/config.py`; `JobDetailModal.tsx`; `AdminManageEmail.tsx`; `ListPage.tsx`; `JobsRecommended.tsx`; `JobsSkipped.tsx`; `SideTabPanel.tsx`; `ArtifactEditor.tsx`; `NavigationShell.tsx`; `AdminDataManagement.tsx`; `AdminScheduledQueries.tsx`; `JobsInReview.tsx`.

**Do not add:** `IconControl.tsx`, a second stylesheet, new SVG modules, `config.py` keys, or a `.icon-control.danger` modifier.

**Do not change:** any `onClick` / `disabled` / `onSkip` / `onResurrect` / `onAction` / `handleSetDispatchTasks` / `setDeleteTarget` / `guardedClose` behavior. Presentation and visible glyph only.

---

## Stage 1: Job-list row actions (`CandidateJobRowActions`)

**Done when:** Every `<button>` in `CandidateJobRowActions.tsx` has `className="icon-control"` and a single-character child. `rg -n 'job-list-icon-btn' src/ui/frontend/src` returns no TSX hits. Skip no longer renders `Sk`. Handlers, `title`, and `aria-label` strings are unchanged. `JobsRecommended` / `JobsSkipped` are unmodified.

1. In `src/ui/frontend/src/components/CandidateJobRowActions.tsx`, on every `<button type="button" className="job-list-icon-btn" …>`, replace `className="job-list-icon-btn"` with `className="icon-control"`. Do not remove `type="button"`, `title`, `aria-label`, or `onClick`. Do not edit the wrapping `<div className="job-list-actions">`.

2. Replace **only** the button children per this table (whitespace/newlines around the child may stay as they are today):

| `title` / `aria-label` (unchanged) | Current child | New child |
|------------------------------------|---------------|-----------|
| Resurrect | `Re` | `R` |
| Skip | `Sk` | `S` |
| View Job Analysis | `Jr` | `J` |
| Reapply | `Re` | `R` |
| Interview | `In` | `I` |
| Rejected | `X` | `X` |
| Ghosted | `Gh` | `G` |

⚠️ **Decision:** Single initials, not new SVGs and not Unicode pictographs. `pattern.ui.icon-control` allows “glyph or a single initial only”; the parent named cramped mini-text (`Sk`) as the defect. Resurrect and Reapply both become `R` because they never render on the same row (`CANDIDATE_SKIPPED` vs `POST_APPLIED`). Accessible names stay on `title` + `aria-label`.

3. Do not edit `JobsRecommended.tsx` or `JobsSkipped.tsx`. They already pass `onSkip` / `onResurrect` / `onAction` / `showViewAnalysis` into this component.

---

## Stage 2: Other list row-action columns

**Done when:** Manage Candidates `_actions` buttons are all `icon-control` (three SVGs + `T`). Manage Agents `rowActions` Delete is `icon-control` with child `D` and the same `disabled` / `title` logic. No `list-page-edit-btn` remains in TSX. `handleSetDispatchTasks` and `setDeleteTarget` are not rewritten. `AdminManageEmail.tsx` is untouched.

1. In `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, in the `_actions` column `render` (the `<span style={{ display: "flex", gap: 6, alignItems: "center" }}>` block):

   a. View button — replace with exactly this shape (keep `<ViewIcon />`):

   ```tsx
   <button type="button" className="icon-control" onClick={e => { e.stopPropagation(); setViewing(row) }} title="View" aria-label="View">
     <ViewIcon />
   </button>
   ```

   b. Edit button — same, `openEdit(row)`, `title="Edit"` `aria-label="Edit"`, `<EditIcon />`.

   c. Delete button — same, `void handleDelete(row)`, `title="Delete"` `aria-label="Delete"`, `<DeleteIcon />`. **Delete the** `style={{ color: "var(--danger)" }}` **prop.** Do not add `.icon-control.danger` or any inline color.

   d. Set dispatch tasks — replace the labeled `dep-btn` with:

   ```tsx
   <button
     type="button"
     className="icon-control"
     title="Set dispatch tasks"
     aria-label={`Set dispatch tasks for ${row.astral_candidate_id}`}
     disabled={settingCandidateId === row.astral_candidate_id}
     onClick={e => { e.stopPropagation(); void handleSetDispatchTasks(row) }}
   >
     T
   </button>
   ```

   Remove `className="dep-btn"` and `style={{ padding: "6px 10px", fontSize: 12 }}` from this control. Do not change `handleSetDispatchTasks`.

2. In `src/ui/frontend/src/pages/AdminAgentPrompts.tsx`, replace the `rowActions` Delete `<button className="dep-btn danger" …>Delete</button>` with:

   ```tsx
   <button
     type="button"
     className="icon-control"
     disabled={disabled}
     title={disabled ? `Agent is assigned to ${count} task(s) — unassign first` : "Delete agent"}
     aria-label="Delete"
     onClick={e => { e.stopPropagation(); if (agent) setDeleteTarget(agent) }}
   >
     D
   </button>
   ```

   Keep the `disabled = count > 0` computation above the return. Remove `style={{ padding: "3px 10px", fontSize: 12 }}`. Do not change the delete confirmation modal or its `modal-btn` / `dep-btn` footer (AST-1301).

⚠️ **Decision:** Set dispatch tasks is a word label inside the same `_actions` column as View/Edit/Delete. Parent AC5 / catalog: row-action columns are icon-controls only. Visible `T` (Tasks) plus existing `aria-label`. Not left for AST-1301 as `btn primary` — that would leave a labeled button in the column.

⚠️ **Decision:** Delete on Manage Candidates drops the inline `--danger` color. `pattern.ui.icon-control` forbids combining with `btn danger` and forbids per-call-site color that recreates a third family. `aria-label="Delete"` stays.

⚠️ **Decision:** Scheduled Actions row Run / Stop / Draining stay on `list-page-bulk-btn` for AST-1301. They are labeled dispatch controls with an in-flight overlay, not Skip/Edit/View-style compact actions. Converting them here would invent icon meaning for Draining and steal `in-flight` from `pattern.ui.shared-button-roles`.

---

## Stage 3: Peer icon-only controls + retire leftover CSS

**Done when:** Modal × (shared `Modal` + both Scheduled Actions custom shells) and the CollapsiblePanel chevron use `className="icon-control"` with `type="button"`. `rg -n 'job-list-icon-btn|list-page-edit-btn|modal-close|collapsible-panel-chevron-btn' src/ui/frontend/src` is empty. `.icon-control` rules in `App.css` section 15 are unchanged. `JobDetailModal` still uses `entity-skip-btn` and the label `Skip This Job`. Footer `modal-btn` / `dep-btn` on every modal is unchanged.

1. In `src/ui/frontend/src/components/Modal.tsx`, replace the header close button with:

   ```tsx
   <button type="button" className="icon-control" onClick={guardedClose} title="Close" aria-label="Close">×</button>
   ```

   Do not edit `modal-btn cancel` / `modal-btn save` in the footer.

2. In `src/ui/frontend/src/pages/AdminScheduledActions.tsx`:

   - Stop-all shell: replace `<button className="modal-close" onClick={() => setShowStopAll(false)}>&times;</button>` with `<button type="button" className="icon-control" onClick={() => setShowStopAll(false)} title="Close" aria-label="Close">×</button>`.
   - Add/Edit shell: replace `<button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>` with `<button type="button" className="icon-control" onClick={() => setShowModal(false)} title="Close" aria-label="Close">×</button>`.

   Do not edit any `list-page-bulk-btn`, `modal-btn`, Run/Stop overlay, or `dispatch-status-badge`.

3. In `src/ui/frontend/src/components/CollapsiblePanel.tsx`, on the chevron `<button>`, replace `className="collapsible-panel-chevron-btn"` with `className="icon-control"`. Keep `type="button"`, `aria-expanded`, `aria-label={expanded ? "Collapse section" : "Expand section"}`, `onClick`, and children `{expanded ? "▼" : "▶"}`. Do not change the label-wrap expand behavior.

4. In `src/ui/frontend/src/App.css`:

   a. Delete the entire `.list-page-edit-btn` rule and the `.list-page-edit-btn:hover` rule (currently immediately above `/* === 8b. Job list candidate actions (AST-312) === */`).

   b. Delete the entire `.job-list-icon-btn` rule and the `.job-list-icon-btn:hover` rule. **Keep** `.job-list-actions` (flex/gap/align).

   c. Delete the entire `.modal-close` rule and the `.modal-close:hover` rule (currently between `.modal-title` and `.modal-body`).

   d. Delete the entire `.collapsible-panel-chevron-btn` rule and the `.collapsible-panel-chevron-btn:hover` rule. Immediately after `.collapsible-panel-header` / `.collapsible-panel.is-expanded .collapsible-panel-header` (where the chevron rules were), insert **only**:

   ```css
   .collapsible-panel-header .icon-control {
     flex: 0 0 auto;
   }
   ```

   Do not add `width` / `height` / `font-size` / `padding` / `border` / `color` on that selector.

   e. Do not edit section 15 `.icon-control` / `:hover` / `:disabled`. Do not delete `.entity-skip-btn`, `.list-page-bulk-btn`, `.sql-hist-btn`, `.dispatch-log-copy-btn`, `.nav-group-chevron`, or `.expand-toggle`.

⚠️ **Decision:** Layout-only `flex: 0 0 auto` on `.collapsible-panel-header .icon-control` is not a third visual family. Do not restore the old 32×32 borderless chevron look — AST-1300 locked `.icon-control` as-is (no extra hit-target).

---

## Execution contract

The plan is binding. Execute stages in order; one commit per stage on the epic worktree; publish each stage to `origin/sub/AST-1166/AST-1302-list-icon-control-remediation`. Do not edit `tests/` or `docs/test-bible/**`. On ambiguity or codebase drift, stop and comment on the **parent** [AST-1166](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency) with the Stage blocked format from plan-child.

---

## Self-Assessment

**Scope:** Single-Component — UI frontend only (`App.css` + six TSX call sites). No API, config, or pattern-doc edits.

**Conf:** high — `pattern.ui.icon-control` and unused `.icon-control` CSS already landed on AST-1300; every in-scope control is named above with the exact class and child to write.

**Risk:** Medium — Skip / resurrect / pipeline-move row actions are operator-critical; a dropped `onClick` or `disabled` would block those rows. Land Meteorite is not in Files Changed, so that parent example cannot regress from this ticket.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Result |
|------|--------|
| §1.3 DRY | One `.icon-control` class; leftover parallel families deleted after last consumer |
| §2.1 config | No new config; no color enum |
| §2.4 batch | N/A |
| §2.6 state machine | No state transitions; handlers unchanged |
| §3.3 imports | No new imports |
| §3.5 placement / naming | Styles only in `App.css`; class name `icon-control` (domain language); no new component file |

No conflicts. `conf-!!-NONE` does not apply.

## Joan validate

[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1302
**Overall:** APPROVED
**Publish-ref:** `origin/sub/AST-1166/AST-1302-list-icon-control-remediation` @ `32321160a6ec32e853af680428a9d1b1b17220d3`

## Traceability
Child AC1→S1–3; Child AC2→S1–3; parent AC5→S1–2; parent AC7→S1–3; parent AC1–4,6→N/A (AST-1300/1301 boundaries)

## Findings

### discuss — Traceability labels use wrong child AC numbers
**Location:** Traceability table (“Child AC5” / “Child AC6”)
**Finding:** Child Description has two unnumbered AC bullets (list icon-only; no regression). Plan labels them AC5/AC6 (parent AC numbers; parent AC6 is in-flight gold, not this ticket).
**Recommendation:** At build handoff, read as Child AC1/AC2 or parent AC5/AC7 — mapping to stages is correct. Non-blocking.

### discuss — CollapsiblePanel chevron visual will change
**Location:** Stage 3; `.collapsible-panel-chevron-btn` → `.icon-control`
**Finding:** Old chevron was 32×32 borderless/transparent; `.icon-control` is bordered compact chrome per AST-1300. Intentional catalog conformance, not a pixel-parity swap.
**Recommendation:** Accept as in-scope presentation change; layout-only `flex: 0 0 auto` helper is appropriate. Non-blocking.

### R5 — Traceability (full)

| AC / scope item | Plan stage(s) | Notes |
|---|---|---|
| Child AC1 — list row columns icon-only; fix cramped text (`Sk`) | S1–2 | `CandidateJobRowActions`, Manage Candidates/Agents row actions |
| Child AC2 — no enablement/handler regression on touched flows | S1–3 | Explicit “do not change onClick/disabled”; Land Meteorite excluded |
| Parent AC5 — list row icon-controls only | S1–2 | Closed inventory |
| Parent AC7 — no regression on touched flows | S1–3 | Same |
| Parent AC1–4, AC6 | N/A | Patterns (AST-1300), labeled sweep / in-flight (AST-1301) |
| Parent Functional scope 5 | S1–2 | |
| Parent catalog — modal ×, chevron | S3 | |
| Child boundary — no pattern docs | — | No `canon/patterns/**` |
| Child boundary — no labeled-button sweep | — | Exclusions table + AST-1301 carve-outs explicit |

| Stage | Parent / child mapping |
|---|---|
| S1 — `CandidateJobRowActions` | Child AC1; parent AC5; `pattern.ui.icon-control` |
| S2 — Manage Candidates + Agents row columns | Child AC1; Set dispatch tasks `T` decision documented |
| S3 — Modal ×, Scheduled Actions ×, CollapsiblePanel chevron + CSS retire | Parent catalog peers; DRY cleanup |

**Inventory verification (publish-ref tip):** `rg` on TSX hits only the six planned files + `App.css` for `job-list-icon-btn` / `list-page-edit-btn` / `modal-close` / `collapsible-panel-chevron-btn`. Matches closed inventory.

**Dependency:** `pattern.ui.icon-control` + `.icon-control` CSS present on publish-ref tip (AST-1300 landed). Plan correctly consumes, does not edit pattern files.

### R6 — Adversarial checklist (summary)

| Check | Result |
|---|---|
| Definition fidelity — icon-control remediation only | Pass |
| Boundaries — no AST-1300/1301 scope creep | Pass |
| Closed inventory — no orphan surfaces in scope | Pass |
| `pattern.ui.icon-control` solution shape | Pass — single initial/glyph; no `btn` combo; no per-site color (Delete inline danger removed) |
| Layer / imports / config | Pass — UI frontend only |
| File placement | Pass — `App.css` + existing components/pages |
| DRY | Pass — retire four legacy families after last consumer |
| Self-assessment Single-Component / high / Medium | Honest |
| Resurrect `R` vs Reapply `R` | Pass — mutually exclusive state branches |

### R1–R3 — Statute matching

**Plan layers:** `ui`
**Plan paths:** six TSX files + `App.css`
**Change types:** `modify`

**Considered (38):** universal orchestration set + scoped matches including `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.names-not-ticket-ids`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.no-cross-contamination`, `astral.docs.features-single-file-per-ticket`, `orch.pipeline.plan-is-bible`, etc.

**Excluded:** `astral.git.engineer-test-tree-ban` (no test paths); `astral.config.*`; batch/agent/core statutes; `astral.seed.*`.

**Key cited pattern:** `pattern.ui.icon-control` — **conforms** (consumes approved pattern; presentation-only; `title`/`aria-label` preserved).

No statute `violates` / `needs-discussion`.

context_tokens≈82000
— Joan
