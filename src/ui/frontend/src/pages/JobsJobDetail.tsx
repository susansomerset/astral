import { Navigate, useParams } from "react-router-dom"

/** AST-1481: deeplink host — opens JobAnalysisReportModal for /jobs/detail/:jobId */
export default function JobsJobDetail() {
  const { jobId: rawJobId } = useParams()
  const jobId = rawJobId?.trim() ?? ""

  if (!jobId) {
    return <Navigate to="/jobs/recommended" replace />
  }

  return <p className="list-page-status">Loading job…</p>
}
