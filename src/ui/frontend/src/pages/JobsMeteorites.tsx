import { useCallback, useEffect, useMemo, useState } from "react"
import ListPage, { type Column } from "../components/ListPage"
import JobAnalysisReportModal from "../components/JobAnalysisReportModal"
import JobTitleText from "../components/JobTitleText"
import MeteoriteDetailModal from "../components/MeteoriteDetailModal"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

/** List row from GET /api/candidates/<id>/meteorites (AST-1748; job_state AST-1974). */
interface MeteoriteRow {
  id: number
  candidate_id: string
  state: string | null
  job_title: string | null
  employer_name: string | null
  classify_outcome: string | null
  link: string | null
  astral_job_id: string | null
  job_state: string | null
  [key: string]: unknown
}

type ApiColumn = {
  key: string
  label: string
  sortable?: boolean
  defaultDesc?: boolean
  type?: string
}

/** AST-1749: Jobs → Meteorites — candidate-scoped staging-row list (read-only); AST-1976 landed-job state + in-page job report link. */
export default function JobsMeteorites() {
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<MeteoriteRow[]>([])
  const [apiColumns, setApiColumns] = useState<ApiColumn[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingId, setViewingId] = useState<number | null>(null)
  const [reportJobId, setReportJobId] = useState<string | null>(null)

  const load = useCallback(() => {
    if (!selectedId) {
      setRows([])
      setApiColumns([])
      setLoading(false)
      return
    }
    setLoading(true)
    api(`/api/candidates/${encodeURIComponent(selectedId)}/meteorites`)
      .then(async r => {
        if (!r.ok) {
          setRows([])
          setApiColumns([])
          return
        }
        const data = await r.json()
        setApiColumns(Array.isArray(data.columns) ? data.columns : [])
        setRows(Array.isArray(data.meteorites) ? data.meteorites : [])
      })
      .catch(() => {
        setRows([])
        setApiColumns([])
      })
      .finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => {
    load()
  }, [load])

  const columns: Column<MeteoriteRow>[] = useMemo(
    () =>
      apiColumns.map(c => {
        const col: Column<MeteoriteRow> = {
          key: c.key,
          label: c.label,
          sortable: c.sortable !== false,
          ...(c.defaultDesc ? { defaultDesc: true } : {}),
          ...(c.type ? { type: c.type } : {}),
        }
        // Job cell opens the landed job's report in place; stopPropagation keeps the row click (Meteorite modal) from also firing.
        if (c.key === "astral_job_id") {
          col.render = value => {
            const jobId = String(value ?? "")
            if (!jobId) return "—"
            return (
              <button
                type="button"
                className="dispatch-batch-link"
                onClick={e => {
                  e.stopPropagation()
                  setReportJobId(jobId)
                }}
                title="Open job report"
              >
                {jobId}
              </button>
            )
          }
        }
        // Raw job.state (matches GET /api/jobs/<id>.state); null = not landed or job row gone.
        if (c.key === "job_state") {
          col.render = value => (value ? String(value) : "—")
        }
        // AST-1981: job title cut at the job-title length (not ListPage's 30) — element render bypasses ListPage string truncation.
        if (c.key === "job_title") {
          col.render = value => <JobTitleText title={typeof value === "string" ? value : null} fallback="—" />
        }
        return col
      }),
    [apiColumns],
  )

  return (
    <>
      <ListPage<MeteoriteRow>
        title="Meteorites"
        columns={columns}
        rows={rows}
        idField="id"
        loading={loading}
        emptyMessage="No meteorites yet"
        onRowClick={row => setViewingId(Number(row.id))}
      />
      <MeteoriteDetailModal meteoriteId={viewingId} onClose={() => setViewingId(null)} />
      <JobAnalysisReportModal
        jobId={reportJobId}
        onClose={() => setReportJobId(null)}
        onRefresh={load}
      />
    </>
  )
}
