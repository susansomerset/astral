import { useEffect, useState } from "react"
import Modal from "./Modal"
import SideTabPanel, { type SideTab } from "./SideTabPanel"
import StateTimeline from "./StateTimeline"
import AgentStoryTab, { type AgentStoryEntry } from "./AgentStoryTab"
import Time from "./Time"
import api from "../lib/api"
import { useStateUi } from "../contexts/StateUiContext"

interface CompanyDetail {
  short_name: string
  company_name: string
  company_website?: string
  job_site?: string
  state: string
  last_scan_at?: string | null
  state_updated_at?: string | null
  prefilter_company_notes?: string
  state_history: Array<{ to_state?: string; timestamp?: string }>
  job_state_counts?: Record<string, number>
  agent_story?: AgentStoryEntry[]
  [key: string]: unknown
}

interface Props {
  shortName: string | null
  onClose: () => void
  onSaved: () => void
}

export default function CompanyDetailModal({ shortName, onClose, onSaved }: Props) {
  const { manifest, loadState } = useStateUi()
  const [data, setData] = useState<CompanyDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ company_name: "", company_website: "", job_site: "" })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  // Fetch full detail when modal opens
  useEffect(() => {
    if (!shortName) { setData(null); return }
    setLoading(true)
    setError("")
    api(`/api/companies/${encodeURIComponent(shortName)}`)
      .then(r => r.json())
      .then((d: CompanyDetail) => {
        setData(d)
        setForm({
          company_name: d.company_name || "",
          company_website: d.company_website || "",
          job_site: d.job_site || "",
        })
      })
      .catch(() => setError("Failed to load company"))
      .finally(() => setLoading(false))
  }, [shortName])

  const watchReadonly = manifest ? new Set(manifest.company.watch_readonly_states) : new Set<string>()
  const readOnly = !data || !manifest || watchReadonly.has(data.state)

  async function handleSave() {
    if (!data || readOnly) return
    setSaving(true)
    setError("")
    try {
      const res = await api(`/api/companies/${encodeURIComponent(data.short_name)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        setError(body.error || "Save failed")
        return
      }
      onSaved()
      onClose()
    } catch {
      setError("Network error")
    } finally {
      setSaving(false)
    }
  }

  // Build side tabs: Summary + one tab per agent story entry
  const agentStory = data?.agent_story ?? []
  const sideTabs: SideTab[] = [
    { id: "__summary__", label: "Summary", content: "" },
    ...agentStory.map((entry, i) => ({
      id: `story_${i}`,
      label: entry.task_key,
      content: "",
    })),
  ]

  function renderSideContent(tabId: string) {
    if (tabId === "__summary__") return <SummaryTab data={data} form={form} setForm={setForm} readOnly={readOnly} />
    const idx = sideTabs.findIndex(t => t.id === tabId) - 1
    const entry = agentStory[idx]
    if (!entry) return null
    return <AgentStoryTab entry={entry} />
  }

  return (
    <Modal
      open={shortName !== null}
      onClose={onClose}
      title={data?.company_name || shortName || ""}
      onSave={readOnly ? undefined : handleSave}
      size="wide"
    >
      {shortName && (loadState === "loading" || !manifest) && <p className="entity-loading">Loading…</p>}
      {shortName && loadState === "error" && <p className="entity-error">State UI manifest unavailable.</p>}
      {loading && <p className="entity-loading">Loading…</p>}
      {error && <p className="entity-error">{error}</p>}
      {saving && <p className="entity-loading">Saving…</p>}
      {data && manifest && loadState === "ready" && (
        <SideTabPanel
          tabs={sideTabs}
          renderContent={renderSideContent}
        />
      )}
    </Modal>
  )
}

// ---- Summary tab ----
function SummaryTab({
  data,
  form,
  setForm,
  readOnly,
}: {
  data: CompanyDetail | null
  form: { company_name: string; company_website: string; job_site: string }
  setForm: (f: { company_name: string; company_website: string; job_site: string }) => void
  readOnly: boolean
}) {
  if (!data) return null
  const counts = data.job_state_counts ?? {}
  const totalJobs = Object.values(counts).reduce((s, n) => s + n, 0)

  return (
    <div className="entity-summary">
      <div className="entity-summary-top">
        {/* Left column: editable fields */}
        <div className="entity-summary-col">
          <DetailRow label="Short Name"><span>{data.short_name}</span></DetailRow>
          <DetailRow label="Company">
            {readOnly
              ? <span>{data.company_name || "—"}</span>
              : <input value={form.company_name} onChange={e => setForm({ ...form, company_name: e.target.value })} />}
          </DetailRow>
          <DetailRow label="Website">
            {readOnly
              ? <span>{data.company_website || "—"}</span>
              : <input value={form.company_website} onChange={e => setForm({ ...form, company_website: e.target.value })} />}
          </DetailRow>
          <DetailRow label="Job Page">
            {readOnly
              ? <span>{data.job_site || "—"}</span>
              : <input value={form.job_site} onChange={e => setForm({ ...form, job_site: e.target.value })} />}
          </DetailRow>
          <DetailRow label="State"><span>{data.state}</span></DetailRow>
          {data.last_scan_at && (
            <DetailRow label="Last Scanned"><span><Time value={data.last_scan_at} /></span></DetailRow>
          )}
          {data.prefilter_company_notes && (
            <DetailRow label="Notes"><span>{data.prefilter_company_notes}</span></DetailRow>
          )}
        </div>
        {/* Right column: state timeline */}
        <div className="entity-summary-col">
          <p className="entity-section-label">State History</p>
          <StateTimeline history={data.state_history || []} />
        </div>
      </div>

      {/* Bottom: job state distribution */}
      <div className="entity-summary-bottom">
        <p className="entity-section-label">Jobs ({totalJobs} total)</p>
        {totalJobs === 0
          ? <span className="entity-empty">No jobs tracked yet.</span>
          : (
            <div className="entity-job-counts">
              {Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([state, count]) => (
                <div key={state} className="entity-job-count-row">
                  <span className="entity-job-count-state">{state}</span>
                  <span className="entity-job-count-n">{count}</span>
                </div>
              ))}
            </div>
          )}
      </div>
    </div>
  )
}

function DetailRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="modal-detail-row">
      <span className="modal-detail-label">{label}</span>
      {children}
    </div>
  )
}
