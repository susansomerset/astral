import { useCallback, useEffect, useMemo, useState } from "react"
import Modal from "./Modal"
import RecommendedJobReportHeader from "./RecommendedJobReportHeader"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import { TabBar } from "./TabbedTextArea"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import {
  emailWithJobPlusTag,
  primaryActionsForState,
  printCoverVisible,
  printResumeVisible,
  type ReportPrimaryAction,
} from "../lib/recommendedJobReport"

interface JobDetail {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  job_link?: string | null
  job_data?: Record<string, unknown>
  jd_grades?: unknown
  do_grades?: unknown
  get_grades?: unknown
  like_grades?: unknown
}

interface Props {
  jobId: string | null
  onClose: () => void
  onRefresh?: () => void
}

/** AST-948: horizontal-tab Recommended Job Report shell (section bodies = siblings). */
export default function JobAnalysisReportModal({ jobId, onClose, onRefresh }: Props) {
  const { manifest } = useStateUi()
  const { selectedId, candidates } = useCandidate()
  const [job, setJob] = useState<JobDetail | null>(null)
  const [companyWebsite, setCompanyWebsite] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [primaryBusy, setPrimaryBusy] = useState(false)
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null)
  const [activeTopTab, setActiveTopTab] = useState("summary")

  const candidate = useMemo(
    () => candidates.find(c => c.astral_candidate_id === selectedId),
    [candidates, selectedId],
  )

  const load = useCallback(async () => {
    if (!jobId) return
    setLoading(true)
    setError(null)
    setCompanyWebsite(null)
    try {
      const res = await api(`/api/jobs/${encodeURIComponent(jobId)}`)
      if (!res.ok) throw new Error("Job not found")
      const data = (await res.json()) as JobDetail
      setJob(data)
      if (data.company) {
        api(`/api/companies/${encodeURIComponent(data.company)}`)
          .then(r => (r.ok ? r.json() : null))
          .then(co => {
            const site = co?.company_website
            setCompanyWebsite(typeof site === "string" && site.trim() ? site.trim() : null)
          })
          .catch(() => setCompanyWebsite(null))
      }
    } catch (e) {
      setJob(null)
      setError(e instanceof Error ? e.message : "Load failed")
    } finally {
      setLoading(false)
    }
  }, [jobId])

  useEffect(() => { load() }, [load])

  // Reset top tab when opening a different job.
  useEffect(() => {
    setActiveTopTab("summary")
  }, [jobId])

  const topTabs = useMemo(() => {
    const rows = manifest?.jobs.recommended.report_top_tabs ?? []
    return rows.map(r => ({ key: r.tab_id, label: r.nav_label }))
  }, [manifest])

  useEffect(() => {
    if (topTabs.length === 0) return
    if (!topTabs.some(t => t.key === activeTopTab)) {
      setActiveTopTab(topTabs[0].key)
    }
  }, [topTabs, activeTopTab])

  const summarySections = useMemo((): ReportSectionDef[] => {
    return (manifest?.jobs.recommended.report_summary_sections ?? []).map(s => ({
      section_id: s.section_id,
      nav_label: s.nav_label,
      default_expanded: s.default_expanded,
    }))
  }, [manifest])

  const analysisSections = useMemo((): ReportSectionDef[] => {
    return (manifest?.jobs.recommended.report_phase_tabs ?? []).map(p => ({
      section_id: p.tab_id,
      nav_label: p.nav_label,
      default_expanded: p.tab_id === "phase_jd",
    }))
  }, [manifest])

  const artifactSections = useMemo((): ReportSectionDef[] => {
    return (manifest?.jobs.recommended.report_artifact_tabs ?? []).map(a => ({
      section_id: a.tab_id,
      nav_label: a.nav_label,
      default_expanded: false,
    }))
  }, [manifest])

  const artifactStripActions = useMemo((): ReportPrimaryAction[] => {
    if (!job) return []
    return primaryActionsForState(manifest, job.state).filter(a => a.action_key !== "apply")
  }, [manifest, job])

  const profile = useMemo(() => {
    const raw = (candidate?.candidate_data as Record<string, unknown> | undefined)?.profile
    if (!raw || typeof raw !== "object") return null
    return raw as Record<string, unknown>
  }, [candidate])

  const applicationEmail = useMemo(() => {
    if (!profile) return null
    for (const key of ["contact_email", "reply_email"] as const) {
      const v = profile[key]
      if (typeof v === "string" && v.trim()) return v.trim()
    }
    return null
  }, [profile])

  const linkedInUrl = useMemo(() => {
    const v = profile?.linkedin_url
    return typeof v === "string" && v.trim() ? v.trim() : null
  }, [profile])

  const artifacts = job?.job_data?.artifacts
  const showPrintResume = printResumeVisible(artifacts)
  const showPrintCover = printCoverVisible(artifacts)

  const emailPlusTag = useMemo(() => {
    if (!job) return jobId ?? ""
    const jd = job.job_data
    const ext =
      jd && typeof jd === "object" && !Array.isArray(jd)
        ? (jd as Record<string, unknown>).external_job_id
        : undefined
    if (typeof ext === "string" && ext.trim()) return ext.trim()
    return job.astral_job_id || jobId || ""
  }, [job, jobId])

  async function runPrimaryAction(action: ReportPrimaryAction) {
    if (!jobId || !job || primaryBusy) return
    setPrimaryBusy(true)
    setError(null)
    try {
      if (action.method === "CLIENT") {
        if (job.job_link) window.open(job.job_link, "_blank", "noopener,noreferrer")
        return
      }
      const path = `/api/jobs/${encodeURIComponent(jobId)}/${action.path_suffix}`
      const res = await api(path, { method: "POST" })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }))
        throw new Error(err.error || "Action failed")
      }
      onRefresh?.()
      // AST-591: after explicit build start/cancel, return to list.
      if (action.action_key === "generate_artifacts" || action.action_key === "cancel_build") {
        onClose()
        return
      }
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action failed")
    } finally {
      setPrimaryBusy(false)
    }
  }

  function handleCopyApplicationEmail() {
    if (!applicationEmail) return
    const text = emailWithJobPlusTag(applicationEmail, emailPlusTag)
    navigator.clipboard.writeText(text).then(() => {
      setCopyFeedback("Copied")
      window.setTimeout(() => setCopyFeedback(null), 2000)
    })
  }

  function handleCopyLinkedIn() {
    if (!linkedInUrl) return
    navigator.clipboard.writeText(linkedInUrl).then(() => {
      setCopyFeedback("Copied")
      window.setTimeout(() => setCopyFeedback(null), 2000)
    })
  }

  const jobTitleDisplay = job?.job_title?.trim() || job?.company || "Recommended Job Report"

  const artifactsLeading =
    artifactStripActions.length > 0 ? (
      <div className="recommended-report-artifacts-actions">
        {artifactStripActions.map(action => (
          <button
            key={action.action_key}
            type="button"
            className={`modal-btn save${primaryBusy ? " in-flight" : ""}`}
            disabled={primaryBusy}
            onClick={() => runPrimaryAction(action)}
          >
            {primaryBusy ? "Working…" : action.label}
          </button>
        ))}
      </div>
    ) : undefined

  return (
    <Modal
      open={!!jobId}
      onClose={onClose}
      title={job?.company || "Recommended Job Report"}
      size="wide"
    >
      {loading && <p className="entity-loading">Loading…</p>}
      {error && <p className="entity-error">{error}</p>}
      {job && !loading && (
        <div className="recommended-report-shell">
          <div className="recommended-report-chrome">
            <RecommendedJobReportHeader
              jobTitle={jobTitleDisplay}
              jobLink={job.job_link ?? null}
              companyName={job.company}
              companyWebsite={companyWebsite}
              applicationEmail={applicationEmail}
              linkedInUrl={linkedInUrl}
              copyFeedback={copyFeedback}
              onCopyApplicationEmail={handleCopyApplicationEmail}
              onCopyLinkedIn={handleCopyLinkedIn}
              showPrintResume={showPrintResume}
              showPrintCover={showPrintCover}
              onPrintResume={() => {
                if (!jobId) return
                window.open(
                  `/candidate/resume/${encodeURIComponent(jobId)}`,
                  "_blank",
                  "noopener,noreferrer",
                )
              }}
              onPrintCover={() => {
                if (!jobId) return
                window.open(
                  `/candidate/cover/${encodeURIComponent(jobId)}`,
                  "_blank",
                  "noopener,noreferrer",
                )
              }}
            />
            {topTabs.length > 0 ? (
              <div className="recommended-report-tabs">
                <TabBar
                  tabs={topTabs}
                  active={activeTopTab}
                  onChange={setActiveTopTab}
                />
              </div>
            ) : (
              <p className="recommended-report-empty">
                {!manifest?.jobs.recommended
                  ? "Report layout unavailable. Try refreshing the page."
                  : "No report tabs available."}
              </p>
            )}
          </div>
          {topTabs.length > 0 && (
            <div className="recommended-report-tab-pane">
              {activeTopTab === "summary" && (
                <ReportSectionList
                  sections={summarySections}
                  renderSection={() => null}
                />
              )}
              {activeTopTab === "analysis" && (
                <ReportSectionList
                  sections={analysisSections}
                  renderSection={() => null}
                />
              )}
              {activeTopTab === "artifacts" && (
                <ReportSectionList
                  leading={artifactsLeading}
                  sections={artifactSections}
                  renderSection={() => null}
                />
              )}
            </div>
          )}
        </div>
      )}
    </Modal>
  )
}
