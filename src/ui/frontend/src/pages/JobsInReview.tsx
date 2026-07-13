import { useCallback, useEffect, useMemo, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import { legacyStateSectionLabel, unmappedJobStates } from "../lib/stateUiSections"
import { ConfidenceBullets } from "../components/ConfidenceBullets"
import JobDetailModal from "../components/JobDetailModal"
import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
import api from "../lib/api"
import Time from "../components/Time"
import { buildJobListRubricColumns, formatGradeDotTooltip, RUBRIC_DEFAULT_IMPORTANCE, type JobListRubricColumn } from "../lib/rubricDisplay"

interface Job {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  latest_score?: number | null
  [key: string]: unknown
}

interface SortState { col: string; asc: boolean }

// A=0 sorts first ascending, missing/unknown sorts last
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
      gradeTooltip: formatGradeDotTooltip(col, grade, row.reason),
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
      const av = a.latest_score ?? null
      const bv = b.latest_score ?? null
      if (av === null && bv === null) cmp = 0
      else if (av === null) cmp = 1
      else if (bv === null) cmp = -1
      else cmp = av - bv
    } else {
      const header = cols.find(c => c.code === col) ?? { code: col, label: col, importance: RUBRIC_DEFAULT_IMPORTANCE, headerCode: col, headerTooltip: col, gradeDescriptions: {} }
      const ao = GRADE_ORDER[gradeForCol(a, gradeKey, header)] ?? 99
      const bo = GRADE_ORDER[gradeForCol(b, gradeKey, header)] ?? 99
      cmp = ao - bo
    }
    return asc ? cmp : -cmp
  })
}

export default function InReview() {
  const { manifest, loadState } = useStateUi()
  const { selectedId, candidates } = useCandidate()
  const [rows, setRows]     = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingId, setViewingId] = useState<string | null>(null)
  const [sorts, setSorts]   = useState<Record<string, SortState>>({})

  const artifacts = useMemo(() => {
    const c = candidates.find(x => x.astral_candidate_id === selectedId)
    return (c?.candidate_data?.artifacts as Record<string, unknown>) ?? {}
  }, [candidates, selectedId])

  const load = useCallback(() => {
    if (!selectedId) return
    setLoading(true)
    api(`/api/jobs?view=in_review&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { load() }, [load])

  const sections = useMemo(() => {
    if (!manifest) return []
    const byState: Record<string, Job[]> = {}
    for (const job of rows) {
      if (!byState[job.state]) byState[job.state] = []
      byState[job.state].push(job)
    }
    const order = manifest.jobs.in_review_sections.map(r => r.state)
    const labels: Record<string, string> = Object.fromEntries(
      manifest.jobs.in_review_sections.map(r => [r.state, r.label]),
    )
    const gradeMap = manifest.jobs.grade_field_by_job_state
    const knownStates = order
    const normal = order.filter(s => byState[s]?.length).map(s => ({
      state: s,
      label: labels[s] ?? s,
      jobs: byState[s],
      gradeKey: gradeMap[s] || "",
    }))
    const legacyStates = unmappedJobStates(rows, knownStates)
    const legacy = legacyStates.filter(s => byState[s]?.length).map(s => ({
      state: s,
      label: legacyStateSectionLabel(s),
      jobs: byState[s],
      gradeKey: gradeMap[s] || "",
    }))
    return [...normal, ...legacy]
  }, [rows, manifest])

  const sectionKeys = useMemo(() => sections.map(s => s.state), [sections])
  const { isExpanded, onExpandedChange, setExpandedKeys } = useSectionExpandPolicy({ sectionKeys })
  useEffect(() => { setExpandedKeys(new Set()) }, [selectedId, setExpandedKeys])

  function getRubricCols(gradeKey: string, jobs: Job[]): JobListRubricColumn[] {
    const rubricKey = manifest?.jobs.grade_rubric_by_field[gradeKey]
    return buildJobListRubricColumns({
      rubricArtifactKey: rubricKey || undefined,
      artifacts,
      gradeKey,
      jobs: jobs as Array<Record<string, unknown>>,
    })
  }

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
        <h1 className="list-page-title">In Review</h1>
      </div>
      {loading ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "loading" ? (
        <div className="list-page-status">Loading...</div>
      ) : loadState === "error" || !manifest ? (
        <div className="list-page-status">State UI manifest unavailable.</div>
      ) : sections.length === 0 ? (
        <div className="list-page-status">No jobs in review</div>
      ) : (
        sections.map(sec => {
          const sectionOpen = isExpanded(sec.state)
          const cols = sec.gradeKey ? getRubricCols(sec.gradeKey, sec.jobs) : []
          const sort = sorts[sec.state] ?? { col: "state_changed_at", asc: false }
          const sorted = sortJobs(sec.jobs, sort.col, sort.asc, sec.gradeKey, cols)
          // Match grade-dot sections: always show Score when we show rubric columns (e.g. Passed Job List uses latest_score from qualify).
          const showScore = Boolean(sec.gradeKey)
          return (
            <div key={sec.state} style={{ marginBottom: 24 }}>
              <button
                type="button"
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
              {sectionOpen && (
                <div className="list-page-table-wrap">
                  <table className="list-page-table">
                    <thead>
                      <tr>
                        <th className="sortable" onClick={() => handleSort(sec.state, "job_title")}>
                          Job Title{sortIndicator(sec.state, "job_title")}
                        </th>
                        <th className="sortable" onClick={() => handleSort(sec.state, "company")}>
                          Company{sortIndicator(sec.state, "company")}
                        </th>
                        {cols.map(c => (
                          <th key={c.code} className="sortable" title={c.headerTooltip}
                            style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}
                            onClick={() => handleSort(sec.state, c.code)}>
                            {c.headerCode}{sortIndicator(sec.state, c.code)}
                          </th>
                        ))}
                        {showScore && (
                          <th className="sortable" style={{ textAlign: "center", minWidth: 60 }}
                            onClick={() => handleSort(sec.state, "latest_score")}>
                            Score{sortIndicator(sec.state, "latest_score")}
                          </th>
                        )}
                        <th className="sortable" onClick={() => handleSort(sec.state, "state_changed_at")}>
                          Updated{sortIndicator(sec.state, "state_changed_at")}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {sorted.map(job => (
                        <tr key={job.astral_job_id} className="clickable" onClick={() => setViewingId(job.astral_job_id)}>
                          <td>{job.job_title || "\u2014"}</td>
                          <td>{job.company}</td>
                          {cols.map(c => {
                            const cell = gradeAndConfidenceForCol(job, sec.gradeKey, c)
                            return (
                              <td key={c.code} style={{ textAlign: "center", whiteSpace: "nowrap", width: 1 }}>
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
                          {showScore && (
                            <td style={{ textAlign: "center" }}>
                              {job.latest_score != null ? (job.latest_score as number).toFixed(2) : "\u2014"}
                            </td>
                          )}
                          <td><Time value={job.state_changed_at} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )
        })
      )}
      <JobDetailModal jobId={viewingId} onClose={() => { setViewingId(null); load() }} />
    </div>
  )
}
