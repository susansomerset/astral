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
        <button type="button" className="job-list-icon-btn" title="Resurrect" aria-label="Resurrect"
          onClick={onResurrect}>Re</button>
      </div>
    )
  }

  if (REVIEW_LIKE.has(state) && onSkip) {
    return (
      <div className="job-list-actions" onClick={e => e.stopPropagation()}>
        <button type="button" className="job-list-icon-btn" title="Skip" aria-label="Skip"
          onClick={onSkip}>Sk</button>
        {showViewAnalysis !== false && onViewAnalysis && (
          <button type="button" className="job-list-icon-btn" title="View Job Analysis" aria-label="View Job Analysis"
            onClick={onViewAnalysis}>Jr</button>
        )}
      </div>
    )
  }

  if (POST_APPLIED.has(state) && onAction) {
    return (
      <div className="job-list-actions" onClick={e => e.stopPropagation()}>
        <button type="button" className="job-list-icon-btn" title="Reapply" aria-label="Reapply"
          onClick={() => onAction("review")}>Re</button>
        <button type="button" className="job-list-icon-btn" title="Interview" aria-label="Interview"
          onClick={() => onAction("interview")}>In</button>
        <button type="button" className="job-list-icon-btn" title="Rejected" aria-label="Rejected"
          onClick={() => onAction("rejected")}>X</button>
        <button type="button" className="job-list-icon-btn" title="Ghosted" aria-label="Ghosted"
          onClick={() => onAction("ghosted")}>Gh</button>
      </div>
    )
  }

  return null
}
