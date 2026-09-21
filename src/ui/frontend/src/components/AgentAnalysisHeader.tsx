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

type RubricRow = { label?: string; content?: string; code?: string; importance?: number }

interface Props {
  grades: Grade[]
  /** Job-carried criteria for labels/order (AST-1327); preferred over live artifact. */
  rubricItems?: RubricRow[] | null
  /** Live candidate artifact key — content for “show rubric” only (snapshot omits content). */
  rubricArtifact?: string
}

function findRubricRow(list: RubricRow[], vector: string): RubricRow | null {
  const gv = normalizeRubricVectorKey(vector || "")
  return (
    list.find(
      r =>
        (r.label && normalizeRubricVectorKey(r.label) === gv) ||
        (r.code && normalizeRubricVectorKey(r.code) === gv),
    ) ?? null
  )
}

export default function AgentAnalysisHeader({ grades, rubricItems, rubricArtifact }: Props) {
  const [rubricVector, setRubricVector] = useState<string | null>(null)
  const { candidates, selectedId } = useCandidate()
  const candidate = candidates.find(c => c.astral_candidate_id === selectedId)

  // Live artifact — content for RubricModal only (AST-1063 snapshots omit content).
  const artifactRaw = rubricArtifact
    ? ((candidate?.candidate_data as Record<string, unknown> | undefined)?.artifacts as
        | Record<string, unknown>
        | undefined)
    : undefined
  const liveList: RubricRow[] = Array.isArray(artifactRaw?.[rubricArtifact!])
    ? (artifactRaw![rubricArtifact!] as RubricRow[])
    : []
  // Labels: job-carried first; live only when no job-carried list (legacy callers).
  const labelList: RubricRow[] =
    Array.isArray(rubricItems) && rubricItems.length > 0 ? rubricItems : liveList

  const labelRow = rubricVector ? findRubricRow(labelList, rubricVector) : null
  // Content: prefer live row matched by vector/code from the label identity.
  const contentRow = rubricVector
    ? findRubricRow(liveList, rubricVector) ||
      (labelRow?.code ? findRubricRow(liveList, labelRow.code) : null) ||
      labelRow
    : null

  return (
    <div className="analysis-header">
      {grades.map(g => {
        const row = findRubricRow(labelList, g.vector)
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
            {(rubricArtifact || (Array.isArray(rubricItems) && rubricItems.length > 0)) && (
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
          content={contentRow?.content ?? null}
        />
      )}
    </div>
  )
}
