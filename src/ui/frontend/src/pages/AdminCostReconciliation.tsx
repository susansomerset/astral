import React, { useCallback, useEffect, useMemo, useState } from "react"
import api from "../lib/api"

/* ---- Types ---- */

interface ReconciliationConfig {
  astral_export_markers: string[]
  export_filename_prefix: string
}

interface CsvRow {
  usage_date_utc: string
  model: string
  workspace: string
  api_key: string
  usage_type: string
  context_window: string
  token_type: string
  cost_usd: number
  cost_type: string
  inference_geo: string
  speed: string
}

interface TimesheetRow {
  created_at: string
  user_prompt_file: string | null
  est_cost: number
  tokens_input: number
  cache_read_tokens: number
  cache_creation_tokens: number
  tokens_output: number
  [key: string]: unknown
}

interface DateAgg {
  calls: number
  est_cost: number
  input_tokens: number
  cache_read_tokens: number
  cache_creation_tokens: number
  output_tokens: number
  byTask: Record<string, { calls: number; est_cost: number }>
}

// Map Anthropic CSV token_type to our aggregated field
function ourTokens(da: DateAgg | undefined, tokenType: string): number | null {
  if (!da) return null
  if (tokenType === "input_no_cache") return da.input_tokens
  if (tokenType === "input_cache_read") return da.cache_read_tokens
  if (tokenType === "output") return da.output_tokens
  if (tokenType === "input_cache_write_5m") return da.cache_creation_tokens
  return null
}

/* ---- CSV parsing ---- */

const CSV_COLS = [
  "usage_date_utc", "model", "workspace", "api_key", "usage_type",
  "context_window", "token_type", "cost_usd", "cost_type", "inference_geo", "speed",
] as const

function parseCsv(text: string): CsvRow[] {
  const lines = text.trim().split("\n")
  if (lines.length < 2) return []
  // Skip header row
  return lines.slice(1).filter(l => l.trim()).map(line => {
    const cols = line.split(",")
    const row: Record<string, string | number> = {}
    CSV_COLS.forEach((key, i) => {
      row[key] = key === "cost_usd" ? parseFloat(cols[i] || "0") : (cols[i] || "")
    })
    return row as unknown as CsvRow
  })
}

/* ---- Formatting ---- */

const fmt = (n: number) => n.toLocaleString()
const fmtCost = (n: number) => `$${n.toFixed(4)}`

/* ---- Component ---- */

export default function CostReconciliation() {
  const [csvRows, setCsvRows] = useState<CsvRow[] | null>(null)
  const [timesheets, setTimesheets] = useState<TimesheetRow[]>([])
  const [loading, setLoading] = useState(false)
  const [fileName, setFileName] = useState("")
  const [fileError, setFileError] = useState<string | null>(null)
  const [reconcConfig, setReconcConfig] = useState<ReconciliationConfig | null>(null)

  useEffect(() => {
    api("/api/admin/config")
      .then(r => r.json())
      .then(data => setReconcConfig(data?.reconciliation ?? null))
      .catch(() => {/* non-fatal — validation and prefix degrade gracefully */})
  }, [])

  const handleFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setFileName(file.name)
    setFileError(null)
    const reader = new FileReader()
    reader.onload = async (ev) => {
      const text = ev.target?.result as string
      const markers = reconcConfig?.astral_export_markers ?? []
      const hasAstralFooter = text.split("\n").some(line =>
        markers.some(m => line.trimStart().startsWith(m))
      )
      if (hasAstralFooter) {
        setFileError("This looks like an Astral export, not a Claude billing CSV. Please upload the original Claude usage export.")
        setCsvRows(null)
        setTimesheets([])
        return
      }
      const rows = parseCsv(text)
      setCsvRows(rows)
      if (rows.length === 0) return

      // Extract date range from CSV
      const dates = rows.map(r => r.usage_date_utc).filter(Boolean).sort()
      const dateFrom = dates[0]
      const dateTo = dates[dates.length - 1]

      // Fetch our timesheets for matching range
      setLoading(true)
      try {
        const qs = new URLSearchParams({ date_from: dateFrom, date_to: dateTo }).toString()
        const resp = await api(`/api/admin/timesheets?${qs}`)
        const data = await resp.json()
        setTimesheets(Array.isArray(data) ? data : [])
      } catch {
        setTimesheets([])
      } finally {
        setLoading(false)
      }
    }
    reader.readAsText(file)
  }, [reconcConfig])

  // Group our timesheets by date, with per-task breakdown
  const dateAgg = useMemo(() => {
    const agg: Record<string, DateAgg> = {}
    for (const ts of timesheets) {
      const date = (ts.created_at || "").slice(0, 10)
      if (!date) continue
      if (!agg[date]) agg[date] = { calls: 0, est_cost: 0, input_tokens: 0, cache_read_tokens: 0, cache_creation_tokens: 0, output_tokens: 0, byTask: {} }
      agg[date].calls += 1
      agg[date].est_cost += ts.est_cost || 0
      const cacheRead = ts.cache_read_tokens || 0
      agg[date].input_tokens += ts.tokens_input || 0
      agg[date].cache_read_tokens += cacheRead
      agg[date].cache_creation_tokens += ts.cache_creation_tokens || 0
      agg[date].output_tokens += ts.tokens_output || 0
      const task = ts.user_prompt_file || "(unknown)"
      if (!agg[date].byTask[task]) agg[date].byTask[task] = { calls: 0, est_cost: 0 }
      agg[date].byTask[task].calls += 1
      agg[date].byTask[task].est_cost += ts.est_cost || 0
    }
    return agg
  }, [timesheets])

  // Discover all task keys across all dates for crosstab columns
  const taskKeys = useMemo(() => {
    const keys = new Set<string>()
    for (const d of Object.values(dateAgg)) {
      for (const k of Object.keys(d.byTask)) keys.add(k)
    }
    return Array.from(keys).sort()
  }, [dateAgg])

  // Totals
  const totals = useMemo(() => {
    if (!csvRows) return null
    const actualTotal = csvRows.reduce((s, r) => s + r.cost_usd, 0)
    const estTotal = Object.values(dateAgg).reduce((s, d) => s + d.est_cost, 0)
    return { actual: actualTotal, estimated: estTotal, variance: actualTotal - estTotal }
  }, [csvRows, dateAgg])

  // Export composite CSV
  function handleExport() {
    if (!csvRows) return
    const taskCols = taskKeys.flatMap(t => [`${t}_calls`, `${t}_est_cost`])
    const header = [
      ...CSV_COLS, "our_tokens", "our_calls", "our_est_cost", ...taskCols,
    ].join(",")

    const lines = csvRows.map(row => {
      const date = row.usage_date_utc
      const da = dateAgg[date]
      const base = CSV_COLS.map(k => String(row[k])).join(",")
      const tokens = ourTokens(da, row.token_type)
      const ourTok = tokens !== null ? tokens : ""
      const ourCalls = da ? da.calls : 0
      const ourCost = da ? da.est_cost.toFixed(4) : "0.0000"
      const taskVals = taskKeys.flatMap(t => {
        const td = da?.byTask[t]
        return [td ? td.calls : 0, td ? td.est_cost.toFixed(4) : "0.0000"]
      })
      return `${base},${ourTok},${ourCalls},${ourCost},${taskVals.join(",")}`
    })

    // Summary rows — pad to match full column count
    const pad = ",".repeat(taskKeys.length * 2)
    const totalCalls = Object.values(dateAgg).reduce((s, d) => s + d.calls, 0)
    const emptyBase = CSV_COLS.map((_, i) => i === 0 ? "TOTALS" : "").join(",")
    const taskTotals = taskKeys.flatMap(t => {
      const c = Object.values(dateAgg).reduce((s, d) => s + (d.byTask[t]?.calls || 0), 0)
      const e = Object.values(dateAgg).reduce((s, d) => s + (d.byTask[t]?.est_cost || 0), 0)
      return [c, e.toFixed(4)]
    })
    lines.push(`${emptyBase},,${totalCalls},${totals!.estimated.toFixed(4)},${taskTotals.join(",")}`)
    lines.push(`${CSV_COLS.map((_, i) => i === 0 ? "ACTUAL_TOTAL" : i === 7 ? totals!.actual.toFixed(4) : "").join(",")},,,${pad}`)
    lines.push(`${CSV_COLS.map((_, i) => i === 0 ? "VARIANCE" : i === 7 ? totals!.variance.toFixed(4) : "").join(",")},,,${pad}`)

    const blob = new Blob([header + "\n" + lines.join("\n") + "\n"], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    const prefix = reconcConfig?.export_filename_prefix ?? "astral"
    a.download = `${prefix}_${fileName.replace(/\.csv$/, "")}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="list-page">
      <div className="list-page-header">
        <h1 className="list-page-title">Cost Reconciliation</h1>
        {csvRows && csvRows.length > 0 && (
          <button className="timesheet-export-btn" onClick={handleExport}>Export CSV</button>
        )}
      </div>

      {/* Upload */}
      <div className="admin-filters" style={{ marginBottom: 16 }}>
        <label>
          Anthropic Billing CSV
          <input type="file" accept=".csv" onChange={handleFile} style={{ marginLeft: 8 }} />
        </label>
      </div>

      {fileError && <div className="list-page-status" style={{ color: "var(--error)" }}>{fileError}</div>}
      {loading && <div className="list-page-status">Loading timesheets...</div>}

      {/* Totals bar */}
      {totals && (
        <div className="timesheet-totals-bar">
          <span className="timesheet-totals-label">
            {csvRows!.length} CSV rows &middot; {fmt(timesheets.length)} timesheet entries
          </span>
          <span>Anthropic Actual: <strong>{fmtCost(totals.actual)}</strong></span>
          <span>Our Estimated: <strong>{fmtCost(totals.estimated)}</strong></span>
          <span>
            Variance:{" "}
            <strong style={{ color: totals.variance > 0 ? "#ff6b6b" : "#4caf50" }}>
              {totals.variance >= 0 ? "+" : ""}{fmtCost(totals.variance)}
            </strong>
          </span>
        </div>
      )}

      {/* Table — horizontally scrollable for wide crosstab */}
      {csvRows && csvRows.length > 0 && !loading && (
        <div className="list-page-table-wrap list-page-table-wrap--scroll">
          <table className="list-page-table list-page-table--auto">
            <thead>
              <tr>
                <th>Date</th>
                <th>Model</th>
                <th>API Key</th>
                <th>Token Type</th>
                <th style={{ textAlign: "right" }}>Actual Cost</th>
                <th style={{ textAlign: "right" }}>Our Tokens</th>
                <th style={{ textAlign: "right" }}>Our Calls</th>
                <th style={{ textAlign: "right" }}>Our Est. Cost</th>
                {taskKeys.map(t => (
                  <th key={t} colSpan={2} style={{ textAlign: "center" }}>{t}</th>
                ))}
              </tr>
              {taskKeys.length > 0 && (
                <tr>
                  <th colSpan={8}></th>
                  {taskKeys.map(t => (
                    <React.Fragment key={t}>
                      <th style={{ textAlign: "right", fontSize: 11 }}>Calls</th>
                      <th style={{ textAlign: "right", fontSize: 11 }}>Est $</th>
                    </React.Fragment>
                  ))}
                </tr>
              )}
            </thead>
            <tbody>
              {csvRows.map((row, i) => {
                const da = dateAgg[row.usage_date_utc]
                return (
                  <tr key={i}>
                    <td>{row.usage_date_utc}</td>
                    <td>{row.model}</td>
                    <td>{row.api_key}</td>
                    <td>{row.token_type}</td>
                    <td style={{ textAlign: "right" }}>{fmtCost(row.cost_usd)}</td>
                    <td style={{ textAlign: "right" }}>{(() => { const t = ourTokens(da, row.token_type); return t !== null ? fmt(t) : "—" })()}</td>
                    <td style={{ textAlign: "right" }}>{da ? fmt(da.calls) : "—"}</td>
                    <td style={{ textAlign: "right" }}>{da ? fmtCost(da.est_cost) : "—"}</td>
                    {taskKeys.map(t => {
                      const td = da?.byTask[t]
                      return (
                        <React.Fragment key={t}>
                          <td style={{ textAlign: "right" }}>{td ? fmt(td.calls) : "—"}</td>
                          <td style={{ textAlign: "right" }}>{td ? fmtCost(td.est_cost) : "—"}</td>
                        </React.Fragment>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
