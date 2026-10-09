import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react"
import AgentAnalysisHeader from "./AgentAnalysisHeader"
import { type AgentStoryEntry } from "./AgentStoryTab"
import ArtifactEditor from "./ArtifactEditor"
import JobDiscussionPane from "./JobDiscussionPane"
import JobArtifactEditModal, { type JobArtifactTab } from "./JobArtifactEditModal"
import JobMeteoritePane, { type RelatedMeteorite } from "./JobMeteoritePane"
import Modal from "./Modal"
import PrintPreview from "./PrintPreview"
import RecommendedJobReportHeader from "./RecommendedJobReportHeader"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import { TabBar } from "./TabbedTextArea"
import Toast, { type ToastMessage } from "./Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import { postSkipJob } from "../lib/candidateJobActions"
import { fetchPrintHtml, openHtmlInNewTab } from "../lib/printHtml"
import { copyJobSnapshotToClipboard } from "../lib/copyJobSnapshot"
import { parseAnalysisUpshot, type AnalysisUpshot } from "../lib/analysisUpshot"
import {
  anyReportArtifactContent,
  artifactHasContent,
  artifactsTabPrimaryActions,
  buildPhaseSectionGradeConfidenceRow,
  emailWithJobPlusTag,
  formatPhaseSectionScoreTitle,
  gradesForHeader,
  isArtifactsBuildInProgress,
  jobGradesForField,
  jobRubricForField,
  jobScoreBreakdownForGradesField,
  printCoverVisible,
  printResumeVisible,
  type ReportPrimaryAction,
} from "../lib/recommendedJobReport"

/** Navigable listing URL only — mirrors AST-1694 http(s) rule; non-http → null. */
function httpListingHref(raw: string | null | undefined): string | null {
  if (raw == null) return null
  const s = String(raw).trim()
  if (s.startsWith("http://") || s.startsWith("https://")) return s
  return null
}

interface JobDetail {
  astral_job_id: string
  job_title: string | null
  company: string
  state: string
  state_changed_at: string | null
  job_link?: string | null
  listing_href?: string | null
  job_data?: Record<string, unknown>
  jd_grades?: unknown
  do_grades?: unknown
  get_grades?: unknown
  like_grades?: unknown
  jd_rubric?: unknown
  do_rubric?: unknown
  get_rubric?: unknown
  like_rubric?: unknown
  agent_story?: AgentStoryEntry[]
  related_meteorite?: RelatedMeteorite | null
  can_skip?: boolean // AST-1872: server-resolved Skip legality
}

interface Props {
  jobId: string | null
  onClose: () => void
  onRefresh?: () => void
}

/** Shell AST-948; Summary AST-949; Analysis AST-950; Artifacts AST-951. */
export default function JobAnalysisReportModal({ jobId, onClose, onRefresh }: Props) {
  const { manifest } = useStateUi()
  const { selectedId, candidates } = useCandidate()
  const [job, setJob] = useState<JobDetail | null>(null)
  const [companyWebsite, setCompanyWebsite] = useState<string | null>(null)
  const [companyUpshot, setCompanyUpshot] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [primaryBusy, setPrimaryBusy] = useState(false)
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null)
  const [snapshotCopied, setSnapshotCopied] = useState(false)
  const [detailLinkCopied, setDetailLinkCopied] = useState(false)
  const [snapshotCopying, setSnapshotCopying] = useState(false)
  const [skipBusy, setSkipBusy] = useState(false)
  // Empty until the manifest tabs resolve — the effect below picks topTabs[0] (config order, AST-1874).
  const [activeTopTab, setActiveTopTab] = useState("")
  // AST-2084: artifact tab open in the stacked edit modal (null = closed).
  const [editTab, setEditTab] = useState<JobArtifactTab | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  const candidate = useMemo(
    () => candidates.find(c => c.astral_candidate_id === selectedId),
    [candidates, selectedId],
  )

  const load = useCallback(async () => {
    if (!jobId) return
    setLoading(true)
    setError(null)
    setCompanyWebsite(null)
    setCompanyUpshot(null)
    try {
      const res = await api(`/api/jobs/${encodeURIComponent(jobId)}`)
      if (!res.ok) {
        if (res.status === 404) throw new Error("Job not found")
        const errBody = (await res.json().catch(() => ({}))) as { error?: string }
        const msg =
          typeof errBody.error === "string" && errBody.error.trim()
            ? errBody.error.trim()
            : `Load failed (HTTP ${res.status})`
        throw new Error(msg)
      }
      const data = (await res.json()) as JobDetail
      setJob(data)
      if (data.company) {
        api(`/api/companies/${encodeURIComponent(data.company)}`)
          .then(r => (r.ok ? r.json() : null))
          .then(co => {
            const site = co?.company_website
            setCompanyWebsite(typeof site === "string" && site.trim() ? site.trim() : null)
            const companyUpshotText = co?.company_upshot
            setCompanyUpshot(
              typeof companyUpshotText === "string" && companyUpshotText.trim() ? companyUpshotText.trim() : null,
            )
          })
          .catch(() => {
            setCompanyWebsite(null)
            setCompanyUpshot(null)
          })
      }
    } catch (e) {
      setJob(null)
      setError(e instanceof Error ? e.message : "Load failed")
    } finally {
      setLoading(false)
    }
  }, [jobId])

  useEffect(() => { load() }, [load])



  // AST-2084: shared print helper; the job's structure is saved by the resume editor, so nothing persists first.
  const handlePrintResume = useCallback(async () => {
    if (!jobId) return
    const r = await fetchPrintHtml({ kind: "job_resume", id: jobId })
    const err = r.ok ? openHtmlInNewTab(r.html) : r.error
    if (err) setToast({ text: err, variant: "error" })
  }, [jobId])

  // Reset top tab when opening a different job; the fallback effect re-picks the first manifest tab.
  useEffect(() => {
    setActiveTopTab("")
  }, [jobId])
  useEffect(() => { setSnapshotCopied(false) }, [jobId])
  useEffect(() => { setDetailLinkCopied(false) }, [jobId])

  const topTabs = useMemo(() => {
    const rows = manifest?.jobs.recommended.report_top_tabs ?? []
    const hasMeteorite = job?.related_meteorite != null
    return rows
      .filter(r => r.tab_id !== "meteorite" || hasMeteorite)
      .map(r => ({ key: r.tab_id, label: r.nav_label }))
  }, [manifest, job?.related_meteorite])

  useEffect(() => {
    if (topTabs.length === 0) return
    if (!topTabs.some(t => t.key === activeTopTab)) {
      setActiveTopTab(topTabs[0].key)
    }
  }, [topTabs, activeTopTab])

  const upshot = useMemo(
    () => parseAnalysisUpshot(job?.job_data?.analysis_upshot),
    [job?.job_data?.analysis_upshot],
  )

  const hasCaveats = !!(upshot?.caveats.some(c => c.text.trim()))
  const hasQuestions = !!(upshot?.candidate_questions.some(q => q.text.trim()))

  // Content-aware expand overrides (AST-949 Stage 3) — emptiness is data-dependent.
  const summarySections = useMemo((): ReportSectionDef[] => {
    return (manifest?.jobs.recommended.report_summary_sections ?? []).map(s => {
      let default_expanded = s.default_expanded
      if (s.section_id === "job_summary") default_expanded = true
      else if (s.section_id === "company_upshot") default_expanded = !!companyUpshot
      else if (s.section_id === "caveats") default_expanded = hasCaveats
      else if (s.section_id === "questions") default_expanded = hasQuestions
      else if (s.section_id === "raw_jd") default_expanded = false
      return {
        section_id: s.section_id,
        nav_label: s.nav_label,
        default_expanded,
      }
    })
  }, [manifest, companyUpshot, hasCaveats, hasQuestions])

  const analysisSections = useMemo((): ReportSectionDef[] => {
    const template = manifest?.jobs.recommended.phase_score_header_title_template ?? ""
    const jobRec = job as unknown as Record<string, unknown> | null
    return (manifest?.jobs.recommended.report_phase_tabs ?? []).map(p => {
      const base = p.nav_label
      let nav_label = base
      if (jobRec) {
        const breakdown = jobScoreBreakdownForGradesField(jobRec, p.grades_field)
        if (breakdown) {
          // List score is flattened top-level on the detail GET as <prefix>_score (jd_grades → jd_score).
          const score = jobRec[p.grades_field.replace(/_grades$/, "_score")]
          nav_label = formatPhaseSectionScoreTitle(base, breakdown, template, score)
        }
      }
      return {
        section_id: p.tab_id,
        nav_label,
        default_expanded: false,
      }
    })
  }, [manifest, job])

  // AST-1551: Discussion hop slots from AST-1550 manifest (local cast — Scope omits StateUiContext).
  const discussionSections = useMemo((): ReportSectionDef[] => {
    const recommended = manifest?.jobs.recommended as
      | {
          report_discussion_sections?: Array<{
            section_id: string
            nav_label: string
            default_expanded: boolean
          }>
        }
      | undefined
    const rows = recommended?.report_discussion_sections ?? []
    return rows.map(s => ({
      section_id: s.section_id,
      nav_label: s.nav_label,
      default_expanded: s.default_expanded,
    }))
  }, [manifest])

  // AST-1692: Meteorite pane sections from typed manifest (AST-1691 config).
  const meteoriteSections = useMemo((): ReportSectionDef[] => {
    const rows = manifest?.jobs.recommended.report_meteorite_sections ?? []
    return rows.map(s => ({
      section_id: s.section_id,
      nav_label: s.nav_label,
      default_expanded: s.default_expanded,
    }))
  }, [manifest])

  const artifactTabs: JobArtifactTab[] | undefined = manifest?.jobs.recommended.report_artifact_tabs
  const artifacts = job?.job_data?.artifacts
  const buildInProgress = !!(job && isArtifactsBuildInProgress(job.state))
  const hasArtifactContent = anyReportArtifactContent(artifacts, artifactTabs)

  const populatedArtifactSections = useMemo((): ReportSectionDef[] => {
    if (!artifactTabs) return []
    return artifactTabs
      .filter(a => artifactHasContent(artifacts, a.artifact_key))
      .map(a => ({
        section_id: a.tab_id,
        nav_label: a.nav_label,
        default_expanded: false,
      }))
  }, [artifactTabs, artifacts])

  const artifactActions = useMemo((): ReportPrimaryAction[] => {
    if (!job) return []
    return artifactsTabPrimaryActions(manifest, job.state)
  }, [manifest, job])

  const profile = useMemo(() => {
    const raw = (candidate?.candidate_data as Record<string, unknown> | undefined)?.contact
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

  function renderSummarySection(sectionId: string): ReactNode {
    if (!job) return null
    const jobData = job.job_data ?? {}

    if (sectionId === "job_summary") {
      const body = upshot?.whole_jd_upshot?.trim() ?? ""
      if (body) return <p className="job-analysis-upshot-body">{body}</p>
      return <p className="recommended-report-empty">No job summary on file.</p>
    }

    if (sectionId === "company_upshot") {
      if (companyUpshot) return <p className="job-analysis-upshot-body">{companyUpshot}</p>
      return <p className="recommended-report-empty">No company upshot on file.</p>
    }

    if (sectionId === "caveats") {
      const rows = (upshot?.caveats ?? []).map(c => c.text.trim()).filter(Boolean)
      if (rows.length === 0) {
        return <p className="recommended-report-empty">No noteworthy caveats on file.</p>
      }
      return (
        <ul className="job-analysis-upshot-list">
          {rows.map((text, i) => (
            <li key={`c-${i}`}>{text}</li>
          ))}
        </ul>
      )
    }

    if (sectionId === "questions") {
      const rows = (upshot?.candidate_questions ?? []).map(q => q.text.trim()).filter(Boolean)
      if (rows.length === 0) {
        return <p className="recommended-report-empty">No questions to ask on file.</p>
      }
      return (
        <ul className="job-analysis-upshot-list">
          {rows.map((text, i) => (
            <li key={`q-${i}`}>{text}</li>
          ))}
        </ul>
      )
    }

    if (sectionId === "raw_jd") {
      const jd = String(jobData.job_description ?? "").trim().replace(/\n{3,}/g, "\n\n")
      if (jd) return <div className="entity-jd-content">{jd}</div>
      return <p className="recommended-report-empty">No job description on file.</p>
    }

    return null
  }

  function renderAnalysisMetadata(sectionId: string): ReactNode {
    if (!job || !manifest) return null
    const phase = manifest.jobs.recommended.report_phase_tabs?.find(p => p.tab_id === sectionId)
    if (!phase) return null
    const jobRec = job as unknown as Record<string, unknown>
    const gradesRaw = jobGradesForField(jobRec, phase.grades_field)
    return buildPhaseSectionGradeConfidenceRow(gradesRaw, jobRec, phase.grades_field)
  }

  function renderAnalysisSection(sectionId: string): ReactNode {
    if (!job || !manifest) return null
    const phase = manifest.jobs.recommended.report_phase_tabs?.find(p => p.tab_id === sectionId)
    if (!phase) return null
    const parsed = parseAnalysisUpshot(job.job_data?.analysis_upshot)
    const takeRaw = parsed?.[phase.take_key as keyof AnalysisUpshot]
    const takeBody = typeof takeRaw === "string" ? takeRaw.trim() : ""
    const jobRec = job as unknown as Record<string, unknown>
    const gradesRaw = jobGradesForField(jobRec, phase.grades_field)
    const rubricKey = manifest.jobs.grade_rubric_by_field[phase.grades_field]
    const grades = gradesForHeader(gradesRaw)
    const rubricItems = jobRubricForField(jobRec, phase.grades_field)
    return (
      <div>
        {takeBody ? <p className="job-analysis-upshot-body">{takeBody}</p> : null}
        {grades.length > 0 ? (
          <AgentAnalysisHeader
            grades={grades}
            rubricItems={rubricItems}
            rubricArtifact={rubricKey}
          />
        ) : (
          <p className="recommended-report-empty">No consult detail on file.</p>
        )}
      </div>
    )
  }

  function renderArtifactSection(sectionId: string): ReactNode {
    if (!jobId || !artifactTabs) return null
    const artTab = artifactTabs.find(a => a.tab_id === sectionId)
    if (!artTab) return null
    // AST-2084: config-flagged tabs show the print preview; a click (or Edit, resume only) opens the stacked edit modal.
    if (artTab.preview_thumbnail) {
      return (
        <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
          <PrintPreview
            target={{ kind: artTab.use_resume_structure ? "job_resume" : "cover", id: jobId }}
            thumbnail
            onClick={() => setEditTab(artTab)}
          />
          {artTab.use_resume_structure && (
            <button type="button" className="btn secondary" onClick={() => setEditTab(artTab)}>
              Edit
            </button>
          )}
        </div>
      )
    }
    const taskKey =
      artTab.artifact_key === "cover_letter"
        ? "craft_cover_letter"
        : "propose_application_responses"
    return (
      <ArtifactEditor
        title={artTab.nav_label}
        artifactKey={artTab.artifact_key}
        taskKey={taskKey}
        shapesKey={artTab.shapes_key ?? undefined}
        jobPersistence={{ jobId, artifactKey: artTab.artifact_key, onSaved: load }}
      />
    )
  }

  function renderArtifactsPane(): ReactNode {
    if (!job) return null

    // A — in progress: Generating… + Cancel; no section panels
    if (buildInProgress) {
      const cancelActions = artifactActions.filter(a => a.action_key === "cancel_build")
      return (
        <div className="recommended-report-artifacts-actions">
          <button type="button" className="btn primary in-flight" disabled>
            Generating…
          </button>
          {cancelActions.map(action => (
            <button
              key={action.action_key}
              type="button"
              className="btn secondary"
              disabled={primaryBusy}
              onClick={() => runPrimaryAction(action)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )
    }

    // B — empty: Generate only
    if (!hasArtifactContent) {
      const generate = artifactActions.find(a => a.action_key === "generate_artifacts")
      if (!generate) return null
      return (
        <div className="recommended-report-artifacts-actions">
          <button
            type="button"
            className={`btn primary${primaryBusy ? " in-flight" : ""}`}
            disabled={primaryBusy}
            onClick={() => runPrimaryAction(generate)}
          >
            {generate.label}
          </button>
        </div>
      )
    }

    // C — populated: collapsible editors; no Generate/Cancel strip
    return (
      <ReportSectionList
        sections={populatedArtifactSections}
        renderSection={renderArtifactSection}
      />
    )
  }

  async function runPrimaryAction(action: ReportPrimaryAction) {

    if (!jobId || !job || primaryBusy) return
    setPrimaryBusy(true)
    setError(null)
    try {
      if (action.method === "CLIENT") {
        const href = httpListingHref(job.listing_href)
        if (href) window.open(href, "_blank", "noopener,noreferrer")
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

  async function handleCopySnapshot() {
    if (!jobId || snapshotCopying) return
    setSnapshotCopying(true)
    const ok = await copyJobSnapshotToClipboard(jobId)
    setSnapshotCopying(false)
    if (!ok) return
    setSnapshotCopied(true)
    window.setTimeout(() => setSnapshotCopied(false), 2000)
  }

  function handleCopyDetailLink() {
    if (!jobId) return
    const url =
      `${window.location.origin}/jobs/detail/${encodeURIComponent(jobId)}`
    navigator.clipboard.writeText(url).then(() => {
      setDetailLinkCopied(true)
      window.setTimeout(() => setDetailLinkCopied(false), 2000)
    })
  }

  // AST-1874: server already gated visibility via can_skip; 409 etc. surface as a toast, modal stays open.
  async function handleSkip() {
    if (!jobId || skipBusy) return
    setSkipBusy(true)
    try {
      await postSkipJob(jobId)
      onRefresh?.()
      onClose()
    } catch (e) {
      setToast({ text: e instanceof Error ? e.message : "Skip failed", variant: "error" })
    } finally {
      setSkipBusy(false)
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

  return (
    <Modal
      open={!!jobId}
      onClose={onClose}
      title={job?.company || "Recommended Job Report"}
      size="wide"
      showFooter={false}
    >
      {loading && <p className="entity-loading">Loading…</p>}
      {error && <p className="entity-error">{error}</p>}
      {job && !loading && (
        <div className="recommended-report-shell">
          <div className="recommended-report-chrome">
            <RecommendedJobReportHeader
              jobTitle={jobTitleDisplay}
              jobLink={httpListingHref(job.listing_href)}
              jobLinkText={httpListingHref(job.listing_href) ?? job.job_link ?? null}
              companyName={job.company}
              companyWebsite={companyWebsite}
              applicationEmail={applicationEmail}
              linkedInUrl={linkedInUrl}
              copyFeedback={copyFeedback}
              onCopyApplicationEmail={handleCopyApplicationEmail}
              onCopyLinkedIn={handleCopyLinkedIn}
              onCopyDetailLink={handleCopyDetailLink}
              detailLinkCopied={detailLinkCopied}
              onCopySnapshot={handleCopySnapshot}
              snapshotCopied={snapshotCopied}
              snapshotCopying={snapshotCopying}
              onSkip={job.can_skip ? () => { void handleSkip() } : undefined}
              skipBusy={skipBusy}
              showPrintResume={showPrintResume}
              showPrintCover={showPrintCover}
              onPrintResume={() => { void handlePrintResume() }}
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
                  renderSection={renderSummarySection}
                />
              )}
              {activeTopTab === "analysis" && (
                <ReportSectionList
                  sections={analysisSections}
                  renderMetadata={renderAnalysisMetadata}
                  renderSection={renderAnalysisSection}
                />
              )}
              {activeTopTab === "artifacts" && renderArtifactsPane()}
              {activeTopTab === "discussion" && (
                <JobDiscussionPane
                  sections={discussionSections}
                  agentStory={job?.agent_story ?? []}
                />
              )}
              {activeTopTab === "meteorite" && job?.related_meteorite != null && (
                <JobMeteoritePane
                  sections={meteoriteSections}
                  relatedMeteorite={job.related_meteorite}
                />
              )}
            </div>
          )}
        </div>
      )}
      {/* Outside the job shell so the reload on close cannot unmount it mid-flush; close reloads the report (thumbnails refetch on remount). */}
      {jobId && (
        <JobArtifactEditModal jobId={jobId} tab={editTab} onClose={() => { setEditTab(null); void load() }} />
      )}
      <Toast message={toast} onDone={clearToast} />
    </Modal>
  )
}
