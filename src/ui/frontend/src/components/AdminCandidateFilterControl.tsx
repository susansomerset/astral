import type { CandidateInfo } from "../contexts/CandidateContext"
import type { AdminCandidateFilterValue } from "../hooks/useAdminCandidateFilter"
import { candidateOptionLabel } from "../lib/candidateLabel"

type Props = {
  value: AdminCandidateFilterValue
  onChange: (v: AdminCandidateFilterValue) => void
  candidates: CandidateInfo[]
}

export default function AdminCandidateFilterControl({ value, onChange, candidates }: Props) {
  return (
    <label>
      Candidate
      <select value={value} onChange={e => onChange(e.target.value)}>
        <option value="">All</option>
        {candidates.map(c => (
          <option key={c.astral_candidate_id} value={c.astral_candidate_id}>
            {candidateOptionLabel(c, candidates)}
          </option>
        ))}
      </select>
    </label>
  )
}
