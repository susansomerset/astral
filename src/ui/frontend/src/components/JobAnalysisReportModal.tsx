import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react"
import AgentAnalysisHeader from "./AgentAnalysisHeader"
import ArtifactEditor from "./ArtifactEditor"
import Modal from "./Modal"
import RecommendedJobReportHeader from "./RecommendedJobReportHeader"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import {
  type Catalog,
  type SectionRow,
} from "./ResumeStructureEditor"
import { TabBar } from "./TabbedTextArea"
import Toast, { type ToastMessage } from "./Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
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

function catalogFromPayload(data: { catalog?: unknown }): Catalog | null {
  const raw = data.catalog
  if (!raw || typeof raw !== "object") return null
  const c = raw as Catalog
  if (!Array.isArray(c.body_formats)) return null
  return c
}

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
  jd_rubric?: unknown
  do_rubric?: unknown
  get_rubric?: unknown
  like_rubric?: unknown
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
  const [companyNotes, setCompanyNotes] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [primaryBusy, setPrimaryBusy] = useState(false)
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null)
  const [snapshotCopied, setSnapshotCopied] = useState(false)
  const [snapshotCopying, setSnapshotCopying] = useState(false)
  const [activeTopTab, setActiveTopTab] = useState("summary")
  const [structureSections, setStructureSections] = useState<{ id: string; label: string }[] | null>(null)
  const [structureError, setStructureError] = useState(false)
  const [allSections, setAllSections] = useState<SectionRow[]>([])
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [structureSaving, setStructureSaving] = useState(false)
  const [structureSaveError, setStructureSaveError] = useState<string | null>(null)
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
    setCompanyNotes(null)
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
            const notes = co?.prefilter_company_notes
            setCompanyNotes(typeof notes === "string" && notes.trim() ? notes.trim() : null)
          })
          .catch(() => {
            setCompanyWebsite(null)
            setCompanyNotes(null)
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

  // Resume section labels + structure authoring (candidate resume_structure as shared defaults).
  useEffect(() => {
    if (!selectedId) {
      setStructureSections(null)
      setStructureError(false)
      setAllSections([])
      setCatalog(null)
      return
    }
    setStructureSections(null)
    setStructureError(false)
    setAllSections([])
    setCatalog(null)
    api(`/api/candidates/${selectedId}/resume_structure`)
      .then(r => r.json())
      .then(data => {
        const sections = Array.isArray(data.sections) ? data.sections : []
        setStructureSections(sections.map((s: { id: string; label: string }) => ({ id: s.id, label: s.label })))
        setAllSections(Array.isArray(data.all_sections) ? data.all_sections as SectionRow[] : [])
        setCatalog(catalogFromPayload(data))
      })
      .catch(() => {
        setStructureSections(null)
        setStructureError(true)
        setAllSections([])
        setCatalog(null)
      })
  }, [selectedId])

  function handleStructureRowsChange(rows: SectionRow[]) {
    setAllSections(rows)
    setStructureSections(rows.map(r => ({ id: r.id, label: r.title })))
  }

  async function persistStructureRows(rows: SectionRow[]): Promise<void> {
    if (!selectedId) throw new Error("No candidate selected")
    const sections: Record<string, Record<string, unknown>> = {}
    rows.forEach((row, index) => {
      const spec: Record<string, unknown> = {
        id: row.id,
        title: row.title,
        enabled: row.enabled,
        order: index,
        job_agent_editable: row.job_agent_editable,
        page_break_policy: row.page_break_policy,
      }
      if (row.format) spec.format = row.format
      sections[row.id] = spec
    })
    setStructureSaving(true)
    setStructureSaveError(null)
    try {
      const r = await api(`/api/candidates/${selectedId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artifacts: { resume_structure: { sections } } }),
      })
      if (!r.ok) {
        const e = await r.json().catch(() => ({})) as { error?: string }
        throw new Error(e.error || "Save failed")
      }
      await r.json()
      const data = await api(`/api/candidates/${selectedId}/resume_structure`).then(res => res.json())
      const sectionsList = Array.isArray(data.sections) ? data.sections : []
      setStructureSections(sectionsList.map((s: { id: string; label: string }) => ({ id: s.id, label: s.label })))
      setAllSections(Array.isArray(data.all_sections) ? data.all_sections as SectionRow[] : [])
      setCatalog(catalogFromPayload(data))
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Save failed"
      setStructureSaveError(msg)
      throw e instanceof Error ? e : new Error(msg)
    } finally {
      setStructureSaving(false)
    }
  }

  function saveStructure(rows: SectionRow[]) {
    void persistStructureRows(rows)
      .then(() => setToast({ text: "Resume sections saved", variant: "success" }))
      .catch(e => {
        const msg = e instanceof Error ? e.message : "Save failed"
        setToast({ text: msg, variant: "error" })
      })
  }

  // AST-1350: fetch-then-blob; AST-1489: auto-persist structure rows before resume GET.
  const handlePrintResume = useCallback(async () => {
    if (!jobId) return
    try {
      if (selectedId) {
        await persistStructureRows(allSections)
      }
      const r = await api(`/candidate/resume/${encodeURIComponent(jobId)}`)
      if (!r.ok) {
        let msg = `HTTP ${r.status}`
        try {
          const data = await r.json()
          if (typeof data.error === "string" && data.error) msg = data.error
        } catch { /* non-JSON error body */ }
        setToast({ text: msg, variant: "error" })
        return
      }
      const html = await r.text()
      if (!html.trim()) {
        setToast({ text: "HTML response was empty", variant: "error" })
        return
      }
      const blobUrl = URL.createObjectURL(
        new Blob([html], { type: "text/html;charset=utf-8" }),
      )
      const win = window.open(blobUrl, "_blank", "noopener,noreferrer")
      if (!win) {
        setToast({
          text: "Popup blocked — allow popups to open the HTML tab.",
          variant: "error",
        })
      }
      window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000)
    } catch (e) {
      setToast({
        text: e instanceof Error ? e.message : "Print failed",
        variant: "error",
      })
    }
  }, [jobId, selectedId, allSections])

  // Reset top tab when opening a different job.
  useEffect(() => {
    setActiveTopTab("summary")
  }, [jobId])
  useEffect(() => { setSnapshotCopied(false) }, [jobId])

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
      else if (s.section_id === "company_upshot") default_expanded = !!companyNotes
      else if (s.section_id === "caveats") default_expanded = hasCaveats
      else if (s.section_id === "questions") default_expanded = hasQuestions
      else if (s.section_id === "raw_jd") default_expanded = false
      return {
        section_id: s.section_id,
        nav_label: s.nav_label,
        default_expanded,
      }
    })
  }, [manifest, companyNotes, hasCaveats, hasQuestions])

  const analysisSections = useMemo((): ReportSectionDef[] => {
    const template = manifest?.jobs.recommended.phase_score_header_title_template ?? ""
    const jobRec = job as unknown as Record<string, unknown> | null
    return (manifest?.jobs.recommended.report_phase_tabs ?? []).map(p => {
      const base = p.nav_label
      let nav_label = base
      if (jobRec) {
        const breakdown = jobScoreBreakdownForGradesField(jobRec, p.grades_field)
        if (breakdown) {
          nav_label = formatPhaseSectionScoreTitle(base, breakdown, template)
        }
      }
      return {
        section_id: p.tab_id,
        nav_label,
        default_expanded: false,
      }
    })
  }, [manifest, job])

  const artifactTabs = manifest?.jobs.recommended.report_artifact_tabs
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
      if (companyNotes) return <p className="job-analysis-upshot-body">{companyNotes}</p>
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
    if (artTab.use_resume_structure) {
      if (structureError) return <p className="entity-error">Failed to load resume structure.</p>
      if (!structureSections?.length) {
        return <p className="recommended-report-empty">Loading resume structure…</p>
      }
      return (
        <ArtifactEditor
          title={artTab.nav_label}
          artifactKey={artTab.artifact_key}
          taskKey="craft_resume_base"
          useCandidateResumeStructure
          structureSections={structureSections}
          structureCatalog={catalog}
          structureRows={allSections}
          onStructureRowsChange={handleStructureRowsChange}
          onStructureSave={saveStructure}
          structureSaving={structureSaving}
          structureError={structureSaveError}
          jobPersistence={{ jobId, artifactKey: artTab.artifact_key, onSaved: load }}
        />
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

  async function handleCopySnapshot() {
    if (!jobId || snapshotCopying) return
    setSnapshotCopying(true)
    const ok = await copyJobSnapshotToClipboard(jobId)
    setSnapshotCopying(false)
    if (!ok) return
    setSnapshotCopied(true)
    window.setTimeout(() => setSnapshotCopied(false), 2000)
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
              jobLink={job.job_link ?? null}
              companyName={job.company}
              companyWebsite={companyWebsite}
              applicationEmail={applicationEmail}
              linkedInUrl={linkedInUrl}
              copyFeedback={copyFeedback}
              onCopyApplicationEmail={handleCopyApplicationEmail}
              onCopyLinkedIn={handleCopyLinkedIn}
              onCopySnapshot={handleCopySnapshot}
              snapshotCopied={snapshotCopied}
              snapshotCopying={snapshotCopying}
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
            </div>
          )}
        </div>
      )}
      <Toast message={toast} onDone={clearToast} />
    </Modal>
  )
}
