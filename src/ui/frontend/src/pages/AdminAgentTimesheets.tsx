import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { useCandidate } from "../contexts/CandidateContext"
import AdminCandidateFilterControl from "../components/AdminCandidateFilterControl"
import {
  type AdminCandidateFilterValue,
  useAdminCandidateFilter,
} from "../hooks/useAdminCandidateFilter"
import api from "../lib/api"
import { rowTotalCost } from "../lib/timesheetCost"
import ListPage, { type Column } from "../components/ListPage"

interface TimesheetRow {
  agent_req_id: string | null
  created_at: string
  candidate_id: string | null
  batch_id: string | null
  task_key_uuid: string | null
  model_code: string | null
  batch_size: number
  cache_write_tokens: number
  cache_read_tokens: number
  no_cache_prompt_tokens: number
  no_cache_live_tokens: number
  total_no_cache_input_tokens: number
  total_output_tokens: number
  calc_cost_cache_write: number
  calc_cost_cache_read: number
  calc_cost_no_cache_input: number
  calc_cost_output: number
  total_cost?: number
  agent_performance: string | null
  failure_note: string | null
  [key: string]: unknown
}

interface Totals {
  cache_write_tokens: number
  cache_read_tokens: number
  total_no_cache_input_tokens: number
  total_output_tokens: number
  total_cost: number
}

const ZERO: Totals = {
  cache_write_tokens: 0, cache_read_tokens: 0,
  total_no_cache_input_tokens: 0, total_output_tokens: 0, total_cost: 0,
}

const FILTER_KEYS = ["date_from", "date_to", "task_key_uuid", "batch_id", "candidate_id", "model_code", "agent_performance"] as const

function candidateIdFromParams(sp: URLSearchParams): AdminCandidateFilterValue {
  return sp.get("candidate_id") || ""
}

function defaultDateFrom(): string {
  const d = new Date()
  d.setDate(d.getDate() - 7)
  return d.toISOString().slice(0, 10)
}

function sum(rows: TimesheetRow[]): Totals {
  return rows.reduce((a, r) => ({
    cache_write_tokens: a.cache_write_tokens + (r.cache_write_tokens || 0),
    cache_read_tokens: a.cache_read_tokens + (r.cache_read_tokens || 0),
    total_no_cache_input_tokens: a.total_no_cache_input_tokens + (r.total_no_cache_input_tokens || 0),
    total_output_tokens: a.total_output_tokens + (r.total_output_tokens || 0),
    total_cost: a.total_cost + rowTotalCost(r),
  }), { ...ZERO })
}

const fmt = (n: number) => n.toLocaleString()
const fmtCost = (n: number) => `$${n.toFixed(4)}`

const COLUMNS: Column<TimesheetRow>[] = [
  { key: "created_at",                  label: "Date",            type: "datetime" },
  { key: "candidate_id",                label: "Candidate",       type: "str" },
  { key: "batch_id",                    label: "Batch",           type: "str" },
  { key: "model_code",                  label: "Model",           type: "str" },
  { key: "batch_size",                  label: "Batch Size",      type: "int" },
  { key: "cache_write_tokens",          label: "Cache Write",     type: "int" },
  { key: "cache_read_tokens",           label: "Cache Read",      type: "int" },
  { key: "no_cache_prompt_tokens",      label: "NoCache Prompt",  type: "int" },
  { key: "no_cache_live_tokens",        label: "NoCache Live",    type: "int" },
  { key: "total_no_cache_input_tokens", label: "Total Input",     type: "int" },
  { key: "total_output_tokens",         label: "Output",          type: "int" },
  { key: "calc_cost_cache_write",       label: "$ Cache Write",   type: "currency" },
  { key: "calc_cost_cache_read",        label: "$ Cache Read",    type: "currency" },
  { key: "calc_cost_no_cache_input",    label: "$ Input",         type: "currency" },
  { key: "calc_cost_output",            label: "$ Output",        type: "currency" },
  { key: "total_cost",                  label: "$ Total",         type: "currency" },
  { key: "agent_performance",           label: "Performance",     type: "str" },
  { key: "failure_note",                label: "Failure",         type: "str" },
  { key: "agent_req_id",                label: "Request ID",      type: "str" },
  { key: "task_key_uuid",               label: "Task UUID",       type: "str" },
]


export default function AgentTimesheets() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<TimesheetRow[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRows, setSelectedRows] = useState<TimesheetRow[]>([])
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

  const filters = useMemo(() => {
    const f: Record<string, string> = {}
    for (const k of FILTER_KEYS) {
      const v = searchParams.get(k)
      if (v) f[k] = v
    }
    if (!f.date_from && !f.date_to && !f.batch_id) {
      f.date_from = defaultDateFrom()
      f.date_to = new Date().toISOString().slice(0, 10)
    }
    return f
  }, [searchParams])

  function setFilter(key: string, value: string) {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev)
      if (value) next.set(key, value)
      else next.delete(key)
      return next
    })
  }

  useEffect(() => {
    if (initialCandidateDefaultApplied.current) return
    if (searchParams.get("candidate_id")) return
    if (!syncWithNav || !selectedId) return
    initialCandidateDefaultApplied.current = true
    setCandidateParam(selectedId)
  }, [searchParams, syncWithNav, selectedId, setCandidateParam])

  const loadData = useCallback(() => {
    setLoading(true)
    const qs = new URLSearchParams(filters).toString()
    api(`/api/admin/timesheets${qs ? `?${qs}` : ""}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false))
  }, [filters])

  useEffect(() => { loadData() }, [loadData])

  const allTotals = useMemo(() => sum(rows), [rows])
  const selTotals = useMemo(() => sum(selectedRows), [selectedRows])

  function handleExport() {
    const qs = new URLSearchParams(filters).toString()
    api(`/api/admin/timesheets/export${qs ? `?${qs}` : ""}`)
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = "timesheets.csv"
        a.click()
        URL.revokeObjectURL(url)
      })
      .catch(() => {})
  }

  return (
    <div className="list-page">
      <div className="admin-filters">
        <label>
          From
          <input type="date" defaultValue={filters.date_from || ""} onBlur={e => setFilter("date_from", e.target.value)} />
        </label>
        <label>
          To
          <input type="date" defaultValue={filters.date_to || ""} onBlur={e => setFilter("date_to", e.target.value)} />
        </label>
        <label>
          Batch ID
          <input type="text" placeholder="batch_id" value={filters.batch_id || ""}
            onChange={e => setFilter("batch_id", e.target.value)} />
        </label>
        <AdminCandidateFilterControl
          value={candidateFilter}
          onChange={setCandidateFilter}
          candidates={candidates}
        />
      </div>

      {selectedRows.length > 0 && (
        <TotalsBar label={`Selected (${fmt(selectedRows.length)} rows)`} totals={selTotals} variant="selected" />
      )}
      <TotalsBar label={`All (${fmt(rows.length)} rows)`} totals={allTotals} />

      <ListPage<TimesheetRow>
        title="Agent Timesheets"
        columns={COLUMNS}
        rows={rows}
        loading={loading}
        emptyMessage="No timesheet entries found."
        selectable
        onSelectionChange={setSelectedRows}
        idField="agent_req_id"
        actions={<button className="timesheet-export-btn" onClick={handleExport}>Export CSV</button>}
      />
    </div>
  )
}


function TotalsBar({ label, totals, variant }: { label: string; totals: Totals; variant?: string }) {
  return (
    <div className={`timesheet-totals-bar${variant ? ` timesheet-totals-${variant}` : ""}`}>
      <span className="timesheet-totals-label">{label}</span>
      <span>Cache Write: <strong>{fmt(totals.cache_write_tokens)}</strong></span>
      <span>Cache Read: <strong>{fmt(totals.cache_read_tokens)}</strong></span>
      <span>Input: <strong>{fmt(totals.total_no_cache_input_tokens)}</strong></span>
      <span>Output: <strong>{fmt(totals.total_output_tokens)}</strong></span>
      <span>Cost: <strong>{fmtCost(totals.total_cost)}</strong></span>
    </div>
  )
}
