import { Fragment, useCallback, useEffect, useMemo, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import { legacyStateSectionLabel, unmappedJobStates } from "../lib/stateUiSections"
import CandidateActionNotesModal from "../components/CandidateActionNotesModal"
import CandidateJobRowActions from "../components/CandidateJobRowActions"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import PhaseAnalysisLines from "../components/PhaseAnalysisLines"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidateJobActions, type BulkActionResult } from "../hooks/useCandidateJobActions"
import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"
import api from "../lib/api"
import { formatPhaseScore, primaryActionsForState } from "../lib/recommendedJobReport"
import Time from "../components/Time"
import JobTitleText from "../components/JobTitleText"

interface Job {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  source?: string | null
  jd_score?: number | null
  do_score?: number | null
  get_score?: number | null
  like_score?: number | null
  [key: string]: unknown
}

interface SortState { col: string; asc: boolean }

const TOTAL_SCORE_COL = "total_score"

function finiteOrNull(v: unknown): number | null {
  return typeof v === "number" && Number.isFinite(v) ? v : null
}

// Sum of manifest phase_score_columns; null if any phase score is missing (AST-1968).
function totalScore(job: Job, phaseFields: string[]): number | null {
  if (!phaseFields.length) return null
  let sum = 0
  for (const field of phaseFields) {
    const n = finiteOrNull(job[field])
    if (n === null) return null
    sum += n
  }
  return sum
}

function sortRecommendedJobs(jobs: Job[], col: string, asc: boolean, phaseFields: string[]): Job[] {
  return [...jobs].sort((a, b) => {
    let cmp = 0
    if (col === "job_title") {
      cmp = (a.job_title || "").localeCompare(b.job_title || "")
    } else if (col === "company") {
      cmp = a.company.localeCompare(b.company)
    } else if (col === "source") {
      cmp = (a.source || "").localeCompare(b.source || "")
    } else if (col === "state_changed_at") {
      cmp = (a.state_changed_at || "").localeCompare(b.state_changed_at || "")
    } else if (col === "state") {
      cmp = (a.state || "").localeCompare(b.state || "")
    } else if (phaseFields.includes(col) || col === TOTAL_SCORE_COL) {
      // Total shares the phase columns' null handling — one sorter, not two.
      const an = col === TOTAL_SCORE_COL ? totalScore(a, phaseFields) : finiteOrNull(a[col])
      const bn = col === TOTAL_SCORE_COL ? totalScore(b, phaseFields) : finiteOrNull(b[col])
      if (an === null && bn === null) cmp = 0
      else if (an === null) cmp = 1
      else if (bn === null) cmp = -1
      else cmp = an - bn
    }
    return asc ? cmp : -cmp
  })
}

// AST-1975: one list component for Jobs → Ready and Jobs → Review; the route supplies both.
interface RecommendedProps { view: "ready" | "review"; title: string }

export default function Recommended({ view, title }: RecommendedProps) {
  const { manifest, loadState } = useStateUi()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<Job[]>([])
  const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()
  const [reportId, setReportId] = useState<string | null>(null)
  // AST-587 / AST-565: row click opens Job Analysis Report only (not Job Detail)
  const openJobReport = useCallback((jobId: string) => setReportId(jobId), [])
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [sorts, setSorts] = useState<Record<string, SortState>>({})
  // Page-level selection keyed by astral_job_id; not persisted (AST-1968).
  const [selected, setSelected] = useState<Set<string>>(new Set())
  // Analysis toggle: on at page load, not persisted (AST-1968).
  const [showAnalysis, setShowAnalysis] = useState(true)

  const load = useCallback((showSpinner = false) => {
    if (!selectedId) return
    beginRefresh(showSpinner)
    api(`/api/jobs?view=${view}&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => r.json())
      .then(data => {
        // Spinner loads are mount + candidate switch only — drop any prior selection there.
        // Cleared in the async callback, not synchronously, so the mount effect stays lint-clean.
        if (showSpinner) setSelected(new Set())
        setRows(Array.isArray(data) ? data : [])
      })
      .finally(() => endRefresh())
  }, [selectedId, view, beginRefresh, endRefresh])

  // After any bulk action: one toast with the split, then clear selection (AC 8).
  const handleBulkDone = useCallback((r: BulkActionResult) => {
    setSelected(new Set())
    setToast({
      text: `${r.label}: ${r.succeeded} succeeded, ${r.failed} failed`,
      variant: r.failed ? "error" : "success",
    })
  }, [])

  const actions = useCandidateJobActions(load, handleBulkDone)

  // Hook errors render as a derived toast (no setState-in-effect); memoized so Toast's
  // timer only restarts when the error itself changes. Page toasts (bulk) take precedence.
  const errorToast = useMemo<ToastMessage | null>(
    () => (actions.error ? { text: actions.error, variant: "error" } : null),
    [actions.error],
  )
  const { clearError } = actions
  const dismissToast = useCallback(() => {
    setToast(null)
    clearError()
  }, [clearError])

  useEffect(() => { load(true) }, [load])

  const phaseFields = useMemo(
    () => manifest?.jobs.recommended.phase_score_columns.map(c => c.field) ?? [],
    [manifest?.jobs.recommended.phase_score_columns],
  )

  // Eligibility from manifest primary_actions_by_state — no hardcoded state list.
  const canGenerate = useCallback(
    (state: string) => primaryActionsForState(manifest, state).some(a => a.action_key === "generate_artifacts"),
    [manifest],
  )

  // Derived from current rows so ids that left the list (row action, refresh) never count.
  const selectedIds = useMemo(
    () => rows.filter(j => selected.has(j.astral_job_id)).map(j => j.astral_job_id),
    [rows, selected],
  )
  const generateIds = useMemo(
    () => rows.filter(j => selected.has(j.astral_job_id) && canGenerate(j.state)).map(j => j.astral_job_id),
    [rows, selected, canGenerate],
  )

  const toggleSelect = useCallback((id: string) => setSelected(prev => {
    const next = new Set(prev)
    if (next.has(id)) next.delete(id); else next.add(id)
    return next
  }), [])

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
      .map(row => ({ state: row.state, label: row.label, jobs: byState[row.state] }))
    const legacy = unmappedJobStates(rows, knownStates)
      .filter(s => byState[s]?.length)
      .map(s => ({ state: s, label: legacyStateSectionLabel(s), jobs: byState[s] }))
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
        <h1 className="list-page-title">{title}</h1>
        <div className="recommended-list-header-actions">
          {selectedIds.length > 0 && (
            <>
              <button type="button" className="btn secondary" disabled={actions.busy}
                onClick={() => actions.skipJobs(selectedIds)}>
                Skip ({selectedIds.length})
              </button>
              <button type="button" className="btn secondary" disabled={actions.busy}
                onClick={() => actions.requestBulkAction(selectedIds, "applied", "Applied")}>
                Applied ({selectedIds.length})
              </button>
              <button type="button" className="btn primary" disabled={actions.busy || generateIds.length === 0}
                onClick={() => actions.generateJobs(generateIds)}>
                Generate Artifacts ({generateIds.length})
              </button>
            </>
          )}
          <label className="recommended-analysis-toggle">
            <input type="checkbox" checked={showAnalysis} onChange={e => setShowAnalysis(e.target.checked)} />
            Analysis
          </label>
        </div>
      </div>
      {loading ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "loading" ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "error" || !manifest ? (
        <div className="list-page-status">State UI manifest unavailable.</div>
      ) : sections.length === 0 ? (
        <div className="list-page-status">{`No jobs in ${title}`}</div>
      ) : (
        sections.map(sec => {
          const sort = sorts[sec.state] ?? { col: "state_changed_at", asc: false }
          const sorted = sortRecommendedJobs(sec.jobs, sort.col, sort.asc, phaseFields)
          // checkbox + actions + title + company + source + state + phase cols + total + updated
          const columnCount = 8 + manifest.jobs.recommended.phase_score_columns.length
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
                      <th style={{ width: 1 }} aria-label="Select" />
                      <th style={{ width: 1, whiteSpace: "nowrap" }}>Actions</th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "job_title")}>
                        Job Title{sortIndicator(sec.state, "job_title")}
                      </th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "company")}>
                        Company{sortIndicator(sec.state, "company")}
                      </th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "source")}>
                        Source{sortIndicator(sec.state, "source")}
                      </th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "state")}>
                        State{sortIndicator(sec.state, "state")}
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
                      <th
                        className="sortable"
                        style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}
                        onClick={() => handleSort(sec.state, TOTAL_SCORE_COL)}
                      >
                        Total{sortIndicator(sec.state, TOTAL_SCORE_COL)}
                      </th>
                      <th className="sortable" onClick={() => handleSort(sec.state, "state_changed_at")}>
                        Updated{sortIndicator(sec.state, "state_changed_at")}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sorted.map(job => (
                      <Fragment key={job.astral_job_id}>
                        <tr className="clickable" onClick={() => openJobReport(job.astral_job_id)}>
                          <td onClick={e => e.stopPropagation()}>
                            <input
                              type="checkbox"
                              aria-label={`Select ${job.job_title || job.astral_job_id}`}
                              checked={selected.has(job.astral_job_id)}
                              onChange={() => toggleSelect(job.astral_job_id)}
                            />
                          </td>
                          <td onClick={e => e.stopPropagation()}>
                            <CandidateJobRowActions
                              state={job.state}
                              showViewAnalysis={false}
                              onSkip={() => actions.skipJob(job.astral_job_id)}
                              onAction={a => actions.requestAction(job.astral_job_id, a)}
                              onGenerate={canGenerate(job.state) ? () => actions.generateJob(job.astral_job_id) : undefined}
                            />
                          </td>
                          <td><JobTitleText title={job.job_title} fallback={"\u2014"} /></td>
                          <td>{job.company}</td>
                          <td>{job.source || "\u2014"}</td>
                          <td>{job.state || "\u2014"}</td>
                          {manifest.jobs.recommended.phase_score_columns.map(col => (
                            <td key={col.field} style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}>
                              {formatPhaseScore(job[col.field])}
                            </td>
                          ))}
                          <td style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}>
                            {formatPhaseScore(totalScore(job, phaseFields))}
                          </td>
                          <td><Time value={job.state_changed_at} /></td>
                        </tr>
                        {showAnalysis && (
                          <tr className="clickable recommended-analysis-row" onClick={() => openJobReport(job.astral_job_id)}>
                            <td colSpan={columnCount}>
                              <PhaseAnalysisLines job={job} />
                            </td>
                          </tr>
                        )}
                      </Fragment>
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
      <Toast message={toast ?? errorToast} onDone={dismissToast} />
    </div>
  )
}
