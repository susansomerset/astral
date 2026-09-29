import type { KeyboardEvent } from "react"
import Time from "./Time"

export interface StateEntry {
  to_state?: string
  state?: string
  timestamp?: string
  batch_id?: string
  run_id?: string
}

/** Run that produced this row: AST-1864 run_id, else legacy batch_id; "" when neither (not clickable). */
function entryRunId(entry: StateEntry): string {
  return entry.run_id || entry.batch_id || ""
}

interface StateTimelineProps {
  history: StateEntry[]
  onSelectRun?: (runId: string) => void
}

export default function StateTimeline({ history, onSelectRun }: StateTimelineProps) {
  if (!history || history.length === 0) {
    return <p style={{ color: "#888", fontSize: 13 }}>No state history recorded.</p>
  }

  // Show most recent first
  const sorted = [...history].reverse()

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
      {sorted.map((entry, i) => {
        const state = entry.to_state || entry.state || "?"
        // Clickable only when the caller opts in AND the row resolves a run id (AST-1865)
        const runId = onSelectRun ? entryRunId(entry) : ""
        const clickProps = runId ? {
          role: "button",
          tabIndex: 0,
          title: `Open run ${runId}`,
          onClick: () => onSelectRun!(runId),
          onKeyDown: (e: KeyboardEvent<HTMLDivElement>) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              onSelectRun!(runId)
            }
          },
        } : {}
        return (
          <div
            key={i}
            style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "6px 0", ...(runId ? { cursor: "pointer" } : {}) }}
            {...clickProps}
          >
            <div style={{
              display: "flex", flexDirection: "column", alignItems: "center", minWidth: 20,
            }}>
              <div style={{
                width: 10, height: 10, borderRadius: "50%",
                background: i === 0 ? "var(--accent, #5b8cff)" : "#555",
                border: i === 0 ? "2px solid var(--accent, #5b8cff)" : "2px solid #666",
              }} />
              {i < sorted.length - 1 && (
                <div style={{ width: 2, height: 24, background: "#444" }} />
              )}
            </div>
            <div style={{ fontSize: 13, lineHeight: 1.4 }}>
              <span style={{ fontWeight: 600, color: "#e0e0e0" }}>{state}</span>
              <span style={{ color: "#888", marginLeft: 8 }}><Time value={entry.timestamp} /></span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
