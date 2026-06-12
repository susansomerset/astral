import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import CompanyDetailModal from "../components/CompanyDetailModal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import type { Column } from "../components/ListPage"

interface Company {
  short_name: string
  company_name: string
  company_website: string
  state: string
  last_scan_at: string | null
  state_history: Array<{ to_state?: string; timestamp?: string }>
  [key: string]: unknown
}

export default function WatchList() {
  const { manifest, loadState } = useStateUi()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<Company[]>([])
  const [columns, setColumns] = useState<Column<Company>[]>([])
  const [loading, setLoading] = useState(true)
  const [viewing, setViewing] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  const load = useCallback(() => {
    if (!selectedId) return
    Promise.all([
      api(`/api/companies?view=watch_list&candidate_id=${encodeURIComponent(selectedId)}`).then(r => r.json()),
      api("/api/shapes/companies").then(r => r.json()),
    ]).then(([data, shapes]) => {
      setRows(Array.isArray(data) ? data : [])
      setColumns(shapes?.list?.watch_list || [])
    }).finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { load() }, [load])

  if (loadState === "loading") {
    return <div className="list-page-status">Loading...</div>
  }
  if (loadState === "error" || !manifest) {
    return <div className="list-page-status">State UI manifest unavailable.</div>
  }

  const bulkTransitions = manifest.company.bulk_transitions

  function handleBulk(action: string, ids: string[]) {
    const bt = bulkTransitions
    const to_state = action === "ignore" ? bt.watch_list_ignore_to_state : bt.watch_list_ack_to_state
    api("/api/companies/bulk_state", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ short_names: ids, to_state }),
    })
      .then(r => r.json())
      .then(res => {
        setToast({ text: `${res.updated} companies updated`, variant: "success" })
        load()
      })
      .catch(() => setToast({ text: "Bulk action failed", variant: "error" }))
  }

  return (
    <>
      <ListPage<Company>
        title="Watch List"
        columns={columns}
        rows={rows}
        idField="short_name"
        loading={loading}
        onRowClick={row => setViewing(row.short_name)}
        bulkActions={[
          { label: "Set to Ignore", onClick: ids => handleBulk("ignore", ids), variant: "danger" },
          { label: "Retry Scrape", onClick: ids => handleBulk("retry", ids) },
        ]}
      />
      <CompanyDetailModal shortName={viewing} onClose={() => setViewing(null)} onSaved={load} />
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
