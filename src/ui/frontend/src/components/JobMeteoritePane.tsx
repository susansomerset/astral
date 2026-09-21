import { type ReactNode } from "react"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"

export type RelatedMeteorite = {
  id: number | string | null
  created_at: string | null
  updated_at: string | null
  state_changed_at: string | null
  estelle_notified_at: string | null
  link: string | null
  classify_outcome: string | null
  content: string | null
  state: string | null
  source_kind: string | null
  source_id: string | null
  error: string | null
}

type Props = {
  sections: readonly ReportSectionDef[]
  relatedMeteorite: RelatedMeteorite
}

/** Recommended Job Report Meteorite — read-only staging-row provenance (AST-1692). */
export default function JobMeteoritePane({ sections, relatedMeteorite }: Props) {
  return (
    <ReportSectionList
      sections={sections}
      renderSection={(sectionId) => renderMeteoriteSection(sectionId, relatedMeteorite)}
    />
  )
}

function isNavigableHttpLink(raw: string | null | undefined): boolean {
  if (raw == null) return false
  const t = raw.trim()
  return t.startsWith("http://") || t.startsWith("https://")
}

function formatMeteoriteAiContent(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2)
  } catch {
    return raw
  }
}

function renderFieldRows(rows: Array<{ label: string; value: string }>): ReactNode {
  if (rows.length === 0) {
    return <p className="recommended-report-empty">No values on file.</p>
  }
  return (
    <>
      {rows.map(r => (
        <div key={r.label} className="job-analysis-upshot-body">
          {r.label}: {r.value}
        </div>
      ))}
    </>
  )
}

function nonEmptyTrimmed(value: unknown): string | null {
  const t = String(value ?? "").trim()
  return t === "" ? null : t
}

function renderMeteoriteSection(sectionId: string, m: RelatedMeteorite): ReactNode {
  if (sectionId === "meteorite_timestamps") {
    const rows: Array<{ label: string; value: string }> = []
    for (const label of ["created_at", "updated_at", "state_changed_at"] as const) {
      const v = nonEmptyTrimmed(m[label])
      if (v) rows.push({ label, value: v })
    }
    if (m.estelle_notified_at != null) {
      const v = nonEmptyTrimmed(m.estelle_notified_at)
      if (v) rows.push({ label: "estelle_notified_at", value: v })
    }
    return renderFieldRows(rows)
  }

  if (sectionId === "meteorite_link") {
    const link = (m.link ?? "").trim()
    if (!link) {
      return <p className="recommended-report-empty">No link on file.</p>
    }
    if (isNavigableHttpLink(link)) {
      return (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          className="recommended-report-title-link"
        >
          {link}
        </a>
      )
    }
    return <p className="job-analysis-upshot-body">{link}</p>
  }

  if (sectionId === "meteorite_ai") {
    const outcome = m.classify_outcome != null ? nonEmptyTrimmed(m.classify_outcome) : null
    const content = m.content != null ? nonEmptyTrimmed(m.content) : null
    if (!outcome && !content) {
      return <p className="recommended-report-empty">No AI content on file.</p>
    }
    return (
      <>
        {outcome ? (
          <div className="job-analysis-upshot-body">classify_outcome: {outcome}</div>
        ) : null}
        {content ? (
          <textarea
            className="entity-story-content"
            readOnly
            value={formatMeteoriteAiContent(String(m.content))}
          />
        ) : null}
      </>
    )
  }

  if (sectionId === "meteorite_provenance") {
    const rows: Array<{ label: string; value: string }> = []
    for (const label of ["id", "state", "source_kind", "source_id"] as const) {
      const v = nonEmptyTrimmed(m[label])
      if (v) rows.push({ label, value: v })
    }
    if (m.error != null) {
      const v = nonEmptyTrimmed(m.error)
      if (v) rows.push({ label: "error", value: v })
    }
    return renderFieldRows(rows)
  }

  return null
}
