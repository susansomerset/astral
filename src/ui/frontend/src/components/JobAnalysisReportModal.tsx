import { useCallback, useEffect, useMemo, useState } from "react"
import Modal from "./Modal"
import SideTabPanel, { type SideTab } from "./SideTabPanel"
import AgentAnalysisHeader from "./AgentAnalysisHeader"
import ArtifactEditor from "./ArtifactEditor"
import RecommendedJobReportHeader, { type ProfileLink } from "./RecommendedJobReportHeader"
import MaterialsPreviewModal from "./MaterialsPreviewModal"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import { parseAnalysisUpshot, snakeCaseToTitle, type AnalysisUpshot } from "../lib/analysisUpshot"
import {
  artifactHasContent,
  buildPhaseTabGradeDots,
  emailWithJobPlusTag,
  formatPhaseTabNavLabel,
  jobGradesForField,
  materialsPreviewVisible,
  primaryActionsForState,
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

function UpshotStringBlock({ heading, body }: { heading: string; body: string }) {
  const trimmed = body.trim()
  if (!trimmed) return null
  return (
    <div className="job-analysis-upshot-section">
      <p className="job-analysis-upshot-heading">{heading}</p>
      <p className="job-analysis-upshot-body">{trimmed}</p>
    </div>
  )
}

function gradesForHeader(raw: unknown): Array<{ vector: string; grade: string; confidence?: number; reason?: string }> {
  if (!raw) return []
  if (Array.isArray(raw)) {
    return (raw as Array<{ vector?: string; grade?: string; confidence?: number; reason?: string }>)
      .filter(row => row.vector && row.grade)
      .map(row => ({
        vector: row.vector!,
        grade: row.grade!,
        confidence: row.confidence,
        reason: row.reason,
      }))
  }
  if (typeof raw === "object") {
    return Object.entries(raw as Record<string, string>).map(([vector, grade]) => ({ vector, grade }))
  }
  return []
}

/** AST-565: tabbed Recommended Job Report modal */
export default function JobAnalysisReportModal({ jobId, onClose, onRefresh }: Props) {
  const { manifest } = useStateUi()
  const { selectedId, candidates } = useCandidate()
  const [job, setJob] = useState<JobDetail | null>(null)
  const [companyWebsite, setCompanyWebsite] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [primaryBusy, setPrimaryBusy] = useState(false)
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [structureSections, setStructureSections] = useState<{ id: string; label: string }[] | null>(null)
  const [structureError, setStructureError] = useState(false)

  const candidate = useMemo(
    () => candidates.find(c => c.astral_candidate_id === selectedId),
    [candidates, selectedId],
  )
  const candidateArtifacts = useMemo(
    () => (candidate?.candidate_data as Record<string, unknown> | undefined)?.artifacts as Record<string, unknown> ?? {},
    [candidate],
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

  useEffect(() => {
    if (!selectedId) {
      setStructureSections(null)
      setStructureError(false)
      return
    }
    setStructureSections(null)
    setStructureError(false)
    api(`/api/candidates/${selectedId}/resume_structure`)
      .then(r => r.json())
      .then(data => {
        const sections = Array.isArray(data.sections) ? data.sections : []
        setStructureSections(sections.map((s: { id: string; label: string }) => ({ id: s.id, label: s.label })))
      })
      .catch(() => {
        setStructureSections(null)
        setStructureError(true)
      })
  }, [selectedId])

  const upshot = useMemo(
    () => parseAnalysisUpshot(job?.job_data?.analysis_upshot),
    [job?.job_data?.analysis_upshot],
  )

  const profileLinks = useMemo((): ProfileLink[] => {
    const profile = (candidate?.candidate_data as Record<string, unknown> | undefined)?.profile
    if (!profile || typeof profile !== "object") return []
    const p = profile as Record<string, unknown>
    const links: ProfileLink[] = []
    const add = (key: string, label: string, raw: unknown, copyable = true) => {
      if (typeof raw === "string" && raw.trim()) links.push({ key, label, value: raw.trim(), copyable })
    }
    add("contact_email", "Email", p.contact_email)
    add("reply_email", "Reply email", p.reply_email)
    add("linkedin_url", "LinkedIn", p.linkedin_url)
    add("github", "GitHub", p.github)
    return links
  }, [candidate])

  const tabs = useMemo((): SideTab[] => {
    const rec = manifest?.jobs.recommended
    if (!rec) return []
    const out: SideTab[] = []
    for (const row of rec.report_fixed_tabs ?? []) {
      out.push({ id: row.tab_id, label: row.nav_label, content: "" })
    }
    if (upshot) {
      for (const row of rec.report_phase_tabs ?? []) {
        out.push({ id: row.tab_id, label: row.nav_label, content: "" })
      }
    }
    const artifacts = job?.job_data?.artifacts
    for (const row of rec.report_artifact_tabs ?? []) {
      if (artifactHasContent(artifacts, row.artifact_key)) {
        out.push({ id: row.tab_id, label: row.nav_label, content: "" })
      }
    }
    return out
  }, [manifest, upshot, job?.job_data?.artifacts])

  const primaryAction: ReportPrimaryAction | null = useMemo(() => {
    if (!job) return null
    const actions = primaryActionsForState(manifest, job.state)
    return actions[0] ?? null
  }, [manifest, job])

  const stateSectionLabel = useMemo(() => {
    if (!job || !manifest) return undefined
    return manifest.jobs.recommended.sections.find(s => s.state === job.state)?.label
  }, [manifest, job])

  const artifacts = job?.job_data?.artifacts
  const showPreview = !!(job && materialsPreviewVisible(job.state, artifacts))
  const hasCover = artifactHasContent(artifacts, "cover_letter")

  async function runPrimaryAction() {
    if (!jobId || !job || !primaryAction || primaryBusy) return
    setPrimaryBusy(true)
    setError(null)
    try {
      if (primaryAction.method === "CLIENT") {
        if (job.job_link) window.open(job.job_link, "_blank", "noopener,noreferrer")
        return
      }
      const path = `/api/jobs/${encodeURIComponent(jobId)}/${primaryAction.path_suffix}`
      const res = await api(path, { method: "POST" })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }))
        throw new Error(err.error || "Action failed")
      }
      onRefresh?.()
      // AST-591: after explicit build start/cancel, return to list (In Progress / Recommended).
      if (
        primaryAction.action_key === "generate_artifacts"
        || primaryAction.action_key === "cancel_artifact_build"
      ) {
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

  function handleCopy(value: string, linkKey?: string) {
    const text =
      linkKey === "contact_email" || linkKey === "reply_email"
        ? emailWithJobPlusTag(value, emailPlusTag)
        : value
    navigator.clipboard.writeText(text).then(() => {
      setCopyFeedback("Copied")
      window.setTimeout(() => setCopyFeedback(null), 2000)
    })
  }

  function renderTabLabel(tab: SideTab) {
    const phase = manifest?.jobs.recommended.report_phase_tabs?.find(p => p.tab_id === tab.id)
    if (!phase || !job) return tab.label
    const gradesRaw = jobGradesForField(job as unknown as Record<string, unknown>, phase.grades_field)
    const rubricKey = manifest?.jobs.grade_rubric_by_field[phase.grades_field]
    const dots = buildPhaseTabGradeDots(gradesRaw, rubricKey, candidateArtifacts)
    return formatPhaseTabNavLabel(phase.nav_label, dots)
  }

  function renderReportPane(tabId: string) {
    if (!job) return null
    const jobData = job.job_data ?? {}
    const parsed = upshot

    if (tabId === "summary") {
      if (!parsed) {
        return <p className="recommended-report-empty">No analysis upshot on file.</p>
      }
      return (
        <div className="job-analysis-upshot">
          <UpshotStringBlock heading="Job Summary" body={parsed.whole_jd_upshot} />
          {parsed.caveats.filter(c => c.text.trim()).length > 0 && (
            <div className="job-analysis-upshot-section">
              <p className="job-analysis-upshot-heading">Noteworthy Caveats</p>
              <ul className="job-analysis-upshot-list">
                {parsed.caveats.filter(c => c.text.trim()).map((c, i) => (
                  <li key={`c-${i}`}>{c.text.trim()}</li>
                ))}
              </ul>
            </div>
          )}
          {parsed.candidate_questions.filter(q => q.text.trim()).length > 0 && (
            <div className="job-analysis-upshot-section">
              <p className="job-analysis-upshot-heading">Questions to Ask</p>
              <ul className="job-analysis-upshot-list">
                {parsed.candidate_questions.filter(q => q.text.trim()).map((q, i) => (
                  <li key={`q-${i}`}>{q.text.trim()}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )
    }

    if (tabId === "jd_full") {
      const jd = String(jobData.job_description ?? "").trim().replace(/\n{3,}/g, "\n\n")
      if (!jd) return <p className="recommended-report-empty">No job description on file.</p>
      return <div className="entity-jd-content">{jd}</div>
    }

    const phase = manifest?.jobs.recommended.report_phase_tabs?.find(p => p.tab_id === tabId)
    if (phase && parsed) {
      const takeBody = parsed[phase.take_key as keyof AnalysisUpshot]
      const gradesRaw = jobGradesForField(job as unknown as Record<string, unknown>, phase.grades_field)
      const rubricKey = manifest?.jobs.grade_rubric_by_field[phase.grades_field]
      const grades = gradesForHeader(gradesRaw)
      return (
        <div>
          {typeof takeBody === "string" && takeBody.trim() && (
            <UpshotStringBlock heading={snakeCaseToTitle(phase.take_key)} body={takeBody} />
          )}
          {grades.length > 0 ? (
            <AgentAnalysisHeader grades={grades} rubricArtifact={rubricKey} />
          ) : (
            <p className="recommended-report-empty">No consult detail on file.</p>
          )}
        </div>
      )
    }

    const artTab = manifest?.jobs.recommended.report_artifact_tabs?.find(a => a.tab_id === tabId)
    if (artTab && jobId) {
      if (artTab.use_resume_structure) {
        if (structureError) return <p className="entity-error">Failed to load resume structure.</p>
        if (!structureSections?.length) return <p className="recommended-report-empty">Loading resume structure…</p>
        return (
          <ArtifactEditor
            title={artTab.nav_label}
            artifactKey={artTab.artifact_key}
            taskKey="craft_resume_base"
            useCandidateResumeStructure
            structureSections={structureSections}
            jobPersistence={{ jobId, artifactKey: artTab.artifact_key, onSaved: load }}
          />
        )
      }
      return (
        <ArtifactEditor
          title={artTab.nav_label}
          artifactKey={artTab.artifact_key}
          taskKey={artTab.artifact_key === "cover_letter" ? "craft_cover_letter" : "propose_application_responses"}
          shapesKey={artTab.shapes_key ?? undefined}
          jobPersistence={{ jobId, artifactKey: artTab.artifact_key, onSaved: load }}
        />
      )
    }

    return null
  }

  return (
    <Modal
      open={!!jobId}
      onClose={onClose}
      title={job?.job_title || job?.company || "Recommended Job Report"}
      size="wide"
    >
      {loading && <p className="entity-loading">Loading…</p>}
      {error && <p className="entity-error">{error}</p>}
      {job && !loading && (
        <div className="recommended-report-shell">
          <RecommendedJobReportHeader
            companyName={job.company}
            companyWebsite={companyWebsite}
            jobLink={job.job_link ?? null}
            jobState={job.state}
            profileLinks={profileLinks}
            primaryAction={primaryAction}
            onPrimaryAction={runPrimaryAction}
            primaryBusy={primaryBusy}
            stateLabel={stateSectionLabel}
            copyFeedback={copyFeedback}
            onCopyLink={(value, key) => handleCopy(value, key)}
            previewMaterials={showPreview ? { onClick: () => setPreviewOpen(true) } : undefined}
          />
          <div className="recommended-report-body">
            {tabs.length > 0 ? (
              <SideTabPanel
                tabs={tabs}
                renderTabLabel={renderTabLabel}
                renderContent={renderReportPane}
              />
            ) : (
              <p className="recommended-report-empty">
                {!manifest?.jobs.recommended
                  ? "Report layout unavailable. Try refreshing the page."
                  : "No report tabs available."}
              </p>
            )}
          </div>
        </div>
      )}
      {jobId && (
        <MaterialsPreviewModal
          open={previewOpen}
          onClose={() => setPreviewOpen(false)}
          jobId={jobId}
          hasCover={hasCover}
        />
      )}
    </Modal>
  )
}
