# AST-2083 — Dedicated resume editor: section rows, search/add/swatches/compare, autosave (Resume Edit Overhaul)

- **Parent:** [AST-2046 Resume Edit Overhaul](https://linear.app/astralcareermatch/issue/AST-2046)
- **Ticket:** [AST-2083](https://linear.app/astralcareermatch/issue/AST-2083)
- **Publish ref:** `sub/AST-2046/AST-2083-resume-editor` (origin only)
- **Depends on:** #1 [AST-2081](https://linear.app/astralcareermatch/issue/AST-2081) (catalog `body_format_details` / `hidden_flow_label`, `line` format, job structure PUT) and #2 [AST-2082](https://linear.app/astralcareermatch/issue/AST-2082) (`printHtml.ts`, `.print-preview-thumb` hook). Both are on `ftr/AST-2046-resume-edit-overhaul` and merged into this branch. #4 [AST-2084](https://linear.app/astralcareermatch/issue/AST-2084) mounts this editor on the base page and the job edit modal, and retires `ArtifactEditor`'s resume mode. None of #4's files are touched here.
- **Canon Scope:** `patt.artifact.ui-consistency` (as amended — parent Decision 7, dedicated resume editor), `patt.artifact.read-current`, `patt.artifact.write-operative`.

This ticket ships two new frontend components and their styles, and mounts neither of them. `ResumeContentEditor` takes a target (`{ kind: "base", id: candidateId }` or `{ kind: "job", id: jobId }`). It loads that resume's body and structure, and renders a sticky header (search, Add Section, accent swatches, Compare to Base for jobs only, and Print) over a list of `ResumeSectionRow`s. It autosaves when focus leaves the rows and on every discrete control change, and calls `onSaved()` once after each successful save. #4 uses that callback to bump `PrintPreview`'s `refreshKey`. `ResumeSectionRow` renders one section. Collapsed, it is a one-line read-only header. Expanded, it has a label input, format select, flow select, and the Job Edit flag, followed by the content editor (single-line input, text area, or `ExperienceJobsEditor`).

## Ground truth (verified on this branch at `708488377`)

- **Structure GETs:** `GET /api/candidates/<id>/resume_structure` and `GET /api/jobs/<id>/resume_structure` return `{ sections, all_sections, accent_color, catalog }`. `all_sections` is the full ordered row list including disabled rows (`SectionRow`: `{ id, title, enabled, order, format, job_agent_editable, required, format_locked, page_break_policy }`). `catalog` (`Catalog`) carries `body_formats`, `page_break_policies`, `page_break_policy_labels{key:label}`, and `new_extra_default_format`; #1 adds `body_format_details{fmt:{label, description, font_family}}` and `hidden_flow_label`. Contact rows (`header`) have `format: null` and `format_locked: true`.
- **Bodies:** `GET /api/candidates/<id>` → `candidate_data.artifacts.base_resume`. `GET /api/jobs/<id>` → `job_data.artifacts.job_resume` and top-level `candidate_id`. Both bodies are dicts keyed by section id. Values are strings, except `experience`, which is an array of jobs (`ExperienceJob[]`, same shape `ExperienceJobsEditor` edits today).
- **Saves:**
  - Base: `PUT /api/candidates/<id>/data` with `{ artifacts: { base_resume?, resume_structure?: { sections, accent_color? } } }` (`api_candidate.py` `update_candidate_data`). Either key may be sent alone.
  - Job structure: `PUT /api/jobs/<id>/artifacts/job_resume_structure` with `{ job_resume_structure: { sections, accent_color? } }` (#1).
  - Job body: `PUT /api/jobs/<id>/artifacts/job_resume` with `{ job_resume: {...} }`.
- **Server-side id assignment:** `candidate.py` `prepare_resume_structure_sections_for_save` keeps keys matching `^[a-z][a-z0-9_]*$` and slugs every other key from its title. A client placeholder id (`_pending_1`) therefore comes back renamed, so the client must refetch the structure and adopt the server ids by position. Normalization rejects an empty title and refuses to disable a required section.
- **Hidden content on save:** the base `/data` PUT filters `base_resume` down to the **enabled** sections of the saved structure, and job prep (`tracker.py` `_prepare_job_resume_content`) filters `job_resume` to the enabled sections of the job's effective structure. So the body of a section set to Hidden is dropped on the next body save (existing #1-era behavior; see Decision 12).
- **Print:** `src/ui/frontend/src/lib/printHtml.ts` (#2) — `fetchPrintHtml({ kind: "base" | "job_resume" | "cover", id })` returns `{ ok: true, html } | { ok: false, error }`. `openHtmlInNewTab(html)` returns `null` on success, or the error text (`POPUP_BLOCKED_MESSAGE`, the existing "Popup blocked" toast) when the popup is blocked.
- **Reused UI pieces:** `ExperienceJobsEditor` (props `value`, `onChange`; role label at L122–125 uses `.experience-jobs-editor-role-label`, styled `color: var(--text-muted)` at App.css ~L2009), `useUserConfirm` (`UserPrompt.tsx`), `useToast`, `getUiConfig()` / `loadUiConfig()` (`lib/uiConfig.ts`: `base_resume_accent_palette`, `experience_job_ui_fields`, `unsupported_resume_structure_message`), `api()` (`lib/api.ts`), the `Catalog` / `SectionRow` types (`ResumeStructureEditor.tsx`), and the swatch classes `.base-resume-accent-swatch*` (still used by today's base page).
- **Retired CSS:** `.base-resume-structure-editor*`, `.base-resume-structure-row/-add/-row-id/-save` and `.structure-authoring-header/-name/-style/-flag` (App.css L1463–1527). `.base-resume-structure-*` has no `className` user left in `src/`. `.structure-authoring-*` is still emitted by `ArtifactEditor`'s resume mode, which #4 deletes.
- **AC5 / AC13 greps today:** `git grep -n "Save sections" -- src/ui/frontend/src` hits only `ArtifactEditor.tsx` L1395 (removed by #4, its own AC 2). `git grep -nE "Word Cloud|Bullet List|Flow uninterrupted" -- src/ui/frontend/src` is already empty, and the new files add no hits.
- **ESLint:** `react-hooks` v7 recommended (`react-hooks/refs` bans ref writes during render; `set-state-in-effect`). `ExperienceJobsEditor.tsx` has one pre-existing error (L65 `set-state-in-effect`), which is the baseline and is untouched here.
- **Existing tests:** `test_ArtifactsBaseResumeContent.test.tsx` (L231, L617, L689–693) and `test_ArtifactEditor.test.tsx` (L1472) query `.structure-authoring-*` **markup** in `ArtifactEditor`. That markup is unchanged here (only its CSS goes), so there is no known test drift from this ticket. Those tests move with #4.

## Canon conformance

- **`patt.artifact.ui-consistency` (as amended — Decision 7):** both resume surfaces get the same dedicated editor (one component, target-switched). It has no Save / Cancel / "Save sections" buttons; all saves are automatic. Every format and flow label, description, and preview font comes from the catalog payload; the only client-side map is presentational (flow → glyph).
- **`patt.artifact.read-current`:** the editor reads body and structure from the live GETs on mount and per target (the inner editor is keyed by target, so a new target never shows a stale copy). Compare to Base reads the candidate's **current** base resume and base structure each time it is switched on. After a save that carries a new section, the editor refetches the structure and adopts the server-assigned ids instead of trusting its placeholders.
- **`patt.artifact.write-operative`:** every write goes through the operative artifact routes (candidate `/data`, job `job_resume_structure`, job `job_resume`), and only the halves that changed are sent. A job body-only edit never PUTs structure, so an inherited job structure stays inherited. Saves are serialized, so two PUTs never race.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ResumeSectionRow.tsx` | **New** — one section row (collapsed header / expanded header + content / compare blocks) and the shared editor types | ui (component) |
| `src/ui/frontend/src/components/ResumeContentEditor.tsx` | **New** — load, header controls, row list, autosave, Compare to Base, Print, `onSaved` | ui (component) |
| `src/ui/frontend/src/components/ExperienceJobsEditor.tsx` | Role label gains `resume-section-title` (section-header color) | ui (component) |
| `src/ui/frontend/src/App.css` | New §10e2 editor/row/compare/thumbnail rules; role label loses `--text-muted`; retired structure-authoring rules removed | ui (styles) |

**Scope gate:** exactly the four files on the ticket's Scope. No backend, no page/modal wiring, no new dependencies, and no edits under `tests/`.

## Stage 1: Styles + experience header color

**Files:** `src/ui/frontend/src/App.css`, `src/ui/frontend/src/components/ExperienceJobsEditor.tsx`.

Apply this diff exactly. It removes the retired structure-authoring rules, drops the muted color from the experience role label, adds `resume-section-title` to that label (so it takes `var(--heading)`, the same rule the section title uses — AC16), and adds §10e2.

```diff
diff --git a/src/ui/frontend/src/App.css b/src/ui/frontend/src/App.css
index 7bc05048d..56f1832bc 100644
--- a/src/ui/frontend/src/App.css
+++ b/src/ui/frontend/src/App.css
@@ -1460,72 +1460,6 @@ body {
   outline-offset: 2px;
 }
 
-.base-resume-structure-editor {
-  padding: 10px 20px;
-  border-bottom: 1px solid var(--border);
-  background: var(--bg-elevated);
-}
-
-.base-resume-structure-editor-title {
-  display: block;
-  font-size: 12px;
-  font-weight: 600;
-  color: var(--text-muted);
-  text-transform: uppercase;
-  letter-spacing: 0.06em;
-  margin-bottom: 8px;
-}
-
-.base-resume-structure-row,
-.base-resume-structure-add {
-  display: flex;
-  flex-wrap: wrap;
-  align-items: center;
-  gap: 8px;
-  margin-bottom: 8px;
-}
-
-.base-resume-structure-row-id {
-  font-size: 12px;
-  color: var(--text-muted);
-  min-width: 8em;
-}
-
-.base-resume-structure-save {
-  margin-top: 4px;
-}
-
-.structure-authoring-header {
-  display: flex;
-  flex-wrap: nowrap;
-  align-items: center;
-  gap: 8px;
-  flex: 1;
-  min-width: 0;
-  overflow-x: auto;
-}
-
-.structure-authoring-name {
-  flex: 1 1 auto;
-  min-width: 8rem;
-}
-
-.structure-authoring-style {
-  flex: 0 0 auto;
-  width: 9rem;
-  max-width: 12rem;
-}
-
-.structure-authoring-flag {
-  display: inline-flex;
-  align-items: center;
-  gap: 4px;
-  flex: 0 0 auto;
-  white-space: nowrap;
-  font-weight: 400;
-  color: var(--text-muted);
-}
-
 .dep-header {
   display: flex;
   align-items: center;
@@ -2008,7 +1942,6 @@ input.side-tab-heading-editable:focus {
 
 .experience-jobs-editor-role-label {
   font-size: 12px;
-  color: var(--text-muted);
 }
 
 .experience-jobs-editor-add {
@@ -2021,6 +1954,190 @@ input.side-tab-heading-editable:focus {
   font-size: 13px;
 }
 
+/* === 10e2. Resume content editor (AST-2083) === */
+
+.resume-editor {
+  display: flex;
+  flex-direction: column;
+  min-height: 100%;
+}
+
+.resume-editor-header {
+  position: sticky;
+  top: 0;
+  z-index: 1;
+  display: flex;
+  flex-wrap: wrap;
+  align-items: center;
+  gap: 8px;
+  padding: 10px 12px;
+  border-bottom: 1px solid var(--border);
+  background: var(--bg-elevated);
+}
+
+.resume-editor-header .resume-editor-search {
+  flex: 1 1 10rem;
+  width: auto;
+  min-width: 8rem;
+}
+
+.resume-editor-rows {
+  padding: 8px 12px;
+}
+
+.resume-section-row {
+  margin-bottom: 6px;
+  border: 1px solid var(--border-subtle);
+  border-radius: 6px;
+  background: var(--bg-card);
+  overflow: hidden;
+}
+
+.resume-section-row.is-expanded {
+  border-color: var(--border);
+}
+
+.resume-section-header {
+  display: flex;
+  align-items: center;
+  gap: 6px;
+  min-height: 36px;
+  padding: 4px 8px 4px 4px;
+  background: var(--bg-elevated);
+}
+
+.resume-section-header > button,
+.resume-section-header > span {
+  flex: 0 0 auto;
+}
+
+/* Section header text; experience job headers share it (AC: same computed color). */
+.resume-section-title {
+  color: var(--heading);
+}
+
+.resume-section-header > .resume-section-summary {
+  flex: 1 1 auto;
+  display: flex;
+  gap: 4px;
+  min-width: 0;
+  padding: 0;
+  border: 0;
+  background: none;
+  font: inherit;
+  font-size: 14px;
+  color: var(--text-primary);
+  text-align: left;
+  white-space: nowrap;
+  overflow: hidden;
+  cursor: pointer;
+}
+
+.resume-section-summary .resume-section-title {
+  font-weight: 600;
+}
+
+.resume-section-value {
+  overflow: hidden;
+  text-overflow: ellipsis;
+  color: var(--text-secondary);
+}
+
+.resume-section-drag {
+  color: var(--text-muted);
+  cursor: grab;
+  user-select: none;
+}
+
+.resume-section-icon,
+.resume-section-format {
+  font-size: 12px;
+  color: var(--text-muted);
+  cursor: help;
+}
+
+.resume-section-format {
+  padding: 0 6px;
+  border: 1px solid var(--border-subtle);
+  border-radius: 4px;
+}
+
+.resume-section-header .resume-section-label-input {
+  flex: 1 1 auto;
+  width: auto;
+  min-width: 8rem;
+  font-weight: 600;
+}
+
+.resume-section-header .resume-section-select {
+  flex: 0 0 auto;
+  width: 10rem;
+}
+
+.resume-section-flag {
+  display: inline-flex;
+  align-items: center;
+  gap: 4px;
+  font-size: 12px;
+  color: var(--text-muted);
+  white-space: nowrap;
+}
+
+.resume-section-body {
+  padding: 8px;
+  background: var(--bg-deep);
+}
+
+.resume-section-textarea {
+  min-height: 8rem;
+  resize: vertical;
+}
+
+.resume-section-compare {
+  margin: 8px;
+  padding: 6px 8px;
+  border-left: 3px solid var(--border);
+  background: var(--bg-deep);
+  font-size: 13px;
+  color: var(--text-secondary);
+  white-space: pre-wrap;
+}
+
+.resume-section-new {
+  border-left-color: var(--accent-gold);
+}
+
+.resume-section-removed {
+  display: flex;
+  align-items: center;
+  gap: 8px;
+  margin-bottom: 6px;
+  padding: 6px 8px;
+  border: 1px dashed var(--border);
+  border-radius: 6px;
+  font-size: 13px;
+  color: var(--text-muted);
+}
+
+.resume-section-removed-text {
+  flex: 1 1 auto;
+  min-width: 0;
+  overflow: hidden;
+  text-overflow: ellipsis;
+  white-space: nowrap;
+}
+
+/* PrintPreview thumbnail hook (AST-2082). */
+.print-preview-thumb {
+  border: 1px solid var(--border);
+  border-radius: 4px;
+  background: #fff;
+}
+
+.print-preview-thumb:hover {
+  border-color: var(--accent-gold);
+}
+
 /* === 10f. Section expand chrome (AST-893) === */
 .section-expand-chrome {
   display: flex;
diff --git a/src/ui/frontend/src/components/ExperienceJobsEditor.tsx b/src/ui/frontend/src/components/ExperienceJobsEditor.tsx
index 9ad1904c5..fce4dee45 100644
--- a/src/ui/frontend/src/components/ExperienceJobsEditor.tsx
+++ b/src/ui/frontend/src/components/ExperienceJobsEditor.tsx
@@ -122,7 +122,7 @@ export default function ExperienceJobsEditor({
       {value.map((job, index) => (
         <CollapsiblePanel
           key={index}
-          label={<span className="experience-jobs-editor-role-label">{roleCollapsedLabel(job)}</span>}
+          label={<span className="experience-jobs-editor-role-label resume-section-title">{roleCollapsedLabel(job)}</span>}
           defaultExpanded={false}
           actions={
             <span className="side-tab-controls">
```

**Done when:**

- `rg -n "structure-authoring-|base-resume-structure-(editor|row|add|save)" src/ui/frontend/src/App.css` returns nothing.
- `cd src/ui/frontend && npm run build` succeeds.
- Commit: `feat(AST-2083): resume editor styles + experience header color`.

## Stage 2: `ResumeSectionRow`

**File:** `src/ui/frontend/src/components/ResumeSectionRow.tsx` (new). Full content:

```tsx
import type { DragEvent } from "react"
import ExperienceJobsEditor, { type ExperienceJob, type ExperienceJobField } from "./ExperienceJobsEditor"
import type { Catalog, SectionRow } from "./ResumeStructureEditor"

/** Structure catalog as served by the resume_structure GETs (AST-2081 adds format details + Hidden label). */
export type EditorCatalog = Catalog & {
  body_format_details: Record<string, { label: string; description: string; font_family: string }>
  hidden_flow_label: string
}

/** Section body: text for every format; a job array for experience (string there = unparseable legacy). */
export type SectionBody = string | ExperienceJob[]

/** Compare to Base state for one job row (AST-2083). */
export type RowCompare = { kind: "differs"; baseText: string } | { kind: "new" }

// Flow-select value for enabled=false; cannot collide with a page_break_policy token.
const HIDDEN = "__hidden__"
// Presentational glyph per flow state; tooltip text always comes from the catalog.
const FLOW_GLYPHS: Record<string, string> = {
  [HIDDEN]: "⊘",
  page_break_before: "⤒",
  avoid_split: "▣",
  normal: "≈",
}

export interface ResumeSectionRowProps {
  row: SectionRow
  body: SectionBody
  /** One-line plain-text value for the collapsed header. */
  preview: string
  catalog: EditorCatalog
  experienceFields: ExperienceJobField[]
  /** Shown instead of the experience editor when the stored body is not a job array. */
  unsupportedMessage: string
  expanded: boolean
  isFirst: boolean
  isLast: boolean
  /** Job Edit checkbox — base resume only. */
  showJobEdit: boolean
  /** New row not yet saved: content stays disabled until the server assigns its id. */
  contentLocked: boolean
  compare: RowCompare | null
  onToggle: () => void
  /** `save` true → header control changed (save now); false → label typing (saves on field exit). */
  onPatch: (patch: Partial<SectionRow>, save: boolean) => void
  onBodyChange: (body: SectionBody) => void
  onMove: (delta: -1 | 1) => void
  onDelete: () => void
  onDragStart: () => void
  onDrop: () => void
}

export default function ResumeSectionRow({
  row,
  body,
  preview,
  catalog,
  experienceFields,
  unsupportedMessage,
  expanded,
  isFirst,
  isLast,
  showJobEdit,
  contentLocked,
  compare,
  onToggle,
  onPatch,
  onBodyChange,
  onMove,
  onDelete,
  onDragStart,
  onDrop,
}: ResumeSectionRowProps) {
  const flow = row.enabled ? row.page_break_policy : HIDDEN
  const flowLabel = flow === HIDDEN ? catalog.hidden_flow_label : (catalog.page_break_policy_labels[flow] ?? flow)
  // Contact sections carry format null: no format label, select, or catalog font.
  const fmt = row.format ? catalog.body_format_details[row.format] : undefined
  const isExperience = row.id === "experience"

  const arrows = (
    <>
      <button type="button" disabled={isFirst} onClick={() => onMove(-1)} title="Move up">▲</button>
      <button type="button" disabled={isLast} onClick={() => onMove(1)} title="Move down">▼</button>
      {!row.required && (
        <button type="button" onClick={onDelete} title="Delete section" aria-label="Delete section">×</button>
      )}
    </>
  )

  function startDrag(e: DragEvent) {
    // Firefox only starts a drag when data is set.
    e.dataTransfer?.setData("text/plain", row.id)
    onDragStart()
  }

  function renderContent() {
    if (isExperience) {
      if (!Array.isArray(body)) {
        return (
          <>
            <p className="experience-jobs-editor-unsupported">{unsupportedMessage}</p>
            <textarea className="dep-input resume-section-textarea" value={body} readOnly />
          </>
        )
      }
      return (
        <ExperienceJobsEditor fields={experienceFields} value={body} onChange={onBodyChange} disabled={contentLocked} />
      )
    }
    const text = typeof body === "string" ? body : ""
    return row.format === "line" ? (
      <input
        className="dep-input"
        type="text"
        aria-label={`${row.title} content`}
        value={text}
        disabled={contentLocked}
        onChange={e => onBodyChange(e.target.value)}
      />
    ) : (
      <textarea
        className="dep-input resume-section-textarea"
        aria-label={`${row.title} content`}
        value={text}
        disabled={contentLocked}
        onChange={e => onBodyChange(e.target.value)}
      />
    )
  }

  return (
    <div
      className={"resume-section-row" + (expanded ? " is-expanded" : "")}
      data-section-id={row.id}
      onDragOver={e => e.preventDefault()}
      onDrop={e => { e.preventDefault(); onDrop() }}
    >
      <div className="resume-section-header">
        <button type="button" className="icon-control" onClick={onToggle} aria-expanded={expanded} title={expanded ? "Collapse" : "Expand"}>
          {expanded ? "▾" : "▸"}
        </button>
        {expanded ? (
          <>
            <input
              className="dep-input resume-section-label-input resume-section-title"
              type="text"
              aria-label="Section label"
              value={row.title}
              autoFocus={contentLocked && !row.title}
              onChange={e => onPatch({ title: e.target.value }, false)}
            />
            {fmt && (
              <select
                className="dep-input resume-section-select"
                aria-label="Format"
                value={row.format ?? ""}
                disabled={row.format_locked}
                onChange={e => onPatch({ format: e.target.value }, true)}
              >
                {catalog.body_formats.map(f => (
                  <option key={f} value={f}>{catalog.body_format_details[f]?.label ?? f}</option>
                ))}
              </select>
            )}
            <select
              className="dep-input resume-section-select"
              aria-label="Flow"
              value={flow}
              onChange={e => onPatch(
                e.target.value === HIDDEN ? { enabled: false } : { enabled: true, page_break_policy: e.target.value },
                true,
              )}
            >
              {!row.required && <option value={HIDDEN}>{catalog.hidden_flow_label}</option>}
              {catalog.page_break_policies.map(p => (
                <option key={p} value={p}>{catalog.page_break_policy_labels[p] ?? p}</option>
              ))}
            </select>
            {showJobEdit && (
              <label className="resume-section-flag">
                Job Edit
                <input
                  type="checkbox"
                  checked={row.job_agent_editable}
                  onChange={e => onPatch({ job_agent_editable: e.target.checked }, true)}
                />
              </label>
            )}
            {arrows}
          </>
        ) : (
          <>
            <span className="resume-section-drag" draggable onDragStart={startDrag} title="Drag to reorder">⠿</span>
            <button type="button" className="resume-section-summary" onClick={onToggle}>
              <span className="resume-section-title">{row.title}</span>:{" "}
              <span className="resume-section-value" style={fmt ? { fontFamily: fmt.font_family } : undefined}>
                {preview}
              </span>
            </button>
            <span className="resume-section-icon" title={flowLabel} aria-label={flowLabel}>
              {FLOW_GLYPHS[flow] ?? "•"}
            </span>
            {fmt && <span className="resume-section-format" title={fmt.description}>{fmt.label}</span>}
            {arrows}
          </>
        )}
      </div>
      {expanded && <div className="resume-section-body">{renderContent()}</div>}
      {compare?.kind === "differs" && <div className="resume-section-compare">{compare.baseText}</div>}
      {compare?.kind === "new" && (
        <div className="resume-section-compare resume-section-new">NEW SECTION: Not found in base</div>
      )}
    </div>
  )
}
```

Behavior notes:

- **Collapsed** (AC8): drag handle, a summary button `<title>: <value>` (value styled with the catalog `font_family` for its format), flow glyph with `title`/`aria-label` = `page_break_policy_labels[policy]` (or `hidden_flow_label` when disabled), format label with `title` = catalog description, ▲ / ▼, and × for non-required rows only. Contact rows (`format === null`) show no format label and no font override.
- **Expanded:** label input (auto-focused on a new empty row), Format select (omitted when `format` is null, disabled when `format_locked`, option text from `body_format_details`), Flow select (Hidden omitted on required rows — AC9), Job Edit checkbox (`job_agent_editable`, base only), ▲ / ▼, ×.
- **Content:** `experience` → `ExperienceJobsEditor` (or a read-only notice + text area when the stored value isn't an array); `line` → single-line input (AC12); everything else → text area.
- **Compare:** when `compare` is set, renders the read-only base block (`differs`) or "NEW SECTION: Not found in base" (`new`) under the row (AC14).
- **Drag:** native HTML5 drag; the row is the drop target and reports `onDropRow(draggedId)`.

**Done when:**

- `npx tsc -b --noEmit` and `npx eslint src/components/ResumeSectionRow.tsx` are clean.
- Commit: `feat(AST-2083): ResumeSectionRow`.

## Stage 3: `ResumeContentEditor`

**File:** `src/ui/frontend/src/components/ResumeContentEditor.tsx` (new). Full content:

```tsx
import { useCallback, useEffect, useRef, useState } from "react"
import type { ExperienceJob, ExperienceJobField } from "./ExperienceJobsEditor"
import ResumeSectionRow, { type EditorCatalog, type RowCompare, type SectionBody } from "./ResumeSectionRow"
import type { SectionRow } from "./ResumeStructureEditor"
import Toast, { type ToastMessage } from "./Toast"
import { useUserConfirm } from "./UserPrompt"
import api from "../lib/api"
import { fetchPrintHtml, openHtmlInNewTab } from "../lib/printHtml"
import { getUiConfig, loadUiConfig, type UiConfig } from "../lib/uiConfig"

/** Which resume to edit: `id` is the candidate id for `base`, else the job id. */
export interface ResumeEditorTarget {
  kind: "base" | "job"
  id: string
}

export interface ResumeContentEditorProps {
  target: ResumeEditorTarget
  /** Called once after each save that wrote at least one PUT (preview refresh). */
  onSaved?: () => void
}

/** ui_config keys this editor reads (served by /api/ui_config; not on the shared UiConfig type). */
type ResumeUiConfig = UiConfig & {
  base_resume_accent_palette?: string[]
  experience_job_ui_fields?: { key: string; label?: string }[]
  unsupported_resume_structure_message?: string
}

// Same contract keys ArtifactEditor falls back to when ui_config is unavailable (AST-1351).
const EXPERIENCE_FIELD_FALLBACK: ExperienceJobField[] = [
  { key: "company", label: "Company" },
  { key: "title", label: "Title" },
  { key: "dates", label: "Dates" },
  { key: "location", label: "Location" },
  { key: "accomplishments", label: "Accomplishments" },
]
const UNSUPPORTED_FALLBACK = "unsupported resume structure, please regenerate"
// Client-only id for an added row until the server slugs its title into a real id (never matches the id pattern).
const PENDING = "_pending_"

type Loaded = {
  rows: SectionRow[]
  bodies: Record<string, SectionBody>
  accent: string | null
  catalog: EditorCatalog
  candidateId: string
}
type BaseSnapshot = { rows: SectionRow[]; bodies: Record<string, SectionBody> }
type Item = { kind: "row"; row: SectionRow } | { kind: "removed"; base: SectionRow; anchor: string | null }

async function getJson(path: string) {
  const r = await api(path)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

async function putJson(path: string, payload: unknown) {
  const r = await api(path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({})) as { error?: string }
    throw new Error(err.error || `Save failed (${r.status})`)
  }
}

function toJob(raw: Record<string, unknown>): ExperienceJob {
  const out: ExperienceJob = {}
  for (const [k, v] of Object.entries(raw)) {
    // AST-1381: accomplishments persist as string[]; coerce a legacy newline string on read.
    out[k] = k === "accomplishments"
      ? (Array.isArray(v) ? v.map(String) : typeof v === "string" ? v.split("\n") : []).map(s => s.trim()).filter(Boolean)
      : v == null ? "" : String(v)
  }
  return out
}

/** Stored resume dict (or legacy [{label, content}]) → id-keyed bodies for the given rows. */
function parseBodies(raw: unknown, rows: SectionRow[]): Record<string, SectionBody> {
  const dict: Record<string, unknown> = Array.isArray(raw)
    ? Object.fromEntries((raw as { label?: string; content?: unknown }[]).map(v => [
        rows.find(r => r.title === v.label)?.id ?? String(v.label), v.content,
      ]))
    : raw && typeof raw === "object" ? raw as Record<string, unknown> : {}
  const out: Record<string, SectionBody> = {}
  for (const row of rows) {
    const v = dict[row.id]
    if (row.id === "experience") {
      const isJobs = Array.isArray(v) && v.every(j => j != null && typeof j === "object" && !Array.isArray(j))
      // Unparseable legacy experience stays a string so the row shows the unsupported notice.
      out[row.id] = isJobs ? (v as Record<string, unknown>[]).map(toJob) : typeof v === "string" && v.trim() ? v : []
    } else {
      out[row.id] = typeof v === "string" ? v : v == null ? "" : JSON.stringify(v, null, 2)
    }
  }
  return out
}

/** Plain text of a body: search haystack, compare display, and (whitespace-collapsed) row preview. */
function bodyText(body: SectionBody | undefined, fields: ExperienceJobField[]): string {
  if (body === undefined) return ""
  if (typeof body === "string") return body
  return body.map(job => {
    const head = fields.filter(f => f.key !== "accomplishments").map(f => String(job[f.key] ?? "").trim()).filter(Boolean)
    const acc = Array.isArray(job.accomplishments) ? job.accomplishments.map(a => `• ${a}`) : []
    return [head.join(" · "), ...acc].filter(Boolean).join("\n")
  }).join("\n\n")
}

/** Compare equality: trimmed text, or the job array as JSON; empty array equals empty text. */
function bodyKey(body: SectionBody | undefined): string {
  if (body === undefined) return ""
  if (typeof body === "string") return body.trim()
  return body.length ? JSON.stringify(body) : ""
}

function reindex(rows: SectionRow[]): SectionRow[] {
  return rows.map((r, i) => ({ ...r, order: i }))
}

/** Remount per target so a switch never saves one resume's state onto another. */
export default function ResumeContentEditor({ target, onSaved }: ResumeContentEditorProps) {
  return <Editor key={`${target.kind}:${target.id}`} target={target} onSaved={onSaved} />
}

function Editor({ target, onSaved }: ResumeContentEditorProps) {
  const { kind, id } = target
  const isJob = kind === "job"
  const enc = encodeURIComponent(id)
  const structUrl = isJob ? `/api/jobs/${enc}/resume_structure` : `/api/candidates/${enc}/resume_structure`
  const confirm = useUserConfirm()

  const [data, setData] = useState<Loaded | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [ui, setUi] = useState<ResumeUiConfig | null>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [search, setSearch] = useState("")
  const [compareOn, setCompareOn] = useState(false)
  const [base, setBase] = useState<BaseSnapshot | null>(null)
  const [printing, setPrinting] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  // Every data write goes through dataRef first, so blur / unmount saves always send the latest edit.
  const dataRef = useRef<Loaded | null>(null)
  const onSavedRef = useRef(onSaved)
  useEffect(() => { onSavedRef.current = onSaved })
  const structDirtyRef = useRef(false)
  const bodyDirtyRef = useRef(false)
  const saveChainRef = useRef<Promise<void>>(Promise.resolve())
  const mountedRef = useRef(true)
  const pendingSeqRef = useRef(0)
  const dragIdRef = useRef<string | null>(null)

  const experienceFields: ExperienceJobField[] = ui?.experience_job_ui_fields?.length
    ? ui.experience_job_ui_fields.map(f => ({ key: f.key, label: f.label || f.key }))
    : EXPERIENCE_FIELD_FALLBACK
  const unsupportedMessage = ui?.unsupported_resume_structure_message || UNSUPPORTED_FALLBACK
  const palette = ui?.base_resume_accent_palette ?? []

  useEffect(() => {
    let live = true
    loadUiConfig(() => { if (live) setUi(getUiConfig() as ResumeUiConfig | null) })
    return () => { live = false }
  }, [])

  // patt.artifact.read-current: body from the entity GET hydrate, structure from the structure GET.
  useEffect(() => {
    let live = true
    const entityUrl = isJob ? `/api/jobs/${enc}` : `/api/candidates/${enc}`
    Promise.all([getJson(entityUrl), getJson(structUrl)]).then(([entity, struct]) => {
      if (!live) return
      const arts = (isJob ? entity.job_data?.artifacts : entity.candidate_data?.artifacts) ?? {}
      const rows = (Array.isArray(struct.all_sections) ? struct.all_sections : []) as SectionRow[]
      dataRef.current = {
        rows,
        bodies: parseBodies(arts[isJob ? "job_resume" : "base_resume"], rows),
        accent: typeof struct.accent_color === "string" ? struct.accent_color.toUpperCase() : null,
        catalog: struct.catalog as EditorCatalog,
        candidateId: isJob ? String(entity.candidate_id ?? "") : id,
      }
      setData(dataRef.current)
    }).catch(e => { if (live) setLoadError(`Failed to load resume: ${(e as Error).message}`) })
    return () => { live = false }
  }, [isJob, enc, id, structUrl])

  // Compare to Base: current base resume + base structure, refetched each time the toggle turns on.
  const candidateId = data?.candidateId
  useEffect(() => {
    if (!compareOn || !candidateId) return
    let live = true
    const cid = encodeURIComponent(candidateId)
    Promise.all([getJson(`/api/candidates/${cid}`), getJson(`/api/candidates/${cid}/resume_structure`)])
      .then(([c, struct]) => {
        if (!live) return
        const rows = (Array.isArray(struct.all_sections) ? struct.all_sections : []) as SectionRow[]
        setBase({ rows, bodies: parseBodies(c.candidate_data?.artifacts?.base_resume, rows) })
      })
      .catch(e => { if (live) setToast({ text: `Compare failed: ${(e as Error).message}`, variant: "error" }) })
    return () => { live = false }
  }, [compareOn, candidateId])

  /** Update editor state from the latest ref; mark which half changed; optionally save now (header controls, moves, adds, deletes). */
  const apply = (
    update: (cur: Loaded) => Partial<Loaded> | null,
    dirty: { struct?: boolean; body?: boolean },
    save: boolean,
  ) => {
    const cur = dataRef.current
    const next = cur && update(cur)
    if (!cur || !next) return
    dataRef.current = { ...cur, ...next }
    setData(dataRef.current)
    if (dirty.struct) structDirtyRef.current = true
    if (dirty.body) bodyDirtyRef.current = true
    if (save) void flush()
  }

  /** After a save that carried new rows: adopt the server's slugged ids (position order) for those rows. */
  async function adoptServerIds(sentPending: string[]) {
    const struct = await getJson(structUrl)
    const cur = dataRef.current
    if (!cur) return
    const known = new Set(cur.rows.map(r => r.id))
    const fresh = (struct.all_sections as SectionRow[]).filter(s => !known.has(s.id)).map(s => s.id)
    const rename = new Map(sentPending.map((pid, i) => [pid, fresh[i]] as const).filter(([, sid]) => !!sid))
    if (rename.size === 0) return
    // Content is locked while pending, so only the (empty) body key moves with the id.
    apply(c => {
      const bodies = { ...c.bodies }
      for (const [pid, sid] of rename) {
        bodies[sid] = bodies[pid]
        delete bodies[pid]
      }
      return { rows: c.rows.map(r => ({ ...r, id: rename.get(r.id) ?? r.id })), bodies }
    }, {}, false)
    setExpanded(prev => new Set([...prev].map(x => rename.get(x) ?? x)))
  }

  /** One save: sends only the half that changed. Base: one candidate /data PUT; job: structure PUT then job_resume PUT. */
  async function saveOnce(): Promise<void> {
    const cur = dataRef.current
    const structDirty = structDirtyRef.current
    let bodyDirty = bodyDirtyRef.current
    if (!cur || (!structDirty && !bodyDirty)) return
    // A new row is not sent until it has a label (the server requires a title).
    const rows = cur.rows.filter(r => !(r.id.startsWith(PENDING) && !r.title.trim()))
    const sentPending = rows.filter(r => r.id.startsWith(PENDING)).map(r => r.id)
    const experience = cur.bodies.experience
    if (bodyDirty && typeof experience === "string" && experience.trim()) {
      // Unparseable legacy experience: never overwrite it; structure edits still save.
      setToast({ text: unsupportedMessage, variant: "error" })
      bodyDirty = false
    }
    structDirtyRef.current = false
    if (bodyDirty) bodyDirtyRef.current = false
    if (!structDirty && !bodyDirty) return
    const structure = {
      sections: Object.fromEntries(rows.map((r, i) => [r.id, {
        id: r.id,
        title: r.title,
        enabled: r.enabled,
        order: i,
        job_agent_editable: r.job_agent_editable,
        page_break_policy: r.page_break_policy,
        ...(r.format ? { format: r.format } : {}),
      }])),
      ...(cur.accent ? { accent_color: cur.accent } : {}),
    }
    const body = Object.fromEntries(
      rows.filter(r => !r.id.startsWith(PENDING) && cur.bodies[r.id] !== undefined).map(r => [r.id, cur.bodies[r.id]]),
    )
    try {
      if (isJob) {
        if (structDirty) await putJson(`/api/jobs/${enc}/artifacts/job_resume_structure`, { job_resume_structure: structure })
        if (bodyDirty) await putJson(`/api/jobs/${enc}/artifacts/job_resume`, { job_resume: body })
      } else {
        await putJson(`/api/candidates/${enc}/data`, {
          artifacts: { ...(bodyDirty ? { base_resume: body } : {}), ...(structDirty ? { resume_structure: structure } : {}) },
        })
      }
      if (sentPending.length) await adoptServerIds(sentPending)
    } catch (e) {
      // Keep the unsaved halves dirty so the next field exit retries them.
      if (structDirty) structDirtyRef.current = true
      if (bodyDirty) bodyDirtyRef.current = true
      if (mountedRef.current) setToast({ text: (e as Error).message || "Save failed", variant: "error" })
      return
    }
    if (mountedRef.current) onSavedRef.current?.()
  }

  /** Serialize saves so PUTs land in edit order; returns when this save (and any before it) settles. */
  function flush(): Promise<void> {
    const run = saveChainRef.current.then(saveOnce)
    saveChainRef.current = run.catch(() => {})
    return run
  }
  const flushRef = useRef(flush)
  useEffect(() => { flushRef.current = flush })

  // Leaving the page/modal saves pending edits; closing the tab with unsaved edits prompts.
  useEffect(() => {
    mountedRef.current = true
    const guard = (e: BeforeUnloadEvent) => {
      if (structDirtyRef.current || bodyDirtyRef.current) e.preventDefault()
    }
    window.addEventListener("beforeunload", guard)
    return () => {
      window.removeEventListener("beforeunload", guard)
      mountedRef.current = false
      void flushRef.current()
    }
  }, [])

  if (loadError) return <p className="entity-error">{loadError}</p>
  if (!data) return <p className="list-page-status">Loading...</p>
  const { rows, bodies, catalog, accent } = data

  const patchRow = (rid: string, patch: Partial<SectionRow>, save: boolean) =>
    apply(c => ({ rows: c.rows.map(r => (r.id === rid ? { ...r, ...patch } : r)) }), { struct: true }, save)

  const moveRow = (fromId: string | null, toIndex: number) => apply(c => {
    const from = c.rows.findIndex(r => r.id === fromId)
    if (from < 0 || toIndex < 0 || toIndex >= c.rows.length || from === toIndex) return null
    const next = c.rows.slice()
    const [moved] = next.splice(from, 1)
    next.splice(toIndex, 0, moved)
    return { rows: reindex(next) }
  }, { struct: true }, true)

  const addSection = () => {
    const rid = `${PENDING}${pendingSeqRef.current++}`
    apply(c => ({
      rows: reindex([...c.rows, {
        id: rid,
        title: "",
        enabled: true,
        order: c.rows.length,
        format: c.catalog.new_extra_default_format,
        job_agent_editable: true,
        required: false,
        format_locked: false,
        page_break_policy: c.catalog.page_break_policy_default,
      }]),
      bodies: { ...c.bodies, [rid]: "" },
    }), {}, false)
    setSearch("")
    setExpanded(prev => new Set(prev).add(rid))
  }

  const deleteRow = async (row: SectionRow) => {
    const ok = await confirm(`Delete the "${row.title || "untitled"}" section?`, {
      title: "Delete section",
      confirmLabel: "Delete",
      variant: "danger",
    })
    if (!ok) return
    apply(c => {
      const rest = { ...c.bodies }
      delete rest[row.id]
      return { rows: reindex(c.rows.filter(r => r.id !== row.id)), bodies: rest }
    }, { struct: true, body: true }, true)
  }

  const addFromBase = (b: SectionRow, anchor: string | null) => {
    if (!base) return
    const baseBody = base.bodies[b.id] ?? (b.id === "experience" ? [] : "")
    apply(c => {
      const next = c.rows.slice()
      next.splice(anchor ? c.rows.findIndex(r => r.id === anchor) + 1 : 0, 0, { ...b })
      return { rows: reindex(next), bodies: { ...c.bodies, [b.id]: baseBody } }
    }, { struct: true, body: true }, true)
  }

  const pickAccent = (hex: string) => apply(() => ({ accent: hex.toUpperCase() }), { struct: true }, true)

  async function print() {
    setPrinting(true)
    await flush()
    const r = await fetchPrintHtml({ kind: isJob ? "job_resume" : "base", id })
    const err = r.ok ? openHtmlInNewTab(r.html) : r.error
    if (err) setToast({ text: err, variant: "error" })
    setPrinting(false)
  }

  const q = search.trim().toLowerCase()
  const matches = (title: string, body: SectionBody | undefined) =>
    !q || title.toLowerCase().includes(q) || bodyText(body, experienceFields).toLowerCase().includes(q)
  const preview = (body: SectionBody | undefined) => bodyText(body, experienceFields).replace(/\s+/g, " ").trim()

  // Compare to Base (job only): differs / NEW SECTION per job row by id; base-only rows become SECTION REMOVED.
  const showCompare = isJob && compareOn && base !== null
  const baseById = new Map((base?.rows ?? []).map(r => [r.id, r]))
  const compareFor = (row: SectionRow): RowCompare | null => {
    if (!showCompare || row.id.startsWith(PENDING)) return null
    if (!baseById.has(row.id)) return { kind: "new" }
    return bodyKey(bodies[row.id]) === bodyKey(base!.bodies[row.id])
      ? null
      : { kind: "differs", baseText: bodyText(base!.bodies[row.id], experienceFields) }
  }
  // Each removed base row sits after the nearest earlier base row the job still has (null → top).
  const items: Item[] = []
  const removedAfter = new Map<string | null, Item[]>()
  if (showCompare) {
    const jobIds = new Set(rows.map(r => r.id))
    let anchor: string | null = null
    for (const b of base!.rows) {
      if (jobIds.has(b.id)) anchor = b.id
      else removedAfter.set(anchor, [...(removedAfter.get(anchor) ?? []), { kind: "removed", base: b, anchor }])
    }
  }
  items.push(...(removedAfter.get(null) ?? []))
  for (const row of rows) items.push({ kind: "row", row }, ...(removedAfter.get(row.id) ?? []))

  return (
    <div className="resume-editor">
      <div className="resume-editor-header">
        <input
          className="dep-input resume-editor-search"
          type="search"
          placeholder="Search sections"
          aria-label="Search sections"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button type="button" className="btn secondary" onClick={addSection}>Add Section</button>
        {palette.length > 0 && (
          <div className="base-resume-accent-swatches" role="group" aria-label="Resume accent color">
            {palette.map(hex => (
              <button
                key={hex}
                type="button"
                className={`base-resume-accent-swatch${accent === hex.toUpperCase() ? " selected" : ""}`}
                style={{ backgroundColor: hex }}
                title={hex}
                aria-label={hex}
                aria-pressed={accent === hex.toUpperCase()}
                onClick={() => pickAccent(hex)}
              />
            ))}
          </div>
        )}
        {isJob && (
          <button
            type="button"
            className={"btn secondary" + (compareOn ? " active" : "")}
            aria-pressed={compareOn}
            onClick={() => { setCompareOn(on => !on); setBase(null) }}
          >
            Compare to Base
          </button>
        )}
        <button type="button" className="btn secondary" onClick={() => void print()} disabled={printing}>
          {printing ? "Opening…" : "Print"}
        </button>
      </div>
      <div className="resume-editor-rows" onBlur={() => void flush()}>
        {items.map(item => {
          if (item.kind === "removed") {
            const b = item.base
            if (!matches(b.title, base!.bodies[b.id])) return null
            return (
              <div key={`removed:${b.id}`} className="resume-section-removed">
                <span className="resume-section-removed-text">
                  SECTION REMOVED: {b.title}: {preview(base!.bodies[b.id])}
                </span>
                <button type="button" className="btn secondary" onClick={() => addFromBase(b, item.anchor)}>Add</button>
              </div>
            )
          }
          const row = item.row
          if (!matches(row.title, bodies[row.id])) return null
          const index = rows.indexOf(row)
          return (
            <ResumeSectionRow
              key={row.id}
              row={row}
              body={bodies[row.id] ?? (row.id === "experience" ? [] : "")}
              preview={preview(bodies[row.id])}
              catalog={catalog}
              experienceFields={experienceFields}
              unsupportedMessage={unsupportedMessage}
              expanded={expanded.has(row.id)}
              isFirst={index === 0}
              isLast={index === rows.length - 1}
              showJobEdit={!isJob}
              contentLocked={row.id.startsWith(PENDING)}
              compare={compareFor(row)}
              onToggle={() => setExpanded(prev => {
                const next = new Set(prev)
                if (!next.delete(row.id)) next.add(row.id)
                return next
              })}
              onPatch={(patch, save) => patchRow(row.id, patch, save)}
              onBodyChange={b => apply(c => ({ bodies: { ...c.bodies, [row.id]: b } }), { body: true }, false)}
              onMove={delta => moveRow(row.id, index + delta)}
              onDelete={() => void deleteRow(row)}
              onDragStart={() => { dragIdRef.current = row.id }}
              onDrop={() => {
                const fromId = dragIdRef.current
                dragIdRef.current = null
                if (fromId) moveRow(fromId, index)
              }}
            />
          )
        })}
      </div>
      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
```

Behavior notes:

- **Load:** body GET + structure GET in parallel. `loadUiConfig()` supplies the swatch palette (`base_resume_accent_palette`), the experience job fields, and the unsupported-experience message; the current accent comes from the structure GET's `accent_color`. The inner `Editor` is keyed by `${kind}:${id}`, so switching targets remounts and reloads.
- **State and dirty tracking:** one `Loaded` object (`rows`, `bodies`, `accent`, `catalog`) is mirrored into `dataRef` by `apply(updater, dirty, saveNow)`. Separate `structDirty` / `bodyDirty` flags mean only the changed halves are sent.
- **When saves fire** (AC4): typing only updates state. Saves fire on `onBlur` of the rows container (field exit), immediately on any select / checkbox / arrow / drag / add / delete / swatch, on unmount (flush), and `beforeunload` warns while a save is pending or dirty.
- **Save order:** base sends one `/data` PUT with `base_resume` and/or `resume_structure`. Job sends the structure PUT first (only if the structure changed), then the `job_resume` PUT. Each save is chained on the previous one. When a save carried a new (`_pending_N`) row, the structure is refetched and the server ids are adopted by position. `onSaved()` fires once per successful save. A failed save toasts and leaves its halves dirty, so the next field exit retries it.
- **New sections** (AC7): appended expanded with `catalog.new_extra_default_format` and id `_pending_N`. The row isn't sent until it has a title, and its content is locked until the server id is adopted.
- **Search** (AC6): case-insensitive match on title or body text; an empty box shows every row.
- **Delete** (AC10): `useUserConfirm`; cancel keeps the row; confirm removes it from the structure and body and saves.
- **Compare to Base** (AC14, job only): toggling on fetches the candidate base body + base structure (by the job's `candidate_id`). A row present in both with a different `bodyKey` gets a `differs` block; a job row missing from base gets `new`; a base row missing from the job is listed as "SECTION REMOVED: <title>: <preview>" with Add, placed after the nearest earlier base row still present. Add inserts the base row and its base content, then saves structure then body.
- **Print** (AC15): flushes the pending save, then `fetchPrintHtml` + `openHtmlInNewTab`, with the existing error / "Popup blocked" toasts.
- **Unsupported experience:** a non-array `experience` value blocks body saves (with a toast) so the server can't drop it; structure saves still go through.

**Done when:**

- `npx tsc -b --noEmit` is clean; `npx eslint src/components/ResumeContentEditor.tsx src/components/ResumeSectionRow.tsx` has 0 problems; `npx eslint src/components/ExperienceJobsEditor.tsx` shows only the L65 baseline error.
- `npm run build` succeeds.
- `git grep -nE "Word Cloud|Bullet List|Flow uninterrupted" -- src/ui/frontend/src` returns nothing (AC13); neither new file contains `Save sections` / `Save` / `Cancel` buttons (AC5).
- Commit: `feat(AST-2083): ResumeContentEditor`.

Pre-plan verification: all three stages were built in a scratch tree at `708488377`. Typecheck, lint, and `npm run build` passed, and a throwaway vitest smoke suite (outside `tests/`, not committed) covered: typing fires no request; blur → one PUT + one `onSaved`; a base body-only save excludes `resume_structure`; flow change and Hidden; search; Add Section adopting the server slug id; delete cancel/confirm; Compare counts (1 differs / 1 NEW / 1 REMOVED); Add → structure PUT then `job_resume` PUT with base content; a job body-only edit sends only `job_resume`; the `line` input; arrow and drag reorder.

## ⚠️ Decisions

1. **Target-keyed remount.** `ResumeContentEditor` wraps an inner `Editor` with `key={`${kind}:${id}`}` instead of resetting state in an effect (react-hooks v7 `set-state-in-effect`).
2. **Field exit = focus leaving the rows container.** One `onBlur` on `.resume-editor-rows` covers every text field, including `ExperienceJobsEditor`'s inner inputs, without threading a blur prop through it. Moving focus between two fields also counts as an exit and saves (AC4 needs one save per exit, not per keystroke).
3. **Discrete controls save immediately:** selects, checkboxes, arrows, drag, add, delete, swatches.
4. **Only changed halves are sent; job structure is PUT only when it changed.** This keeps an inherited job structure inherited, and AC14's Add still persists both halves (structure first, so the job prep filter keeps the new section's body).
5. **Saves are serialized** (promise chain). A save that carried a new row is followed by a structure refetch to adopt the server-slugged ids by position.
6. **New rows stay unsent until titled**, because the server rejects an empty title. Their content is locked until the real id lands, so no body is ever written under a placeholder key.
7. **Delete uses the app's `useUserConfirm`** dialog, not `window.confirm`.
8. **Drag reorder is native HTML5 drag-and-drop** (no new dependency). Arrows remain the keyboard path.
9. **Tooltips are native `title` attributes** (plus `aria-label` on the flow glyph). No tooltip component.
10. **The flow → glyph map is the only client-side constant** (⊘ hidden, ⤒ page break before, ▣ avoid split, ≈ normal). It's presentational; all text comes from the catalog (AC13).
11. **Format select lists every `catalog.body_formats` entry** on every non-contact row, matching today's structure authoring. Contact rows show no format control, label, or font.
12. **Flag for Susan — Hidden drops content.** Because the backend keeps only enabled sections' bodies on save (Ground truth), hiding a section and then editing any other body erases the hidden section's text; un-hiding shows it empty. This is existing #1-era server behavior, and changing it is backend scope, not this ticket's. Raising it in case it should become a follow-up.
13. **Flag — unsupported (non-array) experience blocks body saves** with a toast, so the server can't silently drop it. #4 removes `ArtifactEditor`'s "Generate" escape, so after #4 there is no in-editor recovery for such a record (it would need a regenerate elsewhere).
14. **Retired CSS is removed here** (it's in this ticket's Scope). Until #4 deletes `ArtifactEditor`'s resume mode, that interim header renders unstyled (wraps instead of one row). This is cosmetic only, and no test asserts layout.
15. **Compare equality** uses a normalized body key (trimmed text; experience serialized); whitespace-only differences count as equal.
16. **Removed-row placement:** after the nearest earlier base row that's still present in the job (or at the top when there's none).
17. **All rows start collapsed;** several rows may be expanded at once. A new row opens expanded.
18. **Search may hide the row being edited** if the edit stops matching. Plain filter, no pinning.
19. **`.print-preview-thumb`** gets a border and a white background (the print page is white), plus a gold hover border, for #4's thumbnails.
20. **No limits, debounce timers, or truncation** beyond CSS ellipsis on the one-line collapsed preview (AC8 requires one line).

## Integration notes (for #4 — no work here)

- Mount `<ResumeContentEditor target={{ kind: "base", id: candidateId }} onSaved={() => setRefreshKey(k => k + 1)} />` on the left of `SplitPanePage`, with `PrintPreview` (same target, `refreshKey`) on the right. Use `{ kind: "job", id: jobId }` in the job edit modal.
- `ResumeContentEditor` fills its panel (`.resume-editor` is a column with `min-height: 100%`; the header is sticky inside the panel's scroller).
- `.print-preview-thumb` styles are ready for the Artifacts-tab thumbnails.

## Parent AC coverage (child numbering)

| Child AC | Covered by |
|----------|-----------|
| 4 Refresh on field exit | Stage 3 save triggers + `onSaved` (refresh wired in #4) |
| 5 No Save buttons | Stages 2–3 (no buttons); grep clean once #4 removes `ArtifactEditor` L1395 |
| 6 Search | Stage 3 |
| 7 Add Section | Stage 3 add + id adoption |
| 8 Collapsed row | Stage 2 collapsed header |
| 9 Flow type | Stage 2 flow select + Stage 3 `patchRow` |
| 10 Delete confirms | Stage 3 `deleteRow` + Stage 2 required gate |
| 11 Reorder | Stage 2 drag + arrows, Stage 3 `moveRow` |
| 12 Line format | Stage 2 `line` input |
| 13 Config-driven text | Stages 2–3 (catalog only) |
| 14 Compare to Base | Stage 3 compare + Stage 2 blocks |
| 15 Print | Stage 3 `print` |
| 16 Experience header color | Stage 1 |

## Estimate

Confirm Chuckles estimate: 5 — agree.
