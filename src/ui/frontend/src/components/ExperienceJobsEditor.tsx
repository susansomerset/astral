/** AST-1351 / AST-1381: per-role experience job-array editor (keys from ui_config). */

import { useEffect, useRef, useState } from "react"
import CollapsiblePanel from "./CollapsiblePanel"

export interface ExperienceJobField {
  key: string
  label: string
}

/** Job wire shape: string fields + accomplishments as string[]. */
export type ExperienceJob = Record<string, string | string[]>

interface ExperienceJobsEditorProps {
  fields: ExperienceJobField[]
  value: ExperienceJob[]
  onChange: (next: ExperienceJob[]) => void
  disabled?: boolean
}

function emptyJob(fields: ExperienceJobField[]): ExperienceJob {
  return Object.fromEntries(
    fields.map(f => [f.key, f.key === "accomplishments" ? [] : ""]),
  )
}

function roleCollapsedLabel(job: ExperienceJob): string {
  const company = String(job.company ?? "").trim()
  const title = String(job.title ?? "").trim()
  const dates = String(job.dates ?? "").trim()
  const left = [company, title].filter(Boolean).join(", ")
  if (left && dates) return `${left} / ${dates}`
  return left || dates || "Role"
}

function accomplishmentsText(job: ExperienceJob): string {
  const raw = job.accomplishments
  if (Array.isArray(raw)) return raw.map(String).join("\n")
  if (typeof raw === "string") return raw
  return ""
}

function parseAccomplishmentsInput(text: string): string[] {
  return text
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map(s => s.trim())
    .filter(Boolean)
}

/** Local text while focused so Enter/newlines are not eaten by array round-trip. */
function AccomplishmentsTextarea({
  job,
  disabled,
  onCommit,
}: {
  job: ExperienceJob
  disabled?: boolean
  onCommit: (next: string[]) => void
}) {
  const fromJob = accomplishmentsText(job)
  const [text, setText] = useState(fromJob)
  const focusedRef = useRef(false)
  useEffect(() => {
    if (!focusedRef.current) setText(fromJob)
  }, [fromJob])
  return (
    <textarea
      className="dep-input"
      rows={5}
      value={text}
      disabled={disabled}
      onFocus={() => {
        focusedRef.current = true
      }}
      onChange={e => {
        const v = e.target.value
        setText(v)
        onCommit(parseAccomplishmentsInput(v))
      }}
      onBlur={() => {
        focusedRef.current = false
        const next = parseAccomplishmentsInput(text)
        onCommit(next)
        setText(next.join("\n"))
      }}
    />
  )
}

export default function ExperienceJobsEditor({
  fields,
  value,
  onChange,
  disabled = false,
}: ExperienceJobsEditorProps) {
  function patchJob(index: number, key: string, nextVal: string | string[]) {
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
        <CollapsiblePanel
          key={index}
          label={<span className="experience-jobs-editor-role-label">{roleCollapsedLabel(job)}</span>}
          defaultExpanded={false}
          actions={
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
          }
        >
          <div className="experience-jobs-editor-role-body">
            {fields.map(field => (
              <div key={field.key} className="dep-field">
                <label className="dep-field-label">{field.label}</label>
                {field.key === "accomplishments" ? (
                  <AccomplishmentsTextarea
                    job={job}
                    disabled={disabled}
                    onCommit={next => patchJob(index, field.key, next)}
                  />
                ) : (
                  <input
                    className="dep-input"
                    type="text"
                    value={String(job[field.key] ?? "")}
                    disabled={disabled}
                    onChange={e => patchJob(index, field.key, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>
        </CollapsiblePanel>
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
