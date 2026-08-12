import type { CandidateActionKey } from "../lib/candidateJobActions"

const REVIEW_LIKE = new Set(["CANDIDATE_REVIEW", "BUILD_ARTIFACTS", "PASSED_LIKE", "RECOMMENDED"])

const POST_APPLIED = new Set([
  "CANDIDATE_APPLIED",
  "CANDIDATE_INTERVIEW",
  "CANDIDATE_REJECTED",
  "CANDIDATE_GHOSTED",
])

interface Props {
  state: string
  onSkip?: () => void
  onViewAnalysis?: () => void
  /** When false, hide Jr (Recommended row click opens report instead). */
  showViewAnalysis?: boolean
  onResurrect?: () => void
  onAction?: (action: CandidateActionKey) => void
}

/** AST-312: per-row candidate workflow icon buttons. */
export default function CandidateJobRowActions({
  state,
  onSkip,
  onViewAnalysis,
  showViewAnalysis = true,
  onResurrect,
  onAction,
}: Props) {
  if (state === "CANDIDATE_SKIPPED" && onResurrect) {
    return (
      <div className="job-list-actions" onClick={e => e.stopPropagation()}>
        <button type="button" className="icon-control" title="Resurrect" aria-label="Resurrect"
          onClick={onResurrect}>R</button>
      </div>
    )
  }

  if (REVIEW_LIKE.has(state) && onSkip) {
    return (
      <div className="job-list-actions" onClick={e => e.stopPropagation()}>
        <button type="button" className="icon-control" title="Skip" aria-label="Skip"
          onClick={onSkip}>S</button>
        {showViewAnalysis !== false && onViewAnalysis && (
          <button type="button" className="icon-control" title="View Job Analysis" aria-label="View Job Analysis"
            onClick={onViewAnalysis}>J</button>
        )}
      </div>
    )
  }

  if (POST_APPLIED.has(state) && onAction) {
    return (
      <div className="job-list-actions" onClick={e => e.stopPropagation()}>
        <button type="button" className="icon-control" title="Reapply" aria-label="Reapply"
          onClick={() => onAction("review")}>R</button>
        <button type="button" className="icon-control" title="Interview" aria-label="Interview"
          onClick={() => onAction("interview")}>I</button>
        <button type="button" className="icon-control" title="Rejected" aria-label="Rejected"
          onClick={() => onAction("rejected")}>X</button>
        <button type="button" className="icon-control" title="Ghosted" aria-label="Ghosted"
          onClick={() => onAction("ghosted")}>G</button>
      </div>
    )
  }

  return null
}
