import { useEffect, useState } from "react"
import Modal from "./Modal"
import JobDetailModal from "./JobDetailModal"
import Time from "./Time"
import JobTitleText from "./JobTitleText"
import api from "../lib/api"

interface WatchJobRow {
  astral_job_id: string
  job_title?: string | null
  state?: string | null
  state_changed_at?: string | null
}

interface Props {
  shortName: string
  bucket: string
  bucketLabel: string
  candidateId: string
  onClose: () => void
}

/** Mount only while a bucket is selected (parent keys remounts). Initial loading=true avoids sync setState in effect. */
export default function CompanyWatchJobsModal({
  shortName,
  bucket,
  bucketLabel,
  candidateId,
  onClose,
}: Props) {
  const [jobs, setJobs] = useState<WatchJobRow[]>([])
  const [loading, setLoading] = useState(true)
  const [jobId, setJobId] = useState<string | null>(null)

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

  function handleClose() {
    setJobId(null)
    onClose()
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
                <th>State</th>
                <th>Changed</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(row => (
                <tr
                  key={row.astral_job_id}
                  className="clickable"
                  onClick={() => setJobId(row.astral_job_id)}
                >
                  <td>
                    <JobTitleText title={row.job_title ?? null} fallback="—" />
                  </td>
                  <td>{row.state || "—"}</td>
                  <td><Time value={row.state_changed_at} /></td>
                </tr>
              ))}
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
