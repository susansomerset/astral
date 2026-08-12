import { useCallback, useEffect, useState } from "react"
import Toast, { type ToastMessage } from "../components/Toast"
import { useUserConfirm } from "../components/UserPrompt"
import api from "../lib/api"

type ScheduledQuery = {
  scheduled_query_id: string
  name: string
  sql_text: string
  active: boolean
  interval_hours: number
  last_run_at: string | null
  last_rows_affected: number | null
  last_error: string | null
  created_at: string
  updated_at: string
}

const emptyForm = {
  name: "",
  sql_text: "",
  active: false,
  interval_hours: 24,
}

export default function AdminScheduledQueries() {
  const [rows, setRows] = useState<ScheduledQuery[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState({ ...emptyForm })
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  const confirm = useUserConfirm()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api("/api/admin/scheduled_queries")
      const data = await res.json().catch(() => [])
      if (!res.ok) {
        throw new Error(
          (typeof data.error === "string" && data.error) || `HTTP ${res.status}`,
        )
      }
      setRows(Array.isArray(data) ? data : [])
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
      setRows([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  function startCreate() {
    setEditingId(null)
    setForm({ ...emptyForm })
  }

  function startEdit(row: ScheduledQuery) {
    setEditingId(row.scheduled_query_id)
    setForm({
      name: row.name,
      sql_text: row.sql_text,
      active: Boolean(row.active),
      interval_hours: Number(row.interval_hours) || 24,
    })
  }

  async function save() {
    if (busy) return
    setBusy(true)
    try {
      const body = {
        name: form.name,
        sql_text: form.sql_text,
        active: form.active,
        interval_hours: Number(form.interval_hours),
      }
      const res = editingId
        ? await api(`/api/admin/scheduled_queries/${editingId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          })
        : await api("/api/admin/scheduled_queries", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          })
      const data = await res.json().catch(() => ({} as Record<string, unknown>))
      if (!res.ok) {
        throw new Error(
          (typeof data.error === "string" && data.error) || `HTTP ${res.status}`,
        )
      }
      setToast({
        text: editingId ? "Query updated." : "Query saved.",
        variant: "success",
      })
      startCreate()
      await load()
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
    } finally {
      setBusy(false)
    }
  }

  async function toggleActive(row: ScheduledQuery) {
    if (busy) return
    setBusy(true)
    try {
      const res = await api(`/api/admin/scheduled_queries/${row.scheduled_query_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active: !row.active }),
      })
      const data = await res.json().catch(() => ({} as Record<string, unknown>))
      if (!res.ok) {
        throw new Error(
          (typeof data.error === "string" && data.error) || `HTTP ${res.status}`,
        )
      }
      await load()
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
    } finally {
      setBusy(false)
    }
  }

  async function remove(row: ScheduledQuery) {
    const ok = await confirm(`Delete scheduled query "${row.name}"?`, {
      title: "Delete query",
      confirmLabel: "Delete",
    })
    if (!ok || busy) return
    setBusy(true)
    try {
      const res = await api(`/api/admin/scheduled_queries/${row.scheduled_query_id}`, {
        method: "DELETE",
      })
      const data = await res.json().catch(() => ({} as Record<string, unknown>))
      if (!res.ok) {
        throw new Error(
          (typeof data.error === "string" && data.error) || `HTTP ${res.status}`,
        )
      }
      if (editingId === row.scheduled_query_id) startCreate()
      setToast({ text: "Query deleted.", variant: "success" })
      await load()
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 1100 }}>
      <h1 style={{ margin: "0 0 8px", fontSize: 22, color: "var(--text-primary)" }}>
        Scheduled Queries
      </h1>
      <p style={{ margin: "0 0 20px", color: "var(--text-secondary)", fontSize: 14 }}>
        Save SQL to run on an hours cadence when Active. Manual execute stays on Data Management —
        no Run now here.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 20,
          alignItems: "start",
        }}
      >
        <section
          style={{
            border: "1px solid var(--border-color)",
            borderRadius: 8,
            padding: 16,
            background: "var(--bg-secondary)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
            <h2 style={{ margin: 0, fontSize: 16 }}>{editingId ? "Edit query" : "New query"}</h2>
            {editingId ? (
              <button type="button" className="btn primary" onClick={startCreate} disabled={busy}>
                New
              </button>
            ) : null}
          </div>
          <label style={{ display: "block", marginBottom: 10, fontSize: 13 }}>
            Name
            <input
              className="dep-input"
              style={{ display: "block", width: "100%", marginTop: 4 }}
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
          </label>
          <label style={{ display: "block", marginBottom: 10, fontSize: 13 }}>
            Interval hours
            <input
              className="dep-input"
              type="number"
              min={0.1}
              step={0.1}
              style={{ display: "block", width: "100%", marginTop: 4 }}
              value={form.interval_hours}
              onChange={e =>
                setForm(f => ({ ...f, interval_hours: Number(e.target.value) || 0 }))
              }
            />
          </label>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              marginBottom: 10,
              fontSize: 13,
            }}
          >
            <input
              type="checkbox"
              checked={form.active}
              onChange={e => setForm(f => ({ ...f, active: e.target.checked }))}
            />
            Active
          </label>
          <label style={{ display: "block", marginBottom: 12, fontSize: 13 }}>
            SQL
            <textarea
              className="dep-input"
              rows={10}
              style={{
                display: "block",
                width: "100%",
                marginTop: 4,
                fontFamily: "ui-monospace, monospace",
                fontSize: 12,
              }}
              value={form.sql_text}
              onChange={e => setForm(f => ({ ...f, sql_text: e.target.value }))}
              placeholder={`DELETE FROM agent_data\nWHERE created_at < datetime('now', '-3 days')\n  AND block_type != 'RESPONSE'`}
            />
          </label>
          <button type="button" className="btn primary" onClick={() => void save()} disabled={busy}>
            {editingId ? "Update" : "Save"}
          </button>
        </section>

        <section>
          {loading ? (
            <p style={{ color: "var(--text-secondary)" }}>Loading…</p>
          ) : rows.length === 0 ? (
            <p style={{ color: "var(--text-secondary)" }}>No scheduled queries yet.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {rows.map(row => (
                <div
                  key={row.scheduled_query_id}
                  style={{
                    border: "1px solid var(--border-color)",
                    borderRadius: 8,
                    padding: 14,
                    background: "var(--bg-secondary)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 12,
                      marginBottom: 8,
                    }}
                  >
                    <strong style={{ color: "var(--text-primary)" }}>{row.name}</strong>
                    <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                      every {row.interval_hours}h · {row.active ? "active" : "off"}
                    </span>
                  </div>
                  <pre
                    style={{
                      margin: "0 0 8px",
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                      fontSize: 11,
                      color: "var(--text-secondary)",
                      maxHeight: 120,
                      overflow: "auto",
                    }}
                  >
                    {row.sql_text}
                  </pre>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8 }}>
                    Last run: {row.last_run_at || "—"} · Records affected:{" "}
                    {row.last_rows_affected == null ? "—" : row.last_rows_affected}
                    {row.last_error ? (
                      <div style={{ color: "var(--danger, #c44)", marginTop: 4 }}>
                        Last error: {row.last_error}
                      </div>
                    ) : null}
                  </div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button
                      type="button"
                      className="btn secondary"
                      onClick={() => startEdit(row)}
                      disabled={busy}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="btn secondary"
                      onClick={() => void toggleActive(row)}
                      disabled={busy}
                    >
                      {row.active ? "Deactivate" : "Activate"}
                    </button>
                    <button
                      type="button"
                      className="btn danger"
                      onClick={() => void remove(row)}
                      disabled={busy}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {toast ? <Toast message={toast} onDone={clearToast} /> : null}
    </div>
  )
}
