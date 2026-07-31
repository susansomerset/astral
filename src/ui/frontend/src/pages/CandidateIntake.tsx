import { useCallback, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useCandidate } from "../contexts/CandidateContext"
import IntakeChatModal, { type IntakeSourceMaterials } from "../components/IntakeChatModal"
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

function intakeConfirmMessage(materials: IntakeSourceMaterials): string {
  const lines = [
    "Start a candidate intake interview? Your saved resume and profile materials on this candidate will be used.",
  ]
  const missing: string[] = []
  if (!materials.sample_cover_text.trim()) missing.push("sample cover letter")
  if (!materials.linkedin_profile_text.trim()) missing.push("LinkedIn profile text")
  if (missing.length) {
    lines.push(
      "",
      `Note: ${missing.join(" and ")} ${missing.length > 1 ? "are" : "is"} not saved on this candidate yet. You can continue, but Estelle will have less context.`,
    )
  }
  return lines.join("\n")
}

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
  const [modalOpen, setModalOpen] = useState(false)
  const [resumeDialogOpen, setResumeDialogOpen] = useState(false)
  const [startOverBusy, setStartOverBusy] = useState(false)
  const [freshStartKey, setFreshStartKey] = useState(0)
  const [freshStartMode, setFreshStartMode] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)

  const goProfile = useCallback(() => navigate("/candidate/profile"), [navigate])
  const clearToast = useCallback(() => setToast(null), [])

  const openModalAfterResumeChoice = useCallback(() => {
    setResumeDialogOpen(false)
    setModalOpen(true)
  }, [])

  const handleResumeContinue = useCallback(() => {
    setFreshStartMode(false)
    openModalAfterResumeChoice()
  }, [openModalAfterResumeChoice])

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
      openModalAfterResumeChoice()
    } catch (e) {
      setToast({
        text: e instanceof Error ? e.message : "Failed to start over",
        variant: "error",
      })
    } finally {
      setStartOverBusy(false)
    }
  }, [selectedId, startOverBusy, openModalAfterResumeChoice])

  const handleResumeDismiss = useCallback(() => {
    setResumeDialogOpen(false)
    goProfile()
  }, [goProfile])

  useEffect(() => {
    if (!selectedId) return
    setModalOpen(false)
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
          starting_resume_text: ctx.starting_resume_text ?? "",
          sample_cover_text: ctx.sample_cover_text ?? "",
          linkedin_profile_text: ctx.linkedin_profile_text ?? "",
        }
        if (!loaded.starting_resume_text.trim()) {
          setToast({
            text: "Add Original Resume Text on Profile before starting Intake.",
            variant: "error",
          })
          goProfile()
          return
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

        const ok = await confirm(intakeConfirmMessage(loaded), {
          title: "Start Intake",
          confirmLabel: "Continue",
        })
        if (cancelled) return
        if (!ok) {
          goProfile()
          return
        }
        setModalOpen(true)
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
      {modalOpen && (
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
