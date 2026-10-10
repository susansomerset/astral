import { useCallback, useEffect, useRef, useState } from "react"
import type { ExperienceJob, ExperienceJobField } from "./ExperienceJobsEditor"
import ResumeSectionRow, { type EditorCatalog, type RowCompare, type SectionBody } from "./ResumeSectionRow"
import type { SectionRow } from "./ResumeStructureEditor"
import Toast, { type ToastMessage } from "./Toast"
import { useUserConfirm } from "./UserPrompt"
import api from "../lib/api"
import { fetchPrintHtml, openHtmlInNewTab } from "../lib/printHtml"
import { getUiConfig, loadUiConfig, type UiConfig } from "../lib/uiConfig"

/** Which resume to edit: `id` is the candidate id for `base`, else the job id. */
export interface ResumeEditorTarget {
  kind: "base" | "job"
  id: string
}

export interface ResumeContentEditorProps {
  target: ResumeEditorTarget
  /** Called once after each save that wrote at least one PUT (preview refresh). */
  onSaved?: () => void
}

/** ui_config keys this editor reads (served by /api/ui_config; not on the shared UiConfig type). */
type ResumeUiConfig = UiConfig & {
  base_resume_accent_palette?: string[]
  experience_job_ui_fields?: { key: string; label?: string }[]
  unsupported_resume_structure_message?: string
}

// Same contract keys ArtifactEditor falls back to when ui_config is unavailable (AST-1351).
const EXPERIENCE_FIELD_FALLBACK: ExperienceJobField[] = [
  { key: "company", label: "Company" },
  { key: "title", label: "Title" },
  { key: "dates", label: "Dates" },
  { key: "location", label: "Location" },
  { key: "accomplishments", label: "Accomplishments" },
]
const UNSUPPORTED_FALLBACK = "unsupported resume structure, please regenerate"
// Client-only id for an added row until the server slugs its title into a real id (never matches the id pattern).
const PENDING = "_pending_"

type Loaded = {
  rows: SectionRow[]
  bodies: Record<string, SectionBody>
  accent: string | null
  catalog: EditorCatalog
  candidateId: string
}
type BaseSnapshot = { rows: SectionRow[]; bodies: Record<string, SectionBody> }
type Item = { kind: "row"; row: SectionRow } | { kind: "removed"; base: SectionRow; anchor: string | null }

async function getJson(path: string) {
  const r = await api(path)
  if (!r.ok) throw new Error(`HTTP ${r.status}`)
  return r.json()
}

async function putJson(path: string, payload: unknown) {
  const r = await api(path, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({})) as { error?: string }
    throw new Error(err.error || `Save failed (${r.status})`)
  }
}

function toJob(raw: Record<string, unknown>): ExperienceJob {
  const out: ExperienceJob = {}
  for (const [k, v] of Object.entries(raw)) {
    // AST-1381: accomplishments persist as string[]; coerce a legacy newline string on read.
    out[k] = k === "accomplishments"
      ? (Array.isArray(v) ? v.map(String) : typeof v === "string" ? v.split("\n") : []).map(s => s.trim()).filter(Boolean)
      : v == null ? "" : String(v)
  }
  return out
}

/** Stored resume dict (or legacy [{label, content}]) → id-keyed bodies for the given rows. */
function parseBodies(raw: unknown, rows: SectionRow[]): Record<string, SectionBody> {
  const dict: Record<string, unknown> = Array.isArray(raw)
    ? Object.fromEntries((raw as { label?: string; content?: unknown }[]).map(v => [
        rows.find(r => r.title === v.label)?.id ?? String(v.label), v.content,
      ]))
    : raw && typeof raw === "object" ? raw as Record<string, unknown> : {}
  const out: Record<string, SectionBody> = {}
  for (const row of rows) {
    const v = dict[row.id]
    if (row.id === "experience") {
      const isJobs = Array.isArray(v) && v.every(j => j != null && typeof j === "object" && !Array.isArray(j))
      // Unparseable legacy experience stays a string so the row shows the unsupported notice.
      out[row.id] = isJobs ? (v as Record<string, unknown>[]).map(toJob) : typeof v === "string" && v.trim() ? v : []
    } else {
      out[row.id] = typeof v === "string" ? v : v == null ? "" : JSON.stringify(v, null, 2)
    }
  }
  return out
}

/** Plain text of one experience job: head fields joined " · ", then "• " accomplishments. */
function jobText(job: ExperienceJob, fields: ExperienceJobField[]): string {
  const head = fields.filter(f => f.key !== "accomplishments").map(f => String(job[f.key] ?? "").trim()).filter(Boolean)
  const acc = Array.isArray(job.accomplishments) ? job.accomplishments.map(a => `• ${a}`) : []
  return [head.join(" · "), ...acc].filter(Boolean).join("\n")
}

/** Plain text of a body: search haystack, compare display, and (whitespace-collapsed) row preview. */
function bodyText(body: SectionBody | undefined, fields: ExperienceJobField[]): string {
  if (body === undefined) return ""
  if (typeof body === "string") return body
  return body.map(job => jobText(job, fields)).join("\n\n")
}

/** Compare equality: trimmed text, or the job array as JSON; empty array equals empty text. */
function bodyKey(body: SectionBody | undefined): string {
  if (body === undefined) return ""
  if (typeof body === "string") return body.trim()
  return body.length ? JSON.stringify(body) : ""
}

function reindex(rows: SectionRow[]): SectionRow[] {
  return rows.map((r, i) => ({ ...r, order: i }))
}

/** Remount per target so a switch never saves one resume's state onto another. */
export default function ResumeContentEditor({ target, onSaved }: ResumeContentEditorProps) {
  return <Editor key={`${target.kind}:${target.id}`} target={target} onSaved={onSaved} />
}

function Editor({ target, onSaved }: ResumeContentEditorProps) {
  const { kind, id } = target
  const isJob = kind === "job"
  const enc = encodeURIComponent(id)
  const structUrl = isJob ? `/api/jobs/${enc}/resume_structure` : `/api/candidates/${enc}/resume_structure`
  const confirm = useUserConfirm()

  const [data, setData] = useState<Loaded | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [ui, setUi] = useState<ResumeUiConfig | null>(null)
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [search, setSearch] = useState("")
  const [compareOn, setCompareOn] = useState(false)
  const [base, setBase] = useState<BaseSnapshot | null>(null)
  const [printing, setPrinting] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const clearToast = useCallback(() => setToast(null), [])

  // Every data write goes through dataRef first, so blur / unmount saves always send the latest edit.
  const dataRef = useRef<Loaded | null>(null)
  const onSavedRef = useRef(onSaved)
  useEffect(() => { onSavedRef.current = onSaved })
  const structDirtyRef = useRef(false)
  const bodyDirtyRef = useRef(false)
  const saveChainRef = useRef<Promise<void>>(Promise.resolve())
  const mountedRef = useRef(true)
  const pendingSeqRef = useRef(0)
  const dragIdRef = useRef<string | null>(null)

  const experienceFields: ExperienceJobField[] = ui?.experience_job_ui_fields?.length
    ? ui.experience_job_ui_fields.map(f => ({ key: f.key, label: f.label || f.key }))
    : EXPERIENCE_FIELD_FALLBACK
  const unsupportedMessage = ui?.unsupported_resume_structure_message || UNSUPPORTED_FALLBACK
  const palette = ui?.base_resume_accent_palette ?? []

  useEffect(() => {
    let live = true
    loadUiConfig(() => { if (live) setUi(getUiConfig() as ResumeUiConfig | null) })
    return () => { live = false }
  }, [])

  // patt.artifact.read-current: body from the entity GET hydrate, structure from the structure GET.
  useEffect(() => {
    let live = true
    const entityUrl = isJob ? `/api/jobs/${enc}` : `/api/candidates/${enc}`
    Promise.all([getJson(entityUrl), getJson(structUrl)]).then(([entity, struct]) => {
      if (!live) return
      const arts = (isJob ? entity.job_data?.artifacts : entity.candidate_data?.artifacts) ?? {}
      const rows = (Array.isArray(struct.all_sections) ? struct.all_sections : []) as SectionRow[]
      dataRef.current = {
        rows,
        bodies: parseBodies(arts[isJob ? "job_resume" : "base_resume"], rows),
        accent: typeof struct.accent_color === "string" ? struct.accent_color.toUpperCase() : null,
        catalog: struct.catalog as EditorCatalog,
        candidateId: isJob ? String(entity.candidate_id ?? "") : id,
      }
      setData(dataRef.current)
    }).catch(e => { if (live) setLoadError(`Failed to load resume: ${(e as Error).message}`) })
    return () => { live = false }
  }, [isJob, enc, id, structUrl])

  // Compare to Base: current base resume + base structure, refetched each time the toggle turns on.
  const candidateId = data?.candidateId
  useEffect(() => {
    if (!compareOn || !candidateId) return
    let live = true
    const cid = encodeURIComponent(candidateId)
    Promise.all([getJson(`/api/candidates/${cid}`), getJson(`/api/candidates/${cid}/resume_structure`)])
      .then(([c, struct]) => {
        if (!live) return
        const rows = (Array.isArray(struct.all_sections) ? struct.all_sections : []) as SectionRow[]
        setBase({ rows, bodies: parseBodies(c.candidate_data?.artifacts?.base_resume, rows) })
      })
      .catch(e => { if (live) setToast({ text: `Compare failed: ${(e as Error).message}`, variant: "error" }) })
    return () => { live = false }
  }, [compareOn, candidateId])

  /** Update editor state from the latest ref; mark which half changed; optionally save now (header controls, moves, adds, deletes). */
  const apply = (
    update: (cur: Loaded) => Partial<Loaded> | null,
    dirty: { struct?: boolean; body?: boolean },
    save: boolean,
  ) => {
    const cur = dataRef.current
    const next = cur && update(cur)
    if (!cur || !next) return
    dataRef.current = { ...cur, ...next }
    setData(dataRef.current)
    if (dirty.struct) structDirtyRef.current = true
    if (dirty.body) bodyDirtyRef.current = true
    if (save) void flush()
  }

  /** After a save that carried new rows: adopt the server's slugged ids (position order) for those rows. */
  async function adoptServerIds(sentPending: string[]) {
    const struct = await getJson(structUrl)
    const cur = dataRef.current
    if (!cur) return
    const known = new Set(cur.rows.map(r => r.id))
    const fresh = (struct.all_sections as SectionRow[]).filter(s => !known.has(s.id)).map(s => s.id)
    const rename = new Map(sentPending.map((pid, i) => [pid, fresh[i]] as const).filter(([, sid]) => !!sid))
    if (rename.size === 0) return
    // Content is locked while pending, so only the (empty) body key moves with the id.
    apply(c => {
      const bodies = { ...c.bodies }
      for (const [pid, sid] of rename) {
        bodies[sid] = bodies[pid]
        delete bodies[pid]
      }
      return { rows: c.rows.map(r => ({ ...r, id: rename.get(r.id) ?? r.id })), bodies }
    }, {}, false)
    setExpanded(prev => new Set([...prev].map(x => rename.get(x) ?? x)))
  }

  /** One save: sends only the half that changed. Base: one candidate /data PUT; job: structure PUT then job_resume PUT. */
  async function saveOnce(): Promise<void> {
    const cur = dataRef.current
    const structDirty = structDirtyRef.current
    let bodyDirty = bodyDirtyRef.current
    if (!cur || (!structDirty && !bodyDirty)) return
    // A new row is not sent until it has a label (the server requires a title).
    const rows = cur.rows.filter(r => !(r.id.startsWith(PENDING) && !r.title.trim()))
    const sentPending = rows.filter(r => r.id.startsWith(PENDING)).map(r => r.id)
    const experience = cur.bodies.experience
    if (bodyDirty && typeof experience === "string" && experience.trim()) {
      // Unparseable legacy experience: never overwrite it; structure edits still save.
      setToast({ text: unsupportedMessage, variant: "error" })
      bodyDirty = false
    }
    structDirtyRef.current = false
    if (bodyDirty) bodyDirtyRef.current = false
    if (!structDirty && !bodyDirty) return
    const structure = {
      sections: Object.fromEntries(rows.map((r, i) => [r.id, {
        id: r.id,
        title: r.title,
        enabled: r.enabled,
        order: i,
        job_agent_editable: r.job_agent_editable,
        page_break_policy: r.page_break_policy,
        ...(r.format ? { format: r.format } : {}),
      }])),
      ...(cur.accent ? { accent_color: cur.accent } : {}),
    }
    const body = Object.fromEntries(
      rows.filter(r => !r.id.startsWith(PENDING) && cur.bodies[r.id] !== undefined).map(r => [r.id, cur.bodies[r.id]]),
    )
    try {
      if (isJob) {
        if (structDirty) await putJson(`/api/jobs/${enc}/artifacts/job_resume_structure`, { job_resume_structure: structure })
        if (bodyDirty) await putJson(`/api/jobs/${enc}/artifacts/job_resume`, { job_resume: body })
      } else {
        await putJson(`/api/candidates/${enc}/data`, {
          artifacts: { ...(bodyDirty ? { base_resume: body } : {}), ...(structDirty ? { resume_structure: structure } : {}) },
        })
      }
      if (sentPending.length) await adoptServerIds(sentPending)
    } catch (e) {
      // Keep the unsaved halves dirty so the next field exit retries them.
      if (structDirty) structDirtyRef.current = true
      if (bodyDirty) bodyDirtyRef.current = true
      if (mountedRef.current) setToast({ text: (e as Error).message || "Save failed", variant: "error" })
      return
    }
    if (mountedRef.current) onSavedRef.current?.()
  }

  /** Serialize saves so PUTs land in edit order; returns when this save (and any before it) settles. */
  function flush(): Promise<void> {
    const run = saveChainRef.current.then(saveOnce)
    saveChainRef.current = run.catch(() => {})
    return run
  }
  const flushRef = useRef(flush)
  useEffect(() => { flushRef.current = flush })

  // Leaving the page/modal saves pending edits; closing the tab with unsaved edits prompts.
  useEffect(() => {
    mountedRef.current = true
    const guard = (e: BeforeUnloadEvent) => {
      if (structDirtyRef.current || bodyDirtyRef.current) e.preventDefault()
    }
    window.addEventListener("beforeunload", guard)
    return () => {
      window.removeEventListener("beforeunload", guard)
      mountedRef.current = false
      void flushRef.current()
    }
  }, [])

  if (loadError) return <p className="entity-error">{loadError}</p>
  if (!data) return <p className="list-page-status">Loading...</p>
  const { rows, bodies, catalog, accent } = data

  const patchRow = (rid: string, patch: Partial<SectionRow>, save: boolean) =>
    apply(c => ({ rows: c.rows.map(r => (r.id === rid ? { ...r, ...patch } : r)) }), { struct: true }, save)

  const moveRow = (fromId: string | null, toIndex: number) => apply(c => {
    const from = c.rows.findIndex(r => r.id === fromId)
    if (from < 0 || toIndex < 0 || toIndex >= c.rows.length || from === toIndex) return null
    const next = c.rows.slice()
    const [moved] = next.splice(from, 1)
    next.splice(toIndex, 0, moved)
    return { rows: reindex(next) }
  }, { struct: true }, true)

  const addSection = () => {
    const rid = `${PENDING}${pendingSeqRef.current++}`
    apply(c => ({
      rows: reindex([...c.rows, {
        id: rid,
        title: "",
        enabled: true,
        order: c.rows.length,
        format: c.catalog.new_extra_default_format,
        job_agent_editable: true,
        required: false,
        format_locked: false,
        page_break_policy: c.catalog.page_break_policy_default,
      }]),
      bodies: { ...c.bodies, [rid]: "" },
    }), {}, false)
    setSearch("")
    setExpanded(prev => new Set(prev).add(rid))
  }

  const deleteRow = async (row: SectionRow) => {
    const ok = await confirm(`Delete the "${row.title || "untitled"}" section?`, {
      title: "Delete section",
      confirmLabel: "Delete",
      variant: "danger",
    })
    if (!ok) return
    apply(c => {
      const rest = { ...c.bodies }
      delete rest[row.id]
      return { rows: reindex(c.rows.filter(r => r.id !== row.id)), bodies: rest }
    }, { struct: true, body: true }, true)
  }

  const addFromBase = (b: SectionRow, anchor: string | null) => {
    if (!base) return
    const baseBody = base.bodies[b.id] ?? (b.id === "experience" ? [] : "")
    apply(c => {
      const next = c.rows.slice()
      next.splice(anchor ? c.rows.findIndex(r => r.id === anchor) + 1 : 0, 0, { ...b })
      return { rows: reindex(next), bodies: { ...c.bodies, [b.id]: baseBody } }
    }, { struct: true, body: true }, true)
  }

  const pickAccent = (hex: string) => apply(() => ({ accent: hex.toUpperCase() }), { struct: true }, true)

  async function print() {
    setPrinting(true)
    await flush()
    const r = await fetchPrintHtml({ kind: isJob ? "job_resume" : "base", id })
    const err = r.ok ? openHtmlInNewTab(r.html) : r.error
    if (err) setToast({ text: err, variant: "error" })
    setPrinting(false)
  }

  const q = search.trim().toLowerCase()
  const matches = (title: string, body: SectionBody | undefined) =>
    !q || title.toLowerCase().includes(q) || bodyText(body, experienceFields).toLowerCase().includes(q)
  // AST-2114: a query that matches inside Experience jobs (not the section title) shows only those jobs.
  const visibleJobs = (title: string, body: SectionBody | undefined): ReadonlySet<number> | undefined =>
    !q || title.toLowerCase().includes(q) || !Array.isArray(body)
      ? undefined
      : new Set(body.flatMap((job, i) => (jobText(job, experienceFields).toLowerCase().includes(q) ? [i] : [])))
  const preview = (body: SectionBody | undefined) => bodyText(body, experienceFields).replace(/\s+/g, " ").trim()

  // Compare to Base (job only): differs / NEW SECTION per job row by id; base-only rows become SECTION REMOVED.
  const showCompare = isJob && compareOn && base !== null
  const baseById = new Map((base?.rows ?? []).map(r => [r.id, r]))
  const compareFor = (row: SectionRow): RowCompare | null => {
    if (!showCompare || row.id.startsWith(PENDING)) return null
    if (!baseById.has(row.id)) return { kind: "new" }
    return bodyKey(bodies[row.id]) === bodyKey(base!.bodies[row.id])
      ? null
      : { kind: "differs", baseText: bodyText(base!.bodies[row.id], experienceFields) }
  }
  // Each removed base row sits after the nearest earlier base row the job still has (null → top).
  const items: Item[] = []
  const removedAfter = new Map<string | null, Item[]>()
  if (showCompare) {
    const jobIds = new Set(rows.map(r => r.id))
    let anchor: string | null = null
    for (const b of base!.rows) {
      if (jobIds.has(b.id)) anchor = b.id
      else removedAfter.set(anchor, [...(removedAfter.get(anchor) ?? []), { kind: "removed", base: b, anchor }])
    }
  }
  items.push(...(removedAfter.get(null) ?? []))
  for (const row of rows) items.push({ kind: "row", row }, ...(removedAfter.get(row.id) ?? []))

  return (
    <div className="resume-editor">
      <div className="resume-editor-header">
        <input
          className="dep-input resume-editor-search"
          type="search"
          placeholder="Search sections"
          aria-label="Search sections"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button type="button" className="btn secondary" onClick={addSection}>Add Section</button>
        {palette.length > 0 && (
          <div className="base-resume-accent-swatches" role="group" aria-label="Resume accent color">
            {palette.map(hex => (
              <button
                key={hex}
                type="button"
                className={`base-resume-accent-swatch${accent === hex.toUpperCase() ? " selected" : ""}`}
                style={{ backgroundColor: hex }}
                title={hex}
                aria-label={hex}
                aria-pressed={accent === hex.toUpperCase()}
                onClick={() => pickAccent(hex)}
              />
            ))}
          </div>
        )}
        {isJob && (
          <button
            type="button"
            className={"btn secondary" + (compareOn ? " active" : "")}
            aria-pressed={compareOn}
            onClick={() => { setCompareOn(on => !on); setBase(null) }}
          >
            Compare to Base
          </button>
        )}
        <button type="button" className="btn secondary" onClick={() => void print()} disabled={printing}>
          {printing ? "Opening…" : "Print"}
        </button>
      </div>
      <div className="resume-editor-rows" onBlur={() => void flush()}>
        {items.map(item => {
          if (item.kind === "removed") {
            const b = item.base
            if (!matches(b.title, base!.bodies[b.id])) return null
            return (
              <div key={`removed:${b.id}`} className="resume-section-removed">
                <span className="resume-section-removed-text">
                  SECTION REMOVED: {b.title}: {preview(base!.bodies[b.id])}
                </span>
                <button type="button" className="btn secondary" onClick={() => addFromBase(b, item.anchor)}>Add</button>
              </div>
            )
          }
          const row = item.row
          if (!matches(row.title, bodies[row.id])) return null
          const index = rows.indexOf(row)
          return (
            <ResumeSectionRow
              key={row.id}
              row={row}
              body={bodies[row.id] ?? (row.id === "experience" ? [] : "")}
              preview={preview(bodies[row.id])}
              catalog={catalog}
              experienceFields={experienceFields}
              visibleJobs={visibleJobs(row.title, bodies[row.id])}
              unsupportedMessage={unsupportedMessage}
              expanded={expanded.has(row.id)}
              isFirst={index === 0}
              isLast={index === rows.length - 1}
              showJobEdit={!isJob}
              contentLocked={row.id.startsWith(PENDING)}
              compare={compareFor(row)}
              onToggle={() => setExpanded(prev => {
                const next = new Set(prev)
                if (!next.delete(row.id)) next.add(row.id)
                return next
              })}
              onPatch={(patch, save) => patchRow(row.id, patch, save)}
              onBodyChange={b => apply(c => ({ bodies: { ...c.bodies, [row.id]: b } }), { body: true }, false)}
              onMove={delta => moveRow(row.id, index + delta)}
              onDelete={() => void deleteRow(row)}
              onDragStart={() => { dragIdRef.current = row.id }}
              onDrop={() => {
                const fromId = dragIdRef.current
                dragIdRef.current = null
                if (fromId) moveRow(fromId, index)
              }}
            />
          )
        })}
      </div>
      <Toast message={toast} onDone={clearToast} />
    </div>
  )
}
