/** AST-359: shared rubric vector label formatting for UI tables and analysis headers. */

export const RUBRIC_DEFAULT_IMPORTANCE = 5

/** Integer 1–10 for UI + saves; missing/invalid in stored JSON → default until normalize on save. */
export function rubricItemImportance(item: { importance?: unknown }): number {
  const n = item.importance
  if (typeof n === "number" && Number.isInteger(n) && !Number.isNaN(n) && n >= 1 && n <= 10) return n
  return RUBRIC_DEFAULT_IMPORTANCE
}

/** Strip trailing " (AB)" suffix from model vector names (matches Jobs* pages). */
export function normalizeRubricVectorKey(value: string): string {
  return value.replace(/\s*\([A-Z]{2}\)\s*$/, "").trim().toLowerCase()
}

/** AST-437: compact job-list table column (code visible; tooltip = `Label (n)`). */
export interface JobListRubricColumn {
  code: string
  label: string
  importance: number
  headerCode: string
  headerTooltip: string
  /** Per-letter rubric text for grade-dot hover (from artifact `grade_descriptions`). */
  gradeDescriptions: Record<string, string>
}

export function parseGradeDescriptions(
  rows?: Array<{ grade?: string; description?: string }>,
): Record<string, string> {
  const out: Record<string, string> = {}
  if (!Array.isArray(rows)) return out
  for (const r of rows) {
    const g = (r.grade ?? "").trim().toUpperCase()
    const d = (r.description ?? "").trim()
    if (g && d) out[g] = d
  }
  return out
}

/** Grade-dot tooltip: job `reason` when present, else rubric criterion text for that letter. */
export function formatGradeDotTooltip(
  col: JobListRubricColumn,
  grade: string,
  reasonFromJob?: string,
): string {
  const fromJob = (reasonFromJob ?? "").trim()
  if (fromJob) return fromJob
  const letter = (grade ?? "").trim().toUpperCase()
  if (!letter) return ""
  return col.gradeDescriptions[letter] ?? ""
}

/** Tooltip for job-list rubric `<th title=…>` — `Label (7)` not full editor header. */
export function formatRubricColumnTooltip(label: string | undefined, importance?: number): string {
  const lab = (label ?? "").trim() || "??"
  const imp = rubricItemImportance({ importance })
  return `${lab} (${imp})`
}

export function resolveRubricHeaderCode(item: { code?: string; label?: string }): string {
  return item.code || item.label?.slice(0, 2).toUpperCase() || "??"
}

export function sortJobListRubricColumns(cols: JobListRubricColumn[]): JobListRubricColumn[] {
  return [...cols].sort((a, b) => b.importance - a.importance || a.code.localeCompare(b.code))
}

export function buildJobListRubricColumnsFromArtifact(
  items: Array<{ code?: string; label?: string; importance?: unknown; grade_descriptions?: Array<{ grade?: string; description?: string }> }>,
): JobListRubricColumn[] {
  const cols = items.map(item => {
    const code = resolveRubricHeaderCode(item)
    const label = item.label || item.code || "??"
    const importance = rubricItemImportance(item)
    return {
      code,
      label,
      importance,
      headerCode: code,
      headerTooltip: formatRubricColumnTooltip(label, importance),
      gradeDescriptions: parseGradeDescriptions(item.grade_descriptions),
    }
  })
  return sortJobListRubricColumns(cols)
}

export function buildJobListRubricColumnsFromJobGrades(
  gradeKey: string,
  jobs: Array<Record<string, unknown>>,
): JobListRubricColumn[] {
  for (const job of jobs) {
    const g = job[gradeKey]
    if (!g) continue
    if (Array.isArray(g)) {
      return sortJobListRubricColumns(
        (g as Array<{ vector: string }>).map(i => {
          const label = i.vector
          return {
            code: label,
            label,
            importance: RUBRIC_DEFAULT_IMPORTANCE,
            headerCode: label,
            headerTooltip: formatRubricColumnTooltip(label, RUBRIC_DEFAULT_IMPORTANCE),
            gradeDescriptions: {},
          }
        }),
      )
    }
    if (typeof g === "object") {
      return sortJobListRubricColumns(
        Object.keys(g as object).map(k => ({
          code: k,
          label: k,
          importance: RUBRIC_DEFAULT_IMPORTANCE,
          headerCode: k,
          headerTooltip: formatRubricColumnTooltip(k, RUBRIC_DEFAULT_IMPORTANCE),
          gradeDescriptions: {},
        })),
      )
    }
  }
  return []
}

export function buildJobListRubricColumns(opts: {
  rubricArtifactKey?: string
  artifacts: Record<string, unknown>
  gradeKey: string
  jobs: Array<Record<string, unknown>>
}): JobListRubricColumn[] {
  const { rubricArtifactKey, artifacts, gradeKey, jobs } = opts
  if (rubricArtifactKey) {
    const items = artifacts[rubricArtifactKey]
    if (Array.isArray(items) && items.length) {
      return buildJobListRubricColumnsFromArtifact(items as Array<{ code?: string; label?: string; importance?: unknown }>)
    }
  }
  return buildJobListRubricColumnsFromJobGrades(gradeKey, jobs)
}

/** `{importance} - {label} ({code})` with fallback when code absent (AST-359 Stage 4). */
export function formatRubricVectorHeader(
  importance: number | undefined,
  label: string | undefined,
  code: string | undefined,
): string {
  const imp =
    typeof importance === "number" && importance >= 1 && importance <= 10
      ? importance
      : RUBRIC_DEFAULT_IMPORTANCE
  const lab = (label ?? "").trim() || "??"
  const cd = (code ?? "").trim()
  if (cd) return `${imp} - ${lab} (${cd})`
  return `${imp} - ${lab}`
}
