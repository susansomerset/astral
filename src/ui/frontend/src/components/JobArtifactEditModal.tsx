import { useState } from "react"
import ArtifactEditor from "./ArtifactEditor"
import Modal from "./Modal"
import PrintPreview from "./PrintPreview"
import ResumeContentEditor from "./ResumeContentEditor"
import SplitPanePage from "./SplitPanePage"

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

/** AST-2084 / AST-2115: stacked 80%-width split pane over the Job Analysis Report — the artifact's editor left, its live print preview right. */
export default function JobArtifactEditModal({ jobId, tab, onClose }: Props) {
  // Bumped after each save so the preview refetches once.
  const [refreshKey, setRefreshKey] = useState(0)
  const bump = () => setRefreshKey(k => k + 1)

  return (
    <Modal open={!!tab} onClose={onClose} title={tab?.nav_label ?? ""} size="overlay" stacked showFooter={false}>
      {tab && (
        <SplitPanePage
          left={tab.use_resume_structure
            ? <ResumeContentEditor target={{ kind: "job", id: jobId }} onSaved={bump} />
            // Cover letter: the report's existing shapes + job persistence editor, unchanged (Decision 8).
            : <ArtifactEditor
                title={tab.nav_label}
                artifactKey={tab.artifact_key}
                taskKey="craft_cover_letter"
                shapesKey={tab.shapes_key ?? undefined}
                jobPersistence={{ jobId, artifactKey: tab.artifact_key, onSaved: bump }}
              />}
          right={
            // Thumbnail-eligible tabs are the job resume (structure tab) and the cover letter.
            <PrintPreview target={{ kind: tab.use_resume_structure ? "job_resume" : "cover", id: jobId }} refreshKey={refreshKey} />
          }
        />
      )}
    </Modal>
  )
}
