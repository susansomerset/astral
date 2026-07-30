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

/** Live-artifact path for non-list consumers. Skipped/In Review use buildJobListRubricColumnsForGroup (AST-1064). */
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

/** gradeKey → job-carried rubric key (`joblist_grades` → `joblist_rubric`). */
export function jobCarriedRubricKey(gradeKey: string): string {
  if (!gradeKey || !gradeKey.endsWith("_grades")) return ""
  return gradeKey.replace(/_grades$/, "_rubric")
}

/** gradeKey → analysis-time score key (`jd_grades` → `jd_score`). */
export function jobCarriedScoreKey(gradeKey: string): string {
  if (!gradeKey || !gradeKey.endsWith("_grades")) return ""
  return gradeKey.replace(/_grades$/, "_score")
}

/** Aligned-shape fingerprint: sorted label|code tokens (ignores importance / descriptions). */
export function jobListRubricFingerprint(
  rubricItems: Array<{ code?: string; label?: string }> | null | undefined,
): string {
  if (!Array.isArray(rubricItems) || !rubricItems.length) return ""
  const tokens: string[] = []
  for (const item of rubricItems) {
    const label = normalizeRubricVectorKey(item.label || item.code || "")
    const code = (item.code || "").trim().toUpperCase()
    const tok = `${label}|${code}`
    if (label || code) tokens.push(tok)
  }
  if (!tokens.length) return ""
  return tokens.sort().join("\0")
}

/** Grades-only fingerprint when `*_rubric` is missing (pre-AST-1063 jobs). */
export function jobListRubricFingerprintFromGrades(grades: unknown): string {
  if (Array.isArray(grades)) {
    const tokens = (grades as Array<{ vector?: string }>)
      .map(g => normalizeRubricVectorKey(g.vector || ""))
      .filter(Boolean)
    if (!tokens.length) return ""
    return tokens.sort().join("\0")
  }
  if (grades && typeof grades === "object") {
    const tokens = Object.keys(grades as object)
      .map(k => normalizeRubricVectorKey(k))
      .filter(Boolean)
    if (!tokens.length) return ""
    return tokens.sort().join("\0")
  }
  return ""
}

export type JobListRubricGroup<T extends Record<string, unknown> = Record<string, unknown>> = {
  fingerprint: string
  jobs: T[]
  /** First job in group — column source (stable first-encounter order). */
  columnSourceJob: T
}

/** Partition jobs by aligned job-carried rubric fingerprint (AST-1064). */
export function groupJobsByAlignedRubric<T extends Record<string, unknown>>(
  jobs: T[],
  gradeKey: string,
): JobListRubricGroup<T>[] {
  const rubricKey = jobCarriedRubricKey(gradeKey)
  const byFp = new Map<string, JobListRubricGroup<T>>()
  const order: string[] = []

  for (const job of jobs) {
    let fingerprint = ""
    const rubric = rubricKey ? job[rubricKey] : undefined
    if (Array.isArray(rubric) && rubric.length) {
      fingerprint = jobListRubricFingerprint(
        rubric as Array<{ code?: string; label?: string }>,
      )
    }
    if (!fingerprint && gradeKey) {
      const fromGrades = jobListRubricFingerprintFromGrades(job[gradeKey])
      if (fromGrades) fingerprint = `grades:${fromGrades}`
    }
    if (!fingerprint) fingerprint = "__empty__"

    const existing = byFp.get(fingerprint)
    if (existing) {
      existing.jobs.push(job)
    } else {
      const group: JobListRubricGroup<T> = {
        fingerprint,
        jobs: [job],
        columnSourceJob: job,
      }
      byFp.set(fingerprint, group)
      order.push(fingerprint)
    }
  }

  return order.map(fp => byFp.get(fp)!)
}

/** Columns from job-carried `*_rubric` (or grades fallback) — never live candidate artifacts. */
export function buildJobListRubricColumnsForGroup(opts: {
  gradeKey: string
  columnSourceJob: Record<string, unknown>
}): JobListRubricColumn[] {
  const { gradeKey, columnSourceJob } = opts
  const rubricKey = jobCarriedRubricKey(gradeKey)
  const items = rubricKey ? columnSourceJob[rubricKey] : undefined
  if (Array.isArray(items) && items.length) {
    return buildJobListRubricColumnsFromArtifact(
      items as Array<{
        code?: string
        label?: string
        importance?: unknown
        grade_descriptions?: Array<{ grade?: string; description?: string }>
      }>,
    )
  }
  return buildJobListRubricColumnsFromJobGrades(gradeKey, [columnSourceJob])
}

/** Prefer `{prefix}_score` for the section grade field, else `latest_score`. */
export function analysisTimeScoreForJob(
  job: Record<string, unknown>,
  gradeKey: string,
): number | null {
  if (!gradeKey) {
    return typeof job.latest_score === "number" ? job.latest_score : null
  }
  const scoreKey = jobCarriedScoreKey(gradeKey)
  const phase = scoreKey ? job[scoreKey] : undefined
  if (typeof phase === "number") return phase
  if (typeof job.latest_score === "number") return job.latest_score
  return null
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
