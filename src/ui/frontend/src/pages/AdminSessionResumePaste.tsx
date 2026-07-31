import { useCallback, useState } from "react"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import api from "../lib/api"
import { useLocalStorage } from "../lib/useLocalStorage"

/** Last successful parse payload retained for Open HTML (AST-987). */
type SessionResumeParse = {
  resume_structure: Record<string, unknown>
  base_resume: Record<string, unknown>
} | null

export default function SessionResumePaste() {
  const [pasteText, setPasteText] = useLocalStorage<string>("session_resume:paste_text", "")
  const [lastParse, setLastParse] = useLocalStorage<SessionResumeParse>(
    "session_resume:last_parse",
    null,
  )
  const [parsing, setParsing] = useState(false)
  const [opening, setOpening] = useState(false)
  const [jsonOpen, setJsonOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  async function handleParse() {
    const text = pasteText.trim()
    if (!text || parsing) return
    setParsing(true)
    setError(null)
    try {
      const r = await api("/api/admin/session_resume/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: pasteText }),
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
      const win = window.open(blobUrl, "_blank", "noopener,noreferrer")
      if (!win) {
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

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <h1 style={{ margin: "0 0 8px", fontSize: 22, color: "var(--text-primary)" }}>
        Session Resume Paste
      </h1>
      <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--text-muted)", lineHeight: 1.5 }}>
        Paste a full resume, Parse to structure-keyed JSON, optionally View Parsed JSON, then Open HTML to Print → PDF.
        This tool does not use the selected candidate and does not save to the database.
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
          className="dep-btn save"
          onClick={() => void handleParse()}
          disabled={!pasteText.trim() || parsing}
        >
          {parsing ? "Parsing…" : "Parse"}
        </button>
        <button
          type="button"
          className="dep-btn"
          onClick={() => setJsonOpen(true)}
          disabled={!lastParse || opening || parsing}
        >
          View Parsed JSON
        </button>
        <button
          type="button"
          className="dep-btn"
          onClick={() => void handleOpenHtml()}
          disabled={!lastParse || opening || parsing}
        >
          {opening ? "Opening…" : "Open HTML"}
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
