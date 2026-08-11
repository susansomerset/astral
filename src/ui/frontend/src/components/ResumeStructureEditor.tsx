import { useEffect, useState } from "react"

export type Catalog = {
  body_formats: string[]
  required_ids: string[]
  contact_ids: string[]
  extra_id_pattern: string
  reserved_extra_ids: string[]
  new_extra_default_format: string
}

export type SectionRow = {
  id: string
  title: string
  enabled: boolean
  order: number
  format: string | null
  job_agent_editable: boolean
  required: boolean
  format_locked: boolean
}

type Props = {
  sections: SectionRow[]
  catalog: Catalog
  disabled: boolean
  onSave: (sections: SectionRow[]) => void
  saving: boolean
  error: string | null
}

export default function ResumeStructureEditor(props: Props) {
  const { sections, catalog, disabled, onSave, saving, error } = props
  const [rows, setRows] = useState<SectionRow[]>(sections)
  const [addTitle, setAddTitle] = useState("")
  const [addFormat, setAddFormat] = useState(
    catalog.new_extra_default_format || catalog.body_formats[0] || "",
  )

  useEffect(() => {
    setRows(sections)
  }, [sections])

  function patchRow(index: number, patch: Partial<SectionRow>) {
    setRows(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)))
  }

  function reindex(next: SectionRow[]) {
    return next.map((row, i) => ({ ...row, order: i }))
  }

  function moveRow(index: number, delta: number) {
    const j = index + delta
    if (j < 0 || j >= rows.length) return
    const next = rows.slice()
    const tmp = next[index]
    next[index] = next[j]
    next[j] = tmp
    setRows(reindex(next))
  }

  function addSection() {
    const title = addTitle.trim()
    if (!title) return
    setRows(reindex([
      ...rows,
      {
        id: `_pending_${rows.length}`,
        title,
        enabled: true,
        order: rows.length,
        format: addFormat,
        job_agent_editable: true,
        required: false,
        format_locked: false,
      },
    ]))
    setAddTitle("")
  }

  return (
    <div className="base-resume-structure-editor">
      <span className="base-resume-structure-editor-title">Resume sections</span>
      {rows.map((row, index) => {
        const formatValue = row.format_locked
          ? (row.format ?? "")
          : (row.format && catalog.body_formats.includes(row.format)
            ? row.format
            : catalog.new_extra_default_format)
        return (
          <div className="base-resume-structure-row" key={row.id || `row-${index}`}>
            <span className="base-resume-structure-row-id">
              {row.id.startsWith("_pending_") ? "" : row.id}
            </span>
            <input
              className="dep-input"
              type="text"
              value={row.title}
              disabled={disabled}
              onChange={e => patchRow(index, { title: e.target.value })}
            />
            <select
              className="dep-input"
              value={formatValue}
              disabled={disabled || row.format_locked}
              onChange={e => patchRow(index, { format: e.target.value })}
            >
              {catalog.body_formats.map(f => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
            <label>
              <input
                type="checkbox"
                checked={row.enabled}
                disabled={disabled || row.required}
                onChange={e => patchRow(index, { enabled: e.target.checked })}
              />
              {" "}Enabled
            </label>
            <label>
              <input
                type="checkbox"
                checked={row.job_agent_editable}
                disabled={disabled}
                onChange={e => patchRow(index, { job_agent_editable: e.target.checked })}
              />
              {" "}Job agent editable
            </label>
            <button type="button" disabled={disabled || index === 0} onClick={() => moveRow(index, -1)}>
              Up
            </button>
            <button type="button" disabled={disabled || index === rows.length - 1} onClick={() => moveRow(index, 1)}>
              Down
            </button>
            {!row.required && (
              <button
                type="button"
                disabled={disabled}
                onClick={() => setRows(reindex(rows.filter((_, i) => i !== index)))}
              >
                Remove
              </button>
            )}
          </div>
        )
      })}
      <div className="base-resume-structure-add">
        <input
          className="dep-input"
          type="text"
          value={addTitle}
          disabled={disabled}
          onChange={e => setAddTitle(e.target.value)}
        />
        <select
          className="dep-input"
          value={addFormat}
          disabled={disabled}
          onChange={e => setAddFormat(e.target.value)}
        >
          {catalog.body_formats.map(f => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <button type="button" disabled={disabled} onClick={addSection}>Add section</button>
      </div>
      <button
        type="button"
        className="base-resume-structure-save"
        disabled={disabled || saving}
        onClick={() => onSave(rows)}
      >
        Save sections
      </button>
      {error ? <div>{error}</div> : null}
    </div>
  )
}
