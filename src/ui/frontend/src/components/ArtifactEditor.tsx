import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import CollapsiblePanel from "./CollapsiblePanel"
import LabeledTextArea from "./LabeledTextArea"
import type { SideTab } from "./SideTabPanel"
import Toast, { type ToastMessage } from "./Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import api from "../lib/api"
import { formatRubricVectorHeader, RUBRIC_DEFAULT_IMPORTANCE, rubricItemImportance } from "../lib/rubricDisplay"

interface ShapeField { key: string; label: string }

interface StructureSection { id: string; label: string }

interface ArtifactEditorProps {
  title: string
  artifactKey: string
  taskKey: string              // craft_* task to call for Generate
  shapesKey?: string           // key in DATA_SHAPES.candidates.detail — if set, tabs are fixed
  useCandidateResumeStructure?: boolean
  structureSections?: StructureSection[] | null
  /** Job-scoped artifact load/save (AST-553/565); no Generate. */
  jobPersistence?: { jobId: string; artifactKey: string; onSaved?: () => void }
}

const AUTOSAVE_MS = 2000
const MIN_ARTIFACT_TABS = 1
const MAX_ARTIFACT_TABS = 15

let _artifactTabSeq = 0
function genArtifactTabId() {
  return `st_${Date.now()}_${_artifactTabSeq++}`
}

/** Map craft_*_rubric `criteria[]` into editor tabs (live Generate + pending recovery). */
function criteriaToTabs(
  criteria: { code?: string; label?: string; content?: string; importance?: number }[],
): SideTab[] {
  return criteria.map((v, i) => ({
    id: `g_${i}`,
    code: v.code,
    label: v.label ?? `Criterion ${i + 1}`,
    content: v.content ?? "",
    importance: rubricItemImportance(v),
  }))
}

export default function ArtifactEditor({
  title,
  artifactKey,
  taskKey,
  shapesKey,
  useCandidateResumeStructure = false,
  structureSections = undefined,
  jobPersistence,
}: ArtifactEditorProps) {
  const { manifest, loadState } = useStateUi()
  const { selectedId, candidates } = useCandidate()
  const [shapeFields, setShapeFields] = useState<ShapeField[] | null>(shapesKey ? null : [])
  const [shapeError, setShapeError] = useState(false)
  const [jobLoadError, setJobLoadError] = useState(false)
  const [tabs, setTabs] = useState<SideTab[]>([])
  const [loaded, setLoaded] = useState(false)
  const [dirty, setDirty] = useState(false)
  const [everSaved, setEverSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const tabsRef = useRef(tabs)
  const dirtyRef = useRef(dirty)
  const snapshotRef = useRef<SideTab[] | null>(null)
  const mountedRef = useRef(true)
  const generateAbortRef = useRef<AbortController | null>(null)
  tabsRef.current = tabs
  dirtyRef.current = dirty

  // Generate/Regenerate state
  const [snapshot, setSnapshot] = useState<SideTab[] | null>(null)
  snapshotRef.current = snapshot
  const [generating, setGenerating] = useState(false)
  const [confirmRegen, setConfirmRegen] = useState(false)
  const [expandedTabId, setExpandedTabId] = useState("")
  const [editingId, setEditingId] = useState<string | null>(null)

  // Unmount: abort in-flight Generate; gate late setState
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      generateAbortRef.current?.abort()
    }
  }, [])

  const structureMode = !!useCandidateResumeStructure
  const editable = !shapesKey && !structureMode
  const fixedFields = shapeFields && shapeFields.length > 0 ? shapeFields : null
  const rubricMode = !fixedFields
  const inReview = snapshot !== null

  /** Display order: importance descending (plan); storage order unchanged in `tabs` / payload. */
  const tabsSortedForRail = useMemo(() => {
    if (!rubricMode) return tabs
    return [...tabs].sort((a, b) => {
      const ia = rubricItemImportance(a)
      const ib = rubricItemImportance(b)
      if (ib !== ia) return ib - ia
      return a.label.localeCompare(b.label)
    })
  }, [tabs, rubricMode])

  /** While importance `<select>` is focused, keep rail positions stable; resort on blur. */
  const [railOrderFreeze, setRailOrderFreeze] = useState<string[] | null>(null)

  const tabsForRail = useMemo(() => {
    if (!rubricMode || railOrderFreeze === null) return tabsSortedForRail
    const byId = Object.fromEntries(tabs.map(t => [t.id, t]))
    return railOrderFreeze.map(id => byId[id]).filter(Boolean) as SideTab[]
  }, [tabs, rubricMode, tabsSortedForRail, railOrderFreeze])

  useEffect(() => {
    setRailOrderFreeze(null)
  }, [selectedId, artifactKey])

  // Candidate state drives Generate visibility
  const candidateState = useMemo(() => {
    const c = candidates.find(c => c.astral_candidate_id === selectedId)
    return c?.state ?? ""
  }, [candidates, selectedId])
  const generateStates = useMemo(
    () => new Set(manifest?.candidate.artifact_generate_states ?? []),
    [manifest?.candidate.artifact_generate_states],
  )
  const canGenerate = !jobPersistence && generateStates.has(candidateState)
  const hasData = useMemo(() => tabs.some(t => t.content.trim() !== ""), [tabs])

  // Fetch shape definitions for fixed-tab mode (global DATA_SHAPES)
  useEffect(() => {
    if (!shapesKey) return
    api("/api/shapes/candidates").then(r => r.json()).then(shapes => {
      const fields = shapes.detail?.[shapesKey] ?? []
      if (fields.length === 0) setShapeError(true)
      else setShapeFields(fields)
    }).catch(() => setShapeError(true))
  }, [shapesKey])

  // Per-candidate structure from parent prop
  useEffect(() => {
    if (!structureMode || structureSections === undefined) return
    if (structureSections === null) {
      setShapeFields(null)
      return
    }
    if (structureSections.length === 0) setShapeError(true)
    else {
      setShapeError(false)
      setShapeFields(structureSections.map(s => ({ key: s.id, label: s.label })))
    }
  }, [structureMode, structureSections])

  // Per-candidate structure fetch when page does not pass sections
  useEffect(() => {
    if (!structureMode || structureSections !== undefined || !selectedId) return
    setShapeFields(null)
    setShapeError(false)
    api(`/api/candidates/${selectedId}/resume_structure`).then(r => r.json()).then(data => {
      const sections = Array.isArray(data.sections) ? data.sections : []
      if (sections.length === 0) setShapeError(true)
      else setShapeFields(sections.map((s: { id: string; label: string }) => ({ key: s.id, label: s.label })))
    }).catch(() => setShapeError(true))
  }, [structureMode, structureSections, selectedId])

  function mapFixedFieldsFromRaw(raw: unknown) {
    if (!fixedFields) return
    const dict = Array.isArray(raw)
      ? Object.fromEntries(
          (raw as { label: string; content: string }[]).map(v => {
            const field = fixedFields.find(f => f.label === v.label)
            return [field ? field.key : v.label, v.content ?? ""]
          }),
        )
      : ((raw ?? {}) as Record<string, unknown>)
    setTabs(fixedFields.map(f => ({
      id: f.key,
      label: f.label,
      content: String(dict[f.key] ?? ""),
    })))
  }

  function mapJobDictArtifactFromRaw(raw: unknown) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
      setTabs([])
      return
    }
    setTabs(
      Object.entries(raw as Record<string, unknown>).map(([key, val]) => ({
        id: key,
        label: key,
        content: String(val ?? ""),
      })),
    )
  }

  // Load artifact data from job (AST-553/565 job persistence mode)
  useEffect(() => {
    if (!jobPersistence) return
    if ((shapesKey || structureMode) && !fixedFields) return
    setLoaded(false)
    setSnapshot(null)
    setJobLoadError(false)
    const persistKey = jobPersistence.artifactKey
    api(`/api/jobs/${encodeURIComponent(jobPersistence.jobId)}`).then(r => r.json()).then(job => {
      const artifacts = (job.job_data?.artifacts ?? {}) as Record<string, unknown>
      const raw = artifacts[persistKey]
      if (fixedFields) mapFixedFieldsFromRaw(raw)
      else mapJobDictArtifactFromRaw(raw)
      setLoaded(true)
      setDirty(false)
    }).catch(() => setJobLoadError(true))
  }, [jobPersistence, artifactKey, fixedFields, shapesKey, structureMode])

  // Load artifact data from candidate
  useEffect(() => {
    if (jobPersistence) return
    if (!selectedId || ((shapesKey || structureMode) && !fixedFields)) return
    setLoaded(false)
    setSnapshot(null)
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      const artifacts = (c.candidate_data?.artifacts ?? {}) as Record<string, unknown>
      const raw = artifacts[artifactKey]

      if (fixedFields) {
        mapFixedFieldsFromRaw(raw)
      } else {
        const arr = Array.isArray(raw) ? raw : []
        if (arr.length > 0) {
          setTabs(arr.map((v: { code?: string; label?: string; content?: string; importance?: number }, i: number) => ({
            id: `v_${i}`,
            code: v.code,
            label: v.label ?? `Criterion ${i + 1}`,
            content: v.content ?? "",
            importance: rubricItemImportance(v),
          })))
        } else {
          setTabs([{ id: "v_0", code: undefined, label: "New Criterion", content: "", importance: RUBRIC_DEFAULT_IMPORTANCE }])
        }
      }
      setLoaded(true)
      setDirty(false)
    })
  }, [jobPersistence, selectedId, artifactKey, fixedFields, shapesKey, structureMode])

  // Build the payload from current tabs
  function buildPayload(t: SideTab[]) {
    if (fixedFields || (jobPersistence && !shapesKey && !structureMode)) {
      const dict: Record<string, string> = {}
      t.forEach(tab => { dict[tab.id] = tab.content })
      return dict
    }
    return t.map(tab => ({
      ...(tab.code ? { code: tab.code } : {}),
      label: tab.label,
      content: tab.content,
      importance: rubricItemImportance(tab),
    }))
  }

  // Save to backend
  const doSave = useCallback(async (t: SideTab[]) => {
    if (jobPersistence) {
      setSaving(true)
      const key = jobPersistence.artifactKey
      try {
        const resp = await api(
          `/api/jobs/${encodeURIComponent(jobPersistence.jobId)}/artifacts/${encodeURIComponent(key)}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ [key]: buildPayload(t) }),
          },
        )
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
          throw new Error(err.error || `Save failed (${resp.status})`)
        }
        setDirty(false)
        setEverSaved(true)
        setSnapshot(null)
        setToast({ text: "Saved", variant: "success" })
        jobPersistence.onSaved?.()
      } catch (e) {
        setToast({ text: (e as Error).message || "Save failed", variant: "error" })
      } finally {
        setSaving(false)
      }
      return
    }
    if (!selectedId) return
    setSaving(true)
    try {
      const resp = await api(`/api/candidates/${selectedId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artifacts: { [artifactKey]: buildPayload(t) } }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
        throw new Error(err.error || `Save failed (${resp.status})`)
      }
      setDirty(false)
      setEverSaved(true)
      setSnapshot(null)
      setToast({ text: "Saved", variant: "success" })
    } catch (e) {
      // Keep review mode (snapshot) — do not clear on failure
      setToast({ text: (e as Error).message || "Save failed", variant: "error" })
    } finally {
      setSaving(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobPersistence, selectedId, artifactKey])

  function handleChange(next: SideTab[]) {
    setTabs(next)
    setDirty(true)
    // Skip auto-save while reviewing generated content
    if (editable && !inReview) {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => doSave(next), AUTOSAVE_MS)
    }
  }

  const resolvedExpandedTabId = useMemo(() => {
    if (tabs.length === 0) return ""
    if (expandedTabId && tabs.some(t => t.id === expandedTabId)) return expandedTabId
    return ""
  }, [tabs, expandedTabId])

  function updateTab(id: string, patch: Partial<SideTab>) {
    handleChange(tabs.map(t => (t.id === id ? { ...t, ...patch } : t)))
  }

  function moveTab(idx: number, dir: -1 | 1) {
    const target = idx + dir
    if (target < 0 || target >= tabs.length) return
    const next = [...tabs]
    ;[next[idx], next[target]] = [next[target], next[idx]]
    handleChange(next)
  }

  function removeTab(id: string) {
    if (tabs.length <= MIN_ARTIFACT_TABS) return
    const idx = tabs.findIndex(t => t.id === id)
    const next = tabs.filter(t => t.id !== id)
    if (resolvedExpandedTabId === id) {
      const neighbor = tabs[idx + 1] ?? tabs[idx - 1]
      setExpandedTabId(neighbor?.id ?? next[0]?.id ?? "")
    }
    handleChange(next)
  }

  function addCriterionTab() {
    if (tabs.length >= MAX_ARTIFACT_TABS) return
    const t: SideTab = { id: genArtifactTabId(), label: "New Criterion", content: "", importance: RUBRIC_DEFAULT_IMPORTANCE }
    handleChange([...tabs, t])
    setExpandedTabId(t.id)
    setEditingId(t.id)
  }

  // Auto-save on unmount when dirty — skip while in review (no silent persist of unreviewed Generate/recovery)
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      if (dirtyRef.current && snapshotRef.current === null) doSave(tabsRef.current)
    }
  }, [doSave])

  // beforeunload guard
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (dirtyRef.current) { e.preventDefault(); e.returnValue = "" }
    }
    window.addEventListener("beforeunload", handler)
    return () => window.removeEventListener("beforeunload", handler)
  }, [])

  // Page-return recovery: backend COMPLETED stash (AST-901) → review mode
  useEffect(() => {
    if (jobPersistence || fixedFields || !selectedId || !taskKey || !loaded) return
    const ac = new AbortController()
    ;(async () => {
      try {
        const resp = await api(
          `/api/candidates/${selectedId}/generate/${taskKey}/pending`,
          { signal: ac.signal },
        )
        if (ac.signal.aborted || !mountedRef.current) return
        if (resp.status === 404 || resp.status === 400) return
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
          setToast({ text: err.error || `HTTP ${resp.status}`, variant: "error" })
          return
        }
        const data = await resp.json()
        if (ac.signal.aborted || !mountedRef.current) return
        if (!data.success || !data.parsed_response) {
          if (data.error) setToast({ text: data.error, variant: "error" })
          return
        }
        const criteria = Array.isArray(data.parsed_response.criteria)
          ? data.parsed_response.criteria
          : []
        if (criteria.length === 0) return
        setSnapshot(tabsRef.current.map(t => ({ ...t })))
        setTabs(criteriaToTabs(criteria))
        setDirty(true)
        setToast({
          text: "Recovered completed generation — review and Save or Cancel",
          variant: "success",
        })
      } catch (e) {
        if (ac.signal.aborted || (e as Error).name === "AbortError") return
        if (mountedRef.current) {
          setToast({ text: (e as Error).message || "Recovery check failed", variant: "error" })
        }
      }
    })()
    return () => { ac.abort() }
  }, [jobPersistence, selectedId, taskKey, loaded, fixedFields])

  // --- Generate / Regenerate ---

  function handleGenerateClick() {
    if (hasData) {
      setConfirmRegen(true)
      return
    }
    doGenerate()
  }

  async function doGenerate() {
    if (!selectedId) return
    setConfirmRegen(false)
    setGenerating(true)
    // Snapshot current state for Cancel
    setSnapshot([...tabs.map(t => ({ ...t }))])

    generateAbortRef.current?.abort()
    const ac = new AbortController()
    generateAbortRef.current = ac

    try {
      const resp = await api(`/api/candidates/${selectedId}/generate/${taskKey}`, {
        method: "POST",
        signal: ac.signal,
      })
      if (!mountedRef.current) return
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
        throw new Error(err.error || "Generation failed")
      }
      const data = await resp.json()
      if (!mountedRef.current) return
      if (!data.success) throw new Error(data.error || "Generation failed")

      const parsed = data.parsed_response
      if (!parsed) throw new Error("No content returned")

      // Map response to tabs
      if (fixedFields) {
        // craft_resume_base returns a dict matching base_resume_structure keys
        setTabs(fixedFields.map(f => ({
          id: f.key,
          label: f.label,
          content: String((parsed as Record<string, unknown>)[f.key] ?? ""),
        })))
      } else {
        // craft_*_rubric returns { criteria: [{code?, label, content}, ...] }
        const criteria = Array.isArray(parsed.criteria) ? parsed.criteria : []
        if (criteria.length === 0) throw new Error("Generation returned no criteria")
        setTabs(criteriaToTabs(criteria))
      }
      setDirty(true)
      setToast({ text: "Generated — review and Save or Cancel", variant: "success" })
    } catch (e) {
      if (!mountedRef.current) return
      // Abort / navigate-away: silent — pending stash + recovery effect handle COMPLETED
      if (ac.signal.aborted || (e as Error).name === "AbortError") {
        setSnapshot(null)
        return
      }
      setSnapshot(null)
      const msg = (e as Error).message || ""
      const networkFail =
        (e as Error).name === "TypeError" || /failed to fetch/i.test(msg)
      setToast({
        text: networkFail
          ? "Generation request interrupted — if it finished on the server, return to this page to recover"
          : msg || "Generation failed",
        variant: "error",
      })
    } finally {
      if (mountedRef.current) setGenerating(false)
    }
  }

  function handleCancel() {
    if (snapshot) {
      setTabs(snapshot)
      setSnapshot(null)
      setDirty(false)
    } else {
      window.location.reload()
    }
  }

  if (!jobPersistence && !selectedId) return <p style={{ padding: 20, color: "#fff" }}>No candidate selected.</p>
  if (!jobPersistence) {
    if (loadState === "loading") return <p className="list-page-status">Loading...</p>
    if (loadState === "error" || !manifest) return <p className="list-page-status">State UI manifest unavailable.</p>
  }
  if (shapeError) {
    const shapeLabel = shapesKey ?? (structureMode ? "resume structure" : "fields")
    return <p style={{ padding: 20, color: "#ff6b6b" }}>Failed to load field definitions for "{shapeLabel}".</p>
  }
  if (jobLoadError) {
    return <p className="entity-error">Failed to load job artifact.</p>
  }
  if (!loaded) return <p style={{ padding: 20, color: "#fff" }}>Loading...</p>

  return (
    <>
      <div className="dep-page">
        <div className="dep-header">
          <h1 className="dep-title">{title}</h1>
          <div className="dep-actions">
            {canGenerate && (
              <button
                className={`dep-btn save${generating ? " in-flight" : ""}`}
                onClick={handleGenerateClick}
                disabled={generating}
                style={{ marginRight: 8 }}
              >
                {generating ? "Generating..." : hasData ? "Regenerate" : "Generate"}
              </button>
            )}
            {(fixedFields || inReview || jobPersistence) ? (
              <>
                <button className="dep-btn cancel" onClick={handleCancel}>Cancel</button>
                <button className="dep-btn save" onClick={() => doSave(tabs)} disabled={saving}>
                  {saving ? "Saving..." : "Save"}
                </button>
              </>
            ) : (
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                {saving ? "Saving..." : dirty ? "Unsaved changes" : everSaved ? "All changes saved" : ""}
              </span>
            )}
          </div>
        </div>
        <div className="dep-body">
          <div className="artifact-editor-collapsible-stack">
            {tabsForRail.map((tab, i) => (
              <CollapsiblePanel
                key={tab.id}
                label={
                  editable && editingId === tab.id ? (
                    <input
                      className="side-tab-rename"
                      value={tab.label}
                      onChange={e => updateTab(tab.id, { label: e.target.value })}
                      onBlur={() => setEditingId(null)}
                      onKeyDown={e => {
                        if (e.key === "Enter") setEditingId(null)
                      }}
                      autoFocus
                      onClick={e => e.stopPropagation()}
                    />
                  ) : (
                    <span
                      className="side-tab-label"
                      onDoubleClick={editable ? () => setEditingId(tab.id) : undefined}
                    >
                      {rubricMode
                        ? formatRubricVectorHeader(tab.importance, tab.label, tab.code)
                        : tab.label}
                    </span>
                  )
                }
                actions={
                  editable ? (
                    <span className="side-tab-controls">
                      {!rubricMode && (
                        <>
                          <button type="button" disabled={i === 0} onClick={() => moveTab(i, -1)} title="Move up">
                            ▲
                          </button>
                          <button
                            type="button"
                            disabled={i === tabs.length - 1}
                            onClick={() => moveTab(i, 1)}
                            title="Move down"
                          >
                            ▼
                          </button>
                        </>
                      )}
                      <button type="button" disabled={tabs.length <= MIN_ARTIFACT_TABS} onClick={() => removeTab(tab.id)} title="Remove">
                        ×
                      </button>
                    </span>
                  ) : undefined
                }
                expanded={resolvedExpandedTabId === tab.id}
                onExpandedChange={next => {
                  if (next) setExpandedTabId(tab.id)
                  else setExpandedTabId("")
                }}
              >
                <LabeledTextArea
                  label={tab.label}
                  value={tab.content}
                  onChange={v => updateTab(tab.id, { content: v })}
                  onLabelChange={undefined}
                  code={tab.code}
                  onCodeChange={editable ? v => updateTab(tab.id, { code: v }) : undefined}
                  importance={tab.importance}
                  onImportanceChange={
                    editable && rubricMode ? n => updateTab(tab.id, { importance: n }) : undefined
                  }
                  onImportanceFocus={
                    editable && rubricMode ? () => setRailOrderFreeze(tabsSortedForRail.map(t => t.id)) : undefined
                  }
                  onImportanceBlur={editable && rubricMode ? () => setRailOrderFreeze(null) : undefined}
                  hideTitle
                />
              </CollapsiblePanel>
            ))}
          </div>
          {editable && tabs.length < MAX_ARTIFACT_TABS && (
            <button type="button" className="side-tab-add artifact-editor-add-criterion" onClick={addCriterionTab}>
              + Add
            </button>
          )}
        </div>
      </div>

      {/* Regenerate confirmation */}
      {confirmRegen && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 1000,
          display: "flex", alignItems: "center", justifyContent: "center",
          background: "rgba(0,0,0,0.6)",
        }}>
          <div style={{
            background: "var(--bg-elevated)", border: "2px solid #ff6b6b",
            borderRadius: 8, padding: 24, maxWidth: 460, width: "90%",
          }}>
            <h3 style={{ margin: "0 0 12px", color: "#ff6b6b", fontSize: 16 }}>Regenerate {title}?</h3>
            <p style={{ margin: "0 0 16px", color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.5 }}>
              This will replace the current content with a new AI-generated version.
              You can review the result and <strong>Cancel</strong> to restore your previous version,
              or <strong>Save</strong> to keep it. Saving cannot be undone.
            </p>
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button className="dep-btn cancel" onClick={() => setConfirmRegen(false)}>
                Cancel
              </button>
              <button className="dep-btn save" onClick={doGenerate} style={{ background: "#ff6b6b" }}>
                Regenerate
              </button>
            </div>
          </div>
        </div>
      )}

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
