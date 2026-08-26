import { useCallback, useEffect, useState, type ReactNode } from "react"
import api from "../lib/api"
import Modal from "./Modal"
import { useUserConfirm } from "./UserPrompt"

type TableKey = "agent" | "agent_task"

interface TableStatus {
  diverged: boolean
  repo_relative_path: string
}

type CompareFieldChange = {
  field: string
  file_value: unknown
  database_value: unknown
}

type CompareChangedRow = {
  row_key: string
  fields: CompareFieldChange[]
}

type ComparePayload = {
  table_key: string
  diverged: boolean
  repo_relative_path: string
  only_in_database: Record<string, unknown>[]
  only_in_file: Record<string, unknown>[]
  changed_rows: CompareChangedRow[]
}

const COPY: Record<TableKey, { label: string; revertNoun: string }> = {
  agent: {
    label: "agent personas",
    revertNoun: "agents",
  },
  agent_task: {
    label: "task prompts",
    revertNoun: "task prompts",
  },
}

const ROW_KEY_FIELD: Record<TableKey, string> = {
  agent: "agent_id",
  agent_task: "task_key",
}

function rowLabel(row: Record<string, unknown>, tableKey: TableKey): string {
  const col = ROW_KEY_FIELD[tableKey]
  const v = row[col]
  return typeof v === "string" && v ? v : String(v ?? "(missing key)")
}

function formatCellValue(value: unknown): string {
  if (value === null || value === undefined) return "—"
  if (typeof value === "string") return value
  return JSON.stringify(value)
}

function diffCellContent(value: unknown): ReactNode {
  const text = formatCellValue(value)
  if (text.length > 120) {
    return (
      <pre style={{ maxHeight: "8em", overflow: "auto", margin: 0, whiteSpace: "pre-wrap" }}>
        {text}
      </pre>
    )
  }
  return text
}

export default function RepoJsonDivergenceBanner({
  tableKey,
  refreshToken = 0,
  onReverted,
}: {
  tableKey: TableKey
  refreshToken?: number
  onReverted?: () => void
}) {
  const confirm = useUserConfirm()
  const [status, setStatus] = useState<TableStatus | null>(null)
  const [reverting, setReverting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [diffOpen, setDiffOpen] = useState(false)
  const [diffLoading, setDiffLoading] = useState(false)
  const [diffError, setDiffError] = useState<string | null>(null)
  const [diffData, setDiffData] = useState<ComparePayload | null>(null)

  const fetchStatus = useCallback(() => {
    api("/api/admin/repo_json/status")
      .then(async r => {
        const data = await r.json()
        if (!r.ok) throw new Error(typeof data.error === "string" ? data.error : "Status check failed")
        const row = data[tableKey]
        if (!row || typeof row.diverged !== "boolean") throw new Error("Invalid status response")
        setStatus(row)
        setError(null)
      })
      .catch(e => {
        setStatus(null)
        setError(e instanceof Error ? e.message : "Status check failed")
      })
  }, [tableKey])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus, refreshToken])

  async function openDiff() {
    setDiffOpen(true)
    setDiffLoading(true)
    setDiffError(null)
    setDiffData(null)
    try {
      const r = await api(`/api/admin/repo_json/compare/${tableKey}`)
      const data = await r.json()
      if (!r.ok) throw new Error(typeof data.error === "string" ? data.error : "Comparison failed")
      setDiffData(data as ComparePayload)
      setDiffError(null)
    } catch (e) {
      setDiffError(e instanceof Error ? e.message : "Comparison failed")
    } finally {
      setDiffLoading(false)
    }
  }

  async function handleRevert() {
    const meta = COPY[tableKey]
    const ok = await confirm(
      `Restore ${meta.revertNoun} in the database from the checked-in repo JSON file? Unsaved local edits will be lost.`,
      {
        title: "Revert to file",
        confirmLabel: "Revert to file",
        cancelLabel: "Cancel",
        variant: "danger",
      },
    )
    if (!ok) return
    setReverting(true)
    setError(null)
    try {
      const r = await api(`/api/admin/repo_json/revert/${tableKey}`, { method: "POST" })
      const data = await r.json()
      if (!r.ok) throw new Error(typeof data.error === "string" ? data.error : "Revert failed")
      fetchStatus()
      onReverted?.()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Revert failed")
    } finally {
      setReverting(false)
    }
  }

  if (error && !status?.diverged) {
    return (
      <div style={{ marginBottom: 12, padding: 12, borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--error, #f87171)" }}>
        <span style={{ color: "var(--error, #f87171)", fontSize: 13 }}>{error}</span>
      </div>
    )
  }

  if (!status?.diverged) return null

  const path = status.repo_relative_path || COPY[tableKey].label
  const meta = COPY[tableKey]
  return (
    <>
      <div style={{ marginBottom: 12, padding: 12, borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--accent-gold)" }}>
        <span style={{ color: "var(--accent-gold)", fontSize: 13 }}>
          Local <strong>{meta.label}</strong> in the database differ from <code>{path}</code>.
          {" "}Use <strong>Show Differences</strong> to inspect drift,{" "}
          <strong>Update file with table version</strong> to write the live table to the repo JSON file, or{" "}
          <strong>Revert to file</strong> to restore the database from the checked-in file.
        </span>
        <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <button
            type="button"
            className="btn secondary"
            disabled={reverting}
            onClick={() => void openDiff()}
          >
            Show Differences
          </button>
          <button
            type="button"
            className="btn secondary"
            disabled={reverting}
            onClick={() => void handleRevert()}
          >
            {reverting ? "Reverting…" : "Revert to file"}
          </button>
          {error ? (
            <span style={{ color: "var(--error, #f87171)", fontSize: 12 }}>{error}</span>
          ) : null}
        </div>
      </div>

      <Modal
        open={diffOpen}
        onClose={() => setDiffOpen(false)}
        title={`Differences — ${meta.label}`}
        showFooter={false}
        size="wide"
      >
        {diffLoading ? (
          <p style={{ fontSize: 13 }}>Loading comparison…</p>
        ) : diffError ? (
          <p style={{ color: "var(--error, #f87171)", fontSize: 13 }}>{diffError}</p>
        ) : diffData ? (
          <div style={{ fontSize: 13 }}>
            <h3 style={{ fontSize: 14, marginTop: 0 }}>Rows only in database</h3>
            {diffData.only_in_database.length === 0 ? (
              <p>(none)</p>
            ) : (
              <ul>
                {diffData.only_in_database.map(row => (
                  <li key={rowLabel(row, tableKey)}>{rowLabel(row, tableKey)}</li>
                ))}
              </ul>
            )}

            <h3 style={{ fontSize: 14 }}>Rows only in file</h3>
            {diffData.only_in_file.length === 0 ? (
              <p>(none)</p>
            ) : (
              <ul>
                {diffData.only_in_file.map(row => (
                  <li key={rowLabel(row, tableKey)}>{rowLabel(row, tableKey)}</li>
                ))}
              </ul>
            )}

            <h3 style={{ fontSize: 14 }}>Changed fields</h3>
            {diffData.changed_rows.length === 0 ? (
              <p>(none)</p>
            ) : (
              diffData.changed_rows.map(row => (
                <div key={row.row_key} style={{ marginBottom: 16 }}>
                  <h4 style={{ fontSize: 13, marginBottom: 8 }}>Row: {row.row_key}</h4>
                  <table className="list-page-table" style={{ width: "100%", fontSize: 13 }}>
                    <thead>
                      <tr>
                        <th>Field</th>
                        <th>File</th>
                        <th>Database</th>
                      </tr>
                    </thead>
                    <tbody>
                      {row.fields.map(field => (
                        <tr key={field.field}>
                          <td>{field.field}</td>
                          <td>{diffCellContent(field.file_value)}</td>
                          <td>{diffCellContent(field.database_value)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))
            )}
          </div>
        ) : (
          <p style={{ fontSize: 13 }}>(no differences reported)</p>
        )}
      </Modal>
    </>
  )
}
