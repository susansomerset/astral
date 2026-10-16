import { useEffect, useState } from "react"
import api from "../lib/api"
import { useCandidate } from "../contexts/CandidateContext"
import { ConfidenceBullets } from "./ConfidenceBullets"
import { GradeMark } from "./GradeMark"
import RubricModal from "./RubricModal"
import { formatRubricVectorHeader, normalizeRubricVectorKey, rubricItemImportance, sortGradesByRubricDisplayOrder } from "../lib/rubricDisplay"

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
  // Hydrated detail artifacts, tagged with the candidate/artifact they were fetched for, so a
  // stale result (candidate switched mid-open) reads as "not loaded" without an in-effect reset.
  const [detail, setDetail] = useState<{ key: string; arts: Record<string, unknown> } | null>(null)
  const detailKey = `${selectedId ?? ""}:${rubricArtifact ?? ""}`
  const detailArtifacts = detail?.key === detailKey ? detail.arts : null
  // Derived (not effect-set) so the first modal frame is already "loading" — no not-found flash.
  const contentLoading = !!(rubricArtifact && selectedId) && detailArtifacts === null

  // Rubric content lives in rubric_vector; only GET /api/candidates/<id> overlays it into
  // artifacts — the CandidateContext list payload never carries it (AST-2059).
  useEffect(() => {
    if (!rubricVector || !selectedId || !rubricArtifact) return
    let cancelled = false
    const key = `${selectedId}:${rubricArtifact}`
    api(`/api/candidates/${selectedId}`)
      .then(r => (r.ok ? r.json() : null))
      .then(body => {
        if (cancelled) return
        const arts = body?.candidate_data?.artifacts
        // Failure / missing → {} so the modal shows "not found", not a perpetual load.
        setDetail({ key, arts: arts && typeof arts === "object" ? arts : {} })
      })
      .catch(() => {
        if (!cancelled) setDetail({ key, arts: {} })
      })
    return () => {
      cancelled = true
    }
  }, [rubricVector, selectedId, rubricArtifact])

  // Clearing on close makes every open start in "loading" and refetch fresh content.
  function closeRubric() {
    setRubricVector(null)
    setDetail(null)
  }

  // List-context artifact — legacy label fallback only (labels/order unchanged by AST-2059).
  const artifactRaw = rubricArtifact
    ? ((candidate?.candidate_data as Record<string, unknown> | undefined)?.artifacts as
        | Record<string, unknown>
        | undefined)
    : undefined
  const listLiveList: RubricRow[] = Array.isArray(artifactRaw?.[rubricArtifact!])
    ? (artifactRaw![rubricArtifact!] as RubricRow[])
    : []
  // Hydrated detail artifact — content for RubricModal (AST-1063 snapshots omit content).
  const contentLiveList: RubricRow[] = Array.isArray(detailArtifacts?.[rubricArtifact!])
    ? (detailArtifacts![rubricArtifact!] as RubricRow[])
    : []
  // Labels: job-carried first; live only when no job-carried list (legacy callers).
  const labelList: RubricRow[] =
    Array.isArray(rubricItems) && rubricItems.length > 0 ? rubricItems : listLiveList

  const orderedGrades = sortGradesByRubricDisplayOrder(grades, rubricItems)

  const labelRow = rubricVector ? findRubricRow(labelList, rubricVector) : null
  // Content: prefer live row matched by vector/code from the label identity.
  const contentRow = rubricVector
    ? findRubricRow(contentLiveList, rubricVector) ||
      (labelRow?.code ? findRubricRow(contentLiveList, labelRow.code) : null) ||
      labelRow
    : null

  return (
    <div className="analysis-header">
      {orderedGrades.map(g => {
        const row = findRubricRow(labelList, g.vector)
        const vectorLabel = row
          ? formatRubricVectorHeader(rubricItemImportance(row), row.label ?? g.vector, row.code)
          : g.vector
        return (
        <div key={g.vector} className="analysis-row">
          <div className="analysis-heading">
            <div className="analysis-grade-block">
              <GradeMark grade={g.grade} />
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
          onClose={closeRubric}
          vector={rubricVector}
          content={contentRow?.content ?? null}
          loading={contentLoading}
        />
      )}
    </div>
  )
}
