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
