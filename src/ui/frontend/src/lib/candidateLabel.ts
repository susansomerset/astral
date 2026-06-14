import type { CandidateInfo } from "../contexts/CandidateContext"

export function candidateBaseLabel(c: CandidateInfo): string {
  const cd = (c.candidate_data || {}) as { first?: string; last?: string }
  return [cd.first, cd.last].filter(Boolean).join(" ") || c.astral_candidate_id
}

export function candidateOptionLabel(c: CandidateInfo, all: CandidateInfo[]): string {
  const base = candidateBaseLabel(c)
  const collisions = all.filter(x => candidateBaseLabel(x) === base).length
  return collisions > 1 ? `${base} (${c.astral_candidate_id})` : base
}

export function sortCandidatesForSelect(candidates: CandidateInfo[]): CandidateInfo[] {
  return [...candidates].sort((a, b) => {
    const cmp = candidateOptionLabel(a, candidates).localeCompare(
      candidateOptionLabel(b, candidates),
      undefined,
      { sensitivity: "base" },
    )
    if (cmp !== 0) return cmp
    return a.astral_candidate_id.localeCompare(b.astral_candidate_id)
  })
}
