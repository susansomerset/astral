import { Fragment, useEffect, useMemo, useState } from "react"
import Modal from "./Modal"
import JobDetailModal from "./JobDetailModal"
import Time from "./Time"
import JobTitleText from "./JobTitleText"
import PhaseAnalysisLines from "./PhaseAnalysisLines"
import { useStateUi } from "../contexts/StateUiContext"
import { buildPhaseListGradeRow } from "../lib/recommendedJobReport"
import api from "../lib/api"

interface WatchJobRow {
  astral_job_id: string
  job_title?: string | null
  state?: string | null
  state_changed_at?: string | null
  [key: string]: unknown
}

interface Props {
  shortName: string
  bucket: string
  bucketLabel: string
  candidateId: string
  onClose: () => void
}

const PHASE_GRADE_KEYS = ["jd_grades", "do_grades", "get_grades", "like_grades", "joblist_grades"] as const

function hasPhaseGrades(job: WatchJobRow): boolean {
  return PHASE_GRADE_KEYS.some(k => {
    const v = job[k]
    if (v == null) return false
    if (Array.isArray(v)) return v.length > 0
    if (typeof v === "object") return Object.keys(v as object).length > 0
    return true
  })
}

/** Title-case state for all-jobs group headers: FAILED_JOBLIST → Failed Joblist. */
function titleCaseState(state: string): string {
  return state
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase())
}

/** Sync grade-dot fallback before StateUi manifest resolves (PhaseAnalysisLines needs it). */
function SyncPhaseGradeDots({ job }: { job: WatchJobRow }) {
  return (
    <div className="recommended-analysis-lines">
      {(["jd_grades", "do_grades", "get_grades", "like_grades"] as const).map(field => {
        const dots = buildPhaseListGradeRow(job, field)
        if (!dots) return null
        return (
          <div key={field} className="recommended-analysis-line">
            {dots}
          </div>
        )
      })}
    </div>
  )
}

/** Mount only while a bucket is selected (parent keys remounts). Initial loading=true avoids sync setState in effect. */
export default function CompanyWatchJobsModal({
  shortName,
  bucket,
  bucketLabel,
  candidateId,
  onClose,
}: Props) {
  const { loadState } = useStateUi()
  const [jobs, setJobs] = useState<WatchJobRow[]>([])
  const [loading, setLoading] = useState(true)
  const [jobId, setJobId] = useState<string | null>(null)
  const allMode = bucket === "all"

  useEffect(() => {
    let cancelled = false
    api(
      `/api/companies/${encodeURIComponent(shortName)}/jobs`
        + `?bucket=${encodeURIComponent(bucket)}`
        + `&candidate_id=${encodeURIComponent(candidateId)}`,
    )
      .then(async r => (r.ok ? (await r.json()) : []))
      .then(data => {
        if (!cancelled) setJobs(Array.isArray(data) ? data : [])
      })
      .catch(() => {
        if (!cancelled) setJobs([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [shortName, bucket, candidateId])

  // all mode: group by state ascending; within group keep API order
  const grouped = useMemo(() => {
    if (!allMode) return null
    const map = new Map<string, WatchJobRow[]>()
    for (const row of jobs) {
      const key = String(row.state ?? "")
      const list = map.get(key)
      if (list) list.push(row)
      else map.set(key, [row])
    }
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b))
  }, [allMode, jobs])

  function handleClose() {
    setJobId(null)
    onClose()
  }

  function renderJobRow(row: WatchJobRow) {
    const graded = hasPhaseGrades(row)
    return (
      <tr
        key={row.astral_job_id}
        className="clickable recommended-analysis-row"
        onClick={() => setJobId(row.astral_job_id)}
      >
        <td>
          <span className="dispatch-batch-link">
            <JobTitleText title={row.job_title ?? null} fallback="—" />
          </span>
          {graded && (
            loadState === "ready"
              ? <PhaseAnalysisLines job={row} />
              : <SyncPhaseGradeDots job={row} />
          )}
        </td>
        <td><Time value={row.state_changed_at as string | null | undefined} /></td>
      </tr>
    )
  }

  return (
    <>
      <Modal
        open
        onClose={handleClose}
        title={`${bucketLabel} — ${shortName}`}
        showFooter={false}
      >
        {loading && <p className="entity-loading">Loading…</p>}
        {!loading && jobs.length === 0 && (
          <p className="list-page-status">No jobs in this bucket.</p>
        )}
        {!loading && jobs.length > 0 && (
          <table className="list-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Changed</th>
              </tr>
            </thead>
            <tbody>
              {allMode && grouped
                ? grouped.map(([state, rows]) => (
                    <Fragment key={`grp:${state}`}>
                      <tr>
                        <td colSpan={2}>{titleCaseState(state || "—")}</td>
                      </tr>
                      {rows.map(renderJobRow)}
                    </Fragment>
                  ))
                : jobs.map(renderJobRow)}
            </tbody>
          </table>
        )}
      </Modal>
      <JobDetailModal
        jobId={jobId}
        onClose={() => setJobId(null)}
        stacked
      />
    </>
  )
}
