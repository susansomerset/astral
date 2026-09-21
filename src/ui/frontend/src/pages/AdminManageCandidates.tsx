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
  first?: string
  last?: string
  full?: string
  pronouns?: string
  has_api_key?: boolean
  [key: string]: unknown
}

type UnboundSlackUser = { slack_user_id: string; username: string }

const EMPTY_ADD_FORM = { first: "", last: "", contact_email: "", pronouns: "", slack_user_id: "" }

function slackBindFromSelection(
  selectedId: string,
  options: UnboundSlackUser[],
): { slack_user_id: string; slack_username: string } | null {
  const sid = selectedId.trim()
  if (!sid) return null
  const row = options.find(u => u.slack_user_id === sid)
  if (!row) return null
  return { slack_user_id: row.slack_user_id, slack_username: row.username }
}

function flattenCandidate(c: Candidate): Candidate & Record<string, unknown> {
  const cd = c.candidate_data || {}
  const contact = (cd.contact || {}) as Record<string, unknown>
  return {
    ...c,
    first: c.first ?? "",
    last: c.last ?? "",
    contact_email: contact.contact_email ?? "",
    api_key_status: c.has_api_key ? "Set" : "Not set",
  }
}

interface CandidateShapes {
  list: { manage: Column<Candidate>[] }
  detail?: { profile?: { label: string; fields: Field[] }[] }
}

function pronounFieldFromShapes(shapes: CandidateShapes | null): Field | undefined {
  const contact = shapes?.detail?.profile?.[0]
  return contact?.fields?.find(f => f.key === "pronouns")
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
  const [addForm, setAddForm] = useState(EMPTY_ADD_FORM)
  const [editOpen, setEditOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Candidate | null>(null)
  const [editForm, setEditForm] = useState({
    first: "", last: "", contact_email: "", pronouns: "", state: "", api_key: "", slack_user_id: "",
  })
  const [unboundSlackUsers, setUnboundSlackUsers] = useState<UnboundSlackUser[]>([])
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

  // Sibling AST-1668 admin GET — unbound workspace posters only (no Slack Web API from React).
  const loadUnboundSlackUsers = useCallback(() => {
    return api("/api/admin/contact/unbound_slack_users")
      .then(async r => {
        if (!r.ok) {
          const body = await r.json().catch(() => ({}))
          throw new Error((body as { error?: string }).error || "Failed to load unbound Slack users")
        }
        return r.json()
      })
      .then(data => {
        const raw = Array.isArray(data?.users) ? data.users : []
        const users: UnboundSlackUser[] = []
        for (const row of raw) {
          if (!row || typeof row !== "object") continue
          const sid = typeof row.slack_user_id === "string" ? row.slack_user_id.trim() : ""
          const uname = typeof row.username === "string" ? row.username.trim() : ""
          if (!sid || !uname) continue
          users.push({ slack_user_id: sid, username: uname })
        }
        setUnboundSlackUsers(users)
      })
      .catch(e => {
        setUnboundSlackUsers([])
        setToast({
          text: e instanceof Error ? e.message : "Failed to load unbound Slack users",
          variant: "error",
        })
      })
  }, [])

  useEffect(() => {
    api("/api/shapes/candidates").then(r => r.json()).then(s => setShapes(s))
    api("/api/candidates/states").then(r => r.json()).then(s => setValidStates(Array.isArray(s) ? s : []))
    loadAll()
    loadDispatchTaskCounts()
  }, [loadAll, loadDispatchTaskCounts])

  function handleAddSave() {
    const { first, last, contact_email, pronouns, slack_user_id } = addForm
    if (!first.trim() || !last.trim()) {
      setToast({ text: "First and last name are required", variant: "error" })
      return
    }
    const candidateId = last.trim().toLowerCase().replace(/\s+/g, "_")
    const contact: Record<string, string> = {
      contact_email: contact_email.trim(),
    }
    const bind = slackBindFromSelection(slack_user_id, unboundSlackUsers)
    if (bind) {
      contact.slack_user_id = bind.slack_user_id
      contact.slack_username = bind.slack_username
    }
    api("/api/candidates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        astral_candidate_id: candidateId,
        first: first.trim(),
        last: last.trim(),
        pronouns,
        candidate_data: { contact },
      }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Create failed") })
        return r.json()
      })
      .then(() => {
        setAddOpen(false)
        setAddForm(EMPTY_ADD_FORM)
        setToast({ text: `Candidate "${first} ${last}" created`, variant: "success" })
        loadAll()
        loadDispatchTaskCounts()
        if (bind) void loadUnboundSlackUsers()
        refresh()
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function openEdit(c: Candidate) {
    const cd = c.candidate_data || {}
    const contact = (cd.contact || {}) as Record<string, unknown>
    const boundId = String(contact.slack_user_id ?? "").trim()
    setEditTarget(c)
    setEditForm({
      first: String(c.first ?? ""),
      last: String(c.last ?? ""),
      contact_email: String(contact.contact_email ?? ""),
      pronouns: String(c.pronouns ?? ""),
      state: c.state || "",
      api_key: "",
      slack_user_id: boundId,
    })
    setShowKey(false)
    setClearKey(false)
    setEditOpen(true)
    void loadUnboundSlackUsers()
  }

  // Edit options = unbound pool + this candidate's current bind when not already unbound.
  const editSlackOptions: UnboundSlackUser[] = (() => {
    const opts = [...unboundSlackUsers]
    if (!editTarget) return opts
    const contact = ((editTarget.candidate_data || {}).contact || {}) as Record<string, unknown>
    const sid = String(contact.slack_user_id ?? "").trim()
    if (!sid || opts.some(u => u.slack_user_id === sid)) return opts
    const uname = String(contact.slack_username ?? "").trim() || sid
    return [{ slack_user_id: sid, username: uname }, ...opts]
  })()

  async function handleEditSave() {
    if (!editTarget) return
    const { first, last, contact_email, pronouns, state, api_key, slack_user_id } = editForm
    const contact: Record<string, string> = {
      contact_email: contact_email.trim(),
    }
    // Empty selection omits Slack keys — deep-merge leaves any existing bind intact.
    const bind = slackBindFromSelection(slack_user_id, editSlackOptions)
    if (bind) {
      contact.slack_user_id = bind.slack_user_id
      contact.slack_username = bind.slack_username
    }
    const payload: Record<string, unknown> = {
      first: first.trim(),
      last: last.trim(),
      pronouns,
      contact,
      state,
    }
    if (clearKey) payload.api_key = ""
    else if (api_key.trim()) payload.api_key = api_key.trim()
    const url = `/api/candidates/${editTarget.astral_candidate_id}/data`
    const putOpts = {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
    const finishOk = () => {
      setEditOpen(false)
      setEditTarget(null)
      setToast({ text: "Candidate updated", variant: "success" })
      loadAll()
      loadDispatchTaskCounts()
      if (bind) void loadUnboundSlackUsers()
      refresh()
    }
    try {
      const r = await api(url, putOpts)
      const body = await r.json().catch(() => ({} as Record<string, unknown>))
      if (r.ok) {
        finishOk()
        return
      }
      // AST-1287: illegal hop → confirm; unknown-state 400 has no this code
      if ((body as { code?: string }).code === "illegal_candidate_transition") {
        const from_state = String(
          (body as { from_state?: string }).from_state ?? editTarget.state ?? "",
        )
        const to_state = String(
          (body as { to_state?: string }).to_state ?? payload.state ?? "",
        )
        const ok = await confirm(
          `This state change is not allowed by the transition rules: ${from_state} → ${to_state}. Proceed anyway?`,
          { title: "Confirm illegal state change", confirmLabel: "Change state", variant: "danger" },
        )
        if (!ok) {
          // Cancel = skip state only; non-state fields may already be on the server
          loadAll()
          loadDispatchTaskCounts()
          setEditForm(p => ({ ...p, state: from_state }))
          setEditTarget(t => (t ? { ...t, state: from_state } : t))
          setToast({ text: "State unchanged; other fields saved if they were.", variant: "info" })
          return
        }
        const confirmR = await api(url, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...payload, confirm_state_override: true }),
        })
        const confirmBody = await confirmR.json().catch(() => ({} as Record<string, unknown>))
        if (confirmR.ok) {
          finishOk()
          return
        }
        setToast({
          text: String((confirmBody as { error?: string }).error || "Update failed"),
          variant: "error",
        })
        return
      }
      setToast({
        text: String((body as { error?: string }).error || "Update failed"),
        variant: "error",
      })
    } catch (e) {
      setToast({ text: e instanceof Error ? e.message : "Update failed", variant: "error" })
    }
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
          <button type="button" className="icon-control" onClick={e => { e.stopPropagation(); setViewing(row) }} title="View" aria-label="View">
            <ViewIcon />
          </button>
          <button type="button" className="icon-control" onClick={e => { e.stopPropagation(); openEdit(row) }} title="Edit" aria-label="Edit">
            <EditIcon />
          </button>
          <button type="button" className="icon-control" onClick={e => { e.stopPropagation(); void handleDelete(row) }} title="Delete" aria-label="Delete">
            <DeleteIcon />
          </button>
          <button
            type="button"
            className="icon-control"
            title="Set dispatch tasks"
            aria-label={`Set dispatch tasks for ${row.astral_candidate_id}`}
            disabled={settingCandidateId === row.astral_candidate_id}
            onClick={e => { e.stopPropagation(); void handleSetDispatchTasks(row) }}
          >
            T
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
          <button
            className="btn primary"
            onClick={() => {
              setAddForm(EMPTY_ADD_FORM)
              setAddOpen(true)
              void loadUnboundSlackUsers()
            }}
          >
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
      <Modal
        open={addOpen}
        onClose={() => {
          setAddOpen(false)
          setAddForm(EMPTY_ADD_FORM)
        }}
        title="Add Candidate"
        onSave={handleAddSave}
      >
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
        <div className="dep-field">
          <label className="dep-field-label">Slack username</label>
          <select
            className="dep-input dep-select"
            value={addForm.slack_user_id}
            onChange={e => setAddForm(p => ({ ...p, slack_user_id: e.target.value }))}
          >
            <option value="">— none —</option>
            {unboundSlackUsers.map(u => (
              <option key={u.slack_user_id} value={u.slack_user_id}>{u.username}</option>
            ))}
          </select>
        </div>
        {pronounField && (
          <PronounSelect
            field={pronounField}
            value={addForm.pronouns}
            onChange={v => setAddForm(p => ({ ...p, pronouns: v }))}
          />
        )}
      </Modal>

      {/* Edit modal */}
      <Modal open={editOpen} onClose={() => { setEditOpen(false); setEditTarget(null) }} title={editTarget ? `Edit: ${editTarget.astral_candidate_id}` : ""} onSave={() => { void handleEditSave() }}>
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
        <div className="dep-field">
          <label className="dep-field-label">Slack username</label>
          <select
            className="dep-input dep-select"
            value={editForm.slack_user_id}
            onChange={e => setEditForm(p => ({ ...p, slack_user_id: e.target.value }))}
          >
            <option value="">— none —</option>
            {editSlackOptions.map(u => (
              <option key={u.slack_user_id} value={u.slack_user_id}>{u.username}</option>
            ))}
          </select>
        </div>
        {pronounField && (
          <PronounSelect
            field={pronounField}
            value={editForm.pronouns}
            onChange={v => setEditForm(p => ({ ...p, pronouns: v }))}
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
              className="btn secondary"
              onClick={() => setShowKey(v => !v)}
            >
              {showKey ? "Hide" : "Show"}
            </button>
            {editTarget?.has_api_key && !editForm.api_key && !clearKey && (
              <button
                type="button"
                className="btn danger"
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
