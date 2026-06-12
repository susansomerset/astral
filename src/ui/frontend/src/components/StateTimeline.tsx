import Time from "./Time"

interface StateEntry {
  to_state?: string
  state?: string
  timestamp?: string
  batch_id?: string
}

interface StateTimelineProps {
  history: StateEntry[]
}

export default function StateTimeline({ history }: StateTimelineProps) {
  if (!history || history.length === 0) {
    return <p style={{ color: "#888", fontSize: 13 }}>No state history recorded.</p>
  }

  // Show most recent first
  const sorted = [...history].reverse()

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
      {sorted.map((entry, i) => {
        const state = entry.to_state || entry.state || "?"
        return (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "6px 0" }}>
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
