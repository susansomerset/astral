import { useCallback, useEffect, useMemo, useState } from "react"
import ListPage, { type Column } from "../components/ListPage"
import MeteoriteDetailModal from "../components/MeteoriteDetailModal"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

/** List row from GET /api/candidates/<id>/meteorites (AST-1748). */
interface MeteoriteRow {
  id: number
  candidate_id: string
  state: string | null
  job_title: string | null
  employer_name: string | null
  classify_outcome: string | null
  link: string | null
  astral_job_id: string | null
  [key: string]: unknown
}

type ApiColumn = {
  key: string
  label: string
  sortable?: boolean
  defaultDesc?: boolean
  type?: string
}

/** AST-1749: Jobs → Meteorites — candidate-scoped staging-row list (read-only). */
export default function JobsMeteorites() {
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<MeteoriteRow[]>([])
  const [apiColumns, setApiColumns] = useState<ApiColumn[]>([])
  const [loading, setLoading] = useState(true)
  const [viewingId, setViewingId] = useState<number | null>(null)

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
      apiColumns.map(c => ({
        key: c.key,
        label: c.label,
        sortable: c.sortable !== false,
        ...(c.defaultDesc ? { defaultDesc: true } : {}),
        ...(c.type ? { type: c.type } : {}),
      })),
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
    </>
  )
}
