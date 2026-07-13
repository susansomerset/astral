import { useCallback, useEffect, useMemo, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import CollapsiblePanel from "../components/CollapsiblePanel"
import Modal from "../components/Modal"
import RepoJsonDivergenceBanner from "../components/RepoJsonDivergenceBanner"
import { TabBar } from "../components/TabbedTextArea"
import Toast, { type ToastMessage } from "../components/Toast"
import TokenTextarea from "../components/TokenTextarea"
import Time from "../components/Time"
import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
import api from "../lib/api"

interface AgentTask {
  task_key: string
  task_key_uuid: string | null
  agent_id: string
  run_next?: string
  task_group_order: string
  task_group_name: string
  task_seq: number | null
  task_name: string
  model_code: string | null
  system_prompt_tokens: number
  base_cache_tokens: number
  parsed_cache_tokens: number | null   // null = TBD (unresolved tokens remain)
  cache_min_tokens: number
  cache_satisfied: boolean
  nocache_prompt_tokens: number
  avg_live_tokens: number | null       // null = never run
  avg_output_tokens: number | null     // null = never run
  task_ready: boolean
  updated_at: string | null
  // edit modal fields (fetched separately)
  user_prompt?: string
  cache_prompt?: string
  cache_prompt_b?: string
  cache_prompt_c?: string
  cache_prompt_d?: string
  nocache_prompt?: string
  [key: string]: unknown
}

/** Edit accordion order — mirrors parent enumerated segment order */
type TabKey = "system" | "cache" | "cache_b" | "cache_c" | "cache_d" | "nocache" | "user"
type PreviewKey = "system" | "cache_a" | "cache_b" | "cache_c" | "cache_d" | "nocache" | "user"

const VALID_EDIT_TAB_KEYS: TabKey[] = ["system", "cache", "cache_b", "cache_c", "cache_d", "nocache", "user"]

const EDIT_PANEL_LABELS: Record<TabKey, string> = {
  system:   "System Prompt",
  cache:    "Cache Block A",
  cache_b:  "Cache Block B",
  cache_c:  "Cache Block C",
  cache_d:  "Cache Block D",
  nocache:  "No Cache Block",
  user:     "User Prompt",
}

const PREVIEW_TABS: { key: PreviewKey; label: string }[] = [
  { key: "system",   label: "System Prompt" },
  { key: "cache_a",  label: "Cache Block A" },
  { key: "cache_b",  label: "Cache Block B" },
  { key: "cache_c",  label: "Cache Block C" },
  { key: "cache_d",  label: "Cache Block D" },
  { key: "nocache",  label: "No Cache Block" },
  { key: "user",     label: "User Prompt" },
]

const fmt = (n: number | null) => n == null ? "N/A" : n.toLocaleString()

const ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS = "astral_admin_task_prompts_default_expanded"

/** Union `tasks/meta/tokens` + `tasks/meta/chain_tokens` (AST-455) for pickers across all segments. */
function mergedAdminTokenAutocomplete(metaTokens: unknown, chainTokens: unknown): string[] {
  const asList = (x: unknown): string[] =>
    (Array.isArray(x) ? (x as string[]) : []).map(t => String(t))
  const s = new Set<string>()
  for (const t of asList(metaTokens)) s.add(t)
  for (const t of asList(chainTokens)) s.add(t)
  return [...s].sort((a, b) => a.localeCompare(b))
}

/** Resolved-preview field: API uses `cache_a`…`; legacy `cache` == block A before AST-455. */
function previewField(tab: PreviewKey, data: Record<string, unknown> | null): string {
  if (!data) return ""
  const txt = (k: string): string => (typeof data[k] === "string" ? (data[k] as string) : "")
  switch (tab) {
    case "cache_a":
      return txt("cache_a") || txt("cache")
    default:
      return txt(tab)
  }
}

function readDefaultEditPanel(): TabKey {
  try {
    const v = localStorage.getItem(ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS)
    if (v && VALID_EDIT_TAB_KEYS.includes(v as TabKey)) return v as TabKey
  } catch {
    /* private mode / quota */
  }
  return "user"
}

/** Build run_next adjacency for current=1 rows; apply an in-editor override for one task_key. */
function draftRunNextMap(tasks: AgentTask[], overrideKey: string | null, overrideRunNext: string): Map<string, string> {
  const m = new Map<string, string>()
  for (const t of tasks) {
    const rn = (t.run_next || "").trim()
    if (rn) m.set(t.task_key, rn)
  }
  if (overrideKey) {
    const s = overrideRunNext.trim()
    if (s) m.set(overrideKey, s)
    else m.delete(overrideKey)
  }
  return m
}

/** Kahn topological sort — returns false if a directed cycle exists. */
function runNextGraphIsAcyclic(edges: Map<string, string>): boolean {
  const nodes = new Set<string>([...edges.keys(), ...edges.values()])
  if (nodes.size === 0) return true
  const indeg = new Map<string, number>()
  for (const n of nodes) indeg.set(n, 0)
  for (const [, dst] of edges) indeg.set(dst, (indeg.get(dst) || 0) + 1)
  const q = [...nodes].filter(n => (indeg.get(n) || 0) === 0)
  let seen = 0
  while (q.length) {
    const cur = q.pop()!
    seen++
    const nxt = edges.get(cur)
    if (!nxt) continue
    const d = (indeg.get(nxt) || 0) - 1
    indeg.set(nxt, d)
    if (d === 0) q.push(nxt)
  }
  return seen === nodes.size
}

function CacheMinCell({ tokens, satisfied }: { tokens: number; satisfied: boolean }) {
  return (
    <span style={{ color: satisfied ? "var(--color-pass, #34d399)" : undefined, fontWeight: satisfied ? 600 : undefined }}>
      {tokens.toLocaleString()}
    </span>
  )
}

export default function TaskPrompts() {
  const { selectedId } = useCandidate()
  const [tasks, setTasks]   = useState<AgentTask[]>([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast]   = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  const [repoJsonRefresh, setRepoJsonRefresh] = useState(0)

  const [agentIds, setAgentIds]     = useState<string[]>([])
  const [tokenList, setTokenList]   = useState<string[]>([])

  // Edit state
  const [editOpen, setEditOpen]     = useState(false)
  const [editTask, setEditTask]     = useState<AgentTask | null>(null)
  const [editAgentId, setEditAgentId] = useState("")
  const [editSystem, setEditSystem]   = useState("")
  const [editUser, setEditUser]     = useState("")
  const [editCache, setEditCache]   = useState("")
  const [editCacheB, setEditCacheB] = useState("")
  const [editCacheC, setEditCacheC] = useState("")
  const [editCacheD, setEditCacheD] = useState("")
  const [editNocache, setEditNocache] = useState("")
  const [editRunNext, setEditRunNext] = useState("")
  const [editGroupOrder, setEditGroupOrder] = useState("")
  const [editGroupName, setEditGroupName] = useState("")
  const [editTaskSeq, setEditTaskSeq] = useState("")
  const [editTaskName, setEditTaskName] = useState("")
  const [editOpenPanel, setEditOpenPanel] = useState<TabKey | null>(null)
  const [defaultPanelPreference, setDefaultPanelPreference] = useState<TabKey>(() => readDefaultEditPanel())

  // Preview state
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewData, setPreviewData] = useState<Record<string, unknown> | null>(null)
  const [previewCandidateId, setPreviewCandidateId] = useState("")
  const [previewTab, setPreviewTab]   = useState<PreviewKey>("system")
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewJobId, setPreviewJobId] = useState("")

  const loadAll = useCallback(() => {
    setLoading(true)
    const qs = selectedId ? `?candidate_id=${encodeURIComponent(selectedId)}` : ""
    Promise.all([
      api(`/api/admin/tasks${qs}`).then(r => r.json()),
      api("/api/admin/agents/ids").then(r => r.json()),
      api("/api/admin/tasks/meta/tokens").then(r => r.json()),
      // Optional meta: older Vitest handlers may omit this URL; do not fail the whole Manage Tasks load.
      api("/api/admin/tasks/meta/chain_tokens")
        .then(async r => (r.ok ? r.json() : []))
        .catch(() => []),
    ]).then(([taskData, agentData, tokData, chainData]) => {
      setTasks(Array.isArray(taskData) ? taskData : [])
      setAgentIds(Array.isArray(agentData) ? agentData : [])
      const merged = mergedAdminTokenAutocomplete(tokData, chainData)
      setTokenList(merged)
    }).catch(() => {
      setTasks([])
      setAgentIds([])
      setTokenList([])
    }).finally(() => setLoading(false))
  }, [selectedId])

  useEffect(() => {
    queueMicrotask(() => {
      void loadAll()
    })
  }, [loadAll])

  const sections = useMemo(() => {
    const bySectionKey: Record<string, AgentTask[]> = {}
    for (const t of tasks) {
      const name = t.task_group_name || "(unassigned)"
      const key = `${t.task_group_order || ""}\u0000${name}`
      if (!bySectionKey[key]) bySectionKey[key] = []
      bySectionKey[key].push(t)
    }
    return Object.entries(bySectionKey)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([sectionKey, rows]) => ({
        sectionKey,
        groupName: rows[0]?.task_group_name || "(unassigned)",
        rows: [...rows].sort((a, b) => {
          const as_ = a.task_seq ?? 999
          const bs_ = b.task_seq ?? 999
          if (as_ !== bs_) return as_ - bs_
          return a.task_key.localeCompare(b.task_key)
        }),
      }))
  }, [tasks])

  const sectionKeys = useMemo(() => sections.map(s => s.sectionKey), [sections])
  const {
    isExpanded,
    onExpandedChange,
    setExpandedKeys,
    expandedKeys,
  } = useSectionExpandPolicy({ sectionKeys })

  // Drop ghost expanded id when the open section's group vanishes from the list
  useEffect(() => {
    const keySet = new Set(sectionKeys)
    for (const k of expandedKeys) {
      if (!keySet.has(k)) {
        setExpandedKeys(new Set())
        break
      }
    }
  }, [sectionKeys, expandedKeys, setExpandedKeys])

  const taskKeyOptions = useMemo(
    () => [...new Set(tasks.map(t => t.task_key))].sort((a, b) => a.localeCompare(b)),
    [tasks],
  )

  const runNextSelectKeys = useMemo(() => {
    if (!editTask) return taskKeyOptions
    const key = editTask.task_key
    return taskKeyOptions.filter(k => {
      if (k === key) return false
      const edges = draftRunNextMap(tasks, key, k)
      // Mirror server rule: ignore edges whose endpoints aren't in the loaded task key universe.
      const filtered = new Map<string, string>()
      const allow = new Set(taskKeyOptions)
      for (const [src, dst] of edges) {
        if (allow.has(src) && allow.has(dst)) filtered.set(src, dst)
      }
      return runNextGraphIsAcyclic(filtered)
    })
  }, [tasks, editTask, taskKeyOptions])

  const runNextSelectKeysForUi = useMemo(() => {
    const cur = (editRunNext || "").trim()
    const base = runNextSelectKeys
    if (cur && !base.includes(cur) && cur !== editTask?.task_key) return [cur, ...base]
    return base
  }, [runNextSelectKeys, editRunNext, editTask])

  const runNextSelectionInvalid = useMemo(() => {
    const cur = (editRunNext || "").trim()
    if (!cur || !editTask) return false
    if (cur === editTask.task_key) return true
    const edges = draftRunNextMap(tasks, editTask.task_key, cur)
    const allow = new Set(taskKeyOptions)
    const filtered = new Map<string, string>()
    for (const [src, dst] of edges) {
      if (allow.has(src) && allow.has(dst)) filtered.set(src, dst)
    }
    return !runNextGraphIsAcyclic(filtered)
  }, [editRunNext, editTask, tasks, taskKeyOptions])

  function openEdit(row: AgentTask) {
    api(`/api/admin/tasks/${row.task_key}`).then(r => r.json()).then(full => {
      setEditTask({ ...row, ...full })
      setEditAgentId(full.agent_id || "")
      setEditSystem(full.system_prompt || "")
      setEditCache(full.cache_prompt || "")
      setEditCacheB((full.cache_prompt_b as string) || "")
      setEditCacheC((full.cache_prompt_c as string) || "")
      setEditCacheD((full.cache_prompt_d as string) || "")
      setEditUser(full.user_prompt || "")
      setEditNocache(full.nocache_prompt || "")
      setEditRunNext((full.run_next as string) || "")
      setEditGroupOrder(String(full.task_group_order ?? ""))
      setEditGroupName(String(full.task_group_name ?? ""))
      setEditTaskSeq(full.task_seq != null ? String(full.task_seq) : "")
      setEditTaskName(String(full.task_name ?? ""))
      const def = readDefaultEditPanel()
      setEditOpenPanel(def)
      setDefaultPanelPreference(def)
      setEditOpen(true)
    }).catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function handleSave() {
    if (!editTask) return
    api(`/api/admin/tasks/${editTask.task_key}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: editAgentId,
        system_prompt: editSystem,
        user_prompt: editUser,
        cache_prompt: editCache,
        cache_prompt_b: editCacheB,
        cache_prompt_c: editCacheC,
        cache_prompt_d: editCacheD,
        nocache_prompt: editNocache,
        run_next: editRunNext,
        task_group_order: editGroupOrder,
        task_group_name: editGroupName,
        task_seq: editTaskSeq.trim() === "" ? null : parseFloat(editTaskSeq),
        task_name: editTaskName,
      }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Update failed") })
        return r.json()
      })
      .then(() => {
        setEditOpen(false)
        setEditTask(null)
        setToast({ text: `Task "${editTask.task_key}" updated`, variant: "success" })
        setRepoJsonRefresh(n => n + 1)
        loadAll()
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function handlePreview() {
    if (!editTask) return
    setPreviewLoading(true)
    const params = new URLSearchParams()
    if (selectedId) params.set("candidate_id", selectedId)
    if (editTask.entity_type === "job" && previewJobId.trim()) {
      params.set("astral_job_id", previewJobId.trim())
    }
    const qs = params.toString() ? `?${params.toString()}` : ""
    api(`/api/admin/tasks/${editTask.task_key}/preview${qs}`)
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Preview failed") })
        return r.json()
      })
      .then(data => {
        setPreviewCandidateId(data.candidate_id || "")
        setPreviewData(data)
        setPreviewTab("system")
        setPreviewOpen(true)
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
      .finally(() => setPreviewLoading(false))
  }

  return (
    <div className="page-container">
      <div className="list-page-header">
        <h1 className="list-page-title">Manage Tasks</h1>
      </div>

      <RepoJsonDivergenceBanner
        tableKey="agent_task"
        refreshToken={repoJsonRefresh}
        onReverted={() => { setRepoJsonRefresh(n => n + 1); loadAll() }}
      />

      {loading ? (
        <div className="list-page-status">Loading...</div>
      ) : sections.length === 0 ? (
        <div className="list-page-status">No tasks configured.</div>
      ) : sections.map(sec => (
          <div key={sec.sectionKey} style={{ marginBottom: 12 }}>
            <CollapsiblePanel
              label={<>{sec.groupName} ({sec.rows.length})</>}
              expanded={isExpanded(sec.sectionKey)}
              onExpandedChange={next => onExpandedChange(sec.sectionKey, next)}
            >
              <div className="list-page-table-wrap">
                <table className="list-page-table">
                  <thead>
                    <tr>
                      <th>Task</th>
                      <th>Run next</th>
                      <th>Agent</th>
                      <th>Model</th>
                      <th style={{ textAlign: "right" }}>System</th>
                      <th style={{ textAlign: "right" }}>Base Cache</th>
                      <th style={{ textAlign: "right" }}>Parsed Cache</th>
                      <th style={{ textAlign: "right" }}>Cache Min</th>
                      <th style={{ textAlign: "right" }}>NoCache</th>
                      <th style={{ textAlign: "right" }}>Avg Live</th>
                      <th style={{ textAlign: "right" }}>Avg Output</th>
                      <th>Version</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sec.rows.map(row => (
                      <tr key={row.task_key} className="clickable" onClick={() => openEdit(row)}>
                        <td>
                          {!row.task_ready && <span style={{ color: "#f87171", marginRight: 5 }}>●</span>}
                          {row.task_name || row.task_key}
                        </td>
                        <td style={{ color: "var(--text-secondary)" }}>{row.run_next || "—"}</td>
                        <td style={{ color: "var(--text-secondary)" }}>{row.agent_id || "—"}</td>
                        <td style={{ color: "var(--text-secondary)" }}>{row.model_code || "—"}</td>
                        <td style={{ textAlign: "right" }}>{row.system_prompt_tokens.toLocaleString()}</td>
                        <td style={{ textAlign: "right" }}>{row.base_cache_tokens.toLocaleString()}</td>
                        <td style={{ textAlign: "right" }}>{row.parsed_cache_tokens != null ? row.parsed_cache_tokens.toLocaleString() : <span style={{ color: "var(--text-secondary)" }}>TBD</span>}</td>
                        <td style={{ textAlign: "right" }}><CacheMinCell tokens={row.cache_min_tokens} satisfied={row.cache_satisfied} /></td>
                        <td style={{ textAlign: "right" }}>{row.nocache_prompt_tokens.toLocaleString()}</td>
                        <td style={{ textAlign: "right", color: "var(--text-secondary)" }}>{fmt(row.avg_live_tokens)}</td>
                        <td style={{ textAlign: "right", color: "var(--text-secondary)" }}>{fmt(row.avg_output_tokens)}</td>
                        <td style={{ color: "var(--text-secondary)", fontSize: 12 }}><Time value={row.updated_at} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CollapsiblePanel>
          </div>
        ))}

      {/* Edit modal */}
      <Modal
        open={editOpen}
        onClose={() => { setEditOpen(false); setEditTask(null) }}
        title={editTask ? `Edit: ${editTask.task_key}` : ""}
        onSave={handleSave}
      >
        {editTask && (
          <div style={{ display: "flex", gap: 24, marginBottom: 12, fontSize: 13, color: "var(--text-secondary)" }}>
            <span><strong>Model:</strong> {editTask.model_code || "—"}</span>
          </div>
        )}

        <div className="dep-field">
          <label className="dep-field-label">Group order</label>
          <input className="dep-input" value={editGroupOrder} onChange={e => setEditGroupOrder(e.target.value)} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Group name</label>
          <input className="dep-input" value={editGroupName} onChange={e => setEditGroupName(e.target.value)} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Task sequence</label>
          <input className="dep-input" type="number" step="any" value={editTaskSeq} onChange={e => setEditTaskSeq(e.target.value)} />
        </div>
        <div className="dep-field">
          <label className="dep-field-label">Task name</label>
          <input className="dep-input" value={editTaskName} onChange={e => setEditTaskName(e.target.value)} />
        </div>

        <div className="dep-field">
          <label className="dep-field-label">Agent</label>
          <select
            className="dep-input"
            value={editAgentId}
            onChange={e => setEditAgentId(e.target.value)}
          >
            <option value="">— Select Agent —</option>
            {agentIds.map(id => <option key={id} value={id}>{id}</option>)}
          </select>
        </div>

        <div className="dep-field">
          <label className="dep-field-label">Run next</label>
          <select
            className="dep-input"
            value={editRunNext}
            onChange={e => setEditRunNext(e.target.value)}
          >
            <option value="">— none —</option>
            {runNextSelectKeysForUi.map(k => <option key={k} value={k}>{k}</option>)}
          </select>
          {runNextSelectionInvalid && (
            <div style={{ marginTop: 6, fontSize: 11, color: "#f87171" }}>
              Current value would repeat a task in this chain. Clear it or pick a different next hop.
            </div>
          )}
        </div>
        <div className="dep-field admin-task-prompts-edit-panels" style={{ marginTop: 12 }}>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.system}
            expanded={editOpenPanel === "system"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("system")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editSystem} onChange={setEditSystem}
              tokens={tokenList} rows={10}
              placeholder="Empty = use assigned agent content. {$SELECTED_AGENT} injects the agent system prompt at runtime." />
          </CollapsiblePanel>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.cache}
            expanded={editOpenPanel === "cache"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("cache")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editCache} onChange={setEditCache}
              tokens={tokenList} rows={14} placeholder="Cache block A (ephemeral cached at API when non-empty)." />
          </CollapsiblePanel>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.cache_b}
            expanded={editOpenPanel === "cache_b"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("cache_b")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editCacheB} onChange={setEditCacheB}
              tokens={tokenList} rows={14} placeholder="Cache block B (optional)." />
          </CollapsiblePanel>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.cache_c}
            expanded={editOpenPanel === "cache_c"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("cache_c")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editCacheC} onChange={setEditCacheC}
              tokens={tokenList} rows={14} placeholder="Cache block C (optional)." />
          </CollapsiblePanel>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.cache_d}
            expanded={editOpenPanel === "cache_d"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("cache_d")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editCacheD} onChange={setEditCacheD}
              tokens={tokenList} rows={14} placeholder="Cache block D (optional)." />
          </CollapsiblePanel>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.nocache}
            expanded={editOpenPanel === "nocache"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("nocache")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editNocache} onChange={setEditNocache}
              tokens={tokenList} rows={20} placeholder="No-cache segment (dynamic context; not cached at API)." />
          </CollapsiblePanel>
          <CollapsiblePanel
            label={EDIT_PANEL_LABELS.user}
            expanded={editOpenPanel === "user"}
            onExpandedChange={next => {
              if (next) setEditOpenPanel("user")
              else setEditOpenPanel(null)
            }}
          >
            <TokenTextarea className="dep-input" value={editUser} onChange={setEditUser}
              tokens={tokenList} rows={14} placeholder="User prompt content..." />
          </CollapsiblePanel>
        </div>

        <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", alignItems: "center", gap: 12, justifyContent: "space-between" }}>
          <label style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: 8 }}>
            Default panel when opening editor:
            <select
              className="dep-input"
              style={{ width: "auto", minWidth: 140, fontSize: 12, padding: "4px 8px" }}
              value={defaultPanelPreference}
              onChange={e => {
                const v = e.target.value as TabKey
                setDefaultPanelPreference(v)
                setEditOpenPanel(v)
                try {
                  localStorage.setItem(ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS, v)
                } catch {
                  /* ignore */
                }
              }}
            >
              <option value="cache">Cache Block A</option>
              <option value="cache_b">Cache Block B</option>
              <option value="cache_c">Cache Block C</option>
              <option value="cache_d">Cache Block D</option>
              <option value="nocache">No cache</option>
            </select>
          </label>
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8 }}>
            {editTask?.entity_type === "job" && (
              <label style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: 6 }}>
                Job ID (optional)
                <input
                  className="dep-input"
                  type="text"
                  value={previewJobId}
                  onChange={e => setPreviewJobId(e.target.value)}
                  placeholder="astral job id"
                  style={{ width: 200, fontSize: 12, padding: "4px 8px" }}
                />
              </label>
            )}
            <button className="dep-btn cancel" type="button" onClick={handlePreview} disabled={previewLoading}
              style={{ fontSize: 12, padding: "5px 12px" }}>
              {previewLoading ? "Loading..." : "Preview Resolved"}
            </button>
            <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>
              Previews saved content
            </span>
          </div>
        </div>
      </Modal>

      {/* Preview modal */}
      <Modal
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        title={editTask ? `Preview: ${editTask.task_key}${previewCandidateId ? ` (${previewCandidateId})` : ""}` : "Preview"}
      >
        <TabBar tabs={PREVIEW_TABS} active={previewTab} onChange={key => setPreviewTab(key)} />
        <pre style={{
          marginTop: 12, padding: 12, borderRadius: 4,
          background: "var(--bg-deep)", border: "1px solid var(--border)",
          color: "var(--text-primary)", fontFamily: "monospace", fontSize: 12,
          whiteSpace: "pre-wrap", wordBreak: "break-word",
          maxHeight: 500, overflow: "auto",
        }}>
          {previewField(previewTab, previewData) || "(empty)"}
        </pre>
      </Modal>

      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
