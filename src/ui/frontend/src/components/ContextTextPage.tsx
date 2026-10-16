import { useCallback, useEffect, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import ArtifactVersionNav, { versionNavState, type VersionMap } from "./ArtifactVersionNav"
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
  const [versions, setVersions] = useState<VersionMap | null>(null)
  const [moving, setMoving] = useState(false)
  // AST-2067 version routes take the full catalog key.
  const versionsBase = selectedId
    ? `/api/candidates/${selectedId}/artifacts/${encodeURIComponent(`candidate.context.${contextKey}`)}`
    : null

  /** Current-read GET (patt.artifact.read-current) — initial load and after a move. */
  const loadBody = useCallback(async () => {
    if (!selectedId) return
    const c = await api(`/api/candidates/${selectedId}`).then(r => r.json())
    const val = coerceToString(c.candidate_data?.context?.[contextKey])
    setSaved(val)
    setDraft(val)
  }, [selectedId, contextKey])

  /** Version map; non-OK / network error → no arrows, editing unaffected. */
  const refreshVersions = useCallback(async () => {
    if (!versionsBase) return
    try {
      const r = await api(`${versionsBase}/versions`)
      setVersions(r.ok ? ((await r.json()).versions as VersionMap) : null)
    } catch {
      setVersions(null)
    }
  }, [versionsBase])

  useEffect(() => {
    if (!selectedId) return
    setLoading(true)
    setVersions(null)
    void refreshVersions()
    loadBody().finally(() => setLoading(false))
  }, [selectedId, loadBody, refreshVersions])

  async function handleSave(): Promise<boolean> {
    /* v8 ignore next -- @preserve */
    if (!selectedId) return false
    if (bodyShape === "plain_text" && !draft.trim()) {
      setToast({ text: `${title} cannot be empty`, variant: "error" })
      return false
    }
    try {
      const r = await api(`/api/candidates/${selectedId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context: { [contextKey]: draft } }),
      })
      if (!r.ok) {
        const e = await r.json()
        throw new Error(e.error || "Save failed")
      }
      const c = await r.json()
      const val = coerceToString(c.candidate_data?.context?.[contextKey]) || draft
      setSaved(val)
      setDraft(val)
      setToast({ text: `${title} saved`, variant: "success" })
      // Awaited: a save-before-move must refresh before the move's PUT (no late stale map).
      await refreshVersions()
      return true
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
      return false
    }
  }

  /** Arrow move (AST-2068): save an unsaved draft as one version first, move current, reload via current-read GET. */
  async function handleMove(dir: -1 | 1) {
    if (!versionsBase) return
    setMoving(true)
    try {
      if (draft !== saved && !(await handleSave())) return
      // Step from current *after* any save: back after an edit lands on the version that was on screen.
      const vr = await api(`${versionsBase}/versions`)
      if (!vr.ok) throw new Error(`Versions failed (${vr.status})`)
      const step = versionNavState((await vr.json()).versions as VersionMap)
      const uuid = dir < 0 ? step.backUuid : step.forwardUuid
      if (!uuid) return
      const r = await api(`${versionsBase}/current`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artifact_uuid: uuid }),
      })
      if (!r.ok) {
        const e = await r.json().catch(() => ({ error: `HTTP ${r.status}` }))
        throw new Error(e.error || `Move failed (${r.status})`)
      }
      setVersions((await r.json()).versions as VersionMap)
      await loadBody()
    } catch (e) {
      setToast({ text: (e as Error).message || "Move failed", variant: "error" })
    } finally {
      setMoving(false)
    }
  }

  function handleCancel() {
    setDraft(saved)
  }

  if (loading) return <p style={{ padding: 20, color: "var(--text-primary)" }}>Loading...</p>
  if (!selectedId) return <p style={{ padding: 20, color: "var(--text-primary)" }}>No candidate selected.</p>

  const nav = versions ? versionNavState(versions) : null

  return (
    <>
      <div className="dep-page">
        <div className="dep-header">
          <h1 className="dep-title">{title}</h1>
          <div className="dep-actions">
            {nav && (
              <ArtifactVersionNav
                position={nav.position}
                total={nav.total}
                disabled={moving}
                onBack={() => void handleMove(-1)}
                onForward={() => void handleMove(1)}
              />
            )}
            <button className="btn secondary" onClick={handleCancel}>Cancel</button>
            <button className="btn primary" onClick={() => void handleSave()} disabled={plainTextEmpty}>Save</button>
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
