import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import CompanyDetailModal from "../components/CompanyDetailModal"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import type { Column } from "../components/ListPage"

interface Company {
  short_name: string
  company_name: string
  state: string
  state_updated_at: string | null
  [key: string]: unknown
}

const METEORITE_COLUMNS: Column<Company>[] = [
  { key: "short_name", label: "Short Name", sortable: true },
  { key: "company_name", label: "Company", sortable: true },
  { key: "state", label: "State", sortable: true },
  {
    key: "state_updated_at",
    label: "State Updated",
    sortable: true,
    defaultDesc: true,
    type: "datetime",
  },
]

export default function Meteorite() {
  const { loadState } = useStateUi()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [viewing, setViewing] = useState<string | null>(null)

  const load = useCallback(() => {
    if (!selectedId) return
    api(
      `/api/companies?view=meteorite_list&candidate_id=${encodeURIComponent(selectedId)}`,
    )
      .then(r => r.json())
      .then(data => {
        setRows(Array.isArray(data) ? data : [])
      })
      .finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => {
    load()
  }, [load])

  if (loadState === "loading") {
    return <div className="list-page-status">Loading...</div>
  }
  if (loadState === "error") {
    return <div className="list-page-status">State UI manifest unavailable.</div>
  }

  return (
    <>
      <ListPage<Company>
        title="Meteorite"
        columns={METEORITE_COLUMNS}
        rows={rows}
        idField="short_name"
        loading={loading}
        onRowClick={row => setViewing(row.short_name)}
      />
      <CompanyDetailModal shortName={viewing} onClose={() => setViewing(null)} onSaved={load} />
    </>
  )
}
