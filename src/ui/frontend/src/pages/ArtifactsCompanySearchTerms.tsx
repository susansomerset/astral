import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import LabeledTextArea from "../components/LabeledTextArea"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import { artifactBlobHasContent } from "../lib/artifactBlobHasContent"

const AUTOSAVE_MS = 2000
const TASK_KEY = "craft_company_search_terms"

export default function CompanySearchTerms() {
  const { manifest, loadState } = useStateUi()
  const { selectedId, candidates, refresh: refreshCandidate } = useCandidate()
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
  const [hasChainData, setHasChainData] = useState(false)

  const inReview = snapshot !== null

  const candidateState = useMemo(() => {
    const c = candidates.find(c => c.astral_candidate_id === selectedId)
    return c?.state ?? ""
  }, [candidates, selectedId])
  const generateStates = useMemo(
    () => new Set(manifest?.candidate.artifact_generate_states ?? []),
    [manifest?.candidate.artifact_generate_states],
  )
  const chainTaskKeys = useMemo(
    () => new Set(manifest?.candidate.artifacts_chain_task_keys ?? []),
    [manifest?.candidate.artifacts_chain_task_keys],
  )
  const chainHopLabels = manifest?.candidate.artifacts_chain_hop_labels ?? []
  const chainArtifactKeys = useMemo(
    () => manifest?.candidate.artifacts_chain_artifact_keys ?? [],
    [manifest?.candidate.artifacts_chain_artifact_keys],
  )
  const isChainHandoff = chainTaskKeys.has(TASK_KEY)
  const canGenerate = generateStates.has(candidateState)

  useEffect(() => {
    if (!selectedId) return
    setLoaded(false)
    setSnapshot(null)
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      const raw = c.company_search_terms
      setText(typeof raw === "string" ? raw : "")
      const artifacts = (c.candidate_data?.artifacts ?? {}) as Record<string, unknown>
      const rubricHit = chainArtifactKeys.some(k => artifactBlobHasContent(artifacts[k]))
      const termsHit = typeof raw === "string" && raw.trim() !== ""
      setHasChainData(rubricHit || termsHit)
      setLoaded(true)
      setDirty(false)
      setEverSaved(typeof raw === "string" && raw.trim() !== "")
    })
  }, [selectedId, chainArtifactKeys])

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
    if (isChainHandoff) {
      if (hasChainData) {
        setConfirmRegen(true)
        return
      }
      void doRequestArtifacts()
      return
    }
    // Non-chain fallback (should not happen for this page once manifest is live)
    if (text.trim() !== "") {
      setConfirmRegen(true)
      return
    }
    void doRequestArtifacts()
  }

  async function doRequestArtifacts() {
    if (!selectedId) return
    setConfirmRegen(false)
    setGenerating(true)
    try {
      const resp = await api(`/api/candidates/${selectedId}/generate_artifacts`, { method: "POST" })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
        throw new Error(err.error || "Request failed")
      }
      const data = await resp.json()
      if (!data.ok) throw new Error(data.error || "Request failed")
      setToast({ text: "Artifacts build requested — watch Execution History", variant: "success" })
      refreshCandidate()
    } catch (e) {
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
                className={`dep-btn save${generating ? " in-flight" : ""}`}
                onClick={handleGenerateClick}
                disabled={generating}
                style={{ marginRight: 8 }}
              >
                {generating ? "Requesting..." : hasChainData ? "Regenerate" : "Generate"}
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
            <h3 style={{ margin: "0 0 12px", color: "#ff6b6b", fontSize: 16 }}>
              Reset all artifact rubrics?
            </h3>
            <p style={{ margin: "0 0 16px", color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.5 }}>
              This rebuilds the full craft chain and resets all of these rubrics:{" "}
              <strong>{chainHopLabels.join(", ") || "all chain hops"}</strong>.
              History is kept, but regeneration is expensive. Default is No.
            </p>
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button
                className="dep-btn cancel"
                autoFocus
                onClick={() => setConfirmRegen(false)}
              >
                No
              </button>
              <button
                className="dep-btn save"
                onClick={() => void doRequestArtifacts()}
                style={{ background: "#ff6b6b" }}
              >
                Yes
              </button>
            </div>
          </div>
        </div>
      )}

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
