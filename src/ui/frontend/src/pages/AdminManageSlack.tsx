import { useCallback, useEffect, useState } from "react"
import Toast, { type ToastMessage } from "../components/Toast"
import api from "../lib/api"

type ListenState = {
  listen_enabled: boolean
  environment: string
  is_production: boolean
}

export default function AdminManageSlack() {
  const [state, setState] = useState<ListenState | null>(null)
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
        const r = await api("/api/admin/contact/listen")
        const data = await r.json().catch(() => ({} as Record<string, unknown>))
        if (!r.ok) {
          const msg =
            (typeof data.error === "string" && data.error) || `HTTP ${r.status}`
          if (!cancelled) {
            setError(msg)
            setToast({ text: msg, variant: "error" })
          }
          return
        }
        if (!cancelled) {
          setState({
            listen_enabled: Boolean(data.listen_enabled),
            environment: typeof data.environment === "string" ? data.environment : "",
            is_production: Boolean(data.is_production),
          })
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
        <div style={{ maxWidth: 480 }}>
          <p style={{ margin: "0 0 8px", fontSize: 14, color: "var(--text-secondary)" }}>
            Environment: <strong style={{ color: "var(--text-primary)" }}>{state.environment || "—"}</strong>
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
      )}
      {toast && <Toast message={toast} onDone={clearToast} />}
    </div>
  )
}
