import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import CollapsiblePanel from "./CollapsiblePanel"
import type { Catalog, SectionRow } from "./ResumeStructureEditor"
import ExperienceJobsEditor, {
  type ExperienceJob,
  type ExperienceJobField,
} from "./ExperienceJobsEditor"
import LabeledTextArea from "./LabeledTextArea"
import type { SideTab } from "./SideTabPanel"
import Toast, { type ToastMessage } from "./Toast"
import { useCandidate } from "../contexts/CandidateContext"
import { useStateUi } from "../contexts/StateUiContext"
import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
import api from "../lib/api"
import { artifactBlobHasContent } from "../lib/artifactBlobHasContent"
import { formatRubricVectorHeader, RUBRIC_DEFAULT_IMPORTANCE, rubricItemImportance } from "../lib/rubricDisplay"

interface ShapeField { key: string; label: string; type?: string }

/** AST-1351: contract keys when ui_config fetch fails (Title-Case labels). */
const EXPERIENCE_JOB_FIELD_FALLBACK: ExperienceJobField[] = [
  { key: "company", label: "Company" },
  { key: "title", label: "Title" },
  { key: "dates", label: "Dates" },
  { key: "location", label: "Location" },
  { key: "accomplishments", label: "Accomplishments" },
]

function isExperienceTab(key: string, fieldType?: string): boolean {
  return fieldType === "experience_jobs" || key === "experience"
}

function normalizeExperienceJob(
  raw: Record<string, unknown>,
  fieldKeys: string[],
): ExperienceJob {
  const out: ExperienceJob = {}
  for (const k of fieldKeys) {
    const v = raw[k]
    if (k === "accomplishments") {
      // AST-1381: persist string[]; coerce legacy newline string on read.
      if (Array.isArray(v)) {
        out[k] = v.map(x => String(x)).map(s => s.trim()).filter(Boolean)
      } else if (typeof v === "string" && v.trim()) {
        out[k] = v.replace(/\r\n/g, "\n").split("\n").map(s => s.trim()).filter(Boolean)
      } else {
        out[k] = []
      }
      continue
    }
    out[k] = typeof v === "string" ? v : v == null ? "" : String(v)
  }
  return out
}

function parseExperienceJobs(
  content: string,
  fieldKeys: string[],
): { ok: true; jobs: ExperienceJob[] } | { ok: false; raw: string } {
  const t = content.trim()
  if (!t) return { ok: true, jobs: [] }
  try {
    const parsed = JSON.parse(t) as unknown
    if (!Array.isArray(parsed)) return { ok: false, raw: content }
    if (!parsed.every(item => item != null && typeof item === "object" && !Array.isArray(item))) {
      return { ok: false, raw: content }
    }
    return {
      ok: true,
      jobs: parsed.map(item => normalizeExperienceJob(item as Record<string, unknown>, fieldKeys)),
    }
  } catch {
    return { ok: false, raw: content }
  }
}

function sectionValueToTabContent(val: unknown): string {
  if (typeof val === "string") return val
  if (val == null) return ""
  return JSON.stringify(val, null, 2)
}

function tabContentToSectionValue(key: string, content: string, fieldType?: string): unknown {
  // experience_jobs from DATA_SHAPES, or structureMode tabs that only carry key/label
  if (isExperienceTab(key, fieldType)) {
    const t = content.trim()
    if (!t) return []
    return JSON.parse(t)
  }
  return content
}

interface StructureSection { id: string; label: string }

interface ArtifactEditorProps {
  title: string
  artifactKey: string
  taskKey: string              // craft_* task to call for Generate
  shapesKey?: string           // key in DATA_SHAPES.candidates.detail — if set, tabs are fixed
  useCandidateResumeStructure?: boolean
  /** Catalog body_shape (BUILD_CONFIG artifact_shapes / ARTIFACT_CONFIG). Pilot: resume_content. AST-1577 / patt.artifacts.ui-consistency — structure-dict mode by shape. */
  bodyShape?: string
  structureSections?: StructureSection[] | null
  /** AST-1323: Base Resume Content structure authoring on collapsible headers. */
  structureCatalog?: Catalog | null
  structureRows?: SectionRow[]
  onStructureRowsChange?: (rows: SectionRow[]) => void
  onStructureSave?: (rows: SectionRow[]) => void
  structureSaving?: boolean
  structureError?: string | null
  /** Job-scoped artifact load/save (AST-553/565); no Generate. */
  jobPersistence?: { jobId: string; artifactKey: string; onSaved?: () => void }
  /** Optional controls after Generate/Regenerate in dep-actions (e.g. Base Resume Print). */
  headerActions?: ReactNode
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
  bodyShape,
  structureSections = undefined,
  structureCatalog = null,
  structureRows,
  onStructureRowsChange,
  onStructureSave,
  structureSaving = false,
  structureError = null,
  jobPersistence,
  headerActions,
}: ArtifactEditorProps) {
  const { manifest, loadState } = useStateUi()
  const { selectedId, candidates, refresh: refreshCandidate } = useCandidate()
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
  const [hasChainData, setHasChainData] = useState(false)
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

  const structureMode =
    !!useCandidateResumeStructure || bodyShape === "resume_content"
  // Tab chrome (rename/add/remove/rubric) stays off in structure/shapes mode; bodies use bodiesEditable.
  const tabChromeEditable = !shapesKey && !structureMode
  const structureAuthoring = !!(
    structureMode
    && structureCatalog
    && structureRows
    && onStructureRowsChange
    && onStructureSave
  )
  const [addTitle, setAddTitle] = useState("")
  const [addFormat, setAddFormat] = useState(
    structureCatalog?.new_extra_default_format || structureCatalog?.body_formats?.[0] || "",
  )
  // AST-1351: experience job UI spine from BUILD_CONFIG via ui_config
  const [experienceJobFields, setExperienceJobFields] = useState<ExperienceJobField[]>(
    EXPERIENCE_JOB_FIELD_FALLBACK,
  )
  const [unsupportedExperienceMessage, setUnsupportedExperienceMessage] = useState(
    "unsupported resume structure, please regenerate",
  )
  useEffect(() => {
    api("/api/system/ui_config")
      .then(r => r.json())
      .then(cfg => {
        const fields = cfg.experience_job_ui_fields
        if (Array.isArray(fields) && fields.length > 0) {
          setExperienceJobFields(
            fields
              .filter((f: { key?: string; label?: string }) => typeof f?.key === "string")
              .map((f: { key: string; label?: string }) => ({
                key: f.key,
                label:
                  typeof f.label === "string" && f.label
                    ? f.label
                    : f.key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
              })),
          )
        }
        if (
          typeof cfg.unsupported_resume_structure_message === "string"
          && cfg.unsupported_resume_structure_message
        ) {
          setUnsupportedExperienceMessage(cfg.unsupported_resume_structure_message)
        }
      })
      .catch(() => {
        setExperienceJobFields(EXPERIENCE_JOB_FIELD_FALLBACK)
      })
  }, [])
  useEffect(() => {
    if (!structureCatalog) return
    setAddFormat(structureCatalog.new_extra_default_format || structureCatalog.body_formats[0] || "")
  }, [structureCatalog])

  function reindexStructureRows(next: SectionRow[]) {
    return next.map((row, i) => ({ ...row, order: i }))
  }

  function patchStructureRow(sid: string, patch: Partial<SectionRow>) {
    if (!structureRows || !onStructureRowsChange) return
    onStructureRowsChange(structureRows.map(r => (r.id === sid ? { ...r, ...patch } : r)))
  }

  function moveStructureRow(sid: string, delta: number) {
    if (!structureRows || !onStructureRowsChange) return
    const index = structureRows.findIndex(r => r.id === sid)
    const j = index + delta
    if (index < 0 || j < 0 || j >= structureRows.length) return
    const next = structureRows.slice()
    const tmp = next[index]
    next[index] = next[j]
    next[j] = tmp
    onStructureRowsChange(reindexStructureRows(next))
  }

  function removeStructureRow(sid: string) {
    if (!structureRows || !onStructureRowsChange) return
    onStructureRowsChange(reindexStructureRows(structureRows.filter(r => r.id !== sid)))
  }

  function addStructureSection() {
    if (!structureRows || !onStructureRowsChange || !structureCatalog) return
    const title = addTitle.trim()
    if (!title) return
    onStructureRowsChange(reindexStructureRows([
      ...structureRows,
      {
        id: `_pending_${structureRows.length}`,
        title,
        enabled: true,
        order: structureRows.length,
        format: addFormat || structureCatalog.new_extra_default_format || structureCatalog.body_formats[0] || "",
        job_agent_editable: true,
        required: false,
        format_locked: false,
        page_break_policy: structureCatalog.page_break_policy_default || "",
      },
    ]))
    setAddTitle("")
  }

  const fixedFields = shapeFields && shapeFields.length > 0 ? shapeFields : null
  const rubricMode = !fixedFields
  const inReview = snapshot !== null
  // Bodies editable in rubric chrome mode OR structure/shapes/job fixed tabs; never during Generate review.
  const bodiesEditable = !inReview && (tabChromeEditable || !!fixedFields || !!jobPersistence)
  // Stable id-set signature: label-only and reorder-only edits do not re-GET / wipe tabs.
  const fixedFieldKeys = fixedFields
    ? [...fixedFields.map(f => f.key)].sort().join("\0")
    : ""

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

  // Candidate Artifacts criteria only — not job-persistence (Recommended Job Modal).
  const criteriaExpandAll = !jobPersistence && rubricMode

  const criteriaSectionKeys = useMemo(
    () => (criteriaExpandAll ? tabsForRail.map(t => t.id) : []),
    [criteriaExpandAll, tabsForRail],
  )
  const {
    isExpanded,
    onExpandedChange,
    expandAllSections,
    setExpandedKeys,
  } = useSectionExpandPolicy({
    expandAll: criteriaExpandAll,
    sectionKeys: criteriaSectionKeys,
  })
  const didSeedCriteriaExpandRef = useRef("")

  useEffect(() => {
    didSeedCriteriaExpandRef.current = ""
    setExpandedKeys(new Set())
    setRailOrderFreeze(null)
  }, [selectedId, artifactKey, setExpandedKeys])

  // One-shot expand-all seed per load (AdminScheduledActions didAutoOpenSectionRef).
  useEffect(() => {
    if (!criteriaExpandAll || !loaded) return
    if (criteriaSectionKeys.length === 0) return
    const seedKey = `${selectedId ?? ""}:${artifactKey}`
    if (didSeedCriteriaExpandRef.current === seedKey) return
    didSeedCriteriaExpandRef.current = seedKey
    expandAllSections()
  }, [
    criteriaExpandAll,
    loaded,
    selectedId,
    artifactKey,
    criteriaSectionKeys.length,
    expandAllSections,
  ])

  // Candidate state drives Generate visibility
  const candidateState = useMemo(() => {
    const c = candidates.find(c => c.astral_candidate_id === selectedId)
    return c?.state ?? ""
  }, [candidates, selectedId])
  const generateStates = useMemo(
    () => new Set(manifest?.candidate.artifact_generate_states ?? []),
    [manifest?.candidate.artifact_generate_states],
  )
  const inflightHideStates = useMemo(
    () => new Set(manifest?.candidate.artifact_generate_inflight_hide_states ?? []),
    [manifest?.candidate.artifact_generate_inflight_hide_states],
  )
  const chainTaskKeys = useMemo(
    () => new Set(manifest?.candidate.artifacts_chain_task_keys ?? []),
    [manifest?.candidate.artifacts_chain_task_keys],
  )
  const chainHopLabels = manifest?.candidate.artifacts_chain_hop_labels ?? []
  const chainArtifactKeys = useMemo(
    () => manifest?.candidate.artifacts_chain_artifact_keys ?? [],
    [manifest?.candidate.artifacts_chain_artifact_keys],
  )
  // Same parse failure that drives the unsupported experience notice (message + affordance).
  const experienceUnsupported = useMemo(() => {
    const fieldKeys = experienceJobFields.map(f => f.key)
    return tabs.some(tab => {
      const fieldType = fixedFields?.find(f => f.key === tab.id)?.type
      if (!isExperienceTab(tab.id, fieldType)) return false
      return !parseExperienceJobs(tab.content, fieldKeys).ok
    })
  }, [tabs, fixedFields, experienceJobFields])
  // AST-1253: craft-chain pages hand off to REQUESTED_ARTIFACTS (not per-artifact generate)
  const isChainHandoff = !jobPersistence && chainTaskKeys.has(taskKey)
  // Base Resume: show Generate/Regenerate when experience is unsupported, except in-flight hide states.
  const baseResumeUnsupportedEscape =
    !jobPersistence
    && (bodyShape === "resume_content" || artifactKey === "base_resume")
    && experienceUnsupported
    && !inflightHideStates.has(candidateState)
  const canGenerate =
    !jobPersistence
    && (generateStates.has(candidateState) || baseResumeUnsupportedEscape)
  const hasData = useMemo(() => tabs.some(t => t.content.trim() !== ""), [tabs])
  const showAsRegenerate = isChainHandoff ? hasChainData : hasData

  // Fetch shape definitions for fixed-tab mode (global DATA_SHAPES)
  useEffect(() => {
    if (!shapesKey) return
    api("/api/shapes/candidates").then(r => r.json()).then(shapes => {
      const fields = shapes.detail?.[shapesKey] ?? []
      if (fields.length === 0) setShapeError(true)
      else setShapeFields(fields)
    }).catch(() => setShapeError(true))
  }, [shapesKey])

  // Per-candidate structure: prefer authoring rows (all sections) so Enabled toggles stay visible;
  // otherwise parent structureSections or internal fetch.
  useEffect(() => {
    if (!structureMode) return
    if (structureAuthoring && structureRows && structureRows.length > 0) {
      setShapeError(false)
      setShapeFields(structureRows.map(r => ({
        key: r.id,
        label: r.title,
        ...(r.id === "experience" ? { type: "experience_jobs" as const } : {}),
      })))
      return
    }
    if (structureSections === undefined) return
    if (structureSections === null) {
      setShapeFields(null)
      return
    }
    if (structureSections.length === 0) setShapeError(true)
    else {
      setShapeError(false)
      // AST-1351: mark experience so Save + editor use job-array path
      setShapeFields(structureSections.map(s => ({
        key: s.id,
        label: s.label,
        ...(s.id === "experience" ? { type: "experience_jobs" as const } : {}),
      })))
    }
  }, [structureMode, structureSections, structureAuthoring, structureRows])

  // Per-candidate structure fetch when page does not pass sections
  useEffect(() => {
    if (!structureMode || structureSections !== undefined || !selectedId) return
    if (structureAuthoring) return
    setShapeFields(null)
    setShapeError(false)
    api(`/api/candidates/${selectedId}/resume_structure`).then(r => r.json()).then(data => {
      const sections = Array.isArray(data.sections) ? data.sections : []
      if (sections.length === 0) setShapeError(true)
      else setShapeFields(sections.map((s: { id: string; label: string }) => ({
        key: s.id,
        label: s.label,
        ...(s.id === "experience" ? { type: "experience_jobs" as const } : {}),
      })))
    }).catch(() => setShapeError(true))
  }, [structureMode, structureSections, selectedId, structureAuthoring])

  function mapFixedFieldsFromRaw(raw: unknown) {
    if (!fixedFields) return
    // Dict or legacy [{label,content}]; reject pin strings / non-objects so bodies stay empty not garbage.
    const dict = Array.isArray(raw)
      ? Object.fromEntries(
          (raw as { label: string; content: string }[]).map(v => {
            const field = fixedFields.find(f => f.label === v.label)
            return [field ? field.key : v.label, v.content ?? ""]
          }),
        )
      : (raw && typeof raw === "object"
        ? (raw as Record<string, unknown>)
        : {})
    setTabs(fixedFields.map(f => ({
      id: f.key,
      label: f.label,
      content: sectionValueToTabContent(dict[f.key]),
    })))
  }

  /** Same field key set: refresh labels; reorder tabs to match structure rows without re-GET. */
  useEffect(() => {
    if (!fixedFields) return
    setTabs(prev => {
      if (prev.length === 0) return prev
      const prevSet = [...prev.map(t => t.id)].sort().join("\0")
      const nextSet = [...fixedFields.map(f => f.key)].sort().join("\0")
      if (prevSet !== nextSet) return prev
      const byId = Object.fromEntries(prev.map(t => [t.id, t]))
      return fixedFields.map(f => {
        const existing = byId[f.key]
        return {
          id: f.key,
          label: f.label,
          content: existing?.content ?? "",
          code: existing?.code,
          importance: existing?.importance,
        }
      })
    })
  }, [fixedFields])

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

  function applyJobArtifactResponse(job: { job_data?: { artifacts?: Record<string, unknown> } }) {
    const persistKey = jobPersistence!.artifactKey
    const artifacts = (job.job_data?.artifacts ?? {}) as Record<string, unknown>
    // AST-1593: trust GET hydrate current under leaf key — do not promote resume_content as SoT.
    const raw = artifacts[persistKey]
    if (fixedFields) mapFixedFieldsFromRaw(raw)
    else mapJobDictArtifactFromRaw(raw)
  }

  function applyCandidateArtifactResponse(c: {
    candidate_data?: { artifacts?: Record<string, unknown> }
    company_search_terms?: unknown
  }) {
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
    const rubricHit = chainArtifactKeys.some(k => artifactBlobHasContent(artifacts[k]))
    const terms = c.company_search_terms
    const termsHit = typeof terms === "string" && terms.trim() !== ""
    setHasChainData(rubricHit || termsHit)
  }

  const jobPersistJobId = jobPersistence?.jobId

  // Load artifact data from job (AST-553/565 job persistence mode)
  useEffect(() => {
    if (!jobPersistence) return
    if ((shapesKey || structureMode) && !fixedFieldKeys) return
    setLoaded(false)
    setSnapshot(null)
    setJobLoadError(false)
    api(`/api/jobs/${encodeURIComponent(jobPersistence.jobId)}`).then(r => r.json()).then(job => {
      applyJobArtifactResponse(job)
      setLoaded(true)
      setDirty(false)
    }).catch(() => setJobLoadError(true))
  // jobPersistJobId: parent inline jobPersistence object must not re-GET on reorder churn
  // fixedFieldKeys: ignore label/reorder shapeField churn
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobPersistJobId, artifactKey, fixedFieldKeys, shapesKey, structureMode])

  // Load artifact data from candidate
  useEffect(() => {
    if (jobPersistence) return
    if (!selectedId || ((shapesKey || structureMode) && !fixedFieldKeys)) return
    setLoaded(false)
    // Don't let a stale loaded render claim seedKey for the new page/candidate (Radia / Joan).
    didSeedCriteriaExpandRef.current = ""
    setSnapshot(null)
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      applyCandidateArtifactResponse(c)
      setLoaded(true)
      setDirty(false)
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobPersistence, selectedId, artifactKey, fixedFieldKeys, shapesKey, structureMode, chainArtifactKeys])

  // Build the payload from current tabs
  function buildPayload(t: SideTab[]) {
    if (fixedFields || (jobPersistence && !shapesKey && !structureMode)) {
      const dict: Record<string, unknown> = {}
      t.forEach(tab => {
        const fieldType = fixedFields?.find(f => f.key === tab.id)?.type
        dict[tab.id] = tabContentToSectionValue(tab.id, tab.content, fieldType)
      })
      return dict
    }
    return t.map(tab => ({
      ...(tab.code ? { code: tab.code } : {}),
      label: tab.label,
      content: tab.content,
      importance: rubricItemImportance(tab),
    }))
  }

  // Save to backend — AST-1381: when structure authoring is on, persist formats with content Save.
  const doSave = useCallback(async (t: SideTab[]) => {
    const fieldKeys = experienceJobFields.map(f => f.key)
    for (const tab of t) {
      const fieldType = fixedFields?.find(f => f.key === tab.id)?.type
      if (isExperienceTab(tab.id, fieldType)) {
        const parsed = parseExperienceJobs(tab.content, fieldKeys)
        if (!parsed.ok) {
          setToast({ text: unsupportedExperienceMessage, variant: "error" })
          return
        }
      }
    }
    let payload: ReturnType<typeof buildPayload>
    try {
      payload = buildPayload(t)
    } catch {
      setToast({ text: unsupportedExperienceMessage, variant: "error" })
      return
    }
    if (jobPersistence) {
      setSaving(true)
      const key = jobPersistence.artifactKey
      try {
        const resp = await api(
          `/api/jobs/${encodeURIComponent(jobPersistence.jobId)}/artifacts/${encodeURIComponent(key)}`,
          {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ [key]: payload }),
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
      const arts: Record<string, unknown> = { [artifactKey]: payload }
      if (structureAuthoring && structureRows) {
        const sections: Record<string, Record<string, unknown>> = {}
        structureRows.forEach((row, index) => {
          const spec: Record<string, unknown> = {
            id: row.id,
            title: row.title,
            enabled: row.enabled,
            order: index,
            job_agent_editable: row.job_agent_editable,
            page_break_policy: row.page_break_policy,
          }
          if (row.format) spec.format = row.format
          sections[row.id] = spec
        })
        arts.resume_structure = { sections }
      }
      const resp = await api(`/api/candidates/${selectedId}/data`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artifacts: arts }),
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
  }, [
    jobPersistence,
    selectedId,
    artifactKey,
    experienceJobFields,
    unsupportedExperienceMessage,
    fixedFields,
    structureAuthoring,
    structureRows,
  ])

  function handleChange(next: SideTab[]) {
    setTabs(next)
    setDirty(true)
    // Skip auto-save while reviewing generated content
    if (tabChromeEditable && !inReview) {
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
    if (criteriaExpandAll) {
      setExpandedKeys(prev => new Set([...prev, t.id]))
    } else {
      setExpandedTabId(t.id)
    }
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
  // AST-905: only when loaded criteria are empty — never overwrite existing/edits
  useEffect(() => {
    if (jobPersistence || fixedFields || !selectedId || !taskKey || !loaded) return
    // Already have criterion content → skip pending fetch/apply
    if (tabsRef.current.some(t => (t.content || "").trim() !== "")) return
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
        // Belt: do not apply if tabs gained content since load
        if (tabsRef.current.some(t => (t.content || "").trim() !== "")) return
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
    if (isChainHandoff) {
      if (hasChainData) {
        setConfirmRegen(true)
        return
      }
      void doRequestArtifacts()
      return
    }
    if (hasData) {
      setConfirmRegen(true)
      return
    }
    void doGenerate()
  }

  /** AST-1253: handoff to REQUESTED_ARTIFACTS (dispatch chain). */
  async function doRequestArtifacts() {
    if (!selectedId) return
    setConfirmRegen(false)
    setGenerating(true)
    try {
      const resp = await api(`/api/candidates/${selectedId}/generate_artifacts`, { method: "POST" })
      if (!mountedRef.current) return
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: `HTTP ${resp.status}` }))
        throw new Error(err.error || "Request failed")
      }
      const data = await resp.json()
      if (!mountedRef.current) return
      if (!data.ok) throw new Error(data.error || "Request failed")
      setToast({ text: "Artifacts build requested — watch Execution History", variant: "success" })
      refreshCandidate()
    } catch (e) {
      if (!mountedRef.current) return
      setToast({ text: (e as Error).message || "Request failed", variant: "error" })
    } finally {
      if (mountedRef.current) setGenerating(false)
    }
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
          content: sectionValueToTabContent((parsed as Record<string, unknown>)[f.key]),
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
      return
    }
    if (jobPersistence) {
      if ((shapesKey || structureMode) && !fixedFieldKeys) return
      api(`/api/jobs/${encodeURIComponent(jobPersistence.jobId)}`).then(r => r.json()).then(job => {
        applyJobArtifactResponse(job)
        setDirty(false)
      }).catch(() => setJobLoadError(true))
      return
    }
    if (!selectedId || ((shapesKey || structureMode) && !fixedFieldKeys)) return
    api(`/api/candidates/${selectedId}`).then(r => r.json()).then(c => {
      applyCandidateArtifactResponse(c)
      setDirty(false)
    })
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
                className={`btn primary${generating ? " in-flight" : ""}`}
                onClick={handleGenerateClick}
                disabled={generating}
                style={{ marginRight: 8 }}
              >
                {generating
                  ? (isChainHandoff ? "Requesting..." : "Generating...")
                  : showAsRegenerate ? "Regenerate" : "Generate"}
              </button>
            )}
            {headerActions}
            {(fixedFields || inReview || jobPersistence) ? (
              <>
                <button className="btn secondary" onClick={handleCancel}>Cancel</button>
                <button className="btn primary" onClick={() => doSave(tabs)} disabled={saving}>
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
            {tabsForRail.map((tab, i) => {
              const structureRow = structureAuthoring
                ? structureRows!.find(r => r.id === tab.id)
                : undefined
              const formatValue = structureRow
                ? (structureRow.format_locked
                  ? (structureRow.format ?? "")
                  : (structureRow.format && structureCatalog!.body_formats.includes(structureRow.format)
                    ? structureRow.format
                    : structureCatalog!.new_extra_default_format))
                : ""
              const structureRowIndex = structureRow
                ? structureRows!.findIndex(r => r.id === structureRow.id)
                : -1
              return (
              <CollapsiblePanel
                key={tab.id}
                label={
                  structureRow ? (
                    <div
                      className="structure-authoring-header"
                      onClick={e => e.stopPropagation()}
                      onKeyDown={e => e.stopPropagation()}
                    >
                      <input
                        className="dep-input structure-authoring-name"
                        type="text"
                        value={structureRow.title}
                        onChange={e => patchStructureRow(structureRow.id, { title: e.target.value })}
                      />
                      <select
                        className="dep-input structure-authoring-style"
                        value={formatValue}
                        disabled={structureRow.format_locked}
                        onChange={e => patchStructureRow(structureRow.id, { format: e.target.value })}
                      >
                        {structureCatalog!.body_formats.map(f => (
                          <option key={f} value={f}>{f}</option>
                        ))}
                      </select>
                      {structureCatalog!.page_break_policies?.length ? (() => {
                        const policyValue = (
                          structureRow.page_break_policy
                          && structureCatalog!.page_break_policies.includes(structureRow.page_break_policy)
                        )
                          ? structureRow.page_break_policy
                          : structureCatalog!.page_break_policy_default
                        return (
                          <select
                            className="dep-input structure-authoring-style"
                            aria-label="Page break"
                            value={policyValue}
                            onChange={e => patchStructureRow(structureRow.id, { page_break_policy: e.target.value })}
                          >
                            {structureCatalog!.page_break_policies.map(token => (
                              <option key={token} value={token}>
                                {structureCatalog!.page_break_policy_labels?.[token] ?? token}
                              </option>
                            ))}
                          </select>
                        )
                      })() : null}
                      <label className="structure-authoring-flag">
                        Enabled:
                        <input
                          type="checkbox"
                          checked={structureRow.enabled}
                          disabled={structureRow.required}
                          onChange={e => patchStructureRow(structureRow.id, { enabled: e.target.checked })}
                        />
                      </label>
                      <label className="structure-authoring-flag">
                        Job Edit:
                        <input
                          type="checkbox"
                          checked={structureRow.job_agent_editable}
                          onChange={e => patchStructureRow(structureRow.id, { job_agent_editable: e.target.checked })}
                        />
                      </label>
                      <button
                        type="button"
                        disabled={structureRowIndex <= 0}
                        onClick={() => moveStructureRow(structureRow.id, -1)}
                      >
                        Up
                      </button>
                      <button
                        type="button"
                        disabled={structureRowIndex < 0 || structureRowIndex >= structureRows!.length - 1}
                        onClick={() => moveStructureRow(structureRow.id, 1)}
                      >
                        Down
                      </button>
                      {!structureRow.required && (
                        <button type="button" onClick={() => removeStructureRow(structureRow.id)}>
                          Remove
                        </button>
                      )}
                    </div>
                  ) : tabChromeEditable && editingId === tab.id ? (
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
                      onDoubleClick={tabChromeEditable ? () => setEditingId(tab.id) : undefined}
                    >
                      {rubricMode
                        ? formatRubricVectorHeader(tab.importance, tab.label, tab.code)
                        : tab.label}
                    </span>
                  )
                }
                actions={
                  structureRow ? undefined : tabChromeEditable ? (
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
                expanded={criteriaExpandAll ? isExpanded(tab.id) : resolvedExpandedTabId === tab.id}
                onExpandedChange={next => {
                  if (criteriaExpandAll) onExpandedChange(tab.id, next)
                  else if (next) setExpandedTabId(tab.id)
                  else setExpandedTabId("")
                }}
              >
                {(() => {
                  const fieldType = fixedFields?.find(f => f.key === tab.id)?.type
                  if (isExperienceTab(tab.id, fieldType)) {
                    const fieldKeys = experienceJobFields.map(f => f.key)
                    const parsed = parseExperienceJobs(tab.content, fieldKeys)
                    if (parsed.ok) {
                      return (
                        <ExperienceJobsEditor
                          fields={experienceJobFields}
                          value={parsed.jobs}
                          onChange={
                            bodiesEditable
                              ? jobs => updateTab(tab.id, { content: JSON.stringify(jobs) })
                              : () => {}
                          }
                          disabled={!bodiesEditable}
                        />
                      )
                    }
                    return (
                      <>
                        <p className="experience-jobs-editor-unsupported">
                          {unsupportedExperienceMessage}
                        </p>
                        <LabeledTextArea
                          label={tab.label}
                          value={parsed.raw}
                          onChange={() => {}}
                          onLabelChange={undefined}
                          disabled
                          hideTitle
                        />
                      </>
                    )
                  }
                  return (
                    <LabeledTextArea
                      label={tab.label}
                      value={tab.content}
                      onChange={bodiesEditable ? v => updateTab(tab.id, { content: v }) : () => {}}
                      onLabelChange={undefined}
                      code={tab.code}
                      onCodeChange={tabChromeEditable ? v => updateTab(tab.id, { code: v }) : undefined}
                      importance={tab.importance}
                      onImportanceChange={
                        tabChromeEditable && rubricMode ? n => updateTab(tab.id, { importance: n }) : undefined
                      }
                      onImportanceFocus={
                        tabChromeEditable && rubricMode ? () => setRailOrderFreeze(tabsSortedForRail.map(t => t.id)) : undefined
                      }
                      onImportanceBlur={tabChromeEditable && rubricMode ? () => setRailOrderFreeze(null) : undefined}
                      disabled={!bodiesEditable}
                      hideTitle
                    />
                  )
                })()}
              </CollapsiblePanel>
              )
            })}
          </div>
          {structureAuthoring && (
            <div className="base-resume-structure-add">
              <input
                className="dep-input"
                type="text"
                value={addTitle}
                onChange={e => setAddTitle(e.target.value)}
              />
              <select
                className="dep-input"
                value={addFormat}
                onChange={e => setAddFormat(e.target.value)}
              >
                {structureCatalog!.body_formats.map(f => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
              <button type="button" onClick={addStructureSection}>Add section</button>
              <button
                type="button"
                className="base-resume-structure-save"
                disabled={structureSaving}
                onClick={() => onStructureSave!(structureRows!)}
              >
                Save sections
              </button>
              {structureError ? <div>{structureError}</div> : null}
            </div>
          )}
          {tabChromeEditable && tabs.length < MAX_ARTIFACT_TABS && (
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
            {isChainHandoff ? (
              <>
                <h3 style={{ margin: "0 0 12px", color: "#ff6b6b", fontSize: 16 }}>
                  Reset all artifact rubrics?
                </h3>
                <p style={{ margin: "0 0 16px", color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.5 }}>
                  This rebuilds the full craft chain and resets all of these rubrics:{" "}
                  <strong>{chainHopLabels.join(", ") || "all chain hops"}</strong>.
                  History is kept, but regeneration is expensive. Default is No.
                </p>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                  <button
                    className="btn secondary"
                    autoFocus
                    onClick={() => setConfirmRegen(false)}
                  >
                    No
                  </button>
                  <button
                    className="btn danger"
                    onClick={() => void doRequestArtifacts()}
                  >
                    Yes
                  </button>
                </div>
              </>
            ) : (
              <>
                <h3 style={{ margin: "0 0 12px", color: "#ff6b6b", fontSize: 16 }}>Regenerate {title}?</h3>
                <p style={{ margin: "0 0 16px", color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.5 }}>
                  This will replace the current content with a new AI-generated version.
                  You can review the result and <strong>Cancel</strong> to restore your previous version,
                  or <strong>Save</strong> to keep it. Saving cannot be undone.
                </p>
                <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                  <button className="btn secondary" onClick={() => setConfirmRegen(false)}>
                    Cancel
                  </button>
                  <button className="btn danger" onClick={() => void doGenerate()}>
                    Regenerate
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <Toast message={toast} onDone={clearToast} />
    </>
  )
}
