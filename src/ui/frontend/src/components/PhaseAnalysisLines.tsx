import { useMemo } from "react"
import { useStateUi } from "../contexts/StateUiContext"
import { buildPhaseListGradeRow } from "../lib/recommendedJobReport"

/** One letterless grade-dot line per manifest phase, em dash when ungraded (AST-1973).
 *  Shared by the Recommended/Review analysis row and the Job Detail modal Info tab. */
export default function PhaseAnalysisLines({ job }: { job: Record<string, unknown> }) {
  const { manifest } = useStateUi()

  // Line order + grades_field from report_phase_tabs (modal order); short label from the
  // matching phase_score_columns entry (jd_grades → jd_score → "JD"), else the tab nav_label.
  const phaseLines = useMemo(() => {
    const rec = manifest?.jobs.recommended
    return (rec?.report_phase_tabs ?? []).map(tab => ({
      gradesField: tab.grades_field,
      label: rec?.phase_score_columns.find(
        c => c.field === tab.grades_field.replace(/_grades$/, "_score"),
      )?.label ?? tab.nav_label,
    }))
  }, [manifest])

  return (
    <div className="recommended-analysis-lines">
      {phaseLines.map(p => (
        <div key={p.gradesField} className="recommended-analysis-line">
          <span className="recommended-analysis-line-label">{p.label}</span>
          {buildPhaseListGradeRow(job, p.gradesField) ?? "\u2014"}
        </div>
      ))}
    </div>
  )
}
