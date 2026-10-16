import { useCallback, useEffect, useMemo, useState, type ComponentType, type ReactNode } from "react"
import AgentAnalysisHeader from "./AgentAnalysisHeader"
import { type AgentStoryEntry } from "./AgentStoryTab"
import CandidateActionNotesModal from "./CandidateActionNotesModal"
import JobDiscussionPane from "./JobDiscussionPane"
import JobArtifactEditModal, { type JobArtifactTab } from "./JobArtifactEditModal"
import JobMeteoritePane, { type RelatedMeteorite } from "./JobMeteoritePane"
import Modal from "./Modal"
import PrintPreview from "./PrintPreview"
import RecommendedJobReportHeader from "./RecommendedJobReportHeader"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import { TabBar } from "./TabbedTextArea"
import Toast, { type ToastMessage } from "./Toast"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import { postCandidateAction, postSkipJob } from "../lib/candidateJobActions"
import { fetchPrintHtml, openHtmlInNewTab } from "../lib/printHtml"
import { parseAnalysisUpshot, type AnalysisUpshot } from "../lib/analysisUpshot"
import {
  anyReportArtifactContent,
  artifactHasContent,
  artifactsTabPrimaryActions,
  buildPhaseSectionGradeConfidenceRow,
  formatPhaseScore,
  gradesForHeader,
  isArtifactsBuildInProgress,
  jobGradablePercent,
  jobGradesForField,
  jobRubricForField,
  jobScoreBreakdownForGradesField,
  phaseThermometerModel,
  printCoverVisible,
  printResumeVisible,
  totalScore,
  type ReportPrimaryAction,
} from "../lib/recommendedJobReport"

/** Navigable listing URL only — mirrors AST-1694 http(s) rule; non-http → null. */
function httpListingHref(raw: string | null | undefined): string | null {
  if (raw == null) return null
  const s = String(raw).trim()
  if (s.startsWith("http://") || s.startsWith("https://")) return s
  return null
}

function formatReportDate(value: string | null | undefined): string | null {
  const raw = value?.trim()
  if (!raw) return null
  const d = new Date(raw)
  if (Number.isNaN(d.getTime())) return null
  return new Intl.DateTimeFormat("en-US", {
    year: "2-digit",
    month: "numeric",
    day: "numeric",
  }).format(d)
}

/** AST-2233 header contract — cast until #2 merges onto this tip (AST-2234). */
type TriageHeaderProps = {
  jobTitle: string
  jobLink: string | null
  jobLinkText?: string | null
  companyName: string
  companyWebsite: string | null
  discoveredAt?: string | null
  recommendedAt?: string | null
  appliedAt?: string | null
  onSkip?: () => void
  skipBusy?: boolean
  onApplied?: () => void
  appliedBusy?: boolean
  onGenerateArtifacts?: () => void
  generateBusy?: boolean
}

const TriageHeader = RecommendedJobReportHeader as unknown as ComponentType<TriageHeaderProps>

interface JobDetail {
  astral_job_id: string
  job_title: string | null
  company: string
  company_name?: string | null
  company_website?: string | null
  discovered_at?: string | null
  recommended_at?: string | null
  applied_at?: string | null
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
  can_skip?: boolean
  can_apply?: boolean
}

interface Props {
  jobId: string | null
  onClose: () => void
  onRefresh?: () => void
}

/** Shell AST-948; panes/wiring AST-2234. */
export default function JobAnalysisReportModal({ jobId, onClose, onRefresh }: Props) {
  const { manifest } = useStateUi()
  const [job, setJob] = useState<JobDetail | null>(null)
  const [companyUpshot, setCompanyUpshot] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [primaryBusy, setPrimaryBusy] = useState(false)
  const [skipBusy, setSkipBusy] = useState(false)
  const [appliedBusy, setAppliedBusy] = useState(false)
  const [appliedNotesOpen, setAppliedNotesOpen] = useState(false)
  const [activeTopTab, setActiveTopTab] = useState("")
  const [editTab, setEditTab] = useState<JobArtifactTab | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [isMobile, setIsMobile] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(max-width: 1023px)").matches,
  )
  const clearToast = useCallback(() => setToast(null), [])

  const load = useCallback(async () => {
    if (!jobId) return
    setLoading(true)
    setError(null)
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
      // Company upshot still comes from the company row; website is on detail (AST-2232).
      if (data.company) {
        api(`/api/companies/${encodeURIComponent(data.company)}`)
          .then(r => (r.ok ? r.json() : null))
          .then(co => {
            const companyUpshotText = co?.company_upshot
            setCompanyUpshot(
              typeof companyUpshotText === "string" && companyUpshotText.trim()
                ? companyUpshotText.trim()
                : null,
            )
          })
          .catch(() => setCompanyUpshot(null))
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
    const mq = window.matchMedia("(max-width: 1023px)")
    const sync = () => setIsMobile(mq.matches)
    sync()
    mq.addEventListener("change", sync)
    return () => mq.removeEventListener("change", sync)
  }, [])

  useEffect(() => {
    if (isMobile) setEditTab(null)
  }, [isMobile])

  const handlePrintResume = useCallback(async () => {
    if (!jobId) return
    const r = await fetchPrintHtml({ kind: "job_resume", id: jobId })
    const err = r.ok ? openHtmlInNewTab(r.html) : r.error
    if (err) setToast({ text: err, variant: "error" })
  }, [jobId])

  const handlePrintCover = useCallback(async () => {
    if (!jobId) return
    const r = await fetchPrintHtml({ kind: "cover", id: jobId })
    const err = r.ok ? openHtmlInNewTab(r.html) : r.error
    if (err) setToast({ text: err, variant: "error" })
  }, [jobId])

  useEffect(() => {
    setActiveTopTab("")
    setAppliedNotesOpen(false)
  }, [jobId])

  const artifactTabs: JobArtifactTab[] | undefined = manifest?.jobs.recommended.report_artifact_tabs
  const artifacts = job?.job_data?.artifacts
  const buildInProgress = !!(job && isArtifactsBuildInProgress(job.state))
  const hasArtifactContent = anyReportArtifactContent(artifacts, artifactTabs)
  const showArtifactsTab = hasArtifactContent || buildInProgress

  const topTabs = useMemo(() => {
    const rows = manifest?.jobs.recommended.report_top_tabs ?? []
    const hasMeteorite = job?.related_meteorite != null
    return rows
      .filter(r => r.tab_id !== "meteorite" || hasMeteorite)
      .filter(r => r.tab_id !== "artifacts" || showArtifactsTab)
      .map(r => ({ key: r.tab_id, label: r.nav_label }))
  }, [manifest, job?.related_meteorite, showArtifactsTab])

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

  const summarySections = useMemo((): ReportSectionDef[] => {
    return (manifest?.jobs.recommended.report_summary_sections ?? [])
      .filter(s => s.section_id !== "raw_jd")
      .map(s => {
        let default_expanded = s.default_expanded
        if (s.section_id === "job_summary") default_expanded = true
        else if (s.section_id === "company_upshot") default_expanded = !!companyUpshot
        else if (s.section_id === "caveats") default_expanded = hasCaveats
        else if (s.section_id === "questions") default_expanded = hasQuestions
        return {
          section_id: s.section_id,
          nav_label: s.nav_label,
          default_expanded,
        }
      })
  }, [manifest, companyUpshot, hasCaveats, hasQuestions])

  const jobDescriptionSections = useMemo((): ReportSectionDef[] => ([
    { section_id: "job_description", nav_label: "Job Description", default_expanded: true },
  ]), [])

  const analysisSections = useMemo((): ReportSectionDef[] => {
    const jobRec = job as unknown as Record<string, unknown> | null
    return (manifest?.jobs.recommended.report_phase_tabs ?? []).map(p => {
      const base = p.nav_label
      let nav_label = base
      if (jobRec) {
        const breakdown = jobScoreBreakdownForGradesField(jobRec, p.grades_field)
        const score = jobRec[p.grades_field.replace(/_grades$/, "_score")]
        if (
          breakdown
          && breakdown.max > 0
          && typeof score === "number"
          && Number.isFinite(score)
        ) {
          const gradable = Math.round((100 * breakdown.possible) / breakdown.max)
          nav_label = `${base} - ${formatPhaseScore(score)} (${gradable}% gradable)`
        }
      }
      return {
        section_id: p.tab_id,
        nav_label,
        default_expanded: false,
      }
    })
  }, [manifest, job])

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

  const meteoriteSections = useMemo((): ReportSectionDef[] => {
    const rows = manifest?.jobs.recommended.report_meteorite_sections ?? []
    return rows.map(s => ({
      section_id: s.section_id,
      nav_label: s.nav_label,
      default_expanded: s.default_expanded,
    }))
  }, [manifest])

  const populatedArtifactThumbs = useMemo(
    () => (artifactTabs ?? []).filter(a => a.preview_thumbnail && artifactHasContent(artifacts, a.artifact_key)),
    [artifactTabs, artifacts],
  )

  const artifactActions = useMemo((): ReportPrimaryAction[] => {
    if (!job) return []
    return artifactsTabPrimaryActions(manifest, job.state)
  }, [manifest, job])

  const phaseScoreFields = useMemo(
    () => (manifest?.jobs.recommended.phase_score_columns ?? []).map(c => c.field),
    [manifest],
  )

  const showPrintResume = printResumeVisible(artifacts)
  const showPrintCover = printCoverVisible(artifacts)

  function renderSummarySection(sectionId: string): ReactNode {
    if (!job) return null

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

    return null
  }

  function renderJobDescriptionSection(_sectionId: string): ReactNode {
    if (!job) return null
    const jd = String(job.job_data?.job_description ?? "").trim().replace(/\n{3,}/g, "\n\n")
    if (jd) return <div className="entity-jd-content">{jd}</div>
    return <p className="recommended-report-empty">No job description on file.</p>
  }

  function renderAnalysisTotalRow(): ReactNode {
    if (!job) return null
    const jobRec = job as unknown as Record<string, unknown>
    const total = totalScore(jobRec, phaseScoreFields)
    const gradable = jobGradablePercent(jobRec)
    const scoreText = `${formatPhaseScore(total)}${gradable != null ? ` (${gradable}% gradable)` : ""}`
    return (
      <div className="recommended-report-total-gradable">
        Total Score: <strong>{scoreText}</strong>
      </div>
    )
  }

  function renderAnalysisMetadata(sectionId: string): ReactNode {
    if (!job || !manifest) return null
    const phase = manifest.jobs.recommended.report_phase_tabs?.find(p => p.tab_id === sectionId)
    if (!phase) return null
    const jobRec = job as unknown as Record<string, unknown>
    const gradesRaw = jobGradesForField(jobRec, phase.grades_field)
    const score = jobRec[phase.grades_field.replace(/_grades$/, "_score")]
    const breakdown = jobScoreBreakdownForGradesField(jobRec, phase.grades_field)
    const thermo = phaseThermometerModel(score, breakdown)
    return (
      <>
        {thermo && (
          <div className="recommended-report-thermometer" title={thermo.tooltip}>
            <div className="recommended-report-thermometer-track">
              <div
                className="recommended-report-thermometer-fill"
                style={{ width: `${thermo.fillRatio * 100}%` }}
              />
            </div>
          </div>
        )}
        {buildPhaseSectionGradeConfidenceRow(gradesRaw, jobRec, phase.grades_field, isMobile)}
      </>
    )
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

  function renderArtifactThumb(artTab: JobArtifactTab): ReactNode {
    if (!jobId) return null
    const printKind = artTab.use_resume_structure ? "job_resume" as const : "cover" as const
    const onPrint = artTab.use_resume_structure ? handlePrintResume : handlePrintCover
    return (
      <div key={artTab.tab_id} style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <PrintPreview
          target={{ kind: printKind, id: jobId }}
          thumbnail
          onClick={isMobile ? undefined : () => setEditTab(artTab)}
        />
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <span>{artTab.nav_label}</span>
          {!isMobile && artTab.use_resume_structure && (
            <button type="button" className="btn secondary" onClick={() => setEditTab(artTab)}>
              Edit
            </button>
          )}
          <button type="button" className="btn secondary" onClick={() => { void onPrint() }}>
            Print
          </button>
        </div>
      </div>
    )
  }

  function renderArtifactsPane(): ReactNode {
    if (!job) return null

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

    // Empty tab is filtered out; keep a Generate fallback if the tab is somehow shown.
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

    return (
      <div className="recommended-report-artifact-thumbs" style={{ display: "flex", alignItems: "flex-start", gap: 24, flexWrap: "wrap" }}>
        {(showPrintResume || showPrintCover) && (
          <div className="recommended-report-artifacts-actions" style={{ width: "100%" }}>
            {showPrintResume && (
              <button type="button" className="btn secondary" onClick={() => { void handlePrintResume() }}>
                Print Resume
              </button>
            )}
            {showPrintCover && (
              <button type="button" className="btn secondary" onClick={() => { void handlePrintCover() }}>
                Print Cover Letter
              </button>
            )}
          </div>
        )}
        {populatedArtifactThumbs.map(renderArtifactThumb)}
      </div>
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

  async function handleAppliedConfirm(notes: string) {
    if (!jobId || appliedBusy) return
    setAppliedBusy(true)
    try {
      await postCandidateAction(jobId, "applied", notes)
      setAppliedNotesOpen(false)
      onRefresh?.()
      onClose()
    } catch (e) {
      setToast({ text: e instanceof Error ? e.message : "Action failed", variant: "error" })
    } finally {
      setAppliedBusy(false)
    }
  }

  function handleHeaderGenerate() {
    const generate = artifactActions.find(a => a.action_key === "generate_artifacts")
    if (generate) void runPrimaryAction(generate)
  }

  const jobTitleDisplay = job?.job_title?.trim() || ""
  const companyNameDisplay = job?.company_name?.trim() || job?.company || ""
  const discoveredLabel = formatReportDate(job?.discovered_at)
  const modalTitle = companyNameDisplay
    ? `${companyNameDisplay}${discoveredLabel ? ` · ${discoveredLabel}` : ""}`
    : ""
  const companyWebsite =
    (typeof job?.company_website === "string" && job.company_website.trim())
      ? job.company_website.trim()
      : null
  const jobHref = job
    ? (httpListingHref(job.listing_href) ?? httpListingHref(job.job_link))
    : null
  const rawJobLink = job?.job_link?.trim() || (typeof job?.listing_href === "string" ? job.listing_href.trim() : "")
  const jobLinkText = jobHref || rawJobLink || null

  return (
    <Modal
      open={!!jobId}
      onClose={onClose}
      title={modalTitle}
      size="wide"
      showFooter={false}
    >
      {loading && <p className="entity-loading">Loading…</p>}
      {error && <p className="entity-error">{error}</p>}
      {job && !loading && (
        <div className="recommended-report-shell">
          <div className="recommended-report-chrome">
            <TriageHeader
              jobTitle={jobTitleDisplay}
              jobLink={jobHref}
              jobLinkText={jobLinkText}
              companyName={companyNameDisplay}
              companyWebsite={companyWebsite}
              discoveredAt={job.discovered_at}
              recommendedAt={job.recommended_at}
              appliedAt={job.applied_at}
              onSkip={job.can_skip ? () => { void handleSkip() } : undefined}
              skipBusy={skipBusy}
              onApplied={job.can_apply ? () => setAppliedNotesOpen(true) : undefined}
              appliedBusy={appliedBusy}
              onGenerateArtifacts={!showArtifactsTab ? () => handleHeaderGenerate() : undefined}
              generateBusy={primaryBusy}
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
              {activeTopTab === "job_description" && (
                <ReportSectionList
                  sections={jobDescriptionSections}
                  renderSection={renderJobDescriptionSection}
                />
              )}
              {activeTopTab === "analysis" && (
                <ReportSectionList
                  sections={analysisSections}
                  leading={renderAnalysisTotalRow()}
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
      {jobId && (
        <JobArtifactEditModal jobId={jobId} tab={editTab} onClose={() => { setEditTab(null); void load() }} />
      )}
      <CandidateActionNotesModal
        open={appliedNotesOpen}
        action={appliedNotesOpen ? "applied" : null}
        busy={appliedBusy}
        onClose={() => setAppliedNotesOpen(false)}
        onConfirm={(notes) => { void handleAppliedConfirm(notes) }}
      />
      <Toast message={toast} onDone={clearToast} />
    </Modal>
  )
}
