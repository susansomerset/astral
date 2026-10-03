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

/** GET /api/admin/agents/models — keyed by model id (AST-1880, AST-1957). JSON keys arrive sorted, so `order`
 *  carries catalog order; default_max_tokens is what a call uses when the agent leaves max_tokens empty. */
interface ModelRow {
  order: number
  label: string
  server_id: string
  server_label: string
  default_max_tokens: number
}
type ModelCatalog = Record<string, ModelRow>

/** Ids of a keyed catalog object in catalog order. */
function byOrder<T extends { order: number }>(o: Record<string, T> | undefined): string[] {
  return Object.entries(o ?? {}).sort((a, b) => a[1].order - b[1].order).map(([id]) => id)
}

interface Agent {
  agent_id: string
  content?: string
  content_length?: number
  model_id?: string | null
  quantization?: string | null
  temperature?: number | null
  reasoning_effort?: string | null
  provider_allow_fallbacks?: boolean | null
  provider_only?: string[] | null
  provider_ignore?: string[] | null
  provider_sort?: string | null
  max_tokens?: number
  task_count?: number
  updated_at?: string
  [key: string]: unknown
}

/** Plain agent settings as the form edits them (AST-1957): text inputs hold strings, lists are comma-separated. */
interface SettingsForm {
  quantization: string
  temperature: string
  reasoning_effort: string
  provider_allow_fallbacks: boolean
  provider_only: string
  provider_ignore: string
  provider_sort: string
}

// New agents start with fallbacks on (the data layer's new-row default) and everything else empty.
const EMPTY_SETTINGS: SettingsForm = {
  quantization: "", temperature: "", reasoning_effort: "", provider_allow_fallbacks: true,
  provider_only: "", provider_ignore: "", provider_sort: "",
}

function settingsFromAgent(a: Agent): SettingsForm {
  return {
    quantization:             a.quantization ?? "",
    temperature:              a.temperature != null ? String(a.temperature) : "",
    reasoning_effort:         a.reasoning_effort ?? "",
    // Stored null reads as the default (true); saving writes the checkbox value explicitly.
    provider_allow_fallbacks: a.provider_allow_fallbacks ?? true,
    provider_only:            (a.provider_only ?? []).join(", "),
    provider_ignore:          (a.provider_ignore ?? []).join(", "),
    provider_sort:            a.provider_sort ?? "",
  }
}

/** Comma-separated slugs → list; blank → null (not sent on the wire). */
function slugList(s: string): string[] | null {
  const v = s.split(",").map(x => x.trim()).filter(Boolean)
  return v.length ? v : null
}

/** Form → request body under the settings keys. Every key is always sent, so clearing an input clears the setting. */
function settingsBody(f: SettingsForm): Record<string, unknown> {
  return {
    quantization:             f.quantization.trim() || null,
    temperature:              f.temperature.trim() === "" ? null : Number(f.temperature),
    reasoning_effort:         f.reasoning_effort.trim() || null,
    provider_allow_fallbacks: f.provider_allow_fallbacks,
    provider_only:            slugList(f.provider_only),
    provider_ignore:          slugList(f.provider_ignore),
    provider_sort:            f.provider_sort.trim() || null,
  }
}

const LIST_COLUMNS: Column<Agent>[] = [
  { key: "agent_id",       label: "Agent ID",      sortable: true },
  { key: "model_label",    label: "Model",         sortable: true },
  { key: "quantization",             label: "Quant",     sortable: true },
  { key: "temperature",              label: "Temp",      sortable: true },
  { key: "reasoning_effort",         label: "Effort",    sortable: true },
  { key: "provider_allow_fallbacks", label: "Fallbacks", sortable: true },
  { key: "provider_only",            label: "Only",      sortable: true },
  { key: "provider_ignore",          label: "Ignore",    sortable: true },
  { key: "provider_sort",            label: "Sort",      sortable: true },
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
  const [editSettings, setEditSettings]   = useState<SettingsForm>(EMPTY_SETTINGS)
  const [editMaxTok, setEditMaxTok]       = useState("")

  // Add state
  const [addOpen, setAddOpen]             = useState(false)
  const [addId, setAddId]                 = useState("")
  const [addContent, setAddContent]       = useState("")
  const [addModelId, setAddModelId]       = useState("")
  const [addSettings, setAddSettings]     = useState<SettingsForm>(EMPTY_SETTINGS)
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

  function openEdit(agent: Agent) {
    api(`/api/admin/agents/${agent.agent_id}`).then(async r => {
      if (!r.ok) await readApiError(r, `/api/admin/agents/${agent.agent_id}`, "GET")
      return r.json()
    }).then(full => {
      setEditAgent(full)
      setEditContent(full.content || "")
      setEditModelId(typeof full.model_id === "string" ? full.model_id : "")
      setEditSettings(settingsFromAgent(full))
      setEditMaxTok(full.max_tokens != null ? String(full.max_tokens) : "")
      setEditOpen(true)
    }).catch(e => setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: e.message, variant: "error" }))
  }

  function handleEditSave() {
    if (!editAgent) return
    const body: Record<string, unknown> = {
      content:     editContent,
      max_tokens:  editMaxTok ? parseInt(editMaxTok) : undefined,
      ...settingsBody(editSettings),
    }
    if (editModelId)
      body.model_id = editModelId
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
      max_tokens:  addMaxTok ? parseInt(addMaxTok)   : undefined,
      ...settingsBody(addSettings),
    }
    if (addModelId)
      body.model_id = addModelId
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
        setAddModelId(""); setAddSettings(EMPTY_SETTINGS); setAddMaxTok("")
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
    quantization:             a.quantization || "—",
    temperature:              a.temperature ?? "—",
    reasoning_effort:         a.reasoning_effort || "—",
    provider_allow_fallbacks: a.provider_allow_fallbacks == null ? "—" : a.provider_allow_fallbacks ? "yes" : "no",
    provider_only:            a.provider_only?.length ? a.provider_only.join(", ") : "—",
    provider_ignore:          a.provider_ignore?.length ? a.provider_ignore.join(", ") : "—",
    provider_sort:            a.provider_sort || "—",
    // Display strings in the grid cells; the row stays an Agent for ListPage (index signature).
  }) as unknown as Agent)

  function openAddModal() {
    setAddModelId(byOrder(models)[0] ?? "")
    setAddSettings(EMPTY_SETTINGS)
    setAddMaxTok("")
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
        <AgentSettingsFields
          models={models}
          modelId={editModelId}
          onModelChange={setEditModelId}
          maxTok={editMaxTok}
          onMaxTokChange={setEditMaxTok}
          settings={editSettings}
          onSettingsChange={setEditSettings}
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
        <AgentSettingsFields
          models={models}
          modelId={addModelId}
          onModelChange={setAddModelId}
          maxTok={addMaxTok}
          onMaxTokChange={setAddMaxTok}
          settings={addSettings}
          onSettingsChange={setAddSettings}
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

/** Model select, max_tokens override and the agent's plain call settings, sent as stored (AST-1880, AST-1957). */
function AgentSettingsFields({
  models,
  modelId,
  onModelChange,
  maxTok,
  onMaxTokChange,
  settings,
  onSettingsChange,
}: {
  models: ModelCatalog
  modelId: string
  onModelChange: (v: string) => void
  maxTok: string
  onMaxTokChange: (v: string) => void
  settings: SettingsForm
  onSettingsChange: (s: SettingsForm) => void
}) {
  const noModelMatch = !!modelId && !models[modelId]
  const defaultMax = models[modelId]?.default_max_tokens
  // One text input per string setting; key is the SettingsForm field it edits.
  const text = (key: keyof SettingsForm, label: string, placeholder: string) => (
    <div className="dep-field" style={{ flex: 1 }}>
      <label className="dep-field-label">{label}</label>
      <input
        className="dep-input"
        type="text"
        value={settings[key] as string}
        placeholder={placeholder}
        onChange={e => onSettingsChange({ ...settings, [key]: e.target.value })}
      />
    </div>
  )
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
      <div style={{ display: "flex", gap: 12 }}>
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">Max Tokens</label>
          <input
            className="dep-input"
            type="number" step="1" min="1"
            value={maxTok}
            placeholder={defaultMax != null ? `default ${defaultMax}` : ""}
            onChange={e => onMaxTokChange(e.target.value)}
          />
        </div>
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">Temperature</label>
          <input
            className="dep-input"
            type="number" step="any"
            value={settings.temperature}
            placeholder="not sent"
            onChange={e => onSettingsChange({ ...settings, temperature: e.target.value })}
          />
        </div>
        {text("reasoning_effort", "Effort", "e.g. high, none")}
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        {text("quantization", "Quantization", "e.g. bf16")}
        {text("provider_sort", "Provider sort", "e.g. price")}
        <div className="dep-field" style={{ flex: 1 }}>
          <label className="dep-field-label">
            <input
              type="checkbox"
              checked={settings.provider_allow_fallbacks}
              onChange={e => onSettingsChange({ ...settings, provider_allow_fallbacks: e.target.checked })}
            />{" "}
            Allow provider fallbacks
          </label>
        </div>
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        {text("provider_only", "Provider only", "comma-separated slugs")}
        {text("provider_ignore", "Provider ignore", "comma-separated slugs")}
      </div>
    </>
  )
}
