/** AST-1351: per-role experience job-array editor (keys from ui_config). */

export interface ExperienceJobField {
  key: string
  label: string
}

interface ExperienceJobsEditorProps {
  fields: ExperienceJobField[]
  value: Record<string, string>[]
  onChange: (next: Record<string, string>[]) => void
  disabled?: boolean
}

function emptyJob(fields: ExperienceJobField[]): Record<string, string> {
  return Object.fromEntries(fields.map(f => [f.key, ""]))
}

export default function ExperienceJobsEditor({
  fields,
  value,
  onChange,
  disabled = false,
}: ExperienceJobsEditorProps) {
  function patchJob(index: number, key: string, nextVal: string) {
    const next = value.map((job, i) => (i === index ? { ...job, [key]: nextVal } : job))
    onChange(next)
  }

  function moveJob(index: number, delta: number) {
    const j = index + delta
    if (j < 0 || j >= value.length) return
    const next = value.slice()
    const tmp = next[index]
    next[index] = next[j]
    next[j] = tmp
    onChange(next)
  }

  function removeJob(index: number) {
    onChange(value.filter((_, i) => i !== index))
  }

  function addJob() {
    onChange([...value, emptyJob(fields)])
  }

  return (
    <div className="experience-jobs-editor">
      {value.map((job, index) => (
        <div key={index} className="experience-jobs-editor-role">
          <div className="experience-jobs-editor-role-header">
            <span className="experience-jobs-editor-role-label">Role {index + 1}</span>
            <span className="side-tab-controls">
              <button
                type="button"
                disabled={disabled || index === 0}
                onClick={() => moveJob(index, -1)}
                title="Move up"
              >
                ▲
              </button>
              <button
                type="button"
                disabled={disabled || index === value.length - 1}
                onClick={() => moveJob(index, 1)}
                title="Move down"
              >
                ▼
              </button>
              <button
                type="button"
                disabled={disabled}
                onClick={() => removeJob(index)}
                title="Remove"
              >
                ×
              </button>
            </span>
          </div>
          {fields.map(field => (
            <div key={field.key} className="dep-field">
              <label className="dep-field-label">{field.label}</label>
              {field.key === "accomplishments" ? (
                <textarea
                  className="dep-input"
                  rows={5}
                  value={job[field.key] ?? ""}
                  disabled={disabled}
                  onChange={e => patchJob(index, field.key, e.target.value)}
                />
              ) : (
                <input
                  className="dep-input"
                  type="text"
                  value={job[field.key] ?? ""}
                  disabled={disabled}
                  onChange={e => patchJob(index, field.key, e.target.value)}
                />
              )}
            </div>
          ))}
        </div>
      ))}
      <button
        type="button"
        className="btn secondary experience-jobs-editor-add"
        disabled={disabled}
        onClick={addJob}
      >
        Add role
      </button>
    </div>
  )
}
