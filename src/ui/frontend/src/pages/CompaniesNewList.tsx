import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import CompanyDetailModal from "../components/CompanyDetailModal"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import type { Column } from "../components/ListPage"

interface Company {
  short_name: string
  company_name: string
  company_website: string
  state: string
  created_at: string
  state_history: Array<{ to_state?: string; timestamp?: string }>
  [key: string]: unknown
}

export default function NewList() {
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<Company[]>([])
  const [columns, setColumns] = useState<Column<Company>[]>([])
  const [loading, setLoading] = useState(true)
  const [viewing, setViewing] = useState<string | null>(null)
  const [importOpen, setImportOpen] = useState(false)
  const [csvText, setCsvText] = useState("")
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  const load = useCallback(() => {
    if (!selectedId) return
    Promise.all([
      api(`/api/companies?view=new_list&candidate_id=${encodeURIComponent(selectedId)}`).then(r => r.json()),
      api("/api/shapes/companies").then(r => r.json()),
    ]).then(([data, shapes]) => {
      setRows(Array.isArray(data) ? data : [])
      setColumns(shapes?.list?.new_list || [])
    }).finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { load() }, [load])

  function handleImport() {
    if (!csvText.trim() || !selectedId) return
    const lines = csvText.trim().split("\n").filter(l => l.trim())
    // Parse CSV: short_name, company_name, company_website (header optional)
    const parsed = lines
      .map(line => {
        const parts = line.split(",").map(s => s.trim())
        // Skip header row
        if (parts[0]?.toLowerCase() === "short_name") return null
        return { short_name: parts[0] || "", company_name: parts[1] || "", company_website: parts[2] || "" }
      })
      .filter((r): r is NonNullable<typeof r> => r !== null && !!r.short_name)

    if (parsed.length === 0) {
      setToast({ text: "No valid rows found in CSV", variant: "error" })
      return
    }

    api("/api/companies/import", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows: parsed, candidate_id: selectedId }),
    })
      .then(r => r.json())
      .then(res => {
        setToast({ text: `${res.created} companies imported`, variant: "success" })
        setImportOpen(false)
        setCsvText("")
        load()
      })
      .catch(() => setToast({ text: "Import failed", variant: "error" }))
  }

  return (
    <>
      <ListPage<Company>
        title="New List"
        columns={columns}
        rows={rows}
        idField="short_name"
        loading={loading}
        onRowClick={row => setViewing(row.short_name)}
        actions={
          <button className="dep-btn save" onClick={() => setImportOpen(true)} style={{ padding: "6px 14px", fontSize: 13 }}>
            Import CSV
          </button>
        }
      />

      <CompanyDetailModal shortName={viewing} onClose={() => setViewing(null)} onSaved={load} />

      {/* Import modal */}
      <Modal open={importOpen} onClose={() => setImportOpen(false)} title="Import Companies from CSV" onSave={handleImport}>
        <p style={{ fontSize: 13, color: "#aaa", marginBottom: 12 }}>
          Paste CSV with columns: <code>short_name, company_name, company_website</code>
        </p>
        <textarea
          value={csvText}
          onChange={e => setCsvText(e.target.value)}
          placeholder={"short_name,company_name,company_website\nacme,Acme Corp,https://acme.com"}
          style={{
            width: "100%", minHeight: 200, fontFamily: "monospace", fontSize: 13,
            background: "#1a1a2e", color: "#e0e0e0", border: "1px solid #333",
            borderRadius: 6, padding: 12, resize: "vertical",
          }}
        />
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
