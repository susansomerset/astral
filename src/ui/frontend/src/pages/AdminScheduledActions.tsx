import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import AdminCandidateFilterControl from "../components/AdminCandidateFilterControl"
import { useAdminCandidateFilter } from "../hooks/useAdminCandidateFilter"
import api from "../lib/api"
import Time from "../components/Time"
import CollapsiblePanel from "../components/CollapsiblePanel"
import ListTableTruncatedCell from "../components/ListTableTruncatedCell"
import { getUiConfig, loadUiConfig } from "../lib/uiConfig"
import { resolveCellTruncateChars, resolveFrozenDataColumns, stickyLeftPx } from "../lib/listTableLayout"
import { useListTableColumnMeasure } from "../lib/useListTableColumnMeasure"
import Toast, { type ToastMessage } from "../components/Toast"
import { ApiError, errorToastFromApiError, readApiError } from "../lib/toastDiagnostics"

type TaskKeyMeta = {
  entity_type: string
  trigger_state: string
  task_group_order: string
  task_group_name: string
  task_seq: number | null
  task_name: string
  is_scored?: boolean
}

type DispatchFormState = {
  candidate_id: string
  task_key: string
  trigger_state: string
  freq_hrs: string
  min_count: string
  batch_size: string
  max_runs: string
  score_floor: string
  auto_mode: boolean
  debug: boolean
  entity_type: string
  is_scored: boolean
}

function taskKeyChangePatch(form: DispatchFormState, key: string, cfg: TaskKeyMeta | undefined): DispatchFormState {
  return {
    ...form,
    task_key: key,
    entity_type: cfg?.entity_type || "",
    is_scored: !!cfg?.is_scored,
  }
}

interface DispatchTask {
  id: number
  candidate_id: string
  task_key: string
  entity_type: string | null
  trigger_state?: string | null
  freq_hrs: number
  min_count: number
  batch_size: number | null
  score_floor: number | null
  is_scored?: boolean
  auto_mode: number
  debug: number
  skip_cache: number
  max_runs: number | null
  last_run_at: string | null
  updated_at: string | null
  available_count: number
}

interface ThreadEntry {
  running: boolean
  draining: boolean
  task_key: string
  candidate_id: string
  is_auto: boolean
}

type SortDir = "asc" | "desc"

const FROZEN_DATA_COLUMNS = 3

const DATA_COL_KEYS = [
  "task_key", "entity_type", "trigger_state", "score_floor",
  "auto_mode", "run", "debug", "freq_hrs", "min_count",
  "batch_size", "max_runs", "candidate_id", "available_count", "last_run_at",
] as const

const DATA_COL_KEYS_ARR = [...DATA_COL_KEYS]
const NO_PERSISTED_WIDTHS: Record<string, number> = {}

function formatAvailableCount(count: number | null): string {
  if (count == null || count === 0) return "—"
  return count.toLocaleString()
}

interface ScheduledPhaseTableProps {
  rows: DispatchTask[]
  frozenN: number
  truncateChars: number
  threadStatus: Record<number, ThreadEntry>
  allTaskKeys: Record<string, TaskKeyMeta>
  toggleSort: (col: string) => void
  sortIcon: (col: string) => string
  openEdit: (row: DispatchTask) => void
  toggleAutoMode: (row: DispatchTask) => void
  toggleDebug: (row: DispatchTask) => void
  handleRun: (e: React.MouseEvent, row: DispatchTask) => void
  handleStop: (e: React.MouseEvent, row: DispatchTask) => void
}

function ScheduledPhaseTable({
  rows,
  frozenN,
  truncateChars,
  threadStatus,
  allTaskKeys,
  toggleSort,
  sortIcon,
  openEdit,
  toggleAutoMode,
  toggleDebug,
  handleRun,
  handleStop,
}: ScheduledPhaseTableProps) {
  const tableRef = useRef<HTMLTableElement>(null)
  const { mergedWidths } = useListTableColumnMeasure(
    tableRef,
    DATA_COL_KEYS_ARR,
    false,
    NO_PERSISTED_WIDTHS,
    [rows.length, frozenN, sortIcon("candidate_id"), sortIcon("task_key"), sortIcon("entity_type")],
  )

  function scheduledFrozenStyle(colIndex: number, base: CSSProperties = {}): CSSProperties {
    const left = stickyLeftPx(colIndex, mergedWidths, DATA_COL_KEYS_ARR, false, frozenN)
    if (left == null) return base
    const predecessorsReady = DATA_COL_KEYS_ARR.slice(0, colIndex).every(
      (k) => (mergedWidths[k] ?? 0) > 0,
    )
    if (!predecessorsReady) return base
    return { ...base, left }
  }

  return (
    <div className="list-page-table-wrap list-page-table-wrap--scroll">
      <table ref={tableRef} className="list-page-table">
        <thead>
          <tr>
            <th className={`sortable${0 < frozenN ? " list-table-cell-frozen" : ""}`.trim()} style={scheduledFrozenStyle(0)} onClick={() => toggleSort("task_key")}>Task{sortIcon("task_key")}</th>
            <th className={`sortable${1 < frozenN ? " list-table-cell-frozen" : ""}`.trim()} style={scheduledFrozenStyle(1)} onClick={() => toggleSort("entity_type")}>Entity{sortIcon("entity_type")}</th>
            <th className={`sortable${2 < frozenN ? " list-table-cell-frozen" : ""}`.trim()} style={scheduledFrozenStyle(2)} onClick={() => toggleSort("trigger_state")}>State{sortIcon("trigger_state")}</th>
            <th className="sortable" style={{ textAlign: "right" }} onClick={() => toggleSort("score_floor")}>Floor{sortIcon("score_floor")}</th>
            <th className="sortable" style={{ textAlign: "center" }} onClick={() => toggleSort("auto_mode")}>AUTO{sortIcon("auto_mode")}</th>
            <th style={{ textAlign: "center" }}>Run</th>
            <th className="sortable" style={{ textAlign: "center" }} onClick={() => toggleSort("debug")}>Dbg{sortIcon("debug")}</th>
            <th className="sortable" style={{ textAlign: "right" }} onClick={() => toggleSort("freq_hrs")}>Freq{sortIcon("freq_hrs")}</th>
            <th className="sortable" style={{ textAlign: "right" }} onClick={() => toggleSort("min_count")}>Min{sortIcon("min_count")}</th>
            <th className="sortable" style={{ textAlign: "right" }} onClick={() => toggleSort("batch_size")}>Batch{sortIcon("batch_size")}</th>
            <th className="sortable" style={{ textAlign: "right" }} onClick={() => toggleSort("max_runs")}>Runs{sortIcon("max_runs")}</th>
            <th className="sortable" onClick={() => toggleSort("candidate_id")}>Candidate{sortIcon("candidate_id")}</th>
            <th className="sortable" style={{ textAlign: "right" }} onClick={() => toggleSort("available_count")}>Avail{sortIcon("available_count")}</th>
            <th className="sortable" onClick={() => toggleSort("last_run_at")}>Last Run{sortIcon("last_run_at")}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => {
            const thread = threadStatus[row.id]
            const isRunning = thread?.running ?? false
            const isDraining = thread?.draining ?? false
            return (
              <tr
                key={row.id}
                onClick={row.auto_mode ? undefined : () => openEdit(row)}
                style={{ cursor: row.auto_mode ? "default" : "pointer" }}
              >
                <td className={0 < frozenN ? "list-table-cell-frozen" : undefined} style={scheduledFrozenStyle(0)}>
                  <ListTableTruncatedCell text={row.task_key} maxChars={truncateChars} />
                </td>
                <td className={1 < frozenN ? "list-table-cell-frozen" : undefined} style={scheduledFrozenStyle(1)}>
                  <ListTableTruncatedCell text={allTaskKeys[row.task_key]?.entity_type || row.entity_type || "—"} maxChars={truncateChars} />
                </td>
                <td className={2 < frozenN ? "list-table-cell-frozen" : undefined} style={scheduledFrozenStyle(2)}>
                  <ListTableTruncatedCell text={row.trigger_state || allTaskKeys[row.task_key]?.trigger_state || "—"} maxChars={truncateChars} />
                </td>
                <td style={{ textAlign: "right" }}>
                  {(row.is_scored ?? !!allTaskKeys[row.task_key]?.is_scored)
                    ? <ListTableTruncatedCell text={(row.score_floor ?? 1).toFixed(2)} maxChars={truncateChars} />
                    : null}
                </td>
                <td style={{ textAlign: "center" }}>
                  <button
                    className={`dispatch-status-badge ${row.auto_mode ? "dispatch-status-ok" : "dispatch-status-muted"}`}
                    onClick={e => { e.stopPropagation(); toggleAutoMode(row) }}
                    style={{ cursor: "pointer", border: "none" }}
                  >
                    {row.auto_mode ? "ON" : "OFF"}
                  </button>
                </td>
                <td style={{ textAlign: "center" }}>
                  <div style={{ position: "relative", display: "inline-block" }}>
                    <button
                      className="list-page-bulk-btn"
                      style={{ padding: "2px 10px", fontSize: "0.78rem", whiteSpace: "nowrap", opacity: isRunning ? 0 : (row.auto_mode ? 0.25 : 1), pointerEvents: (isRunning || row.auto_mode) ? "none" : "auto" }}
                      disabled={isRunning || !!row.auto_mode}
                      onClick={e => handleRun(e, row)}
                    >
                      Run
                    </button>
                    {isRunning && (
                      <button
                        className="list-page-bulk-btn"
                        style={{ position: "absolute", inset: 0, padding: "2px 10px", fontSize: "0.78rem", whiteSpace: "nowrap", background: isDraining ? "#7d6608" : "#c0392b", color: "#fff" }}
                        onClick={e => handleStop(e, row)}
                        disabled={isDraining}
                      >
                        {isDraining ? "Draining…" : "Stop"}
                      </button>
                    )}
                  </div>
                </td>
                <td style={{ textAlign: "center" }}>
                  <button
                    className={`dispatch-status-badge ${row.debug ? "dispatch-status-warn" : "dispatch-status-muted"}`}
                    onClick={e => { e.stopPropagation(); toggleDebug(row) }}
                    style={{ cursor: "pointer", border: "none" }}
                  >
                    {row.debug ? "ON" : "OFF"}
                  </button>
                </td>
                <td style={{ textAlign: "right" }}>
                  <ListTableTruncatedCell text={row.freq_hrs ? String(row.freq_hrs) : "—"} maxChars={truncateChars} />
                </td>
                <td style={{ textAlign: "right" }}>
                  <ListTableTruncatedCell text={String(row.min_count)} maxChars={truncateChars} />
                </td>
                <td style={{ textAlign: "right" }}>
                  <ListTableTruncatedCell text={row.batch_size != null ? String(row.batch_size) : "—"} maxChars={truncateChars} />
                </td>
                <td style={{ textAlign: "right" }}>
                  <span title={row.max_runs === 0 ? "Loop until drained" : undefined}>
                    {row.max_runs === 0 ? "∞" : (row.max_runs ?? 1)}
                  </span>
                </td>
                <td>
                  <ListTableTruncatedCell text={row.candidate_id} maxChars={truncateChars} />
                </td>
                <td style={{ textAlign: "right" }}>
                  <ListTableTruncatedCell text={formatAvailableCount(row.available_count)} maxChars={truncateChars} />
                </td>
                <td><Time value={row.last_run_at} /></td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default function ScheduledActions() {
  const { selectedId } = useCandidate()
  const { candidateFilter, setCandidateFilter, candidates } = useAdminCandidateFilter()
  const [data, setData] = useState<DispatchTask[]>([])
  const [loading, setLoading] = useState(true)
  const [sortCol, setSortCol] = useState<string>("_default")
  const [sortDir, setSortDir] = useState<SortDir>("asc")

  const [allTaskKeys, setAllTaskKeys] = useState<Record<string, TaskKeyMeta>>({})
  const [stateOptions, setStateOptions] = useState<{ job: string[]; company: string[]; candidate: string[] }>({ job: [], company: [], candidate: [] })
  const [openSection, setOpenSection] = useState<string | null>(null)
  const didAutoOpenSectionRef = useRef(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  // Modal state (add/edit)
  const [showModal, setShowModal] = useState(false)
  const [editRow, setEditRow] = useState<DispatchTask | null>(null)
  const [form, setForm] = useState({ candidate_id: "", task_key: "", trigger_state: "", freq_hrs: "0", min_count: "1", batch_size: "", max_runs: "1", score_floor: "1.00", auto_mode: false, debug: false, entity_type: "", is_scored: false })
  const [saving, setSaving] = useState(false)

  // Thread status (polled every 5s)
  const [threadStatus, setThreadStatus] = useState<Record<number, ThreadEntry>>({})
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const prevRunningRef = useRef<Record<number, boolean>>({})

  // Stop All confirmation modal
  const [showStopAll, setShowStopAll] = useState(false)
  const [stoppingAll, setStoppingAll] = useState(false)
  const [, forceUiConfig] = useState(0)

  useEffect(() => { loadUiConfig(() => forceUiConfig(n => n + 1)) }, [])
  const uiConfig = getUiConfig()
  const frozenN = resolveFrozenDataColumns(uiConfig, FROZEN_DATA_COLUMNS)
  const truncateChars = resolveCellTruncateChars(uiConfig)

  const loadThreadStatus = useCallback(async () => {
    const res = await api("/api/admin/scheduler/thread_status")
    if (res.ok) setThreadStatus(await res.json())
  }, [])

  useEffect(() => {
    loadThreadStatus()
    pollRef.current = setInterval(loadThreadStatus, 5_000)
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [loadThreadStatus])

  const [taskKeyFilter, setTaskKeyFilter] = useState("")
  const [sectionGroupFilter, setSectionGroupFilter] = useState("")
  const [floorMin, setFloorMin] = useState("")
  const [floorMax, setFloorMax] = useState("")
  const [autoFilter, setAutoFilter] = useState("")
  const [debugFilter, setDebugFilter] = useState("")
  const [freqFilter, setFreqFilter] = useState("")
  const [minCountFilter, setMinCountFilter] = useState("")
  const [batchSizeFilter, setBatchSizeFilter] = useState("")
  const [maxRunsFilter, setMaxRunsFilter] = useState("")
  const scoreFloorOptions = useMemo(
    () => Array.from({ length: 19 }, (_, i) => (1 + i * 0.5).toFixed(2)),
    [],
  )
  const inputStateOptions = useMemo(
    () => (
      form.entity_type === "company"
        ? stateOptions.company
        : form.entity_type === "candidate"
          ? stateOptions.candidate
          : stateOptions.job
    ),
    [form.entity_type, stateOptions],
  )

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [tasksRes, keysRes, statesRes] = await Promise.all([
        api("/api/admin/dispatch_tasks"),
        api("/api/admin/dispatch_tasks/task_keys"),
        api("/api/admin/dispatch_tasks/state_options"),
      ])
      if (tasksRes.ok) setData(await tasksRes.json())
      else setToast({ text: `Failed to load dispatch tasks (${tasksRes.status})`, variant: "error" })
      if (keysRes.ok) {
        const keys = await keysRes.json()
        setAllTaskKeys(typeof keys === "object" && !Array.isArray(keys) ? keys : {})
      }
      if (statesRes.ok) {
        const states = await statesRes.json()
        setStateOptions({
          job: Array.isArray(states?.job) ? states.job : [],
          company: Array.isArray(states?.company) ? states.company : [],
          candidate: Array.isArray(states?.candidate) ? states.candidate : [],
        })
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  useEffect(() => {
    for (const row of data) {
      const running = threadStatus[row.id]?.running ?? false
      const wasRunning = prevRunningRef.current[row.id] ?? false
      if (wasRunning && !running) loadData()
      prevRunningRef.current[row.id] = running
    }
  }, [threadStatus, data, loadData])

  const taskKeys = useMemo(() => [...new Set(data.map(d => d.task_key))].sort(), [data])

  const sectionGroupOptions = useMemo(() => {
    const seen = new Map<string, string>()
    for (const meta of Object.values(allTaskKeys)) {
      const name = meta.task_group_name || "(unassigned)"
      const key = `${meta.task_group_order || ""}\u0000${name}`
      if (!seen.has(key)) seen.set(key, name)
    }
    return [...seen.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, name]) => ({ key, name }))
  }, [allTaskKeys])

  const filterOptionValues = useMemo(() => ({
    freq: [...new Set(data.map(r => r.freq_hrs ?? 0))].sort((a, b) => a - b),
    minCount: [...new Set(data.map(r => r.min_count))].sort((a, b) => a - b),
    batchSize: [...new Set(data.map(r => r.batch_size).filter(v => v != null))].sort((a, b) => (a as number) - (b as number)),
    maxRuns: [...new Set(data.map(r => r.max_runs ?? 1))].sort((a, b) => a - b),
  }), [data])

  const sortRowsWithinSection = useCallback((rows: DispatchTask[]) => {
    return [...rows].sort((a, b) => {
      if (sortCol === "_default") {
        const as_ = allTaskKeys[a.task_key]?.task_seq ?? 999
        const bs_ = allTaskKeys[b.task_key]?.task_seq ?? 999
        if (as_ !== bs_) return sortDir === "asc" ? as_ - bs_ : bs_ - as_
        const tk = a.task_key.localeCompare(b.task_key)
        if (tk !== 0) return tk
        if (!candidateFilter) {
          const av = a.available_count ?? 0
          const bv = b.available_count ?? 0
          if (av !== bv) return bv - av
        }
        return a.id - b.id
      }
      const av = a[sortCol as keyof DispatchTask]
      const bv = b[sortCol as keyof DispatchTask]
      if (av == null && bv == null) return 0
      if (av == null) return 1
      if (bv == null) return -1
      const cmp = av < bv ? -1 : av > bv ? 1 : 0
      return sortDir === "asc" ? cmp : -cmp
    })
  }, [sortCol, sortDir, allTaskKeys, candidateFilter])

  const filteredRows = useMemo(() => {
    let filtered = data
    if (candidateFilter) filtered = filtered.filter(r => r.candidate_id === candidateFilter)
    if (sectionGroupFilter) {
      filtered = filtered.filter(r => {
        const meta = allTaskKeys[r.task_key]
        const name = meta?.task_group_name || "(unassigned)"
        const key = `${meta?.task_group_order || ""}\u0000${name}`
        return key === sectionGroupFilter
      })
    }
    if (taskKeyFilter) filtered = filtered.filter(r => r.task_key === taskKeyFilter)
    if (autoFilter === "on") filtered = filtered.filter(r => !!r.auto_mode)
    if (autoFilter === "off") filtered = filtered.filter(r => !r.auto_mode)
    if (debugFilter === "on") filtered = filtered.filter(r => !!r.debug)
    if (debugFilter === "off") filtered = filtered.filter(r => !r.debug)
    if (freqFilter !== "") filtered = filtered.filter(r => (r.freq_hrs ?? 0) === Number(freqFilter))
    if (minCountFilter !== "") filtered = filtered.filter(r => r.min_count === Number(minCountFilter))
    if (batchSizeFilter !== "") filtered = filtered.filter(r => r.batch_size === Number(batchSizeFilter))
    if (maxRunsFilter !== "") filtered = filtered.filter(r => (r.max_runs ?? 1) === Number(maxRunsFilter))
    if (floorMin !== "" || floorMax !== "") {
      const lo = floorMin === "" ? -Infinity : parseFloat(floorMin)
      const hi = floorMax === "" ? Infinity : parseFloat(floorMax)
      filtered = filtered.filter(r => {
        const scored = r.is_scored ?? !!allTaskKeys[r.task_key]?.is_scored
        if (!scored) return false
        const floor = r.score_floor ?? 1
        return floor >= lo && floor <= hi
      })
    }
    return filtered
  }, [data, candidateFilter, sectionGroupFilter, taskKeyFilter, autoFilter, debugFilter, freqFilter, minCountFilter, batchSizeFilter, maxRunsFilter, floorMin, floorMax, allTaskKeys])

  const sections = useMemo(() => {
    const bySectionKey: Record<string, DispatchTask[]> = {}
    for (const row of filteredRows) {
      const meta = allTaskKeys[row.task_key]
      const name = meta?.task_group_name || "(unassigned)"
      const key = `${meta?.task_group_order || ""}\u0000${name}`
      if (!bySectionKey[key]) bySectionKey[key] = []
      bySectionKey[key].push(row)
    }
    return Object.entries(bySectionKey)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([sectionKey, rows]) => {
        const autoOnCount = rows.filter(r => !!r.auto_mode).length
        return {
          sectionKey,
          groupName: allTaskKeys[rows[0]?.task_key]?.task_group_name || "(unassigned)",
          autoOnCount,
          rows: sortRowsWithinSection(rows),
        }
      })
  }, [filteredRows, allTaskKeys, sortRowsWithinSection])

  useEffect(() => {
    if (didAutoOpenSectionRef.current || sections.length === 0) return
    didAutoOpenSectionRef.current = true
    setOpenSection(sections[0].sectionKey)
  }, [sections])

  const resolvedOpenSection = useMemo(() => {
    if (sections.length === 0) return null
    if (openSection != null && sections.some(s => s.sectionKey === openSection)) return openSection
    return null
  }, [sections, openSection])

  const toggleSort = (col: string) => {
    if (sortCol === col) setSortDir(d => d === "asc" ? "desc" : "asc")
    else { setSortCol(col); setSortDir("asc") }
  }
  const sortIcon = (col: string) => sortCol === col ? (sortDir === "asc" ? " ▲" : " ▼") : ""

  const toggleAutoMode = async (row: DispatchTask) => {
    const res = await api(`/api/admin/dispatch_tasks/${row.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ auto_mode: !row.auto_mode }),
    })
    if (!res.ok) {
      try {
        await readApiError(res, `/api/admin/dispatch_tasks/${row.id}`, "PUT")
      } catch (e) {
        setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: `Update failed (${res.status})`, variant: "error" })
      }
      return
    }
    loadData()
  }

  const toggleDebug = async (row: DispatchTask) => {
    await api(`/api/admin/dispatch_tasks/${row.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ debug: !row.debug }),
    })
    loadData()
  }

  const handleRun = async (e: React.MouseEvent, row: DispatchTask) => {
    e.stopPropagation()
    const res = await api(`/api/admin/dispatch_tasks/${row.id}/run`, { method: "POST" })
    if (!res.ok) {
      try {
        await readApiError(res, `/api/admin/dispatch_tasks/${row.id}/run`, "POST")
      } catch (e) {
        setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: `Run failed (${res.status})`, variant: "error" })
      }
      return
    }
    setTimeout(loadThreadStatus, 500)
  }

  const handleStop = async (e: React.MouseEvent, row: DispatchTask) => {
    e.stopPropagation()
    await api(`/api/admin/dispatch_tasks/${row.id}/stop`, { method: "POST" })
    setTimeout(loadThreadStatus, 500)
  }

  const handleKillAll = async () => {
    setStoppingAll(true)
    try {
      await api("/api/admin/scheduler/stop_all", { method: "POST" })
      setShowStopAll(false)
      setTimeout(loadThreadStatus, 500)
    } finally {
      setStoppingAll(false)
    }
  }

  const activeThreads = useMemo(() =>
    Object.entries(threadStatus).filter(([, e]) => e.running),
    [threadStatus]
  )

  const openAdd = () => {
    setEditRow(null)
    setForm({ candidate_id: selectedId ?? "", task_key: "", trigger_state: "", freq_hrs: "0", min_count: "1", batch_size: "", max_runs: "1", score_floor: "1.00", auto_mode: false, debug: false, entity_type: "", is_scored: false })
    setShowModal(true)
  }
  const openEdit = (row: DispatchTask) => {
    if (row.auto_mode) {
      setToast({ text: "Turn AUTO mode off before editing this row", variant: "error" })
      return
    }
    setEditRow(row)
    const cfg = allTaskKeys[row.task_key]
    setForm({
      candidate_id: row.candidate_id,
      task_key: row.task_key,
      trigger_state: row.trigger_state || cfg?.trigger_state || "",
      freq_hrs: String(row.freq_hrs ?? 0),
      min_count: String(row.min_count),
      batch_size: row.batch_size != null ? String(row.batch_size) : "",
      max_runs: row.max_runs != null ? String(row.max_runs) : "1",
      score_floor: (row.score_floor ?? 1).toFixed(2),
      auto_mode: !!row.auto_mode,
      debug: !!row.debug,
      entity_type: row.entity_type || cfg?.entity_type || "",
      is_scored: row.is_scored ?? !!cfg?.is_scored,
    })
    setShowModal(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      if (editRow) {
        const res = await api(`/api/admin/dispatch_tasks/${editRow.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            freq_hrs: parseFloat(form.freq_hrs) || 0,
            min_count: parseInt(form.min_count, 10),
            trigger_state: form.trigger_state,
            task_key: form.task_key,
            batch_size: form.batch_size ? parseInt(form.batch_size, 10) : null,
            max_runs: form.max_runs !== "" ? parseInt(form.max_runs, 10) : 1,
            score_floor: form.is_scored ? (parseFloat(form.score_floor) || 1) : null,
            auto_mode: form.auto_mode,
            debug: form.debug,
          }),
        })
        if (!res.ok) {
          try {
            await readApiError(res, `/api/admin/dispatch_tasks/${editRow.id}`, "PUT")
          } catch (e) {
            setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: `Save failed (${res.status})`, variant: "error" })
          }
          return
        }
      } else {
        const res = await api("/api/admin/dispatch_tasks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            candidate_id: form.candidate_id,
            task_key: form.task_key,
            trigger_state: form.trigger_state,
            freq_hrs: parseFloat(form.freq_hrs) || 0,
            min_count: parseInt(form.min_count, 10),
            batch_size: form.batch_size ? parseInt(form.batch_size, 10) : null,
            max_runs: form.max_runs !== "" ? parseInt(form.max_runs, 10) : 1,
            score_floor: form.is_scored ? (parseFloat(form.score_floor) || 1) : null,
            auto_mode: form.auto_mode,
          }),
        })
        if (!res.ok) {
          try {
            await readApiError(res, "/api/admin/dispatch_tasks", "POST")
          } catch (e) {
            setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: `Save failed (${res.status})`, variant: "error" })
          }
          return
        }
      }
      setShowModal(false)
      loadData()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-container">
      <div className="list-page-header">
        <h1 className="list-page-title">Scheduled Actions</h1>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {activeThreads.length > 0 && (
            <span className="dispatch-status-badge dispatch-status-warn">
              {activeThreads.length} running
            </span>
          )}
          <button
            className="list-page-bulk-btn"
            style={{ background: activeThreads.length > 0 ? "#c0392b" : undefined, color: activeThreads.length > 0 ? "#fff" : undefined }}
            onClick={() => setShowStopAll(true)}
            disabled={activeThreads.length === 0}
          >
            Stop All
          </button>
          <button className="list-page-bulk-btn" onClick={openAdd}>+ Add Task</button>
        </div>
      </div>

      <div className="admin-filters">
        <AdminCandidateFilterControl
          value={candidateFilter}
          onChange={setCandidateFilter}
          candidates={candidates}
        />
        <label>
          Section/Group
          <select value={sectionGroupFilter} onChange={e => setSectionGroupFilter(e.target.value)}>
            <option value="">All</option>
            {sectionGroupOptions.map(opt => (
              <option key={opt.key} value={opt.key}>{opt.name}</option>
            ))}
          </select>
        </label>
        <label>
          Task
          <select value={taskKeyFilter} onChange={e => setTaskKeyFilter(e.target.value)}>
            <option value="">All</option>
            {taskKeys.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label>
          Floor min
          <select value={floorMin} onChange={e => setFloorMin(e.target.value)}>
            <option value="">All</option>
            {scoreFloorOptions.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label>
          Floor max
          <select value={floorMax} onChange={e => setFloorMax(e.target.value)}>
            <option value="">All</option>
            {scoreFloorOptions.map(v => <option key={v} value={v}>{v}</option>)}
          </select>
        </label>
        <label>
          AUTO
          <select value={autoFilter} onChange={e => setAutoFilter(e.target.value)}>
            <option value="">All</option>
            <option value="on">ON</option>
            <option value="off">OFF</option>
          </select>
        </label>
        <label>
          Debug
          <select value={debugFilter} onChange={e => setDebugFilter(e.target.value)}>
            <option value="">All</option>
            <option value="on">ON</option>
            <option value="off">OFF</option>
          </select>
        </label>
        <label>
          Freq
          <select value={freqFilter} onChange={e => setFreqFilter(e.target.value)}>
            <option value="">All</option>
            {filterOptionValues.freq.map(v => <option key={v} value={String(v)}>{v}</option>)}
          </select>
        </label>
        <label>
          Min count
          <select value={minCountFilter} onChange={e => setMinCountFilter(e.target.value)}>
            <option value="">All</option>
            {filterOptionValues.minCount.map(v => <option key={v} value={String(v)}>{v}</option>)}
          </select>
        </label>
        <label>
          Batch size
          <select value={batchSizeFilter} onChange={e => setBatchSizeFilter(e.target.value)}>
            <option value="">All</option>
            {filterOptionValues.batchSize.map(v => <option key={v} value={String(v)}>{v}</option>)}
          </select>
        </label>
        <label>
          Run counts
          <select value={maxRunsFilter} onChange={e => setMaxRunsFilter(e.target.value)}>
            <option value="">All</option>
            {filterOptionValues.maxRuns.map(v => (
              <option key={v} value={String(v)}>{v === 0 ? "∞ (0)" : String(v)}</option>
            ))}
          </select>
        </label>
      </div>

      {loading ? (
        <div className="list-page-status">Loading…</div>
      ) : sections.length === 0 ? (
        <div className="list-page-status">
          {data.length > 0
            ? "No dispatch tasks match the current filters. Try Candidate: All or clear Section/Group and Task filters."
            : "No dispatch tasks configured"}
        </div>
      ) : sections.map(sec => (
        <div key={sec.sectionKey} style={{ marginBottom: 12 }}>
          <CollapsiblePanel
            label={<>{sec.groupName} ({sec.autoOnCount} / {sec.rows.length} AUTO)</>}
            expanded={resolvedOpenSection === sec.sectionKey}
            onExpandedChange={next => {
              if (next) setOpenSection(sec.sectionKey)
              else setOpenSection(null)
            }}
          >
            {resolvedOpenSection === sec.sectionKey ? (
              <ScheduledPhaseTable
                rows={sec.rows}
                frozenN={frozenN}
                truncateChars={truncateChars}
                threadStatus={threadStatus}
                allTaskKeys={allTaskKeys}
                toggleSort={toggleSort}
                sortIcon={sortIcon}
                openEdit={openEdit}
                toggleAutoMode={toggleAutoMode}
                toggleDebug={toggleDebug}
                handleRun={handleRun}
                handleStop={handleStop}
              />
            ) : null}
          </CollapsiblePanel>
        </div>
      ))}

      {/* Stop All confirmation modal */}
      {showStopAll && (
        <div className="modal-overlay" onClick={() => setShowStopAll(false)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span className="modal-title">Kill Running Threads</span>
              <button className="modal-close" onClick={() => setShowStopAll(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: "0.75rem" }}>The following tasks will be immediately killed:</p>
              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {activeThreads.map(([id, entry]) => (
                  <li key={id} style={{ padding: "0.25rem 0", fontFamily: "monospace", fontSize: "0.88rem" }}>
                    <span className="dispatch-status-badge dispatch-status-warn">{entry.is_auto ? "AUTO" : "CLICK"}</span>
                    {" "}{entry.task_key} <span style={{ color: "var(--text-secondary, #8b949e)" }}>({entry.candidate_id})</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="modal-footer">
              <button className="modal-btn cancel" onClick={() => setShowStopAll(false)}>Cancel</button>
              <button className="modal-btn save" style={{ background: "#c0392b" }} onClick={handleKillAll} disabled={stoppingAll}>
                {stoppingAll ? "Killing…" : "Kill Now"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add / Edit task modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span className="modal-title">{editRow ? "Edit Task" : "Add Task"}</span>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <div className="modal-body">
              {!editRow && (
                <div className="modal-detail-row">
                  <span className="modal-detail-label">Candidate</span>
                  <input type="text" value={form.candidate_id || "(none selected)"} readOnly style={{ opacity: 0.7 }} />
                </div>
              )}
              <div className="modal-detail-row">
                <span className="modal-detail-label">Task</span>
                <select value={form.task_key} onChange={e => {
                  const key = e.target.value
                  const cfg = allTaskKeys[key]
                  if (editRow) {
                    setForm(f => taskKeyChangePatch(f, key, cfg))
                  } else {
                    setForm({
                      ...form,
                      task_key: key,
                      entity_type: cfg?.entity_type || "",
                      trigger_state: cfg?.trigger_state || "",
                      is_scored: !!cfg?.is_scored,
                      score_floor: "1.00",
                    })
                  }
                }}>
                  <option value="">Select…</option>
                  {Object.keys(allTaskKeys).sort().map(k => <option key={k} value={k}>{k}</option>)}
                </select>
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Entity Type</span>
                <input type="text" value={form.entity_type} readOnly style={{ opacity: 0.7 }} />
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Input State</span>
                <select value={form.trigger_state} onChange={e => setForm({ ...form, trigger_state: e.target.value })}>
                  <option value="">Select…</option>
                  {(inputStateOptions).map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Freq (hrs)</span>
                <input type="number" min="0" step="0.25" value={form.freq_hrs} onChange={e => setForm({ ...form, freq_hrs: e.target.value })} />
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Min Count</span>
                <input type="number" min="0" value={form.min_count} onChange={e => setForm({ ...form, min_count: e.target.value })} />
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Batch Size</span>
                <input type="number" min="1" placeholder="default" value={form.batch_size} onChange={e => setForm({ ...form, batch_size: e.target.value })} />
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Max Runs</span>
                <input type="number" min="0" placeholder="1" value={form.max_runs} onChange={e => setForm({ ...form, max_runs: e.target.value })}
                  title="0 = loop until queue drained below min_count; 1 = once per cycle; N = up to N times" />
              </div>
              {form.is_scored && (
                <div className="modal-detail-row">
                  <span className="modal-detail-label">Score Floor</span>
                  <select value={form.score_floor} onChange={e => setForm({ ...form, score_floor: e.target.value })}>
                    {scoreFloorOptions.map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </div>
              )}
              <div className="modal-detail-row">
                <span className="modal-detail-label">AUTO mode</span>
                <input type="checkbox" checked={form.auto_mode} onChange={e => setForm({ ...form, auto_mode: e.target.checked })} />
              </div>
              <div className="modal-detail-row">
                <span className="modal-detail-label">Debug</span>
                <input type="checkbox" checked={form.debug} onChange={e => setForm({ ...form, debug: e.target.checked })} />
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-btn cancel" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="modal-btn save" onClick={handleSave} disabled={saving || (!editRow && !form.candidate_id)}>
                {saving ? "Saving…" : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}

      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
