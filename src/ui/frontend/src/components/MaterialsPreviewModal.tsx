import { useEffect, useMemo, useState } from "react"
import Modal from "./Modal"
import { TabBar } from "./TabbedTextArea"

type PreviewTab = "resume" | "cover"

interface Props {
  open: boolean
  onClose: () => void
  jobId: string
  hasCover: boolean
}

export default function MaterialsPreviewModal({ open, onClose, jobId, hasCover }: Props) {
  const [activeTab, setActiveTab] = useState<PreviewTab>("resume")

  useEffect(() => {
    if (!open) setActiveTab("resume")
  }, [open])

  const tabs = useMemo(() => {
    const out: { key: PreviewTab; label: string }[] = [{ key: "resume", label: "Resume" }]
    if (hasCover) out.push({ key: "cover", label: "Cover Letter" })
    return out
  }, [hasCover])

  const iframeSrc =
    activeTab === "resume"
      ? `/candidate/resume/${encodeURIComponent(jobId)}`
      : `/candidate/cover/${encodeURIComponent(jobId)}`

  const iframeTitle = activeTab === "resume" ? "Resume preview" : "Cover letter preview"

  return (
    <Modal open={open} onClose={onClose} title="Preview Materials" size="wide" stacked>
      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />
      <iframe
        title={iframeTitle}
        className="materials-preview-iframe"
        src={iframeSrc}
      />
    </Modal>
  )
}
