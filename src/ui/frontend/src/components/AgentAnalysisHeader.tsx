import { useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import { ConfidenceBullets } from "./ConfidenceBullets"
import RubricModal from "./RubricModal"
import { formatRubricVectorHeader, normalizeRubricVectorKey, rubricItemImportance } from "../lib/rubricDisplay"

interface Grade {
  vector: string
  grade: string
  reason?: string
  /** 1–5 for graded vectors; 0 with grade X; omitted on legacy rows → all dim bullets */
  confidence?: number
}

interface Props {
  grades: Grade[]
  rubricArtifact?: string
}

export default function AgentAnalysisHeader({ grades, rubricArtifact }: Props) {
  const [rubricVector, setRubricVector] = useState<string | null>(null)
  const { candidates, selectedId } = useCandidate()
  const candidate = candidates.find(c => c.astral_candidate_id === selectedId)

  // Look up rubric content for the selected vector
  const artifactRaw = rubricArtifact
    ? (candidate?.candidate_data as Record<string, unknown> | undefined)?.artifacts as Record<string, unknown> | undefined
    : undefined
  type RubricRow = { label?: string; content?: string; code?: string; importance?: number }
  const rubricList: RubricRow[] = Array.isArray(artifactRaw?.[rubricArtifact!])
    ? (artifactRaw![rubricArtifact!] as RubricRow[])
    : []
  function rubricRowForVector(vector: string): RubricRow | null {
    const gv = normalizeRubricVectorKey(vector || "")
    return (
      rubricList.find(r => (r.label && normalizeRubricVectorKey(r.label) === gv) || (r.code && normalizeRubricVectorKey(r.code) === gv)) ??
      null
    )
  }
  const rubricEntry = rubricVector ? rubricRowForVector(rubricVector) : null

  return (
    <div className="analysis-header">
      {grades.map(g => {
        const row = rubricArtifact ? rubricRowForVector(g.vector) : null
        const vectorLabel = row
          ? formatRubricVectorHeader(rubricItemImportance(row), row.label ?? g.vector, row.code)
          : g.vector
        return (
        <div key={g.vector} className="analysis-row">
          <div className="analysis-heading">
            <div className="analysis-grade-block">
              <span className={`grade-dot dot-${g.grade.toLowerCase()}`}>{g.grade}</span>
              <ConfidenceBullets confidence={g.confidence} />
            </div>
            <span className="analysis-vector">{vectorLabel}</span>
            {rubricArtifact && (
              <button className="analysis-rubric-link" onClick={() => setRubricVector(g.vector)}>
                show rubric
              </button>
            )}
          </div>
          {g.reason && <div className="analysis-reason">{g.reason}</div>}
        </div>
        )
      })}
      {rubricVector && (
        <RubricModal
          open
          onClose={() => setRubricVector(null)}
          vector={rubricVector}
          content={rubricEntry?.content ?? null}
        />
      )}
    </div>
  )
}
