import { useCallback, useEffect, useRef, useState } from "react"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import api from "../lib/api"

interface QueryResult {
  type: "select" | "execute"
  columns?: string[]
  rows?: Record<string, unknown>[]
  count?: number
  rows_affected?: number
}

interface FieldInfo {
  name: string
  type: string
  pk: boolean
}

const HISTORY_KEY = "sql:history"
const MAX_HISTORY = 200

function loadHistory(): string[] {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]") } catch { return [] }
}
function saveHistory(h: string[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(h.slice(0, MAX_HISTORY)))
}
function pushToHistory(h: string[], sql: string): string[] {
  const trimmed = sql.trim()
  if (!trimmed) return h
  // Dedupe: remove prior identical entry, then prepend
  const next = [trimmed, ...h.filter(s => s !== trimmed)]
  saveHistory(next)
  return next
}

async function runSql(query: string): Promise<QueryResult> {
  const r = await api("/api/admin/data/sql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sql: query }),
  })
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`)
  return data
}

export default function DataManagement() {
  const [sql, setSql] = useState("")
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<QueryResult | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [expandedCells, setExpandedCells] = useState<Set<string>>(new Set())
  const [history, setHistory] = useState<string[]>(loadHistory)
  const histIdx = useRef(-1)
  const clearToast = useCallback(() => setToast(null), [])

  // Table upsert (Copy Output → SQLite)
  const [upsertTable, setUpsertTable] = useState("")
  const [upsertModalOpen, setUpsertModalOpen] = useState(false)
  const [upsertJson, setUpsertJson] = useState("")
  const [upsertPosting, setUpsertPosting] = useState(false)

  const handleUpsertModalClose = useCallback(() => {
    if (upsertPosting) return
    setUpsertModalOpen(false)
  }, [upsertPosting])

  /** Modal Save — dispatch async upsert (Modal does not await handlers). */
  function handleUpsertApply() {
    void (async () => {
      if (!upsertJson.trim()) {
        setToast({ text: "Paste JSON rows first.", variant: "error" })
        return
      }
      if (upsertPosting) return
      const table = upsertTable.trim()
      if (!window.confirm(`Apply JSON upsert into table "${table}"? Unrelated rows remain untouched.`)) return

      setUpsertPosting(true)
      try {
        const r = await api("/api/admin/data/table_copy_upsert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ table, json_payload: upsertJson }),
        })
        const data = await r.json() as { ok?: boolean; error?: string; inserted?: number; updated?: number; skipped?: number }
        if (!r.ok || data.ok === false) {
          throw new Error(typeof data.error === "string" ? data.error : `HTTP ${r.status}`)
        }
        setToast({
          text: `Upsert completed: inserted ${data.inserted ?? 0}, updated ${data.updated ?? 0}, skipped ${data.skipped ?? 0}`,
          variant: "success",
        })
        setUpsertJson("")
        setUpsertModalOpen(false)
      } catch (e) {
        setToast({ text: (e as Error).message, variant: "error" })
      } finally {
        setUpsertPosting(false)
      }
    })()
  }

  // Schema browser state
  const [tables, setTables] = useState<string[]>([])
  const [selectedTable, setSelectedTable] = useState("")
  const [fields, setFields] = useState<FieldInfo[]>([])

  useEffect(() => {
    runSql("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
      .then(r => setTables((r.rows ?? []).map(row => String(row.name))))
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedTable) { setFields([]); return }
    runSql(`PRAGMA table_info(${selectedTable})`)
      .then(r => setFields((r.rows ?? []).map(row => ({
        name: String(row.name),
        type: String(row.type || ""),
        pk: row.pk === 1,
      }))))
      .catch(() => setFields([]))
  }, [selectedTable])

  async function handleRun() {
    if (!sql.trim()) return
    setRunning(true)
    setResult(null)
    setExpandedCells(new Set())
    try {
      const data = await runSql(sql)
      setResult(data)
      setHistory(prev => pushToHistory(prev, sql))
      histIdx.current = -1
      if (data.type === "execute") {
        setToast({ text: `${data.rows_affected} row(s) affected`, variant: "success" })
      }
    } catch (e) {
      setToast({ text: (e as Error).message, variant: "error" })
    } finally {
      setRunning(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault()
      handleRun()
    }
  }

  function navigateHistory(dir: -1 | 1) {
    if (history.length === 0) return
    const next = Math.max(0, Math.min(history.length - 1, histIdx.current + dir))
    histIdx.current = next
    setSql(history[next])
  }

  function toggleCell(key: string) {
    setExpandedCells(prev => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  return (
    <div style={{ padding: 24, maxWidth: 1200 }}>
      <h1 style={{ margin: "0 0 16px", fontSize: 22, color: "var(--text-primary)" }}>Data Management</h1>

      {/* Table Upsert — paste Copy Output JSON */}
      <div style={{
        marginBottom: 20, padding: "12px 16px",
        border: "1px solid var(--border)", borderRadius: 6,
        background: "var(--bg-elevated)",
      }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <label style={{ fontSize: 13, color: "var(--text-primary)", fontWeight: 500 }}>Table Upsert</label>
          <select
            className="dep-input"
            value={upsertTable}
            onChange={e => setUpsertTable(e.target.value)}
            disabled={upsertPosting}
            style={{ fontSize: 12, padding: "3px 8px", minWidth: 220 }}
          >
            <option value="">— select table —</option>
            {tables.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <button
            type="button"
            className="dep-btn save"
            onClick={() => setUpsertModalOpen(true)}
            disabled={!upsertTable.trim() || upsertPosting}
            style={{ fontSize: 12 }}
          >
            Update
          </button>
        </div>
      </div>

      <Modal
        open={upsertModalOpen}
        onClose={handleUpsertModalClose}
        title={`Upsert rows — ${upsertTable}`}
        size="wide"
        dirty={upsertJson.trim().length > 0}
        onSave={handleUpsertApply}
      >
        <textarea
          className="dep-input"
          value={upsertJson}
          onChange={e => setUpsertJson(e.target.value)}
          rows={16}
          placeholder="Paste Copy Output JSON array here"
          style={{ width: "100%", fontFamily: "monospace", fontSize: 12, resize: "vertical", boxSizing: "border-box" }}
          disabled={upsertPosting}
          spellCheck={false}
        />
      </Modal>

      <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
        {/* Schema browser panel */}
        <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 8 }}>
          <label style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1 }}>Tables</label>
          <div style={{
            border: "1px solid var(--border)", borderRadius: 4,
            background: "var(--bg-elevated)", overflowY: "auto",
            maxHeight: 260, minHeight: 120,
          }}>
            {tables.length === 0 && (
              <div style={{ padding: "8px 10px", fontSize: 12, color: "var(--text-muted)" }}>Loading…</div>
            )}
            {tables.map(t => (
              <div
                key={t}
                onClick={() => setSelectedTable(t)}
                style={{
                  padding: "4px 10px", fontSize: 12, fontFamily: "monospace",
                  cursor: "pointer", color: "var(--text-primary)",
                  background: t === selectedTable ? "var(--accent-gold-dim, rgba(212,168,67,0.15))" : "transparent",
                }}
              >{t}</div>
            ))}
          </div>

          {selectedTable && (
            <>
              <label style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, marginTop: 4 }}>
                Fields — {selectedTable}
              </label>
              <div style={{
                border: "1px solid var(--border)", borderRadius: 4,
                background: "var(--bg-elevated)", overflowY: "auto",
                maxHeight: 300,
              }}>
                {fields.map(f => (
                  <div key={f.name} style={{
                    padding: "3px 10px", fontSize: 12, fontFamily: "monospace",
                    color: "var(--text-primary)",
                  }}>
                    {f.pk ? "🔑 " : ""}<span style={{ color: "var(--accent-gold)" }}>{f.name}</span>{" "}
                    <span style={{ color: "var(--text-muted)" }}>{f.type}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Main query panel */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 4, paddingTop: 2 }}>
              <button
                className="sql-hist-btn"
                onClick={() => navigateHistory(-1)}
                disabled={history.length === 0}
                title="Previous query"
              >▲</button>
              <button
                className="sql-hist-btn"
                onClick={() => navigateHistory(1)}
                disabled={history.length === 0}
                title="Next query"
              >▼</button>
            </div>
            <textarea
              className="dep-input"
              value={sql}
              onChange={e => { setSql(e.target.value); histIdx.current = -1 }}
              onKeyDown={handleKeyDown}
              rows={6}
              placeholder="SELECT * FROM agent_task LIMIT 10;  (Cmd+Enter to run)"
              style={{ flex: 1, fontFamily: "monospace", fontSize: 13, resize: "vertical" }}
            />
          </div>

          <div style={{ marginTop: 12, display: "flex", gap: 12, alignItems: "center" }}>
            <button className="dep-btn save" onClick={handleRun} disabled={running || !sql.trim()}>
              {running ? "Running..." : "Run"}
            </button>
            {result?.type === "select" && (
              <>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{result.count} row(s)</span>
                <button className="dep-btn cancel" onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(result.rows, null, 2))
                  setToast({ text: "Copied to clipboard", variant: "success" })
                }}>
                  Copy Output
                </button>
              </>
            )}
          </div>

      {result?.type === "select" && result.columns && result.rows && (
        <div style={{ marginTop: 16, overflow: "auto", maxHeight: "70vh", border: "1px solid var(--border)", borderRadius: 4 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, fontFamily: "monospace" }}>
            <thead>
              <tr>
                {result.columns.map(col => (
                  <th key={col} style={{
                    position: "sticky", top: 0, padding: "8px 12px", textAlign: "left",
                    background: "var(--bg-elevated)", color: "var(--accent-gold)",
                    borderBottom: "2px solid var(--border)", whiteSpace: "nowrap",
                  }}>
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.rows.map((row, i) => (
                <tr key={i}>
                  {result.columns!.map(col => {
                    const cellKey = `${i}:${col}`
                    const expanded = expandedCells.has(cellKey)
                    const raw = row[col]
                    const isLong = isLongValue(raw)
                    return (
                      <td key={col}
                        onClick={isLong ? () => toggleCell(cellKey) : undefined}
                        style={{
                          padding: "6px 12px", borderBottom: "1px solid var(--border)",
                          color: "var(--text-primary)", verticalAlign: "top",
                          cursor: isLong ? "pointer" : "default",
                          ...(expanded ? {} : { whiteSpace: "nowrap", maxWidth: 400, overflow: "hidden", textOverflow: "ellipsis" }),
                        }}
                      >
                        {expanded ? (
                          <pre style={{
                            margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-word",
                            maxHeight: 500, overflow: "auto", fontSize: 12,
                            background: "var(--bg-deep)", padding: 8, borderRadius: 4,
                          }}>
                            {formatExpanded(raw)}
                          </pre>
                        ) : formatCell(raw)}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
        </div>
      </div>

      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}

function isLongValue(val: unknown): boolean {
  if (val === null || val === undefined) return false
  const s = String(val)
  return s.length > 60 || s.startsWith("{") || s.startsWith("[")
}

function formatCell(val: unknown): string {
  if (val === null || val === undefined) return "NULL"
  if (typeof val === "object") return JSON.stringify(val)
  return String(val)
}

function formatExpanded(val: unknown): string {
  if (val === null || val === undefined) return "NULL"
  const s = typeof val === "object" ? JSON.stringify(val) : String(val)
  // Try to pretty-print JSON strings
  try {
    return JSON.stringify(JSON.parse(s), null, 2)
  } catch {
    return s
  }
}
