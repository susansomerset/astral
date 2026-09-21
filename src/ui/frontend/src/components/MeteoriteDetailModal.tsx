import { useEffect, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import Modal from "./Modal"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import api from "../lib/api"

type MeteoriteDetail = {
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
  job_title: string | null
  employer_name: string | null
  astral_job_id: string | null
  [key: string]: unknown
}

type Props = {
  meteoriteId: number | null
  onClose: () => void
}

/** AST-1749: read-only Jobs → Meteorites detail (content + metadata + link/deeplink honesty). */
export default function MeteoriteDetailModal({ meteoriteId, onClose }: Props) {
  const [sections, setSections] = useState<ReportSectionDef[]>([])
  const [meteorite, setMeteorite] = useState<MeteoriteDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (meteoriteId == null) {
      setMeteorite(null)
      setSections([])
      setError(null)
      return
    }
    setLoading(true)
    setError(null)
    api(`/api/meteorites/${meteoriteId}`)
      .then(async r => {
        if (r.status === 404) {
          setError("Meteorite not found")
          setMeteorite(null)
          setSections([])
          return
        }
        if (!r.ok) {
          setError("Failed to load meteorite")
          setMeteorite(null)
          setSections([])
          return
        }
        const data = await r.json()
        const rawSections = Array.isArray(data.sections) ? data.sections : []
        setSections(
          rawSections.map((s: { section_id: string; nav_label: string; default_expanded?: boolean }) => ({
            section_id: s.section_id,
            nav_label: s.nav_label,
            default_expanded: Boolean(s.default_expanded),
          })),
        )
        setMeteorite(data.meteorite ?? null)
      })
      .catch(() => {
        setError("Failed to load meteorite")
        setMeteorite(null)
        setSections([])
      })
      .finally(() => setLoading(false))
  }, [meteoriteId])

  if (meteoriteId == null) return null

  const title = modalTitle(meteorite, meteoriteId)

  return (
    <Modal open title={title} onClose={onClose} showFooter={false} size="wide">
      {loading ? (
        <p className="list-page-status">Loading...</p>
      ) : error ? (
        <p className="list-page-status">{error}</p>
      ) : meteorite == null ? (
        <p className="list-page-status">Meteorite not found</p>
      ) : (
        <ReportSectionList
          sections={sections}
          renderSection={sectionId => renderMeteoriteSection(sectionId, meteorite)}
        />
      )}
    </Modal>
  )
}

function modalTitle(m: MeteoriteDetail | null, id: number): string {
  if (!m) return `Meteorite ${id}`
  const title = nonEmptyTrimmed(m.job_title)
  const employer = nonEmptyTrimmed(m.employer_name)
  if (title && employer) return `${title} — ${employer}`
  if (title) return title
  if (employer) return employer
  return `Meteorite ${id}`
}

function isNavigableHttpLink(raw: string | null | undefined): boolean {
  if (raw == null) return false
  const t = raw.trim()
  return t.startsWith("http://") || t.startsWith("https://")
}

function formatMeteoriteContent(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2)
  } catch {
    return raw
  }
}

function nonEmptyTrimmed(value: unknown): string | null {
  const t = String(value ?? "").trim()
  return t === "" ? null : t
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

function renderMeteoriteSection(sectionId: string, m: MeteoriteDetail): ReactNode {
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

  if (sectionId === "meteorite_content") {
    const outcome = m.classify_outcome != null ? nonEmptyTrimmed(m.classify_outcome) : null
    const content = m.content != null ? nonEmptyTrimmed(m.content) : null
    if (!outcome && !content) {
      return <p className="recommended-report-empty">No content on file.</p>
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
            value={formatMeteoriteContent(String(m.content))}
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

  if (sectionId === "meteorite_job") {
    const jobId = String(m.astral_job_id ?? "").trim()
    if (!jobId) {
      return null
    }
    return (
      <Link
        to={`/jobs/detail/${encodeURIComponent(jobId)}`}
        className="recommended-report-title-link"
      >
        Open job {jobId}
      </Link>
    )
  }

  return null
}
