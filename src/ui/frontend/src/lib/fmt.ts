let _timezone = "UTC"

/** Set the IANA timezone used by fmtTime's default (e.g. "America/New_York"). */
export function setFmtTimezone(tz: string) { _timezone = tz }

/** Format a UTC timestamp string, 12h, down to seconds.
 *  e.g. "3/5/26, 4:48:11 PM"
 *  Returns "—" for null/undefined/empty.
 *  Prefer using <Time value={...}/> in React components — it derives
 *  the timezone from CandidateContext at render time. */
export function fmtTime(iso: string | null | undefined, tz?: string): string {
  if (!iso) return "—"
  // DB stores UTC without a Z suffix — JS would misinterpret as local time
  const raw = iso.endsWith("Z") || /[+-]\d{2}:\d{2}$/.test(iso) ? iso : iso + "Z"
  const d = new Date(raw)
  if (isNaN(d.getTime())) return String(iso)
  return d.toLocaleString("en-US", {
    timeZone: tz || _timezone,
    year: "2-digit",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  })
}

/**
 * Format a cell value by number_format token (from UI_CONFIG column_types).
 * Returns "—" for null/undefined. Falls back to String(value) for unknown formats.
 */
export function formatCell(value: unknown, numberFormat: string | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—"
  const n = Number(value)
  switch (numberFormat) {
    case "integer":  return isNaN(n) ? String(value) : n.toLocaleString("en-US", { maximumFractionDigits: 0 })
    case "decimal":  return isNaN(n) ? String(value) : n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 4 })
    case "currency": return isNaN(n) ? String(value) : "$" + n.toLocaleString("en-US", { minimumFractionDigits: 4, maximumFractionDigits: 4 })
    case "date":     return fmtTime(String(value)).split(",")[0]  // date portion only
    case "datetime": return fmtTime(String(value))
    default:         return String(value)
  }
}
