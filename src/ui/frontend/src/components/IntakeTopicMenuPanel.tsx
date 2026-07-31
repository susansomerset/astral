import { useCallback, useEffect, useState } from "react"
import Toast, { type ToastMessage } from "./Toast"
import api from "../lib/api"

type TopicMenuUi = {
  panel_title: string
  accept_label: string
  send_label: string
  placeholder: string
  generating_label: string
  done_title: string
}

type TopicRow = {
  id: string
  name: string
  ask: string
  required: boolean
  informs: string[]
  status: string
}

type IntakeTopicMenuPanelProps = {
  candidateId: string
  onDone: () => void
  onCancel: () => void
}

const DEFAULT_UI: TopicMenuUi = {
  panel_title: "Confirm preamble with Estelle",
  accept_label: "Looks good — generate Topic Menu",
  send_label: "Send to Estelle",
  placeholder: "Tell Estelle what to change, or accept below.",
  generating_label: "Estelle is building your Topic Menu…",
  done_title: "Topic Menu ready",
}

export default function IntakeTopicMenuPanel({
  candidateId,
  onDone,
  onCancel,
}: IntakeTopicMenuPanelProps) {
  const [ui, setUi] = useState<TopicMenuUi>(DEFAULT_UI)
  const [assistantMessage, setAssistantMessage] = useState("")
  const [draft, setDraft] = useState("")
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [topics, setTopics] = useState<TopicRow[] | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)

  const clearToast = useCallback(() => setToast(null), [])

  const postConfirm = useCallback(
    async (message?: string) => {
      const body =
        message !== undefined && message !== ""
          ? JSON.stringify({ message })
          : JSON.stringify({})
      const r = await api(`/api/candidates/${candidateId}/topic-menu/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      })
      const data = await r.json().catch(() => ({}))
      if (!r.ok) {
        throw new Error((data as { error?: string }).error ?? "Confirm failed")
      }
      return data as {
        outcome: string
        assistant_message: string
      }
    },
    [candidateId],
  )

  const postGenerate = useCallback(async () => {
    setGenerating(true)
    try {
      const r = await api(`/api/candidates/${candidateId}/topic-menu/generate`, {
        method: "POST",
      })
      const data = await r.json().catch(() => ({}))
      if (!r.ok) {
        throw new Error((data as { error?: string }).error ?? "Generate failed")
      }
      const menu = (data as { menu?: { topics?: TopicRow[] } }).menu
      setTopics(Array.isArray(menu?.topics) ? menu!.topics! : [])
    } finally {
      setGenerating(false)
    }
  }, [candidateId])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api("/api/ui_config")
      .then(r => {
        if (!r.ok) throw new Error("Failed to load ui_config")
        return r.json()
      })
      .then(cfg => {
        if (cancelled) return
        const copy = cfg?.topic_menu_gen?.ui as Partial<TopicMenuUi> | undefined
        if (copy && typeof copy === "object") {
          setUi({ ...DEFAULT_UI, ...copy })
        }
      })
      .catch(e => {
        if (cancelled) return
        setToast({
          text: e instanceof Error ? e.message : "Failed to load Topic Menu config",
          variant: "error",
        })
      })
      .finally(async () => {
        if (cancelled) return
        try {
          const data = await postConfirm()
          if (cancelled) return
          setAssistantMessage(data.assistant_message || "")
        } catch (e) {
          if (cancelled) return
          setToast({
            text: e instanceof Error ? e.message : "Confirm failed",
            variant: "error",
          })
        } finally {
          if (!cancelled) setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [postConfirm])

  const handleSend = useCallback(async () => {
    if (busy || generating || topics) return
    const message = draft.trim()
    if (!message) return
    setBusy(true)
    try {
      const data = await postConfirm(message)
      setAssistantMessage(data.assistant_message || "")
      setDraft("")
      if (data.outcome === "accepted") {
        await postGenerate()
      }
    } catch (e) {
      setToast({
        text: e instanceof Error ? e.message : "Confirm failed",
        variant: "error",
      })
    } finally {
      setBusy(false)
    }
  }, [busy, generating, topics, draft, postConfirm, postGenerate])

  const handleAccept = useCallback(async () => {
    if (busy || generating || topics) return
    setBusy(true)
    try {
      const data = await postConfirm("Looks good — nothing to change.")
      setAssistantMessage(data.assistant_message || "")
      if (data.outcome !== "accepted") {
        return
      }
      await postGenerate()
    } catch (e) {
      setToast({
        text: e instanceof Error ? e.message : "Topic Menu failed",
        variant: "error",
      })
    } finally {
      setBusy(false)
    }
  }, [busy, generating, topics, postConfirm, postGenerate])

  if (loading) {
    return (
      <>
        <div className="intake-topic-menu-panel">
          <p className="intake-hold">Loading…</p>
        </div>
        <Toast message={toast} onDone={clearToast} />
      </>
    )
  }

  if (topics) {
    return (
      <>
        <div className="intake-topic-menu-panel">
          <h3 className="intake-topic-menu-title">{ui.done_title}</h3>
          <ul className="intake-topic-menu-list">
            {topics.map(t => (
              <li key={t.id}>
                <strong>{t.name}</strong>
                {t.required ? " (required)" : ""}
                {Array.isArray(t.informs) && t.informs.length > 0
                  ? ` — informs: ${t.informs.join(", ")}`
                  : ""}
              </li>
            ))}
          </ul>
          <div className="intake-topic-menu-actions">
            <button type="button" className="modal-btn save" onClick={onDone}>
              Done
            </button>
          </div>
        </div>
        <Toast message={toast} onDone={clearToast} />
      </>
    )
  }

  return (
    <>
      <div className="intake-topic-menu-panel">
        <h3 className="intake-topic-menu-title">{ui.panel_title}</h3>
        <div className="intake-thread">
          {assistantMessage ? (
            <div className="intake-msg intake-msg--assistant">{assistantMessage}</div>
          ) : null}
          {generating ? (
            <div className="intake-msg intake-msg--assistant">{ui.generating_label}</div>
          ) : null}
        </div>
        <textarea
          className="intake-topic-menu-input"
          value={draft}
          disabled={busy || generating}
          placeholder={ui.placeholder}
          onChange={e => setDraft(e.target.value)}
          rows={4}
        />
        <div className="intake-topic-menu-actions">
          <button type="button" className="modal-btn cancel" disabled={busy || generating} onClick={onCancel}>
            Cancel
          </button>
          <button
            type="button"
            className="modal-btn cancel"
            disabled={busy || generating || !draft.trim()}
            onClick={() => void handleSend()}
          >
            {ui.send_label}
          </button>
          <button
            type="button"
            className="modal-btn save"
            disabled={busy || generating}
            onClick={() => void handleAccept()}
          >
            {ui.accept_label}
          </button>
        </div>
      </div>
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
