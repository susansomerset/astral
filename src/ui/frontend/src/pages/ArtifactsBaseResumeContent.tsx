import { useState } from "react"
import PrintPreview from "../components/PrintPreview"
import ResumeContentEditor from "../components/ResumeContentEditor"
import SplitPanePage from "../components/SplitPanePage"
import { useCandidate } from "../contexts/CandidateContext"

/** AST-2084: base resume editor (left) + live base print preview (right); the editor owns accent, Print, and autosave. */
export default function BaseResumeContent() {
  const { selectedId } = useCandidate()
  // Bumped after each editor save so the preview refetches once (never per keystroke).
  const [refreshKey, setRefreshKey] = useState(0)

  if (!selectedId) return <p style={{ padding: 20, color: "var(--text-primary)" }}>No candidate selected.</p>
  return (
    <SplitPanePage
      left={<ResumeContentEditor target={{ kind: "base", id: selectedId }} onSaved={() => setRefreshKey(k => k + 1)} />}
      right={<PrintPreview target={{ kind: "base", id: selectedId }} refreshKey={refreshKey} />}
    />
  )
}
