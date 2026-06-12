import { useEffect, useState } from "react"
import Modal from "./Modal"
import { TabBar } from "./TabbedTextArea"
import api from "../lib/api"
import { sumCalcCostComponents } from "../lib/timesheetCost"

// Block types in canonical display order (matches BLOCK_TYPES in config.py)
const BLOCK_TYPE_ORDER = ["SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE", "TASK", "RESPONSE"]

interface AgentDataBlock {
  agent_data_id: string
  block_type: string
  block_data: string
  token_size: number
  task_key: string
  created_at: string
}

interface TimesheetRow {
  cache_write_tokens: number
  cache_read_tokens: number
  total_no_cache_input_tokens: number
  total_output_tokens: number
  calc_cost_cache_write: number
  calc_cost_cache_read: number
  calc_cost_no_cache_input: number
  calc_cost_output: number
}

interface Totals {
  cache_write_tokens: number
  cache_read_tokens: number
  total_no_cache_input_tokens: number
  total_output_tokens: number
  cost_cache_write: number
  cost_cache_read: number
  cost_input: number
  cost_output: number
}

function sumTimesheets(rows: TimesheetRow[]): Totals {
  return rows.reduce((a, r) => ({
    cache_write_tokens:        a.cache_write_tokens        + (r.cache_write_tokens || 0),
    cache_read_tokens:         a.cache_read_tokens         + (r.cache_read_tokens || 0),
    total_no_cache_input_tokens: a.total_no_cache_input_tokens + (r.total_no_cache_input_tokens || 0),
    total_output_tokens:       a.total_output_tokens       + (r.total_output_tokens || 0),
    cost_cache_write:          a.cost_cache_write          + (r.calc_cost_cache_write || 0),
    cost_cache_read:           a.cost_cache_read           + (r.calc_cost_cache_read || 0),
    cost_input:                a.cost_input                + (r.calc_cost_no_cache_input || 0),
    cost_output:               a.cost_output               + (r.calc_cost_output || 0),
  }), {
    cache_write_tokens: 0, cache_read_tokens: 0,
    total_no_cache_input_tokens: 0, total_output_tokens: 0,
    cost_cache_write: 0, cost_cache_read: 0, cost_input: 0, cost_output: 0,
  })
}

function formatContent(raw: string): string {
  try { return JSON.stringify(JSON.parse(raw), null, 2) } catch { return raw }
}

function blockContent(blocks: AgentDataBlock[]): string {
  if (blocks.length === 1) return formatContent(blocks[0].block_data)
  return blocks.map((b, i) => `--- [${i + 1}/${blocks.length}] ---\n${formatContent(b.block_data)}`).join("\n\n")
}

interface Props {
  batchId: string | null
  onClose: () => void
}

export default function BatchAgentDataModal({ batchId, onClose }: Props) {
  const [blocks, setBlocks] = useState<AgentDataBlock[]>([])
  const [totals, setTotals] = useState<Totals | null>(null)
  const [timesheetRows, setTimesheetRows] = useState<TimesheetRow[]>([])
  const [loading, setLoading] = useState(false)
  const [activeType, setActiveType] = useState<string>("")

  useEffect(() => {
    if (!batchId) return
    setLoading(true)
    setBlocks([])
    setTotals(null)
    setTimesheetRows([])
    Promise.all([
      api(`/api/agent_data/${encodeURIComponent(batchId)}`).then(r => r.json()),
      api(`/api/admin/timesheets?batch_id=${encodeURIComponent(batchId)}`).then(r => r.json()),
    ]).then(([blockData, tsData]) => {
      const b: AgentDataBlock[] = Array.isArray(blockData) ? blockData : []
      setBlocks(b)
      const ts = Array.isArray(tsData) ? tsData : []
      setTimesheetRows(ts)
      setTotals(sumTimesheets(ts))
      // Default to first block type present in canonical order
      const present = BLOCK_TYPE_ORDER.filter(t => b.some(x => x.block_type === t))
      setActiveType(present[0] ?? b[0]?.block_type ?? "")
    }).catch(() => {}).finally(() => setLoading(false))
  }, [batchId])

  // Group blocks by type; preserve canonical order, append any unknown types at end
  const byType: Record<string, AgentDataBlock[]> = {}
  for (const b of blocks) {
    ;(byType[b.block_type] ??= []).push(b)
  }
  const orderedTypes = [
    ...BLOCK_TYPE_ORDER.filter(t => byType[t]),
    ...Object.keys(byType).filter(t => !BLOCK_TYPE_ORDER.includes(t)),
  ]
  const tabBarTabs = orderedTypes.map(t => ({
    key: t,
    label: byType[t].length > 1 ? `${t} ×${byType[t].length}` : t,
  }))

  const totalCost = timesheetRows.reduce(
    (s, r) => s + sumCalcCostComponents(r as unknown as Record<string, unknown>),
    0,
  )

  const fmt = (n: number) => n.toLocaleString()
  const fmtCost = (n: number) => `$${n.toFixed(4)}`

  return (
    <Modal open={!!batchId} onClose={onClose} title={batchId ?? ""} size="wide">
      <div className="batch-agent-data-wrapper">
        {loading && <p className="entity-loading">Loading…</p>}

        {!loading && totals && (
          <div className="batch-cost-summary">
            <span className="batch-cost-label">Tokens &amp; Cost</span>
            <span>Cache Write: <strong>{fmt(totals.cache_write_tokens)}</strong> <em>{fmtCost(totals.cost_cache_write)}</em></span>
            <span>Cache Read: <strong>{fmt(totals.cache_read_tokens)}</strong> <em>{fmtCost(totals.cost_cache_read)}</em></span>
            <span>Input: <strong>{fmt(totals.total_no_cache_input_tokens)}</strong> <em>{fmtCost(totals.cost_input)}</em></span>
            <span>Output: <strong>{fmt(totals.total_output_tokens)}</strong> <em>{fmtCost(totals.cost_output)}</em></span>
            <span className="batch-cost-total">Total: <strong>{fmtCost(totalCost)}</strong></span>
          </div>
        )}

        {!loading && orderedTypes.length > 0 && (
          <div className="batch-agent-data-body">
            <TabBar tabs={tabBarTabs} active={activeType} onChange={setActiveType} />
            <textarea
              className="entity-story-content batch-agent-data-textarea"
              readOnly
              value={activeType && byType[activeType] ? blockContent(byType[activeType]) : ""}
            />
          </div>
        )}

        {!loading && blocks.length === 0 && (
          <p className="entity-empty">No agent data blocks recorded for this batch.</p>
        )}
      </div>
    </Modal>
  )
}
