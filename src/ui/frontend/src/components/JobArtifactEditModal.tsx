import { useEffect, useState } from "react"
import ArtifactEditor from "./ArtifactEditor"
import Modal from "./Modal"
import PrintPreview from "./PrintPreview"
import ResumeContentEditor from "./ResumeContentEditor"
import SplitPanePage from "./SplitPanePage"
import Toast, { type ToastMessage } from "./Toast"
import { fetchPrintHtml, openHtmlInNewTab } from "../lib/printHtml"

/** One manifest `report_artifact_tabs` row. `preview_thumbnail` (AST-2081 config) is not on the shared StateUi type yet. */
export interface JobArtifactTab {
  tab_id: string
  nav_label: string
  artifact_key: string
  shapes_key: string | null
  use_resume_structure: boolean
  preview_thumbnail?: boolean
}

interface Props {
  jobId: string
  /** Tab being edited; null keeps the modal closed. */
  tab: JobArtifactTab | null
  onClose: () => void
}

/** AST-2084 / AST-2115 edit path; AST-2234 mobile = read-only drafted text + Print only. */
export default function JobArtifactEditModal({ jobId, tab, onClose }: Props) {
  const [refreshKey, setRefreshKey] = useState(0)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [isMobile, setIsMobile] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(max-width: 1023px)").matches,
  )
  const bump = () => setRefreshKey(k => k + 1)

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 1023px)")
    const sync = () => setIsMobile(mq.matches)
    sync()
    mq.addEventListener("change", sync)
    return () => mq.removeEventListener("change", sync)
  }, [])

  const printKind = tab?.use_resume_structure ? "job_resume" as const : "cover" as const

  async function handlePrint() {
    if (!tab) return
    const r = await fetchPrintHtml({ kind: printKind, id: jobId })
    const err = r.ok ? openHtmlInNewTab(r.html) : r.error
    if (err) setToast({ text: err, variant: "error" })
  }

  return (
    <Modal open={!!tab} onClose={onClose} title={tab?.nav_label ?? ""} size="overlay" stacked showFooter={false}>
      {tab && isMobile && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ display: "flex", gap: 8 }}>
            <button type="button" className="btn secondary" onClick={() => { void handlePrint() }}>
              Print
            </button>
          </div>
          <PrintPreview target={{ kind: printKind, id: jobId }} refreshKey={refreshKey} />
        </div>
      )}
      {tab && !isMobile && (
        <SplitPanePage
          left={tab.use_resume_structure
            ? <ResumeContentEditor target={{ kind: "job", id: jobId }} onSaved={bump} />
            : <ArtifactEditor
                title={tab.nav_label}
                artifactKey={tab.artifact_key}
                taskKey="craft_cover_letter"
                shapesKey={tab.shapes_key ?? undefined}
                jobPersistence={{ jobId, artifactKey: tab.artifact_key, onSaved: bump }}
              />}
          right={
            <PrintPreview target={{ kind: printKind, id: jobId }} refreshKey={refreshKey} />
          }
        />
      )}
      <Toast message={toast} onDone={() => setToast(null)} />
    </Modal>
  )
}
