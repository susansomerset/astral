import { useCallback, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import { ApiError, errorToastFromApiError, readApiError } from "../lib/toastDiagnostics"

type SurferConsentDto = {
  status: string
  accepted_version: string | null
  updated_at: string | null
  current_version: string
  disclosure_copy: string
  is_current: boolean
  disclosure_title: string
  opt_in_label: string
  decline_label: string
  current_ok_title: string
  current_ok_body: string
}

function DisclosureParagraphs({ copy }: { copy: string }) {
  return (
    <>
      {copy.split("\n\n").map((block, i) => (
        <p key={i}>
          {block.split("\n").map((line, j) => (
            <span key={j}>
              {j > 0 ? <br /> : null}
              {line}
            </span>
          ))}
        </p>
      ))}
    </>
  )
}

export default function CandidateSurferConsent() {
  const { selectedId } = useCandidate()
  const navigate = useNavigate()
  const [dto, setDto] = useState<SurferConsentDto | null>(null)
  const [loading, setLoading] = useState(false)
  const [optingIn, setOptingIn] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    if (!selectedId) {
      setDto(null)
      return
    }
    let cancelled = false
    setLoading(true)
    setDto(null)
    api(`/api/candidates/${selectedId}/surfer/consent`)
      .then(async (r) => {
        if (!r.ok) {
          await readApiError(r, `/api/candidates/${selectedId}/surfer/consent`, "GET")
        }
        return r.json() as Promise<SurferConsentDto>
      })
      .then((data) => {
        if (!cancelled) setDto(data)
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setToast(
            e instanceof ApiError
              ? errorToastFromApiError(e)
              : {
                  text: e instanceof Error ? e.message : "Failed to load Surfer consent",
                  variant: "error",
                },
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [selectedId])

  async function onOptIn() {
    if (!selectedId || !dto || optingIn) return
    setOptingIn(true)
    try {
      const r = await api(`/api/candidates/${selectedId}/surfer/consent`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "opt_in",
          accepted_version: dto.current_version,
        }),
      })
      if (!r.ok) {
        await readApiError(r, `/api/candidates/${selectedId}/surfer/consent`, "PUT")
      }
      const next = (await r.json()) as SurferConsentDto
      setDto(next)
    } catch (e: unknown) {
      setToast(
        e instanceof ApiError
          ? errorToastFromApiError(e)
          : { text: e instanceof Error ? e.message : "Opt-in failed", variant: "error" },
      )
    } finally {
      setOptingIn(false)
    }
  }

  // Decline: navigate away with no PUT (AST-1237 — dismissing is not consent).
  function onDecline() {
    navigate("/jobs/recommended")
  }

  return (
    <div className="surfer-consent-page">
      <Toast message={toast} onDone={clearToast} />
      {!selectedId ? (
        <p className="surfer-consent-empty">Select a candidate to view Surfer consent.</p>
      ) : loading || !dto ? (
        <p className="surfer-consent-empty">Loading…</p>
      ) : dto.is_current ? (
        <>
          <h1 className="surfer-consent-title">{dto.current_ok_title}</h1>
          <div className="surfer-consent-body">
            <DisclosureParagraphs copy={dto.current_ok_body} />
          </div>
        </>
      ) : (
        <>
          <h1 className="surfer-consent-title">{dto.disclosure_title}</h1>
          <div className="surfer-consent-body">
            <DisclosureParagraphs copy={dto.disclosure_copy} />
          </div>
          <div className="surfer-consent-actions">
            <button
              type="button"
              className="modal-btn save"
              disabled={optingIn}
              onClick={() => void onOptIn()}
            >
              {dto.opt_in_label}
            </button>
            <button
              type="button"
              className="modal-btn cancel"
              disabled={optingIn}
              onClick={onDecline}
            >
              {dto.decline_label}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
