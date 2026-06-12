<!-- linear-archive: AST-308 archived 2026-06-03 -->

## Linear archive (AST-308)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-308/collapsiblepanel-component-replace-artifacteditor-tab-pattern  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** katherine  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-312; related: AST-300

### Description

New shared React component CollapsiblePanel replacing the current tab-based ArtifactEditor. Each section renders as a collapsible row: collapsed state shows section header label + optional metadata (dot matrix, score badge, status chip) in a single header row; expanded state shows full section content below. Replaces the side-tab pattern in ArtifactEditor (used by all 7 Artifacts criteria pages: GetJobCriteria, DoJobCriteria, LikeJobCriteria, JobListCriteria, JobDescCriteria, CompanyWatchCriteria, BaseResumeContent) and AdminTaskPrompts. All 7 criteria page wrappers are thin — one component change updates all of them. Job Analysis Report is built on CollapsiblePanel from day one. Component accepts: label, metadata (optional), defaultExpanded (bool), children.

### Comments

#### katherine — 2026-05-23T20:00:37.609Z
[check-linear]

- Read **Susan** thread note (2026-05-05) asking for **zero** expanded panels by default on the CollapsiblePanel / ArtifactEditor work.
- **AST-308** is **Done** (Chuckles finish-up 2026-05-18); no product or plan-doc edit attempted from this pass.
- Katherine integration branch **`dev-kath`** is currently **not** rebased cleanly onto **`origin/dev`** — see **`[check-linear]` on AST-456** for the **`CandidateProfile.tsx`** rebase conflict during §0a. If any **UI default** still looks wrong on current `origin/dev`, call it out on a **User Testing** or new ticket and we can handle it under the right stage skill.

#### chuckles — 2026-05-18T19:17:57.683Z
## finish-up (cleanup) — Chuckles

AST-308 is **Done**, not **PR Ready** — skipped formal finish-up gate.

`origin/ftr/AST-308-collapsiblepanel-component-replace-artifacteditor-tab-pattern` had **0 commits** ahead of `origin/dev`. **Deleted** stale feature branch.

— Chuckles

#### susan — 2026-05-05T16:48:57.761Z
Katherine, this looks great, but I would like to allow for 0 expanded items (in fact, I'd like you to default to zero expanded).

#### susan — 2026-05-04T21:30:21.526Z
[check-linear]

**Pass — Katherine / Astral Artifacts**

**Scanned:** `project: Astral Artifacts` + label `Katherine` for Todo, Plan Ready, Plan Approved, In Progress, Code Complete, Review Posted, Testing (`limit: 250` each; no `hasNextPage`).

**Issues in set:** AST-297, AST-299, AST-300, AST-301, AST-363, AST-366, AST-307, AST-312 (Todo); AST-308 (Testing, assignee Susan).

**Threads:**
- **AST-300 / AST-301:** One planning comment each (2026-04-29 split / ownership note). No open question directed at Katherine that needs code or doc edits in-repo from this pass.
- **Other Todo issues in set:** `list_comments` returned **no** comments.
- **AST-308:** Latest `[check-linear]` remains `faf17f57`; only follow-up is the resolve/testing handoff (`109b23e3`) — nothing new to execute in-thread.

**Actionable comments processed this pass:** **0** (no Susan / engineer-directed items after the latest `[check-linear]` that require implementation).

**Step 6 (post-inbox chain):** Not run. **a-plan-linear** queue mode would grab the first Katherine **Todo** (several exist) and produce a full plan + branch push without you naming a priority ticket; **e-push** / **d-resolve** / **b-build** are status-gated and not applicable from this drain alone. Say which **Todo** id to plan next if you want that chain executed.

**Blocked:** none.

— Katherine

#### susan — 2026-05-04T20:48:53.328Z
Review feedback resolved. Branch `chuckles/ast-308-collapsiblepanel-component-replace-artifacteditor-tab` is ready for testing. Commit: `e7b7e569`

#### susan — 2026-05-04T20:48:51.179Z
[check-linear]

**Pass 1 — Katherine queue**

- **Issues scanned:** Astral Artifacts + label `Katherine` across Todo / Plan Ready / Plan Approved / In Progress / Code Complete / Review Posted / Testing (all pages, no further results).
- **Actionable thread:** Radia’s **Review Posted** comment (2026-05-04) on this ticket — discuss/advisory items in the combined doc.
- **Done:**
  - Dropped unused **`expandMode`** from **`CollapsiblePanelProps`**.
  - **`LabeledTextArea`**: new **`hideTitle`**; **`ArtifactEditor`** uses it so the panel header is the only criterion title (code row kept when rubric uses `onCodeChange`).
  - **`CollapsiblePanel`**: label strip **`tabIndex={0}`**, **`role="button"`**, **`aria-expanded`**, Enter/Space still expand when collapsed.
  - **`docs/features/artifacts/ast-308-collapsiblepanel-component-replace-artifacteditor-tab.md`**: **Resolution** section appended.
- **Commit:** `e7b7e569` on `chuckles/ast-308-collapsiblepanel-component-replace-artifacteditor-tab` (pushed).

— Katherine

#### susan — 2026-05-04T20:19:51.283Z
**Review posted — Radia**

Summary: **0** fix-now, **2** discuss, **1** advisory (see combined doc: unused `expandMode` prop, possible duplicate criterion labels, header keyboard detail).

Diff reviewed: **`origin/dev`…feature branch** (merge-base `50aed96`). Owner label → **Katherine** per build handoff. Conf / Risk / Scope preserved.

**Combined doc:**  
https://github.com/susansomerset/astral/blob/e55c63973fe6f5d9fc0a1fe88f8dc30fd85c58e8/docs/features/artifacts/ast-308-collapsiblepanel-component-replace-artifacteditor-tab.md

— Radia

#### susan — 2026-05-04T20:07:53.653Z
Built by **Katherine**.

Branch `chuckles/ast-308-collapsiblepanel-component-replace-artifacteditor-tab` — implementation `18eb2d5`, plan stub hash `a09c613`.

— Katherine

#### susan — 2026-05-04T20:02:26.393Z
Label review (build agent):

Conf: agree — current conf-Medium matches plan scope (controlled accordion + `SideTabPanel` parity in `actions`).
Risk: agree — risk-Medium matches user-visible artifact/admin surfaces without touching dispatch/schema.
Scope: agree — scope-Single-Component matches planned files only (`CollapsiblePanel`, `ArtifactEditor`, `AdminTaskPrompts`, `App.css`).

— Katherine

#### susan — 2026-05-04T19:57:46.724Z
**Plan doc:** `docs/features/artifacts/ast-308-collapsiblepanel-component-replace-artifacteditor-tab.md` (feature branch; full refresh per updated **a-plan-linear** — stages, execution contract, Layer column, controlled-expand API).

**Self-assessment (labels):**
- **Scope — Single-Component:** Only React `components/`, `AdminTaskPrompts.tsx`, and `App.css`; no API or `config.py`.
- **Conf — Medium:** `SideTabPanel` parity for reorder/rename/delete maps to `actions`; parent-owned single-open state is clear with edge cases on candidate switch.
- **Risk — Medium:** Regressions hit artifact editing and admin prompts; modals still use `SideTabPanel` unchanged.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-308-collapsiblepanel-component-replace-artifacteditor-tab/docs/features/artifacts/ast-308-collapsiblepanel-component-replace-artifacteditor-tab.md

— Katherine

#### susan — 2026-04-29T20:57:05.372Z
**Plan revision 2 pushed:** `CollapsiblePanel` now specifies discrete **`metadata`** (read-only context from data) and **`actions`** (interactive header chrome — ▲▼×, rename, etc.). CSS: separate header regions so they stay visually distinct. Branch updated on origin.

— Katherine

#### susan — 2026-04-29T20:53:42.787Z
**Plan revision pushed** (merge `origin/dev` + updated `docs/features/artifacts/ast-308-collapsiblepanel-component-replace-artifacteditor-tab.md`).

Summary:
- **Metadata** = contextual read-only UI from *data* (badges, scores, chips). **Not** where ▲▼× / rename live — those use **`headerTrailing`** so we are not overloading the metadata slot.
- **Accordion:** single-open for ArtifactEditor + AdminTaskPrompts; **`expandMode: "single" | "multiple"`** (default single) so a later ticket can allow multi-expand without a rewrite.
- **Admin edit modal:** persisted **editable** default-expanded (`localStorage`), factory default **`user`**.

— Katherine

#### susan — 2026-04-29T20:31:06.566Z
**Plan doc:** `docs/features/artifacts/ast-308-collapsiblepanel-component-replace-artifacteditor-tab.md` (GitHub attachment on feature branch).

**Self-assessment (from plan)**

- **Scope — Single-Component:** Touches only React `components/`, `AdminTaskPrompts.tsx`, and `App.css`; no API or config.
- **Conf — Medium:** Ticket’s four props are clear; parity with `SideTabPanel` needs a small optional `headerTrailing` prop and careful UX for add/rename/reorder—understood before build.
- **Risk — Medium:** Bugs would hurt artifact editing (autosave / generate / review) but stay on that surface; `SideTabPanel` remains for entity modals.

— Katherine (plan-linear)

---

# CollapsiblePanel Component — Replace ArtifactEditor Tab Pattern

**Linear:** https://linear.app/astralcareermatch/issue/AST-308/collapsiblepanel-component-replace-artifacteditor-tab-pattern  
**Feature branch:** `<agent>/ast-308-collapsiblepanel-component-replace-artifacteditor-tab`

Replace the side-tab layout in **`ArtifactEditor`** with a stack of **`CollapsiblePanel`** rows (header: label + optional read-only metadata + optional interactive actions + chevron; body: existing editor content). Reuse the same component in **`AdminTaskPrompts`** for phase sections and the three prompt panes in the edit modal so **AST-307** (Job Analysis Report) can depend on **`CollapsiblePanel`** without a second accordion pattern. Do **not** change **`SideTabPanel`** in **`JobDetailModal`** or **`CompanyDetailModal`**; do not change Flask, `config.py`, or artifact persistence.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/CollapsiblePanel.tsx` | New shared component (`label`, optional `metadata`, optional `actions`, `defaultExpanded`, `children`, `expandMode`) | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Remove `SideTabPanel`; map `tabs` to `CollapsiblePanel`; single-open state; relocate “+ Add” control | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Phase list + edit modal use `CollapsiblePanel`; `localStorage` default-expanded panel | ui |
| `src/ui/frontend/src/App.css` | Styles for collapsible header regions (label / metadata / actions / chevron) and body | ui |

Do **not** edit `SideTabPanel.tsx`, the seven `Artifacts*.tsx` wrappers (they only import `ArtifactEditor`), or any `src/ui/api` / `src/` files unless a step below explicitly says so.

---

## Stage 1: `CollapsiblePanel` + CSS

**Done when:** `CollapsiblePanel.tsx` exists, exports a single default component, and `npx tsc -b --noEmit` passes from `src/ui/frontend`. Header is keyboard-accessible (`button` or `role="button"`, `aria-expanded`).

1. Add `src/ui/frontend/src/components/CollapsiblePanel.tsx` with props: **`label: ReactNode`**, **`metadata?: ReactNode`** (read-only context only), **`actions?: ReactNode`** (interactive header controls only — never pass interactive controls through **`metadata`**), **`defaultExpanded?: boolean`**, **`children: ReactNode`**, **`expandMode?: "single" | "multiple"`** (default **`"single"`**). **`metadata`** and **`actions`** render in **separate** flex regions; do not merge into one prop or one DOM bucket.

2. For **`expandMode="single"`**, the component does **not** own sibling state: it accepts **`expanded: boolean`** and **`onExpandedChange: (next: boolean) => void`** (or equivalent controlled API documented in the file) so **`ArtifactEditor`** / **`AdminTaskPrompts`** can enforce exactly one open panel in a group. Document in a short file comment that parents coordinate single-open.

3. In `src/ui/frontend/src/App.css`, add a TOC subsection for collapsible panels: header row uses flex + gap with distinct areas for label, metadata slot, actions slot, and chevron; collapsed body hidden without removing children from React tree if you use CSS `display`/height (pick one approach and keep it consistent).

⚠️ **Decision:** Accordion is **strict single-open** for `ArtifactEditor` and for admin phase list + edit modal, with **`expandMode`** left as an escape hatch for a future multi-open ticket without rewriting this component.

---

## Stage 2: `ArtifactEditor` migration

**Done when:** `ArtifactEditor` no longer imports `SideTabPanel`; all seven artifact criteria pages + base resume page behave as today for load, autosave, generate, threshold UI, and `beforeunload` dirty guard; only layout/navigation changes.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, remove the `SideTabPanel` import. Keep using the **`SideTab`** type from `./SideTabPanel` **or** define a local **`ArtifactSection`** type with the same fields (`id`, `label`, `content`, `code?`) so load/save/generate logic touching `tabs` is unchanged.

2. Add React state: **`expandedTabId: string | null`** (or equivalent) holding which tab is open when **`expandMode` is single**. When **`tabs`**’ identity set changes (candidate switch, regenerate empty shape, etc.), reset **`expandedTabId`** to a sensible default: **first tab id** if that tab still exists, else **first tab in the new list**.

3. Replace the **`SideTabPanel`** render with **`tabs.map`**: each item is **`CollapsiblePanel`** with **`label`** = criterion label; **`metadata`** = anything read-only you already show in the tab chrome (if nothing, omit); **`actions`** = when **`editable`**, wire ▲/▼/× to the same **`moveTab` / `removeTab` / `updateTab`** handlers **`SideTabPanel`** used; when not editable, omit **`actions`**. **`children`** = the same **`LabeledTextArea`** (and props) **`SideTabPanel`** passed through today.

4. Double-click rename when **`editable`**: match **`SideTabPanel`** behavior (rename in the header path, not hidden inside collapsed-only content).

5. Move the **“+ Add”** criterion control out of a side list: place one control below the collapsible stack (or a slim bar under the page title inside the existing **`dep-body`** wrapper) so it remains visible when every panel is collapsed.

6. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 3: `AdminTaskPrompts` migration

**Done when:** Main page phases and the edit-modal prompt areas use **`CollapsiblePanel`** with single-open behavior; default expanded panel in the modal follows persisted user choice; `handleSave` / `handlePreview` signatures and behavior unchanged.

1. In `src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, **main list:** replace the ad-hoc phase **`button` + `collapsed` state** block with one **`CollapsiblePanel`** per phase: **`label`** = phase name + count; **`children`** = existing table wrapped in **`list-page-table-wrap`** (keep class names unless CSS requires rename). Single-open across phases using the same controlled-expand pattern as Stage 2.

2. **Edit modal:** replace **`TabBar`** + single visible **`TokenTextarea`** with three **`CollapsiblePanel`** rows: User / Cache / NoCache prompts. Single-open inside the modal.

3. **Default expanded panel:** Add minimal UI (footer control or small admin chrome dropdown) plus **`localStorage`** key namespaced e.g. **`astral_admin_task_prompts_default_expanded`**. Allowed values **`user` | `cache` | `nocache`**; factory default **`user`**. On modal open, expand the matching panel and collapse the others.

4. Run `cd src/ui/frontend && npx tsc -b --noEmit`.

---

## Stage 4: Smoke verification

**Done when:** You have manually confirmed each route loads and expand/collapse does not lose edits.

1. Smoke the seven artifact routes under the app (`ArtifactsGetJobCriteria`, `ArtifactsDoJobCriteria`, `ArtifactsLikeJobCriteria`, `ArtifactsJobListCriteria`, `ArtifactsJobDescCriteria`, `ArtifactsCompanyWatchCriteria`, `ArtifactsBaseResumeContent`) — expand/collapse, add/remove/reorder when editable, generate path.

2. Smoke **Admin → Manage Tasks** (`AdminTaskPrompts`): phase expand/collapse; open edit modal; switch default expanded via setting; verify Cache/NoCache panels.

---

## Execution contract (for the developer agent)

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order across the plan.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.** No fix-on-the-fly.
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes a stage, performs the stage completion ritual (commit + Linear comment), and proceeds to the next stage only after the commit lands.

Linear comment format for a block:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope — `Single-Component`**  
Only React `components/`, one admin page, and `App.css` change; no API, `config.py`, or data layer.

**Conf — `Medium`**  
`SideTabPanel` behavior is a known template for reorder/rename/delete; mapping to `actions` + controlled accordion is clear, with some care for `expandedTabId` edge cases on candidate switch.

**Risk — `Medium`**  
A bug breaks artifact editing or admin prompts (autosave, generate, dirty tracking); impact is user-visible but scoped to those surfaces; modals still use `SideTabPanel` unchanged.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | One `CollapsiblePanel`; editor logic stays in `ArtifactEditor`. |
| §2.1 config | No `config.py` changes. |
| §2.4 / §2.6 | N/A (frontend only). |
| §3.3 imports | New file under `src/ui/frontend/src/components/`; no forbidden cross-layer imports. |
| §3.5 naming | `CollapsiblePanel.tsx` PascalCase; CSS subsection with TOC in `App.css`. |

**Conflicts:** None. Branching follows Linear skills (`<agent>/...`); ignore any stale prose elsewhere that suggests editing only `dev` without a feature branch.

---

## Revisions

Revision 1 — 2026-04-29  
Driven by: Susan (chat): metadata vs chrome; single-open accordion with `expandMode`; admin default-expanded persistence.  
Changes: Prior plan steps and decisions (superseded by this doc).

Revision 2 — 2026-04-29  
Driven by: Susan (chat): discrete **`metadata`** vs **`actions`**.  
Changes: Renamed chrome prop to **`actions`**; separate layout regions.

Revision 3 — 2026-05-04  
Driven by: **a-plan-linear** skill update (execution contract, stages with **Done when**, Files table **Layer** column, controlled-expand API called out, full replace on slug collision).  
Changes: Restructured entire plan into stages 1–4; added execution contract; normalized header (Linear URL + branch); self-assessment tightened to skill format.

---

## Review

**Branch:** `<agent>/ast-308-collapsiblepanel-component-replace-artifacteditor-tab`  
**Diff reviewed:** `origin/dev`…`origin/<agent>/ast-308-collapsiblepanel-component-replace-artifacteditor-tab` (merge-base `50aed96`)  
**Implementation commit:** `18eb2d5b12f91df437b5bf3e894e9d052061ccde`  
**Reviewed:** 2026-05-04 — Radia (`e-review-linear`). Doc-only follow-ups may land in later commits on this branch.

### What's solid

- **Plan fidelity:** New **`CollapsiblePanel`** with discrete **`metadata`** / **`actions`** regions + CSS subsection **10e** in **`App.css`**; **`ArtifactEditor`** drops **`SideTabPanel`** for a controlled single-open stack, **`+ Add`** moved below panels, reorder/rename/remove preserved; **`AdminTaskPrompts`** migrates phases + modal prompts per staged plan.
- **§3.3 / §3.5:** No forbidden cross-layer imports; component file naming and flat **`components/`** placement match project rules.
- **Single-open:** Parent-owned **`expanded` / `onExpandedChange`** with fallback when collapsing so at least one tab stays addressable matches the strict accordion decision.

### Issues

| Severity | Topic | Notes |
|----------|--------|--------|
| — | — | No fix-now items. |
| Discuss | **`expandMode` on `CollapsiblePanelProps` unused** | Prop is documented for future multi-open but never read — either wire it (e.g. ignore single-close coercion when `multiple`) or drop until needed to avoid misleading API surface. |
| Discuss | **Duplicate labeling** | Header **`label`** shows the criterion name while **`LabeledTextArea`** still receives **`label={tab.label}`** inside the body (likely pre-existing pattern from **`SideTabPanel`**). Confirm visually that stacked headers are not noisy vs the old tab chrome. |
| Advisory | **Header label strip a11y** | Chevron is a proper **`button`** with **`aria-expanded`**. The label area uses **`role="presentation"`** + click-to-expand + **`onKeyDown`** without **`tabIndex`**, so it is not keyboard-equivalent to a second toggle — acceptable if chevron is the sole keyboard path; document or add **`tabIndex={0}`** + `role="button"` if you want parity with the plan’s “header is keyboard-accessible” wording for the whole strip. |

### Recommended actions

| Priority | Action | Owner |
|----------|--------|-------|
| Discuss | Resolve **`expandMode`**: implement, remove from props, or document as reserved-for-parent-only. | Katherine |
| Advisory | Quick UX pass on one artifact page + Manage Tasks modal after merge to `dev` (spacing, duplicate titles). | Katherine |

---

## Resolution

**2026-05-04 — Katherine (post-Radia review)**

- **Unused `expandMode`:** Removed from **`CollapsiblePanelProps`**; parent-only coordination stays documented in the component file comment.
- **Duplicate criterion title:** **`ArtifactEditor`** passes **`hideTitle`** on **`LabeledTextArea`** so the collapsible header is the sole title; code row remains when **`onCodeChange`** is used.
- **Label strip a11y:** **`collapsible-panel-label-wrap`** is **`tabIndex={0}`**, **`role="button"`**, **`aria-expanded`**, plus existing Enter/Space when collapsed (chevron remains primary toggle).

