import { Fragment, type ReactNode, useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom"
import api from "../lib/api"
import Time from "../components/Time"
import { useCandidate } from "../contexts/CandidateContext"
import AdminCandidateFilterControl from "../components/AdminCandidateFilterControl"
import BatchAgentDataModal from "../components/BatchAgentDataModal"
import {
  type AdminCandidateFilterValue,
  useAdminCandidateFilter,
} from "../hooks/useAdminCandidateFilter"

interface LedgerRow {
  batch_id: string
  task_key: string | null
  candidate_id: string | null
  started_at: string | null
  completed_at: string | null
  status: string | null
  total_processed: number
  total_passed: number
  total_failed: number
  total_errors: number
  total_cost: number
  [key: string]: unknown
}

interface LogEntry {
  id: string
  level: string
  logger_name: string
  message: string
  batch_id: string | null
  created_at: string
}

type SortDir = "asc" | "desc"
const FILTER_KEYS = ["task_key", "candidate_id", "status", "date_from", "date_to"] as const
const STATUSES = ["RUNNING", "COMPLETED", "FAILED", "INTERRUPTED"]
const LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"] as const

function candidateIdFromParams(sp: URLSearchParams): AdminCandidateFilterValue {
  return sp.get("candidate_id") || ""
}

function todayInTz(tz: string): string {
  // Returns "YYYY-MM-DD" in the given timezone
  return new Date().toLocaleDateString("en-CA", { timeZone: tz })
}

function durationMs(row: LedgerRow): number | null {
  if (!row.started_at || !row.completed_at) return null
  return new Date(row.completed_at).getTime() - new Date(row.started_at).getTime()
}

function formatDuration(ms: number | null): string {
  if (ms === null) return "—"
  if (ms < 1000) return `${ms}ms`
  const s = Math.round(ms / 1000)
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${s % 60}s`
}

/** Cost per processed item when total_processed > 0. */
function formatPerItemCost(row: LedgerRow): string {
  const n = row.total_processed
  if (typeof n !== "number" || n <= 0) return "—"
  const c = Number(row.total_cost) || 0
  return `$${(c / n).toFixed(4)}`
}

function statusClass(s: string | null): string {
  if (s === "COMPLETED") return "dispatch-status-ok"
  if (s === "FAILED") return "dispatch-status-fail"
  if (s === "RUNNING") return "dispatch-status-running"
  if (s === "INTERRUPTED") return "dispatch-status-interrupted"
  return ""
}

const COLUMNS = [
  { key: "started_at",      label: "Started",   width: 130 },
  { key: "task_key",        label: "Task",       width: 120 },
  { key: "candidate_id",    label: "Candidate",  width: 100 },
  { key: "status",          label: "Status",     width: 110 },
  { key: "total_processed", label: "Count",      width: 52,  align: "center" as const },
  { key: "total_passed",    label: "Pass",       width: 48,  align: "center" as const },
  { key: "total_failed",    label: "Fail",       width: 48,  align: "center" as const },
  { key: "total_errors",    label: "Errors",     width: 52,  align: "center" as const },
  { key: "_duration",       label: "Duration",   width: 80  },
]


export default function PerformanceMonitor() {
  const { selectedId } = useCandidate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [rows, setRows] = useState<LedgerRow[]>([])
  const [loading, setLoading] = useState(true)
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>("asc")
  const [expandedBatch, setExpandedBatch] = useState<string | null>(null)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [logsLoading, setLogsLoading] = useState(false)
  const [logCache, setLogCache] = useState<Record<string, LogEntry[]>>({})
  const [skipChecks, setSkipChecks] = useState(true)
  const [agentDataBatchId, setAgentDataBatchId] = useState<string | null>(null)
  const [agentDataCandidateId, setAgentDataCandidateId] = useState<string | null>(null)
  const userSetDateFrom = useRef(false)
  const userSetDateTo = useRef(false)
  const initialCandidateDefaultApplied = useRef(false)

  const setCandidateParam = useCallback((next: AdminCandidateFilterValue) => {
    setSearchParams(prev => {
      const nextParams = new URLSearchParams(prev)
      if (next) nextParams.set("candidate_id", next)
      else nextParams.delete("candidate_id")
      return nextParams
    }, { replace: true })
  }, [setSearchParams])

  const urlCandidate = candidateIdFromParams(searchParams)
  const urlBacked = useMemo(
    () => ({ value: urlCandidate, setValue: setCandidateParam }),
    [urlCandidate, setCandidateParam],
  )
  const { candidateFilter, setCandidateFilter, syncWithNav, candidates } = useAdminCandidateFilter({
    urlBacked,
    urlPresentDisablesSync: true,
  })

  const tz = useMemo(() => {
    const c = candidates.find(x => x.astral_candidate_id === selectedId)
    return (c?.candidate_data?.profile as Record<string, string> | undefined)?.timezone || "UTC"
  }, [candidates, selectedId])

  const filters = useMemo(() => {
    const f: Record<string, string> = {}
    for (const k of FILTER_KEYS) {
      const v = searchParams.get(k)
      if (v) f[k] = v
    }
    if (!searchParams.get("date_from") && !userSetDateFrom.current) {
      f.date_from = todayInTz(tz)
    }
    return f
  }, [searchParams, tz])

  const logLevelFilter = searchParams.get("log_level") || ""

  const [dateFromInput, setDateFromInput] = useState("")
  const [dateToInput, setDateToInput] = useState("")

  useEffect(() => {
    setDateFromInput(filters.date_from || "")
    setDateToInput(filters.date_to || "")
  }, [filters.date_from, filters.date_to])

  useEffect(() => {
    if (userSetDateFrom.current) return
    if (!searchParams.get("date_from")) {
      setSearchParams(prev => {
        const next = new URLSearchParams(prev)
        next.set("date_from", todayInTz(tz))
        return next
      }, { replace: true })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tz])

  useEffect(() => {
    if (initialCandidateDefaultApplied.current) return
    if (searchParams.get("candidate_id")) return
    if (!syncWithNav || !selectedId) return
    initialCandidateDefaultApplied.current = true
    setCandidateParam(selectedId)
  }, [searchParams, syncWithNav, selectedId, setCandidateParam])

  // Distinct values for dropdowns (derived from loaded data)
  const taskOptions = useMemo(() => {
    const s = new Set(rows.map(r => r.task_key).filter(Boolean) as string[])
    return Array.from(s).sort()
  }, [rows])

  function setFilter(key: string, value: string) {
    if (key === "date_from") userSetDateFrom.current = true
    if (key === "date_to") userSetDateTo.current = true
    setSearchParams(prev => {
      const next = new URLSearchParams(prev)
      if (value) next.set(key, value)
      else next.delete(key)
      return next
    })
  }

  function commitDateFrom() {
    setFilter("date_from", dateFromInput)
  }

  function commitDateTo() {
    setFilter("date_to", dateToInput)
  }

  const loadData = useCallback((showSpinner = false) => {
    if (showSpinner) setLoading(true)
    const qs = new URLSearchParams(filters).toString()
    api(`/api/admin/dispatch_ledger${qs ? `?${qs}` : ""}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false))
  }, [filters])

  useEffect(() => {
    loadData(true)                                    // spinner on first/filter load
    const id = setInterval(() => loadData(), 15_000)  // silent background refresh
    return () => clearInterval(id)
  }, [loadData])

  const filtered = useMemo(() => {
    if (!skipChecks) return rows
    return rows.filter(r => {
      const allZero =
        (r.total_processed ?? 0) === 0 &&
        (r.total_passed ?? 0) === 0 &&
        (r.total_failed ?? 0) === 0 &&
        (r.total_errors ?? 0) === 0
      if (!allZero) return true
      // Keep in-flight and failed attempts visible even when counts were not backfilled (AST-521).
      return r.status === "RUNNING" || r.status === "FAILED" || r.status === "INTERRUPTED"
    })
  }, [rows, skipChecks])

  const totalCost = useMemo(() => filtered.reduce((sum, r) => sum + (r.total_cost || 0), 0), [filtered])

  // Sort
  const sorted = useMemo(() => {
    if (!sortKey) return filtered
    return [...filtered].sort((a, b) => {
      if (sortKey === "_duration") {
        const av = durationMs(a) ?? -1
        const bv = durationMs(b) ?? -1
        return sortDir === "asc" ? av - bv : bv - av
      }
      const av = a[sortKey] ?? ""
      const bv = b[sortKey] ?? ""
      const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true })
      return sortDir === "asc" ? cmp : -cmp
    })
  }, [filtered, sortKey, sortDir])

  function handleSort(key: string) {
    if (sortKey === key) setSortDir(d => d === "asc" ? "desc" : "asc")
    else { setSortKey(key); setSortDir("asc") }
  }

  function toggleExpand(batchId: string) {
    if (expandedBatch === batchId) {
      setExpandedBatch(null)
      setLogs([])
      return
    }
    setExpandedBatch(batchId)
    // Use cached logs if available (completed batches won't change)
    if (logCache[batchId]) {
      setLogs(logCache[batchId])
      return
    }
    setLogsLoading(true)
    api(`/api/admin/dispatch_ledger/${batchId}/logs`)
      .then(r => r.json())
      .then(data => {
        const entries = Array.isArray(data) ? data : []
        setLogs(entries)
        setLogCache(prev => ({ ...prev, [batchId]: entries }))
      })
      .catch(() => setLogs([]))
      .finally(() => setLogsLoading(false))
  }

  function cellValue(row: LedgerRow, key: string): ReactNode {
    if (key === "_duration") return formatDuration(durationMs(row))
    if (key.endsWith("_at")) return <Time value={row[key] as string} />
    return String(row[key] ?? "")
  }

  return (
    <div className="list-page">
      <div className="list-page-header">
        <h1 className="list-page-title">Execution History</h1>
        {!loading && <span className="perf-total-cost">${totalCost.toFixed(4)} total</span>}
      </div>

      {/* Filters */}
      <div className="admin-filters">
        <label>
          Task
          <select value={filters.task_key || ""} onChange={e => setFilter("task_key", e.target.value)}>
            <option value="">All</option>
            {taskOptions.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <AdminCandidateFilterControl
          value={candidateFilter}
          onChange={setCandidateFilter}
          candidates={candidates}
        />
        <label>
          Status
          <select value={filters.status || ""} onChange={e => setFilter("status", e.target.value)}>
            <option value="">All</option>
            {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <label>
          Level
          <select value={logLevelFilter} onChange={e => setFilter("log_level", e.target.value)}>
            <option value="">All</option>
            {LOG_LEVELS.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </label>
        <label>
          From
          <input
            type="date"
            value={dateFromInput}
            onChange={e => setDateFromInput(e.target.value)}
            onBlur={commitDateFrom}
          />
        </label>
        <label>
          To
          <input
            type="date"
            value={dateToInput}
            onChange={e => setDateToInput(e.target.value)}
            onBlur={commitDateTo}
          />
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <input type="checkbox" checked={skipChecks} onChange={e => setSkipChecks(e.target.checked)} />
          Skip Checks
        </label>
      </div>

      {/* Table */}
      {loading ? (
        <p className="list-page-status">Loading...</p>
      ) : sorted.length === 0 ? (
        <p className="list-page-status">No execution records found.</p>
      ) : (
        <div className="list-page-table-wrap">
          <table className="list-page-table">
            <thead>
              <tr>
                <th style={{ width: 32 }} />
                {COLUMNS.map(col => (
                  <th key={col.key} className="sortable" style={{ width: col.width, textAlign: col.align }} onClick={() => handleSort(col.key)}>
                    {col.label}
                    {sortKey === col.key && (sortDir === "asc" ? " ▲" : " ▼")}
                  </th>
                ))}
                <th style={{ width: 72, textAlign: "right" }}>Per</th>
                <th style={{ width: 72, textAlign: "right" }}>Cost</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map(row => (
                <Fragment key={row.batch_id}>
                  <tr className="clickable" onClick={() => toggleExpand(row.batch_id)}>
                    <td style={{ textAlign: "center", fontSize: 12 }}>
                      {expandedBatch === row.batch_id ? "▼" : "▶"}
                    </td>
                    {COLUMNS.map(col => (
                      <td key={col.key} style={{ textAlign: col.align }}>
                        {col.key === "status" ? (
                          <span className={`dispatch-status-badge ${statusClass(row.status)}`}>
                            {row.status || "—"}
                          </span>
                        ) : cellValue(row, col.key)}
                      </td>
                    ))}
                    <td style={{ textAlign: "right" }} title="total_cost ÷ Count when Count > 0">
                      {formatPerItemCost(row)}
                    </td>
                    <td style={{ textAlign: "right" }} onClick={e => e.stopPropagation()}>
                      <a
                        className="dispatch-link"
                        href={`/admin/agent_timesheets?batch_id=${row.batch_id}`}
                        title="View timesheets for this batch"
                      >
                        ${((row.total_cost as number) || 0).toFixed(4)}
                      </a>
                    </td>
                  </tr>
                  {expandedBatch === row.batch_id && (
                    <tr>
                      <td colSpan={COLUMNS.length + 3} style={{ padding: 0 }}>
                        <div className="dispatch-expand-header">
                          <button
                            className="dispatch-batch-link"
                            onClick={() => {
                              setAgentDataBatchId(row.batch_id)
                              setAgentDataCandidateId(row.candidate_id || null)
                            }}
                            title="View agent data for this batch"
                          >
                            {row.batch_id}
                          </button>
                        </div>
                        <LogViewer logs={logs} loading={logsLoading} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <BatchAgentDataModal
        batchId={agentDataBatchId}
        candidateId={agentDataCandidateId || undefined}
        onClose={() => {
          setAgentDataBatchId(null)
          setAgentDataCandidateId(null)
        }}
      />
    </div>
  )
}


function LogViewer({ logs, loading }: { logs: LogEntry[]; loading: boolean }) {
  const [copied, setCopied] = useState(false)

  if (loading) return <div className="dispatch-log-panel"><p className="list-page-status">Loading logs...</p></div>
  if (logs.length === 0) return <div className="dispatch-log-panel"><p className="list-page-status">No log entries for this batch.</p></div>

  function copyLogs() {
    const text = logs.map(e => `[${e.created_at}] ${e.level} ${e.logger_name}: ${e.message}`).join("\n")
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="dispatch-log-panel">
      <div className="dispatch-log-toolbar">
        <button className="dispatch-log-copy-btn" onClick={copyLogs} title="Copy logs to clipboard">
          {copied ? "✓ Copied" : "⎘ Copy"}
        </button>
      </div>
      <table className="dispatch-log-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Level</th>
            <th>Logger</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(entry => (
            <tr key={entry.id} className={entry.level === "ERROR" ? "dispatch-log-error" : entry.level === "WARNING" ? "dispatch-log-warn" : ""}>
              <td className="dispatch-log-time"><Time value={entry.created_at} /></td>
              <td className={`dispatch-log-level dispatch-log-level-${entry.level.toLowerCase()}`}>{entry.level}</td>
              <td className="dispatch-log-logger">{entry.logger_name}</td>
              <td className="dispatch-log-msg">{entry.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
