import { useEffect, useRef, useState } from "react"
import { Link, Navigate, useNavigate, useParams } from "react-router-dom"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import { useAuth } from "../contexts/AuthContext"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

type Gate = "loading" | "ready" | "error"

/** AST-1481: deeplink host — opens JobAnalysisReportModal for /jobs/detail/:jobId */
export default function JobsJobDetail() {
  const navigate = useNavigate()
  const { isAdmin } = useAuth()
  const { jobId: rawJobId } = useParams()
  const jobId = rawJobId?.trim() ?? ""
  const { alignSelectedCandidateForJobCompany, candidatesHydrated } = useCandidate()
  const alignRef = useRef(alignSelectedCandidateForJobCompany)
  alignRef.current = alignSelectedCandidateForJobCompany
  const readyJobIdRef = useRef<string | null>(null)
  const [gate, setGate] = useState<Gate>("loading")
  const [gateError, setGateError] = useState<string | null>(null)
  // undefined = job prefetch in flight; string = fetched (may be empty)
  const [company, setCompany] = useState<string | undefined>(undefined)

  useEffect(() => {
    if (!jobId) return
    let cancelled = false
    readyJobIdRef.current = null
    setGate("loading")
    setGateError(null)
    setCompany(undefined)
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
      const co = typeof data.company === "string" ? data.company.trim() : ""
      setCompany(co)
    })()
    return () => { cancelled = true }
  }, [jobId])

  useEffect(() => {
    if (!jobId || company === undefined) return
    if (isAdmin && !candidatesHydrated) return
    if (readyJobIdRef.current === jobId) return
    let cancelled = false
    void (async () => {
      if (company) {
        await alignRef.current(company)
      }
      if (!cancelled) {
        readyJobIdRef.current = jobId
        setGate("ready")
      }
    })()
    return () => { cancelled = true }
  }, [jobId, company, isAdmin, candidatesHydrated])

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
