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
  state: string
  prefilter_company_notes: string
  state_updated_at: string | null
  state_history: Array<{ to_state?: string; timestamp?: string }>
  [key: string]: unknown
}

export default function Ignored() {
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
      api(`/api/companies?view=ignored&candidate_id=${encodeURIComponent(selectedId)}`).then(r => r.json()),
      api("/api/shapes/companies").then(r => r.json()),
    ]).then(([data, shapes]) => {
      setRows(Array.isArray(data) ? data : [])
      setColumns(shapes?.list?.ignored || [])
    }).finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { load() }, [load])

  if (loadState === "loading") {
    return <div className="list-page-status">Loading...</div>
  }
  if (loadState === "error" || !manifest) {
    return <div className="list-page-status">State UI manifest unavailable.</div>
  }

  const ignoredListToState = manifest.company.bulk_transitions.ignored_list_to_state

  function handleMoveToWatch(ids: string[]) {
    api("/api/companies/bulk_state", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        short_names: ids,
        to_state: ignoredListToState,
      }),
    })
      .then(r => r.json())
      .then(res => {
        setToast({ text: `${res.updated} precious snowflakes moved to watch list`, variant: "success" })
        load()
      })
      .catch(() => setToast({ text: "Move failed", variant: "error" }))
  }

  return (
    <>
      <ListPage<Company>
        title="Ignored"
        columns={columns}
        rows={rows}
        idField="short_name"
        loading={loading}
        onRowClick={row => setViewing(row.short_name)}
        bulkActions={[
          { label: "Move to Watch", onClick: handleMoveToWatch },
        ]}
      />
      <CompanyDetailModal shortName={viewing} onClose={() => setViewing(null)} onSaved={load} />
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
