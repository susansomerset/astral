import { useCallback, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useCandidate } from "../contexts/CandidateContext"
import IntakeChatModal, { type IntakeSourceMaterials } from "../components/IntakeChatModal"
import IntakePreamblePanel from "../components/IntakePreamblePanel"
import IntakeTopicMenuPanel from "../components/IntakeTopicMenuPanel"
import Modal from "../components/Modal"
import Toast, { type ToastMessage } from "../components/Toast"
import { useUserConfirm } from "../components/UserPrompt"
import api from "../lib/api"

const emptyMaterials = (): IntakeSourceMaterials => ({
  starting_resume_text: "",
  sample_cover_text: "",
  linkedin_profile_text: "",
})

const RESUME_INTAKE_TITLE = "Resume Intake"
const RESUME_INTAKE_MESSAGE = "Would you like to continue your intake?"

type IntakePhase = "idle" | "preamble" | "topic_menu" | "chat"

type IntakeResumeDialogProps = {
  onContinue: () => void
  onStartOver: () => void
  onDismiss: () => void
  busy?: boolean
}

function IntakeResumeDialog({ onContinue, onStartOver, onDismiss, busy = false }: IntakeResumeDialogProps) {
  return (
    <div
      className="modal-overlay user-prompt-overlay"
      role="presentation"
      onClick={() => {
        if (!busy) onDismiss()
      }}
    >
      <div
        className="modal-card user-prompt-card"
        role="alertdialog"
        aria-labelledby="intake-resume-title"
        aria-describedby="intake-resume-message"
        aria-busy={busy || undefined}
        onClick={e => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 id="intake-resume-title" className="modal-title">{RESUME_INTAKE_TITLE}</h2>
        </div>
        <div className="modal-body">
          <p id="intake-resume-message" className="user-prompt-message">{RESUME_INTAKE_MESSAGE}</p>
        </div>
        <div className="modal-footer">
          <button type="button" className="modal-btn cancel" disabled={busy} onClick={onStartOver}>
            Start Over
          </button>
          <button type="button" className="modal-btn save" disabled={busy} onClick={onContinue}>
            Continue
          </button>
        </div>
      </div>
    </div>
  )
}

export default function CandidateIntake() {
  const navigate = useNavigate()
  const confirm = useUserConfirm()
  const { selectedId } = useCandidate()
  const [materials, setMaterials] = useState<IntakeSourceMaterials>(emptyMaterials)
  const [phase, setPhase] = useState<IntakePhase>("idle")
  const [resumeDialogOpen, setResumeDialogOpen] = useState(false)
  const [startOverBusy, setStartOverBusy] = useState(false)
  const [freshStartKey, setFreshStartKey] = useState(0)
  const [freshStartMode, setFreshStartMode] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)

  const goProfile = useCallback(() => navigate("/candidate/profile"), [navigate])
  const clearToast = useCallback(() => setToast(null), [])

  const openPreamble = useCallback(() => {
    setResumeDialogOpen(false)
    setPhase("preamble")
  }, [])

  const handleResumeContinue = useCallback(() => {
    // Active session — skip preamble; Estelle chat only.
    setFreshStartMode(false)
    setResumeDialogOpen(false)
    setPhase("chat")
  }, [])

  const handleResumeStartOver = useCallback(async () => {
    if (!selectedId || startOverBusy) return
    setStartOverBusy(true)
    try {
      const r = await api(
        `/api/candidates/${selectedId}/intake/sessions/active/archive`,
        { method: "POST" },
      )
      if (!r.ok && r.status !== 404) {
        const e = await r.json().catch(() => ({}))
        throw new Error((e as { error?: string }).error ?? "Failed to archive intake session")
      }
      const activeCheck = await api(`/api/candidates/${selectedId}/intake/sessions/active`)
      if (activeCheck.ok) {
        throw new Error("Active intake session still present after archive")
      }
      if (activeCheck.status !== 404) {
        throw new Error("Failed to verify intake session cleared")
      }
      setFreshStartMode(true)
      setFreshStartKey(k => k + 1)
      openPreamble()
    } catch (e) {
      setToast({
        text: e instanceof Error ? e.message : "Failed to start over",
        variant: "error",
      })
    } finally {
      setStartOverBusy(false)
    }
  }, [selectedId, startOverBusy, openPreamble])

  const handleResumeDismiss = useCallback(() => {
    setResumeDialogOpen(false)
    goProfile()
  }, [goProfile])

  const handlePreambleComplete = useCallback(
    (m: IntakeSourceMaterials) => {
      if (!m.starting_resume_text.trim()) {
        setToast({
          text: "Resume text is required before Estelle can begin.",
          variant: "error",
        })
        goProfile()
        return
      }
      setMaterials(m)
      setPhase("topic_menu")
    },
    [goProfile],
  )

  useEffect(() => {
    if (!selectedId) return
    setPhase("idle")
    setResumeDialogOpen(false)
    let cancelled = false

    api(`/api/candidates/${selectedId}`)
      .then(r => {
        if (!r.ok) throw new Error("Failed to load candidate")
        return r.json()
      })
      .then(async c => {
        if (cancelled) return
        const ctx = (c.candidate_data?.context ?? {}) as Record<string, string>
        const loaded: IntakeSourceMaterials = {
          starting_resume_text: ctx.raw_resume ?? ctx.starting_resume_text ?? "",
          sample_cover_text: ctx.raw_sample ?? ctx.sample_cover_text ?? "",
          linkedin_profile_text: ctx.raw_profile ?? ctx.linkedin_profile_text ?? "",
        }
        setMaterials(loaded)

        const activeRes = await api(`/api/candidates/${selectedId}/intake/sessions/active`)
        if (cancelled) return

        if (activeRes.ok) {
          setResumeDialogOpen(true)
          return
        }
        if (activeRes.status !== 404) {
          setToast({ text: "Failed to load intake session", variant: "error" })
          goProfile()
          return
        }

        const ok = await confirm(
          "Start a candidate intake interview? We'll collect any missing source materials, then Estelle will begin.",
          {
            title: "Start Intake",
            confirmLabel: "Continue",
          },
        )
        if (cancelled) return
        if (!ok) {
          goProfile()
          return
        }
        setFreshStartMode(true)
        setFreshStartKey(k => k + 1)
        setPhase("preamble")
      })
      .catch(() => {
        if (cancelled) return
        setToast({ text: "Failed to load candidate", variant: "error" })
        goProfile()
      })

    return () => {
      cancelled = true
    }
  }, [selectedId, confirm, goProfile])

  if (!selectedId) {
    return <p className="entity-empty">Select a candidate to open Intake.</p>
  }

  return (
    <>
      {resumeDialogOpen && (
        <IntakeResumeDialog
          busy={startOverBusy}
          onContinue={handleResumeContinue}
          onStartOver={() => void handleResumeStartOver()}
          onDismiss={handleResumeDismiss}
        />
      )}
      {phase === "preamble" && (
        <Modal open onClose={goProfile} title="Candidate Intake" size="wide">
          <IntakePreamblePanel
            candidateId={selectedId}
            initialMaterials={materials}
            onComplete={handlePreambleComplete}
            onCancel={goProfile}
          />
        </Modal>
      )}
      {phase === "topic_menu" && (
        <Modal open onClose={goProfile} title="Candidate Intake" size="wide">
          <IntakeTopicMenuPanel
            candidateId={selectedId}
            onDone={goProfile}
            onCancel={goProfile}
          />
        </Modal>
      )}
      {phase === "chat" && (
        <IntakeChatModal
          key={freshStartKey}
          open
          autoStart
          freshStart={freshStartMode}
          onClose={goProfile}
          candidateId={selectedId}
          materials={materials}
        />
      )}
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
