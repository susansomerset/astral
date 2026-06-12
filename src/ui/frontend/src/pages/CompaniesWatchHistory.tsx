import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import type { Column } from "../components/ListPage"

interface ScanRow {
  batch_id: string
  short_name: string
  company_name: string | null
  scan_completed_at: string
  total_found: number | null
  new: number | null
  duplicates: number | null
  title_mismatch: number | null
  status: string
  failure_message: string | null
  [key: string]: unknown
}

export default function WatchHistory() {
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<ScanRow[]>([])
  const [columns, setColumns] = useState<Column<ScanRow>[]>([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(() => {
    if (!selectedId) return
    Promise.all([
      api(`/api/companies/scan_history?candidate_id=${encodeURIComponent(selectedId)}`).then(r => r.json()),
      api("/api/shapes/companies").then(r => r.json()),
    ]).then(([data, shapes]) => {
      // Each row needs a unique id — composite of batch_id + short_name
      const withId = (Array.isArray(data) ? data : []).map((r: ScanRow) => ({
        ...r,
        _id: `${r.batch_id}__${r.short_name}`,
      }))
      setRows(withId)
      const cols: Column<ScanRow>[] = shapes?.list?.watch_history || []
      // Add a status renderer for visual distinction
      setColumns(cols.map(c => {
        if (c.key === "status") {
          return {
            ...c,
            render: (val: unknown) => (
              <span style={{
                color: val === "success" ? "var(--success, #4caf50)" : "var(--danger, #f44336)",
                fontWeight: 600, fontSize: 12,
              }}>
                {String(val || "")}
              </span>
            ),
          }
        }
        return c
      }))
    }).finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { load() }, [load])

  return (
    <ListPage<ScanRow>
      title="Watch History"
      columns={columns}
      rows={rows}
      idField="_id"
      loading={loading}
      emptyMessage="No scan history recorded yet."
    />
  )
}
