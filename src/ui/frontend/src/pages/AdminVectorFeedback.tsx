import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { useCandidate } from "../contexts/CandidateContext"
import AdminCandidateFilterControl from "../components/AdminCandidateFilterControl"
import BatchAgentDataModal from "../components/BatchAgentDataModal"
import {
  type AdminCandidateFilterValue,
  useAdminCandidateFilter,
} from "../hooks/useAdminCandidateFilter"
import api from "../lib/api"
import ListPage, { type Column } from "../components/ListPage"

const FILTER_KEYS = [
  "candidate_id", "owner_task_key", "batch_id", "vector_code",
  "feedback_type", "value", "date_from", "date_to",
] as const

const FEEDBACK_TYPE_LABELS: Record<string, string> = {
  relevance: "Relevance",
  clarity: "Clarity",
  verdict: "Verdict",
}

const FEEDBACK_VALUES: Record<string, string[]> = {
  relevance: ["A", "O", "S", "R", "N"],
  clarity: ["A", "O", "S", "R", "N"],
  verdict: ["K", "E", "D"],
}

interface FeedbackRow {
  vector_feedback_id: string
  candidate_id: string | null
  batch_id: string | null
  batch_size: number | null
  completed_at: string | null
  task_key: string | null
  feedback_type: string | null
  value: string | null
  value_label?: string | null
  agent_data_id: string | null
  created_at: string | null
  vector_code: string | null
  vector_label: string | null
  vector_content?: string | null
  vector_importance?: number | null
  vector_assessment_header?: string | null
  [key: string]: unknown
}

interface SummaryRow {
  code: string
  label: string
  importance: number
  batch_count: number
  feedback_row_count: number
  relevance_dist: string
  clarity_dist: string
  verdict_dist: string
  [key: string]: unknown
}

function candidateIdFromParams(sp: URLSearchParams): AdminCandidateFilterValue {
  return sp.get("candidate_id") || ""
}

function defaultDateFrom(): string {
  const d = new Date()
  d.setDate(d.getDate() - 7)
  return d.toISOString().slice(0, 10)
}

const SUMMARY_COLUMNS: Column<SummaryRow>[] = [
  { key: "code", label: "Vector", type: "str" },
  { key: "label", label: "Label", type: "str" },
  { key: "importance", label: "Importance", type: "int" },
  { key: "batch_count", label: "Batches", type: "int" },
  { key: "feedback_row_count", label: "Feedback rows", type: "int" },
  { key: "relevance_dist", label: "Relevance", type: "str" },
  { key: "clarity_dist", label: "Clarity", type: "str" },
  { key: "verdict_dist", label: "Verdict", type: "str" },
]

export default function AdminVectorFeedback() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { selectedId } = useCandidate()
  const [rows, setRows] = useState<FeedbackRow[]>([])
  const [summaryRows, setSummaryRows] = useState<SummaryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [taskKeys, setTaskKeys] = useState<string[]>([])
  const [agentDataBatchId, setAgentDataBatchId] = useState<string | null>(null)
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

  useEffect(() => {
    api("/api/admin/vector_feedback/task_keys")
      .then(r => r.json())
      .then(data => setTaskKeys(Array.isArray(data) ? data : []))
      .catch(() => setTaskKeys([]))
  }, [])

  const loadDetail = useCallback(() => {
    setLoading(true)
    const qs = new URLSearchParams(filters).toString()
    api(`/api/admin/vector_feedback${qs ? `?${qs}` : ""}`)
      .then(r => r.json())
      .then(data => setRows(Array.isArray(data) ? data : []))
      .catch(() => setRows([]))
      .finally(() => setLoading(false))
  }, [filters])

  const loadSummary = useCallback(() => {
    const candidate_id = filters.candidate_id
    const owner_task_key = filters.owner_task_key
    if (!candidate_id || !owner_task_key) {
      setSummaryRows([])
      return
    }
    setSummaryLoading(true)
    const qs = new URLSearchParams({ candidate_id, owner_task_key }).toString()
    api(`/api/admin/vector_feedback/summary?${qs}`)
      .then(r => r.json())
      .then(data => setSummaryRows(Array.isArray(data) ? data : []))
      .catch(() => setSummaryRows([]))
      .finally(() => setSummaryLoading(false))
  }, [filters.candidate_id, filters.owner_task_key])

  useEffect(() => { loadDetail() }, [loadDetail])
  useEffect(() => { loadSummary() }, [loadSummary])

  const detailColumns: Column<FeedbackRow>[] = useMemo(() => [
    { key: "created_at", label: "Date", type: "datetime" },
    { key: "candidate_id", label: "Candidate", type: "str" },
    { key: "task_key", label: "Task", type: "str" },
    {
      key: "batch_id",
      label: "Batch",
      type: "str",
      render: (value, row) => {
        const id = String(value ?? row.batch_id ?? "")
        if (!id) return "—"
        return (
          <button
            type="button"
            className="dispatch-batch-link"
            onClick={e => { e.stopPropagation(); setAgentDataBatchId(id) }}
            title="View agent data for this batch"
          >
            {id}
          </button>
        )
      },
    },
    { key: "batch_size", label: "Batch size", type: "int" },
    { key: "completed_at", label: "Completed", type: "datetime" },
    { key: "vector_code", label: "Code", type: "str" },
    { key: "vector_assessment_header", label: "Assessment", type: "str" },
    { key: "vector_content", label: "Criterion", type: "str", expandable: true },
    { key: "feedback_type", label: "Type", type: "str" },
    { key: "value", label: "Value", type: "str" },
    { key: "value_label", label: "Value label", type: "str" },
    { key: "agent_data_id", label: "Agent data", type: "str" },
    { key: "vector_feedback_id", label: "Feedback ID", type: "str" },
  ], [])

  const summaryEmpty = !filters.candidate_id || !filters.owner_task_key
    ? "Select candidate and rubric task to see per-vector aggregation."
    : "No active rubric vectors or no feedback yet."

  const valueOptions = filters.feedback_type
    ? FEEDBACK_VALUES[filters.feedback_type] ?? []
    : ["A", "O", "S", "R", "N", "K", "E", "D"]

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
          Rubric task
          <select value={filters.owner_task_key || ""} onChange={e => setFilter("owner_task_key", e.target.value)}>
            <option value="">All</option>
            {taskKeys.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label>
          Batch ID
          <input type="text" placeholder="batch_id" value={filters.batch_id || ""}
            onChange={e => setFilter("batch_id", e.target.value)} />
        </label>
        <label>
          Vector code
          <input type="text" placeholder="code" value={filters.vector_code || ""}
            onChange={e => setFilter("vector_code", e.target.value)} />
        </label>
        <label>
          Feedback type
          <select value={filters.feedback_type || ""} onChange={e => setFilter("feedback_type", e.target.value)}>
            <option value="">All</option>
            {Object.entries(FEEDBACK_TYPE_LABELS).map(([k, lab]) => (
              <option key={k} value={k}>{lab}</option>
            ))}
          </select>
        </label>
        <label>
          Value
          <select value={filters.value || ""} onChange={e => setFilter("value", e.target.value)}>
            <option value="">All</option>
            {valueOptions.map(v => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </label>
        <AdminCandidateFilterControl
          value={candidateFilter}
          onChange={setCandidateFilter}
          candidates={candidates}
        />
      </div>

      <ListPage<SummaryRow>
        title="Per-vector summary (active rubric)"
        columns={SUMMARY_COLUMNS}
        rows={summaryRows}
        loading={summaryLoading}
        emptyMessage={summaryEmpty}
      />

      <ListPage<FeedbackRow>
        title="Vector feedback rows"
        columns={detailColumns}
        rows={rows}
        loading={loading}
        emptyMessage="No vector feedback rows match filters."
        idField="vector_feedback_id"
      />

      <BatchAgentDataModal
        batchId={agentDataBatchId}
        candidateId={filters.candidate_id || undefined}
        onClose={() => setAgentDataBatchId(null)}
      />
    </div>
  )
}
