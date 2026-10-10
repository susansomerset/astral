import { useCallback, useEffect, useMemo, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import AdminCandidateFilterControl from "../components/AdminCandidateFilterControl"
import api from "../lib/api"
import { fmtTime } from "../lib/fmt"
import { useLocalStorage } from "../lib/useLocalStorage"

// Admin-grade script page (not under the test bible). Flat rows from the API are stitched into
// Total > Group > Task > Version > Candidate > Ledger line; sorting is per sibling set.

type Level = "total" | "group" | "task" | "version" | "candidate" | "line"
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Row = Record<string, any> & { id: string; parent: string | null; level: Level; label: string; has_children: boolean }

type Fmt = "text" | "int" | "money" | "pct" | "date" | "bool" | "dur"
type Align = "left" | "center" | "right"
interface Col { key: string; label: string; title: string; fmt: Fmt; align: Align }

// Order follows Susan's column list; abbreviations are explained in the header tooltips.
const COLS: Col[] = [
  { key: "entity_type", label: "Entity type", title: "Entity type — what kind of thing this task works on (job, company, candidate, meteorite...), taken from the dispatch ledger.", fmt: "text", align: "left" },
  { key: "valid", label: "Valid", title: "Valid — can this version's prompts be built for this candidate? On a candidate row: yes = every {$TOKEN} in the prompts (artifacts, rubric) has content for that candidate and the rubric has no errors; no = something is missing (hover the 'no' to see what). On rows above: how many candidate/version pairs are valid out of how many could be checked, e.g. 3/5.", fmt: "bool", align: "center" },
  { key: "batches", label: "Runs", title: "Runs — number of dispatch batches (one ledger row each), whatever their final status.", fmt: "int", align: "center" },
  { key: "completed", label: "Done", title: "Done — batches that finished with status COMPLETED. The rest failed or were interrupted.", fmt: "int", align: "center" },
  { key: "fail_calls", label: "Call fail", title: "Failed calls — LLM calls recorded in the timesheet as failures (bad JSON, truncated output, API errors).", fmt: "int", align: "center" },
  { key: "ok_calls", label: "Call ok", title: "Successful calls — LLM calls in the timesheet that did not fail.", fmt: "int", align: "center" },
  { key: "subjects", label: "Subj", title: "Subjects — how many entities (jobs, companies, candidates...) the batches processed. Ledger total_processed.", fmt: "int", align: "center" },
  { key: "passed", label: "Pass", title: "Pass — subjects that ended in a pass state. Ledger total_passed.", fmt: "int", align: "center" },
  { key: "failed", label: "Fail", title: "Fail — subjects that ended in a fail state (judged and rejected). Ledger total_failed.", fmt: "int", align: "center" },
  { key: "errors", label: "Error", title: "Error — subjects that ended in a technical error. Ledger total_errors.", fmt: "int", align: "center" },
  { key: "unresolved", label: "Unres", title: "Unresolved — Subjects minus Pass, Fail and Error. Anything other than 0 means some subjects have no recorded end state (still waiting, or a counting mismatch).", fmt: "int", align: "center" },
  { key: "retries", label: "Retry", title: "Retries — failed calls that were followed by a successful call in the same step, i.e. the bad response got another attempt.", fmt: "int", align: "center" },
  { key: "tokens", label: "Total tokens", title: "Total tokens — all input tokens plus all output tokens.", fmt: "int", align: "right" },
  { key: "in_tokens", label: "Input tokens", title: "Total input tokens — No-cache + Cache-write + Cache-read.", fmt: "int", align: "right" },
  { key: "nocache_tokens", label: "No-cache tokens", title: "No-cache input tokens — input sent at full price (not served from, or saved to, the prompt cache).", fmt: "int", align: "right" },
  { key: "cache_write_tokens", label: "Cache-write tokens", title: "Cache-write tokens — input saved into the prompt cache on this call (some providers price this higher).", fmt: "int", align: "right" },
  { key: "cache_read_tokens", label: "Cache-read tokens", title: "Cache-read tokens — input served from the prompt cache, as reported by the provider (cheaper).", fmt: "int", align: "right" },
  { key: "cache_hit_pct", label: "Cache hit %", title: "Cache hit % — Cache-read tokens as a share of total input tokens. Higher means more of the prompt was served from cache.", fmt: "pct", align: "center" },
  { key: "out_tokens", label: "Output tokens", title: "Total output tokens — tokens the model generated.", fmt: "int", align: "right" },
  { key: "out_min", label: "Output min", title: "Output per run, smallest — fewest output tokens in any single run (runs that made at least one LLM call).", fmt: "int", align: "right" },
  { key: "out_avg", label: "Output avg", title: "Output per run, average — output tokens divided by the number of runs that made at least one LLM call.", fmt: "int", align: "right" },
  { key: "out_max", label: "Output max", title: "Output per run, largest — most output tokens in any single run (runs that made at least one LLM call).", fmt: "int", align: "right" },
  { key: "spend", label: "Total spend", title: "Total spend — sum of what the timesheets recorded: the provider's actual charge (platform cost) when it has been reconciled, otherwise the cost stored on the timesheet row. Never re-priced here.", fmt: "money", align: "center" },
  { key: "spend_input", label: "Input spend", title: "Input spend — stored cost of no-cache input tokens. Empty for rows where only the provider's total charge is known.", fmt: "money", align: "center" },
  { key: "spend_cache_write", label: "Cache-write spend", title: "Cache-write spend — stored cost of cache-write tokens. Empty for rows where only the provider's total charge is known.", fmt: "money", align: "center" },
  { key: "spend_cache_read", label: "Cache-read spend", title: "Cache-read spend — stored cost of cache-read tokens. Empty for rows where only the provider's total charge is known.", fmt: "money", align: "center" },
  { key: "spend_output", label: "Output spend", title: "Output spend — stored cost of output tokens. Empty for rows where only the provider's total charge is known.", fmt: "money", align: "center" },
  { key: "spend_platform_only", label: "Unitemized spend", title: "Unitemized spend — the part of Total spend that the provider reported only as a single charge, with no input/cache/output split. Total spend = the four itemized columns + this one.", fmt: "money", align: "center" },
  { key: "spend_run_avg", label: "Spend/run avg", title: "Spend per run, average — total spend divided by runs that made at least one LLM call.", fmt: "money", align: "center" },
  { key: "spend_run_min", label: "Spend/run min", title: "Spend per run, cheapest — lowest spend of any single run (runs with at least one LLM call).", fmt: "money", align: "center" },
  { key: "spend_run_max", label: "Spend/run max", title: "Spend per run, priciest — highest spend of any single run (runs with at least one LLM call).", fmt: "money", align: "center" },
  { key: "spend_run_sd", label: "Spend/run spread", title: "Spend per run, spread — standard deviation of run cost. Small = predictable cost per run; large = costs vary a lot between runs.", fmt: "money", align: "center" },
  { key: "spend_entity", label: "Spend/subject", title: "Spend per subject — total spend divided by the number of subjects processed.", fmt: "money", align: "center" },
  { key: "duration", label: "Total duration", title: "Total duration \u2014 wall-clock time from start to finish, added up over runs that COMPLETED or FAILED (interrupted runs are left out: their end time is when something restarted, not when the run finished). Includes waiting between calls and looping over entities, not just LLM time. In Copy JSON/TSV this is in seconds.", fmt: "dur", align: "center" },
  { key: "dur_run_avg", label: "Duration/run avg", title: "Duration per run, average \u2014 total duration divided by the number of runs that COMPLETED or FAILED (interrupted runs are left out: their end time is when something restarted, not when the run finished).", fmt: "dur", align: "center" },
  { key: "dur_run_min", label: "Duration/run min", title: "Duration per run, shortest \u2014 quickest single run among runs that COMPLETED or FAILED (interrupted runs are left out: their end time is when something restarted, not when the run finished).", fmt: "dur", align: "center" },
  { key: "dur_run_max", label: "Duration/run max", title: "Duration per run, longest \u2014 slowest single run among runs that COMPLETED or FAILED (interrupted runs are left out: their end time is when something restarted, not when the run finished).", fmt: "dur", align: "center" },
  { key: "dur_run_sd", label: "Duration/run spread", title: "Duration per run, spread \u2014 standard deviation of run length. Small = runs take about the same time; large = run times vary a lot.", fmt: "dur", align: "center" },
  { key: "dur_entity", label: "Duration/subject", title: "Duration per subject \u2014 total duration divided by the subjects processed in those same runs.", fmt: "dur", align: "center" },
  { key: "last_success", label: "Last successful run", title: "Last successful run — start date of the most recent batch that COMPLETED with at least one pass. Hover for the full timestamp.", fmt: "date", align: "center" },
  { key: "last_clean", label: "Last error-free run", title: "Last clean run — start date of the most recent batch that COMPLETED, processed at least one subject, and had 0 errors. Hover for the full timestamp.", fmt: "date", align: "center" },
  { key: "version_date", label: "Version date", title: "Version date — when this agent_task version was last updated. On a task row: its current version. Hover for the full timestamp.", fmt: "date", align: "center" },
  { key: "status", label: "Status", title: "Status — the ledger status of this batch (COMPLETED, FAILED or INTERRUPTED). Shown on ledger lines only.", fmt: "text", align: "left" },
]
// Column groups. Collapsed = only the headline column stays. Entity type / Valid / Status are never grouped.
const GROUPS = [
  { id: "counts", label: "Counts", head: "batches", keys: ["batches", "completed", "fail_calls", "ok_calls", "subjects", "passed", "failed", "errors", "unresolved", "retries"] },
  { id: "tokens", label: "Tokens", head: "tokens", keys: ["tokens", "in_tokens", "nocache_tokens", "cache_write_tokens", "cache_read_tokens", "cache_hit_pct", "out_tokens", "out_min", "out_avg", "out_max"] },
  { id: "spend", label: "Spend", head: "spend", keys: ["spend", "spend_input", "spend_cache_write", "spend_cache_read", "spend_output", "spend_platform_only", "spend_run_avg", "spend_run_min", "spend_run_max", "spend_run_sd", "spend_entity"] },
  { id: "duration", label: "Duration", head: "duration", keys: ["duration", "dur_run_avg", "dur_run_min", "dur_run_max", "dur_run_sd", "dur_entity"] },
  { id: "dates", label: "Dates", head: "last_success", keys: ["last_success", "last_clean", "version_date"] },
] as const
const GROUP_OF: Record<string, (typeof GROUPS)[number]> = {}
for (const g of GROUPS) for (const k of g.keys) GROUP_OF[k] = g

// Path columns are exported too so a flat TSV/JSON row says where it sits in the tree.
const PATH_KEYS = ["level", "task_group", "task_key", "version", "candidate_id", "batch_id"]
const EXPORT_KEYS = [...PATH_KEYS, ...COLS.map(c => c.key), "valid_note"]

function fmtMoney(n: number): string {
  const a = Math.abs(n)
  return `$${n.toFixed(a >= 1 ? 2 : a >= 0.01 ? 4 : 6)}`
}

// Money renders as two fixed-width halves so the decimal points line up down the column.
function Money({ v }: { v: unknown }) {
  if (v === null || v === undefined || v === "") return <>—</>
  const [i, f] = fmtMoney(Number(v)).split(".")
  return <span className="tp-money"><span className="tp-mi">{i}</span><span className="tp-mf">.{f}</span></span>
}

// 4000s -> "1h 6m 40s"; under a minute keeps one decimal below 10s so quick runs stay distinguishable.
function fmtDur(sec: number): string {
  if (sec < 10) return `${sec.toFixed(1)}s`
  const t = Math.round(sec)
  const d = Math.floor(t / 86400), h = Math.floor((t % 86400) / 3600), m = Math.floor((t % 3600) / 60), s = t % 60
  return [d && `${d}d`, (d || h) && `${h}h`, (d || h || m) && `${m}m`, `${s}s`].filter(Boolean).join(" ")
}

function fmtCell(v: unknown, f: Fmt): string {
  if (v === null || v === undefined || v === "") return "—"
  switch (f) {
    case "int": return Math.round(Number(v)).toLocaleString()  // #,##0 — no decimals, averages included
    case "dur": return fmtDur(Number(v))
    case "pct": return `${Number(v).toFixed(1)}%`
    case "date": return fmtTime(String(v)).split(",")[0]  // m/d/yy; full timestamp lives in the tooltip
    case "bool": return typeof v === "string" ? v : v ? "yes" : "no"  // ratio strings like "3/5" pass through
    default: return String(v)
  }
}

function cmp(a: unknown, b: unknown): number {
  // Blanks always sink, whichever direction is active, so empty cells are easy to find with a date sort.
  const an = a === null || a === undefined || a === "", bn = b === null || b === undefined || b === ""
  if (an || bn) return an === bn ? 0 : an ? 1 : -1
  if (typeof a === "number" && typeof b === "number") return a - b
  if (typeof a === "boolean" && typeof b === "boolean") return Number(a) - Number(b)
  return String(a).localeCompare(String(b), undefined, { numeric: true })
}

// Pass / Fail / Error / Runs filters: All = no filter, None = value is 0, Any = value > 0 (rows AND together).
type Tri = "all" | "none" | "any"
const FLT = [
  { key: "passed", label: "Pass" }, { key: "failed", label: "Fail" },
  { key: "errors", label: "Error" }, { key: "batches", label: "Runs" },
] as const
type Flt = Record<(typeof FLT)[number]["key"], Tri>
const NO_FLT: Flt = { passed: "all", failed: "all", errors: "all", batches: "all" }
const filtering = (f: Flt) => FLT.some(x => f[x.key] !== "all")
const matches = (r: Row, f: Flt) => FLT.every(x => {
  const n = Number(r[x.key]) || 0
  return f[x.key] === "all" || (f[x.key] === "none" ? n === 0 : n > 0)
})

// A row stays visible if it matches or any loaded descendant matches (ancestors give context).
function keepSet(byParent: Record<string, Row[]>, rootId: string, f: Flt): Set<string> {
  const keep = new Set<string>()
  const walk = (id: string): boolean => {
    let any = false
    for (const r of byParent[id] || []) {
      const sub = walk(r.id)
      if (sub || matches(r, f)) { keep.add(r.id); any = true }
    }
    return any
  }
  walk(rootId)
  return keep
}

const toUtcParam = (local: string) => (local ? new Date(local).toISOString() : "")

async function copyText(text: string) {
  try { await navigator.clipboard.writeText(text) } catch {
    const ta = document.createElement("textarea")
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand("copy")
    document.body.removeChild(ta)
  }
}

export default function AdminTaskPerformance() {
  const { candidates } = useCandidate()
  const [from, setFrom] = useState("")
  const [to, setTo] = useState("")
  const [currentOnly, setCurrentOnly] = useState(true)
  const [candidate, setCandidate] = useState("")
  const [rows, setRows] = useState<Row[]>([])
  const [lineRows, setLineRows] = useState<Record<string, Row[]>>({})  // candidate node id -> ledger lines
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<Set<string>>(new Set(["T"]))
  const [sort, setSort] = useState<{ key: string; dir: "asc" | "desc" } | null>(null)
  const [note, setNote] = useState("")
  const [flt, setFlt] = useState<Flt>(NO_FLT)
  const [collapsedGroups, setCollapsedGroups] = useLocalStorage<string[]>("tp-collapsed-groups", [])
  // Collapsed groups keep only their headline column; sorting/copy still see every column.
  const shownCols = useMemo(
    () => COLS.filter(c => { const g = GROUP_OF[c.key]; return !g || !collapsedGroups.includes(g.id) || g.head === c.key }),
    [collapsedGroups],
  )
  const toggleGroup = (id: string) => setCollapsedGroups(p => (p.includes(id) ? p.filter(x => x !== id) : [...p, id]))

  const baseQs = useCallback(() => {
    const p = new URLSearchParams()
    if (from) p.set("date_from", toUtcParam(from))
    if (to) p.set("date_to", toUtcParam(to))
    if (currentOnly) p.set("current_only", "1")
    if (candidate) p.set("candidate_id", candidate)
    return p
  }, [from, to, currentOnly, candidate])

  const fetchRows = useCallback(async (extra: Record<string, string> = {}): Promise<Row[]> => {
    const p = baseQs()
    for (const [k, v] of Object.entries(extra)) p.set(k, v)
    const r = await api(`/api/admin/task_performance?${p}`)
    const data = await r.json()
    return Array.isArray(data.rows) ? data.rows : []
  }, [baseQs])

  const fetchLines = useCallback(async (cand: Row) => {
    const got = await fetchRows({ line_task_key: cand.task_key, line_version: cand.version, line_candidate: cand.candidate_id })
    setLineRows(prev => ({ ...prev, [cand.id]: got.filter(r => r.level === "line") }))
  }, [fetchRows])

  // Reload aggregates whenever a filter changes; re-pull lines for candidate nodes that are still open.
  useEffect(() => {
    let live = true
    setLoading(true)
    fetchRows().then(async got => {
      if (!live) return
      setRows(got)
      setLineRows({})
      const open = got.filter(r => r.level === "candidate" && expanded.has(r.id))
      await Promise.all(open.map(fetchLines))
    }).catch(() => live && setRows([])).finally(() => live && setLoading(false))
    return () => { live = false }
    // expanded is read once per reload on purpose; toggling a node must not refetch everything.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchRows])

  const children = useMemo(() => {
    const m: Record<string, Row[]> = {}
    for (const r of [...rows, ...Object.values(lineRows).flat()]) {
      if (r.parent) (m[r.parent] ||= []).push(r)
    }
    if (sort) {
      for (const k of Object.keys(m)) {
        m[k].sort((a, b) => (sort.dir === "asc" ? 1 : -1) * cmp(a[sort.key], b[sort.key]) || cmp(a.label, b.label))
      }
    }
    return m
  }, [rows, lineRows, sort])

  const total = rows.find(r => r.level === "total")

  // DFS in display order; `all` ignores collapse state (used by copy).
  const keep = useMemo(() => (total && filtering(flt) ? keepSet(children, total.id, flt) : null), [children, total, flt])

  const visible = useMemo(() => {
    const out: Row[] = []
    const walk = (id: string) => {
      for (const r of children[id] || []) {
        if (keep && !keep.has(r.id)) continue
        out.push(r)
        if (expanded.has(r.id)) walk(r.id)
      }
    }
    if (total && expanded.has("T")) walk(total.id)
    return out
  }, [children, expanded, total, keep])

  // Changing a filter opens the path down to every surviving row so matches are visible straight away.
  function changeFilter(key: keyof Flt, v: Tri) {
    const next = { ...flt, [key]: v }
    setFlt(next)
    if (!total || !filtering(next)) return
    const k = keepSet(children, total.id, next)
    const all = [...rows, ...Object.values(lineRows).flat()]
    setExpanded(prev => {
      const n = new Set(prev)
      for (const r of all) if (k.has(r.id) && r.parent) n.add(r.parent)
      return n
    })
  }

  function toggle(r: Row) {
    if (!r.has_children) return
    const open = expanded.has(r.id)
    setExpanded(prev => {
      const n = new Set(prev)
      if (open) n.delete(r.id); else n.add(r.id)
      return n
    })
    if (!open && r.level === "candidate" && !lineRows[r.id]) fetchLines(r)
  }

  async function expandAll() {
    setLoading(true)
    const got = await fetchRows({ lines: "all" })
    const byParent: Record<string, Row[]> = {}
    for (const r of got.filter(x => x.level === "line")) (byParent[r.parent as string] ||= []).push(r)
    setLineRows(byParent)
    setExpanded(new Set(got.filter(r => r.has_children).map(r => r.id)))
    setLoading(false)
  }

  function clickSort(key: string) {
    setSort(s => (!s || s.key !== key ? { key, dir: "asc" } : s.dir === "asc" ? { key, dir: "desc" } : null))
  }

  // Copy always includes every ledger line (one extra fetch), in the current sort order.
  async function copyAll(kind: "json" | "tsv") {
    setNote("Collecting rows…")
    const got = await fetchRows({ lines: "all" })
    const byParent: Record<string, Row[]> = {}
    for (const r of got) if (r.parent) (byParent[r.parent] ||= []).push(r)
    if (sort) for (const k of Object.keys(byParent)) {
      byParent[k].sort((a, b) => (sort.dir === "asc" ? 1 : -1) * cmp(a[sort.key], b[sort.key]) || cmp(a.label, b.label))
    }
    const out: Row[] = []
    const t = got.find(r => r.level === "total")
    const k = t && filtering(flt) ? keepSet(byParent, t.id, flt) : null
    const walk = (id: string) => { for (const r of byParent[id] || []) { if (k && !k.has(r.id)) continue; out.push(r); walk(r.id) } }
    if (t) { out.push(t); walk(t.id) }
    const text = kind === "json"
      ? JSON.stringify(out.map(r => Object.fromEntries(EXPORT_KEYS.map(k => [k, r[k] ?? null]))), null, 2)
      : [EXPORT_KEYS.join("\t"), ...out.map(r => EXPORT_KEYS.map(k => String(r[k] ?? "").replace(/[\t\r\n]+/g, " ")).join("\t"))].join("\n")
    await copyText(text)
    setNote(`Copied ${out.length.toLocaleString()} rows as ${kind.toUpperCase()}`)
    setTimeout(() => setNote(""), 4000)
  }

  const arrow = (key: string) => (sort?.key === key ? (sort.dir === "asc" ? " ▲" : " ▼") : "")

  function renderRow(r: Row, sticky = false) {
    const open = expanded.has(r.id)
    return (
      <tr key={r.id} onClick={() => { if (!window.getSelection()?.toString()) toggle(r) }}  // a drag-select to copy text must not collapse the row
        className={`tp-row tp-${r.level}${r.has_children ? " tp-click" : ""}${keep && r.level !== "total" && !matches(r, flt) ? " tp-ctx" : ""}${sticky ? " tp-total-row" : ""}`}>
        <td className="tp-label" style={{ paddingLeft: 8 + ["total", "group", "task", "version", "candidate", "line"].indexOf(r.level) * 16 }}>
          <span className={`tp-twisty${r.has_children ? "" : " tp-twisty-off"}`}>{open ? "▾" : "▸"}</span>
          <span title={r.label}>{r.label}</span>
        </td>
        {shownCols.map(c => (
          <td key={c.key} className={`tp-num tp-a-${c.align} tp-f-${c.fmt}`}
            title={c.key === "valid" && r.valid_note ? r.valid_note : c.fmt === "date" && r[c.key] ? fmtTime(String(r[c.key])) : undefined}>
            {c.fmt === "money" ? <Money v={r[c.key]} /> : fmtCell(r[c.key], c.fmt)}
          </td>
        ))}
      </tr>
    )
  }

  return (
    <div className="list-page">
      <div className="list-page-header"><h1 className="list-page-title">Task Performance</h1></div>
      <div className="admin-filters">
        <label>From (local)<input type="datetime-local" step={1} value={from} onChange={e => setFrom(e.target.value)} /></label>
        <label>To (local)<input type="datetime-local" step={1} value={to} onChange={e => setTo(e.target.value)} /></label>
        <label>
          Versions
          <select value={currentOnly ? "current" : "all"} onChange={e => setCurrentOnly(e.target.value === "current")}>
            <option value="current">Current only</option>
            <option value="all">All</option>
          </select>
        </label>
        <AdminCandidateFilterControl value={candidate} onChange={setCandidate} candidates={candidates} />
        {FLT.map(f => (
          <div key={f.key} className="tp-tri" title={`${f.label} filter — All: show every row. None: only rows where ${f.label} is 0. Any: only rows where ${f.label} is greater than 0. Rows above a match stay visible, greyed, for context.`}>
            <span>{f.label}</span>
            <div className="tp-tri-row">
              {(["none", "any", "all"] as Tri[]).map(t => (
                <button key={t} className={`tp-tri-btn${flt[f.key] === t ? " on" : ""}`} onClick={() => changeFilter(f.key, t)}>
                  {t === "none" ? "None" : t === "any" ? "Any" : "All"}
                </button>
              ))}
            </div>
          </div>
        ))}
        <button className="btn" onClick={() => { setFrom(""); setTo("") }}>Clear dates</button>
        <button className="btn" onClick={() => setExpanded(new Set(["T"]))}>Collapse</button>
        <button className="btn" onClick={expandAll}>Expand all</button>
        <button className="btn primary" onClick={() => copyAll("json")}>Copy JSON</button>
        <button className="btn primary" onClick={() => copyAll("tsv")}>Copy TSV</button>
        {note && <span className="tp-note">{note}</span>}
      </div>

      {loading && !rows.length ? <p className="list-page-status">Loading...</p> : (
        <div className="list-page-table-wrap list-page-table-wrap--scroll tp-wrap">
          <table className="list-page-table tp-table">
            <thead>
              <tr className="tp-band">
                <th className="tp-label" />
                <th colSpan={2} />
                {GROUPS.map(g => {
                  const n = shownCols.filter(c => GROUP_OF[c.key] === g).length
                  const closed = collapsedGroups.includes(g.id)
                  return (
                    <th key={g.id} colSpan={n} className="tp-band-th tp-a-center"
                      title={closed ? `${g.label} is collapsed to its headline column. Click to show every ${g.label.toLowerCase()} column.` : `Click to collapse ${g.label} to its headline column.`}
                      onClick={() => toggleGroup(g.id)}>
                      {closed ? "▸" : "▾"} {g.label}
                    </th>
                  )
                })}
                <th />
              </tr>
              <tr>
                <th className="tp-label tp-a-left sortable" title="Task key — the tree runs Task group > Task key > Version (agent_task record) > Candidate > Ledger line. Click a row to open or close it; click this header to sort by name."
                  onClick={() => clickSort("label")}>Task key{arrow("label")}</th>
                {shownCols.map(c => (
                  <th key={c.key} className={`sortable tp-a-${c.fmt === "money" ? "center" : c.align}`} title={c.title} onClick={() => clickSort(c.key)}>
                    {c.label}{arrow(c.key)}
                  </th>
                ))}
              </tr>
              {total && renderRow(total, true)}
            </thead>
            <tbody>{visible.map(r => renderRow(r))}</tbody>
          </table>
        </div>
      )}
    </div>
  )
}
