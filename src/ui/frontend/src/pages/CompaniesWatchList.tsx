import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import CompanyDetailModal from "../components/CompanyDetailModal"
import Modal from "../components/Modal"
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
  const [addOpen, setAddOpen] = useState(false)
  const [companyName, setCompanyName] = useState("")
  const [companyWebsite, setCompanyWebsite] = useState("")
  const [jobSite, setJobSite] = useState("")

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

  function handleAddCompany() {
    if (!selectedId) return
    api("/api/companies/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: selectedId,
        company_name: companyName,
        company_website: companyWebsite,
        job_site: jobSite,
      }),
    })
      .then(async r => {
        const res = await r.json()
        if (!r.ok) throw new Error(res.error || "Add failed")
        return res
      })
      .then(res => {
        setToast({ text: `Added ${res.short_name} (TEST_WATCH)`, variant: "success" })
        setAddOpen(false)
        setCompanyName("")
        setCompanyWebsite("")
        setJobSite("")
        load()
      })
      .catch(() => setToast({ text: "Add company failed", variant: "error" }))
  }

  const fieldStyle = {
    display: "block" as const,
    marginBottom: 10,
    fontSize: 13,
  }
  const inputStyle = {
    display: "block" as const,
    width: "100%",
    marginTop: 4,
    padding: "6px 8px",
    fontSize: 13,
    background: "var(--bg-deep)",
    color: "var(--text-primary)",
    border: "1px solid var(--border)",
    borderRadius: 6,
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
        actions={
          <button className="btn primary" onClick={() => setAddOpen(true)} disabled={!selectedId}>
            Add Company
          </button>
        }
        bulkActions={[
          { label: "Set to Ignore", onClick: ids => handleBulk("ignore", ids), variant: "danger" },
          { label: "Retry Scrape", onClick: ids => handleBulk("retry", ids) },
        ]}
      />
      <CompanyDetailModal shortName={viewing} onClose={() => setViewing(null)} onSaved={load} />

      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add Company" onSave={handleAddCompany}>
        <label style={fieldStyle}>
          Company Name
          <input
            type="text"
            value={companyName}
            onChange={e => setCompanyName(e.target.value)}
            style={inputStyle}
          />
        </label>
        <label style={fieldStyle}>
          Website
          <input
            type="text"
            value={companyWebsite}
            onChange={e => setCompanyWebsite(e.target.value)}
            style={inputStyle}
          />
        </label>
        <label style={fieldStyle}>
          Careers Page URL
          <input
            type="text"
            value={jobSite}
            onChange={e => setJobSite(e.target.value)}
            style={inputStyle}
          />
        </label>
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
