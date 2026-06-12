import { useState } from "react"
import FormFields, { setByPath } from "./FormFields"
import type { Section } from "./FormFields"

export type { Field, Section } from "./FormFields"

export interface DetailsEditPageProps {
  title: string
  sections: Section[]
  data: Record<string, unknown>
  onSave?: (updated: Record<string, unknown>) => void
  onCancel?: () => void
}

export default function DetailsEditPage({
  title,
  sections,
  data,
  onSave,
  onCancel,
}: DetailsEditPageProps) {
  const [values, setValues] = useState<Record<string, unknown>>({ ...data })

  function set(key: string, value: unknown) {
    setValues(prev => setByPath(prev, key, value))
  }

  function handleSave() {
    onSave?.(values)
  }

  function handleCancel() {
    setValues({ ...data })
    onCancel?.()
  }

  return (
    <div className="dep-page">
      <div className="dep-header">
        <h1 className="dep-title">{title}</h1>
        <div className="dep-actions">
          <button className="dep-btn cancel" onClick={handleCancel}>Cancel</button>
          <button className="dep-btn save" onClick={handleSave}>Save</button>
        </div>
      </div>
      <div className="dep-body">
        {sections.map(section => (
          <div key={section.label} className="dep-section">
            <h2 className="dep-section-label">{section.label}</h2>
            <FormFields fields={section.fields} values={values} onChange={set} />
          </div>
        ))}
      </div>
    </div>
  )
}
