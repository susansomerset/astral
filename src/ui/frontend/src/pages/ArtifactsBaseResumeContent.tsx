import { useCallback, useEffect, useState } from "react"
import ArtifactEditor from "../components/ArtifactEditor"
import {
  type Catalog,
  type SectionRow,
} from "../components/ResumeStructureEditor"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import Toast, { type ToastMessage } from "../components/Toast"

function normalizeHex(raw: unknown): string | null {
  if (typeof raw !== "string" || !raw) return null
  const t = raw.trim().toUpperCase()
  return /^#[0-9A-F]{6}$/.test(t) ? t : null
}

function catalogFromPayload(data: { catalog?: unknown }): Catalog | null {
  const raw = data.catalog
  if (!raw || typeof raw !== "object") return null
  const c = raw as Catalog
  if (!Array.isArray(c.body_formats)) return null
  return c
}

export default function BaseResumeContent() {
  const { selectedId } = useCandidate()
  const [palette, setPalette] = useState<string[]>([])
  const [accent, setAccent] = useState<string | null>(null)
  const [structureSections, setStructureSections] = useState<{ id: string; label: string }[] | null>(null)
  const [allSections, setAllSections] = useState<SectionRow[]>([])
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [structureSaving, setStructureSaving] = useState(false)
  const [structureError, setStructureError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  function applyStructurePayload(data: {
    sections?: unknown
    all_sections?: unknown
    accent_color?: unknown
    catalog?: unknown
  }) {
    setStructureSections(Array.isArray(data.sections) ? data.sections : [])
    setAccent(normalizeHex(data.accent_color))
    setAllSections(Array.isArray(data.all_sections) ? data.all_sections as SectionRow[] : [])
    setCatalog(catalogFromPayload(data))
  }

  function handleStructureRowsChange(rows: SectionRow[]) {
    setAllSections(rows)
    setStructureSections(rows.map(r => ({ id: r.id, label: r.title })))
  }

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
      setAllSections([])
      setCatalog(null)
      return
    }
    api(`/api/candidates/${selectedId}/resume_structure`)
      .then(r => r.json())
      .then(data => applyStructurePayload(data))
      .catch(() => {
        setStructureSections([])
        setAccent(null)
        setAllSections([])
        setCatalog(null)
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

  function saveStructure(rows: SectionRow[]) {
    if (!selectedId) return
    const sections: Record<string, Record<string, unknown>> = {}
    rows.forEach((row, index) => {
      const spec: Record<string, unknown> = {
        id: row.id,
        title: row.title,
        enabled: row.enabled,
        order: index,
        job_agent_editable: row.job_agent_editable,
      }
      if (row.format) spec.format = row.format
      sections[row.id] = spec
    })
    setStructureSaving(true)
    setStructureError(null)
    api(`/api/candidates/${selectedId}/data`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ artifacts: { resume_structure: { sections } } }),
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || "Save failed") })
        return r.json()
      })
      .then(() => api(`/api/candidates/${selectedId}/resume_structure`).then(r => r.json()))
      .then(data => {
        applyStructurePayload(data)
        setToast({ text: "Resume sections saved", variant: "success" })
      })
      .catch(e => {
        const msg = e.message || "Save failed"
        setStructureError(msg)
        setToast({ text: msg, variant: "error" })
      })
      .finally(() => setStructureSaving(false))
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
        structureCatalog={catalog}
        structureRows={allSections}
        onStructureRowsChange={handleStructureRowsChange}
        onStructureSave={saveStructure}
        structureSaving={structureSaving}
        structureError={structureError}
      />
      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
