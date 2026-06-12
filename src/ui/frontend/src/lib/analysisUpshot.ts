/**
 * Mirrors TASK_CONFIG["analysis_upshot"]["response_schema"] (src/utils/config.py).
 * Persisted JSON lives at job.job_data.analysis_upshot (AST-480).
 */

export type UpshotSegment = {
  segment_key: string
  upshot: string
}

export type UpshotTextItem = {
  text: string
}

export type AnalysisUpshot = {
  take_get: string
  take_do: string
  take_like: string
  take_jd: string
  whole_jd_upshot: string
  segment_upshots: UpshotSegment[]
  candidate_questions: UpshotTextItem[]
  caveats: UpshotTextItem[]
}

/** Convert config snake_case keys to short titles for headings. */
export function snakeCaseToTitle(snake: string): string {
  return snake
    .split("_")
    .filter(Boolean)
    .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(" ")
}

function isPlainObject(raw: unknown): raw is Record<string, unknown> {
  return typeof raw === "object" && raw !== null && !Array.isArray(raw)
}

function isSegmentRow(x: unknown): x is UpshotSegment {
  if (!isPlainObject(x)) return false
  return typeof x.segment_key === "string" && typeof x.upshot === "string"
}

function isTextItem(x: unknown): x is UpshotTextItem {
  return isPlainObject(x) && typeof x.text === "string"
}

function hasSubstantiveContent(u: AnalysisUpshot): boolean {
  const headline = [
    u.take_get,
    u.take_do,
    u.take_like,
    u.take_jd,
    u.whole_jd_upshot,
  ].some(s => typeof s === "string" && s.trim().length > 0)
  if (headline) return true
  if (u.segment_upshots.some(s => s.upshot.trim().length > 0)) return true
  if (u.candidate_questions.some(q => q.text.trim().length > 0)) return true
  if (u.caveats.some(c => c.text.trim().length > 0)) return true
  return false
}

/**
 * Validates shape against the analysis_upshot response_schema; rejects non-objects,
 * missing keys and wrong leaf types; returns null if no substantive content remains.
 */
export function parseAnalysisUpshot(raw: unknown): AnalysisUpshot | null {
  if (!isPlainObject(raw)) return null

  // Legacy upshots may omit take_jd (pre-AST-561); coerce missing headline keys to "".
  const str = (v: unknown) => (typeof v === "string" ? v : "")
  const take_get = str(raw.take_get)
  const take_do = str(raw.take_do)
  const take_like = str(raw.take_like)
  const take_jd = str(raw.take_jd)
  const whole_jd_upshot = str(raw.whole_jd_upshot)
  const segment_upshots = raw.segment_upshots
  const candidate_questions = raw.candidate_questions
  const caveats = raw.caveats

  if (
    (typeof raw.take_get !== "undefined" && typeof raw.take_get !== "string") ||
    (typeof raw.take_do !== "undefined" && typeof raw.take_do !== "string") ||
    (typeof raw.take_like !== "undefined" && typeof raw.take_like !== "string") ||
    (typeof raw.take_jd !== "undefined" && typeof raw.take_jd !== "string") ||
    (typeof raw.whole_jd_upshot !== "undefined" && typeof raw.whole_jd_upshot !== "string")
  )
    return null
  if (!Array.isArray(segment_upshots) || !segment_upshots.every(isSegmentRow)) return null
  if (!Array.isArray(candidate_questions) || !candidate_questions.every(isTextItem)) return null
  if (!Array.isArray(caveats) || !caveats.every(isTextItem)) return null

  const parsed: AnalysisUpshot = {
    take_get,
    take_do,
    take_like,
    take_jd,
    whole_jd_upshot,
    segment_upshots: [...segment_upshots],
    candidate_questions: [...candidate_questions],
    caveats: [...caveats],
  }
  if (!hasSubstantiveContent(parsed)) return null
  return parsed
}
