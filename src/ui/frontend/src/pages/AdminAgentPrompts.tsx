import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import Modal from "../components/Modal"
import RepoJsonDivergenceBanner from "../components/RepoJsonDivergenceBanner"
import Toast, { type ToastMessage } from "../components/Toast"
import TokenTextarea from "../components/TokenTextarea"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import { ApiError, errorToastFromApiError, readApiError } from "../lib/toastDiagnostics"
import type { Column } from "../components/ListPage"

/** Rows from GET /api/admin/agents/brain_settings (config-backed tiers). */
interface BrainSettingCatalogRow {
  brain_setting: string
  label: string
  default_temperature: number
  default_max_tokens: number
}

interface Agent {
  agent_id: string
  content?: string
  content_length?: number
  model_code?: string
  brain_setting?: string | null
  temperature?: number
  max_tokens?: number
  task_count?: number
  updated_at?: string
  [key: string]: unknown
}

const LIST_COLUMNS: Column<Agent>[] = [
  { key: "agent_id",       label: "Agent ID",      sortable: true },
  { key: "brain_setting", label: "Brain setting", sortable: true },
  { key: "temperature",    label: "Temp",          sortable: true },
  { key: "max_tokens",     label: "Max Tok",       sortable: true },
  { key: "task_count",     label: "Tasks",         sortable: true },
  { key: "content_length", label: "Chars",         sortable: true },
  { key: "updated_at",     label: "Updated",       sortable: true, type: "datetime" },
]

/** Agent template picker: registry minus chain/hop tokens (AST-632). */
function useAgentTokenList(): string[] {
  const [tokenList, setTokenList] = useState<string[]>([])
  useEffect(() => {
    api("/api/admin/agents/meta/tokens")
      .then(async r => {
        if (!r.ok) { setTokenList([]); return }
        const data = await r.json()
        setTokenList(Array.isArray(data) ? data : [])
      })
      .catch(() => setTokenList([]))
  }, [])
  return tokenList
}

/** Verbatim tier for grid; absent / unknown-backed storage → em dash */
function tierCell(a: Agent) {
  const t = a.brain_setting
  return (typeof t === "string" && t.length > 0) ? t : "—"
}

export default function AgentPrompts() {
  const { selectedId } = useCandidate()
  const tokenList = useAgentTokenList()
  const [agents, setAgents]   = useState<Agent[]>([])
  const [brainSettings, setBrainSettings] = useState<BrainSettingCatalogRow[]>([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast]     = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  // Edit state
  const [editOpen, setEditOpen]           = useState(false)
  const [editAgent, setEditAgent]         = useState<Agent | null>(null)
  const [editContent, setEditContent]     = useState("")
  const [editBrainSetting, setEditBrainSetting] = useState("")
  const [editTemp, setEditTemp]           = useState("")
  const [editMaxTok, setEditMaxTok]       = useState("")

  // Add state
  const [addOpen, setAddOpen]             = useState(false)
  const [addId, setAddId]                 = useState("")
  const [addContent, setAddContent]       = useState("")
  const [addBrainSetting, setAddBrainSetting] = useState("")
  const [addTemp, setAddTemp]             = useState("")
  const [addMaxTok, setAddMaxTok]         = useState("")

  // Delete confirm state
  const [deleteTarget, setDeleteTarget]   = useState<Agent | null>(null)

  // Preview state (AST-632)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewText, setPreviewText] = useState("")
  const [previewCandidateId, setPreviewCandidateId] = useState("")
  const [previewSource, setPreviewSource] = useState<"edit" | "add">("edit")
  const [repoJsonRefresh, setRepoJsonRefresh] = useState(0)

  const loadAll = useCallback(() => {
    setLoading(true)
    api("/api/admin/agents").then(r => r.json()).then(data => {
      setAgents(Array.isArray(data) ? data : [])
    }).catch(() => setAgents([]))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    loadAll()
    api("/api/admin/agents/brain_settings")
      .then(r => r.json())
      .then(data => {
        const list: BrainSettingCatalogRow[] = Array.isArray(data) ? data : []
        setBrainSettings(list)
        if (list.length > 0 && !addBrainSetting)
          setAddBrainSetting(list[0].brain_setting)
      })
      .catch(() => {})
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadAll])

  // When tier changes in add/edit, fill defaults from catalog row for that tier
  function applyTierDefaults(setting: string, setter: (t: string, m: string) => void) {
    const row = brainSettings.find(x => x.brain_setting === setting)
    if (!row)
      return
    setter(String(row.default_temperature), String(row.default_max_tokens))
  }

  function onAddTierChange(setting: string) {
    setAddBrainSetting(setting)
    applyTierDefaults(setting, (t, m) => { setAddTemp(t); setAddMaxTok(m) })
  }

  function onEditTierChange(setting: string) {
    setEditBrainSetting(setting)
    applyTierDefaults(setting, (t, m) => { setEditTemp(t); setEditMaxTok(m) })
  }

  function openEdit(agent: Agent) {
    api(`/api/admin/agents/${agent.agent_id}`).then(async r => {
      if (!r.ok) await readApiError(r, `/api/admin/agents/${agent.agent_id}`, "GET")
      return r.json()
    }).then(full => {
      setEditAgent(full)
      setEditContent(full.content || "")
      setEditBrainSetting(
        typeof full.brain_setting === "string" ? full.brain_setting : "",
      )
      setEditTemp(full.temperature != null ? String(full.temperature) : "")
      setEditMaxTok(full.max_tokens != null ? String(full.max_tokens) : "")
      setEditOpen(true)
    }).catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
  }

  function handleEditSave() {
    if (!editAgent) return
    const body: Record<string, unknown> = {
      content:     editContent,
      temperature: editTemp  ? parseFloat(editTemp)  : undefined,
      max_tokens:  editMaxTok ? parseInt(editMaxTok) : undefined,
    }
    if (editBrainSetting)
      body.brain_setting = editBrainSetting
    api(`/api/admin/agents/${editAgent.agent_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(async r => {
        if (!r.ok) await readApiError(r, `/api/admin/agents/${editAgent.agent_id}`, "PUT")
        return r.json()
      })
      .then(() => {
        setEditOpen(false); setEditAgent(null)
        setToast({ text: "Agent updated", variant: "success" })
        setRepoJsonRefresh(n => n + 1)
        loadAll()
      })
      .catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
  }

  function handleAddSave() {
    const id = addId.trim().toLowerCase().replace(/\s+/g, "_")
    if (!id) { setToast({ text: "Agent ID is required", variant: "error" }); return }
    const body: Record<string, unknown> = {
      agent_id:    id,
      content:     addContent,
      temperature: addTemp   ? parseFloat(addTemp)   : undefined,
      max_tokens:  addMaxTok ? parseInt(addMaxTok)   : undefined,
    }
    if (addBrainSetting)
      body.brain_setting = addBrainSetting
    api("/api/admin/agents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(async r => {
        if (!r.ok) await readApiError(r, "/api/admin/agents", "POST")
        return r.json()
      })
      .then(() => {
        setAddOpen(false); setAddId(""); setAddContent("")
        setAddBrainSetting(brainSettings[0]?.brain_setting || "")
        setAddTemp(""); setAddMaxTok("")
        setToast({ text: `Agent "${id}" created`, variant: "success" })
        setRepoJsonRefresh(n => n + 1)
        loadAll()
      })
      .catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
  }

  function handleDeleteConfirm() {
    if (!deleteTarget) return
    api(`/api/admin/agents/${deleteTarget.agent_id}`, { method: "DELETE" })
      .then(async r => {
        if (!r.ok) await readApiError(r, `/api/admin/agents/${deleteTarget.agent_id}`, "DELETE")
        return r.json()
      })
      .then(() => {
        setDeleteTarget(null)
        setToast({ text: `Agent "${deleteTarget.agent_id}" deleted`, variant: "success" })
        setRepoJsonRefresh(n => n + 1)
        loadAll()
      })
      .catch(e => { setDeleteTarget(null); setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }) })
  }

  function handlePreview(source: "edit" | "add") {
    setPreviewSource(source)
    setPreviewLoading(true)
    const content = source === "edit" ? editContent : addContent
    api("/api/admin/agents/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, candidate_id: selectedId || undefined }),
    })
      .then(async r => {
        if (!r.ok) await readApiError(r, "/api/admin/agents/preview", "POST")
        return r.json()
      })
      .then(data => {
        setPreviewText(typeof data.content === "string" ? data.content : "")
        setPreviewCandidateId(data.candidate_id || "")
        setPreviewOpen(true)
      })
      .catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
      .finally(() => setPreviewLoading(false))
  }

  const renderedAgents = agents.map(a => ({
    ...a,
    brain_setting: tierCell(a),
  }))

  function openAddModal() {
    const first = brainSettings[0]?.brain_setting || ""
    setAddBrainSetting(first)
    applyTierDefaults(first, (t, m) => { setAddTemp(t); setAddMaxTok(m) })
    setAddOpen(true)
  }

  return (
    <>
      <RepoJsonDivergenceBanner
        tableKey="agent"
        refreshToken={repoJsonRefresh}
        onReverted={() => { setRepoJsonRefresh(n => n + 1); loadAll() }}
      />
      <ListPage<Agent>
        title="Manage Agents"
        columns={LIST_COLUMNS}
        rows={renderedAgents}
        idField="agent_id"
        loading={loading}
        onRowClick={row => openEdit(agents.find(a => a.agent_id === row.agent_id) ?? row)}
        actions={
          <button className="dep-btn save" onClick={() => openAddModal()} style={{ padding: "6px 14px", fontSize: 13 }}>
            + Add Agent
          </button>
        }
        rowActions={row => {
          const agent = agents.find(a => a.agent_id === row.agent_id)
          const count = agent?.task_count ?? 1
          const disabled = count > 0
          return (
            <button
              className="dep-btn danger"
              disabled={disabled}
              title={disabled ? `Agent is assigned to ${count} task(s) — unassign first` : "Delete agent"}
              onClick={e => { e.stopPropagation(); if (agent) setDeleteTarget(agent) }}
              style={{ padding: "3px 10px", fontSize: 12 }}
            >
              Delete
            </button>
          )
        }}
      />

      {/* Edit modal */}
      <Modal
        open={editOpen}
        onClose={() => { setEditOpen(false); setEditAgent(null) }}
        title={editAgent ? `Edit: ${editAgent.agent_id}` : ""}
        onSave={handleEditSave}
      >
        <BrainSettingFields
          brainSettings={brainSettings}
          brainSetting={editBrainSetting}
          temp={editTemp}
          maxTok={editMaxTok}
          onTierChange={onEditTierChange}
          onTempChange={setEditTemp}
          onMaxTokChange={setEditMaxTok}
        />
        <div className="dep-field">
          <label className="dep-field-label">System Prompt Content</label>
          <TokenTextarea
            className="dep-input"
            value={editContent}
            onChange={setEditContent}
            tokens={tokenList}
            rows={20}
            placeholder="Agent system prompt — type {$ to insert merge tokens."
          />
          <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
            <button
              className="dep-btn cancel"
              type="button"
              onClick={() => handlePreview("edit")}
              disabled={previewLoading}
              style={{ fontSize: 12, padding: "5px 12px" }}
            >
              {previewLoading && previewSource === "edit" ? "Loading..." : "Preview Resolved"}
            </button>
            <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>
              Resolves tokens for the selected candidate (draft text)
            </span>
          </div>
        </div>
      </Modal>

      {/* Add modal */}
      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add Agent" onSave={handleAddSave}>
        <div className="dep-field">
          <label className="dep-field-label">Agent ID</label>
          <input
            className="dep-input"
            type="text"
            value={addId}
            onChange={e => setAddId(e.target.value)}
            placeholder="e.g. job_analyst_grace"
          />
        </div>
        <BrainSettingFields
          brainSettings={brainSettings}
          brainSetting={addBrainSetting}
          temp={addTemp}
          maxTok={addMaxTok}
          onTierChange={onAddTierChange}
          onTempChange={setAddTemp}
          onMaxTokChange={setAddMaxTok}
        />
        <div className="dep-field">
          <label className="dep-field-label">System Prompt Content</label>
          <TokenTextarea
            className="dep-input"
            value={addContent}
            onChange={setAddContent}
            tokens={tokenList}
            rows={12}
            placeholder="Agent system prompt — type {$ to insert merge tokens."
          />
          <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8 }}>
            <button
              className="dep-btn cancel"
              type="button"
              onClick={() => handlePreview("add")}
              disabled={previewLoading}
              style={{ fontSize: 12, padding: "5px 12px" }}
            >
              {previewLoading && previewSource === "add" ? "Loading..." : "Preview Resolved"}
            </button>
            <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>
              Resolves tokens for the selected candidate (draft text)
            </span>
          </div>
        </div>
      </Modal>

      {/* Delete confirm modal */}
      <Modal
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title={`Delete agent: ${deleteTarget?.agent_id ?? ""}`}
        onSave={handleDeleteConfirm}
      >
        <p style={{ margin: 0 }}>
          Delete <strong>{deleteTarget?.agent_id}</strong>? This cannot be undone.
        </p>
      </Modal>

      {/* Preview modal (AST-632) */}
      <Modal
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        title={`Preview${previewCandidateId ? `: ${previewCandidateId}` : ""}`}
      >
        <pre style={{
          margin: 0, padding: 12, borderRadius: 4,
          background: "var(--bg-deep)", border: "1px solid var(--border)",
          color: "var(--text-primary)", fontFamily: "monospace", fontSize: 12,
          whiteSpace: "pre-wrap", wordBreak: "break-word",
          maxHeight: 500, overflow: "auto",
        }}>
          {previewText || "(empty)"}
        </pre>
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}

/** Tier select + temperature / max_tokens (catalog-driven tier list; no vendor CPM in v1) */
function BrainSettingFields({
  brainSettings,
  brainSetting,
  temp,
  maxTok,
  onTierChange,
  onTempChange,
  onMaxTokChange,
}: {
  brainSettings: BrainSettingCatalogRow[]
  brainSetting: string
  temp: string
  maxTok: string
  onTierChange: (v: string) => void
  onTempChange:  (v: string) => void
  onMaxTokChange: (v: string) => void
}) {
  const noMatch =
    !!brainSetting && !brainSettings.some(r => r.brain_setting === brainSetting)
  return (
    <>
      <div className="dep-field">
        <label className="dep-field-label">Brain setting</label>
        <select className="dep-input" value={brainSetting} onChange={e => onTierChange(e.target.value)}>
          {noMatch ? <option value={brainSetting}>— (unmapped) —</option> : null}
          {brainSetting === "" ? <option value="">— choose tier —</option> : null}
          {brainSettings.map(row => (
            <option key={row.brain_setting} value={row.brain_setting}>{row.label}</option>
          ))}
        </select>
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">Temperature</label>
          <input
            className="dep-input"
            type="number" step="0.1" min="0" max="1"
            value={temp}
            onChange={e => onTempChange(e.target.value)}
          />
        </div>
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">Max Tokens</label>
          <input
            className="dep-input"
            type="number" step="1" min="1"
            value={maxTok}
            onChange={e => onMaxTokChange(e.target.value)}
          />
        </div>
      </div>
    </>
  )
}
