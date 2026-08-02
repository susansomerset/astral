import { useCallback, useState } from "react"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import { useLocalStorage } from "../lib/useLocalStorage"

/** Must match BUILD_CONFIG["session_cover_letter"]["fields"] keys/required (AST-1024). */
const SESSION_COVER_FIELDS = [
  { key: "from_block", label: "From block", required: true, rows: 3 },
  { key: "letter_date", label: "Date", required: true, rows: 1 },
  { key: "to_block", label: "To block", required: false, rows: 2 },
  { key: "subject", label: "Subject", required: false, rows: 1 },
  { key: "letter", label: "Letter body", required: true, rows: 12 },
  { key: "signoff_closing", label: "Sign-off closing", required: true, rows: 1 },
  { key: "signature", label: "Signature name", required: true, rows: 1 },
] as const

type SessionCoverFieldKey = (typeof SESSION_COVER_FIELDS)[number]["key"]
type SessionCoverFields = Record<SessionCoverFieldKey, string>

type SessionCoverLastRender = {
  fields: SessionCoverFields
  candidate_id: string | null
} | null

const EMPTY_FIELDS: SessionCoverFields = {
  from_block: "",
  letter_date: "",
  to_block: "",
  subject: "",
  letter: "",
  signoff_closing: "",
  signature: "",
}

export default function SessionCoverLetter() {
  const { selectedId } = useCandidate()
  const [fields, setFields] = useLocalStorage<SessionCoverFields>(
    "session_cover_letter:fields",
    EMPTY_FIELDS,
  )
  const [, setLastRender] = useLocalStorage<SessionCoverLastRender>(
    "session_cover_letter:last_render",
    null,
  )
  const [opening, setOpening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  // AST-1139: empty from_block OK when candidate selected (server resolves defaults).
  const candidateSelected = Boolean(selectedId && selectedId.trim())
  const requiredComplete = SESSION_COVER_FIELDS.every(f => {
    if (!f.required) return true
    if (f.key === "from_block" && candidateSelected) return true
    return (fields[f.key] ?? "").trim() !== ""
  })

  function setField(key: SessionCoverFieldKey, value: string) {
    setFields(prev => ({ ...prev, [key]: value }))
  }

  async function handleOpenHtml() {
    if (!requiredComplete || opening) return
    setOpening(true)
    setError(null)
    const candidate_id =
      selectedId && selectedId.trim() ? selectedId.trim() : null
    const body = { ...fields, candidate_id }
    try {
      const r = await api("/api/admin/session_cover_letter/html", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
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
      setLastRender({ fields: { ...fields }, candidate_id })
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
        Session Cover Letter
      </h1>
      <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--text-muted)", lineHeight: 1.5 }}>
        Enter cover-letter field values, then Open HTML to Print → PDF.
        Letter fields come from this form. When a candidate is selected, leave
        From block empty to use that candidate’s cover from-block text or the
        contact default (Name • City, ST / email • phone). Without a candidate,
        From block is required. If a candidate is selected and has a profile
        signature image, the server may include it in the sign-off; otherwise
        name-only. This tool does not save to the database.
      </p>

      {SESSION_COVER_FIELDS.map(f => (
        <label
          key={f.key}
          style={{ display: "block", marginBottom: 12, fontSize: 13, color: "var(--text-primary)" }}
        >
          <span style={{ display: "block", marginBottom: 4 }}>
            {f.label}{f.required ? "" : " (optional)"}
          </span>
          {f.rows === 1 ? (
            <input
              className="dep-input"
              type="text"
              value={fields[f.key] ?? ""}
              onChange={e => setField(f.key, e.target.value)}
              disabled={opening}
              style={{ width: "100%", boxSizing: "border-box" }}
            />
          ) : (
            <textarea
              className="dep-input"
              value={fields[f.key] ?? ""}
              onChange={e => setField(f.key, e.target.value)}
              rows={f.rows}
              spellCheck={false}
              disabled={opening}
              style={{
                width: "100%",
                boxSizing: "border-box",
                resize: "vertical",
                ...(f.key === "letter"
                  ? { fontFamily: "monospace", fontSize: 12 }
                  : {}),
              }}
            />
          )}
        </label>
      ))}

      <div style={{ display: "flex", gap: 8, marginTop: 4, alignItems: "center" }}>
        <button
          type="button"
          className="dep-btn save"
          onClick={() => void handleOpenHtml()}
          disabled={!requiredComplete || opening}
        >
          {opening ? "Opening…" : "Open HTML"}
        </button>
      </div>

      {error && (
        <p style={{ marginTop: 12, color: "var(--danger, #c44)", fontSize: 13 }}>
          {error}
        </p>
      )}

      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
