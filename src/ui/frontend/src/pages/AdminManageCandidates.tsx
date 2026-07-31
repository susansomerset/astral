import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useUserConfirm } from "../components/UserPrompt"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import type { Column } from "../components/ListPage"
import type { Field } from "../components/FormFields"

interface Candidate {
  astral_candidate_id: string
  state: string
  candidate_data: Record<string, unknown>
  has_api_key?: boolean
  [key: string]: unknown
}

function flattenCandidate(c: Candidate): Candidate & Record<string, unknown> {
  const cd = c.candidate_data || {}
  const profile = (cd.profile || {}) as Record<string, unknown>
  return { ...c, ...profile, api_key_status: c.has_api_key ? "Set" : "Not set" }
}

interface CandidateShapes {
  list: { manage: Column<Candidate>[] }
  detail?: { profile?: { label: string; fields: Field[] }[] }
}

function pronounFieldFromShapes(shapes: CandidateShapes | null): Field | undefined {
  const contact = shapes?.detail?.profile?.[0]
  return contact?.fields?.find(f => f.key === "profile.pronoun_preference")
}

function PronounSelect({
  field,
  value,
  onChange,
}: {
  field: Field
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="dep-field">
      <label className="dep-field-label">{field.label}</label>
      <select
        className="dep-input dep-select"
        value={value}
        onChange={e => onChange(e.target.value)}
      >
        {field.options?.map(opt => {
          const v = typeof opt === "string" ? opt : opt.value
          const lbl = typeof opt === "string" ? opt : opt.label
          return <option key={v} value={v}>{lbl}</option>
        })}
      </select>
    </div>
  )
}

function ViewIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EditIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  )
}

function DeleteIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  )
}

export default function ManageCandidates() {
  const [shapes, setShapes] = useState<CandidateShapes | null>(null)
  const [allCandidates, setAllCandidates] = useState<Candidate[]>([])
  const [dispatchTaskCounts, setDispatchTaskCounts] = useState<Record<string, number>>({})
  const [settingCandidateId, setSettingCandidateId] = useState<string | null>(null)
  const [validStates, setValidStates] = useState<string[]>([])
  const [viewing, setViewing] = useState<Candidate | null>(null)
  const [addOpen, setAddOpen] = useState(false)
  const [addForm, setAddForm] = useState({ first: "", last: "", contact_email: "", pronoun_preference: "" })
  const [editOpen, setEditOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Candidate | null>(null)
  const [editForm, setEditForm] = useState({ first: "", last: "", contact_email: "", pronoun_preference: "", state: "", api_key: "" })
  const [showKey, setShowKey] = useState(false)
  const [clearKey, setClearKey] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  const { refresh } = useCandidate()
  const confirm = useUserConfirm()
  const pronounField = pronounFieldFromShapes(shapes)

  // Admin view fetches ALL candidates including DELETED
  const loadAll = useCallback(() => {
    api("/api/candidates?include_deleted=true").then(r => r.json()).then(data => {
      setAllCandidates(Array.isArray(data) ? data : [])
    }).catch(() => setAllCandidates([]))
  }, [])

  const loadDispatchTaskCounts = useCallback(() => {
    api("/api/admin/dispatch_tasks/counts")
      .then(async r => {
        if (!r.ok) {
          const body = await r.json().catch(() => ({}))
          throw new Error((body as { error?: string }).error || "Failed to load dispatch task counts")
        }
        return r.json()
      })
      .then(data => {
        const counts = (data && typeof data === "object" && data.counts && typeof data.counts === "object")
          ? data.counts as Record<string, number>
          : {}
        setDispatchTaskCounts(counts)
      })
      .catch(() => setDispatchTaskCounts({}))
  }, [])

  useEffect(() => {
    api("/api/shapes/candidates").then(r => r.json()).then(s => setShapes(s))
    api("/api/candidates/states").then(r => r.json()).then(s => setValidStates(Array.isArray(s) ? s : []))
    loadAll()
    loadDispatchTaskCounts()
  }, [loadAll, loadDispatchTaskCounts])

  function handleAddSave() {
    const { first, last, contact_email, pronoun_preference } = addForm
    if (!first.trim() || !last.trim()) {
      setToast({ text: "First and last name are required", variant: "error" })
      return
    }
    const candidateId = last.trim().toLowerCase().replace(/\s+/g, "_")
    api("/api/candidates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        astral_candidate_id: candidateId,
        candidate_data: {
          profile: {
            first: first.trim(),
            last: last.trim(),
            contact_email: contact_email.trim(),
            pronoun_preference,
          },
        },
      }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Create failed") })
        return r.json()
      })
      .then(() => {
        setAddOpen(false)
        setAddForm({ first: "", last: "", contact_email: "", pronoun_preference: "" })
        setToast({ text: `Candidate "${first} ${last}" created`, variant: "success" })
        loadAll()
        loadDispatchTaskCounts()
        refresh()
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function openEdit(c: Candidate) {
    const cd = c.candidate_data || {}
    const profile = (cd.profile || {}) as Record<string, unknown>
    setEditTarget(c)
    setEditForm({
      first: (profile.first as string) || "",
      last: (profile.last as string) || "",
      contact_email: (profile.contact_email as string) || "",
      pronoun_preference: String(profile.pronoun_preference ?? ""),
      state: c.state || "",
      api_key: "",
    })
    setShowKey(false)
    setClearKey(false)
    setEditOpen(true)
  }

  function handleEditSave() {
    if (!editTarget) return
    const { first, last, contact_email, pronoun_preference, state, api_key } = editForm
    const payload: Record<string, unknown> = {
      profile: {
        first: first.trim(),
        last: last.trim(),
        contact_email: contact_email.trim(),
        pronoun_preference,
      },
      state,
    }
    if (clearKey) payload.api_key = ""
    else if (api_key.trim()) payload.api_key = api_key.trim()
    api(`/api/candidates/${editTarget.astral_candidate_id}/data`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Update failed") })
        return r.json()
      })
      .then(() => {
        setEditOpen(false)
        setEditTarget(null)
        setToast({ text: "Candidate updated", variant: "success" })
        loadAll()
        loadDispatchTaskCounts()
        refresh()
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  async function handleDelete(c: Candidate) {
    const ok = await confirm(
      `Delete candidate "${c.astral_candidate_id}"? This is a logical delete (state → DELETED).`,
      { title: "Delete candidate", confirmLabel: "Delete", variant: "danger" },
    )
    if (!ok) return
    api(`/api/candidates/${c.astral_candidate_id}`, { method: "DELETE" })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Delete failed") })
        return r.json()
      })
      .then(() => {
        setToast({ text: `Candidate "${c.astral_candidate_id}" deleted`, variant: "success" })
        loadAll()
        loadDispatchTaskCounts()
        refresh()
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  async function handleSetDispatchTasks(c: Candidate) {
    const ok = await confirm(
      `Replace dispatch tasks for "${c.astral_candidate_id}" with the template candidate’s full set? Existing extras for this candidate will be removed.`,
      { title: "Set dispatch tasks", confirmLabel: "Set tasks", variant: "danger" },
    )
    if (!ok) return
    setSettingCandidateId(c.astral_candidate_id)
    api("/api/admin/dispatch_tasks/set_from_template", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_id: c.astral_candidate_id }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Set dispatch tasks failed") })
        return r.json()
      })
      .then(data => {
        const id = c.astral_candidate_id
        const count = Number(data.count ?? 0)
        setToast({ text: `Dispatch tasks set for "${id}" (${count} rows)`, variant: "success" })
        setDispatchTaskCounts(prev => ({ ...prev, [id]: count }))
        loadDispatchTaskCounts()
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
      .finally(() => setSettingCandidateId(null))
  }

  if (!shapes) return <p style={{ padding: 20, color: "#fff" }}>Loading...</p>

  const rows = allCandidates.map(c => {
    const flat = flattenCandidate(c)
    const id = String(flat.astral_candidate_id || "")
    return {
      ...flat,
      dispatch_task_count: Number(dispatchTaskCounts[id] ?? 0),
    }
  })

  const baseColumns = shapes.list.manage.map((col: Column<Candidate>) => {
    if (col.key === "api_key_status") {
      return {
        ...col,
        render: (val: unknown) => (
          <span style={{ color: val === "Set" ? "var(--success, #4caf50)" : "var(--warning, #ff9800)", fontWeight: 600, fontSize: 12 }}>
            {val === "Set" ? "🔑 Set" : "⚠️ Not set"}
          </span>
        ),
      }
    }
    if (col.key === "dispatch_task_count") {
      return {
        ...col,
        render: (val: unknown) => <>{Number(val ?? 0)}</>,
      }
    }
    return col
  })

  const columns: Column<Candidate>[] = [
    ...baseColumns,
    {
      key: "_actions", label: "", sortable: false,
      render: (_, row) => (
        <span style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <button className="list-page-edit-btn" onClick={e => { e.stopPropagation(); setViewing(row) }} aria-label="View">
            <ViewIcon />
          </button>
          <button className="list-page-edit-btn" onClick={e => { e.stopPropagation(); openEdit(row) }} aria-label="Edit">
            <EditIcon />
          </button>
          <button className="list-page-edit-btn" onClick={e => { e.stopPropagation(); void handleDelete(row) }} aria-label="Delete" style={{ color: "var(--danger)" }}>
            <DeleteIcon />
          </button>
          <button
            type="button"
            className="dep-btn"
            style={{ padding: "6px 10px", fontSize: 12 }}
            aria-label={`Set dispatch tasks for ${row.astral_candidate_id}`}
            disabled={settingCandidateId === row.astral_candidate_id}
            onClick={e => { e.stopPropagation(); void handleSetDispatchTasks(row) }}
          >
            Set dispatch tasks
          </button>
        </span>
      ),
    },
  ]

  return (
    <>
      <ListPage<Candidate>
        title="Manage Candidates"
        columns={columns}
        rows={rows}
        actions={
          <button className="dep-btn save" onClick={() => setAddOpen(true)} style={{ padding: "6px 14px", fontSize: 13 }}>
            + Add Candidate
          </button>
        }
      />

      {/* View modal */}
      <Modal open={viewing !== null} onClose={() => setViewing(null)} title={viewing ? `${viewing.astral_candidate_id} (${viewing.state})` : ""}>
        <pre style={{
          whiteSpace: "pre-wrap", wordBreak: "break-word", fontSize: 13,
          color: "#e0e0e0", background: "#1a1a2e", padding: 16, borderRadius: 8,
          maxHeight: "60vh", overflow: "auto",
        }}>
          {viewing ? JSON.stringify(viewing.candidate_data, null, 2) : ""}
        </pre>
      </Modal>

      {/* Add modal */}
      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add Candidate" onSave={handleAddSave}>
        <div className="dep-field">
          <label className="dep-field-label">First Name</label>
          <input className="dep-input" type="text" value={addForm.first} onChange={e => setAddForm(p => ({ ...p, first: e.target.value }))} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Last Name</label>
          <input className="dep-input" type="text" value={addForm.last} onChange={e => setAddForm(p => ({ ...p, last: e.target.value }))} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Email</label>
          <input className="dep-input" type="email" value={addForm.contact_email} onChange={e => setAddForm(p => ({ ...p, contact_email: e.target.value }))} />
        </div>
        {pronounField && (
          <PronounSelect
            field={pronounField}
            value={addForm.pronoun_preference}
            onChange={v => setAddForm(p => ({ ...p, pronoun_preference: v }))}
          />
        )}
      </Modal>

      {/* Edit modal */}
      <Modal open={editOpen} onClose={() => { setEditOpen(false); setEditTarget(null) }} title={editTarget ? `Edit: ${editTarget.astral_candidate_id}` : ""} onSave={handleEditSave}>
        <div className="dep-field">
          <label className="dep-field-label">First Name</label>
          <input className="dep-input" type="text" value={editForm.first} onChange={e => setEditForm(p => ({ ...p, first: e.target.value }))} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Last Name</label>
          <input className="dep-input" type="text" value={editForm.last} onChange={e => setEditForm(p => ({ ...p, last: e.target.value }))} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Email</label>
          <input className="dep-input" type="email" value={editForm.contact_email} onChange={e => setEditForm(p => ({ ...p, contact_email: e.target.value }))} />
        </div>
        {pronounField && (
          <PronounSelect
            field={pronounField}
            value={editForm.pronoun_preference}
            onChange={v => setEditForm(p => ({ ...p, pronoun_preference: v }))}
          />
        )}
        <div className="dep-field">
          <label className="dep-field-label">State (admin override)</label>
          <select className="dep-input" value={editForm.state} onChange={e => setEditForm(p => ({ ...p, state: e.target.value }))}>
            {validStates.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Anthropic API Key (leave blank to keep current)</label>
          <div style={{ display: "flex", gap: 6 }}>
            <input
              className="dep-input"
              type={showKey ? "text" : "password"}
              value={editForm.api_key}
              onChange={e => setEditForm(p => ({ ...p, api_key: e.target.value }))}
              placeholder="sk-ant-..."
              autoComplete="off"
              style={{ flex: 1 }}
            />
            <button
              type="button"
              className="dep-btn"
              onClick={() => setShowKey(v => !v)}
              style={{ padding: "6px 10px", fontSize: 12 }}
            >
              {showKey ? "Hide" : "Show"}
            </button>
            {editTarget?.has_api_key && !editForm.api_key && !clearKey && (
              <button
                type="button"
                className="dep-btn"
                onClick={() => {
                  void (async () => {
                    const ok = await confirm(
                      "Clear this candidate's API key? They won't be able to run tasks until a new key is set.",
                      { title: "Clear API key", confirmLabel: "Clear key", variant: "danger" },
                    )
                    if (!ok) return
                    setClearKey(true)
                    setToast({ text: "Key will be cleared on save", variant: "info" })
                  })()
                }}
                style={{ padding: "6px 10px", fontSize: 12, color: "var(--danger)" }}
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
