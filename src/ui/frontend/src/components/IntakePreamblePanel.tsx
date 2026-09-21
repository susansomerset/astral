import { useCallback, useEffect, useMemo, useState } from "react"
import Toast, { type ToastMessage } from "./Toast"
import api from "../lib/api"

/** Closed outcome set — mirror of AST-1015 PREAMBLE_VALIDATION_CONFIG["outcomes"]. */
const PREAMBLE_OUTCOMES = ["Valid", "Try Again", "Escalate"] as const
type PreambleOutcome = (typeof PREAMBLE_OUTCOMES)[number]

export type PreambleMaterials = {
  starting_resume_text: string
  sample_cover_text: string
  linkedin_profile_text: string
}

type PreambleStep = {
  id: string
  order: number
  prompt_1st_try: string
  prompt_2nd_try: string
  target: { blob: string; field: string }
  validation_question: string
}

type PreambleConfig = {
  intro: string
  validation_task_key: string
  steps: PreambleStep[]
}

export type IntakePreamblePanelProps = {
  candidateId: string
  /** Current context raw_* (and legacy aliases already resolved by parent). */
  initialMaterials: PreambleMaterials
  onComplete: (materials: PreambleMaterials) => void
  onCancel: () => void
}

const FIELD_TO_MATERIAL: Record<string, keyof PreambleMaterials> = {
  raw_resume: "starting_resume_text",
  raw_profile: "linkedin_profile_text",
  raw_sample: "sample_cover_text",
}

function materialForField(materials: PreambleMaterials, field: string): string {
  const key = FIELD_TO_MATERIAL[field]
  return key ? materials[key] : ""
}

function withField(
  materials: PreambleMaterials,
  field: string,
  value: string,
): PreambleMaterials {
  const key = FIELD_TO_MATERIAL[field]
  if (!key) return materials
  return { ...materials, [key]: value }
}

export default function IntakePreamblePanel({
  candidateId,
  initialMaterials,
  onComplete,
  onCancel,
}: IntakePreamblePanelProps) {
  const [preamble, setPreamble] = useState<PreambleConfig | null>(null)
  const [materials, setMaterials] = useState<PreambleMaterials>(initialMaterials)
  const [use2ndTry, setUse2ndTry] = useState(false)
  const [draft, setDraft] = useState("")
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<ToastMessage | null>(null)

  const clearToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    setMaterials(initialMaterials)
    setUse2ndTry(false)
    setDraft("")
  }, [initialMaterials])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    api("/api/ui_config")
      .then(r => {
        if (!r.ok) throw new Error("Failed to load intake preamble config")
        return r.json()
      })
      .then(cfg => {
        if (cancelled) return
        const p = cfg?.preamble as PreambleConfig | undefined
        if (
          !p ||
          typeof p.intro !== "string" ||
          !p.intro ||
          !Array.isArray(p.steps) ||
          p.steps.length === 0
        ) {
          setToast({ text: "Intake preamble config missing or invalid", variant: "error" })
          onCancel()
          return
        }
        setPreamble(p)
        setLoading(false)
      })
      .catch(() => {
        if (cancelled) return
        setToast({ text: "Failed to load intake preamble config", variant: "error" })
        onCancel()
      })
    return () => {
      cancelled = true
    }
  }, [candidateId, onCancel])

  const pendingSteps = useMemo(() => {
    if (!preamble) return []
    return [...preamble.steps]
      .sort((a, b) => a.order - b.order)
      .filter(s => !materialForField(materials, s.target.field).trim())
  }, [preamble, materials])

  const currentStep = pendingSteps[0] ?? null
  const promptText = currentStep
    ? use2ndTry
      ? currentStep.prompt_2nd_try
      : currentStep.prompt_1st_try
    : ""

  const handleContinueEmpty = useCallback(() => {
    onComplete(materials)
  }, [materials, onComplete])

  const handleSubmit = useCallback(async () => {
    if (!preamble || !currentStep || busy || !draft.trim()) return
    setBusy(true)
    try {
      const vr = await api(`/api/candidates/${candidateId}/preamble/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: currentStep.validation_question,
          answer: draft,
          step_index: currentStep.order,
          step_total: preamble.steps.length,
        }),
      })
      if (!vr.ok) {
        const e = await vr.json().catch(() => ({}))
        throw new Error((e as { error?: string }).error ?? "Validation request failed")
      }
      const result = (await vr.json()) as {
        success?: boolean
        outcome?: string | null
        error?: string | null
      }
      if (
        !result.success ||
        !result.outcome ||
        !(PREAMBLE_OUTCOMES as readonly string[]).includes(result.outcome)
      ) {
        setToast({
          text: result.error || "Validation failed",
          variant: "error",
        })
        return
      }
      const outcome = result.outcome as PreambleOutcome
      if (outcome === "Try Again") {
        setUse2ndTry(true)
        setDraft("")
        return
      }
      if (outcome === "Escalate") {
        setToast({
          text: "This answer needs human review. Try a clearer paste, or edit this field on Profile and return to Intake.",
          variant: "error",
        })
        return
      }
      // Valid — persist then advance
      const trimmed = draft.trim()
      const put = await api(`/api/candidates/${candidateId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context: { [currentStep.target.field]: trimmed } }),
      })
      if (!put.ok) {
        const e = await put.json().catch(() => ({}))
        throw new Error((e as { error?: string }).error ?? "Failed to save preamble answer")
      }
      const nextMaterials = withField(materials, currentStep.target.field, trimmed)
      setMaterials(nextMaterials)
      setUse2ndTry(false)
      setDraft("")
      const remaining = [...preamble.steps]
        .sort((a, b) => a.order - b.order)
        .filter(s => !materialForField(nextMaterials, s.target.field).trim())
      if (remaining.length === 0) {
        onComplete(nextMaterials)
      }
    } catch (e) {
      setToast({
        text: e instanceof Error ? e.message : "Preamble step failed",
        variant: "error",
      })
    } finally {
      setBusy(false)
    }
  }, [preamble, currentStep, busy, draft, candidateId, materials, onComplete])

  if (loading || !preamble) {
    return (
      <>
        <div className="intake-preamble-panel">
          <p className="intake-hold">Loading preamble…</p>
        </div>
        <Toast message={toast} onDone={clearToast} />
      </>
    )
  }

  const noPending = pendingSteps.length === 0

  return (
    <>
      <div className="intake-preamble-panel">
        <div className="intake-thread intake-preamble-thread">
          <div className="intake-msg intake-msg--assistant">{preamble.intro}</div>
          {!noPending && currentStep && (
            <div className="intake-msg intake-msg--assistant">{promptText}</div>
          )}
        </div>

        {noPending ? (
          <div className="intake-preamble-actions">
            <button type="button" className="btn secondary" disabled={busy} onClick={onCancel}>
              Cancel
            </button>
            <button
              type="button"
              className="btn primary"
              disabled={busy}
              onClick={handleContinueEmpty}
            >
              Continue
            </button>
          </div>
        ) : (
          <>
            <textarea
              className="intake-preamble-input"
              value={draft}
              onChange={e => setDraft(e.target.value)}
              disabled={busy}
              placeholder="Paste your answer…"
            />
            <div className="intake-preamble-actions">
              <button type="button" className="btn secondary" disabled={busy} onClick={onCancel}>
                Cancel
              </button>
              <button
                type="button"
                className="btn primary"
                disabled={busy || !draft.trim()}
                onClick={() => void handleSubmit()}
              >
                Submit
              </button>
            </div>
          </>
        )}
      </div>
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
