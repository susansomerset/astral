import { useEffect, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import Modal from "./Modal"
import ReportSectionList, { type ReportSectionDef } from "./ReportSectionList"
import JobTitleText from "./JobTitleText"
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
  /** Optional: host refreshes its list after a successful candidate save (AST-2224). */
  onSaved?: () => void
}

type DetailEnvelope = {
  sections: ReportSectionDef[]
  meteorite: MeteoriteDetail | null
  editable: boolean
  editableFields: string[]
  stateOptions: string[]
  defaultSaveState: string
}

/** First open → server default; after PUT 200 → stored meteorite.state (Joan round=1). */
function buildDraft(
  editableFields: string[],
  meteorite: MeteoriteDetail | null,
  defaultSaveState: string,
  stateSource: "default" | "stored",
): Record<string, string> {
  const draft: Record<string, string> = {}
  for (const key of editableFields) {
    if (key === "state") {
      draft[key] = stateSource === "default" ? defaultSaveState : String(meteorite?.state ?? "")
    } else {
      draft[key] = String(meteorite?.[key] ?? "")
    }
  }
  return draft
}

function parseDetailPayload(data: Record<string, unknown>): DetailEnvelope {
  const rawSections = Array.isArray(data.sections) ? data.sections : []
  const sections = rawSections.map((s: { section_id: string; nav_label: string; default_expanded?: boolean }) => ({
    section_id: s.section_id,
    nav_label: s.nav_label,
    default_expanded: Boolean(s.default_expanded),
  }))
  return {
    sections,
    meteorite: (data.meteorite as MeteoriteDetail | null) ?? null,
    editable: data.editable === true,
    editableFields: Array.isArray(data.editable_fields) ? data.editable_fields.map(String) : [],
    stateOptions: Array.isArray(data.state_options) ? data.state_options.map(String) : [],
    defaultSaveState: typeof data.default_save_state === "string" ? data.default_save_state : "",
  }
}

/** AST-1749 read-only detail; AST-2224 candidate edit form when server says editable. */
export default function MeteoriteDetailModal({ meteoriteId, onClose, onSaved }: Props) {
  const [sections, setSections] = useState<ReportSectionDef[]>([])
  const [meteorite, setMeteorite] = useState<MeteoriteDetail | null>(null)
  const [editable, setEditable] = useState(false)
  const [editableFields, setEditableFields] = useState<string[]>([])
  const [stateOptions, setStateOptions] = useState<string[]>([])
  const [draft, setDraft] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function clearDetail() {
    setMeteorite(null)
    setSections([])
    setEditable(false)
    setEditableFields([])
    setStateOptions([])
    setDraft({})
    setSaveError(null)
  }

  /** Sets envelope state; draft is caller's job (stateSource differs open vs post-save). */
  function applyDetailPayload(data: Record<string, unknown>): DetailEnvelope {
    const parsed = parseDetailPayload(data)
    setSections(parsed.sections)
    setMeteorite(parsed.meteorite)
    setEditable(parsed.editable)
    setEditableFields(parsed.editableFields)
    setStateOptions(parsed.stateOptions)
    // defaultSaveState lives on the returned envelope only — used for buildDraft, not render.
    return parsed
  }

  useEffect(() => {
    if (meteoriteId == null) {
      clearDetail()
      setError(null)
      return
    }
    setLoading(true)
    setError(null)
    setSaveError(null)
    api(`/api/meteorites/${meteoriteId}`)
      .then(async r => {
        if (r.status === 404) {
          setError("Meteorite not found")
          clearDetail()
          return
        }
        if (!r.ok) {
          setError("Failed to load meteorite")
          clearDetail()
          return
        }
        const data = await r.json()
        const parsed = applyDetailPayload(data)
        if (parsed.editable) {
          setDraft(buildDraft(parsed.editableFields, parsed.meteorite, parsed.defaultSaveState, "default"))
        } else {
          setDraft({})
          setSaveError(null)
        }
      })
      .catch(() => {
        setError("Failed to load meteorite")
        clearDetail()
      })
      .finally(() => setLoading(false))
  }, [meteoriteId])

  async function handleSave() {
    if (meteoriteId == null || !editable || saving) return
    setSaving(true)
    setSaveError(null)
    const body: Record<string, string> = {}
    for (const key of editableFields) {
      body[key] = draft[key] ?? ""
    }
    try {
      const res = await api(`/api/meteorites/${meteoriteId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}))
        setSaveError(String((errBody as { error?: string }).error ?? "Save failed"))
        return
      }
      const data = await res.json()
      const parsed = applyDetailPayload(data)
      // Post-save: seed state from stored row, not default_save_state.
      setDraft(buildDraft(parsed.editableFields, parsed.meteorite, parsed.defaultSaveState, "stored"))
      onSaved?.()
    } catch {
      setSaveError("Save failed")
    } finally {
      setSaving(false)
    }
  }

  if (meteoriteId == null) return null

  const title = modalTitle(meteorite, meteoriteId)

  return (
    <Modal
      open
      title={title}
      onClose={onClose}
      showFooter={editable}
      onSave={editable ? handleSave : undefined}
      size="wide"
    >
      {loading ? (
        <p className="list-page-status">Loading...</p>
      ) : error ? (
        <p className="list-page-status">{error}</p>
      ) : meteorite == null ? (
        <p className="list-page-status">Meteorite not found</p>
      ) : (
        <>
          {editable ? (
            <div className="meteorite-edit-form">
              {editableFields.map(key => (
                <div key={key} className="job-analysis-upshot-body">
                  <label>
                    {key}
                    {key === "content" ? (
                      <textarea
                        className="entity-story-content"
                        value={draft[key] ?? ""}
                        onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))}
                      />
                    ) : key === "state" ? (
                      <select
                        value={draft[key] ?? ""}
                        onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))}
                      >
                        {stateOptions.map(opt => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={draft[key] ?? ""}
                        onChange={e => setDraft(d => ({ ...d, [key]: e.target.value }))}
                      />
                    )}
                  </label>
                </div>
              ))}
              {saveError ? <p className="list-page-status">{saveError}</p> : null}
              {saving ? <p className="list-page-status">Saving…</p> : null}
            </div>
          ) : null}
          <ReportSectionList
            sections={sections}
            renderSection={sectionId => renderMeteoriteSection(sectionId, meteorite)}
          />
        </>
      )}
    </Modal>
  )
}

function modalTitle(m: MeteoriteDetail | null, id: number): ReactNode {
  if (!m) return `Meteorite ${id}`
  const title = nonEmptyTrimmed(m.job_title)
  const employer = nonEmptyTrimmed(m.employer_name)
  // AST-1981: only the job-title part is cut (JobTitleText); the employer suffix stays whole.
  // fallback={null} is never reached — title is non-empty in both branches.
  if (title && employer) return <><JobTitleText title={title} fallback={null} />{` — ${employer}`}</>
  if (title) return <JobTitleText title={title} fallback={null} />
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
