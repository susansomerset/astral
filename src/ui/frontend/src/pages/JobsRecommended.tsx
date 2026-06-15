import { useCallback, useEffect, useMemo, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import { legacyStateSectionLabel, unmappedJobStates } from "../lib/stateUiSections"
import CandidateActionNotesModal from "../components/CandidateActionNotesModal"
import CandidateJobRowActions from "../components/CandidateJobRowActions"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidateJobActions } from "../hooks/useCandidateJobActions"
import api from "../lib/api"
import Time from "../components/Time"

interface Job {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  jd_score?: number | null
  do_score?: number | null
  get_score?: number | null
  like_score?: number | null
  [key: string]: unknown
}

interface SortState { col: string; asc: boolean }

function formatPhaseScore(value: unknown): string {
  if (typeof value === "number" && Number.isFinite(value)) return value.toFixed(1)
  return "\u2014"
}

function sortRecommendedJobs(jobs: Job[], col: string, asc: boolean, phaseFields: string[]): Job[] {
  return [...jobs].sort((a, b) => {
    let cmp = 0
    if (col === "job_title") {
      cmp = (a.job_title || "").localeCompare(b.job_title || "")
    } else if (col === "company") {
      cmp = a.company.localeCompare(b.company)
    } else if (col === "state_changed_at") {
      cmp = (a.state_changed_at || "").localeCompare(b.state_changed_at || "")
    } else if (phaseFields.includes(col)) {
      const av = a[col]
      const bv = b[col]
      const an = typeof av === "number" && Number.isFinite(av) ? av : null
      const bn = typeof bv === "number" && Number.isFinite(bv) ? bv : null
      if (an === null && bn === null) cmp = 0
      else if (an === null) cmp = 1
      else if (bn === null) cmp = -1
      else cmp = an - bn
    }
    return asc ? cmp : -cmp
  })
}

export default function Recommended() {
  const { manifest, loadState } = useStateUi()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [reportId, setReportId] = useState<string | null>(null)
  // AST-587 / AST-565: row click opens Job Analysis Report only (not Job Detail)
  const openJobReport = useCallback((jobId: string) => setReportId(jobId), [])
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [sorts, setSorts] = useState<Record<string, SortState>>({})

  const load = useCallback(() => {
    if (!selectedId) return
    setLoading(true)
    api(`/api/jobs?view=recommended&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false))
  }, [selectedId])

  const actions = useCandidateJobActions(load)

  useEffect(() => {
    if (actions.error) setToast({ text: actions.error, variant: "error" })
  }, [actions.error])

  useEffect(() => { load() }, [load])

  const phaseFields = useMemo(
    () => manifest?.jobs.recommended.phase_score_columns.map(c => c.field) ?? [],
    [manifest?.jobs.recommended.phase_score_columns],
  )

  const sections = useMemo(() => {
    if (!manifest) return []
    const byState: Record<string, Job[]> = {}
    for (const job of rows) {
      if (!byState[job.state]) byState[job.state] = []
      byState[job.state].push(job)
    }
    const knownStates = manifest.jobs.recommended.sections.map(r => r.state)
    const normal = manifest.jobs.recommended.sections
      .filter(row => (byState[row.state]?.length ?? 0) > 0)
      .map(row => ({
        state: row.state,
        label: row.label,
        jobs: byState[row.state],
      }))
    const legacy = unmappedJobStates(rows, knownStates)
      .filter(s => byState[s]?.length)
      .map(s => ({
        state: s,
        label: legacyStateSectionLabel(s),
        jobs: byState[s],
      }))
    return [...normal, ...legacy]
  }, [rows, manifest])

  function handleSort(sectionState: string, col: string) {
    setSorts(prev => {
      const cur = prev[sectionState] ?? { col: "state_changed_at", asc: false }
      return { ...prev, [sectionState]: { col, asc: cur.col === col ? !cur.asc : true } }
    })
  }

  function sortIndicator(sectionState: string, col: string) {
    const s = sorts[sectionState]
    return s?.col === col ? <span style={{ fontSize: 10, marginLeft: 3 }}>{s.asc ? "▲" : "▼"}</span> : null
  }

  return (
    <div className="page-container">
      <div className="list-page-header">
        <h1 className="list-page-title">Recommended</h1>
      </div>
      {loading ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "loading" ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "error" || !manifest ? (
        <div className="list-page-status">State UI manifest unavailable.</div>
      ) : sections.length === 0 ? (
        <div className="list-page-status">No recommended jobs yet</div>
      ) : (
        sections.map(sec => {
          const sort = sorts[sec.state] ?? { col: "state_changed_at", asc: false }
          const sorted = sortRecommendedJobs(sec.jobs, sort.col, sort.asc, phaseFields)
          return (
            <div key={sec.state} style={{ marginBottom: 24 }}>
              <h2 style={{
                margin: "8px 0",
                color: "var(--text-primary)",
                fontSize: 15,
                fontWeight: 600,
              }}>
                {sec.label} ({sec.jobs.length})
              </h2>
              <div className="list-page-table-wrap">
                <table className="list-page-table">
                  <thead>
                    <tr>
                      <th style={{ width: 1, whiteSpace: "nowrap" }}>Actions</th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "job_title")}>
                        Job Title{sortIndicator(sec.state, "job_title")}
                      </th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "company")}>
                        Company{sortIndicator(sec.state, "company")}
                      </th>
                      {manifest.jobs.recommended.phase_score_columns.map(col => (
                        <th
                          key={col.field}
                          className="sortable"
                          style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}
                          onClick={() => handleSort(sec.state, col.field)}
                        >
                          {col.label}{sortIndicator(sec.state, col.field)}
                        </th>
                      ))}
                      <th className="sortable" onClick={() => handleSort(sec.state, "state_changed_at")}>
                        Updated{sortIndicator(sec.state, "state_changed_at")}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sorted.map(job => (
                      <tr key={job.astral_job_id} className="clickable" onClick={() => openJobReport(job.astral_job_id)}>
                        <td onClick={e => e.stopPropagation()}>
                          <CandidateJobRowActions
                            state={job.state}
                            showViewAnalysis={false}
                            onSkip={() => actions.skipJob(job.astral_job_id)}
                            onAction={a => actions.requestAction(job.astral_job_id, a)}
                          />
                        </td>
                        <td>{job.job_title || "\u2014"}</td>
                        <td>{job.company}</td>
                        {manifest.jobs.recommended.phase_score_columns.map(col => (
                          <td key={col.field} style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}>
                            {formatPhaseScore(job[col.field])}
                          </td>
                        ))}
                        <td><Time value={job.state_changed_at} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )
        })
      )}
      <JobAnalysisReportModal
        jobId={reportId}
        onClose={() => setReportId(null)}
        onRefresh={load}
      />
      <CandidateActionNotesModal
        open={!!actions.pending}
        action={actions.pending?.action ?? null}
        busy={actions.busy}
        onClose={actions.closePending}
        onConfirm={actions.confirmPending}
      />
      <Toast message={toast} onDone={() => setToast(null)} />
    </div>
  )
}
