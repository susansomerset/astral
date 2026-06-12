export interface Field {
  key: string
  label: string
  type: "text" | "textarea" | "select" | "toggle"
  options?: (string | { value: string; label: string })[]
}

export interface Section {
  label: string
  fields: Field[]
}

interface FormFieldsProps {
  fields: Field[]
  values: Record<string, unknown>
  onChange: (key: string, value: unknown) => void
}

// Dot-path utilities for nested data (e.g. "profile.first" -> obj.profile.first)
export function getByPath(obj: Record<string, unknown>, path: string): unknown {
  const parts = path.split(".")
  let cur: unknown = obj
  for (const p of parts) {
    if (cur == null || typeof cur !== "object") return undefined
    cur = (cur as Record<string, unknown>)[p]
  }
  return cur
}

export function setByPath(obj: Record<string, unknown>, path: string, value: unknown): Record<string, unknown> {
  const parts = path.split(".")
  const root = structuredClone(obj)
  let cur: Record<string, unknown> = root
  for (let i = 0; i < parts.length - 1; i++) {
    if (cur[parts[i]] == null || typeof cur[parts[i]] !== "object") cur[parts[i]] = {}
    cur = cur[parts[i]] as Record<string, unknown>
  }
  cur[parts[parts.length - 1]] = value
  return root
}

export default function FormFields({ fields, values, onChange }: FormFieldsProps) {
  return (
    <>
      {fields.map(field => (
        <div key={field.key} className="dep-field">
          <label className="dep-field-label">{field.label}</label>
          {renderInput(field, getByPath(values, field.key), v => onChange(field.key, v))}
        </div>
      ))}
    </>
  )
}

function renderInput(
  field: Field,
  value: unknown,
  onChange: (v: unknown) => void,
) {
  switch (field.type) {
    case "textarea":
      return (
        <textarea
          className="dep-input dep-textarea"
          value={String(value ?? "")}
          onChange={e => onChange(e.target.value)}
        />
      )

    case "select":
      return (
        <select
          className="dep-input dep-select"
          value={String(value ?? "")}
          onChange={e => onChange(e.target.value)}
        >
          {field.options?.map(opt => {
            const v = typeof opt === "string" ? opt : opt.value
            const lbl = typeof opt === "string" ? opt : opt.label
            return <option key={v} value={v}>{lbl}</option>
          })}
        </select>
      )

    case "toggle":
      return (
        <label className="dep-toggle">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={e => onChange(e.target.checked)}
          />
          <span className="dep-toggle-label">
            {value ? "Enabled" : "Disabled"}
          </span>
        </label>
      )

    default:
      return (
        <input
          className="dep-input"
          type="text"
          value={String(value ?? "")}
          onChange={e => onChange(e.target.value)}
        />
      )
  }
}
