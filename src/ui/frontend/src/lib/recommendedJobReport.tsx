import type { ReactNode } from "react"
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
      gradesRaw as Array<{ vector: string; grade: string; reason?: string }>
    ).find(i => {
      const vector = normalizeRubricVectorKey(i.vector || "")
      return vector === colCode || vector === colLabel
    })
    if (!row) return { grade: "", gradeTooltip: "" }
    const grade = row.grade || ""
    return { grade, gradeTooltip: formatGradeDotTooltip(col, grade, row.reason) }
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
