import { useCallback, useEffect, useState } from "react"
import AdminCandidateFilterControl from "../components/AdminCandidateFilterControl"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import type { AdminCandidateFilterValue } from "../hooks/useAdminCandidateFilter"
import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"
import api from "../lib/api"

type InboxMessage = {
  id: string
  thread_id: string
  subject: string
  from_address: string
  date: string
  unread: boolean
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
  const { candidates } = useCandidate()
  // Default All — do not sync to nav selected candidate (AST-1558 AC).
  const [candidateFilter, setCandidateFilter] =
    useState<AdminCandidateFilterValue>("")
  const [messages, setMessages] = useState<InboxMessage[]>([])
  const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()
  const [error, setError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [assembledHtml, setAssembledHtml] = useState("")
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
  const landEnabled = Boolean(candidateFilter) && selectionCount > 0 && !landBusy
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

  function onFilterChange(next: AdminCandidateFilterValue) {
    setCandidateFilter(next)
    clearSelection()
  }

  const loadMessages = useCallback(async (showSpinner = false) => {
    beginRefresh(showSpinner)
    setError(null)
    try {
      const url = candidateFilter
        ? `/api/admin/inbox/messages?candidate_id=${encodeURIComponent(candidateFilter)}`
        : "/api/admin/inbox/messages"
      const r = await api(url)
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
      endRefresh()
    }
  }, [beginRefresh, endRefresh, candidateFilter])

  useEffect(() => {
    void loadMessages(true)
  }, [loadMessages])

  async function openMessage(row: InboxMessage) {
    setSelectedId(row.id)
    setAssembledHtml("")
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
      // Prefer assembled_html only — no html_body fallback (header+body AC).
      setAssembledHtml(
        typeof data.assembled_html === "string" ? data.assembled_html : "",
      )
    } catch (e) {
      setBodyError(e instanceof Error ? e.message : "Failed to load message")
    } finally {
      setBodyLoading(false)
    }
  }

  function closeModal() {
    setSelectedId(null)
    setAssembledHtml("")
    setBodyError(null)
  }

  const selected = messages.find(m => m.id === selectedId)
  const modalTitle = (selected?.subject || "").trim() || "Message"

  async function onLandMeteorite() {
    if (!candidateFilter || selectedIds.size === 0 || landBusy) return
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
        body: JSON.stringify({
          message_ids: ids,
          candidate_id: candidateFilter,
        }),
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
            <AdminCandidateFilterControl
              value={candidateFilter}
              onChange={onFilterChange}
              candidates={candidates}
            />
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
        </>
      )}

      <Modal
        open={selectedId !== null}
        onClose={closeModal}
        title={modalTitle}
        size="wide"
      >
        {bodyLoading && <p style={{ padding: 20 }}>Loading…</p>}
        {!bodyLoading && bodyError && (
          <p style={{ padding: 20, color: "var(--danger)", fontSize: 13 }}>{bodyError}</p>
        )}
        {!bodyLoading && !bodyError && (
          <>
            <div className="manage-email-modal-toolbar">
              <button
                type="button"
                className="btn secondary"
                disabled={!assembledHtml}
                onClick={() => {
                  void navigator.clipboard.writeText(assembledHtml).then(() => {
                    setToast({ text: "Copied to clipboard", variant: "success" })
                  })
                }}
                title="Copy header+body HTML"
              >
                Copy
              </button>
            </div>
            <div className="email-html-frame">
              <pre className="email-html-source" title="Email body">
                {assembledHtml || ""}
              </pre>
            </div>
          </>
        )}
      </Modal>

      {toast && <Toast message={toast} onDone={clearToast} />}
    </div>
  )
}
