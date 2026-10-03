import { useCallback, useEffect, useState } from "react"
import ListPage from "../components/ListPage"
import Modal from "../components/Modal"
import RepoJsonDivergenceBanner from "../components/RepoJsonDivergenceBanner"
import Toast, { type ToastMessage } from "../components/Toast"
import TokenTextarea from "../components/TokenTextarea"
import { useCandidate } from "../contexts/CandidateContext"
import { useInPlaceLiveRefresh } from "../hooks/useInPlaceLiveRefresh"
import api from "../lib/api"
import { ApiError, errorToastFromApiError, readApiError } from "../lib/toastDiagnostics"
import type { Column } from "../components/ListPage"

/** GET /api/admin/agents/models — keyed by model id; each model lists only its own brain sizes (AST-1880).
 *  JSON keys arrive sorted, so `order` carries catalog order. */
interface BrainSizeRow {
  order: number
  default_max_tokens: number
}
interface ModelRow {
  order: number
  label: string
  server_id: string
  server_label: string
  brain_sizes: Record<string, BrainSizeRow>
}
type ModelCatalog = Record<string, ModelRow>

/** Ids of a keyed catalog object in catalog order. */
function byOrder<T extends { order: number }>(o: Record<string, T> | undefined): string[] {
  return Object.entries(o ?? {}).sort((a, b) => a[1].order - b[1].order).map(([id]) => id)
}

/** Agent mode choices; must match AGENT_MODES in src/utils/config.py (AST-1947). The models endpoint does not send them. */
const AGENT_MODES = ["Deterministic", "Creative"] as const

interface Agent {
  agent_id: string
  content?: string
  content_length?: number
  model_id?: string | null
  brain_setting?: string | null
  mode?: string | null
  max_tokens?: number
  task_count?: number
  updated_at?: string
  [key: string]: unknown
}

const LIST_COLUMNS: Column<Agent>[] = [
  { key: "agent_id",       label: "Agent ID",      sortable: true },
  { key: "model_label",    label: "Model",         sortable: true },
  { key: "brain_setting", label: "Brain setting", sortable: true },
  { key: "mode",           label: "Mode",          sortable: true },
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
  const [models, setModels] = useState<ModelCatalog>({})
  const { loading, beginRefresh, endRefresh } = useInPlaceLiveRefresh()
  const [toast, setToast]     = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  // Edit state
  const [editOpen, setEditOpen]           = useState(false)
  const [editAgent, setEditAgent]         = useState<Agent | null>(null)
  const [editContent, setEditContent]     = useState("")
  const [editModelId, setEditModelId]     = useState("")
  const [editBrainSetting, setEditBrainSetting] = useState("")
  const [editMode, setEditMode]           = useState("")
  const [editMaxTok, setEditMaxTok]       = useState("")

  // Add state
  const [addOpen, setAddOpen]             = useState(false)
  const [addId, setAddId]                 = useState("")
  const [addContent, setAddContent]       = useState("")
  const [addModelId, setAddModelId]       = useState("")
  const [addBrainSetting, setAddBrainSetting] = useState("")
  const [addMode, setAddMode]             = useState("")
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

  const loadAll = useCallback((showSpinner = false) => {
    beginRefresh(showSpinner)
    api("/api/admin/agents").then(r => r.json()).then(data => {
      setAgents(Array.isArray(data) ? data : [])
    }).catch(() => setAgents([]))
      .finally(() => endRefresh())
  }, [beginRefresh, endRefresh])

  useEffect(() => {
    loadAll(true)
    api("/api/admin/agents/models")
      .then(r => r.json())
      .then(data => setModels(data && typeof data === "object" && !Array.isArray(data) ? data : {}))
      .catch(() => {})
  }, [loadAll])

  // When size changes in add/edit, fill the max-tokens default from that model's row for that size
  function applyTierDefaults(modelId: string, setting: string, setMaxTok: (m: string) => void) {
    const row = models[modelId]?.brain_sizes[setting]
    if (!row)
      return
    setMaxTok(String(row.default_max_tokens))
  }

  // Model change keeps the size when the new model has it; otherwise the model's first size + its defaults.
  function sizeForModel(modelId: string, current: string): string {
    const sizes = byOrder(models[modelId]?.brain_sizes)
    return sizes.includes(current) ? current : (sizes[0] ?? "")
  }

  function onAddTierChange(setting: string) {
    setAddBrainSetting(setting)
    applyTierDefaults(addModelId, setting, setAddMaxTok)
  }

  function onEditTierChange(setting: string) {
    setEditBrainSetting(setting)
    applyTierDefaults(editModelId, setting, setEditMaxTok)
  }

  function onAddModelChange(modelId: string) {
    setAddModelId(modelId)
    const size = sizeForModel(modelId, addBrainSetting)
    setAddBrainSetting(size)
    if (size !== addBrainSetting)
      applyTierDefaults(modelId, size, setAddMaxTok)
  }

  function onEditModelChange(modelId: string) {
    setEditModelId(modelId)
    const size = sizeForModel(modelId, editBrainSetting)
    setEditBrainSetting(size)
    if (size !== editBrainSetting)
      applyTierDefaults(modelId, size, setEditMaxTok)
  }

  function openEdit(agent: Agent) {
    api(`/api/admin/agents/${agent.agent_id}`).then(async r => {
      if (!r.ok) await readApiError(r, `/api/admin/agents/${agent.agent_id}`, "GET")
      return r.json()
    }).then(full => {
      setEditAgent(full)
      setEditContent(full.content || "")
      setEditModelId(typeof full.model_id === "string" ? full.model_id : "")
      setEditBrainSetting(
        typeof full.brain_setting === "string" ? full.brain_setting : "",
      )
      setEditMode(typeof full.mode === "string" ? full.mode : "")
      setEditMaxTok(full.max_tokens != null ? String(full.max_tokens) : "")
      setEditOpen(true)
    }).catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
  }

  function handleEditSave() {
    if (!editAgent) return
    const body: Record<string, unknown> = {
      content:     editContent,
      mode:        editMode,
      max_tokens:  editMaxTok ? parseInt(editMaxTok) : undefined,
    }
    if (editModelId)
      body.model_id = editModelId
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
      mode:        addMode,
      max_tokens:  addMaxTok ? parseInt(addMaxTok)   : undefined,
    }
    if (addModelId)
      body.model_id = addModelId
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
        setAddModelId(""); setAddBrainSetting("")
        setAddMode(""); setAddMaxTok("")
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
    model_label: (a.model_id && models[a.model_id]?.label) || a.model_id || "—",
    brain_setting: tierCell(a),
    mode: a.mode || "—",
  }))

  function openAddModal() {
    const firstModel = byOrder(models)[0] ?? ""
    const firstSize = byOrder(models[firstModel]?.brain_sizes)[0] ?? ""
    setAddModelId(firstModel)
    setAddBrainSetting(firstSize)
    applyTierDefaults(firstModel, firstSize, setAddMaxTok)
    setAddMode(AGENT_MODES[0])
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
          <button className="btn primary" onClick={() => openAddModal()}>
            + Add Agent
          </button>
        }
        rowActions={row => {
          const agent = agents.find(a => a.agent_id === row.agent_id)
          const count = agent?.task_count ?? 1
          const disabled = count > 0
          return (
            <button
              type="button"
              className="icon-control"
              disabled={disabled}
              title={disabled ? `Agent is assigned to ${count} task(s) — unassign first` : "Delete agent"}
              aria-label="Delete"
              onClick={e => { e.stopPropagation(); if (agent) setDeleteTarget(agent) }}
            >
              D
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
          models={models}
          modelId={editModelId}
          onModelChange={onEditModelChange}
          brainSetting={editBrainSetting}
          mode={editMode}
          maxTok={editMaxTok}
          onTierChange={onEditTierChange}
          onModeChange={setEditMode}
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
              className="btn secondary"
              type="button"
              onClick={() => handlePreview("edit")}
              disabled={previewLoading}
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
          models={models}
          modelId={addModelId}
          onModelChange={onAddModelChange}
          brainSetting={addBrainSetting}
          mode={addMode}
          maxTok={addMaxTok}
          onTierChange={onAddTierChange}
          onModeChange={setAddMode}
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
              className="btn secondary"
              type="button"
              onClick={() => handlePreview("add")}
              disabled={previewLoading}
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

/** Model select, then that model's own brain sizes, the agent mode and max_tokens (catalog-driven; AST-1880, AST-1949) */
function BrainSettingFields({
  models,
  modelId,
  onModelChange,
  brainSetting,
  mode,
  maxTok,
  onTierChange,
  onModeChange,
  onMaxTokChange,
}: {
  models: ModelCatalog
  modelId: string
  onModelChange: (v: string) => void
  brainSetting: string
  mode: string
  maxTok: string
  onTierChange: (v: string) => void
  onModeChange:  (v: string) => void
  onMaxTokChange: (v: string) => void
}) {
  const sizes = byOrder(models[modelId]?.brain_sizes)
  const noModelMatch = !!modelId && !models[modelId]
  const noMatch = !!brainSetting && !sizes.includes(brainSetting)
  return (
    <>
      <div className="dep-field">
        <label className="dep-field-label">Model</label>
        <select className="dep-input" value={modelId} onChange={e => onModelChange(e.target.value)}>
          {noModelMatch ? <option value={modelId}>— (unknown model) —</option> : null}
          {modelId === "" ? <option value="">— choose model —</option> : null}
          {byOrder(models).map(id => (
            <option key={id} value={id}>{models[id].label}</option>
          ))}
        </select>
      </div>
      <div className="dep-field">
        <label className="dep-field-label">Brain size</label>
        <select className="dep-input" value={brainSetting} onChange={e => onTierChange(e.target.value)}>
          {noMatch ? <option value={brainSetting}>— (unmapped) —</option> : null}
          {brainSetting === "" ? <option value="">— choose size —</option> : null}
          {sizes.map(bs => (
            <option key={bs} value={bs}>{bs}</option>
          ))}
        </select>
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">Mode</label>
          <select className="dep-input" value={mode} onChange={e => onModeChange(e.target.value)}>
            {mode === "" ? <option value="">— choose mode —</option> : null}
            {AGENT_MODES.map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
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
