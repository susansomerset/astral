import { useCallback, useEffect, useState } from "react"
import Modal from "./Modal"
import SideTabPanel, { type SideTab } from "./SideTabPanel"
import StateTimeline from "./StateTimeline"
import AgentStoryTab, { type AgentStoryEntry } from "./AgentStoryTab"
import Time from "./Time"
import api from "../lib/api"
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

  const load = useCallback(async () => {
    if (!jobId) return
    setLoading(true)
    try {
      const res = await api(`/api/jobs/${encodeURIComponent(jobId)}`)
      if (res.ok) setJob(await res.json())
    } finally {
      setLoading(false)
    }
  }, [jobId])

  useEffect(() => { load() }, [load])

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
  const sideTabs: SideTab[] = [
    { id: "__info__", label: "Info", content: "" },
    ...(hasJD ? [{ id: "__jd__", label: "Job Description", content: "" }] : []),
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
          onSkip={handleSkip}
          skipping={skipping}
        />
      )
    }
    if (tabId === "__jd__") {
      const jd = ((job?.job_data as Record<string, unknown>)?.job_description as string) ?? ""
      // Collapse runs of 3+ newlines to 2, trim leading/trailing whitespace
      const normalized = jd.trim().replace(/\n{3,}/g, "\n\n")
      return <div className="entity-jd-content">{normalized}</div>
    }
    const storyOffset = hasJD ? 2 : 1
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
  onSkip,
  skipping,
}: {
  job: JobDetail | null
  onSkip: () => void
  skipping: boolean
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
          <div className="modal-detail-row"><span className="modal-detail-label">Title</span><span>{job.job_title || "—"}</span></div>
          <div className="modal-detail-row">
            <span className="modal-detail-label">State</span>
            <span>
              {job.state}
              {legacyState && (
                <span style={{ color: "var(--text-muted)", fontSize: 12 }}> (legacy — not in current manifest)</span>
              )}
            </span>
          </div>
          {job.job_link && (
            <div className="modal-detail-row">
              <span className="modal-detail-label">Link</span>
              <span><a href={job.job_link} target="_blank" rel="noreferrer">{job.job_link}</a></span>
            </div>
          )}
          <div className="modal-detail-row"><span className="modal-detail-label">Created</span><span><Time value={job.created_at} /></span></div>
          <div className="modal-detail-row"><span className="modal-detail-label">Last Transition</span><span><Time value={job.state_changed_at} /></span></div>

          <div style={{ marginTop: 20 }}>
            <button
              className="entity-skip-btn"
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
