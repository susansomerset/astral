import { useCallback, useEffect, useState } from "react"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import api from "../lib/api"

type CandidateMatch = {
  matched: boolean
  astral_candidate_id: string | null
}

type InboxMessage = {
  id: string
  thread_id: string
  subject: string
  from_address: string
  date: string
  unread: boolean
  candidate_match?: CandidateMatch
}

export default function AdminManageEmail() {
  const [messages, setMessages] = useState<InboxMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [htmlBody, setHtmlBody] = useState("")
  const [bodyLoading, setBodyLoading] = useState(false)
  const [bodyError, setBodyError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const r = await api("/api/admin/inbox/messages")
        const data = await r.json().catch(() => ({} as Record<string, unknown>))
        if (!r.ok) {
          const msg =
            (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
          if (!cancelled) {
            setError(msg)
            setToast({ text: msg, variant: "error" })
          }
          return
        }
        const rows = Array.isArray(data.messages) ? data.messages : []
        if (!cancelled) {
          setMessages(rows as InboxMessage[])
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to load inbox"
        if (!cancelled) {
          setError(msg)
          setToast({ text: msg, variant: "error" })
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  async function openMessage(row: InboxMessage) {
    setSelectedId(row.id)
    setHtmlBody("")
    setBodyError(null)
    setBodyLoading(true)
    try {
      const r = await api(`/api/admin/inbox/messages/${encodeURIComponent(row.id)}`)
      const data = await r.json().catch(() => ({} as Record<string, unknown>))
      if (!r.ok) {
        const msg =
          (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
        setBodyError(msg)
        return
      }
      setHtmlBody(typeof data.html_body === "string" ? data.html_body : "")
    } catch (e) {
      setBodyError(e instanceof Error ? e.message : "Failed to load message")
    } finally {
      setBodyLoading(false)
    }
  }

  function closeModal() {
    setSelectedId(null)
    setHtmlBody("")
    setBodyError(null)
  }

  // AST-1049 owns strip/extract + meteorite create wire from this control.
  function onCreateClick() {}

  const selected = messages.find(m => m.id === selectedId)
  const modalTitle = (selected?.subject || "").trim() || "Message"
  const selectedMatched =
    selected?.candidate_match?.matched === true &&
    Boolean((selected.candidate_match.astral_candidate_id || "").trim())
  const selectedMatchId = selectedMatched
    ? (selected!.candidate_match!.astral_candidate_id as string)
    : null

  function matchCell(row: InboxMessage) {
    const m = row.candidate_match
    if (m?.matched === true && (m.astral_candidate_id || "").trim()) {
      return (
        <td>
          <span className="manage-email-match">Matched: {m.astral_candidate_id}</span>
        </td>
      )
    }
    return <td>—</td>
  }

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ margin: "0 0 16px", fontSize: 22, color: "var(--text-primary)" }}>
        Manage Email
      </h1>
      {loading && <p>Loading…</p>}
      {error && !loading && (
        <p style={{ color: "var(--danger)", fontSize: 13 }}>{error}</p>
      )}
      {!loading && !error && (
        <div className="list-page-table-wrap">
          <table className="list-page-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>From</th>
                <th>Candidate</th>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {messages.map(row => (
                <tr
                  key={row.id}
                  style={{ cursor: "pointer" }}
                  onClick={() => openMessage(row)}
                >
                  <td>{row.subject}</td>
                  <td>{row.from_address}</td>
                  {matchCell(row)}
                  <td>{row.date}</td>
                  <td>{row.unread ? "Unread" : "Read"}</td>
                </tr>
              ))}
              {messages.length === 0 && (
                <tr>
                  <td colSpan={5}>No messages in inbox.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={selectedId !== null}
        onClose={closeModal}
        title={modalTitle}
        size="wide"
      >
        {selectedMatchId && (
          <p className="manage-email-match manage-email-match--modal">
            Matched: {selectedMatchId}
          </p>
        )}
        {bodyLoading && <p style={{ padding: 20 }}>Loading…</p>}
        {!bodyLoading && bodyError && (
          <p style={{ padding: 20, color: "var(--danger)", fontSize: 13 }}>{bodyError}</p>
        )}
        {!bodyLoading && !bodyError && (
          <div className="email-html-frame">
            <pre className="email-html-source" title="Email body">{htmlBody || ""}</pre>
          </div>
        )}
        <div className="manage-email-actions">
          <button
            type="button"
            className="manage-email-create"
            disabled={!selected?.candidate_match?.matched}
            onClick={onCreateClick}
          >
            Create
          </button>
        </div>
      </Modal>

      {toast && <Toast message={toast} onDone={clearToast} />}
    </div>
  )
}
