import { useState, useMemo, useCallback, useRef, useEffect, useLayoutEffect, type ReactNode, type CSSProperties } from "react"
import { formatCell } from "../lib/fmt"
import { getUiConfig, loadUiConfig } from "../lib/uiConfig"
import { resolveCellTruncateChars, resolveFrozenDataColumns, stickyLeftPx } from "../lib/listTableLayout"
import ListTableTruncatedCell from "./ListTableTruncatedCell"

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Row = Record<string, any>

interface ColumnTypeConfig { align: "left" | "right" | "center"; number_format: string | null }

export interface Column<T = Row> {
  key: string
  label: string
  type?: string                                         // UI_CONFIG column type: "str" | "int" | "float" | "currency" | "date" | "datetime"
  sortable?: boolean                                    // default: true
  defaultDesc?: boolean                                 // if true, default sort for this column is descending
  expandable?: boolean                                  // truncate long text with expand/collapse toggle
  render?: (value: unknown, row: T) => ReactNode
}

export interface BulkAction {
  label: string
  onClick: (selectedIds: string[]) => void
  variant?: "default" | "danger"
}

export interface ListPageProps<T = Row> {
  title: string
  columns: Column<T>[]
  rows: T[]
  idField?: string                                      // default: "id"
  selectable?: boolean                                  // show checkboxes even without bulkActions
  bulkActions?: BulkAction[]
  onSelectionChange?: (selectedRows: T[]) => void       // fires on every selection change with full row objects
  onRowClick?: (row: T) => void
  loading?: boolean
  emptyMessage?: string
  actions?: ReactNode
  rowActions?: (row: T) => ReactNode
  frozenDataColumns?: number                            // per-screen override; omit → UI_CONFIG default
}

const EXPAND_THRESHOLD = 100

// Persist column layout per page title in localStorage
const STORAGE_PREFIX = "listpage:"
function loadLayout(title: string): { order?: string[]; widths?: Record<string, number> } {
  try {
    const raw = localStorage.getItem(STORAGE_PREFIX + title)
    return raw ? JSON.parse(raw) : {}
  } catch { return {} }
}
function saveLayout(title: string, order: string[], widths: Record<string, number>) {
  try {
    localStorage.setItem(STORAGE_PREFIX + title, JSON.stringify({ order, widths }))
  } catch { /* quota exceeded, etc. */ }
}

function ExpandableCell({ text }: { text: string }) {
  const [open, setOpen] = useState(false)
  if (text.length <= EXPAND_THRESHOLD) return <>{text}</>
  return (
    <span>
      {open ? text : text.slice(0, EXPAND_THRESHOLD) + "…"}
      <button
        className="expand-toggle"
        onClick={e => { e.stopPropagation(); setOpen(o => !o) }}
      >
        {open ? "less" : "more"}
      </button>
    </span>
  )
}

type SortDir = "asc" | "desc"
interface SortSpec { key: string; dir: SortDir }

function cmpValues(a: unknown, b: unknown): number {
  const av = a ?? ""
  const bv = b ?? ""
  return String(av).localeCompare(String(bv), undefined, { numeric: true })
}

export default function ListPage<T extends Row>({
  title,
  columns,
  rows,
  idField = "id",
  selectable = false,
  bulkActions = [],
  onSelectionChange,
  onRowClick,
  loading = false,
  emptyMessage = "No records found.",
  actions,
  rowActions,
  frozenDataColumns,
}: ListPageProps<T>) {
  const [filter, setFilter] = useState("")
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [, forceUpdate] = useState(0)

  // Load UI_CONFIG once (module-level cache) — triggers re-render when ready
  useEffect(() => { loadUiConfig(() => forceUpdate(n => n + 1)) }, [])

  const uiConfig = getUiConfig()
  const frozenN = resolveFrozenDataColumns(uiConfig, frozenDataColumns)
  const truncateChars = resolveCellTruncateChars(uiConfig)

  // Column ordering (drag-and-drop reposition) — restored from localStorage
  const colKeys = useMemo(() => columns.map(c => c.key), [columns])
  const [colOrder, setColOrder] = useState<string[]>(() => {
    const saved = loadLayout(title).order
    if (saved && saved.length === colKeys.length && saved.every(k => colKeys.includes(k))) return saved
    return colKeys
  })
  const dragColRef = useRef<string | null>(null)

  // Re-sync colOrder when columns prop changes — layout effect so the header row matches columns before paint (tests and UX).
  useLayoutEffect(() => {
    const saved = loadLayout(title).order
    if (saved && saved.length === colKeys.length && saved.every(k => colKeys.includes(k))) {
      setColOrder(saved)
    } else {
      setColOrder(colKeys)
    }
  }, [colKeys, title])

  const orderedColumns = useMemo(() => {
    const byKey = new Map(columns.map(c => [c.key, c]))
    return colOrder.map(k => byKey.get(k)).filter(Boolean) as Column<T>[]
  }, [columns, colOrder])

  const onColDragStart = useCallback((key: string) => { dragColRef.current = key }, [])
  const onColDrop = useCallback((targetKey: string) => {
    const srcKey = dragColRef.current
    dragColRef.current = null
    if (!srcKey || srcKey === targetKey) return
    setColOrder(prev => {
      const next = [...prev]
      const srcIdx = next.indexOf(srcKey)
      const tgtIdx = next.indexOf(targetKey)
      if (srcIdx === -1 || tgtIdx === -1) return prev
      next.splice(srcIdx, 1)
      next.splice(tgtIdx, 0, srcKey)
      return next
    })
  }, [])

  // Column resizing — restored from localStorage
  const [colWidths, setColWidths] = useState<Record<string, number>>(() => loadLayout(title).widths || {})

  // Persist layout changes to localStorage
  useEffect(() => { saveLayout(title, colOrder, colWidths) }, [title, colOrder, colWidths])
  const dragRef = useRef<{ key: string; startX: number; startW: number } | null>(null)

  const onResizeStart = useCallback((e: React.MouseEvent, key: string, th: HTMLTableCellElement) => {
    e.preventDefault()
    e.stopPropagation()
    dragRef.current = { key, startX: e.clientX, startW: th.offsetWidth }

    const onMove = (ev: MouseEvent) => {
      if (!dragRef.current) return
      const delta = ev.clientX - dragRef.current.startX
      const newW = Math.max(40, dragRef.current.startW + delta)
      setColWidths(prev => ({ ...prev, [dragRef.current!.key]: newW }))
    }
    const onUp = () => {
      dragRef.current = null
      document.removeEventListener("mousemove", onMove)
      document.removeEventListener("mouseup", onUp)
    }
    document.addEventListener("mousemove", onMove)
    document.addEventListener("mouseup", onUp)
  }, [])

  // Default sort: all sortable columns in order, each using its defaultDesc flag
  const defaultSort = useMemo<SortSpec[]>(() =>
    columns
      .filter(c => c.sortable !== false)
      .map(c => ({ key: c.key, dir: c.defaultDesc ? "desc" : "asc" })),
    [columns]
  )

  // User-clicked sort (single column) overrides the default multi-column sort
  const [userSort, setUserSort] = useState<SortSpec | null>(null)

  const activeSorts = useMemo<SortSpec[]>(() => {
    if (!userSort) return defaultSort
    return [userSort]
  }, [userSort, defaultSort])

  const getId = (row: T): string => String(row[idField])

  // Notify parent whenever selection changes
  function notifySelection(next: Set<string>) {
    if (onSelectionChange) {
      const selectedRows = rows.filter(r => next.has(getId(r)))
      onSelectionChange(selectedRows)
    }
  }

  const filtered = useMemo(() => {
    if (!filter) return rows
    const q = filter.toLowerCase()
    return rows.filter(row =>
      columns.some(col => {
        const val = row[col.key]
        return val != null && String(val).toLowerCase().includes(q)
      })
    )
  }, [rows, filter, columns])

  const sorted = useMemo(() => {
    if (activeSorts.length === 0) return filtered
    return [...filtered].sort((a, b) => {
      for (const { key, dir } of activeSorts) {
        const cmp = cmpValues(a[key], b[key])
        if (cmp !== 0) return dir === "asc" ? cmp : -cmp
      }
      return 0
    })
  }, [filtered, activeSorts])

  function handleSort(key: string) {
    if (userSort?.key === key) {
      setUserSort({ key, dir: userSort.dir === "asc" ? "desc" : "asc" })
    } else {
      const col = columns.find(c => c.key === key)
      setUserSort({ key, dir: col?.defaultDesc ? "desc" : "asc" })
    }
  }

  function toggleRow(id: string) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      notifySelection(next)
      return next
    })
  }

  function toggleAll() {
    if (selected.size === sorted.length) {
      notifySelection(new Set())
      setSelected(new Set())
    } else {
      const next = new Set(sorted.map(getId))
      notifySelection(next)
      setSelected(next)
    }
  }

  // Clean up drag listeners on unmount
  useEffect(() => {
    return () => { dragRef.current = null }
  }, [])

  const selectedArr = Array.from(selected)
  const hasBulk = bulkActions.length > 0
  const showCheckboxes = selectable || hasBulk
  const primarySortKey = userSort?.key ?? null

  function colTypeConfig(col: Column<T>): ColumnTypeConfig | null {
    if (!col.type || !uiConfig) return null
    return uiConfig.column_types[col.type] ?? null
  }

  function colAlign(col: Column<T>): CSSProperties | undefined {
    const cfg = colTypeConfig(col)
    return cfg ? { textAlign: cfg.align } : undefined
  }

  function frozenCellStyle(dataColIndex: number | null, base: CSSProperties): CSSProperties {
    if (dataColIndex == null) return base
    const left = stickyLeftPx(dataColIndex, colWidths, colOrder, showCheckboxes, frozenN)
    if (left == null) return base
    return { ...base, left }
  }

  function renderCellContent(col: Column<T>, raw: unknown, row: T): ReactNode {
    if (col.render) {
      const rendered = col.render(raw, row)
      if (typeof rendered === "string" && rendered.length > truncateChars) {
        return <ListTableTruncatedCell text={rendered} maxChars={truncateChars} />
      }
      return rendered
    }
    if (col.expandable) return <ExpandableCell text={String(raw ?? "")} />
    const cfg = colTypeConfig(col)
    const text = cfg ? formatCell(raw, cfg.number_format) : String(raw ?? "")
    return <ListTableTruncatedCell text={text} maxChars={truncateChars} />
  }

  return (
    <div className="list-page">
      <div className="list-page-header">
        <h1 className="list-page-title">{title}</h1>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {actions}
          <input
            className="list-page-search"
            type="text"
            placeholder="Search..."
            value={filter}
            onChange={e => setFilter(e.target.value)}
          />
        </div>
      </div>

      {selectedArr.length > 0 && hasBulk && (
        <div className="list-page-bulk-bar">
          <span>{selectedArr.length} selected</span>
          {bulkActions.map(action => (
            <button
              key={action.label}
              className={`list-page-bulk-btn${action.variant === "danger" ? " danger" : ""}`}
              onClick={() => action.onClick(selectedArr)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <p className="list-page-status">Loading...</p>
      ) : sorted.length === 0 ? (
        <p className="list-page-status">{emptyMessage}</p>
      ) : (
        <div className="list-page-table-wrap list-page-table-wrap--scroll">
          <table className="list-page-table">
            <thead>
              <tr>
                {showCheckboxes && (
                  <th className="list-page-check-col list-table-cell-frozen" style={{ left: 0 }}>
                    <input
                      type="checkbox"
                      checked={selected.size === sorted.length && sorted.length > 0}
                      onChange={toggleAll}
                    />
                  </th>
                )}
                {orderedColumns.map((col, i) => {
                  const frozen = i < frozenN
                  const thStyle = frozenCellStyle(i, {
                    ...colAlign(col),
                    ...(colWidths[col.key] ? { width: colWidths[col.key] } : {}),
                  })
                  return (
                  <th
                    key={col.key}
                    className={`${col.sortable !== false ? "sortable" : ""}${frozen ? " list-table-cell-frozen" : ""}`.trim()}
                    style={Object.keys(thStyle).length ? thStyle : undefined}
                    onClick={() => col.sortable !== false && handleSort(col.key)}
                    draggable
                    onDragStart={() => onColDragStart(col.key)}
                    onDragOver={e => e.preventDefault()}
                    onDrop={() => onColDrop(col.key)}
                  >
                    {col.label}
                    {primarySortKey === col.key && (userSort!.dir === "asc" ? " ▲" : " ▼")}
                    <span
                      className="col-resize-handle"
                      onMouseDown={e => {
                        const th = e.currentTarget.parentElement as HTMLTableCellElement
                        onResizeStart(e, col.key, th)
                      }}
                    />
                  </th>
                  )
                })}
                {rowActions && <th className="list-table-cell-frozen-right" />}
              </tr>
            </thead>
            <tbody>
              {sorted.map(row => {
                const id = getId(row)
                return (
                  <tr
                    key={id}
                    className={onRowClick ? "clickable" : ""}
                    onClick={() => onRowClick?.(row)}
                  >
                    {showCheckboxes && (
                      <td className="list-page-check-col list-table-cell-frozen" style={{ left: 0 }} onClick={e => e.stopPropagation()}>
                        <input
                          type="checkbox"
                          checked={selected.has(id)}
                          onChange={() => toggleRow(id)}
                        />
                      </td>
                    )}
                    {orderedColumns.map((col, i) => {
                      const frozen = i < frozenN
                      const tdStyle = frozenCellStyle(i, {
                        ...colAlign(col),
                        ...(colWidths[col.key] ? { width: colWidths[col.key] } : {}),
                      })
                      return (
                        <td
                          key={col.key}
                          className={frozen ? "list-table-cell-frozen" : undefined}
                          style={Object.keys(tdStyle).length ? tdStyle : undefined}
                        >
                          {renderCellContent(col, row[col.key], row)}
                        </td>
                      )
                    })}
                    {rowActions && (
                      <td className="list-page-row-actions list-table-cell-frozen-right" onClick={e => e.stopPropagation()}>
                        {rowActions(row)}
                      </td>
                    )}
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
