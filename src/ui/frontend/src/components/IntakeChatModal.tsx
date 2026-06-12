import { useCallback, useEffect, useRef, useState } from "react"
import Modal from "./Modal"
import Toast, { type ToastMessage } from "./Toast"
import { useUserConfirm } from "./UserPrompt"
import api from "../lib/api"

export type IntakeTurnMode = "initiate_candidate" | "candidate_response" | "build_request"

export interface IntakeChatMessage {
  role: "user" | "assistant"
  content: string
  mode?: IntakeTurnMode
}

/** AST-558 session DTO — UI maps transcript[].text → display content. */
export interface IntakeTranscriptEntry {
  role: "user" | "assistant"
  text: string
  mode?: IntakeTurnMode
  ready_to_build?: boolean
}

export interface IntakeSessionDto {
  session_id: string
  status: string
  transcript: IntakeTranscriptEntry[]
  ready_to_build: boolean
  can_build: boolean
  build_completed: boolean
  awaiting_agent?: boolean
}

export interface IntakeSourceMaterials {
  starting_resume_text: string
  sample_cover_text: string
  linkedin_profile_text: string
}

const INTAKE_HOLD_COPY = "One moment while we review your details before we begin…"

function isHiddenTranscriptEntry(entry: IntakeTranscriptEntry): boolean {
  return entry.role === "user" && entry.mode === "initiate_candidate"
}

function transcriptToMessages(transcript: IntakeTranscriptEntry[]): IntakeChatMessage[] {
  return transcript
    .filter(entry => !isHiddenTranscriptEntry(entry))
    .map(entry => ({
      role: entry.role,
      content: entry.text,
      mode: entry.mode,
    }))
}

function applySessionDto(
  dto: IntakeSessionDto,
  setSessionId: (id: string | null) => void,
  setMessages: (m: IntakeChatMessage[]) => void,
  setReadyToBuild: (b: boolean) => void,
  setBuildCompleted: (b: boolean) => void,
) {
  setSessionId(dto.session_id)
  setMessages(transcriptToMessages(dto.transcript))
  setReadyToBuild(dto.can_build)
  setBuildCompleted(dto.build_completed)
}

export interface IntakeChatModalProps {
  open: boolean
  onClose: () => void
  candidateId: string
  /** Persisted candidate context — sent in session POST body (no modal PUT). */
  materials: IntakeSourceMaterials
  /** When true and no active session, auto POST create after active GET completes. */
  autoStart?: boolean
  /** After parent archived active session — always POST create; do not resume stale active GET. */
  freshStart?: boolean
}

export default function IntakeChatModal({
  open,
  onClose,
  candidateId,
  materials,
  autoStart = false,
  freshStart = false,
}: IntakeChatModalProps) {
  const confirm = useUserConfirm()
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<IntakeChatMessage[]>([])
  const [readyToBuild, setReadyToBuild] = useState(false)
  const [buildCompleted, setBuildCompleted] = useState(false)
  const [draft, setDraft] = useState("")
  const [busy, setBusy] = useState(false)
  const [starting, setStarting] = useState(false)
  const [activeLoaded, setActiveLoaded] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const threadRef = useRef<HTMLDivElement | null>(null)
  const autoStartAttempted = useRef(false)
  const mountedRef = useRef(true)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const clearToast = useCallback(() => setToast(null), [])
  const hasSession = sessionId !== null

  const sessionCreateBody = useCallback(
    () => ({
      starting_resume_text: materials.starting_resume_text,
      sample_cover_text: materials.sample_cover_text,
      linkedin_profile_text: materials.linkedin_profile_text,
    }),
    [materials],
  )

  const createSession = useCallback(async () => {
    const r = await api(`/api/candidates/${candidateId}/intake/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sessionCreateBody()),
    })
    if (!r.ok) {
      const e = await r.json().catch(() => ({}))
      throw new Error((e as { error?: string }).error ?? "Failed to start intake")
    }
    return (await r.json()) as IntakeSessionDto
  }, [candidateId, sessionCreateBody])

  const loadActiveSession = useCallback(() => {
    if (mountedRef.current) setActiveLoaded(false)
    return api(`/api/candidates/${candidateId}/intake/sessions/active`)
      .then(async r => {
        if (!mountedRef.current) return
        if (r.status === 404) {
          setSessionId(null)
          setMessages([])
          setReadyToBuild(false)
          setBuildCompleted(false)
          return
        }
        if (!r.ok) {
          const e = await r.json().catch(() => ({}))
          throw new Error((e as { error?: string }).error ?? "Failed to load intake session")
        }
        const body = (await r.json()) as IntakeSessionDto
        if (!mountedRef.current) return
        if (freshStart) {
          setSessionId(null)
          setMessages([])
          setReadyToBuild(false)
          setBuildCompleted(false)
          return
        }
        applySessionDto(body, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
        if (body.awaiting_agent) {
          setStarting(false)
          setBusy(false)
        }
      })
      .catch(e => {
        if (!mountedRef.current) return
        setToast({ text: e.message, variant: "error" })
      })
      .finally(() => {
        if (!mountedRef.current) return
        setActiveLoaded(true)
      })
  }, [candidateId, freshStart])

  const pollActiveSession = useCallback(() => {
    void api(`/api/candidates/${candidateId}/intake/sessions/active`)
      .then(async r => {
        if (!r.ok) return
        const body = (await r.json()) as IntakeSessionDto
        if (!mountedRef.current) return
        if (!body.awaiting_agent) {
          applySessionDto(body, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
        }
      })
      .catch(() => {})
  }, [candidateId])

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [open])

  useEffect(() => {
    if (!open || !candidateId) return
    autoStartAttempted.current = false
    setStarting(false)
    setActiveLoaded(false)
    void loadActiveSession()
  }, [open, candidateId, loadActiveSession])

  useEffect(() => {
    if (!open || !activeLoaded || !autoStart || autoStartAttempted.current) return
    if (hasSession && !freshStart) return
    autoStartAttempted.current = true
    setStarting(true)
    setBusy(true)
    createSession()
      .then(dto => {
        if (!mountedRef.current) return
        applySessionDto(dto, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
      })
      .catch(e => {
        if (!mountedRef.current) return
        setToast({ text: e instanceof Error ? e.message : "Start failed", variant: "error" })
      })
      .finally(() => {
        if (!mountedRef.current) return
        setStarting(false)
        setBusy(false)
      })
  }, [open, activeLoaded, autoStart, freshStart, hasSession, createSession])

  useEffect(() => {
    if (!open || !hasSession) return
    const dtoAwaiting =
      messages.length === 0 ||
      (messages.length > 0 && messages[messages.length - 1].role === "user")
    if (!dtoAwaiting) return
    pollActiveSession()
    pollRef.current = setInterval(pollActiveSession, 3000)
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [open, hasSession, messages, pollActiveSession])

  useEffect(() => {
    const el = threadRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages.length, starting])

  const handleSend = useCallback(async () => {
    const text = draft.trim()
    if (!sessionId || !text || busy) return
    setBusy(true)
    setDraft("")
    try {
      const r = await api(
        `/api/candidates/${candidateId}/intake/sessions/${sessionId}/turns`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        },
      )
      if (!r.ok) {
        const e = await r.json().catch(() => ({}))
        throw new Error((e as { error?: string }).error ?? "Send failed")
      }
      const dto = (await r.json()) as IntakeSessionDto
      if (!mountedRef.current) return
      applySessionDto(dto, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
    } catch (e) {
      if (!mountedRef.current) return
      setDraft(text)
      setToast({ text: e instanceof Error ? e.message : "Send failed", variant: "error" })
    } finally {
      if (!mountedRef.current) return
      setBusy(false)
    }
  }, [candidateId, draft, sessionId, busy])

  const handleBuild = useCallback(async () => {
    if (!sessionId || buildCompleted || busy) return
    setBusy(true)
    try {
      const r = await api(
        `/api/candidates/${candidateId}/intake/sessions/${sessionId}/build`,
        { method: "POST" },
      )
      if (!r.ok) {
        const e = await r.json().catch(() => ({}))
        throw new Error((e as { error?: string }).error ?? "Build failed")
      }
      const dto = (await r.json()) as IntakeSessionDto
      if (!mountedRef.current) return
      applySessionDto(dto, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
      setToast({
        text: "Profile generated — review on Profile and context screens.",
        variant: "success",
      })
    } catch (e) {
      if (!mountedRef.current) return
      setToast({ text: e instanceof Error ? e.message : "Build failed", variant: "error" })
    } finally {
      if (!mountedRef.current) return
      setBusy(false)
    }
  }, [candidateId, sessionId, buildCompleted, busy])

  const handleNewSession = useCallback(async () => {
    if (!buildCompleted || busy) return
    const ok = await confirm(
      "Start a new intake session? The previous conversation will remain stored but a new session will begin.",
      { title: "New intake session", confirmLabel: "Start new session" },
    )
    if (!ok) return
    setBusy(true)
    setStarting(true)
    try {
      const dto = await createSession()
      if (!mountedRef.current) return
      applySessionDto(dto, setSessionId, setMessages, setReadyToBuild, setBuildCompleted)
    } catch (e) {
      if (!mountedRef.current) return
      setToast({ text: e instanceof Error ? e.message : "New session failed", variant: "error" })
    } finally {
      if (!mountedRef.current) return
      setStarting(false)
      setBusy(false)
    }
  }, [buildCompleted, busy, confirm, createSession])

  const showHold =
    !activeLoaded || starting || (hasSession && messages.length === 0)

  return (
    <>
      <Modal open={open} onClose={onClose} title="Candidate Intake" size="wide">
        <div className="intake-modal-body">
          <div className="intake-thread" ref={threadRef}>
            {showHold && <p className="intake-hold">{INTAKE_HOLD_COPY}</p>}
            {messages.map((msg, i) => (
              <div
                key={`${msg.role}-${i}-${msg.content.slice(0, 24)}`}
                className={`intake-msg intake-msg--${msg.role}`}
              >
                {msg.content}
              </div>
            ))}
          </div>

          {hasSession && (
            <div className="intake-composer">
              <textarea
                className="intake-composer-input"
                value={draft}
                onChange={e => setDraft(e.target.value)}
                disabled={busy}
                placeholder="Reply…"
              />
              <button
                type="button"
                className="modal-btn save"
                disabled={!draft.trim() || busy}
                onClick={() => void handleSend()}
              >
                Send
              </button>
              <button
                type="button"
                className="modal-btn save intake-generate-btn"
                disabled={!readyToBuild || buildCompleted || busy}
                onClick={() => void handleBuild()}
              >
                Generate Profile
              </button>
            </div>
          )}

          {hasSession && buildCompleted && (
            <div className="intake-actions">
              <button
                type="button"
                className="modal-btn cancel"
                disabled={busy}
                onClick={() => void handleNewSession()}
              >
                New intake session
              </button>
            </div>
          )}
        </div>
      </Modal>
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
