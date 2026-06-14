import { useCallback, useEffect, useState } from "react"
import ArtifactEditor from "../components/ArtifactEditor"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import Toast, { type ToastMessage } from "../components/Toast"

function normalizeHex(raw: unknown): string | null {
  if (typeof raw !== "string" || !raw) return null
  const t = raw.trim().toUpperCase()
  return /^#[0-9A-F]{6}$/.test(t) ? t : null
}

export default function BaseResumeContent() {
  const { selectedId } = useCandidate()
  const [palette, setPalette] = useState<string[]>([])
  const [accent, setAccent] = useState<string | null>(null)
  const [structureSections, setStructureSections] = useState<{ id: string; label: string }[] | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    api("/api/system/ui_config")
      .then(r => r.json())
      .then(cfg => setPalette(Array.isArray(cfg.base_resume_accent_palette) ? cfg.base_resume_accent_palette : []))
      .catch(() => setPalette([]))
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setStructureSections(null)
      setAccent(null)
      return
    }
    api(`/api/candidates/${selectedId}/resume_structure`)
      .then(r => r.json())
      .then(data => {
        setStructureSections(Array.isArray(data.sections) ? data.sections : [])
        setAccent(normalizeHex(data.accent_color))
      })
      .catch(() => {
        setStructureSections([])
        setAccent(null)
      })
  }, [selectedId])

  function pickSwatch(hex: string) {
    const up = hex.toUpperCase()
    setAccent(up)
    if (!selectedId) return
    api(`/api/candidates/${selectedId}/data`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ artifacts: { resume_structure: { accent_color: up } } }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Save failed") })
        return r.json()
      })
      .then(() => setToast({ text: "Accent color saved", variant: "success" }))
      .catch(e => setToast({ text: e.message, variant: "error" }))
  }

  return (
    <>
      {palette.length > 0 && (
        <div className="base-resume-accent-bar" role="group" aria-label="Resume accent color">
          <span className="base-resume-accent-label">Accent</span>
          <div className="base-resume-accent-swatches">
            {palette.map(hex => (
              <button
                key={hex}
                type="button"
                className={`base-resume-accent-swatch${accent === hex.toUpperCase() ? " selected" : ""}`}
                style={{ backgroundColor: hex }}
                title={hex}
                aria-label={hex}
                aria-pressed={accent === hex.toUpperCase()}
                onClick={() => pickSwatch(hex)}
              />
            ))}
          </div>
        </div>
      )}
      <ArtifactEditor
        title="Base Resume Content"
        artifactKey="base_resume"
        taskKey="craft_resume_base"
        useCandidateResumeStructure
        structureSections={structureSections}
      />
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
