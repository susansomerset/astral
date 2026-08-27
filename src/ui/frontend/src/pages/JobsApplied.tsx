import { useCallback, useEffect, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import CandidateActionNotesModal from "../components/CandidateActionNotesModal"
import CandidateJobRowActions from "../components/CandidateJobRowActions"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidateJobActions } from "../hooks/useCandidateJobActions"
import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"
import api from "../lib/api"
import Time from "../components/Time"

interface Job {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  [key: string]: unknown
}

interface SortState { col: string; asc: boolean }

function sortAppliedJobs(jobs: Job[], col: string, asc: boolean): Job[] {
  return [...jobs].sort((a, b) => {
    let cmp = 0
    if (col === "job_title") {
      cmp = (a.job_title || "").localeCompare(b.job_title || "")
    } else if (col === "company") {
      cmp = a.company.localeCompare(b.company)
    } else if (col === "state_changed_at") {
      cmp = (a.state_changed_at || "").localeCompare(b.state_changed_at || "")
    } else if (col === "state") {
      cmp = (a.state || "").localeCompare(b.state || "")
    }
    return asc ? cmp : -cmp
  })
}

/** AST-1488 (re-land of AST-1479): Applied jobs list — post-applied rows + shared R/I/X/G actions. */
export default function Applied() {
  const { selectedId, candidatesHydrated } = useCandidate()
  const [rows, setRows] = useState<Job[]>([])
  const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [sort, setSort] = useState<SortState>({ col: "state_changed_at", asc: false })
  const [confirmBusy, setConfirmBusy] = useState(false)
  const [confirmError, setConfirmError] = useState<string | null>(null)

  const load = useCallback((showSpinner = false) => {
    if (!selectedId) return
    beginRefresh(showSpinner)
    api(`/api/jobs?view=applied&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .finally(() => endRefresh())
  }, [selectedId, beginRefresh, endRefresh])

  const actions = useCandidateJobActions(load)

  const confirmPending = useCallback(async (notes: string) => {
    const pending = actions.pending
    if (!pending || confirmBusy || !selectedId) return
    setConfirmBusy(true)
    setConfirmError(null)
    try {
      const res = await api(`/api/jobs/${encodeURIComponent(pending.jobId)}/candidate_action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: pending.action,
          notes: notes ?? "",
          candidate_id: selectedId,
        }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error((body as { error?: string }).error || "Action failed")
      }
      actions.closePending()
      load()
    } catch (e) {
      setConfirmError(e instanceof Error ? e.message : "Action failed")
    } finally {
      setConfirmBusy(false)
    }
  }, [actions.pending, actions.closePending, confirmBusy, selectedId, load])

  useEffect(() => {
    const err = confirmError || actions.error
    if (err) setToast({ text: err, variant: "error" })
  }, [actions.error, confirmError])

  useEffect(() => { load(true) }, [load])

  function handleSort(col: string) {
    setSort(prev => ({ col, asc: prev.col === col ? !prev.asc : true }))
  }

  function sortIndicator(col: string) {
    return sort.col === col ? <span style={{ fontSize: 10, marginLeft: 3 }}>{sort.asc ? "▲" : "▼"}</span> : null
  }

  const sorted = sortAppliedJobs(rows, sort.col, sort.asc)

  if (!candidatesHydrated) {
    return (
      <div className="page-container">
        <div className="list-page-header">
          <h1 className="list-page-title">Applied</h1>
        </div>
        <div className="list-page-status">Loading...</div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="list-page-header">
        <h1 className="list-page-title">Applied</h1>
      </div>
      {loading ? (
        <div className="list-page-status">Loading...</div>
      ) : rows.length === 0 ? (
        <div className="list-page-status">No applied jobs yet</div>
      ) : (
        <div className="list-page-table-wrap">
          <table className="list-page-table">
            <thead>
              <tr>
                <th style={{ width: 1, whiteSpace: "nowrap" }}>Actions</th>
                <th className="sortable" onClick={() => handleSort("job_title")}>
                  Job Title{sortIndicator("job_title")}
                </th>
                <th className="sortable" onClick={() => handleSort("company")}>
                  Company{sortIndicator("company")}
                </th>
                <th className="sortable" onClick={() => handleSort("state")}>
                  State{sortIndicator("state")}
                </th>
                <th className="sortable" onClick={() => handleSort("state_changed_at")}>
                  Updated{sortIndicator("state_changed_at")}
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(job => (
                <tr key={job.astral_job_id}>
                  <td>
                    <CandidateJobRowActions
                      state={job.state}
                      onAction={a => actions.requestAction(job.astral_job_id, a)}
                    />
                  </td>
                  <td>{job.job_title || "\u2014"}</td>
                  <td>{job.company}</td>
                  <td>{job.state || "\u2014"}</td>
                  <td><Time value={job.state_changed_at} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <CandidateActionNotesModal
        open={!!actions.pending}
        action={actions.pending?.action ?? null}
        busy={actions.busy || confirmBusy}
        onClose={actions.closePending}
        onConfirm={confirmPending}
      />
      <Toast message={toast} onDone={() => setToast(null)} />
    </div>
  )
}
