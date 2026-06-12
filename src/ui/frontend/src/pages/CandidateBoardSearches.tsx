import { useCallback, useEffect, useMemo, useState } from "react"
import ListPage, { type Column } from "../components/ListPage"
import Modal from "../components/Modal"
import { useUserConfirm } from "../components/UserPrompt"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

type SearchMode = "criteria" | "deeplink"

type WorkflowState = "ACTIVE" | "INACTIVE" | "ERROR"

interface BoardSearchRow {
  board_search_id: string
  board_key: string
  label: string
  mode: SearchMode
  criteria?: Record<string, unknown> | null
  deeplink_url?: string | null
  state?: WorkflowState
  created_at: string
  updated_at: string
}

interface AdoptedBoard {
  board_key: string
  label: string
}

const MODE_SWITCH_MSG =
  "Switching clears the current criteria/deeplink. Continue?"

function criteriaToText(criteria: unknown): string {
  if (criteria == null) return "{}"
  if (typeof criteria === "string") {
    try {
      return JSON.stringify(JSON.parse(criteria), null, 2)
    } catch {
      return criteria
    }
  }
  return JSON.stringify(criteria, null, 2)
}

export default function CandidateBoardSearches() {
  const confirm = useUserConfirm()
  const { selectedId } = useCandidate()
  const [boards, setBoards] = useState<AdoptedBoard[]>([])
  const [rows, setRows] = useState<BoardSearchRow[]>([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<BoardSearchRow | null>(null)
  const [label, setLabel] = useState("")
  const [boardKey, setBoardKey] = useState("")
  const [workflow, setWorkflow] = useState<WorkflowState>("ACTIVE")
  const [mode, setMode] = useState<SearchMode>("criteria")
  const [criteriaText, setCriteriaText] = useState("{}")
  const [deeplinkUrl, setDeeplinkUrl] = useState("")

  const boardLabelByKey = useMemo(() => {
    const m: Record<string, string> = {}
    for (const b of boards) m[b.board_key] = b.label
    return m
  }, [boards])

  const loadBoards = useCallback(() => {
    api("/api/boards")
      .then(async r => {
        const data = await r.json()
        if (!r.ok)
          throw new Error(typeof data?.error === "string" ? data.error : "Failed to load board list")
        return data
      })
      .then(data => setBoards(Array.isArray(data) ? data : []))
      .catch(err => {
        setBoards([])
        setToast({
          text: err instanceof Error ? err.message : "Failed to load board list",
          variant: "error",
        })
      })
  }, [])

  const loadSearches = useCallback(() => {
    if (!selectedId) {
      setRows([])
      setLoading(false)
      return
    }
    setLoading(true)
    api(`/api/boards/searches?candidate_id=${encodeURIComponent(selectedId)}`)
      .then(async r => {
        const data = await r.json()
        if (!r.ok) throw new Error(typeof data?.error === "string" ? data.error : "Failed to load searches")
        return data
      })
      .then(data => setRows(Array.isArray(data) ? data : []))
      .catch(err => {
        setRows([])
        setToast({ text: err instanceof Error ? err.message : "Failed to load searches", variant: "error" })
      })
      .finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => { loadBoards() }, [loadBoards])
  useEffect(() => { loadSearches() }, [loadSearches])

  const resetForm = () => {
    setEditing(null)
    setLabel("")
    setBoardKey(boards[0]?.board_key ?? "")
    setWorkflow("ACTIVE")
    setMode("criteria")
    setCriteriaText("{}")
    setDeeplinkUrl("")
  }

  const openCreate = () => {
    resetForm()
    setFormOpen(true)
  }

  const coerceState = useCallback((s: unknown): WorkflowState => {
    const u = String(s ?? "").toUpperCase()
    if (u === "ACTIVE" || u === "INACTIVE" || u === "ERROR") return u
    return "ACTIVE"
  }, [])

  const openEdit = (row: BoardSearchRow) => {
    setEditing(row)
    setLabel(row.label)
    setBoardKey(row.board_key)
    setWorkflow(coerceState(row.state))
    setMode(row.mode === "deeplink" ? "deeplink" : "criteria")
    setCriteriaText(criteriaToText(row.criteria))
    setDeeplinkUrl(row.deeplink_url?.trim() ?? "")
    setFormOpen(true)
  }

  const switchMode = async (next: SearchMode) => {
    if (next === mode) return
    const dirty =
      (mode === "criteria" && criteriaText.trim() !== "{}" && criteriaText.trim() !== "") ||
      (mode === "deeplink" && deeplinkUrl.trim() !== "")
    if (dirty && !(await confirm(MODE_SWITCH_MSG, { title: "Switch mode?", confirmLabel: "Continue" }))) return
    setMode(next)
    if (next === "criteria") {
      setDeeplinkUrl("")
      if (!criteriaText.trim()) setCriteriaText("{}")
    } else {
      setCriteriaText("{}")
    }
  }

  const handleSave = () => {
    const trimmedLabel = label.trim()
    if (!trimmedLabel) {
      setToast({ text: "Label is required", variant: "error" })
      return
    }
    if (!boardKey) {
      setToast({ text: "Board is required", variant: "error" })
      return
    }
    if (!selectedId) {
      setToast({ text: "Select a candidate first", variant: "error" })
      return
    }

    let criteria: Record<string, unknown> | undefined
    if (mode === "criteria") {
      try {
        const parsed = JSON.parse(criteriaText) as unknown
        if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
          setToast({ text: "Invalid JSON: criteria must be an object", variant: "error" })
          return
        }
        criteria = parsed as Record<string, unknown>
      } catch {
        setToast({ text: "Invalid JSON", variant: "error" })
        return
      }
    }

    const body: Record<string, unknown> = {
      label: trimmedLabel,
      board_key: boardKey,
      state: workflow,
      mode,
    }
    if (mode === "deeplink") {
      const url = deeplinkUrl.trim()
      if (!url) {
        setToast({ text: "Deeplink URL is required", variant: "error" })
        return
      }
      body.deeplink_url = url
    } else {
      body.criteria = criteria
    }

    const url = editing
      ? `/api/boards/searches/${encodeURIComponent(editing.board_search_id)}`
      : "/api/boards/searches"
    const method = editing ? "PATCH" : "POST"
    if (!editing) body.candidate_id = selectedId

    api(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(async r => {
        const data = await r.json()
        if (!r.ok) throw new Error(typeof data?.error === "string" ? data.error : "Save failed")
        return data
      })
      .then(() => {
        setToast({ text: editing ? "Search updated" : "Search created", variant: "success" })
        setFormOpen(false)
        resetForm()
        loadSearches()
      })
      .catch(err => {
        setToast({ text: err instanceof Error ? err.message : "Save failed", variant: "error" })
      })
  }

  const handleDelete = async (row: BoardSearchRow) => {
    if (!(await confirm(`Delete board search "${row.label}"?`, {
      title: "Delete search?",
      confirmLabel: "Delete",
      variant: "danger",
    }))) return
    api(`/api/boards/searches/${encodeURIComponent(row.board_search_id)}`, { method: "DELETE" })
      .then(async r => {
        const data = await r.json().catch(() => ({}))
        if (!r.ok) throw new Error(typeof data?.error === "string" ? data.error : "Delete failed")
        setToast({ text: "Search deleted", variant: "success" })
        loadSearches()
      })
      .catch(err => setToast({ text: err instanceof Error ? err.message : "Delete failed", variant: "error" }))
  }
  const resumeSearch = useCallback(
    (row: BoardSearchRow) => {
      api(`/api/boards/searches/${encodeURIComponent(row.board_search_id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state: "ACTIVE" }),
      })
        .then(async r => {
          const data = await r.json().catch(() => ({}))
          if (!r.ok) throw new Error(typeof data?.error === "string" ? data.error : "Resume failed")
          setToast({ text: "Search resumed (ACTIVE)", variant: "success" })
          loadSearches()
        })
        .catch(err => setToast({ text: err instanceof Error ? err.message : "Resume failed", variant: "error" }))
    },
    [loadSearches],
  )

  const columns: Column<BoardSearchRow>[] = [
    { key: "label", label: "Label" },
    {
      key: "board_key",
      label: "Board",
      render: (_v, row) => boardLabelByKey[row.board_key] ?? row.board_key,
    },
    {
      key: "state",
      label: "Gaze state",
      render: (_v, row) => {
        const st = coerceState(row.state)
        if (st === "ERROR") return "ERROR"
        return st === "INACTIVE" ? "Paused (INACTIVE)" : "ACTIVE"
      },
    },
    { key: "created_at", label: "Created", type: "datetime" },
    { key: "updated_at", label: "Updated", type: "datetime" },
  ]
  return (
    <>
      <ListPage<BoardSearchRow>
        title="Board Searches"
        columns={columns}
        rows={rows}
        idField="board_search_id"
        loading={loading}
        emptyMessage={selectedId ? "No board searches yet." : "Select a candidate to view board searches."}
        actions={
          <>
            <button type="button" className="dep-btn save" style={{ padding: "6px 14px", fontSize: 13 }} onClick={loadSearches}>
              Refresh
            </button>
            <button
              type="button"
              className="dep-btn save"
              style={{ padding: "6px 14px", fontSize: 13 }}
              onClick={openCreate}
              disabled={!selectedId}
            >
              New search
            </button>
          </>
        }
        rowActions={row => (
          <>
            {coerceState(row.state) === "ERROR" ? (
              <button
                type="button"
                className="dep-btn save"
                style={{ padding: "4px 10px", fontSize: 12 }}
                onClick={() => resumeSearch(row)}
              >
                Resume ACTIVE
              </button>
            ) : null}
            <button type="button" className="dep-btn cancel" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => openEdit(row)}>
              Edit
            </button>
            <button type="button" className="dep-btn danger" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => handleDelete(row)}>
              Delete
            </button>
          </>
        )}
      />

      <Modal
        open={formOpen}
        onClose={() => { setFormOpen(false); resetForm() }}
        title={editing ? "Edit board search" : "New board search"}
        onSave={handleSave}
      >
        <div className="dep-field">
          <label className="dep-field-label">Label</label>
          <input className="dep-input" type="text" value={label} onChange={e => setLabel(e.target.value)} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Board</label>
          <select className="dep-input dep-select" value={boardKey} onChange={e => setBoardKey(e.target.value)}>
            <option value="">Select board…</option>
            {boards.map(b => (
              <option key={b.board_key} value={b.board_key}>{b.label}</option>
            ))}
          </select>
        </div>
        {editing != null && coerceState(editing.state) === "ERROR" ? (
          <div className="dep-field">
            <p style={{ margin: "0 0 8px 0", fontSize: 13 }}>
              Last board gaze failed — set ACTIVE below to resume automatic runs.
            </p>
          </div>
        ) : null}
        <div className="dep-field">
          <span className="dep-field-label">Board gaze</span>
          <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
            <button type="button" className={`dep-btn${workflow === "ACTIVE" ? " save" : " cancel"}`} onClick={() => setWorkflow("ACTIVE")}>
              Active
            </button>
            <button type="button" className={`dep-btn${workflow === "INACTIVE" ? " save" : " cancel"}`} onClick={() => setWorkflow("INACTIVE")}>
              Paused
            </button>
          </div>
        </div>
        <div className="dep-field">
          <span className="dep-field-label">Mode</span>
          <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
            <button type="button" className={`dep-btn${mode === "criteria" ? " save" : " cancel"}`} onClick={() => switchMode("criteria")}>
              Criteria
            </button>
            <button type="button" className={`dep-btn${mode === "deeplink" ? " save" : " cancel"}`} onClick={() => switchMode("deeplink")}>
              Deeplink
            </button>
          </div>
        </div>
        {mode === "criteria" ? (
          <div className="dep-field">
            <label className="dep-field-label">Criteria (JSON object)</label>
            <textarea
              className="dep-input dep-textarea"
              rows={8}
              value={criteriaText}
              onChange={e => setCriteriaText(e.target.value)}
            />
          </div>
        ) : (
          <div className="dep-field">
            <label className="dep-field-label">Deeplink URL</label>
            <textarea
              className="dep-input dep-textarea"
              rows={3}
              value={deeplinkUrl}
              onChange={e => setDeeplinkUrl(e.target.value)}
              placeholder="https://…"
            />
          </div>
        )}
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
