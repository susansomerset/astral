import { describe, expect, it } from "vitest"
import {
  candidateBaseLabel,
  candidateOptionLabel,
  sortCandidatesForSelect,
} from "../../../../src/ui/frontend/src/lib/candidateLabel"
import type { CandidateInfo } from "../../../../src/ui/frontend/src/contexts/CandidateContext"

const mk = (id: string, first?: string, last?: string): CandidateInfo => ({
  astral_candidate_id: id,
  state: "ACTIVE",
  candidate_data: { first, last },
})

describe("candidateLabel", () => {
  it("falls back to astral_candidate_id when name empty", () => {
    expect(candidateBaseLabel(mk("c9"))).toBe("c9")
  })

  it("disambiguates duplicate display names", () => {
    const all = [mk("c1", "Sam", "Lee"), mk("c2", "Sam", "Lee")]
    expect(candidateOptionLabel(all[0], all)).toBe("Sam Lee (c1)")
    expect(candidateOptionLabel(mk("solo", "Only", "One"), [mk("solo", "Only", "One")])).toBe("Only One")
  })

  it("sorts candidates by option label", () => {
    const sorted = sortCandidatesForSelect([mk("c2", "Zed"), mk("c1", "Ada")])
    expect(sorted.map(c => c.astral_candidate_id)).toEqual(["c1", "c2"])
  })
})
