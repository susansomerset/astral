import { useCallback, useEffect, useState } from "react"
import Toast, { type ToastMessage } from "../components/Toast"
import api from "../lib/api"

type ListenState = {
  listen_enabled: boolean
  environment: string
  is_production: boolean
}

type EstelleActivityRow = {
  slack_user_id: string
  slack_username: string | null
  slack_display_name: string | null
  bind_ok: boolean
  astral_candidate_id: string | null
  candidate_state: string | null
  inbound_message_count: number
  last_channel: string | null
  last_message_ts: string | null
}

export default function AdminManageSlack() {
  const [state, setState] = useState<ListenState | null>(null)
  const [activity, setActivity] = useState<EstelleActivityRow[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const [listenRes, activityRes] = await Promise.all([
          api("/api/admin/contact/listen"),
          api("/api/admin/contact/estelle_activity"),
        ])
        const listenData = await listenRes.json().catch(() => ({} as Record<string, unknown>))
        if (!listenRes.ok) {
          const msg =
            (typeof listenData.error === "string" && listenData.error) ||
            `HTTP ${listenRes.status}`
          if (!cancelled) {
            setError(msg)
            setToast({ text: msg, variant: "error" })
          }
          return
        }
        if (!cancelled) {
          setState({
            listen_enabled: Boolean(listenData.listen_enabled),
            environment:
              typeof listenData.environment === "string" ? listenData.environment : "",
            is_production: Boolean(listenData.is_production),
          })
        }
        // Activity load failure toasts but does not block listen controls.
        const activityData = await activityRes.json().catch(() => ({} as Record<string, unknown>))
        if (!activityRes.ok) {
          const msg =
            (typeof activityData.error === "string" && activityData.error) ||
            `HTTP ${activityRes.status}`
          if (!cancelled) {
            setToast({ text: msg, variant: "error" })
            setActivity([])
          }
        } else if (!cancelled) {
          const users = Array.isArray(activityData.users) ? activityData.users : []
          setActivity(
            users.map((u: Record<string, unknown>) => ({
              slack_user_id: typeof u.slack_user_id === "string" ? u.slack_user_id : "",
              slack_username:
                typeof u.slack_username === "string" ? u.slack_username : null,
              slack_display_name:
                typeof u.slack_display_name === "string" ? u.slack_display_name : null,
              bind_ok: Boolean(u.bind_ok),
              astral_candidate_id:
                typeof u.astral_candidate_id === "string" ? u.astral_candidate_id : null,
              candidate_state:
                typeof u.candidate_state === "string" ? u.candidate_state : null,
              inbound_message_count:
                typeof u.inbound_message_count === "number" ? u.inbound_message_count : 0,
              last_channel: typeof u.last_channel === "string" ? u.last_channel : null,
              last_message_ts:
                typeof u.last_message_ts === "string" ? u.last_message_ts : null,
            })).filter((r: EstelleActivityRow) => r.slack_user_id),
          )
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Failed to load listen state"
        if (!cancelled) {
          setError(msg)
          setToast({ text: msg, variant: "error" })
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  async function toggleListen() {
    if (!state || busy) return
    const next = !state.listen_enabled
    setBusy(true)
    try {
      const r = await api("/api/admin/contact/listen", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ listen_enabled: next }),
      })
      const data = await r.json().catch(() => ({} as Record<string, unknown>))
      if (!r.ok) {
        const msg =
          (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
        setToast({ text: msg, variant: "error" })
        return
      }
      setState({
        listen_enabled: Boolean(data.listen_enabled),
        environment: typeof data.environment === "string" ? data.environment : state.environment,
        is_production: Boolean(data.is_production),
      })
      setToast({
        text: next ? "Slack listen enabled" : "Slack listen disabled",
        variant: "success",
      })
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to update listen"
      setToast({ text: msg, variant: "error" })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ margin: "0 0 16px", fontSize: 22, color: "var(--text-primary)" }}>
        Manage Slack
      </h1>
      {loading && <p>Loading…</p>}
      {error && !loading && (
        <p style={{ color: "var(--danger)", fontSize: 13 }}>{error}</p>
      )}
      {!loading && !error && state && (
        <>
          <div style={{ maxWidth: 480 }}>
            <p style={{ margin: "0 0 8px", fontSize: 14, color: "var(--text-secondary)" }}>
              Environment:{" "}
              <strong style={{ color: "var(--text-primary)" }}>{state.environment || "—"}</strong>
            </p>
            <p style={{ margin: "0 0 16px", fontSize: 14, color: "var(--text-secondary)" }}>
              Listen:{" "}
              <strong style={{ color: "var(--text-primary)" }}>
                {state.listen_enabled ? "On" : "Off"}
              </strong>
            </p>
            {state.is_production ? (
              <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--text-secondary)" }}>
                Production — replies are not prefixed.
              </p>
            ) : (
              <p style={{ margin: "0 0 16px", fontSize: 13, color: "var(--text-secondary)" }}>
                Non-production — replies are prefixed with [{state.environment}]{" "}
              </p>
            )}
            <button
              type="button"
              disabled={busy}
              onClick={() => void toggleListen()}
              style={{
                padding: "8px 14px",
                fontSize: 14,
                cursor: busy ? "wait" : "pointer",
              }}
            >
              {state.listen_enabled ? "Disable listen" : "Enable listen"}
            </button>
          </div>
          <h2 style={{ margin: "32px 0 12px", fontSize: 16, color: "var(--text-primary)" }}>
            @Estelle users
          </h2>
          <div className="list-page-table-wrap">
            <table className="list-page-table">
              <thead>
                <tr>
                  <th>Slack user</th>
                  <th>Username</th>
                  <th>Display</th>
                  <th>Bind</th>
                  <th>Candidate</th>
                  <th>Messages</th>
                  <th>Last channel</th>
                  <th>Last ts</th>
                </tr>
              </thead>
              <tbody>
                {activity.map(row => (
                  <tr key={row.slack_user_id}>
                    <td>{row.slack_user_id}</td>
                    <td>{row.slack_username || "—"}</td>
                    <td>{row.slack_display_name || "—"}</td>
                    <td>{row.bind_ok ? "ok" : "fail"}</td>
                    <td>{row.astral_candidate_id || "—"}</td>
                    <td>{row.inbound_message_count}</td>
                    <td>{row.last_channel || "—"}</td>
                    <td>{row.last_message_ts || "—"}</td>
                  </tr>
                ))}
                {activity.length === 0 && (
                  <tr>
                    <td colSpan={8}>No @Estelle users recorded yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
      {toast && <Toast message={toast} onDone={clearToast} />}
    </div>
  )
}
