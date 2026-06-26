import type { LogOffReason } from "../lib/sessionAuthMark"
import { clearSessionAuthMarks } from "../lib/sessionAuthMark"

const COPY: Record<LogOffReason, { title: string; body: string }> = {
  timeout: {
    title: "You were signed out",
    body: "Your session expired after a period of inactivity. Refresh the page to sign in again and return to Astral.",
  },
  "server-rejection": {
    title: "Your session is no longer valid",
    body: "The server rejected your request while you were using the app. Refresh the page to sign in again and return to Astral.",
  },
}

export default function LogOffScreen({ reason }: { reason: LogOffReason }) {
  const { title, body } = COPY[reason]

  function handleRefresh() {
    clearSessionAuthMarks()
    window.location.reload()
  }

  return (
    <div
      className="content"
      style={{ display: "flex", justifyContent: "center", padding: "2rem" }}
      data-testid="logoff-screen"
    >
      <div style={{ maxWidth: "28rem", textAlign: "center" }}>
        <h1 style={{ marginBottom: "1rem" }}>{title}</h1>
        <p style={{ marginBottom: "1.5rem", color: "var(--text-secondary)" }}>{body}</p>
        <button type="button" onClick={handleRefresh} data-testid="logoff-refresh">
          Refresh
        </button>
      </div>
    </div>
  )
}
