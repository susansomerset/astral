import { useCallback, useEffect, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import Toast, { type ToastMessage } from "./Toast"

interface ContextTextPageProps {
  title: string
  contextKey: string
  /** Catalog body_shape (ARTIFACT_CONFIG / BUILD_CONFIG artifact_shapes). Strengths: plain_text. Omit for legacy blob context pages. AST-1634 / patt.artifact.ui-consistency */
  bodyShape?: string
}

// Gracefully handle pre-migration data: arrays of objects → readable text
function coerceToString(val: unknown): string {
  if (typeof val === "string") return val
  if (!Array.isArray(val)) return val ? String(val) : ""
  return val.map(item => {
    if (typeof item === "string") return item
    if (typeof item !== "object" || !item) return String(item)
    const o = item as Record<string, unknown>
    if ("title" in o || "organization" in o) {
      const parts = [o.title, o.organization].filter(Boolean).join(" — ")
      return [parts, o.job_reality, o.left_because].filter(Boolean).join("\n")
    }
    const label = o.label ?? ""
    const desc = o.description ?? ""
    return label ? `${label}: ${desc}` : String(desc)
  }).join("\n\n")
}

export default function ContextTextPage({ title, contextKey, bodyShape }: ContextTextPageProps) {
  const { selectedId } = useCandidate()
  const [saved, setSaved] = useState("")
  const [draft, setDraft] = useState("")
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  // plain_text (Strengths): refuse empty save — matches operative validation (AST-1634)
  const plainTextEmpty = bodyShape === "plain_text" && !draft.trim()

  useEffect(() => {
    if (!selectedId) return
    setLoading(true)
    api(`/api/candidates/${selectedId}`)
      .then(r => r.json())
      .then(c => {
        const val = coerceToString(c.candidate_data?.context?.[contextKey])
        setSaved(val)
        setDraft(val)
      })
      .finally(() => setLoading(false))
  }, [selectedId, contextKey])

  function handleSave() {
    /* v8 ignore next -- @preserve */
    if (!selectedId) return
    if (bodyShape === "plain_text" && !draft.trim()) {
      setToast({ text: `${title} cannot be empty`, variant: "error" })
      return
    }
    api(`/api/candidates/${selectedId}/data`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ context: { [contextKey]: draft } }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Save failed") })
        return r.json()
      })
      .then(c => {
        const val = coerceToString(c.candidate_data?.context?.[contextKey]) || draft
        setSaved(val)
        setDraft(val)
        setToast({ text: `${title} saved`, variant: "success" })
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function handleCancel() {
    setDraft(saved)
  }

  if (loading) return <p style={{ padding: 20, color: "#fff" }}>Loading...</p>
  if (!selectedId) return <p style={{ padding: 20, color: "#fff" }}>No candidate selected.</p>

  return (
    <>
      <div className="dep-page">
        <div className="dep-header">
          <h1 className="dep-title">{title}</h1>
          <div className="dep-actions">
            <button className="btn secondary" onClick={handleCancel}>Cancel</button>
            <button className="btn primary" onClick={handleSave} disabled={plainTextEmpty}>Save</button>
          </div>
        </div>
        <div className="dep-body">
          <div className="dep-section">
            <textarea
              className="dep-input dep-textarea"
              style={{ width: "100%", minHeight: 400 }}
              value={draft}
              onChange={e => setDraft(e.target.value)}
            />
          </div>
        </div>
      </div>
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
