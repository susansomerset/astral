import { useCallback, useEffect, useState } from "react"
import Toast, { type ToastMessage } from "../components/Toast"
import { useUserConfirm } from "../components/UserPrompt"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import { ApiError, errorToastFromApiError, readApiError } from "../lib/toastDiagnostics"

type SurferConsentDto = {
  status: string
  is_current: boolean
  off_switch_heading: string
  off_switch_button_label: string
  off_switch_confirm: string
  status_on_label: string
  status_off_label: string
  status_stale_label: string
  uninstall_guidance: string
}

export default function CandidateSurfer() {
  const { selectedId } = useCandidate()
  const confirm = useUserConfirm()
  const [dto, setDto] = useState<SurferConsentDto | null>(null)
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  const load = useCallback(async (candidateId: string) => {
    const r = await api(`/api/candidates/${candidateId}/surfer/consent`)
    if (!r.ok) await readApiError(r, `/api/candidates/${candidateId}/surfer/consent`, "GET")
    const data = (await r.json()) as SurferConsentDto
    setDto(data)
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setDto(null)
      return
    }
    let cancelled = false
    ;(async () => {
      try {
        await load(selectedId)
      } catch (e) {
        if (cancelled) return
        setDto(null)
        setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: "Failed to load Surfer status", variant: "error" })
      }
    })()
    return () => {
      cancelled = true
    }
  }, [selectedId, load])

  async function handleOptOut() {
    if (!selectedId || !dto) return
    if (!(await confirm(dto.off_switch_confirm))) return
    setBusy(true)
    try {
      const r = await api(`/api/candidates/${selectedId}/surfer/consent`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "opt_out" }),
      })
      if (!r.ok) await readApiError(r, `/api/candidates/${selectedId}/surfer/consent`, "PUT")
      await load(selectedId)
      setToast({ text: "Surfer turned off", variant: "success" })
    } catch (e) {
      setToast(e instanceof ApiError ? errorToastFromApiError(e) : { text: "Failed to turn Surfer off", variant: "error" })
    } finally {
      setBusy(false)
    }
  }

  if (!selectedId) {
    return <div className="surfer-page"><p>Select a candidate.</p></div>
  }

  const statusLine = !dto
    ? null
    : dto.is_current
      ? dto.status_on_label
      : dto.status === "opted_in"
        ? dto.status_stale_label
        : dto.status_off_label

  return (
    <div className="surfer-page">
      {dto && (
        <>
          <h1>{dto.off_switch_heading}</h1>
          {statusLine && <p className="surfer-page-status">{statusLine}</p>}
          {dto.status === "opted_in" && (
            <button type="button" className="btn secondary" disabled={busy} onClick={() => void handleOptOut()}>
              {dto.off_switch_button_label}
            </button>
          )}
          <p className="surfer-page-uninstall">{dto.uninstall_guidance}</p>
        </>
      )}
      {toast && <Toast message={toast} onDone={clearToast} />}
    </div>
  )
}
