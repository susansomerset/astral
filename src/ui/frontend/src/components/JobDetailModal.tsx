import { useCallback, useEffect, useState } from "react"
import Modal from "./Modal"
import SideTabPanel, { type SideTab } from "./SideTabPanel"
import StateTimeline from "./StateTimeline"
import AgentStoryTab, { type AgentStoryEntry } from "./AgentStoryTab"
import Time from "./Time"
import api from "../lib/api"
import { copyJobSnapshotToClipboard } from "../lib/copyJobSnapshot"
import { useStateUi } from "../contexts/StateUiContext"

interface JobDetail {
  astral_job_id: string
  job_title: string | null
  company: string
  job_link: string | null
  state: string
  state_changed_at: string | null
  created_at: string | null
  state_history?: Array<{ to_state?: string; timestamp?: string }>
  job_data?: Record<string, unknown>
  agent_story?: AgentStoryEntry[]
  fields_editable?: boolean
  legal_next_states?: string[]
}

type FieldDraft = {
  job_title: string
  job_link: string
  job_description: string
  state: string
}

function draftFromJob(j: JobDetail): FieldDraft {
  return {
    job_title: j.job_title ?? "",
    job_link: j.job_link ?? "",
    job_description: String(
      ((j.job_data as Record<string, unknown> | undefined)?.job_description) ?? ""
    ),
    state: j.state,
  }
}

interface Props {
  jobId: string | null
  onClose: () => void
  onRefresh?: () => void
}

export default function JobDetailModal({ jobId, onClose, onRefresh }: Props) {
  const [job, setJob] = useState<JobDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [skipping, setSkipping] = useState(false)
  const [snapshotCopied, setSnapshotCopied] = useState(false)
  const [snapshotCopying, setSnapshotCopying] = useState(false)
  const [draft, setDraft] = useState<FieldDraft | null>(null)
  const [baseline, setBaseline] = useState<FieldDraft | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!jobId) return
    setLoading(true)
    try {
      const res = await api(`/api/jobs/${encodeURIComponent(jobId)}`)
      if (res.ok) {
        const data = (await res.json()) as JobDetail
        setJob(data)
        const d = draftFromJob(data)
        setDraft(d)
        setBaseline(d)
        setSaveError(null)
      }
    } finally {
      setLoading(false)
    }
  }, [jobId])

  useEffect(() => { load() }, [load])
  useEffect(() => { setSnapshotCopied(false) }, [jobId])

  const fieldsEditable = Boolean(job?.fields_editable)
  const isDraftDirty = Boolean(
    fieldsEditable
    && draft
    && baseline
    && (
      draft.job_title !== baseline.job_title
      || draft.job_link !== baseline.job_link
      || draft.job_description !== baseline.job_description
      || draft.state !== baseline.state
    )
  )

  async function handleSave() {
    if (!jobId || !draft || !fieldsEditable || saving) return
    setSaving(true)
    setSaveError(null)
    try {
      const payload: Record<string, string> = {
        job_title: draft.job_title,
        job_link: draft.job_link,
        job_description: draft.job_description,
      }
      if (draft.state !== (job?.state ?? "")) {
        payload.state = draft.state
      }
      const res = await api(`/api/jobs/${encodeURIComponent(jobId)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      const body = (await res.json().catch(() => ({}))) as Record<string, unknown>
      if (res.ok) {
        const saved = body as unknown as JobDetail
        setJob(saved)
        const d = draftFromJob(saved)
        setDraft(d)
        setBaseline(d)
        onRefresh?.()
        return
      }
      const msg = typeof body.error === "string" ? body.error : "Save failed"
      if (
        msg.startsWith("Invalid transition")
        || msg.includes("not in allowed list")
        || msg === "Job is not in a skipped state"
      ) {
        await load()
        onRefresh?.()
        setSaveError(msg)
      } else {
        setSaveError(msg)
      }
    } finally {
      setSaving(false)
    }
  }

  async function handleCopySnapshot() {
    if (!jobId || snapshotCopying) return
    setSnapshotCopying(true)
    const ok = await copyJobSnapshotToClipboard(jobId)
    setSnapshotCopying(false)
    if (!ok) return
    setSnapshotCopied(true)
    window.setTimeout(() => setSnapshotCopied(false), 2000)
  }

  async function handleSkip() {
    if (!jobId || skipping) return
    setSkipping(true)
    try {
      await api(`/api/jobs/${encodeURIComponent(jobId)}/skip`, { method: "POST" })
      onRefresh?.()
      onClose()
    } finally {
      setSkipping(false)
    }
  }

  const agentStory = job?.agent_story ?? []
  const hasJD = Boolean((job?.job_data as Record<string, unknown>)?.job_description)
  const showJdTab = fieldsEditable || hasJD
  const sideTabs: SideTab[] = [
    { id: "__info__", label: "Info", content: "" },
    ...(showJdTab ? [{ id: "__jd__", label: "Job Description", content: "" }] : []),
    ...agentStory.map((entry, i) => ({
      id: `story_${i}`,
      label: entry.task_key,
      content: "",
    })),
  ]

  function renderSideContent(tabId: string) {
    if (tabId === "__info__") {
      return (
        <InfoTab
          job={job}
          fieldsEditable={fieldsEditable}
          draft={draft}
          legalNextStates={job?.legal_next_states ?? []}
          saveError={saveError}
          onDraftChange={(patch) => {
            setDraft((prev) => (prev ? { ...prev, ...patch } : prev))
          }}
          onSkip={handleSkip}
          skipping={skipping}
          onCopy={handleCopySnapshot}
          copied={snapshotCopied}
          copying={snapshotCopying}
        />
      )
    }
    if (tabId === "__jd__") {
      if (fieldsEditable && draft) {
        return (
          <textarea
            className="dep-input dep-textarea"
            value={draft.job_description}
            onChange={(e) =>
              setDraft((prev) =>
                prev ? { ...prev, job_description: e.target.value } : prev
              )
            }
            rows={16}
            style={{ width: "100%", minHeight: 240 }}
          />
        )
      }
      const jd = ((job?.job_data as Record<string, unknown>)?.job_description as string) ?? ""
      // Collapse runs of 3+ newlines to 2, trim leading/trailing whitespace
      const normalized = jd.trim().replace(/\n{3,}/g, "\n\n")
      return <div className="entity-jd-content">{normalized}</div>
    }
    const storyOffset = showJdTab ? 2 : 1
    const idx = sideTabs.findIndex(t => t.id === tabId) - storyOffset
    const entry = agentStory[idx]
    if (!entry) return null
    return <AgentStoryTab entry={entry} />
  }

  return (
    <Modal
      open={!!jobId}
      onClose={onClose}
      title={job?.job_title || job?.company || "Job Detail"}
      size="wide"
      dirty={isDraftDirty}
      onSave={fieldsEditable ? () => { void handleSave() } : undefined}
    >
      {loading && <p className="entity-loading">Loading…</p>}
      {job && (
        <SideTabPanel
          tabs={sideTabs}
          renderContent={renderSideContent}
        />
      )}
      {!loading && !job && jobId && <p className="entity-error">Job not found.</p>}
    </Modal>
  )
}

// ---- Info tab ----
function InfoTab({
  job,
  fieldsEditable,
  draft,
  legalNextStates,
  saveError,
  onDraftChange,
  onSkip,
  skipping,
  onCopy,
  copied,
  copying,
}: {
  job: JobDetail | null
  fieldsEditable: boolean
  draft: FieldDraft | null
  legalNextStates: string[]
  saveError: string | null
  onDraftChange: (patch: Partial<FieldDraft>) => void
  onSkip: () => void
  skipping: boolean
  onCopy: () => void
  copied: boolean
  copying: boolean
}) {
  const { manifest, loadState } = useStateUi()
  if (!job) return null
  const alreadySkipped = manifest ? job.state === manifest.jobs.detail.already_skipped_state : false
  const legacyState = loadState === "ready" && manifest
    && !Object.prototype.hasOwnProperty.call(manifest.jobs.grade_field_by_job_state, job.state)
    && job.state !== manifest.jobs.detail.already_skipped_state

  return (
    <div className="entity-summary">
      <div className="entity-summary-top">
        {/* Left column: metadata + skip */}
        <div className="entity-summary-col">
          <div className="modal-detail-row"><span className="modal-detail-label">Company</span><span>{job.company}</span></div>
          <div className="modal-detail-row">
            <span className="modal-detail-label">Title</span>
            {fieldsEditable && draft ? (
              <input
                className="dep-input"
                value={draft.job_title}
                onChange={(e) => onDraftChange({ job_title: e.target.value })}
              />
            ) : (
              <span>{job.job_title || "—"}</span>
            )}
          </div>
          <div className="modal-detail-row">
            <span className="modal-detail-label">State</span>
            <span>
              {job.state}
              {legacyState && (
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}> (legacy — not in current manifest)</span>
              )}
            </span>
          </div>
          {fieldsEditable && draft && (
            <div className="modal-detail-row">
              <span className="modal-detail-label">Change to</span>
              <select
                className="dep-input"
                value={draft.state === job.state ? "" : draft.state}
                onChange={(e) => onDraftChange({ state: e.target.value || job.state })}
              >
                <option value="">No change</option>
                {[...legalNextStates].sort((a, b) => a.localeCompare(b)).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          )}
          {fieldsEditable && draft ? (
            <div className="modal-detail-row">
              <span className="modal-detail-label">Link</span>
              <input
                className="dep-input"
                value={draft.job_link}
                onChange={(e) => onDraftChange({ job_link: e.target.value })}
              />
            </div>
          ) : (
            job.job_link && (
              <div className="modal-detail-row">
                <span className="modal-detail-label">Link</span>
                <span><a href={job.job_link} target="_blank" rel="noreferrer">{job.job_link}</a></span>
              </div>
            )
          )}
          <div className="modal-detail-row"><span className="modal-detail-label">Created</span><span><Time value={job.created_at} /></span></div>
          <div className="modal-detail-row"><span className="modal-detail-label">Last Transition</span><span><Time value={job.state_changed_at} /></span></div>

          {saveError && <p className="entity-error">{saveError}</p>}

          <div className="entity-summary-actions">
            <button
              type="button"
              className="btn secondary"
              onClick={onCopy}
              disabled={copying}
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <div style={{ marginTop: 20 }}>
            <button
              className="btn secondary"
              onClick={onSkip}
              disabled={skipping || alreadySkipped}
            >
              {alreadySkipped ? "Already Skipped" : skipping ? "Skipping…" : "Skip This Job"}
            </button>
          </div>
        </div>
        {/* Right column: state history */}
        <div className="entity-summary-col">
          <p className="entity-section-label">State History</p>
          <StateTimeline history={job.state_history || []} />
        </div>
      </div>
    </div>
  )
}
