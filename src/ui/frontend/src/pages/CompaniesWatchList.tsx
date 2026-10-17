import { useCallback, useEffect, useMemo, useState } from "react"
import ListPage from "../components/ListPage"
import CompanyDetailModal from "../components/CompanyDetailModal"
import CompanyWatchJobsModal from "../components/CompanyWatchJobsModal"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import { formatCell } from "../lib/fmt"
import type { Column } from "../components/ListPage"

/** AST-2320 bucket keys (not including total `jobs`) — clickable count columns. */
const COUNT_BUCKET_KEYS = ["jl", "jd", "do", "get", "like", "active", "skipped", "applied"] as const
type CountBucketKey = (typeof COUNT_BUCKET_KEYS)[number]

interface Company {
  short_name: string
  company_name: string
  company_website?: string
  state?: string
  last_scan_at?: string | null
  scan_start?: string | null
  best_fit_label?: string | null
  best_fit_at?: string | null
  jobs?: number
  [key: string]: unknown
}

interface ShapeCol {
  key: string
  label: string
  sortable?: boolean
  type?: string
  defaultDesc?: boolean
}

function shortDate(raw: string | null | undefined): string {
  const text = raw == null ? "" : String(raw).trim()
  if (!text) return ""
  const formatted = formatCell(text, "date")
  return formatted === "—" ? "" : formatted
}

export default function WatchList() {
  const { manifest, loadState } = useStateUi()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<Company[]>([])
  const [apiColumns, setApiColumns] = useState<ShapeCol[]>([])
  const [loading, setLoading] = useState(true)
  const [viewing, setViewing] = useState<string | null>(null)
  const [showDates, setShowDates] = useState(false)
  const [jobsModal, setJobsModal] = useState<{
    shortName: string
    bucket: string
    label: string
  } | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  // AST-2322 add-company affordance (kept alongside AST-2321 dates / jobs modal)
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
      setApiColumns(Array.isArray(shapes?.list?.watch_list) ? shapes.list.watch_list : [])
    }).finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { load() }, [load])

  const columns: Column<Company>[] = useMemo(() => {
    const countSet = new Set<string>(COUNT_BUCKET_KEYS)
    return apiColumns
      .filter(c => c.key !== "best_fit_at")
      .map(c => {
        const col: Column<Company> = {
          key: c.key,
          label: c.label,
          sortable: c.sortable !== false,
          ...(c.type ? { type: c.type } : {}),
          ...(c.defaultDesc ? { defaultDesc: true } : {}),
        }
        if (c.key === "best_fit_label") {
          col.render = (_v, row) => {
            const label = String(row.best_fit_label ?? "").trim()
            if (!label) return "—"
            const at = shortDate(row.best_fit_at != null ? String(row.best_fit_at) : null)
            return at ? `${label} (${at})` : label
          }
        }
        if (countSet.has(c.key)) {
          const bucket = c.key as CountBucketKey
          const label = c.label
          col.render = (value, row) => {
            const n = Number(value) || 0
            let text = String(n)
            if (showDates && n >= 1) {
              const at = shortDate(
                row[`${bucket}_newest_at`] != null ? String(row[`${bucket}_newest_at`]) : null,
              )
              if (at) text = `${n} (${at})`
            }
            if (n < 1) return text
            return (
              <button
                type="button"
                className="dispatch-batch-link"
                onClick={e => {
                  e.stopPropagation()
                  setJobsModal({ shortName: row.short_name, bucket, label })
                }}
              >
                {text}
              </button>
            )
          }
        }
        return col
      })
  }, [apiColumns, showDates])

  if (loadState === "loading") {
    return <div className="list-page-status">Loading...</div>
  }
  if (loadState === "error" || !manifest) {
    return <div className="list-page-status">State UI manifest unavailable.</div>
  }

  const ignoreToState = manifest.company.bulk_transitions.watch_list_ignore_to_state

  function handleIgnore(ids: string[]) {
    api("/api/companies/bulk_state", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ short_names: ids, to_state: ignoreToState }),
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
          <>
            <label className="recommended-analysis-toggle">
              <input
                type="checkbox"
                checked={showDates}
                onChange={e => setShowDates(e.target.checked)}
              />
              Show dates
            </label>
            <button className="btn primary" onClick={() => setAddOpen(true)} disabled={!selectedId}>
              Add Company
            </button>
          </>
        }
        bulkActions={[
          { label: "Set to Ignore", onClick: ids => handleIgnore(ids), variant: "danger" },
        ]}
      />
      <CompanyDetailModal shortName={viewing} onClose={() => setViewing(null)} onSaved={load} />
      {jobsModal && selectedId && (
        <CompanyWatchJobsModal
          key={`${jobsModal.shortName}:${jobsModal.bucket}`}
          shortName={jobsModal.shortName}
          bucket={jobsModal.bucket}
          bucketLabel={jobsModal.label}
          candidateId={selectedId}
          onClose={() => setJobsModal(null)}
        />
      )}
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
