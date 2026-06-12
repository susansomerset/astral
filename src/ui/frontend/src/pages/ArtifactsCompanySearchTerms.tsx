import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import LabeledTextArea from "../components/LabeledTextArea"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"

const AUTOSAVE_MS = 2000
const TASK_KEY = "craft_company_search_terms"

export default function CompanySearchTerms() {
  const { manifest, loadState } = useStateUi()
  const { selectedId, candidates } = useCandidate()
  const [text, setText] = useState("")
  const [loaded, setLoaded] = useState(false)
  const [dirty, setDirty] = useState(false)
  const [everSaved, setEverSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const textRef = useRef(text)
  const dirtyRef = useRef(dirty)
  textRef.current = text
  dirtyRef.current = dirty

  const [snapshot, setSnapshot] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [confirmRegen, setConfirmRegen] = useState(false)

  const inReview = snapshot !== null

  const candidateState = useMemo(() => {
    const c = candidates.find(c => c.astral_candidate_id === selectedId)
    return c?.state ?? ""
  }, [candidates, selectedId])
  const generateStates = useMemo(
    () => new Set(manifest?.candidate.artifact_generate_states ?? []),
    [manifest?.candidate.artifact_generate_states],
  )
  const canGenerate = generateStates.has(candidateState)
  const hasData = text.trim() !== ""

  useEffect(() => {
    if (!selectedId) return
    setLoaded(false)
    setSnapshot(null)
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      const raw = c.company_search_terms
      setText(typeof raw === "string" ? raw : "")
      setLoaded(true)
      setDirty(false)
      setEverSaved(typeof raw === "string" && raw.trim() !== "")
    })
  }, [selectedId])

  const doSave = useCallback(async (value: string) => {
    if (!selectedId) return
    setSaving(true)
    try {
      const resp = await api(`/api/candidates/${selectedId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artifacts: { company_search_terms: value } }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
        throw new Error(err.error || `Save failed (${resp.status})`)
      }
      setDirty(false)
      setEverSaved(true)
      setSnapshot(null)
      setToast({ text: "Saved", variant: "success" })
    } catch (e) {
      setToast({ text: (e as Error).message || "Save failed", variant: "error" })
    } finally {
      setSaving(false)
    }
  }, [selectedId])

  function handleChange(next: string) {
    setText(next)
    setDirty(true)
    if (!inReview) {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => doSave(next), AUTOSAVE_MS)
    }
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      if (dirtyRef.current) doSave(textRef.current)
    }
  }, [doSave])

  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (dirtyRef.current) { e.preventDefault(); e.returnValue = "" }
    }
    window.addEventListener("beforeunload", handler)
    return () => window.removeEventListener("beforeunload", handler)
  }, [])

  function handleGenerateClick() {
    if (hasData) {
      setConfirmRegen(true)
      return
    }
    doGenerate()
  }

  async function doGenerate() {
    if (!selectedId) return
    setConfirmRegen(false)
    setGenerating(true)
    setSnapshot(text)

    try {
      const resp = await api(`/api/candidates/${selectedId}/generate/${TASK_KEY}`, { method: "POST" })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
        throw new Error(err.error || "Generation failed")
      }
      const data = await resp.json()
      if (!data.success) throw new Error(data.error || "Generation failed")

      const parsed = data.parsed_response
      if (!parsed) throw new Error("No content returned")

      const terms = parsed.search_terms
      setText(
        typeof terms === "string"
          ? terms
          : Array.isArray(terms)
            ? terms.map((t) => String(t).trim()).filter(Boolean).join("\n")
            : String(terms ?? "")
      )
      setDirty(true)
      setToast({ text: "Generated — review and Save or Cancel", variant: "success" })
    } catch (e) {
      setSnapshot(null)
      setToast({ text: (e as Error).message, variant: "error" })
    } finally {
      setGenerating(false)
    }
  }

  function handleCancel() {
    if (snapshot !== null) {
      setText(snapshot)
      setSnapshot(null)
      setDirty(false)
    } else {
      window.location.reload()
    }
  }

  if (!selectedId) return <p style={{ padding: 20, color: "#fff" }}>No candidate selected.</p>
  if (loadState === "loading") return <p className="list-page-status">Loading...</p>
  if (loadState === "error" || !manifest) return <p className="list-page-status">State UI manifest unavailable.</p>
  if (!loaded) return <p style={{ padding: 20, color: "#fff" }}>Loading...</p>

  return (
    <>
      <div className="dep-page">
        <div className="dep-header">
          <h1 className="dep-title">Company Search Terms</h1>
          <div className="dep-actions">
            {canGenerate && (
              <button
                className="dep-btn save"
                onClick={handleGenerateClick}
                disabled={generating}
                style={{ marginRight: 8 }}
              >
                {generating ? "Generating..." : hasData ? "Regenerate" : "Generate"}
              </button>
            )}
            {inReview ? (
              <>
                <button className="dep-btn cancel" onClick={handleCancel}>Cancel</button>
                <button className="dep-btn save" onClick={() => doSave(text)} disabled={saving}>
                  {saving ? "Saving..." : "Save"}
                </button>
              </>
            ) : (
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                {saving ? "Saving..." : dirty ? "Unsaved changes" : everSaved ? "All changes saved" : ""}
              </span>
            )}
          </div>
        </div>
        <div className="dep-body">
          <LabeledTextArea
            label="Search terms (one per line)"
            value={text}
            onChange={handleChange}
            hideTitle
          />
        </div>
      </div>

      {confirmRegen && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 1000,
          display: "flex", alignItems: "center", justifyContent: "center",
          background: "rgba(0,0,0,0.6)",
        }}>
          <div style={{
            background: "var(--bg-elevated)", border: "2px solid #ff6b6b",
            borderRadius: 8, padding: 24, maxWidth: 460, width: "90%",
          }}>
            <h3 style={{ margin: "0 0 12px", color: "#ff6b6b", fontSize: 16 }}>Regenerate Company Search Terms?</h3>
            <p style={{ margin: "0 0 16px", color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.5 }}>
              This will replace the current content with a new AI-generated version.
              You can review the result and <strong>Cancel</strong> to restore your previous version,
              or <strong>Save</strong> to keep it. Saving cannot be undone.
            </p>
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button className="dep-btn cancel" onClick={() => setConfirmRegen(false)}>
                Cancel
              </button>
              <button className="dep-btn save" onClick={doGenerate} style={{ background: "#ff6b6b" }}>
                Regenerate
              </button>
            </div>
          </div>
        </div>
      )}

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
