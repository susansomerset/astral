import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { TabBar } from "../components/TabbedTextArea"
import TokenTextarea from "../components/TokenTextarea"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import { useLocalStorage } from "../lib/useLocalStorage"

const LS = "adhoc:"  // localStorage key prefix

type TabKey = "user" | "cache" | "nocache"
type PreviewKey = "system" | "cache" | "nocache" | "user" | "live_content"

const TABS: { key: TabKey; label: string }[] = [
  { key: "user", label: "User Prompt" },
  { key: "cache", label: "Cache Prompt" },
  { key: "nocache", label: "NoCache Prompt" },
]

const PREVIEW_TABS: { key: PreviewKey; label: string }[] = [
  { key: "system",       label: "System" },
  { key: "cache",        label: "Cache" },
  { key: "nocache",      label: "NoCache" },
  { key: "user",         label: "User" },
  { key: "live_content", label: "Live Content" },
]

interface TaskSummary {
  task_key: string
  user_prompt_len?: number
  cache_prompt_len?: number
  nocache_prompt_len?: number
}

interface EntityOption { id: string; label: string }
interface EntityMeta { entity_type: string; trigger_state: string; batch_mode: boolean; entities: EntityOption[] }
interface PreviewData extends Record<PreviewKey, string> {}

function byteSize(s: string): string {
  const b = new Blob([s]).size
  if (b >= 1024 * 1024) return `${(b / 1024 / 1024).toFixed(1)} MB`
  if (b >= 1024) return `${(b / 1024).toFixed(1)} KB`
  return `${b} B`
}

export default function AnthropicAdHoc() {
  const { selectedId, candidates } = useCandidate()
  const candidateName = useMemo(() => {
    const c = candidates.find(c => c.astral_candidate_id === selectedId)
    if (!c) return null
    const cd = c.candidate_data || {}
    return [cd.first as string, cd.last as string].filter(Boolean).join(" ") || selectedId
  }, [candidates, selectedId])

  const [agentIds, setAgentIds] = useState<string[]>([])
  const [tokenList, setTokenList] = useState<string[]>([])
  const [tasks, setTasks] = useState<TaskSummary[]>([])

  const [agentId, setAgentId] = useLocalStorage<string>(`${LS}agentId`, "")
  const [taskKey, setTaskKey] = useLocalStorage<string>(`${LS}taskKey`, "")
  const [entityId, setEntityId] = useLocalStorage<string>(`${LS}entityId`, "")
  const [batchCount, setBatchCount] = useLocalStorage<number>(`${LS}batchCount`, 5)

  const [entityMeta, setEntityMeta] = useState<EntityMeta | null>(null)

  const entityMeta_batchIds = entityMeta?.batch_mode
    ? entityMeta.entities.slice(0, batchCount).map(e => e.id)
    : null
  const [userPrompt, setUserPrompt] = useLocalStorage<string>(`${LS}userPrompt`, "")
  const [cachePrompt, setCachePrompt] = useLocalStorage<string>(`${LS}cachePrompt`, "")
  const [nocachePrompt, setNocachePrompt] = useLocalStorage<string>(`${LS}nocachePrompt`, "")
  const [activeTab, setActiveTab] = useLocalStorage<TabKey>(`${LS}activeTab`, "user")

  const [previewing, setPreviewing] = useState(false)
  const [previewData, setPreviewData] = useState<PreviewData | null>(null)
  const [previewTab, setPreviewTab] = useState<PreviewKey>("system")

  const [testing, setTesting] = useState(false)
  const [response, setResponse] = useState<string | null>(null)
  const [timesheet, setTimesheet] = useState<Record<string, unknown> | null>(null)

  const [saveAsOpen, setSaveAsOpen] = useState(false)
  const [confirmTask, setConfirmTask] = useState<string | null>(null)
  const [confirmFetch, setConfirmFetch] = useState<string | null>(null)
  const saveRef = useRef<HTMLDivElement>(null)
  const isInitialMount = useRef(true)

  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    Promise.all([
      api("/api/admin/agents/ids").then(r => r.json()),
      api("/api/admin/tasks/meta/tokens").then(r => r.json()),
      api("/api/admin/tasks").then(r => r.json()),
    ]).then(([agentData, tokData, taskData]) => {
      setAgentIds(Array.isArray(agentData) ? agentData : [])
      setTokenList(Array.isArray(tokData) ? tokData : [])
      setTasks(Array.isArray(taskData) ? taskData : [])
    })
    // If no taskKey was restored, flip the mount flag now so the first user
    // selection correctly triggers the entity + prompt-fetch logic
    if (!taskKey) isInitialMount.current = false
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Dismiss save-as dropdown on outside click
  useEffect(() => {
    if (!saveAsOpen) return
    function handler(e: MouseEvent) {
      if (saveRef.current && !saveRef.current.contains(e.target as Node)) setSaveAsOpen(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [saveAsOpen])

  // When task key changes, load entity list + prompts
  useEffect(() => {
    if (!taskKey) { setEntityMeta(null); return }

    // Always reload entities (they may change; entityId is persisted separately)
    const params = new URLSearchParams({ task_key: taskKey })
    if (selectedId) params.set("candidate_id", selectedId)
    api(`/api/admin/adhoc/entities?${params}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setEntityMeta(d || null))

    // On initial mount with a restored taskKey: skip the prompt-fetch entirely
    // (user's own prompts are already restored from localStorage)
    if (isInitialMount.current) { isInitialMount.current = false; return }

    // User actively changed the task key — offer to load its prompts
    const existing = tasks.find(t => t.task_key === taskKey)
    if (!existing) return
    if (userPrompt || cachePrompt || nocachePrompt) {
      setConfirmFetch(taskKey)
    } else {
      doFetchFrom(taskKey)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskKey, selectedId])

  const hasContent = userPrompt.trim() || cachePrompt.trim() || nocachePrompt.trim()

  function handlePreview() {
    if (!agentId) { setToast({ text: "Select an agent first", variant: "error" }); return }
    setPreviewing(true)
    api("/api/admin/adhoc/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: agentId,
        task_key: taskKey || "",
        entity_id: entityMeta_batchIds ? "" : (entityId || ""),
        entity_ids: entityMeta_batchIds || undefined,
        user_prompt: userPrompt,
        cache_prompt: cachePrompt,
        nocache_prompt: nocachePrompt,
        candidate_id: selectedId || "",
      }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Preview failed") })
        return r.json()
      })
      .then(data => { setPreviewData(data as PreviewData); setPreviewTab("system") })
      .catch(e => setToast({ text: e.message, variant: "error" }))
      .finally(() => setPreviewing(false))
  }

  function handleTest() {
    if (!agentId) { setToast({ text: "Select an agent first", variant: "error" }); return }
    setTesting(true)
    setResponse(null)
    setTimesheet(null)
    api("/api/admin/adhoc/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: agentId,
        task_key: taskKey || "",
        entity_id: entityMeta_batchIds ? "" : (entityId || ""),
        entity_ids: entityMeta_batchIds || undefined,
        user_prompt: userPrompt,
        cache_prompt: cachePrompt,
        nocache_prompt: nocachePrompt,
        candidate_id: selectedId || "",
      }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || `HTTP ${r.status}`) })
        return r.json()
      })
      .then(data => {
        if (data.success) {
          setResponse(data.response_text)
          setTimesheet(data.timesheet || null)
        } else {
          setResponse(`ERROR: ${data.error || "Unknown error"}`)
        }
      })
      .catch(e => setResponse(`ERROR: ${e.message}`))
      .finally(() => setTesting(false))
  }

  function doFetchFrom(fetchKey: string) {
    setConfirmFetch(null)
    api(`/api/admin/tasks/${fetchKey}`)
      .then(r => r.json())
      .then(data => {
        setUserPrompt(data.user_prompt || "")
        setCachePrompt(data.cache_prompt || "")
        setNocachePrompt(data.nocache_prompt || "")
        setToast({ text: `Loaded prompts from "${fetchKey}"`, variant: "success" })
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function handleSaveAs(key: string) {
    setSaveAsOpen(false)
    const task = tasks.find(t => t.task_key === key)
    const existing = task && ((task.user_prompt_len || 0) > 0 || (task.cache_prompt_len || 0) > 0 || (task.nocache_prompt_len || 0) > 0)
    if (existing) { setConfirmTask(key); return }
    doSaveAs(key)
  }

  function doSaveAs(key: string) {
    setConfirmTask(null)
    api(`/api/admin/tasks/${key}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agentId || undefined, user_prompt: userPrompt, cache_prompt: cachePrompt, nocache_prompt: nocachePrompt }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Save failed") })
        return r.json()
      })
      .then(() => {
        setToast({ text: `Prompts saved to "${key}"`, variant: "success" })
        api("/api/admin/tasks").then(r => r.json()).then(d => setTasks(Array.isArray(d) ? d : []))
      })
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  function formatResponse(text: string): string {
    try { return JSON.stringify(JSON.parse(text), null, 2) } catch { return text }
  }

  // Build preview tab label with byte size badge
  const previewTabsWithSize = PREVIEW_TABS.map(t => ({
    ...t,
    label: previewData
      ? `${t.label} (${byteSize(previewData[t.key] || "")})`
      : t.label,
  }))

  return (
    <div style={{ padding: 24, maxWidth: 1100 }}>
      <h1 style={{ margin: "0 0 16px", fontSize: 22, color: "var(--text-primary)" }}>Agent Ad Hoc</h1>

      {candidateName && (
        <div style={{ marginBottom: 12, fontSize: 13, color: "var(--text-secondary)" }}>
          Candidate: <strong style={{ color: "var(--accent-gold)" }}>{candidateName}</strong>
        </div>
      )}

      {/* ── Row 1: Task Key (Fetch From) + Agent ── */}
      <div style={{ display: "flex", gap: 16, marginBottom: 12, alignItems: "flex-end" }}>
        <div className="dep-field" style={{ flex: 1, maxWidth: 340 }}>
          <label className="dep-field-label">Task Key <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(loads prompts + entities)</span></label>
          <select className="dep-input" value={taskKey} onChange={e => setTaskKey(e.target.value)}>
            <option value="">— No Task (ad hoc) —</option>
            {tasks.map(t => <option key={t.task_key} value={t.task_key}>{t.task_key}</option>)}
          </select>
        </div>
        <div className="dep-field" style={{ flex: 1, maxWidth: 280 }}>
          <label className="dep-field-label">Agent</label>
          <select className="dep-input" value={agentId} onChange={e => setAgentId(e.target.value)}>
            <option value="">— Select Agent —</option>
            {agentIds.map(id => <option key={id} value={id}>{id}</option>)}
          </select>
        </div>
      </div>

      {/* ── Row 2: Task meta badges + entity picker ── */}
      {entityMeta && (
        <div style={{ display: "flex", gap: 12, marginBottom: 16, alignItems: "center", flexWrap: "wrap" }}>
          <span style={{
            fontSize: 12, fontFamily: "monospace", padding: "2px 8px",
            borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--border)",
            color: "var(--text-secondary)",
          }}>
            entity: <strong style={{ color: "var(--accent-gold)" }}>{entityMeta.entity_type}</strong>
          </span>
          <span style={{
            fontSize: 12, fontFamily: "monospace", padding: "2px 8px",
            borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--border)",
            color: "var(--text-secondary)",
          }}>
            trigger: <strong style={{ color: "var(--accent-gold)" }}>{entityMeta.trigger_state}</strong>
          </span>
          <div className="dep-field" style={{ margin: 0, minWidth: 280, flex: 1, maxWidth: 480 }}>
            {entityMeta.batch_mode ? (
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <label className="dep-field-label" style={{ margin: 0, whiteSpace: "nowrap" }}>First</label>
                <input
                  type="number" min={1} max={entityMeta.entities.length || 30}
                  className="dep-input"
                  value={batchCount}
                  onChange={e => setBatchCount(Math.max(1, parseInt(e.target.value) || 1))}
                  style={{ width: 64, textAlign: "center" }}
                />
                <span style={{ fontSize: 12, color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                  of {entityMeta.entities.length} entities
                </span>
              </div>
            ) : (
              <select
                className="dep-input"
                value={entityId}
                onChange={e => setEntityId(e.target.value)}
                style={{ fontSize: 13 }}
              >
                <option value="">— No entity (ad hoc) —</option>
                {entityMeta.entities.map(e => (
                  <option key={e.id} value={e.id}>{e.label}</option>
                ))}
              </select>
            )}
          </div>
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
            {entityMeta.entities.length} available
          </span>
        </div>
      )}

      {/* ── Action buttons ── */}
      <div style={{ marginBottom: 16, display: "flex", gap: 12, alignItems: "center" }}>
        <button className="dep-btn cancel" onClick={handlePreview} disabled={previewing || !agentId}>
          {previewing ? "Loading..." : "Preview Prompt"}
        </button>
        <button className="dep-btn save" onClick={handleTest} disabled={testing || !agentId} style={{ minWidth: 100 }}>
          {testing ? "Testing..." : "▶ Test"}
        </button>

        {/* SAVE AS */}
        <div ref={saveRef} style={{ position: "relative" }}>
          <button className="dep-btn cancel" onClick={() => setSaveAsOpen(!saveAsOpen)} disabled={!hasContent}>
            Save As
          </button>
          {saveAsOpen && (
            <div style={{
              position: "absolute", top: "100%", left: 0, marginTop: 4, zIndex: 50,
              background: "var(--bg-elevated)", border: "1px solid var(--border)",
              borderRadius: 4, boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
              maxHeight: 300, overflowY: "auto", minWidth: 280,
            }}>
              {tasks.map(t => {
                const hasExisting = (t.user_prompt_len || 0) > 0 || (t.cache_prompt_len || 0) > 0 || (t.nocache_prompt_len || 0) > 0
                return (
                  <div key={t.task_key} onClick={() => handleSaveAs(t.task_key)} style={{
                    padding: "6px 12px", cursor: "pointer", fontSize: 13, fontFamily: "monospace",
                    color: hasExisting ? "var(--accent-gold)" : "var(--text-secondary)",
                  }}
                    onMouseEnter={e => (e.currentTarget.style.background = "var(--bg-card)")}
                    onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                  >
                    {t.task_key}{hasExisting ? " ●" : ""}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* ── Confirmation banners ── */}
      {confirmFetch && (
        <div style={{ marginBottom: 12, padding: 12, borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--accent-gold)" }}>
          <span style={{ color: "var(--accent-gold)", fontSize: 13 }}>
            Replace current prompt content with prompts from <strong>{confirmFetch}</strong>?
          </span>
          <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
            <button className="dep-btn save" onClick={() => doFetchFrom(confirmFetch)} style={{ fontSize: 12, padding: "4px 12px" }}>Yes, Replace</button>
            <button className="dep-btn cancel" onClick={() => setConfirmFetch(null)} style={{ fontSize: 12, padding: "4px 12px" }}>Cancel</button>
          </div>
        </div>
      )}
      {confirmTask && (
        <div style={{ marginBottom: 12, padding: 12, borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--accent-gold)" }}>
          <span style={{ color: "var(--accent-gold)", fontSize: 13 }}>
            Overwrite existing prompts for <strong>{confirmTask}</strong>?
          </span>
          <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
            <button className="dep-btn save" onClick={() => doSaveAs(confirmTask)} style={{ fontSize: 12, padding: "4px 12px" }}>Yes, Overwrite</button>
            <button className="dep-btn cancel" onClick={() => setConfirmTask(null)} style={{ fontSize: 12, padding: "4px 12px" }}>Cancel</button>
          </div>
        </div>
      )}

      {/* ── Prompt editor tabs ── */}
      <div style={{ marginTop: 8 }}>
        <TabBar tabs={TABS} active={activeTab} onChange={setActiveTab} />
        <div style={{ marginTop: 12 }}>
          {activeTab === "user" && (
            <TokenTextarea className="dep-input" value={userPrompt} onChange={setUserPrompt}
              tokens={tokenList} rows={16} placeholder="User prompt content..." />
          )}
          {activeTab === "cache" && (
            <TokenTextarea className="dep-input" value={cachePrompt} onChange={setCachePrompt}
              tokens={tokenList} rows={22} placeholder="Cache prompt content (large context blocks)..." />
          )}
          {activeTab === "nocache" && (
            <TokenTextarea className="dep-input" value={nocachePrompt} onChange={setNocachePrompt}
              tokens={tokenList} rows={22} placeholder="NoCache prompt content (dynamic context)..." />
          )}
        </div>
      </div>

      {/* ── Preview area ── */}
      {previewData && (
        <div style={{ marginTop: 20 }}>
          <h3 style={{ margin: "0 0 8px", fontSize: 14, color: "var(--text-secondary)" }}>Resolved Prompt Preview</h3>
          <TabBar tabs={previewTabsWithSize} active={previewTab} onChange={setPreviewTab} />
          <pre style={{
            marginTop: 12, padding: 16, borderRadius: 4,
            background: "var(--bg-deep)", border: "1px solid var(--border)",
            color: "var(--text-primary)", fontFamily: "monospace", fontSize: 12,
            whiteSpace: "pre-wrap", wordBreak: "break-word",
            maxHeight: 520, overflow: "auto",
          }}>
            {previewData[previewTab] || "(empty)"}
          </pre>
        </div>
      )}

      {/* ── Response area ── */}
      {response !== null && (
        <div style={{ marginTop: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <h3 style={{ margin: 0, fontSize: 14, color: "var(--text-secondary)" }}>Response</h3>
            {timesheet && (
              <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "monospace" }}>
                {timesheet.duration ? `${Number(timesheet.duration).toFixed(1)}s` : ""}
                {timesheet.inputtotal ? ` · ${timesheet.inputtotal} in` : ""}
                {timesheet.outputtotal ? ` · ${timesheet.outputtotal} out` : ""}
                {timesheet.inputcached ? ` · ${timesheet.inputcached} cached` : ""}
              </span>
            )}
          </div>
          <pre style={{
            padding: 16, borderRadius: 4,
            background: "var(--bg-deep)", border: "1px solid var(--border)",
            color: response.startsWith("ERROR:") ? "#ff6b6b" : "var(--text-primary)",
            fontFamily: "monospace", fontSize: 13,
            whiteSpace: "pre-wrap", wordBreak: "break-word",
            maxHeight: 600, overflow: "auto",
          }}>
            {formatResponse(response)}
          </pre>
        </div>
      )}

      {/* ── Hydrated output (for abbreviated output_type tasks) ── */}
      {/* Hydrated response section disabled for now — showing raw response is sufficient for debugging */}

      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
