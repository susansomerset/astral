import { useCallback, useEffect, useState } from "react"
import api from "../lib/api"
import { useUserConfirm } from "./UserPrompt"

type TableKey = "agent" | "agent_task"

interface TableStatus {
  diverged: boolean
  repo_relative_path: string
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
    <div style={{ marginBottom: 12, padding: 12, borderRadius: 4, background: "var(--bg-card)", border: "1px solid var(--accent-gold)" }}>
      <span style={{ color: "var(--accent-gold)", fontSize: 13 }}>
        Local <strong>{meta.label}</strong> in the database differ from <code>{path}</code>.
        {" "}Changes will be overwritten on the next server restart or deploy unless you run{" "}
        <code>python3 scripts/export_repo_admin_json.py</code> and commit the updated JSON.
      </span>
      <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center" }}>
        <button
          type="button"
          className="dep-btn cancel"
          disabled={reverting}
          onClick={() => void handleRevert()}
          style={{ fontSize: 12, padding: "4px 12px" }}
        >
          {reverting ? "Reverting…" : "Revert to file"}
        </button>
        {error ? (
          <span style={{ color: "var(--error, #f87171)", fontSize: 12 }}>{error}</span>
        ) : null}
      </div>
    </div>
  )
}
