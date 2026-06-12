import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react"
import FormFields, { getByPath, setByPath } from "../components/FormFields"
import TabbedTextArea from "../components/TabbedTextArea"
import type { TextTab } from "../components/TabbedTextArea"
import Toast, { type ToastMessage } from "../components/Toast"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import type { Section } from "../components/FormFields"

interface SigImageLimits {
  max_width_px: number
  max_height_px: number
}

function readJpegDataUrl(file: File, maxW: number, maxH: number): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!/^image\/jpe?g$/i.test(file.type)) {
      reject(new Error("Signature image must be a JPEG"))
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      const dataUrl = String(reader.result ?? "")
      const img = new Image()
      img.onload = () => {
        if (img.width > maxW || img.height > maxH) {
          reject(new Error(`Signature image must be at most ${maxW}×${maxH} pixels`))
          return
        }
        resolve(dataUrl)
      }
      img.onerror = () => reject(new Error("Could not read signature image"))
      img.src = dataUrl
    }
    reader.onerror = () => reject(new Error("Could not read signature image"))
    reader.readAsDataURL(file)
  })
}

export default function Profile() {
  const { selectedId, refresh: refreshCandidate } = useCandidate()
  const [sections, setSections] = useState<Section[] | null>(null)
  const [fetched, setFetched] = useState<{ id: string; data: Record<string, unknown> } | null>(null)
  const [values, setValues] = useState<Record<string, unknown>>({})
  const [sigLimits, setSigLimits] = useState<SigImageLimits | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  const sigFileRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    api("/api/shapes/candidates").then(r => r.json()).then(shapes => {
      setSections(shapes.detail.profile)
    })
    api("/api/ui_config").then(r => r.json()).then(cfg => {
      setSigLimits(cfg.cover_letter_signature_image ?? null)
    }).catch(() => setSigLimits(null))
  }, [])

  useEffect(() => {
    if (!selectedId) return
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      const d = c.candidate_data ?? {}
      setFetched({ id: selectedId, data: d })
      setValues({ ...d })
    })
  }, [selectedId])

  const data = fetched?.id === selectedId ? fetched.data : null

  function set(key: string, value: unknown) {
    setValues(prev => setByPath(prev, key, value))
  }

  function handleSave() {
    if (!selectedId) return
    setError(null)
    api(`/api/candidates/${selectedId}/data`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Save failed") })
        return r.json()
      })
      .then(candidate => {
        const d = candidate.candidate_data ?? {}
        setFetched({ id: selectedId, data: d })
        setValues({ ...d })
        refreshCandidate()
        setToast({ text: "Profile saved", variant: "success" })
      })
      .catch(e => {
        setError(e.message)
        setToast({ text: "Save failed", variant: "error" })
      })
  }

  function handleCancel() {
    if (data) setValues({ ...data })
    setError(null)
  }

  const hasBaseResume = Boolean(getByPath(values, "artifacts.base_resume"))
  const sigImg = String(getByPath(values, "profile.cover_letter_signature_image") ?? "")
  const maxSigW = sigLimits?.max_width_px
  const maxSigH = sigLimits?.max_height_px

  const handleSignatureImagePick = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    e.target.value = ""
    if (!file || maxSigW == null || maxSigH == null) return
    setError(null)
    readJpegDataUrl(file, maxSigW, maxSigH)
      .then(url => setValues(prev => setByPath(prev, "profile.cover_letter_signature_image", url)))
      .catch(err => {
        setError(err instanceof Error ? err.message : "Invalid signature image")
        setToast({ text: "Signature image rejected", variant: "error" })
      })
  }, [maxSigW, maxSigH])

  const handleClearSignatureImage = useCallback(() => {
    setValues(prev => setByPath(prev, "profile.cover_letter_signature_image", ""))
    if (sigFileRef.current) sigFileRef.current.value = ""
  }, [])

  const signatureImagePanel = useMemo(() => {
    if (maxSigW == null || maxSigH == null) {
      return <p style={{ color: "#8b949e" }}>Loading signature image limits…</p>
    }
    return (
      <>
        <p style={{ color: "#8b949e", marginBottom: 8 }}>
          JPEG only, max {maxSigW}×{maxSigH} pixels.
        </p>
        <div className="dep-field">
          <input
            ref={sigFileRef}
            type="file"
            accept="image/jpeg,.jpg,.jpeg"
            onChange={handleSignatureImagePick}
          />
          {sigImg ? (
            <div style={{ marginTop: 12 }}>
              <img src={sigImg} alt="" style={{ maxWidth: maxSigW, maxHeight: maxSigH, display: "block" }} />
              <button type="button" className="dep-btn cancel" style={{ marginTop: 8 }} onClick={handleClearSignatureImage}>
                Remove image
              </button>
            </div>
          ) : null}
        </div>
      </>
    )
  }, [maxSigW, maxSigH, sigImg, handleSignatureImagePick, handleClearSignatureImage])

  if (!sections || data === null) return <p style={{ padding: 20, color: "#fff" }}>Loading...</p>
  if (!selectedId) return <p style={{ padding: 20, color: "#fff" }}>No candidate selected.</p>

  const contactSection = sections[0]
  const tabSections = sections.slice(1)
  const half = Math.ceil(contactSection.fields.length / 2)
  const contactLeft = contactSection.fields.slice(0, half)
  const contactRight = contactSection.fields.slice(half)

  const textTabs: TextTab[] = tabSections.map(sec => {
    const f = sec.fields[0]
    const isResume = f.key === "context.starting_resume_text"
    return {
      label: sec.label,
      key: f.key,
      disabled: isResume && hasBaseResume,
      placeholder: isResume && hasBaseResume ? "Locked — base resume has been generated from this text" : undefined,
    }
  })

  return (
    <>
      {error && <p style={{ padding: "8px 20px", color: "#ff6b6b" }}>{error}</p>}
      <div className="dep-page">
        <div className="dep-header">
          <h1 className="dep-title">Candidate Profile</h1>
          <div className="dep-actions">
            <button className="dep-btn cancel" onClick={handleCancel}>Cancel</button>
            <button className="dep-btn save" onClick={handleSave}>Save</button>
          </div>
        </div>
        <div className="dep-body">
          <div className="dep-section">
            <h2 className="dep-section-label">{contactSection.label}</h2>
            <div className="profile-contact-grid">
              <div className="profile-contact-col">
                <FormFields fields={contactLeft} values={values} onChange={set} />
              </div>
              <div className="profile-contact-col">
                <FormFields fields={contactRight} values={values} onChange={set} />
              </div>
            </div>
          </div>

          <div className="dep-section">
            <TabbedTextArea
              tabs={textTabs}
              values={values}
              onChange={set}
              customPanels={{ "profile.cover_letter_signature_image": signatureImagePanel }}
            />
          </div>
        </div>
      </div>
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
