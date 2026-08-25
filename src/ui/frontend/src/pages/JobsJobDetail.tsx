import { useEffect, useState } from "react"
import { Link, Navigate, useNavigate, useParams } from "react-router-dom"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

type Gate = "loading" | "ready" | "error"

/** AST-1481: deeplink host — opens JobAnalysisReportModal for /jobs/detail/:jobId */
export default function JobsJobDetail() {
  const navigate = useNavigate()
  const { jobId: rawJobId } = useParams()
  const jobId = rawJobId?.trim() ?? ""
  const { alignSelectedCandidateForJobCompany } = useCandidate()
  const [gate, setGate] = useState<Gate>("loading")
  const [gateError, setGateError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) return
    let cancelled = false
    setGate("loading")
    setGateError(null)
    void (async () => {
      const res = await api(`/api/jobs/${encodeURIComponent(jobId)}`)
      if (cancelled) return
      if (res.status === 404) {
        setGate("error")
        setGateError("Job not found")
        return
      }
      if (!res.ok) {
        const errBody = (await res.json().catch(() => ({}))) as { error?: string }
        const msg =
          typeof errBody.error === "string" && errBody.error.trim()
            ? errBody.error.trim()
            : `Load failed (HTTP ${res.status})`
        setGate("error")
        setGateError(msg)
        return
      }
      const data = (await res.json()) as { company?: unknown }
      const company = typeof data.company === "string" ? data.company.trim() : ""
      if (company) {
        await alignSelectedCandidateForJobCompany(company)
      }
      if (cancelled) return
      setGate("ready")
    })()
    return () => { cancelled = true }
  }, [jobId, alignSelectedCandidateForJobCompany])

  if (!jobId) {
    return <Navigate to="/jobs/recommended" replace />
  }

  if (gate === "loading") {
    return (
      <div className="page-container">
        <p className="list-page-status">Loading job…</p>
      </div>
    )
  }

  if (gate === "error") {
    return (
      <div className="page-container">
        <h1 className="list-page-title">Job unavailable</h1>
        <p className="entity-error">{gateError}</p>
        <Link to="/jobs/recommended" className="btn secondary">Back to Recommended</Link>
      </div>
    )
  }

  return (
    <JobAnalysisReportModal
      jobId={jobId}
      onClose={() => navigate("/jobs/recommended")}
    />
  )
}
