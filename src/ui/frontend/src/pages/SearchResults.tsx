import { useEffect, useState, type ReactNode } from "react"
import { useSearchParams } from "react-router-dom"
import CompanyDetailModal from "../components/CompanyDetailModal"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import JobDetailModal from "../components/JobDetailModal"
import MeteoriteDetailModal from "../components/MeteoriteDetailModal"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

type EntityType = "job" | "company" | "meteorite"

/** One hit from GET /api/search (AST-2173 src/core/search.py search_entities). */
interface SearchHit {
  entity_id: string | number
  display_name: string
  state: string | null
  tier: "base" | "payload"
  matched_fields: string[]
  jobs_list?: string                  // jobs only
  modal_kind?: "report" | "detail"    // jobs only — which job modal opens
}

type ResultsByType = Record<EntityType, SearchHit[]>

// Key order is render order: Jobs, Companies, Meteorites.
const SECTION_LABELS: Record<EntityType, string> = { job: "Jobs", company: "Companies", meteorite: "Meteorites" }
const ENTITY_TYPES = Object.keys(SECTION_LABELS) as EntityType[]

/** A failed request, or a missing / non-list key, reads as no hits for that type. */
function toResults(data: unknown): ResultsByType {
  const d = (data ?? {}) as Partial<Record<EntityType, unknown>>
  return Object.fromEntries(ENTITY_TYPES.map(t => [t, Array.isArray(d[t]) ? d[t] : []])) as ResultsByType
}

/** AST-2174: /search?q=… — the selected candidate's hits by entity type, rows in API order; each opens its existing modal. */
export default function SearchResults() {
  const [searchParams] = useSearchParams()
  const q = searchParams.get("q") ?? ""
  const { selectedId } = useCandidate()
  // Results carry the candidate + q they answer, so a switch never shows the previous candidate's rows.
  const [result, setResult] = useState<{ key: string; byType: ResultsByType } | null>(null)
  // Bumped on modal close / save to re-fetch the same key in place.
  const [reloadTick, setReloadTick] = useState(0)
  const [open, setOpen] = useState<{ type: EntityType; hit: SearchHit } | null>(null)
  const requestKey = selectedId && q.trim() ? `${selectedId}\n${q}` : null

  useEffect(() => {
    // No candidate or blank q → no request at all (AC 10 / AC 12).
    if (!selectedId || !requestKey) return
    let stale = false
    api(`/api/search?q=${encodeURIComponent(q)}&candidate_id=${encodeURIComponent(selectedId)}`)
      .then(r => (r.ok ? r.json() : null))
      .catch(() => null)
      .then(data => { if (!stale) setResult({ key: requestKey, byType: toResults(data) }) })
    return () => { stale = true }
  }, [selectedId, q, requestKey, reloadTick])

  const reload = () => setReloadTick(t => t + 1)
  const close = () => { setOpen(null); reload() }
  const byType = result && result.key === requestKey ? result.byType : null
  const jobId = (kind: "report" | "detail") =>
    open?.type === "job" && open.hit.modal_kind === kind ? String(open.hit.entity_id) : null

  let body: ReactNode
  if (!selectedId) body = <p className="list-page-status">Select a candidate</p>
  else if (!q.trim()) body = <p className="list-page-status">No results</p>
  else if (!byType) body = <p className="list-page-status">Loading...</p>
  else if (ENTITY_TYPES.every(t => byType[t].length === 0)) body = <p className="list-page-status">No results</p>
  else body = (
    <div className="list-page-table-wrap list-page-table-wrap--scroll">
      {ENTITY_TYPES.filter(t => byType[t].length > 0).map(t => (
        <section key={t}>
          <h2 className="search-results-section-title">{SECTION_LABELS[t]} ({byType[t].length})</h2>
          <table className="list-page-table">
            <thead>
              <tr><th>Name</th><th>State</th><th>Matched fields</th></tr>
            </thead>
            <tbody>
              {byType[t].map(hit => (
                <tr key={String(hit.entity_id)} className="clickable" onClick={() => setOpen({ type: t, hit })}>
                  <td>{hit.display_name}</td>
                  <td>{hit.state ?? "—"}</td>
                  <td>{hit.matched_fields.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </div>
  )

  return (
    <>
      <div className="list-page">
        <div className="list-page-header">
          <h1 className="list-page-title">{q.trim() ? `Search results for “${q.trim()}”` : "Search results"}</h1>
        </div>
        {body}
      </div>
      <JobAnalysisReportModal jobId={jobId("report")} onClose={close} onRefresh={reload} />
      <JobDetailModal jobId={jobId("detail")} onClose={close} onRefresh={reload} />
      <CompanyDetailModal
        shortName={open?.type === "company" ? String(open.hit.entity_id) : null}
        onClose={close}
        onSaved={reload}
      />
      <MeteoriteDetailModal
        meteoriteId={open?.type === "meteorite" ? Number(open.hit.entity_id) : null}
        onClose={close}
      />
    </>
  )
}
