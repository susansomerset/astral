import { useMemo, useState } from "react"
import Time from "./Time"

export interface LogEntry {
  id: number
  level: string
  logger_name: string
  message: string
  batch_id: string | null
  created_at: string
}

/** Shared Execution History log table (AST-1865); used by AdminPerformanceMonitor and BatchExecutionModal. */
export default function BatchLogViewer({
  logs,
  loading,
  logLevelFilter = "",
}: {
  logs: LogEntry[]
  loading: boolean
  logLevelFilter?: string
}) {
  const [copied, setCopied] = useState(false)

  const visibleLogs = useMemo(() => {
    const filtered = !logLevelFilter ? logs : logs.filter(entry => entry.level === logLevelFilter)
    return [...filtered].sort((a, b) => {
      const byTime = a.created_at.localeCompare(b.created_at)
      if (byTime !== 0) return byTime
      return a.id - b.id
    })
  }, [logs, logLevelFilter])

  if (loading) return <div className="dispatch-log-panel"><p className="list-page-status">Loading logs...</p></div>
  if (logs.length === 0) {
    return <div className="dispatch-log-panel"><p className="list-page-status">No log entries for this batch.</p></div>
  }
  if (visibleLogs.length === 0) {
    return (
      <div className="dispatch-log-panel">
        <p className="list-page-status">{`No '${logLevelFilter}' type log entries for this batch.`}</p>
      </div>
    )
  }

  function copyLogs() {
    const text = visibleLogs.map(e => `[${e.created_at}] ${e.level} ${e.logger_name}: ${e.message}`).join("\n")
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="dispatch-log-panel">
      <div className="dispatch-log-toolbar">
        <button className="btn secondary" onClick={copyLogs} title="Copy logs to clipboard">
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
          {visibleLogs.map(entry => (
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
