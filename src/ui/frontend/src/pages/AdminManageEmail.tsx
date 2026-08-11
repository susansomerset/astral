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

type LandMeteoriteResultRow = {
  message_id: string
  outcome: string
  astral_candidate_id: string | null
}

type LandMeteoriteResponse = {
  results?: LandMeteoriteResultRow[]
  total_processed?: number
  total_passed?: number
  total_failed?: number
  total_errors?: number
  total_skipped?: number
  error?: string
}

function outcomeKind(outcome: string): "skip" | "fail" | "ok" {
  const o = (outcome || "").trim()
  if (o.startsWith("skipped-") || o === "skipped-other-candidate") return "skip"
  if (o === "error" || o === "failed") return "fail"
  return "ok"
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
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [landBusy, setLandBusy] = useState(false)
  const [landResults, setLandResults] = useState<LandMeteoriteResultRow[] | null>(null)
  const [landError, setLandError] = useState<string | null>(null)
  const [landSubjectById, setLandSubjectById] = useState<Record<string, string>>({})
  const clearToast = useCallback(() => setToast(null), [])

  const selectionCount = selectedIds.size
  const landEnabled = selectionCount > 0 && !landBusy
  const allSelected =
    messages.length > 0 && selectedIds.size === messages.length

  function toggleSelect(id: string) {
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function selectAllVisible() {
    setSelectedIds(new Set(messages.map(m => m.id)))
  }

  function clearSelection() {
    setSelectedIds(new Set())
  }

  const loadMessages = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await api("/api/admin/inbox/messages")
      const data = await r.json().catch(() => ({} as Record<string, unknown>))
      if (!r.ok) {
        const msg =
          (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
        setError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      const rows = Array.isArray(data.messages) ? data.messages : []
      setMessages(rows as InboxMessage[])
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load inbox"
      setError(msg)
      setToast({ text: msg, variant: "error" })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadMessages()
  }, [loadMessages])

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

  const selected = messages.find(m => m.id === selectedId)
  const modalTitle = (selected?.subject || "").trim() || "Message"
  const selectedMatchId =
    selected?.candidate_match?.matched === true &&
    (selected.candidate_match.astral_candidate_id || "").trim()
      ? (selected.candidate_match.astral_candidate_id as string)
      : null

  async function onLandMeteorite() {
    if (selectedIds.size === 0 || landBusy) return
    const ordered = messages.filter(m => selectedIds.has(m.id)).map(m => m.id)
    const orderedSet = new Set(ordered)
    const leftovers = [...selectedIds].filter(id => !orderedSet.has(id))
    const ids = [...ordered, ...leftovers]
    const subjectById = Object.fromEntries(messages.map(m => [m.id, m.subject]))
    setLandSubjectById(subjectById)
    setLandBusy(true)
    setLandError(null)
    setLandResults(null)
    setToast(null)
    try {
      const r = await api("/api/admin/inbox/land-meteorite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_ids: ids }),
      })
      const data = (await r.json().catch(() => ({}))) as LandMeteoriteResponse
      if (!r.ok) {
        const msg =
          (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
        setLandError(msg)
        setToast({ text: msg, variant: "error" })
        return
      }
      setLandResults(Array.isArray(data.results) ? data.results : [])
      clearSelection()
      const parts = [
        typeof data.total_passed === "number" ? `passed ${data.total_passed}` : null,
        typeof data.total_skipped === "number" ? `skipped ${data.total_skipped}` : null,
        typeof data.total_failed === "number" ? `failed ${data.total_failed}` : null,
        typeof data.total_errors === "number" ? `errors ${data.total_errors}` : null,
      ].filter(Boolean)
      if (parts.length > 0) {
        setToast({ text: `Land Meteorite: ${parts.join(", ")}`, variant: "success" })
      }
      await loadMessages()
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Land Meteorite failed"
      setLandError(msg)
      setToast({ text: msg, variant: "error" })
    } finally {
      setLandBusy(false)
    }
  }

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
        <>
          <div className="manage-email-toolbar">
            <button
              type="button"
              className="btn primary"
              disabled={messages.length === 0}
              onClick={selectAllVisible}
            >
              Select all
            </button>
            <button
              type="button"
              className="btn secondary"
              disabled={selectionCount === 0}
              onClick={clearSelection}
            >
              Clear selection
            </button>
            <button
              type="button"
              className="btn primary"
              disabled={!landEnabled}
              onClick={onLandMeteorite}
            >
              Land Meteorite
            </button>
            <span>{selectionCount} selected</span>
          </div>
          {landError && (
            <p style={{ color: "var(--danger)", fontSize: 13, margin: "0 0 12px" }}>
              {landError}
            </p>
          )}
          {landResults && (
            <div className="manage-email-results">
              <div className="manage-email-results-title">Land Meteorite results</div>
              <ul>
                {landResults.map(row => {
                  const subject =
                    (landSubjectById[row.message_id] || "").trim() || row.message_id
                  const kind = outcomeKind(row.outcome)
                  const cid =
                    row.astral_candidate_id && String(row.astral_candidate_id).trim()
                      ? String(row.astral_candidate_id).trim()
                      : null
                  return (
                    <li
                      key={row.message_id}
                      className={`manage-email-outcome manage-email-outcome--${kind}`}
                    >
                      {subject} — {row.outcome}
                      {cid ? ` (${cid})` : ""}
                    </li>
                  )
                })}
              </ul>
            </div>
          )}
          <div className="list-page-table-wrap">
            <table className="list-page-table">
              <thead>
                <tr>
                  <th>
                    <input
                      type="checkbox"
                      checked={allSelected}
                      onChange={() =>
                        allSelected ? clearSelection() : selectAllVisible()
                      }
                    />
                  </th>
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
                    <td onClick={e => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={selectedIds.has(row.id)}
                        onChange={() => toggleSelect(row.id)}
                      />
                    </td>
                    <td>{row.subject}</td>
                    <td>{row.from_address}</td>
                    {matchCell(row)}
                    <td>{row.date}</td>
                    <td>{row.unread ? "Unread" : "Read"}</td>
                  </tr>
                ))}
                {messages.length === 0 && (
                  <tr>
                    <td colSpan={6}>No messages in inbox.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
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
      </Modal>

      {toast && <Toast message={toast} onDone={clearToast} />}
    </div>
  )
}
