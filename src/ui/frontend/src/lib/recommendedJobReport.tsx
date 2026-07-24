import type { ReactNode } from "react"
import { ConfidenceBullets } from "../components/ConfidenceBullets"
import {
  buildJobListRubricColumnsFromArtifact,
  formatGradeDotTooltip,
  normalizeRubricVectorKey,
  sortJobListRubricColumns,
  type JobListRubricColumn,
} from "./rubricDisplay"
import type { StateUiManifest } from "../contexts/StateUiContext"

export type ReportPrimaryAction = {
  action_key: string
  label: string
  method: string
  path_suffix: string
}

export function primaryActionsForState(
  manifest: StateUiManifest | null,
  state: string,
): ReportPrimaryAction[] {
  return manifest?.jobs.recommended.primary_actions_by_state?.[state] ?? []
}

/** True for BUILD_ARTIFACTS and legacy daisy-chain BUILD_ARTIFACTS.<hop> (not ERROR_BUILD_ARTIFACTS). */
export function isArtifactsBuildInProgress(jobState: string): boolean {
  return jobState === "BUILD_ARTIFACTS" || jobState.startsWith("BUILD_ARTIFACTS.")
}

/**
 * Primary actions for the Artifacts strip.
 * Looks up manifest actions for jobState; if empty while build-in-progress,
 * fall back to BUILD_ARTIFACTS (compound hops share Cancel). Filters out apply.
 */
export function artifactsTabPrimaryActions(
  manifest: StateUiManifest | null,
  jobState: string,
): ReportPrimaryAction[] {
  let actions = primaryActionsForState(manifest, jobState)
  if (actions.length === 0 && isArtifactsBuildInProgress(jobState)) {
    actions = primaryActionsForState(manifest, "BUILD_ARTIFACTS")
  }
  return actions.filter(a => a.action_key !== "apply")
}

/** True if any report_artifact_tabs artifact_key has content on job artifacts blob. */
export function anyReportArtifactContent(
  artifacts: unknown,
  artifactTabs: Array<{ artifact_key: string }> | undefined,
): boolean {
  if (!artifactTabs?.length) return false
  return artifactTabs.some(t => artifactHasContent(artifacts, t.artifact_key))
}

export function artifactHasContent(artifacts: unknown, key: string): boolean {
  if (!artifacts || typeof artifacts !== "object" || Array.isArray(artifacts)) return false
  const raw = (artifacts as Record<string, unknown>)[key]
  if (raw == null) return false
  if (Array.isArray(raw)) return raw.length > 0
  if (typeof raw === "object") {
    return Object.values(raw as Record<string, unknown>).some(
      v => typeof v === "string" && v.trim().length > 0,
    )
  }
  return false
}

export function printResumeVisible(artifacts: unknown): boolean {
  return artifactHasContent(artifacts, "resume_content")
}

export function printCoverVisible(artifacts: unknown): boolean {
  return artifactHasContent(artifacts, "cover_letter")
}

export function materialsPreviewVisible(
  jobState: string,
  artifacts: unknown,
): boolean {
  if (jobState === "CANDIDATE_REVIEW") return true
  return (
    artifactHasContent(artifacts, "resume_content")
    || artifactHasContent(artifacts, "cover_letter")
  )
}

interface GradeCell {
  grade: string
  gradeTooltip: string
  /** Present on array grade rows; omitted for object-map grades (bullets dim). */
  confidence?: number
}

function gradeAndConfidenceForCol(
  gradesRaw: unknown,
  col: JobListRubricColumn,
): GradeCell {
  if (!gradesRaw) return { grade: "", gradeTooltip: "" }
  const colCode = normalizeRubricVectorKey(col.code)
  const colLabel = normalizeRubricVectorKey(col.label)
  if (Array.isArray(gradesRaw)) {
    const row = (
      gradesRaw as Array<{ vector: string; grade: string; reason?: string; confidence?: number }>
    ).find(i => {
      const vector = normalizeRubricVectorKey(i.vector || "")
      return vector === colCode || vector === colLabel
    })
    if (!row) return { grade: "", gradeTooltip: "" }
    const grade = row.grade || ""
    return {
      grade,
      gradeTooltip: formatGradeDotTooltip(col, grade, row.reason),
      confidence: row.confidence,
    }
  }
  if (typeof gradesRaw === "object") {
    const obj = gradesRaw as Record<string, string>
    const exact = obj[col.code] || obj[col.label]
    if (exact) return { grade: exact, gradeTooltip: formatGradeDotTooltip(col, exact) }
    for (const [key, value] of Object.entries(obj)) {
      const normalized = normalizeRubricVectorKey(key)
      if (normalized === colCode || normalized === colLabel) {
        return { grade: value, gradeTooltip: formatGradeDotTooltip(col, value) }
      }
    }
  }
  return { grade: "", gradeTooltip: "" }
}

/** Normalize job grade payloads for AgentAnalysisHeader (array or letter map). */
export function gradesForHeader(
  raw: unknown,
): Array<{ vector: string; grade: string; confidence?: number; reason?: string }> {
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

function gradeDot(grade: string, tooltip: string) {
  return (
    <span className={`grade-dot dot-${grade.toLowerCase()}`} title={tooltip || undefined}>
      {grade}
    </span>
  )
}

export function buildPhaseTabGradeDots(
  gradesRaw: unknown,
  rubricArtifactKey: string | undefined,
  candidateArtifacts: Record<string, unknown>,
): ReactNode {
  if (!rubricArtifactKey) return null
  const items = candidateArtifacts[rubricArtifactKey]
  if (!Array.isArray(items) || !items.length) return null
  const cols = sortJobListRubricColumns(
    buildJobListRubricColumnsFromArtifact(
      items as Array<{ code?: string; label?: string; importance?: unknown }>,
    ),
  )
  const dots = cols
    .map(col => {
      const { grade, gradeTooltip } = gradeAndConfidenceForCol(gradesRaw, col)
      if (!grade) return null
      return gradeDot(grade, gradeTooltip)
    })
    .filter(Boolean)
  if (!dots.length) return null
  return <>{dots}</>
}

/** Horizontal grade + confidence row for Analysis section headers (AST-950). */
export function buildPhaseSectionGradeConfidenceRow(
  gradesRaw: unknown,
  rubricArtifactKey: string | undefined,
  candidateArtifacts: Record<string, unknown>,
): ReactNode {
  const cells: ReactNode[] = []

  const rubricItems =
    rubricArtifactKey && Array.isArray(candidateArtifacts[rubricArtifactKey])
      ? (candidateArtifacts[rubricArtifactKey] as Array<{
          code?: string
          label?: string
          importance?: unknown
        }>)
      : null

  if (rubricItems && rubricItems.length > 0) {
    const cols = sortJobListRubricColumns(buildJobListRubricColumnsFromArtifact(rubricItems))
    for (const col of cols) {
      const { grade, gradeTooltip, confidence } = gradeAndConfidenceForCol(gradesRaw, col)
      if (!grade) continue
      cells.push(
        <span key={col.code || col.label} className="recommended-report-phase-grade-cell">
          {gradeDot(grade, gradeTooltip)}
          <ConfidenceBullets confidence={confidence} />
        </span>,
      )
    }
  } else if (Array.isArray(gradesRaw) && gradesRaw.length > 0) {
    // Rubric missing — still show graded vectors in array order.
    for (const row of gradesRaw as Array<{
      vector?: string
      grade?: string
      reason?: string
      confidence?: number
    }>) {
      if (!row.vector || !row.grade) continue
      cells.push(
        <span key={row.vector} className="recommended-report-phase-grade-cell">
          {gradeDot(row.grade, row.reason?.trim() || "")}
          <ConfidenceBullets confidence={row.confidence} />
        </span>,
      )
    }
  }

  if (!cells.length) return null
  return <div className="recommended-report-phase-grade-row">{cells}</div>
}

export function formatPhaseTabNavLabel(prefix: string, dots: ReactNode): ReactNode {
  if (!dots) return prefix
  return (
    <span className="recommended-report-tab-label">
      {prefix} {dots}
    </span>
  )
}

/** Plus-address tag for copy-email (Susan UAT: external_job_id → fallback astral_job_id). */
export function emailWithJobPlusTag(email: string, jobTag: string): string {
  const addr = email.trim()
  const tag = jobTag.trim()
  if (!addr || !tag) return addr
  const at = addr.lastIndexOf("@")
  if (at <= 0) return addr
  return `${addr.slice(0, at)}+${tag}@${addr.slice(at + 1)}`
}

export function jobGradesForField(job: Record<string, unknown>, gradesField: string): unknown {
  const jd = job.job_data
  if (jd && typeof jd === "object" && !Array.isArray(jd)) {
    const fromJd = (jd as Record<string, unknown>)[gradesField]
    if (fromJd !== undefined) return fromJd
  }
  return job[gradesField]
}
