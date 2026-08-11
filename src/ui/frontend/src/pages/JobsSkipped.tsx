import { useCallback, useEffect, useMemo, useState } from "react"
import { ConfidenceBullets } from "../components/ConfidenceBullets"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import { legacyStateSectionLabel, unmappedJobStates } from "../lib/stateUiSections"
import CandidateActionNotesModal from "../components/CandidateActionNotesModal"
import CandidateJobRowActions from "../components/CandidateJobRowActions"
import JobDetailModal from "../components/JobDetailModal"
import { useCandidateJobActions } from "../hooks/useCandidateJobActions"
import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
import api from "../lib/api"
import {
  analysisTimeScoreForJob,
  buildJobListRubricColumnsForGroup,
  formatGradeDotTooltip,
  groupJobsByAlignedRubric,
  RUBRIC_DEFAULT_IMPORTANCE,
  type JobListRubricColumn,
} from "../lib/rubricDisplay"
import Time from "../components/Time"

interface Job {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  latest_score?: number | null
  /** API: PASSED_* job not claimable until latest_score >= dispatch score_floor */
  virtual_skip?: boolean
  dispatch_score_floor?: number | null
  [key: string]: unknown
}

interface SortState { col: string; asc: boolean }

const GRADE_ORDER: Record<string, number> = { A: 0, B: 1, C: 2, D: 3, F: 4, X: 5 }

function gradeDot(grade: string, tooltip: string) {
  return <span className={`grade-dot dot-${grade.toLowerCase()}`} title={tooltip || undefined}>{grade}</span>
}

function normalizeVectorName(value: string): string {
  return value.replace(/\s*\([A-Z]{2}\)\s*$/, "").trim().toLowerCase()
}

interface GradeCell {
  grade: string
  confidence?: number
  gradeTooltip: string
}

// Match grade by code OR full label — job grades may store either depending on pipeline version
function gradeAndConfidenceForCol(job: Job, gradeKey: string, col: JobListRubricColumn): GradeCell {
  const g = job[gradeKey]
  if (!g) return { grade: "", gradeTooltip: "" }
  const colCode = normalizeVectorName(col.code)
  const colLabel = normalizeVectorName(col.label)
  if (Array.isArray(g)) {
    const row = (g as Array<{ vector: string; grade: string; confidence?: number; reason?: string }>).find(i => {
      const vector = normalizeVectorName(i.vector || "")
      return vector === colCode || vector === colLabel
    })
    if (!row) return { grade: "", gradeTooltip: "" }
    const grade = row.grade || ""
    return {
      grade,
      confidence: row.confidence,
      gradeTooltip: formatGradeDotTooltip(col, grade, row.reason, row.confidence),
    }
  }
  if (typeof g === "object") {
    const obj = g as Record<string, string>
    const exact = obj[col.code] || obj[col.label]
    if (exact) return { grade: exact, gradeTooltip: formatGradeDotTooltip(col, exact) }
    for (const [key, value] of Object.entries(obj)) {
      const normalized = normalizeVectorName(key)
      if (normalized === colCode || normalized === colLabel) {
        return { grade: value, gradeTooltip: formatGradeDotTooltip(col, value) }
      }
    }
  }
  return { grade: "", gradeTooltip: "" }
}

function gradeForCol(job: Job, gradeKey: string, col: JobListRubricColumn): string {
  return gradeAndConfidenceForCol(job, gradeKey, col).grade
}

function sortJobs(jobs: Job[], col: string, asc: boolean, gradeKey: string, cols: JobListRubricColumn[]): Job[] {
  return [...jobs].sort((a, b) => {
    let cmp = 0
    if (col === "job_title") {
      cmp = (a.job_title || "").localeCompare(b.job_title || "")
    } else if (col === "company") {
      cmp = a.company.localeCompare(b.company)
    } else if (col === "state_changed_at") {
      cmp = (a.state_changed_at || "").localeCompare(b.state_changed_at || "")
    } else if (col === "latest_score") {
      const av = analysisTimeScoreForJob(a as Record<string, unknown>, gradeKey)
      const bv = analysisTimeScoreForJob(b as Record<string, unknown>, gradeKey)
      if (av === null && bv === null) cmp = 0
      else if (av === null) cmp = 1
      else if (bv === null) cmp = -1
      else cmp = av - bv
    } else if (col === "state") {
      cmp = (a.state || "").localeCompare(b.state || "")
    } else {
      const header = cols.find(c => c.code === col) ?? {
        code: col, label: col, importance: RUBRIC_DEFAULT_IMPORTANCE, headerCode: col, headerTooltip: col, gradeDescriptions: {},
      }
      const ao = GRADE_ORDER[gradeForCol(a, gradeKey, header)] ?? 99
      const bo = GRADE_ORDER[gradeForCol(b, gradeKey, header)] ?? 99
      cmp = ao - bo
    }
    return asc ? cmp : -cmp
  })
}

export default function Skipped() {
  const { manifest, loadState } = useStateUi()
  const { selectedId } = useCandidate()
  const [rows, setRows]     = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingId, setViewingId] = useState<string | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [sorts, setSorts]   = useState<Record<string, SortState>>({})
  const [toast, setToast]   = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  const load = useCallback(() => {
    if (!selectedId) return
    setLoading(true)
    api(`/api/jobs?view=skipped&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => r.json())
      .then(data => { setRows(Array.isArray(data) ? data : []); setSelected(new Set()) })
      .finally(() => setLoading(false))
  }, [selectedId])

  const actions = useCandidateJobActions(load)

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (actions.error) setToast({ text: actions.error, variant: "error" })
  }, [actions.error])

  const sections = useMemo(() => {
    if (!manifest) return []
    const sk = manifest.jobs.skipped
    const belowKey = sk.below_dispatch_key
    const floorJobs = rows.filter(j => j.virtual_skip)
    const rest = rows.filter(j => !j.virtual_skip)
    const byState: Record<string, Job[]> = {}
    for (const job of rest) {
      if (!byState[job.state]) byState[job.state] = []
      byState[job.state].push(job)
    }
    const order = sk.section_order
    const labels = sk.section_labels
    const gradeMap = manifest.jobs.grade_field_by_job_state
    const knownStates = [sk.below_dispatch_key, ...order]
    const normal = order.filter(s => byState[s]?.length).map(s => ({
      state: s,
      label: labels[s] || s,
      jobs: byState[s],
      gradeKey: gradeMap[s] || "",
    }))
    const legacyStates = unmappedJobStates(rest, knownStates)
    const legacy = legacyStates.filter(s => byState[s]?.length).map(s => ({
      state: s,
      label: legacyStateSectionLabel(s),
      jobs: byState[s],
      gradeKey: gradeMap[s] || "",
    }))
    const withLegacy = [...normal, ...legacy]
    if (!floorJobs.length) return withLegacy
    return [{
      state: belowKey,
      label: sk.below_dispatch_label,
      jobs: floorJobs,
      gradeKey: "",
    }, ...withLegacy]
  }, [rows, manifest])

  const sectionKeys = useMemo(() => sections.map(s => s.state), [sections])
  const { isExpanded, onExpandedChange, setExpandedKeys } = useSectionExpandPolicy({ sectionKeys })
  useEffect(() => { setExpandedKeys(new Set()) }, [selectedId, setExpandedKeys])

  const toggleSelect = (id: string) => setSelected(prev => {
    const next = new Set(prev)
    if (next.has(id)) next.delete(id); else next.add(id)
    return next
  })

  function handleSort(sortKey: string, col: string) {
    setSorts(prev => {
      const cur = prev[sortKey] ?? { col: "state_changed_at", asc: false }
      return { ...prev, [sortKey]: { col, asc: cur.col === col ? !cur.asc : true } }
    })
  }

  function sortIndicator(sortKey: string, col: string) {
    const s = sorts[sortKey]
    return s?.col === col ? <span style={{ fontSize: 10, marginLeft: 3 }}>{s.asc ? "▲" : "▼"}</span> : null
  }

  const handleRetry = () => {
    if (!selected.size) return
    const retryMap = manifest!.jobs.skipped.bulk_retry_to_state_by_from_state
    // One POST per destination so mixed-family selections stay hop-correct.
    const byDest = new Map<string, string[]>()
    for (const id of selected) {
      const fromState = rows.find(r => r.astral_job_id === id)?.state
      if (!fromState) continue
      const toState = retryMap[fromState]
      if (!toState) continue
      const bucket = byDest.get(toState) ?? []
      bucket.push(id)
      byDest.set(toState, bucket)
    }
    if (byDest.size === 0) {
      setToast({ text: "No retryable jobs in selection", variant: "error" })
      return
    }
    ;(async () => {
      try {
        let total = 0
        for (const [to_state, astral_job_ids] of byDest) {
          const r = await api("/api/jobs/bulk_state", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ astral_job_ids, to_state }),
          })
          const res = await r.json()
          total += Number(res.updated) || 0
        }
        if (total === 0) {
          setToast({ text: "Retry failed", variant: "error" })
        } else {
          setToast({ text: `${total} jobs queued for retry`, variant: "success" })
        }
        load()
      } catch {
        setToast({ text: "Retry failed", variant: "error" })
      }
    })()
  }

  return (
    <div className="page-container">
      <div className="list-page-header">
        <h1 className="list-page-title">Skipped</h1>
        {selected.size > 0 && (
          <button className="btn primary" onClick={handleRetry}>Retry ({selected.size})</button>
        )}
      </div>
      {loading ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "loading" ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "error" || !manifest ? (
        <div className="list-page-status">State UI manifest unavailable.</div>
      ) : sections.length === 0 ? (
        <div className="list-page-status">No skipped jobs</div>
      ) : (
        sections.map(sec => {
          const sectionOpen = isExpanded(sec.state)
          const isFloor = sec.state === manifest.jobs.skipped.below_dispatch_key
          // Floor: single table, no rubric grouping. Grade sections: one table per aligned rubric.
          const groups = (!isFloor && sec.gradeKey)
            ? groupJobsByAlignedRubric(sec.jobs as Array<Record<string, unknown>>, sec.gradeKey)
            : [{ fingerprint: sec.state, jobs: sec.jobs as Array<Record<string, unknown>>, columnSourceJob: (sec.jobs[0] ?? {}) as Record<string, unknown> }]
          return (
            <div key={sec.state} style={{ marginBottom: 24 }}>
              <button
                type="button"
                title={isFloor ? "DB state stays PASSED_*; not claimable until latest_score clears the dispatch task score floor." : undefined}
                onClick={() => onExpandedChange(sec.state, !sectionOpen)}
                style={{
                  background: "none", border: "none", cursor: "pointer", width: "100%",
                  display: "flex", alignItems: "center", gap: 8, padding: "8px 0",
                  color: "var(--text-primary)", fontSize: 15, fontWeight: 600, fontFamily: "inherit",
                }}
              >
                <span style={{ transform: sectionOpen ? "rotate(0deg)" : "rotate(-90deg)", transition: "transform 0.15s", fontSize: 12 }}>&#9660;</span>
                {sec.label} ({sec.jobs.length})
              </button>
              {sectionOpen && groups.map(group => {
                const sortKey = `${sec.state}::${group.fingerprint}`
                const cols = (!isFloor && sec.gradeKey)
                  ? buildJobListRubricColumnsForGroup({ gradeKey: sec.gradeKey, columnSourceJob: group.columnSourceJob })
                  : []
                const sort = sorts[sortKey] ?? { col: "state_changed_at", asc: false }
                const sorted = sortJobs(group.jobs as Job[], sort.col, sort.asc, sec.gradeKey, cols)
                const showScore = isFloor
                  || group.jobs.some(j => analysisTimeScoreForJob(j, sec.gradeKey) != null)
                return (
                <div key={sortKey} className="list-page-table-wrap" style={{ marginBottom: groups.length > 1 ? 12 : 0 }}>
                  <table className="list-page-table">
                    <thead>
                      <tr>
                        {!isFloor && <th style={{ width: 1, whiteSpace: "nowrap" }}>Actions</th>}
                        {!isFloor && <th style={{ width: 32 }}></th>}
                        {isFloor && <th style={{ width: 32 }} aria-hidden />}
                        <th className="sortable" onClick={() => handleSort(sortKey, "job_title")}>
                          Job Title{sortIndicator(sortKey, "job_title")}
                        </th>
                        <th className="sortable" onClick={() => handleSort(sortKey, "company")}>
                          Company{sortIndicator(sortKey, "company")}
                        </th>
                        {isFloor && (
                          <>
                            <th className="sortable" style={{ textAlign: "center", minWidth: 88 }} onClick={() => handleSort(sortKey, "state")}>
                              State{sortIndicator(sortKey, "state")}
                            </th>
                            <th className="sortable" style={{ textAlign: "center", minWidth: 56 }} onClick={() => handleSort(sortKey, "latest_score")}>
                              Score{sortIndicator(sortKey, "latest_score")}
                            </th>
                            <th style={{ textAlign: "center", minWidth: 56 }}>Floor</th>
                          </>
                        )}
                        {!isFloor && cols.map(c => (
                          <th key={c.code} className="sortable" title={c.headerTooltip}
                            style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}
                            onClick={() => handleSort(sortKey, c.code)}>
                            {c.headerCode}{sortIndicator(sortKey, c.code)}
                          </th>
                        ))}
                        {!isFloor && showScore && (
                          <th className="sortable" style={{ textAlign: "center", minWidth: 60 }}
                            onClick={() => handleSort(sortKey, "latest_score")}>
                            Score{sortIndicator(sortKey, "latest_score")}
                          </th>
                        )}
                        <th className="sortable" onClick={() => handleSort(sortKey, "state_changed_at")}>
                          {isFloor ? "Updated" : "Failed At"}{sortIndicator(sortKey, "state_changed_at")}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {sorted.map(job => {
                        const rowScore = analysisTimeScoreForJob(job as Record<string, unknown>, isFloor ? "" : sec.gradeKey)
                        return (
                        <tr key={job.astral_job_id} className="clickable">
                          {!isFloor && (
                            <td>
                              <CandidateJobRowActions
                                state={job.state}
                                onResurrect={() => actions.requestAction(job.astral_job_id, "review")}
                                onAction={a => actions.requestAction(job.astral_job_id, a)}
                              />
                            </td>
                          )}
                          {!isFloor && (
                            <td onClick={e => e.stopPropagation()}>
                              <input type="checkbox" checked={selected.has(job.astral_job_id)} onChange={() => toggleSelect(job.astral_job_id)} />
                            </td>
                          )}
                          {isFloor && <td aria-hidden />}
                          <td onClick={() => setViewingId(job.astral_job_id)}>{job.job_title || "\u2014"}</td>
                          <td onClick={() => setViewingId(job.astral_job_id)}>{job.company}</td>
                          {isFloor && (
                            <>
                              <td style={{ textAlign: "center", whiteSpace: "nowrap" }} onClick={() => setViewingId(job.astral_job_id)}>{job.state}</td>
                              <td style={{ textAlign: "center" }} onClick={() => setViewingId(job.astral_job_id)}>
                                {rowScore != null ? rowScore.toFixed(2) : "\u2014"}
                              </td>
                              <td style={{ textAlign: "center" }} onClick={() => setViewingId(job.astral_job_id)}>
                                {job.dispatch_score_floor != null && job.dispatch_score_floor !== undefined
                                  ? (job.dispatch_score_floor as number).toFixed(2)
                                  : "\u2014"}
                              </td>
                            </>
                          )}
                          {!isFloor && cols.map(c => {
                            const cell = gradeAndConfidenceForCol(job, sec.gradeKey, c)
                            return (
                              <td key={c.code} style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }} onClick={() => setViewingId(job.astral_job_id)}>
                                {cell.grade ? (
                                  <div className="analysis-grade-block">
                                    {gradeDot(cell.grade, cell.gradeTooltip)}
                                    <ConfidenceBullets confidence={cell.confidence} />
                                  </div>
                                ) : (
                                  "\u2014"
                                )}
                              </td>
                            )
                          })}
                          {!isFloor && showScore && (
                            <td style={{ textAlign: "center" }} onClick={() => setViewingId(job.astral_job_id)}>
                              {rowScore != null ? rowScore.toFixed(2) : "\u2014"}
                            </td>
                          )}
                          <td onClick={() => setViewingId(job.astral_job_id)}><Time value={job.state_changed_at} /></td>
                        </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
                )
              })}
            </div>
          )
        })
      )}
      <JobDetailModal jobId={viewingId} onClose={() => { setViewingId(null); load() }} />
      <CandidateActionNotesModal
        open={!!actions.pending}
        action={actions.pending?.action ?? null}
        busy={actions.busy}
        onClose={actions.closePending}
        onConfirm={actions.confirmPending}
      />
      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
