import { useCallback, useState } from "react"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import { useLocalStorage } from "../lib/useLocalStorage"

/** Last successful parse payload retained for Open HTML (AST-987). */
type SessionResumeParse = {
  resume_structure: Record<string, unknown>
  base_resume: Record<string, unknown>
} | null

export default function SessionResumePaste() {
  // AST-1880: Ruth's call runs on the selected candidate's key for her model's server.
  const { selectedId } = useCandidate()
  const [pasteText, setPasteText] = useLocalStorage<string>("session_resume:paste_text", "")
  const [lastParse, setLastParse] = useLocalStorage<SessionResumeParse>(
    "session_resume:last_parse",
    null,
  )
  const [parsing, setParsing] = useState(false)
  const [opening, setOpening] = useState(false)
  const [saving, setSaving] = useState(false)
  const [jsonOpen, setJsonOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  async function handleParse() {
    const text = pasteText.trim()
    if (!text || parsing || !selectedId) return
    setParsing(true)
    setError(null)
    try {
      const r = await api("/api/admin/session_resume/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: pasteText, candidate_id: selectedId }),
      })
      const data = await r.json().catch(() => ({} as Record<string, unknown>))
      if (!r.ok || data.success !== true) {
        const msg =
          (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      const structure = data.resume_structure
      const content = data.base_resume
      if (
        !structure ||
        typeof structure !== "object" ||
        Array.isArray(structure) ||
        !content ||
        typeof content !== "object" ||
        Array.isArray(content)
      ) {
        const msg = "Parse succeeded but resume_structure/base_resume missing"
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      setLastParse({
        resume_structure: structure as Record<string, unknown>,
        base_resume: content as Record<string, unknown>,
      })
      setError(null)
      setToast({ text: "Parsed resume structure.", variant: "success" })
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Parse failed"
      setError(msg)
      setToast({ text: msg, variant: "error" })
    } finally {
      setParsing(false)
    }
  }

  async function handleOpenHtml() {
    if (!lastParse || opening || parsing) return
    setOpening(true)
    setError(null)
    try {
      const r = await api("/api/admin/session_resume/html", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lastParse),
      })
      if (!r.ok) {
        let msg = `HTTP ${r.status}`
        try {
          const data = await r.json()
          if (typeof data.error === "string" && data.error) msg = data.error
        } catch { /* non-JSON error body */ }
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      const html = await r.text()
      if (!html.trim()) {
        const msg = "HTML response was empty"
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      const blobUrl = URL.createObjectURL(
        new Blob([html], { type: "text/html;charset=utf-8" }),
      )
      // No noopener/noreferrer features — those force a null return even on success.
      const win = window.open(blobUrl, "_blank")
      if (win) {
        win.opener = null
      } else {
        setToast({
          text: "Popup blocked — allow popups to open the HTML tab.",
          variant: "error",
        })
      }
      window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Open HTML failed"
      setError(msg)
      setToast({ text: msg, variant: "error" })
    } finally {
      setOpening(false)
    }
  }

  async function handleSave() {
    if (!selectedId || !lastParse || saving || parsing || opening) return
    setSaving(true)
    setError(null)
    try {
      // Sections only — no accent_color — so the route replaces the layout and keeps the candidate's accent.
      // base_resume goes as parsed: the route's ingest/filter owns shaping (no client-side reshape).
      const r = await api(`/api/candidates/${selectedId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          artifacts: {
            resume_structure: { sections: lastParse.resume_structure.sections },
            base_resume: lastParse.base_resume,
          },
        }),
      })
      if (!r.ok) {
        let msg = `HTTP ${r.status}`
        try {
          const data = await r.json()
          if (typeof data.error === "string" && data.error) msg = data.error
        } catch { /* non-JSON error body */ }
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      setToast({ text: "Saved parse as the candidate's base resume.", variant: "success" })
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Save failed"
      setError(msg)
      setToast({ text: msg, variant: "error" })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <h1 style={{ margin: "0 0 8px", fontSize: 22, color: "var(--text-primary)" }}>
        Session Resume Paste
      </h1>
      <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--text-muted)", lineHeight: 1.5 }}>
        Paste a full resume, Parse to structure-keyed JSON, optionally View Parsed JSON, then Open HTML to Print → PDF.
        Uses the selected candidate's API key for Ruth's model. Parse and Open HTML do not save; Save to Candidate writes
        the parse as the selected candidate's base resume and section layout.
      </p>

      <textarea
        className="dep-input"
        value={pasteText}
        onChange={e => setPasteText(e.target.value)}
        rows={16}
        placeholder="Paste full resume text here"
        style={{
          width: "100%",
          fontFamily: "monospace",
          fontSize: 12,
          resize: "vertical",
          boxSizing: "border-box",
        }}
        spellCheck={false}
        disabled={parsing}
      />

      <div style={{ display: "flex", gap: 8, marginTop: 12, alignItems: "center" }}>
        <button
          type="button"
          className="btn primary"
          onClick={() => void handleParse()}
          disabled={!selectedId || !pasteText.trim() || parsing || saving}
          title={selectedId ? undefined : "Select a candidate first — Parse runs on their API key"}
        >
          {parsing ? "Parsing…" : "Parse"}
        </button>
        <button
          type="button"
          className="btn secondary"
          onClick={() => setJsonOpen(true)}
          disabled={!lastParse || opening || parsing || saving}
        >
          View Parsed JSON
        </button>
        <button
          type="button"
          className="btn secondary"
          onClick={() => void handleOpenHtml()}
          disabled={!lastParse || opening || parsing || saving}
        >
          {opening ? "Opening…" : "Open HTML"}
        </button>
        <button
          type="button"
          className="btn secondary"
          onClick={() => void handleSave()}
          disabled={!selectedId || !lastParse || parsing || opening || saving}
        >
          {saving ? "Saving…" : "Save to Candidate"}
        </button>
      </div>

      {error && (
        <p style={{ marginTop: 12, color: "var(--danger, #c44)", fontSize: 13 }}>
          {error}
        </p>
      )}

      <Modal
        open={jsonOpen}
        onClose={() => setJsonOpen(false)}
        title="Parsed resume JSON"
      >
        <pre style={{
          whiteSpace: "pre-wrap", wordBreak: "break-word", fontSize: 13,
          color: "#e0e0e0", background: "#1a1a2e", padding: 16, borderRadius: 8,
          maxHeight: "60vh", overflow: "auto",
        }}>
          {lastParse ? JSON.stringify(lastParse, null, 2) : ""}
        </pre>
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
